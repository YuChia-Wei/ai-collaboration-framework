"""Project skill authoring, provenance and explicit routing; never installer ownership.

Plans bind all preimages, the registry and framework lock. Multi-file application
is resumable, not atomic: publish resources/projections, detach selected old entries,
then publish the registry. Unknown files and custom authoring are never deleted.
"""
import os
from pathlib import Path
import re
import tempfile
import uuid

from . import installation_state as state
from . import subagent_policy as p
from .project_layout import resolve as layout


def registry_path(project):
    return layout(project) + '/skill-registry.json'


def packages(project):
    return layout(project) + '/skills/'


REGISTRY = '.ai/project/skill-registry.json'
PACKAGES = '.ai/project/skills/'
ADAPTERS = {'codex': ('.agents/skills/', '/SKILL.md'), 'claude': ('.claude/skills/', '/SKILL.md')}


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
    return {'schema_version': 1, 'skills': {}, 'routes': {}, 'extensions': {}}


def validate(value):
    fields(value, 'schema_version skills routes extensions')
    p.require(type(value['schema_version']) is int and value['schema_version'] == 1, 'registry version')
    p.require(type(value['skills']) is dict and len(value['skills']) <= 64, 'skill budget')
    p.require(type(value['routes']) is dict and type(value['extensions']) is dict, 'registry maps')
    destinations = []
    for rid, role in value['skills'].items():
        identifier(rid)
        fields(role, 'origin source_ref intent acceptance capabilities members baseline projections integration')
        p.require(role['origin'] in {'project-authored', 'project-derived', 'unknown'}, 'project origin')
        for key in ('source_ref', 'intent'):
            text(role[key])
        for key in ('acceptance', 'capabilities'):
            p.require(type(role[key]) is list and role[key] and len(role[key]) <= 32, 'skill intent evidence')
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
                utf8(content)
        p.require(type(role['projections']) is dict, 'projection map')
        for adapter, binding in role['projections'].items():
            fields(binding, 'files runtime_id')
            p.require(type(binding['files']) is dict and 'SKILL.md' in binding['files']
                      and len(binding['files']) <= 64, 'projection member map requires SKILL.md')
            for destination, source in binding['files'].items():
                relative(destination)
                p.require(source in role['members'], 'projection source missing from closure')
                destinations.append(native(adapter, binding, destination))
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
            p.require(adapter in ADAPTERS, 'unsupported adapter')
            text(route['decision_ref'])
            if route['kind'] == 'project':
                p.require(route['id'] in value['skills'] and adapter in value['skills'][route['id']]['projections']
                          and route['expected_sha256'] is None, 'project route target')
            else:
                p.require(route['kind'] == 'framework', 'route kind')
                from .data import identifier as package_identifier
                package_identifier(route['id'], 'framework skill ID')
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
    raw = p.raw_read(at(project, registry_path(project)))
    return (empty() if raw is None else validate(p.decode(raw))), p.digest(raw)


def lock(project):
    # The existing validated reader owns all lock versions and managed membership.
    installed = state.read_lock(project)
    return (None, {}) if installed is None else (installed.sha256, installed.members)


def managed_read(project, name):
    # Framework payload uses its installer-owned file budget, independently of
    # the smaller project-native UTF-8 authoring budget.
    reader = state._Reader()
    target = reader.locate(Path(project), name)
    return None if target is None else reader.read(target, name)


def expected(registry, prefix=PACKAGES):
    result = {}
    for rid, role in registry['skills'].items():
        result.update({prefix + rid + '/' + name: digest for name, digest in role['members'].items()})
        for adapter, binding in role['projections'].items():
            for destination, source in binding['files'].items():
                result[native(adapter, binding, destination)] = role['members'][source]
    return result


def retain_records(previous, proposed):
    p.require(set(previous['skills']) <= set(proposed['skills']),
              'skill records must be retained; detach projections and routes explicitly')
    for rid, before in previous['skills'].items():
        after = proposed['skills'][rid]
        old_native = {native(a, b, n) for a, b in before['projections'].items() for n in b['files']}
        new_native = {native(a, b, n) for a, b in after['projections'].items() for n in b['files']}
        if old_native - new_native:
            p.require(all(before[key] == after[key] for key in ('origin', 'source_ref', 'baseline')),
                      'detachment must preserve provenance and baseline')


def inspect(project):
    REGISTRY, PACKAGES = registry_path(project), packages(project)
    registry, digest = read_registry(project)
    _, managed = lock(project)
    observed = {}
    for name, wanted in expected(registry, PACKAGES).items():
        actual = p.digest(p.raw_read(at(project, name)))
        observed[name] = {'sha256': actual, 'state': 'managed-collision' if name in managed else
                         'missing' if actual is None else 'matched' if actual == wanted else 'drift'}
    roles = {}
    for rid, role in registry['skills'].items():
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
            for child in directory.iterdir():
                p.direct(child, directory=True)
                entry = prefix + child.name + suffix
                if p.raw_read(at(project, entry)) is not None and entry not in observed and entry not in managed:
                    unknown.append(entry)
    managed_resources = {}
    for name, member in managed.items():
        if name.startswith('.ai/core/skills/') or any(name.startswith(a[0]) for a in ADAPTERS.values()):
            actual = p.digest(managed_read(project, name))
            managed_resources[name] = {'ownership': 'framework-managed', 'sha256': actual,
                                       'state': 'missing' if actual is None else
                                       'matched' if actual == member['sha256'] else 'managed-drift'}
    return {'outcome': 'inspected', 'changed': False, 'path': REGISTRY, 'sha256': digest,
            'registry': registry, 'resources': observed, 'skills': roles,
            'unknown_entries': sorted(unknown), 'managed_resources': managed_resources,
            'runtime_activation': 'unknown'}


def native(adapter, binding, destination):
    relative(destination)
    return runtime(adapter, binding['runtime_id'])[:-len('SKILL.md')] + destination


def utf8(value):
    p.require(type(value) is str, 'UTF-8 resource text required')
    raw = value.encode('utf-8')
    p.require(len(raw) <= 256 * 1024 and not any(ord(c) < 32 and c not in '\t\n\r' for c in value),
              'opaque or oversized resource unsupported; bounded UTF-8 text required')
    return raw


def check_projection(adapter, binding, raw):
    content = raw.decode('utf-8')
    utf8(content)
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', content, re.DOTALL)
    p.require(match is not None, 'skill frontmatter')
    from .data import yaml_object
    front = yaml_object(match.group(1).encode('utf-8'), 'native skill frontmatter')
    p.require(front.get('name') == binding['runtime_id'], 'projection name and runtime ID differ')


def check_resources(registry, content, prefix):
    # Framework metadata is optional. Declaring it opts into its real loader and
    # reference closure checks; plain native skills have no framework dependency.
    from .package import load_package, check_references
    from .git_source import Blob
    for rid, skill in registry['skills'].items():
        blobs = {n: Blob(n, '', '100644', content[prefix + rid + '/' + n]) for n in skill['members']}
        if 'skill-package.yaml' in blobs:
            package = load_package(blobs['skill-package.yaml'])
            p.require(package.members <= set(blobs), 'declared framework resource missing from closure')
            check_references(package, blobs)
        for adapter, binding in skill['projections'].items():
            check_projection(adapter, binding, content[prefix + rid + '/' + binding['files']['SKILL.md']])


def plan(project, proposed, files, adopt=None, detach=None):
    """files are explicit UTF-8 authoring content, keyed by full project path.

    adopt maps existing unregistered/drifted paths to current SHAs. detach is an
    explicit list of no-longer-selected, previously registered runtime entries.
    Authoring resources and records remain after detaching all projections.
    """
    REGISTRY, PACKAGES = registry_path(project), packages(project)
    validate(proposed)
    old, before_registry = read_registry(project)
    retain_records(old, proposed)
    lock_sha, managed = lock(project)
    owned, wanted = expected(old, PACKAGES), expected(proposed, PACKAGES)
    adopt, detach = {} if adopt is None else adopt, [] if detach is None else detach
    p.require(type(files) is dict and type(adopt) is dict and type(detach) is list, 'plan maps')
    p.require(len(set(detach)) == len(detach), 'duplicate detach')
    source_names = {PACKAGES + rid + '/' + n for rid, r in proposed['skills'].items() for n in r['members']}
    p.require(set(files) <= source_names, 'only declared authoring files may be supplied')
    content = {}
    for name in source_names:
        if name in files:
            p.require(type(files[name]) is str, 'UTF-8 authoring text')
            content[name] = utf8(files[name])
        else:
            content[name] = p.raw_read(at(project, name))
        p.require(content[name] is not None and p.digest(content[name]) == wanted[name], 'authoring content mismatch')
        utf8(content[name].decode('utf-8'))
    check_resources(proposed, content, PACKAGES)
    for rid, role in proposed['skills'].items():
        for adapter, binding in role['projections'].items():
            for destination, source in binding['files'].items():
                content[native(adapter, binding, destination)] = content[PACKAGES + rid + '/' + source]
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
    document = {'plan_version': 1, 'operation_id': str(uuid.uuid4()),
                'project_root': str(Path(project)), 'lock_sha256': lock_sha,
                'previous': old, 'writes': writes}
    p.decode(p.encode(document))
    return {'outcome': 'planned', 'changed': False, 'plan': document, 'plan_sha256': p.digest(p.encode(document))}


def apply(project, document, plan_sha256):
    from .project_layout import writer
    with writer(project):
        return _apply(project, document, plan_sha256)


def _apply(project, document, plan_sha256):
    REGISTRY, PACKAGES = registry_path(project), packages(project)
    fields(document, 'plan_version operation_id project_root lock_sha256 previous writes')
    operation_id = document['operation_id']
    p.require(type(operation_id) is str and str(uuid.UUID(operation_id)) == operation_id
              and uuid.UUID(operation_id).version == 4, 'canonical random operation UUID required')
    p.require(type(document['plan_version']) is int and document['plan_version'] == 1
              and document['project_root'] == str(Path(project))
              and p.digest(p.encode(document)) == plan_sha256, 'registry plan changed')
    rows = document['writes']
    p.require(type(rows) is list and rows and rows[-1]['path'] == REGISTRY, 'registry must publish last')
    final = validate(p.decode(rows[-1]['content'].encode('utf-8')))
    wanted = expected(final, PACKAGES)
    current, current_sha = read_registry(project)
    previous = validate(document['previous'])
    retain_records(previous, final)
    p.require(current_sha in (rows[-1]['before_sha256'], rows[-1]['after_sha256']), 'stale registry plan')
    p.require(current == (final if current_sha == rows[-1]['after_sha256'] else previous), 'previous registry mismatch')
    owned = expected(previous, PACKAGES)
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
    source_content = {row['path']: utf8(row['content']) for row in rows if row['path'].startswith(PACKAGES)}
    check_resources(final, source_content, PACKAGES)
    for rid, skill in final['skills'].items():
        for adapter, binding in skill['projections'].items():
            for destination, source in binding['files'].items():
                row = next(r for r in rows if r['path'] == native(adapter, binding, destination))
                p.require(row['content'].encode('utf-8') == source_content[PACKAGES + rid + '/' + source],
                          'projection differs from authoring member')
    completion_name = '.ai/local/skill-registry-completed/' + plan_sha256 + '.json'
    completion = at(project, completion_name)
    completed_bytes = p.encode({'completion_version': 1, 'plan_sha256': plan_sha256})
    completion_before = p.raw_read(completion)
    p.require(completion_before in (None, completed_bytes), 'malformed or mismatched skill completion marker')
    guard = at(project, REGISTRY + '.writer')
    guard.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise p.PolicyError('registry writer active; reconcile its owner before resuming')
    written = []
    completing = False
    try:
        os.close(descriptor)
        p.require(read_registry(project)[1] == current_sha, 'registry changed before writer acquired')
        lock_sha, managed = lock(project)
        p.require(lock_sha == document['lock_sha256'], 'framework lock changed')
        p.require(p.raw_read(completion) == completion_before, 'completion marker changed before apply')
        p.require(completion_name not in managed, 'framework-owned completion marker denied')
        completed = (completion_before is not None or
                     (current_sha == rows[-1]['after_sha256']
                      and rows[-1]['before_sha256'] != rows[-1]['after_sha256']))
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
                fd, temporary = tempfile.mkstemp(prefix='.skill-', dir=target.parent)
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
        # A successful same-registry repair cannot be distinguished by registry
        # bytes alone. Keep a separate immutable completion fact for every exact
        # plan, after verifying the entire published state again.
        p.require(lock(project)[0] == lock_sha and all(
            p.digest(p.raw_read(at(project, row['path']))) == row['after_sha256'] for row in rows),
            'final registry plan state changed')
        p.require(p.raw_read(completion) == completion_before, 'completion marker changed during apply')
        completing = True
        if completion_before is None:
            completion.parent.mkdir(parents=True, exist_ok=True)
            p.direct(completion.parent, directory=True)
            fd, temporary = tempfile.mkstemp(prefix='.skill-completion-', dir=completion.parent)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(completed_bytes)
                    stream.flush()
                    os.fsync(stream.fileno())
                p.require(p.raw_read(completion) is None, 'completion marker appeared during apply')
                os.replace(temporary, completion)
                written.append(completion_name)
            finally:
                Path(temporary).unlink(missing_ok=True)
        p.require(p.raw_read(completion) == completed_bytes, 'completion marker readback mismatch')
        return {'outcome': 'applied' if written else 'unchanged', 'changed': bool(written),
                'written': written, 'runtime_activation': 'unknown'}
    except (ValueError, OSError) as exc:
        if not written and not completing:
            raise
        return {'outcome': 'interrupted', 'changed': bool(written), 'written': written,
                'reason': str(exc), 'recovery': 'Preserve the plan and files; inspect, then explicitly resume the same plan.'}
    finally:
        guard.unlink()


def compare(project, candidates):
    REGISTRY, PACKAGES = registry_path(project), packages(project)
    current = inspect(project)
    p.require(type(candidates) is list and len(candidates) <= 64, 'candidate budget')
    results, collisions = [], []
    for candidate in candidates:
        fields(candidate, 'id ref capabilities files runtime_paths')
        from .data import identifier as package_identifier
        package_identifier(candidate['id'], 'framework candidate ID')
        text(candidate['ref'])
        p.require(type(candidate['capabilities']) is list and type(candidate['files']) is dict
                  and type(candidate['runtime_paths']) is list, 'candidate shape')
        for name, content in candidate['files'].items():
            relative(name)
            utf8(content)
        candidate_collisions = []
        for name in candidate['runtime_paths']:
            p.require(type(name) is str, 'candidate runtime path')
            prefixes = [prefix for prefix, _ in ADAPTERS.values() if name.startswith(prefix)]
            p.require(len(prefixes) == 1, 'candidate runtime path')
            parts = name[len(prefixes[0]):].split('/', 1)
            p.require(len(parts) == 2, 'candidate skill member required')
            package_identifier(parts[0], 'framework candidate entry name')
            relative(parts[1])
            if (name in current['resources'] or name in current['managed_resources']
                    or p.raw_read(at(project, name)) is not None):
                owner = ('project-registered' if name in current['resources'] else 'framework-managed'
                         if name in current['managed_resources'] else 'unknown-preserve')
                candidate_collisions.append(name)
                collisions.append({'candidate': candidate['ref'], 'path': name, 'ownership': owner})
        for rid, role in current['registry']['skills'].items():
            role_entries = {native(a, b, dest) for a, b in role['projections'].items() for dest in b['files']}
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
            results.append({'project_skill': rid, 'candidate': candidate['ref'], 'match': 'declared-capability-or-id',
                            'differences': differences, 'runtime_collisions': role_collisions,
                            'semantic_coverage': 'not-established-by-comparison',
                            'choices': ['keep-project', 'coexist-with-unique-runtime-id', 'adopt-framework'],
                            'route_changed': False})
    return {'outcome': 'compared', 'changed': False, 'comparisons': results, 'runtime_collisions': collisions}


def resolve(project, purpose, adapter):
    REGISTRY, PACKAGES = registry_path(project), packages(project)
    current = inspect(project)
    route = current['registry']['routes'].get(purpose, {}).get(adapter)
    p.require(route is not None, 'explicit skill route missing')
    if route['kind'] == 'project':
        skill = current['registry']['skills'][route['id']]
        binding = skill['projections'][adapter]
        names = [PACKAGES + route['id'] + '/' + n for n in skill['members']]
        projections = [native(adapter, binding, n) for n in binding['files']]
        p.require(all(current['resources'][n]['state'] == 'matched' for n in [*names, *projections]),
                  'project route resource drift')
        content = {n: p.raw_read(at(project, n)) for n in names}
        check_resources({'skills': {route['id']: skill}}, content, PACKAGES)
        name, runtime_id = runtime(adapter, binding['runtime_id']), binding['runtime_id']
    else:
        _, managed = lock(project)
        owner = f"adapter/{adapter}/skill/{route['id']}"
        entries = [(n, member) for n, member in managed.items() if member.get('owner') == owner]
        p.require(len(entries) == 1, 'framework route pending installation or ambiguous binding')
        name, member = entries[0]
        binding = member.get('binding')
        p.require(type(binding) is dict and binding.get('skill') == route['id']
                  and binding.get('adapter') == adapter and type(binding.get('entry_name')) is str,
                  'framework installed skill binding missing')
        runtime_id = binding['entry_name']
        from .data import identifier as package_identifier
        package_identifier(runtime_id, 'installed skill entry name')
        prefix, suffix = ADAPTERS[adapter]
        p.require(name == prefix + runtime_id + suffix and member['sha256'] == route['expected_sha256']
                  and p.digest(managed_read(project, name)) == route['expected_sha256'],
                  'framework route pending installation or drifted')
        names = [n for n, row in managed.items() if row.get('owner') == 'skill/' + route['id']]
        p.require(names and binding.get('core_entrypoint') in names
                  and all(p.digest(managed_read(project, n)) == managed[n]['sha256'] for n in names),
                  'framework skill resource closure missing or drifted')
        projections = [name]
    return {'outcome': 'selected', 'changed': False, 'runtime_id': runtime_id, 'entry': name,
            'resources': names, 'projections': projections, 'route': route, 'files_observed': True,
            'runtime_activation': 'unknown', 'behavior_acceptance': 'unknown'}


def execute(request):
    operation = request.get('operation')
    args = {'registry-inspect': {'project_root'}, 'registry-plan': {'project_root', 'proposed', 'files', 'adopt', 'detach'},
            'registry-apply': {'project_root', 'plan', 'plan_sha256'},
            'skill-compare': {'project_root', 'candidates'},
            'route-resolve': {'project_root', 'purpose', 'adapter'}}
    p.require(operation in args and set(request) <= args[operation] | {'operation', 'engine', 'engine_root'}, 'registry request')
    root = request['project_root']
    if operation == 'registry-inspect':
        return inspect(root)
    if operation == 'registry-plan':
        return plan(root, request['proposed'], request['files'], request.get('adopt'), request.get('detach'))
    if operation == 'registry-apply':
        return apply(root, request['plan'], request['plan_sha256'])
    if operation == 'skill-compare':
        return compare(root, request['candidates'])
    return resolve(root, request['purpose'], request['adapter'])


def migration_writes(project):
    """Explicit layout relocation rewrites registered text and mapped projections.

    Baseline bytes/ref and provenance remain historical comparison evidence.
    """
    from copy import deepcopy
    from .project_layout import LEGACY, CANONICAL, relocated
    registry, before = read_registry(project)
    updated = deepcopy(registry)
    _, managed = lock(project)
    writes = []
    content = {}
    for rid, skill in registry['skills'].items():
        for member, wanted in skill['members'].items():
            name = packages(project) + rid + '/' + member
            raw = p.raw_read(at(project, name))
            p.require(p.digest(raw) == wanted and name not in managed and relocated(name) not in managed,
                      'registered skill authoring drift or managed collision')
            replacement = utf8(raw.decode('utf-8').replace(LEGACY + '/', CANONICAL + '/'))
            content[name] = replacement
            updated['skills'][rid]['members'][member] = p.digest(replacement)
            targets = [relocated(name)]
            for adapter, binding in skill['projections'].items():
                for destination, source in binding['files'].items():
                    if source != member:
                        continue
                    entry = native(adapter, binding, destination)
                    p.require(entry not in managed and p.raw_read(at(project, entry)) == raw,
                              'registered skill projection drift or managed collision')
                    targets.append(entry)
            if replacement != raw:
                writes.extend({'path': target, 'before_sha256': wanted,
                               'after_sha256': p.digest(replacement), 'content': replacement.decode('utf-8')}
                              for target in targets)
    check_resources(updated, content, packages(project))
    if before is not None:
        validate(updated)
        raw = p.encode(updated)
        writes.append({'path': CANONICAL + '/skill-registry.json', 'before_sha256': before,
                       'after_sha256': p.digest(raw), 'content': raw.decode('utf-8')})
    return writes
