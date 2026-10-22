"""Project subagent authoring, provenance and explicit routing; never installer ownership.

Plans bind all preimages, the registry and framework lock. Multi-file application
is resumable, not atomic: publish resources/projections, detach selected old entries,
then publish the registry. Unknown files and custom authoring are never deleted.
"""
import os
from pathlib import Path
import re
import tempfile
import tomllib

from . import installation_state as state
from . import subagent_policy as p

REGISTRY = '.ai/custom/sub-agent-registry.json'
PACKAGES = '.ai/custom/sub-agents/'
ADAPTERS = {'codex': ('.codex/agents/', '.toml'), 'claude': ('.claude/agents/', '.md')}


def identifier(value):
    p.require(type(value) is str and re.fullmatch(r'[a-z][a-z0-9-]{0,63}', value), 'registry identifier')
    return value


def relative(value):
    p.require(type(value) is str and value and '\\' not in value and ':' not in value,
              'relative resource path required')
    parts = value.split('/')
    p.require(all(re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', x) and not x.endswith('.')
                  and x.casefold().split('.')[0] not in {'con', 'prn', 'aux', 'nul',
                      *('com' + str(n) for n in range(1, 10)), *('lpt' + str(n) for n in range(1, 10))}
                  for x in parts), 'unsafe resource path')
    return value


def fields(value, names):
    p.require(type(value) is dict and set(value) == set(names.split()), 'registry fields')


def text(value):
    p.require(type(value) is str and bool(value.strip()), 'nonempty text required')


def hash_value(value):
    p.require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'resource digest')


def runtime(adapter, runtime_id):
    p.require(adapter in ADAPTERS, 'unsupported adapter')
    prefix, suffix = ADAPTERS[adapter]
    return prefix + identifier(runtime_id) + suffix


def empty():
    return {'schema_version': 1, 'roles': {}, 'routes': {}, 'extensions': {}}


def validate(value):
    fields(value, 'schema_version roles routes extensions')
    p.require(type(value['schema_version']) is int and value['schema_version'] == 1, 'registry version')
    p.require(type(value['roles']) is dict and len(value['roles']) <= 64, 'role budget')
    p.require(type(value['routes']) is dict and type(value['extensions']) is dict, 'registry maps')
    destinations = []
    for rid, role in value['roles'].items():
        identifier(rid)
        fields(role, 'origin source_ref intent acceptance capabilities members baseline projections integration')
        p.require(role['origin'] in {'project-authored', 'project-derived', 'unknown'}, 'project origin')
        for key in ('source_ref', 'intent'):
            text(role[key])
        for key in ('acceptance', 'capabilities'):
            p.require(type(role[key]) is list and role[key] and len(role[key]) <= 32, 'role intent evidence')
            for item in role[key]:
                text(item)
        p.require(type(role['members']) is dict and 0 < len(role['members']) <= 64, 'member closure')
        for name, digest in role['members'].items():
            relative(name)
            hash_value(digest)
            destinations.append(PACKAGES + rid + '/' + name)
        base = role['baseline']
        if base is not None:
            fields(base, 'ref files')
            text(base['ref'])
            p.require(type(base['files']) is dict and len(base['files']) <= 64, 'baseline files')
            for name, content in base['files'].items():
                relative(name)
                p.require(type(content) is str, 'baseline content')
        p.require(type(role['projections']) is dict, 'projection map')
        for adapter, binding in role['projections'].items():
            fields(binding, 'source runtime_id')
            p.require(binding['source'] in role['members'], 'projection source missing from closure')
            destinations.append(runtime(adapter, binding['runtime_id']))
        record = role['integration']
        fields(record, 'candidate_ref coverage status evidence_ref decision_ref')
        p.require(record['coverage'] in {'not-assessed', 'not-covered', 'partial', 'covered'}, 'coverage')
        p.require(record['status'] in {'pending', 'proposed', 'adopted'}, 'integration status')
        for key in ('candidate_ref', 'evidence_ref', 'decision_ref'):
            if record[key] is not None:
                text(record[key])
        if record['coverage'] != 'not-assessed':
            p.require(record['candidate_ref'] and record['evidence_ref'], 'coverage evidence required')
        if record['status'] == 'adopted':
            p.require(record['candidate_ref'] and record['evidence_ref'] and record['decision_ref'],
                      'adoption evidence required')
    state._paths(destinations)
    for purpose, adapters in value['routes'].items():
        identifier(purpose)
        p.require(type(adapters) is dict and adapters, 'route adapters')
        for adapter, route in adapters.items():
            fields(route, 'kind id decision_ref expected_sha256')
            runtime(adapter, route['id'])
            text(route['decision_ref'])
            if route['kind'] == 'project':
                p.require(route['id'] in value['roles'] and adapter in value['roles'][route['id']]['projections']
                          and route['expected_sha256'] is None, 'project route target')
            else:
                p.require(route['kind'] == 'framework', 'route kind')
                hash_value(route['expected_sha256'])
    p.require(p.decode(p.encode(value)) == value, 'registry JSON round trip')
    return value


def at(project, name):
    root = Path(project)
    p.direct(root, directory=True)
    target = root / name
    p.direct(target, missing=True)
    return target


def read_registry(project):
    raw = p.raw_read(at(project, REGISTRY))
    return (empty() if raw is None else validate(p.decode(raw))), p.digest(raw)


def lock(project):
    # The existing validated reader owns all lock versions and managed membership.
    installed = state.read_lock(project)
    return (None, {}) if installed is None else (installed.sha256, installed.members)


def expected(registry):
    result = {}
    for rid, role in registry['roles'].items():
        result.update({PACKAGES + rid + '/' + name: digest for name, digest in role['members'].items()})
        for adapter, binding in role['projections'].items():
            result[runtime(adapter, binding['runtime_id'])] = role['members'][binding['source']]
    return result


def inspect(project):
    registry, digest = read_registry(project)
    _, managed = lock(project)
    observed = {}
    for name, wanted in expected(registry).items():
        actual = p.digest(p.raw_read(at(project, name)))
        observed[name] = {'sha256': actual, 'state': 'managed-collision' if name in managed else
                         'missing' if actual is None else 'matched' if actual == wanted else 'drift'}
    roles = {}
    for rid, role in registry['roles'].items():
        base = role['baseline']
        current = {name: observed[PACKAGES + rid + '/' + name]['sha256'] for name in role['members']}
        baseline = None if base is None else {n: p.digest(v.encode('utf-8')) for n, v in base['files'].items()}
        delta = 'unknown' if baseline is None else 'none' if current == baseline else 'present'
        record = role['integration']
        labels = [role['origin']]
        if delta == 'present':
            labels.append('user-modified')
        if record['coverage'] == 'covered' and record['status'] == 'adopted':
            labels.append('framework-integrated-with-referenced-evidence')
        roles[rid] = {'labels': labels, 'local_delta': delta, 'integration': record,
                      'evidence_verified': False, 'runtime_activation': 'unknown'}
    unknown = []
    for adapter, (prefix, suffix) in ADAPTERS.items():
        directory = Path(project) / prefix
        p.direct(directory, directory=True, missing=True)
        if directory.exists():
            unknown.extend(prefix + f.name for f in directory.iterdir()
                           if f.name.endswith(suffix) and prefix + f.name not in observed
                           and prefix + f.name not in managed)
    managed_resources = {}
    for name, member in managed.items():
        if name.startswith('.ai/core/sub-agents/') or any(name.startswith(a[0]) for a in ADAPTERS.values()):
            actual = p.digest(p.raw_read(at(project, name)))
            managed_resources[name] = {'ownership': 'framework-managed', 'sha256': actual,
                                       'state': 'missing' if actual is None else
                                       'matched' if actual == member['sha256'] else 'managed-drift'}
    return {'outcome': 'inspected', 'changed': False, 'path': REGISTRY, 'sha256': digest,
            'registry': registry, 'resources': observed, 'roles': roles,
            'unknown_entries': sorted(unknown), 'managed_resources': managed_resources,
            'runtime_activation': 'unknown'}


def check_projection(adapter, binding, raw):
    content = raw.decode('utf-8')
    if adapter == 'codex':
        actual = tomllib.loads(content).get('name')
    else:
        p.require(content.startswith('---\n') or content.startswith('---\r\n'), 'Claude frontmatter')
        front = content.split('---', 2)[1]
        matches = re.findall(r'^name:\s*([a-z][a-z0-9-]*)\s*$', front, re.M)
        p.require(len(matches) == 1, 'Claude profile identity')
        actual = matches[0]
    p.require(actual == binding['runtime_id'], 'projection name and runtime ID differ')


def plan(project, proposed, files, adopt=None, detach=None):
    """files are explicit UTF-8 authoring content, keyed by full project path.

    adopt maps existing unregistered/drifted paths to current SHAs. detach is an
    explicit list of no-longer-selected, previously registered runtime entries.
    Authoring resources are retained even after unregistering a role.
    """
    validate(proposed)
    old, before_registry = read_registry(project)
    lock_sha, managed = lock(project)
    owned, wanted = expected(old), expected(proposed)
    adopt, detach = {} if adopt is None else adopt, [] if detach is None else detach
    p.require(type(files) is dict and type(adopt) is dict and type(detach) is list, 'plan maps')
    p.require(len(set(detach)) == len(detach), 'duplicate detach')
    source_names = {PACKAGES + rid + '/' + n for rid, r in proposed['roles'].items() for n in r['members']}
    p.require(set(files) <= source_names, 'only declared authoring files may be supplied')
    content = {}
    for name in source_names:
        if name in files:
            p.require(type(files[name]) is str, 'UTF-8 authoring text')
            content[name] = files[name].encode('utf-8')
        else:
            content[name] = p.raw_read(at(project, name))
        p.require(content[name] is not None and p.digest(content[name]) == wanted[name], 'authoring content mismatch')
    for rid, role in proposed['roles'].items():
        for adapter, binding in role['projections'].items():
            raw = content[PACKAGES + rid + '/' + binding['source']]
            check_projection(adapter, binding, raw)
            content[runtime(adapter, binding['runtime_id'])] = raw
    removed = {n for n in owned if not n.startswith(PACKAGES) and n not in wanted}
    p.require(set(detach) == removed, 'explicit detach required for old runtime entries')
    p.require(set(adopt) <= set(wanted), 'unexpected adoption path')
    writes = []
    for name in sorted(set(wanted) | removed):
        p.require(name not in managed, 'framework-owned path; preserve drift and use installation recovery')
        raw = p.raw_read(at(project, name))
        before = p.digest(raw)
        if name in removed:
            p.require(before == owned[name], 'detachment requires exact registered bytes')
        elif raw is not None and (name not in owned or before != owned[name]):
            p.require(adopt.get(name) == before, 'explicit adoption of existing or drifted resource required')
        if name in adopt:
            p.require(adopt[name] == before and before is not None, 'adoption preimage mismatch')
        after = None if name in removed else content[name].decode('utf-8')
        writes.append({'path': name, 'before_sha256': before,
                       'after_sha256': None if after is None else p.digest(content[name]), 'content': after})
    writes.sort(key=lambda r: (r['content'] is None, not r['path'].startswith(PACKAGES), r['path']))
    writes.append({'path': REGISTRY, 'before_sha256': before_registry,
                   'after_sha256': p.digest(p.encode(proposed)), 'content': p.encode(proposed).decode('utf-8')})
    document = {'plan_version': 1, 'project_root': str(Path(project)), 'lock_sha256': lock_sha,
                'previous': old, 'writes': writes}
    p.decode(p.encode(document))
    return {'outcome': 'planned', 'changed': False, 'plan': document, 'plan_sha256': p.digest(p.encode(document))}


def apply(project, document, plan_sha256):
    fields(document, 'plan_version project_root lock_sha256 previous writes')
    p.require(type(document['plan_version']) is int and document['plan_version'] == 1
              and document['project_root'] == str(Path(project))
              and p.digest(p.encode(document)) == plan_sha256, 'registry plan changed')
    rows = document['writes']
    p.require(type(rows) is list and rows and rows[-1]['path'] == REGISTRY, 'registry must publish last')
    final = validate(p.decode(rows[-1]['content'].encode('utf-8')))
    wanted = expected(final)
    current, current_sha = read_registry(project)
    previous = validate(document['previous'])
    p.require(current_sha in (rows[-1]['before_sha256'], rows[-1]['after_sha256']), 'stale registry plan')
    p.require(current == (final if current_sha == rows[-1]['after_sha256'] else previous), 'previous registry mismatch')
    owned = expected(previous)
    state._paths([r['path'] for r in rows])
    for row in rows:
        fields(row, 'path before_sha256 after_sha256 content')
        name = row['path']
        p.require(name == REGISTRY or name in wanted or
                  (name in owned and not name.startswith(PACKAGES) and row['content'] is None), 'write boundary')
        raw = None if row['content'] is None else row['content'].encode('utf-8')
        p.require(p.digest(raw) == row['after_sha256'], 'plan bytes mismatch')
        if name in wanted:
            p.require(row['after_sha256'] == wanted[name], 'registry output mismatch')
    removed = {n for n in owned if not n.startswith(PACKAGES) and n not in wanted}
    p.require(set(wanted) | removed | {REGISTRY} == {r['path'] for r in rows}, 'planned resource closure')
    for rid, role in final['roles'].items():
        for adapter, binding in role['projections'].items():
            row = next(r for r in rows if r['path'] == runtime(adapter, binding['runtime_id']))
            check_projection(adapter, binding, row['content'].encode('utf-8'))
    guard = at(project, REGISTRY + '.writer')
    guard.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise p.PolicyError('registry writer active; reconcile its owner before resuming')
    written = []
    try:
        os.close(descriptor)
        p.require(read_registry(project)[1] == current_sha, 'registry changed before writer acquired')
        lock_sha, managed = lock(project)
        p.require(lock_sha == document['lock_sha256'], 'framework lock changed')
        completed = (current_sha == rows[-1]['after_sha256']
                     and rows[-1]['before_sha256'] != rows[-1]['after_sha256'])
        # Validate every preimage before the first write; exact after bytes permit resume.
        for row in rows:
            p.require(row['path'] not in managed, 'framework-owned write denied')
            actual = p.digest(p.raw_read(at(project, row['path'])))
            # Registry is the last published file. Once published, a former entry
            # can be unknown/newly owned; replay cannot acquire its ownership again.
            p.require(not completed or actual == row['after_sha256'], 'completed registry plan no longer matches')
            p.require(actual in (row['before_sha256'], row['after_sha256']), 'stale registry plan')
        for row in rows:
            target = at(project, row['path'])
            actual = p.digest(p.raw_read(target))
            if actual == row['after_sha256']:
                continue
            p.require(actual == row['before_sha256'] and lock(project)[0] == lock_sha, 'input changed during apply')
            if row['content'] is None:
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                p.direct(target.parent, directory=True)
                fd, temporary = tempfile.mkstemp(prefix='.sub-agent-', dir=target.parent)
                try:
                    with os.fdopen(fd, 'wb') as stream:
                        stream.write(row['content'].encode('utf-8'))
                        stream.flush()
                        os.fsync(stream.fileno())
                    p.require(p.digest(p.raw_read(target)) == row['before_sha256'], 'write preimage changed')
                    os.replace(temporary, target)
                finally:
                    Path(temporary).unlink(missing_ok=True)
            written.append(row['path'])
            p.require(p.digest(p.raw_read(target)) == row['after_sha256'], 'resource readback mismatch')
        return {'outcome': 'applied' if written else 'unchanged', 'changed': bool(written),
                'written': written, 'runtime_activation': 'unknown'}
    except (ValueError, OSError) as exc:
        if not written:
            raise
        return {'outcome': 'interrupted', 'changed': True, 'written': written,
                'reason': str(exc), 'recovery': 'Preserve the plan and files; inspect, then explicitly resume the same plan.'}
    finally:
        guard.unlink()


def compare(project, candidates):
    current = inspect(project)
    p.require(type(candidates) is list and len(candidates) <= 64, 'candidate budget')
    results, collisions = [], []
    for candidate in candidates:
        fields(candidate, 'id ref capabilities files runtime_paths')
        identifier(candidate['id'])
        text(candidate['ref'])
        p.require(type(candidate['capabilities']) is list and type(candidate['files']) is dict
                  and type(candidate['runtime_paths']) is list, 'candidate shape')
        for name, content in candidate['files'].items():
            relative(name)
            p.require(type(content) is str, 'candidate text')
        candidate_collisions = []
        for name in candidate['runtime_paths']:
            p.require(type(name) is str and any(name.startswith(prefix) and name.endswith(suffix)
                      and re.fullmatch(r'[a-z][a-z0-9-]{0,63}', name[len(prefix):-len(suffix)])
                      for prefix, suffix in ADAPTERS.values()), 'candidate runtime path')
            if p.raw_read(at(project, name)) is not None:
                owner = ('project-registered' if name in current['resources'] else 'framework-managed'
                         if name in current['managed_resources'] else 'unknown-preserve')
                candidate_collisions.append(name)
                collisions.append({'candidate': candidate['ref'], 'path': name, 'ownership': owner})
        for rid, role in current['registry']['roles'].items():
            role_entries = {runtime(a, b['runtime_id']) for a, b in role['projections'].items()}
            if (candidate['id'] != rid and not set(candidate['capabilities']) & set(role['capabilities'])
                    and not role_entries & set(candidate['runtime_paths'])):
                continue
            base = role['baseline']
            differences = []
            local = {n: current['resources'][PACKAGES + rid + '/' + n]['sha256'] for n in role['members']}
            incoming = {n: p.digest(v.encode('utf-8')) for n, v in candidate['files'].items()}
            old = {} if base is None else {n: p.digest(v.encode('utf-8')) for n, v in base['files'].items()}
            for name in sorted(set(old) | set(local) | set(incoming)):
                b, l, c = old.get(name), local.get(name), incoming.get(name)
                status = ('baseline-unavailable' if base is None else 'unchanged' if b == l == c else
                          'same-change' if l == c else 'candidate-only' if b == l else
                          'local-only' if b == c else 'conflict')
                differences.append({'path': name, 'difference': status, 'baseline': b, 'local': l, 'candidate': c})
            role_collisions = sorted(role_entries & set(candidate_collisions))
            results.append({'project_role': rid, 'candidate': candidate['ref'], 'match': 'declared-capability-or-id',
                            'differences': differences, 'runtime_collisions': role_collisions,
                            'semantic_coverage': 'not-established-by-comparison',
                            'choices': ['keep-project', 'coexist-with-unique-runtime-id', 'adopt-framework'],
                            'route_changed': False})
    return {'outcome': 'compared', 'changed': False, 'comparisons': results, 'runtime_collisions': collisions}


def resolve(project, purpose, adapter, task, **selection):
    current = inspect(project)
    route = current['registry']['routes'].get(purpose, {}).get(adapter)
    p.require(route is not None, 'explicit role route missing')
    if route['kind'] == 'project':
        role = current['registry']['roles'][route['id']]
        binding = role['projections'][adapter]
        names = [PACKAGES + route['id'] + '/' + n for n in role['members']]
        name = runtime(adapter, binding['runtime_id'])
        p.require(all(current['resources'][n]['state'] == 'matched' for n in [*names, name]), 'project route resource drift')
        runtime_id = binding['runtime_id']
    else:
        runtime_id = route['id']
        name = runtime(adapter, runtime_id)
        _, managed = lock(project)
        p.require(name in managed and managed[name].get('owner') == f'adapter/{adapter}/sub-agent/{runtime_id}'
                  and managed[name]['sha256'] == route['expected_sha256']
                  and p.digest(p.raw_read(at(project, name))) == route['expected_sha256'],
                  'framework route pending installation or drifted')
        names = [n for n, member in managed.items() if member.get('owner') == 'sub-agent/' + runtime_id]
        p.require(names and all(p.digest(p.raw_read(at(project, n))) == managed[n]['sha256'] for n in names),
                  'framework role resource closure missing or drifted')
    raw = p.raw_read(at(project, name))
    profile = tomllib.loads(raw.decode('utf-8')) if adapter == 'codex' else {}
    observation = {k: profile[key] for k, key in [('model', 'model'), ('effort', 'model_reasoning_effort')] if key in profile}
    policy = p.inspect(project)['policy']
    p.require(policy is not None, 'policy missing')
    result = p.resolve(policy, adapter, task, profile=observation, **selection)
    return {**result, 'runtime_id': runtime_id, 'entry': name, 'resources': names,
            'route': route, 'files_observed': True, 'runtime_activation': 'unknown'}


def execute(request):
    operation = request.get('operation')
    args = {'registry-inspect': {'project_root'}, 'registry-plan': {'project_root', 'proposed', 'files', 'adopt', 'detach'},
            'registry-apply': {'project_root', 'plan', 'plan_sha256'},
            'role-compare': {'project_root', 'candidates'},
            'route-resolve': {'project_root', 'purpose', 'adapter', 'task', 'tier', 'authority_ref', 'observations'}}
    p.require(operation in args and set(request) <= args[operation] | {'operation', 'engine', 'engine_root'}, 'registry request')
    root = request['project_root']
    if operation == 'registry-inspect':
        return inspect(root)
    if operation == 'registry-plan':
        return plan(root, request['proposed'], request['files'], request.get('adopt'), request.get('detach'))
    if operation == 'registry-apply':
        return apply(root, request['plan'], request['plan_sha256'])
    if operation == 'role-compare':
        return compare(root, request['candidates'])
    return resolve(root, request['purpose'], request['adapter'], request['task'],
                   **{k: request[k] for k in ('tier', 'authority_ref', 'observations') if k in request})
