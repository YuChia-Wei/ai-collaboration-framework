"""One project-owned layout and explicit, pinned legacy relocation.

Migration is a resumable directory rename followed by exact registered rewrites
and an installation-owned lock transition. It does not adopt or activate roles.
External writers must be stopped; participating writers share installer exclusion.
"""
from contextlib import contextmanager
from copy import deepcopy
import os
from pathlib import Path
import stat
import tempfile

CANONICAL = '.ai/project'
LEGACY = '.ai/custom'


def resolve(project):
    from . import subagent_policy as p
    root = Path(project)
    p.direct(root, directory=True)
    for name in (CANONICAL, LEGACY):
        p.direct(root / name, directory=True, missing=True)
    old, new = (root / LEGACY).exists(), (root / CANONICAL).exists()
    p.require(not (old and new), 'ambiguous project layout: both roots exist')
    return LEGACY if old else CANONICAL


@contextmanager
def writer(project):
    from . import installation_state as s
    from .installation_io import Backend, Changes, IO
    from .maintenance_coordination import WriterLock
    root = Path(project)
    s._root(str(root))
    backend = Backend({'project': root}, {'declared_by': 'project-layout',
        'declaration_reference': 'explicit participating writer', 'failure_domain': 'process-termination'})
    io = IO(backend, s._Reader(), Changes())
    with WriterLock(io, root, allow_create=True) as held:
        yield held


def inventory(project, base):
    """Hash the entire direct tree, including empty directories and opaque files."""
    from . import subagent_policy as p
    from . import installation_state as s
    root, result = Path(project), []
    target = root / base
    p.direct(target, directory=True)
    pending = [target]
    total = 0
    while pending:
        current = pending.pop()
        names = list(current.iterdir())
        p.require(len({n.name.casefold() for n in names}) == len(names), 'layout case collision')
        for item in names:
            relative = item.relative_to(target).as_posix()
            s._relative(relative)
            info = item.lstat()
            p.require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                      'linked layout member')
            p.require(info.st_dev == target.stat().st_dev, 'layout volume boundary')
            if stat.S_ISDIR(info.st_mode):
                result.append({'path': relative, 'kind': 'directory'})
                pending.append(item)
            else:
                p.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                          and info.st_size <= s.LIMITS['file_bytes'], 'layout file type or budget')
                raw = item.read_bytes()
                after = item.stat()
                p.require((info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink) ==
                          (after.st_ino, after.st_size, after.st_mtime_ns, after.st_nlink), 'layout read drift')
                total += len(raw)
                result.append({'path': relative, 'kind': 'file', 'sha256': p.digest(raw), 'size': len(raw)})
        p.require(len(result) <= s.LIMITS['entries'] and total <= s.LIMITS['total_bytes'], 'layout tree budget')
    return sorted(result, key=lambda row: row['path'])


def inspect(project):
    from . import installation_state as s
    base = resolve(project)
    lock = s.read_lock(project)
    return {'outcome': 'inspected', 'changed': False, 'layout': base,
            'legacy': base == LEGACY, 'lock_sha256': None if lock is None else lock.sha256,
            'inventory': inventory(project, base) if (Path(project) / base).exists() else []}


def relocated(name):
    return CANONICAL + name[len(LEGACY):] if name.startswith(LEGACY + '/') else name


def read(project, name):
    from . import installation_state as s, catalog
    reader = s._Reader()
    root = s._root(str(project))
    target = reader.locate(root, name)
    return None if target is None else catalog.read_raw(reader, root, name, s.LIMITS['file_bytes'])


def _lock_transition(project, writes, engine):
    """Installation reader/serializer own relocation; selection and assets stay fixed."""
    from . import installation_state as s, catalog, subagent_policy as p
    from .data import json_bytes
    installed = s.read_lock(project)
    if installed is None:
        return None
    p.require(installed.document['lock_version'] == 2, 'legacy installation lock needs installation upgrade')
    before = installed.document
    after = deepcopy(before)
    for binding in before['selection']['desired']['bindings']:
        p.require(all(not a['path'].startswith(LEGACY + '/') for a in binding['authorities']),
                  'selected binding authority relocation requires a separately planned installation')
    replacements = {row['path']: row for row in writes}
    for row in after['project_inputs']:
        if row['path'].startswith(LEGACY + '/'):
            raw = catalog.read_raw(s._Reader(), Path(project), row['path'], s.LIMITS['file_bytes'])
            p.require(p.digest(raw) == row['sha256'], 'moved installation input drift')
            row['path'] = relocated(row['path'])
            if row['path'] in replacements:
                row['sha256'] = replacements[row['path']]['after_sha256']
    after['project_inputs'].sort(key=lambda row: row['path'])
    s._engine_shape(engine)
    p.require(tuple(row['path'] for row in engine['files']) == s.ENGINE_FILES, 'migration engine closure')
    after['engine'] = deepcopy(engine)
    raw = json_bytes(after)
    catalog.lock_bytes(raw)
    return {'path': s.LOCK_PATH, 'before_sha256': installed.sha256,
            'after_sha256': p.digest(raw), 'content': raw.decode('utf-8')}


def plan(project, engine):
    from . import installation_state as s, subagent_policy as p, subagent_registry as r
    p.require(resolve(project) == LEGACY, 'legacy project layout required')
    p.require(not any((Path(project) / LEGACY / name).exists() for name in
                      ('sub-agent-policy.json.writer', 'sub-agent-registry.json.writer')),
              'legacy subagent writer active; reconcile its owner')
    p.require(all(not (Path(project) / marker).exists() for marker in s.MARKERS), 'installation operation active')
    before = inventory(project, LEGACY)
    registry, _ = r.read_registry(project)
    _, managed = r.lock(project)
    p.require(not any(name.startswith((LEGACY + '/', CANONICAL + '/')) for name in managed),
              'framework-managed project tree cannot be relocated')
    writes = []
    updated = deepcopy(registry)
    for rid, role in registry['roles'].items():
        for member, wanted in role['members'].items():
            name = LEGACY + '/sub-agents/' + rid + '/' + member
            raw = p.raw_read(r.at(project, name))
            p.require(p.digest(raw) == wanted and name not in managed and relocated(name) not in managed,
                      'registered authoring drift or managed collision')
            # Only registered UTF-8 authoring receives reference edits; binary members retain bytes.
            try:
                replacement = raw.decode('utf-8').replace(LEGACY + '/', CANONICAL + '/').encode('utf-8')
            except UnicodeDecodeError:
                replacement = raw
            updated['roles'][rid]['members'][member] = p.digest(replacement)
            if replacement != raw:
                writes.append({'path': relocated(name), 'before_sha256': wanted,
                               'after_sha256': p.digest(replacement), 'content': replacement.decode('utf-8')})
            for adapter, binding in role['projections'].items():
                if binding['source'] != member:
                    continue
                native = r.runtime(adapter, binding['runtime_id'])
                p.require(native not in managed, 'framework-managed native collision')
                p.require(p.raw_read(r.at(project, native)) == raw, 'registered native drift')
                r.check_projection(adapter, binding, replacement)
                if replacement != raw:
                    writes.append({'path': native, 'before_sha256': wanted,
                                   'after_sha256': p.digest(replacement), 'content': replacement.decode('utf-8')})
    old_registry = p.raw_read(r.at(project, LEGACY + '/sub-agent-registry.json'))
    if old_registry is not None:
        r.validate(updated)
        raw = p.encode(updated)
        writes.append({'path': CANONICAL + '/sub-agent-registry.json', 'before_sha256': p.digest(old_registry),
                       'after_sha256': p.digest(raw), 'content': raw.decode('utf-8')})
    lock = _lock_transition(project, writes, engine)
    post = deepcopy(before)
    by_path = {row['path']: row for row in writes}
    for row in post:
        change = by_path.get(CANONICAL + '/' + row['path'])
        if change is not None:
            row.update(sha256=change['after_sha256'], size=len(change['content'].encode('utf-8')))
    document = {'plan_version': 1, 'project_root': str(Path(project)), 'source': LEGACY,
                'destination': CANONICAL, 'before': before, 'after': post, 'writes': writes,
                'lock': lock, 'engine': deepcopy(engine)}
    return {'outcome': 'planned', 'changed': False, 'plan': document, 'plan_sha256': p.digest(p.encode(document))}


def _replace(project, row):
    from . import subagent_policy as p
    target = Path(project) / row['path']
    p.require(p.digest(read(project, row['path'])) == row['before_sha256'], 'migration preimage changed')
    fd, name = tempfile.mkstemp(prefix='.layout-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(row['content'].encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
        p.require(p.digest(read(project, row['path'])) == row['before_sha256'], 'migration preimage changed')
        os.replace(name, target)
    finally:
        Path(name).unlink(missing_ok=True)
    p.require(p.digest(read(project, row['path'])) == row['after_sha256'], 'migration readback mismatch')


def apply(project, document, plan_sha256, engine):
    from . import installation_state as s, subagent_policy as p, subagent_registry as r, catalog
    r.fields(document, 'plan_version project_root source destination before after writes lock engine')
    p.require(document['plan_version'] == 1 and document['project_root'] == str(Path(project))
              and document['source'] == LEGACY and document['destination'] == CANONICAL
              and document['engine'] == engine and p.digest(p.encode(document)) == plan_sha256, 'layout plan changed')
    # Reconstruct the complete proposal while old state exists. An attacker-supplied
    # digest does not grant a general-purpose writer or lock editing authority.
    base = resolve(project)
    if base == LEGACY:
        p.require(plan(project, engine)['plan'] == document, 'stale layout plan')
    receipt = Path(project) / '.ai/local/project-layout-plan.json'
    accepted = p.encode(document)
    read(project, '.ai/local/project-layout-plan.json')
    if base == CANONICAL:
        p.require(read(project, '.ai/local/project-layout-plan.json') == accepted, 'accepted migration plan missing or changed')
    completion_path = '.ai/local/project-layout-complete.json'
    completed_bytes = p.encode({'plan_sha256': plan_sha256})
    completed = read(project, completion_path)
    p.require(completed in (None, completed_bytes), 'different migration completion exists')
    writes = document['writes']
    lock = document['lock']
    for row in [*writes, *([] if lock is None else [lock])]:
        r.fields(row, 'path before_sha256 after_sha256 content')
        p.require(p.digest(row['content'].encode('utf-8')) == row['after_sha256'], 'migration bytes changed')
        p.require(row['path'].startswith(CANONICAL + '/') or
                  any(row['path'].startswith(v[0]) for v in r.ADAPTERS.values()) or row['path'] == s.LOCK_PATH,
                  'migration write boundary')
    if lock is not None:
        catalog.lock_bytes(lock['content'].encode('utf-8'))
    written = []
    with writer(project) as held:
        try:
            p.require(resolve(project) == base, 'layout changed before exclusion')
            p.require(read(project, completion_path) == completed, 'migration completion changed before exclusion')
            if base == CANONICAL:
                p.require(read(project, '.ai/local/project-layout-plan.json') == accepted,
                          'accepted migration plan changed before exclusion')
            p.require(all(not (Path(project) / marker).exists() for marker in s.MARKERS), 'installation operation active')
            actual_lock = s.read_lock(project)
            current_lock = None if actual_lock is None else actual_lock.sha256
            p.require(current_lock in ({None} if lock is None else {lock['before_sha256'], lock['after_sha256']}),
                      'framework lock changed')
            complete = completed is not None or (lock is not None and current_lock == lock['after_sha256'])
            if base == LEGACY:
                p.require(inventory(project, LEGACY) == document['before'], 'layout contents changed')
            else:
                actual = inventory(project, CANONICAL)
                expected = deepcopy(document['before'])
                changes = {row['path'][len(CANONICAL) + 1:]: row for row in writes if row['path'].startswith(CANONICAL + '/')}
                for row in expected:
                    change = changes.get(row['path'])
                    if change and next((a for a in actual if a['path'] == row['path']), None) != row:
                        row.update(sha256=change['after_sha256'], size=len(change['content'].encode('utf-8')))
                p.require(actual == (document['after'] if complete else expected), 'migrated layout drift')
            for row in writes:
                name = row['path'] if base == CANONICAL else row['path'].replace(CANONICAL + '/', LEGACY + '/', 1)
                actual = p.digest(p.raw_read(r.at(project, name)))
                p.require(actual == row['after_sha256'] if complete else
                          actual in (row['before_sha256'], row['after_sha256']), 'migration resource drift')
                p.require(actual_lock is None or row['path'] not in actual_lock.members, 'managed migration collision')
            if base == LEGACY:
                p.require(plan(project, engine)['plan'] == document, 'stale layout plan after exclusion')
                if receipt.exists():
                    p.require(read(project, '.ai/local/project-layout-plan.json') == accepted, 'different accepted migration plan exists')
                else:
                    # Keep the accepted proposal outside the renamed tree. Resume
                    # never accepts arbitrary new content after the rename.
                    with receipt.open('xb') as stream:
                        stream.write(accepted)
                        stream.flush()
                        os.fsync(stream.fileno())
                    written.append('.ai/local/project-layout-plan.json')
                held.verify()
                p.require(resolve(project) == LEGACY, 'destination appeared')
                os.rename(Path(project) / LEGACY, Path(project) / CANONICAL)
                written.append(CANONICAL)
            for row in [*writes, *([] if lock is None else [lock])]:
                held.verify()
                p.require(resolve(project) == CANONICAL, 'legacy root reappeared')
                if p.digest(read(project, row['path'])) == row['after_sha256']:
                    continue
                _replace(project, row)
                written.append(row['path'])
            p.require(inventory(project, CANONICAL) == document['after'], 'final layout drift')
            if completed is None:
                with (Path(project) / completion_path).open('xb') as stream:
                    stream.write(completed_bytes)
                    stream.flush()
                    os.fsync(stream.fileno())
                written.append(completion_path)
            return {'outcome': 'applied' if written else 'unchanged', 'changed': bool(written),
                    'written': written, 'layout': CANONICAL, 'runtime_activation': 'unknown'}
        except (ValueError, OSError) as exc:
            if not written:
                raise
            return {'outcome': 'interrupted', 'changed': True, 'written': written, 'reason': str(exc),
                    'recovery': 'Preserve the accepted plan and inspect before resuming it.'}


def execute(request):
    from . import subagent_policy as p
    operation = request['operation']
    extras = {'layout-inspect': set(), 'layout-plan': set(), 'layout-apply': {'plan', 'plan_sha256'}}
    p.require(operation in extras and set(request) <= extras[operation] |
              {'operation', 'project_root', 'engine', 'engine_root'}, 'layout request')
    root = request['project_root']
    if operation == 'layout-inspect':
        return inspect(root)
    if operation == 'layout-plan':
        return plan(root, request['engine'])
    return apply(root, request['plan'], request['plan_sha256'], request['engine'])
