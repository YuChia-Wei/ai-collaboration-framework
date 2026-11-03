"""Install a verified generation bundle into .ai/tools/dotnet-generation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile


def direct(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError('Linked installation path: ' + str(item))


def verify(root):
    direct(root)
    doc = json.loads((root / 'generation.json').read_text(encoding='utf-8'))
    if doc['schema'] != 'aicf-generation/1':
        raise ValueError('Unsupported generation manifest')
    names = set()
    for row in doc['files']:
        name = row['path']
        parts = PurePosixPath(name).parts
        if not parts or PurePosixPath(name).is_absolute() or any(p in ('.', '..') for p in parts) or '\\' in name or ':' in name:
            raise ValueError('Unsafe member path')
        if name.casefold() in names or name == 'generation.json':
            raise ValueError('Duplicate member path')
        names.add(name.casefold())
        path = root / name
        direct(path)
        raw = path.read_bytes()
        if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256'] or row['mode'] not in (0o644, 0o755):
            raise ValueError('Changed bundle member: ' + name)
    actual = set()
    expected_dirs = {str(parent).replace('\\', '/').casefold()
                     for name in names for parent in PurePosixPath(name).parents if str(parent) != '.'}
    for path in root.rglob('*'):
        direct(path)
        if path.is_file():
            actual.add(path.relative_to(root).as_posix().casefold())
        elif path.is_dir() and path.relative_to(root).as_posix().casefold() not in expected_dirs:
            raise ValueError('Unknown bundle directory')
    if actual != names | {'generation.json'}:
        raise ValueError('Unknown or missing bundle files')
    return doc


def install(bundle, project):
    bundle = bundle.absolute()
    project = project.absolute()
    direct(project)
    if not project.is_dir():
        raise ValueError('Project must exist')
    doc = verify(bundle)
    target = project / '.ai/tools/dotnet-generation'
    direct(target)
    if bundle == target or bundle.is_relative_to(target) or target.is_relative_to(bundle):
        raise ValueError('Source and destination overlap')
    previous = verify(target) if target.exists() else None
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / '.dotnet-generation-install.lock'
    guard = lock.open('x')
    try:
        stage = Path(tempfile.mkdtemp(prefix='.generation-stage-', dir=target.parent))
        retired = stage / 'previous'
        payload = stage / 'payload'
        try:
            shutil.copytree(bundle, payload)
            verify(payload)
            for row in doc['files']:
                if os.name != 'nt':
                    (payload / row['path']).chmod(row['mode'])
            direct(target)
            if target.exists():
                if previous is None or verify(target) != previous:
                    raise ValueError('Installation changed during preparation')
                target.rename(retired)
            elif previous is not None:
                raise ValueError('Installation disappeared during preparation')
            try:
                payload.rename(target)
            except BaseException:
                if retired.exists():
                    retired.rename(target)
                raise
            verify(target)
        finally:
            # Retain a displaced installation if an interrupted replacement needs recovery.
            if retired.exists() and not target.exists():
                raise ValueError('Recovery required at ' + str(stage))
            shutil.rmtree(stage)
    finally:
        guard.close()
        lock.unlink()
    return {'outcome': 'installed', 'path': str(target), 'version': doc['version'], 'source_commit': doc['source_commit']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(install(Path(__file__).absolute().parent, args.project)))
