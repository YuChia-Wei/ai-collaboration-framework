"""Small disposable-fixture helpers; no product/config/native policy lives here."""
from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.metadata
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

REPOSITORY = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
MAX_FILES = 256
MAX_RETAINED_BYTES = 16 * 1024 * 1024
MAX_AUTHORED_BYTES = 1024 * 1024
MAX_NORMAL_INPUT = 16 * 1024
MAX_PROCESSES = 256
ACTIVE = None


class FixtureError(RuntimeError):
    pass


def check(condition, message):
    if not condition:
        raise FixtureError(message)


def direct_directory(path):
    """Existing absolute path, no traversal, symlink or reparse ancestor."""
    path = Path(path)
    check(path.is_absolute() and '..' not in path.parts, 'root must be absolute without traversal')
    check(not str(path).startswith(('\\\\', '//')), 'network/device roots are refused')
    for part in path.parts[1:]:
        check(not part.endswith(('.', ' ')) and not re.search(r'[<>:"|?*\x00-\x1f]', part)
              and not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part),
              'ambiguous fixture path segment')
    for current in (path, *path.parents):
        info = current.lstat()
        check(not stat.S_ISLNK(info.st_mode) and not
              getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
              'linked/reparse fixture paths are refused')
        check(stat.S_ISDIR(info.st_mode), 'fixture ancestor must be a directory')
    # lstat established existence and direct ancestry. No final-path syscall is
    # needed: some direct Windows RAM filesystems refuse that optional API.
    return Path(os.path.abspath(path))


def output_parent(explicit=None, environment=None):
    """CLI > new env > OS temp. No legacy setting, drive search or global mutation."""
    environment = os.environ if environment is None else environment
    choice = explicit if explicit is not None else environment.get('FRAMEWORK_TEST_OUTPUT_ROOT')
    value = Path(tempfile.gettempdir()) if choice is None else Path(choice)
    check(bool(str(choice)) if choice is not None else True, 'empty explicit root is refused')
    check(value.is_absolute() and '..' not in value.parts, 'root must be absolute without traversal')
    check(value != Path(value.anchor), 'drive/filesystem root is unsafe')
    parent = direct_directory(value.parent)
    resolved = parent / value.name
    check(not resolved.is_relative_to(REPOSITORY) and not REPOSITORY.is_relative_to(resolved),
          'fixture root must be outside and not contain the source worktree')
    if not value.exists():
        value.mkdir(mode=0o700)  # only this explicit leaf; never mkdir(parents=True)
    return direct_directory(value)


class FixtureRun:
    """One exclusive run; successful close deletes only its verified owned tree."""
    def __init__(self, output_root=None, *, environment=None):
        self.parent = output_parent(output_root, environment)
        self.root = self.parent / ('fn-' + uuid.uuid4().hex)
        self.root.mkdir(mode=0o700)
        info = self.root.lstat()
        self.identity = (info.st_dev, info.st_ino)
        self.started = time.monotonic()
        self.seen = {}
        self.authored_bytes = 0
        self.processes = {'git': 0, 'python': 0, 'other': 0}
        self.closed = False

    def verify(self):
        check(not self.closed, 'fixture run is closed')
        check(direct_directory(self.root).parent == self.parent, 'run containment changed')
        info = self.root.lstat()
        check((info.st_dev, info.st_ino) == self.identity, 'owned run identity changed; retain residue')

    def case(self, name):
        self.verify()
        check(re.fullmatch(r'[a-z][a-z0-9-]*', name) is not None, 'case must be a simple name')
        target = self.root / name
        target.mkdir(mode=0o700)  # duplicates fail; no silent case reuse
        return target

    def write(self, path, raw):
        self.verify()
        path = Path(path)
        check(path.is_absolute() and path.is_relative_to(self.root) and '..' not in path.parts,
              'fixture write escaped owned run')
        check(type(raw) is bytes and len(raw) <= MAX_NORMAL_INPUT, 'normal authored fixture exceeds 16 KiB')
        check(self.authored_bytes + len(raw) <= MAX_AUTHORED_BYTES, 'authored fixture budget exceeded')
        direct_directory(path.parent)
        with path.open('xb') as stream:
            stream.write(raw)
        self.authored_bytes += len(raw)
        self.measure()
        return path

    def measure(self):
        self.verify()
        count = total = 0
        pending = [self.root]
        while pending:
            directory = pending.pop()
            for item in directory.iterdir():
                info = item.lstat()
                check(not stat.S_ISLNK(info.st_mode) and not
                      getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                      'linked residue retained; cleanup refused')
                if stat.S_ISDIR(info.st_mode):
                    pending.append(item)
                else:
                    check(stat.S_ISREG(info.st_mode), 'nonregular residue retained')
                    count += 1
                    total += info.st_size
                    key = item.relative_to(self.root).as_posix()
                    self.seen[key] = max(self.seen.get(key, 0), info.st_size)
                    check(len(self.seen) <= MAX_FILES, 'created file observation cap exceeded; retain residue')
                    check(total <= MAX_RETAINED_BYTES, 'retained byte cap exceeded; retain residue')
        return {'observed_files': len(self.seen), 'observed_logical_bytes': sum(self.seen.values()),
                'retained_files': count, 'retained_bytes': total, 'authored_bytes': self.authored_bytes,
                'processes': dict(self.processes), 'process_total': sum(self.processes.values()),
                'wall_seconds': round(time.monotonic() - self.started, 3)}

    def close(self, success):
        observation = self.measure()
        if success:
            # Full no-link walk and root identity/containment are checked immediately
            # before recursive deletion. The supplied parent is never removed.
            self.verify()
            shutil.rmtree(self.root)
            self.closed = True
        observation['residue'] = None if success else str(self.root)
        observation['next_action'] = None if success else 'Inspect recorded failure and this owned run before explicit cleanup.'
        return observation


def _process_audit(event, args):
    if event != 'subprocess.Popen' or ACTIVE is None:
        return
    executable = args[0]
    if executable is None:
        argv = args[1]
        if isinstance(argv, str):  # Windows audit reports a command line and None executable.
            match = re.match(r'^\s*(?:"([^"]+)"|(\S+))', argv)
            executable = (match.group(1) or match.group(2)) if match else ''
        else:
            executable = argv[0]
    executable = Path(str(executable)).name.lower()
    kind = 'git' if executable in {'git', 'git.exe'} else 'python' if executable.startswith('python') else 'other'
    check(sum(ACTIVE.processes.values()) < MAX_PROCESSES, 'process cap exceeded; retain residue')
    ACTIVE.processes[kind] += 1


sys.addaudithook(_process_audit)


@contextmanager
def use_run(run):
    global ACTIVE
    previous, ACTIVE = ACTIVE, run
    try:
        yield run
    finally:
        ACTIVE = previous


def active_run():
    check(ACTIVE is not None, 'invoke selected tests through run.py')
    return ACTIVE


def run_process(argv, *, cwd, input=None, timeout=30):
    """Bytes stdin/stdout, shell=False, finite timeout; caller must name cwd.

    Selected trusted tools emit bounded output. The 8 MiB post-capture check is
    not a streaming memory bound and this helper is not for untrusted programs.
    Audit counts include in-process product subprocesses, not opaque grandchildren.
    """
    result = subprocess.run([str(x) for x in argv], cwd=cwd, input=input,
                            capture_output=True, timeout=timeout, shell=False)
    check(len(result.stdout) + len(result.stderr) <= 8 * 1024 * 1024, 'captured output budget exceeded')
    return result


def git(*args, cwd=REPOSITORY, input=None):
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
               GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(cwd), *args],
                            cwd=REPOSITORY, input=input, capture_output=True, timeout=30, env=env)
    check(result.returncode == 0, f'Git {args[0]} failed: {result.stderr.decode(errors="replace")}')
    check(len(result.stdout) <= 8 * 1024 * 1024, 'Git capture budget exceeded')
    return result.stdout


def runtime_versions():
    check((3, 11) <= sys.version_info < (4, 0), 'unavailable: Python >=3.11,<4 required')
    values = {'python': sys.version.split()[0], 'executable': PYTHON}
    for name, minimum, ceiling in [('PyYAML', (6, 0), 7), ('jsonschema', (4, 18), 5),
                                    ('referencing', (0, 0), None)]:
        value = importlib.metadata.version(name)
        pair = tuple(int(x) for x in value.split('.')[:2])
        check(pair >= minimum and (ceiling is None or pair[0] < ceiling), f'unavailable: unsupported {name}')
        values[name] = value
    return values


def git_blobs(commit, paths):
    """Read only explicit paths at a full commit; batch protocol, no worktree copy.

    Returns actual Blob objects for the owner's loader/selector, not a metadata
    parser. Nonregular/missing inputs fail. GitSource itself has separate tests.
    """
    from distribution.git_source import Blob
    check(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', commit) is not None, 'full commit required')
    paths = sorted(set(paths))
    check(paths and all(p.startswith('src/') and '..' not in p.split('/') for p in paths), 'explicit src paths required')
    rows = git('ls-tree', '-rz', '--full-tree', commit, '--', *paths).split(b'\0')
    entries = {}
    for row in filter(None, rows):
        header, raw_name = row.split(b'\t', 1)
        mode, kind, oid = header.decode('ascii').split()
        name = raw_name.decode('utf-8')
        check(name in paths and kind == 'blob' and mode in {'100644', '100755'}, 'nonregular or unexpected Git member')
        entries[name] = (mode, oid)
    check(set(entries) == set(paths), 'missing exact Git members')
    raw = git('cat-file', '--batch', input=''.join(entries[p][1] + '\n' for p in paths).encode('ascii'))
    offset, blobs = 0, {}
    for name in paths:
        end = raw.index(b'\n', offset)
        oid, kind, size = raw[offset:end].decode('ascii').split()
        size = int(size)
        data = raw[end + 1:end + 1 + size]
        mode, expected_oid = entries[name]
        check(oid == expected_oid and kind == 'blob' and len(data) == size, 'Git batch identity mismatch')
        digest = sha1 if len(oid) == 40 else sha256
        check(digest(b'blob ' + str(size).encode() + b'\0' + data).hexdigest() == oid, 'Git blob digest mismatch')
        offset = end + size + 2
        check(raw[offset - 1:offset] == b'\n', 'Git batch separator mismatch')
        blobs[name] = Blob(name, oid, mode, data)
    check(offset == len(raw), 'unexpected Git batch bytes')
    return blobs
