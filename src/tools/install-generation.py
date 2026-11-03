"""Install or recover .NET generation tools under .ai/tools/dotnet-generation."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat


def direct(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError('Linked installation path: ' + str(item))


def regular(path):
    direct(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Not a regular bundle file: ' + str(path))
    return path.read_bytes()


def verify(root):
    doc = json.loads(regular(root / 'generation.json'))
    if doc['schema'] != 'aicf-generation/1':
        raise ValueError('Unsupported generation manifest')
    names, folded = set(), {'generation.json'}
    expected_dirs = set()
    for row in doc['files']:
        name = row['path']
        parts = PurePosixPath(name).parts
        if (not parts or PurePosixPath(name).is_absolute() or any(p in ('.', '..') for p in parts)
                or '\\' in name or ':' in name or PurePosixPath(name).as_posix() != name):
            raise ValueError('Unsafe member path')
        if name.casefold() in folded:
            raise ValueError('Duplicate member path')
        folded.add(name.casefold())
        names.add(name)
        expected_dirs.update(p.as_posix() for p in PurePosixPath(name).parents if str(p) != '.')
        raw = regular(root / name)
        if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256'] or row['mode'] not in (0o644, 0o755):
            raise ValueError('Changed bundle member: ' + name)
    paths = names | expected_dirs | {'generation.json'}
    if len({p.casefold() for p in paths}) != len(paths):
        raise ValueError('Aliased bundle paths')
    actual = set()
    for path in root.rglob('*'):
        direct(path)
        name = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            actual.add(name)
        elif stat.S_ISDIR(mode):
            if name not in expected_dirs:
                raise ValueError('Unknown bundle directory')
        else:
            raise ValueError('Unsupported bundle entry: ' + name)
    if actual != names | {'generation.json'}:
        raise ValueError('Unknown or missing bundle files')
    return doc


@contextmanager
def exclusive(parent):
    """OS lock releases on process death; keep its pathname stable for all callers."""
    parent.mkdir(parents=True, exist_ok=True)
    path = parent / '.dotnet-generation-install.lock'
    direct(path)
    with path.open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'\0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def manifest_hash(root):
    verify(root)
    return hashlib.sha256(regular(root / 'generation.json')).hexdigest()


def location(project):
    project = project.absolute()
    direct(project)
    if not project.is_dir():
        raise ValueError('Project must exist')
    target = project / '.ai/tools/dotnet-generation'
    direct(target)
    stage = target.parent / '.dotnet-generation-pending'
    direct(stage)
    return target, stage


def cleanup(stage):
    # Keep the journal until all payload cleanup has finished.
    for name in ('previous', 'payload'):
        path = stage / name
        if path.exists():
            shutil.rmtree(path)
    (stage / 'transaction.json').unlink()
    stage.rmdir()


def remaining_unchanged(root, rows):
    """Cleanup may have removed files, but must preserve changed or added data."""
    expected = {row['path']: row for row in rows}
    directories = {p.as_posix() for name in expected for p in PurePosixPath(name).parents if str(p) != '.'}
    for path in root.rglob('*'):
        direct(path)
        name = path.relative_to(root).as_posix()
        if path.is_dir():
            if name not in directories:
                raise ValueError('Unknown displaced directory; reconcile manually')
            continue
        raw = regular(path)
        row = expected.get(name)
        if row is None or len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Displaced installation changed; reconcile manually')


def recover(project):
    target, stage = location(project)
    with exclusive(target.parent):
        if not stage.exists():
            return {'outcome': 'no-pending-installation', 'path': str(target)}
        if not list(stage.iterdir()):
            stage.rmdir()
            return {'outcome': 'removed-empty-stage', 'path': str(target)}
        journal = json.loads(regular(stage / 'transaction.json'))
        if set(journal) != {'before', 'after', 'before_files'}:
            raise ValueError('Unknown recovery journal')
        if {p.name for p in stage.iterdir()} - {'transaction.json', 'payload', 'previous'}:
            raise ValueError('Unknown recovery entries')
        # Never follow links or remove special objects while cleaning owned staging.
        for item in stage.rglob('*'):
            direct(item)
            if not (stat.S_ISREG(item.lstat().st_mode) or stat.S_ISDIR(item.lstat().st_mode)):
                raise ValueError('Unsupported recovery entry')
        previous = stage / 'previous'
        if target.exists():
            current = manifest_hash(target)
            if current == journal['after']:
                outcome = 'completed-installation'
            elif current == journal['before'] and not previous.exists():
                outcome = 'kept-previous-installation'
            else:
                raise ValueError('Target changed; reconcile manually')
        elif previous.exists():
            if manifest_hash(previous) != journal['before']:
                raise ValueError('Previous installation changed; reconcile manually')
            previous.rename(target)
            outcome = 'restored-previous-installation'
        elif journal['before'] is None:
            outcome = 'cancelled-new-installation'
        else:
            raise ValueError('Previous installation is missing; reconcile manually')
        if previous.exists():
            remaining_unchanged(previous, journal['before_files'])
        cleanup(stage)
        return {'outcome': outcome, 'path': str(target)}


def install(bundle, project):
    bundle = bundle.absolute()
    doc = verify(bundle)
    target, stage = location(project)
    if bundle == target or bundle.is_relative_to(target) or target.is_relative_to(bundle):
        raise ValueError('Source and destination overlap')
    with exclusive(target.parent):
        if stage.exists():
            raise ValueError('Pending installation; run --recover before retrying')
        before = manifest_hash(target) if target.exists() else None
        before_files = []
        if before is not None:
            raw = regular(target / 'generation.json')
            before_files = json.loads(raw)['files'] + [
                {'path': 'generation.json', 'size': len(raw), 'sha256': before}]
        after = hashlib.sha256(regular(bundle / 'generation.json')).hexdigest()
        stage.mkdir()
        # Journal is complete before any target rename; an invalid journal fails closed.
        (stage / 'transaction.json').write_text(json.dumps(
            {'before': before, 'after': after, 'before_files': before_files}), encoding='utf-8')
        retired, payload = stage / 'previous', stage / 'payload'
        shutil.copytree(bundle, payload)
        if manifest_hash(payload) != after:
            raise ValueError('Source changed during preparation; run --recover')
        if os.name != 'nt':
            for row in doc['files']:
                (payload / row['path']).chmod(row['mode'])
        direct(target)
        current = manifest_hash(target) if target.exists() else None
        if current != before:
            raise ValueError('Installation changed during preparation; run --recover')
        if target.exists():
            target.rename(retired)
        payload.rename(target)
        if manifest_hash(target) != after:
            raise ValueError('Installed bytes changed; run --recover')
        # Cleanup is itself recoverable while the journal exists.
        cleanup(stage)
    return {'outcome': 'installed', 'path': str(target), 'version': doc['version'], 'source_commit': doc['source_commit']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--recover', action='store_true', help='Reconcile an interrupted installation before retrying')
    args = parser.parse_args()
    print(json.dumps(recover(args.project) if args.recover else install(Path(__file__).absolute().parent, args.project)))
