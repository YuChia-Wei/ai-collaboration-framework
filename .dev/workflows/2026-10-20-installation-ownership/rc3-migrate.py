"""One-project RC3 retirement/restore bridge; never a portable upgrade route.

Use the original engine for ownership inspection. Use the released v0.20.2
public CLI separately for installation/recovery. No recursive deletion.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

TARGET = Path('C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend')
LOCK = '.ai/framework.lock'
OLD_LOCK = '1536e7ae04cb58b96cebc928d3e97d277664ce9ba1545a6e04a6b55dbbfc73a4'
NEW_PIN = '2ed639c3e6b5fd90818cf7fb1611d6461c415c8c4cd4a3ff1ae6ddb414b4100a'
GUARD = '.ai/local/installation.guard'
SCOPES = ('.ai', '.agents', '.claude', '.dev', '.codex')
ROOT_FILES = ('AGENTS.md', 'AGENTS.zh-TW.md', 'CLAUDE.md', 'README.md', 'README.en.md')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def plain(path):
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            info = item.lstat()
            require(not (getattr(info, 'st_file_attributes', 0) & 1024), f'reparse: {item}')
            require(not stat.S_ISLNK(info.st_mode), f'link: {item}')
    if path.exists() and path.is_file():
        require(path.stat().st_nlink == 1, f'hard link: {path}')
    return path


def member(root, name):
    rel = PurePosixPath(name)
    require(name == rel.as_posix() and not rel.is_absolute() and
            all(p not in ('', '.', '..') and ':' not in p and '\\' not in p for p in rel.parts),
            f'unsafe member: {name}')
    path = plain(root.joinpath(*rel.parts))
    require(path.resolve().is_relative_to(root.resolve()), f'escape: {name}')
    cursor = root
    for part in rel.parts:
        if cursor.exists():
            require(cursor.is_dir(), f'ancestor is not a directory: {cursor}')
            matches = [p.name for p in cursor.iterdir() if p.name.casefold() == part.casefold()]
            require(not matches or matches == [part], f'case alias: {name}')
        cursor = cursor / part
    if path.exists():
        require(path.is_file(), f'not a regular member: {name}')
    return path


def raw_hash(path):
    plain(path)
    return digest(path.read_bytes()) if path.exists() else None


def save(path, value):
    data = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    plain(path)
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return digest(data)


def inventory(root):
    result = {}
    for scope in SCOPES:
        start = plain(root / scope)
        if not start.exists():
            continue
        for directory, directories, files in os.walk(start, followlinks=False):
            for name in directories + files:
                plain(Path(directory) / name)
            for name in files:
                path = Path(directory) / name
                result[path.relative_to(root).as_posix()] = raw_hash(path)
    for name in ROOT_FILES:
        if (root / name).exists():
            result[name] = raw_hash(root / name)
    return result


def git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.safecrlf=false', '-C', str(root), *args]).decode().strip()


def verify_git_preimages(root, head, owned):
    for name, expected in owned.items():
        content = subprocess.check_output(['git', '-C', str(root), 'show', head + ':' + name])
        require(digest(content) == expected, f'Git cannot restore exact owned bytes: {name}')


def inspect_old(root, engine, output):
    require(raw_hash(root / LOCK) == OLD_LOCK, 'original project lock changed')
    pin = json.loads((root / LOCK).read_bytes())['engine']
    require(pin['source_commit'] == '5ed50d1b59115a2677711dbb91fcb8cc12dc2148', 'wrong old source')
    for row in pin['files']:
        require(raw_hash(member(engine, row['path'])) == row['sha256'], 'old engine bytes changed')
    request = dict(api_version=2, operation='inspect', project_root=str(root),
                   engine_root=str(engine), engine=pin)
    save(output.with_suffix('.request.json'), request)
    process = subprocess.run([sys.executable, '-I', '-B', str(engine / 'src/tools/maintain_framework.py')],
                             input=json.dumps(request).encode(), capture_output=True, timeout=120)
    output.write_bytes(process.stdout)
    output.with_suffix('.stderr.txt').write_bytes(process.stderr)
    require(process.returncode == 0, f'old inspection failed; see {output}')
    response = json.loads(process.stdout)
    details = response['details']
    require(details['managed_state'] == 'managed-bytes-consistent' and details['drift'] == [], 'managed drift')
    rows = details['owned']
    require(len(rows) == 135 and len({r['destination'].casefold() for r in rows}) == 135, 'unexpected ownership')
    return {r['destination']: r['sha256'] for r in rows}


def no_markers(root):
    for name in ('.ai/framework.operation', '.ai/config-transition.operation'):
        require(not member(root, name).exists(), f'recover original operation first: {name}')


def prepare(args, root, operation):
    require(not operation.exists(), 'choose a new external operation directory')
    require(not git(root, 'diff', '--name-only', 'HEAD'), 'tracked changes before snapshot')
    no_markers(root)
    require(not member(root, '.ai/local/installation.guard').exists(), 'preexisting guard has no retirement authority')
    operation.mkdir(parents=True)
    owned = inspect_old(root, args.engine.resolve(), operation / 'inspect.json')
    owned[LOCK] = OLD_LOCK
    baseline = inventory(root)
    for name, expected in owned.items():
        require(baseline.get(name) == expected, f'owned preimage changed: {name}')
    head = git(root, 'rev-parse', 'HEAD')
    verify_git_preimages(root, head, owned)
    require(inventory(root) == baseline, 'snapshot changed')
    manifest = dict(project_root=str(root), head=head,
                    engine_root=str(args.engine.resolve()), owned=owned, baseline=baseline,
                    untracked=git(root, 'ls-files', '--others', '--exclude-standard').splitlines())
    print(json.dumps({'manifest_sha256': save(operation / 'manifest.json', manifest),
                      'retire_files': len(owned), 'observed_files': len(baseline)}))


def load(args, root, operation):
    path = plain(operation / 'manifest.json')
    require(raw_hash(path) == args.manifest_sha256, 'manifest hash mismatch')
    manifest = json.loads(path.read_bytes())
    require(manifest['project_root'] == str(root), 'different target')
    require(git(root, 'rev-parse', 'HEAD') == manifest['head'], 'HEAD changed')
    for name, expected in manifest['owned'].items():
        member(root, name)
    verify_git_preimages(root, manifest['head'], manifest['owned'])
    return manifest


def retire(args, root, operation, manifest):
    no_markers(root)
    require(inventory(root) == manifest['baseline'], 'project drift since snapshot')
    fresh = inspect_old(root, Path(manifest['engine_root']), operation / 'retire-inspect.json')
    require(fresh == {k: v for k, v in manifest['owned'].items() if k != LOCK}, 'ownership changed')
    require(not args.stop_after or root != TARGET.resolve(), 'fault injection is fixture-only')
    # Durable complete intent precedes the first deletion. Missing owned members
    # can be restored from this pinned Git revision even if the process dies next.
    save(operation / 'retirement-intent.json', {'manifest_sha256': args.manifest_sha256})
    names = sorted(k for k in manifest['owned'] if k != LOCK) + [LOCK]
    for count, name in enumerate(names, 1):
        path = member(root, name)
        require(raw_hash(path) == manifest['owned'][name], f'retirement drift: {name}')
        path.unlink()
        if args.stop_after == count:
            raise RuntimeError(f'fixture interruption after {count} deletions')
    print(json.dumps({'retired': len(names)}))


def remove_restored_guard(args, root, operation, manifest):
    """Retire only this fresh-install residue after official restore verification."""
    require(GUARD not in manifest['baseline'], 'guard predated this migration')
    require(raw_hash(member(root, GUARD)) == digest(b''), 'unknown guard content')
    require(args.recovery_request is not None, 'provide the original official restore request')
    require(raw_hash(args.recovery_request) == args.recovery_request_sha256, 'recovery request changed')
    request = json.loads(args.recovery_request.read_bytes())
    require(request['project_root'] == str(root) and request['direction'] == 'restore', 'wrong recovery target')
    require(digest(json.dumps(request['engine'], sort_keys=True, separators=(',', ':')).encode()) == NEW_PIN,
            'wrong public v0.20.2 engine pin')
    engine = plain(Path(request['engine_root']))
    for row in request['engine']['files']:
        require(raw_hash(member(engine, row['path'])) == row['sha256'], 'new engine changed')
    request['expected_lock_sha256'] = None
    request['expected_marker_sha256'] = None
    # Replaying restore after marker removal is read-only and must prove the
    # complete exact before state. Completed successful installs cannot pass.
    process = subprocess.run([sys.executable, '-I', '-B', str(engine / 'src/tools/maintain_framework.py')],
                             input=json.dumps(request).encode(), capture_output=True, timeout=180)
    (operation / 'restore-recheck.json').write_bytes(process.stdout)
    (operation / 'restore-recheck.stderr').write_bytes(process.stderr)
    require(process.returncode == 0, 'official restoration recheck failed')
    result = json.loads(process.stdout)
    require(result['outcome'] == 'already-matching' and result['changed'] is False and
            result['details']['managed_state'] == 'uninstalled', 'official before state not proven')
    require(os.name == 'nt', 'this residue retirement is Windows-only')
    import ctypes
    from ctypes import wintypes
    import msvcrt
    path = member(root, GUARD)
    before = path.stat()
    native = ctypes.WinDLL('kernel32', use_last_error=True)
    native.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    native.CreateFileW.restype = wintypes.HANDLE
    # Zero sharing rejects any other open writer; disposition deletes the same
    # held file on close, avoiding a close-then-unlink pathname race.
    handle = native.CreateFileW(str(path), 0x80000000 | 0x10000, 0, None, 3, 0x80, None)
    require(handle != ctypes.c_void_p(-1).value, 'guard is open or inaccessible')
    descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY)
    try:
        opened = os.fstat(descriptor)
        require((opened.st_dev, opened.st_ino, opened.st_size, opened.st_nlink) ==
                (before.st_dev, before.st_ino, 0, 1), 'guard identity changed')
        native.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        native.SetFileInformationByHandle.restype = wintypes.BOOL
        disposition = ctypes.c_ubyte(1)
        require(native.SetFileInformationByHandle(handle, 4, ctypes.byref(disposition), ctypes.sizeof(disposition)),
                'cannot retire verified guard')
    finally:
        os.close(descriptor)
    require(not path.exists(), 'guard retirement incomplete')


def restore(args, root, operation, manifest):
    no_markers(root)
    # The formal new installer must recover to its before state first.
    current = inventory(root)
    expected = manifest['baseline']
    residue = {GUARD} if GUARD not in expected and GUARD in current else set()
    require({k: v for k, v in current.items() if k not in manifest['owned'] and k not in residue} ==
            {k: v for k, v in expected.items() if k not in manifest['owned']},
            'non-owned state differs; recover new operation before old restoration')
    for name, value in manifest['owned'].items():
        require(current.get(name) in (None, value), f'unknown replacement: {name}')
    if residue:
        remove_restored_guard(args, root, operation, manifest)
    missing = sorted(k for k in manifest['owned'] if k != LOCK and k not in current)
    if missing:
        git(root, 'restore', '--source=' + manifest['head'], '--worktree', '--', *missing)
    if LOCK not in current:
        git(root, 'restore', '--source=' + manifest['head'], '--worktree', '--', LOCK)
    require(inventory(root) == expected, 'restoration incomplete')
    print(json.dumps({'restored': True, 'files': len(expected)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'retire', 'restore'))
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--operation', required=True, type=Path)
    parser.add_argument('--engine', type=Path)
    parser.add_argument('--manifest-sha256')
    parser.add_argument('--stop-after', type=int, default=0)
    parser.add_argument('--recovery-request', type=Path)
    parser.add_argument('--recovery-request-sha256')
    args = parser.parse_args()
    root = plain(args.project).resolve()
    operation = plain(args.operation).resolve()
    require(root == TARGET.resolve() or root.is_relative_to(Path('C:/tmp/mig202').resolve()), 'unselected target')
    require(not operation.is_relative_to(root) and not root.is_relative_to(operation), 'evidence directory overlaps project')
    if args.action == 'prepare':
        require(args.engine is not None, 'old engine required')
        prepare(args, root, operation)
    else:
        manifest = load(args, root, operation)
        if args.action == 'retire':
            retire(args, root, operation, manifest)
        else:
            restore(args, root, operation, manifest)


if __name__ == '__main__':
    main()
