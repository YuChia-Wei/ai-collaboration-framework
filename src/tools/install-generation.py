"""Install or recover .NET generation tools under .ai/tools/dotnet-generation."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys


class InstallationError(ValueError):
    """Expected refusal with a stable CLI diagnostic code."""

    def __init__(self, code, reason):
        super().__init__(reason)
        self.code = code


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise InstallationError('invalid-arguments', message)


def direct(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise InstallationError('linked-path', 'Linked installation path: ' + str(item)
                                        + '. Inspect the link, then supply the intended physical path'
                                        + ' (for example, the result of realpath on POSIX).')


def regular(path):
    direct(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise InstallationError('invalid-bundle', 'Not a regular bundle file: ' + str(path))
    return path.read_bytes()


def verify(root):
    doc = json.loads(regular(root / 'generation.json'))
    if not isinstance(doc, dict) or any(
            not isinstance(doc.get(name), str) or not doc[name].strip()
            for name in ('version', 'source_commit')):
        raise InstallationError('invalid-bundle', 'Bundle version and source_commit must be non-empty strings')
    if doc['schema'] != 'aicf-generation/1':
        raise InstallationError('invalid-bundle', 'Unsupported generation manifest')
    names, folded = set(), {'generation.json'}
    expected_dirs = set()
    for row in doc['files']:
        name = row['path']
        parts = PurePosixPath(name).parts
        if (not parts or PurePosixPath(name).is_absolute() or any(p in ('.', '..') for p in parts)
                or '\\' in name or ':' in name or PurePosixPath(name).as_posix() != name):
            raise InstallationError('invalid-bundle', 'Unsafe member path')
        if name.casefold() in folded:
            raise InstallationError('invalid-bundle', 'Duplicate member path')
        folded.add(name.casefold())
        names.add(name)
        expected_dirs.update(p.as_posix() for p in PurePosixPath(name).parents if str(p) != '.')
        raw = regular(root / name)
        if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256'] or row['mode'] not in (0o644, 0o755):
            raise InstallationError('bundle-changed', 'Changed bundle member: ' + name)
    paths = names | expected_dirs | {'generation.json'}
    if len({p.casefold() for p in paths}) != len(paths):
        raise InstallationError('invalid-bundle', 'Aliased bundle paths')
    actual = set()
    for path in root.rglob('*'):
        direct(path)
        name = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            actual.add(name)
        elif stat.S_ISDIR(mode):
            if name not in expected_dirs:
                raise InstallationError('invalid-bundle', 'Unknown bundle directory')
        else:
            raise InstallationError('invalid-bundle', 'Unsupported bundle entry: ' + name)
    if actual != names | {'generation.json'}:
        raise InstallationError('invalid-bundle', 'Unknown or missing bundle files')
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
        raise InstallationError('project-not-found', 'Project must exist')
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
                raise InstallationError('recovery-conflict', 'Unknown displaced directory; reconcile manually')
            continue
        raw = regular(path)
        row = expected.get(name)
        if row is None or len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise InstallationError('recovery-conflict', 'Displaced installation changed; reconcile manually')


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
            raise InstallationError('invalid-recovery', 'Unknown recovery journal')
        if {p.name for p in stage.iterdir()} - {'transaction.json', 'payload', 'previous'}:
            raise InstallationError('invalid-recovery', 'Unknown recovery entries')
        # Never follow links or remove special objects while cleaning owned staging.
        for item in stage.rglob('*'):
            direct(item)
            if not (stat.S_ISREG(item.lstat().st_mode) or stat.S_ISDIR(item.lstat().st_mode)):
                raise InstallationError('invalid-recovery', 'Unsupported recovery entry')
        previous = stage / 'previous'
        if target.exists():
            current = manifest_hash(target)
            if current == journal['after']:
                outcome = 'completed-installation'
            elif current == journal['before'] and not previous.exists():
                outcome = 'kept-previous-installation'
            else:
                raise InstallationError('recovery-conflict', 'Target changed; reconcile manually')
        elif previous.exists():
            if manifest_hash(previous) != journal['before']:
                raise InstallationError('recovery-conflict', 'Previous installation changed; reconcile manually')
            previous.rename(target)
            outcome = 'restored-previous-installation'
        elif journal['before'] is None:
            outcome = 'cancelled-new-installation'
        else:
            raise InstallationError('recovery-conflict', 'Previous installation is missing; reconcile manually')
        if previous.exists():
            remaining_unchanged(previous, journal['before_files'])
        cleanup(stage)
        return {'outcome': outcome, 'path': str(target)}


def install(bundle, project):
    bundle = bundle.absolute()
    doc = verify(bundle)
    target, stage = location(project)
    if bundle == target or bundle.is_relative_to(target) or target.is_relative_to(bundle):
        raise InstallationError('overlapping-paths', 'Source and destination overlap')
    with exclusive(target.parent):
        if stage.exists():
            raise InstallationError('pending-installation', 'Pending installation; run --recover before retrying')
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
            raise InstallationError('concurrent-change', 'Source changed during preparation; run --recover')
        if os.name != 'nt':
            for row in doc['files']:
                (payload / row['path']).chmod(row['mode'])
        direct(target)
        current = manifest_hash(target) if target.exists() else None
        if current != before:
            raise InstallationError('concurrent-change', 'Installation changed during preparation; run --recover')
        if target.exists():
            target.rename(retired)
        payload.rename(target)
        if manifest_hash(target) != after:
            raise InstallationError('concurrent-change', 'Installed bytes changed; run --recover')
        # Cleanup is itself recoverable while the journal exists.
        cleanup(stage)
    return {'outcome': 'installed', 'path': str(target), 'version': doc['version'], 'source_commit': doc['source_commit']}


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--recover', action='store_true', help='Reconcile an interrupted installation before retrying')
    try:
        args = parser.parse_args(argv)
        result = recover(args.project) if args.recover else install(Path(__file__).absolute().parent, args.project)
    except InstallationError as exc:
        result = {'outcome': 'blocked', 'code': exc.code, 'reason': str(exc)}
    except OSError as exc:
        result = {'outcome': 'blocked', 'code': 'filesystem-error', 'reason': str(exc)}
    except (ValueError, KeyError, TypeError) as exc:
        result = {'outcome': 'blocked', 'code': 'invalid-data', 'reason': str(exc)}
    else:
        print(json.dumps(result))
        return 0
    print(json.dumps(result), file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
