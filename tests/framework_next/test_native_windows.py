"""Issue 382 bounded native observations. All outputs retained; no product hooks."""
from __future__ import annotations
import ast
import base64
import ctypes
from ctypes import wintypes as w
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import queue
import stat
import struct
import subprocess
import sys
import threading
import time
import uuid

HERE = Path(__file__).absolute().parent
SOURCE = HERE.parents[1]
NATIVE = Path('F:/framework-next/p7-runs/native-w01/382')
BOOTSTRAP = Path('C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend')
DURABLE = BOOTSTRAP / '.dev/ai-context/local/p7/n382'
RECOVERY, OBSERVATIONS = DURABLE / 'recovery', DURABLE / 'observations'
CASES = ('entry-pin', 'fresh-apply', 'same-content', 'drift-collision', 'writer-exclusion', 'interruption-recovery')
LOCK, MARKER, GUARD = '.ai/framework.lock', '.ai/framework.operation', '.ai/local/installation.guard'
MAX_FILES, MAX_BYTES = 256, 16 * 1024 * 1024


def check(value, reason):
    if not value:
        raise RuntimeError(reason)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def digest(path):
    return sha256(path.read_bytes()).hexdigest() if path.exists() else None


def direct(path):
    check(path.is_absolute() and '..' not in path.parts and not str(path).startswith(('\\\\', '//')), 'direct local root required')
    devices = set()
    for item in (path, *path.parents):
        info = item.lstat()
        check(stat.S_ISDIR(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400, 'linked/nondirectory root')
        check(info.st_dev and info.st_ino, 'identity unavailable')
        devices.add(info.st_dev)
    check(len(devices) == 1, 'nested volume refused')


def snapshot(root):
    direct(root)
    rows, pending = {}, [root]
    while pending:
        for target in pending.pop().iterdir():
            info = target.lstat()
            check(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400, 'linked residue retained')
            if stat.S_ISDIR(info.st_mode):
                pending.append(target)
            else:
                check(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'nonregular/hardlinked residue')
                check(len(rows) < MAX_FILES and info.st_size <= MAX_BYTES, 'file observation cap')
                rows[target.relative_to(root).as_posix()] = {'sha256': digest(target), 'size': info.st_size,
                    'mtime_ns': info.st_mtime_ns, 'mode': stat.S_IMODE(info.st_mode)}
    return rows


class NativeRun:
    def __init__(self):
        self.launches, self.children, self.seen = [], [], {}
        self.git_launches = self.max_children = 0
        self.started = time.monotonic()
        self.result = {'interface': 'native-windows/382-v1', 'selection': list(CASES), 'outcome': 'not-passed',
            'exit': 2, 'cases': [], 'launches': self.launches, 'interruption_attempts': 0, 'failure_domain': 'process-termination',
            'project_readiness': 'not-assessed', 'nested_child_launches': 'unavailable; product Git grandchildren not instrumented',
            'cleanup': 'retain all roots; program 322 coordinator owns disposition',
            'started_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
        self.identities = {}

    def prepare(self, parent):
        check(os.name == 'nt' and sys.flags.isolated and sys.flags.dont_write_bytecode, 'requires native Windows Python -I -B')
        check(Path(parent) == NATIVE and SOURCE == Path('F:/framework-next/382'), 'wrong Issue 382 root binding')
        roots = (SOURCE, NATIVE, RECOVERY, OBSERVATIONS)
        for root in roots:
            direct(root)
        for i, root in enumerate(roots):
            for other in roots[i + 1:]:
                check(not root.is_relative_to(other) and not other.is_relative_to(root), 'root overlap')
                check((root.stat().st_dev, root.stat().st_ino) != (other.stat().st_dev, other.stat().st_ino), 'root alias')
        relative = [str(path.relative_to(BOOTSTRAP)) for path in (RECOVERY, OBSERVATIONS)]
        check(not self.git('ls-files', '--', *relative, cwd=BOOTSTRAP).strip(), 'durable paths tracked')
        check(len(self.git('check-ignore', '--', *relative, cwd=BOOTSTRAP).splitlines()) == 2, 'durable paths not ignored')
        check(not self.git('status', '--porcelain=v1', '--untracked-files=all').strip(), 'source not clean')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        branch = self.git('branch', '--show-current').decode().strip()
        check(branch == 'codex/2026-09-23-native-maintenance-checks', 'wrong branch')
        self.result.update(source_commit=self.commit, source_root=str(SOURCE), branch=branch,
            command=[sys.executable, '-I', '-B', str(HERE / 'run.py'), '--layer', 'native-windows', '--native-root', str(NATIVE)])
        token = uuid.uuid4().hex[:8]
        self.root, self.recovery, self.observations = NATIVE / token, RECOVERY / token, OBSERVATIONS / token
        for path in (self.root, self.recovery, self.observations):
            path.mkdir()  # exclusive, never reuse previous evidence
            self.identities[path] = (path.stat().st_dev, path.stat().st_ino)
        self.result['roots'] = dict(native=str(self.root), recovery=str(self.recovery), observations=str(self.observations))
        for name in ('project', 'candidates', 'build-scratch', 'scratch', 'staging', 'observations'):
            (self.root / name).mkdir()
        self.project = self.root / 'project'
        self.transcript = self.observations / 'calls.jsonl'
        self.result['transcript'] = str(self.transcript)
        tree = ast.parse((SOURCE / 'src/tools/maintain_framework.py').read_text(encoding='utf-8'))
        declarations = [n for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'ENGINE_FILES' for t in n.targets)]
        check(len(declarations) == 1, 'bootstrap closure unavailable')
        files = ast.literal_eval(declarations[0].value)
        check(type(files) is tuple and len(files) == 10 and tuple(sorted(files)) == files, 'unexpected engine closure')
        self.pin = dict(id='framework-managed-installation', version='1.0.0', source_commit=self.commit,
            files=[dict(path=name, sha256=digest(SOURCE / name)) for name in files])
        self.result['engine_pin'] = self.pin
        import importlib.metadata
        self.result['runtime'] = dict(python=sys.version, executable=sys.executable, os=os.name,
                                      pyyaml=importlib.metadata.version('PyYAML'))
        self.source_caches = self.caches()
        self.write(self.observations / 'engine-pin.json', encoded(self.pin))
        self.save()

    def git(self, *args, cwd=SOURCE):
        self.git_launches += 1
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
        env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
        result = subprocess.run(['git', '--no-replace-objects', '-C', str(cwd), *args], cwd=SOURCE,
                                capture_output=True, timeout=20, env=env)
        check(result.returncode == 0, 'Git preflight failed: ' + result.stderr.decode(errors='replace'))
        return result.stdout

    def caches(self):
        return sorted(str(p) for directory in (SOURCE / 'src/distribution', SOURCE / 'src/tools')
                      for p in directory.glob('__pycache__/*.pyc'))

    def write(self, path, raw):
        check(any(path.is_relative_to(root) for root in self.identities), 'write escaped owned roots')
        check(len(raw) <= MAX_BYTES, 'single output cap')
        path.parent.mkdir(parents=True, exist_ok=True)
        direct(path.parent)
        with path.open('xb') as stream:
            stream.write(raw)

    def account(self):
        count = total = 0
        for root, identity in self.identities.items():
            check((root.stat().st_dev, root.stat().st_ino) == identity, 'root identity changed')
            for name, info in snapshot(root).items():
                key = str(root / name)
                self.seen[key] = max(self.seen.get(key, 0), info['size'])
                count += 1
                total += info['size']
        operations = list(self.recovery.glob('i-*')) if hasattr(self, 'recovery') else []
        check(len(self.seen) <= MAX_FILES and total <= MAX_BYTES and len(operations) <= 3, 'file/byte/operation cap exceeded')
        return dict(observed_created_file_names=len(self.seen), observed_logical_bytes=sum(self.seen.values()),
            retained_files=count, retained_logical_bytes=total, public_helper_launches=len(self.launches),
            driver_git_launches=self.git_launches, maximum_simultaneous_owned_children=self.max_children,
            retained_operation_roots=len(operations), transient_file_creation_total='unavailable; snapshot names are a lower bound',
            elapsed_seconds=round(time.monotonic() - self.started, 3))

    def save(self):
        self.result['accounting'] = self.account()
        if hasattr(self, 'observations') and self.observations.exists():
            target = self.observations / 'result.json'
            target.write_bytes(encoded(self.result))
            self.result['accounting'] = self.account()
            target.write_bytes(encoded(self.result))

    def start(self, argv, label, request=None):
        self.account()
        self.children = [p for p in self.children if p.poll() is None]
        check(len(self.children) < 2 and len(self.launches) < 30, 'child/launch cap')
        command = [str(value) for value in argv]
        row = dict(label=label, command=command, cwd=str(self.root / 'observations'))
        self.launches.append(row)
        process = subprocess.Popen(command, cwd=self.root / 'observations', stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        self.children.append(process)
        self.max_children = max(self.max_children, len(self.children))
        row.update(pid=process.pid, started_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), _start=time.monotonic())
        if request is not None:
            row['request'] = request
        return process, row

    def finish(self, process, row, stdout, stderr):
        row.update(exit=process.returncode, elapsed_seconds=round(time.monotonic() - row.pop('_start'), 4))
        transcript = {**row, 'stdout_base64': base64.b64encode(stdout).decode(), 'stderr_base64': base64.b64encode(stderr).decode()}
        check(len(encoded(transcript)) <= 2 * 1024 * 1024, 'transcript cap')
        with self.transcript.open('ab') as stream:
            stream.write(json.dumps(transcript, ensure_ascii=False, sort_keys=True).encode() + b'\n')
        row.pop('request', None)
        try:
            result = json.loads(stdout)
        except (ValueError, UnicodeError):
            result = None
        row['public_outcome'] = result.get('outcome') if isinstance(result, dict) else None
        self.account()
        return result

    def call(self, argv, label, request=None):
        process, row = self.start(argv, label, request)
        try:
            stdout, stderr = process.communicate(encoded(request) if request is not None else None, timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
            self.finish(process, row, stdout, stderr)
            raise RuntimeError(label + ': timed out; owned child terminated; residue retained')
        result = self.finish(process, row, stdout, stderr)
        check(isinstance(result, dict), label + ': missing JSON result')
        return result, row

    def public(self, label, request, expected):
        result, row = self.call([sys.executable, '-I', '-B', SOURCE / 'src/tools/maintain_framework.py'], label, request)
        check(result.get('outcome') in expected, label + ': unexpected public outcome ' + str(result))
        success = result['outcome'] in {'inspected', 'planned', 'applied', 'unchanged', 'recovered', 'already-matching'}
        check(row['exit'] == (0 if success else 1), label + ': inconsistent exit')
        return result

    def base(self, project, operation):
        return dict(api_version=1, operation=operation, project_root=str(project), engine_root=str(SOURCE), engine=self.pin)

    def project_fixture(self, project):
        project.mkdir(exist_ok=True)
        fixtures = {'AGENTS.md': b'Native fixture only. Capabilities inactive.\n', '.gitattributes': b'* -text\n',
                    '.gitignore': b'.ai/local/\n', '.ai/custom/framework.json': b'{"fixture":"protected opaque bytes"}\n',
                    'unknown/keep.txt': b'unknown subtree sentinel\n'}
        for name, raw in fixtures.items():
            self.write(project / name, raw)
        return [dict(path=name, sha256=digest(project / name)) for name in sorted(fixtures) if name != 'unknown/keep.txt'] + [
            dict(path='protected-absent.txt', sha256=None)]

    def plan_request(self, project, protected):
        return {**self.base(project, 'plan'), 'candidate_root': self.candidate['candidate_root'],
            'candidate_identity': self.candidate['candidate_identity'], 'expected_lock_sha256': digest(project / LOCK),
            'mode_policy': 'windows-inventory-only', 'scratch_root': str(self.root / 'scratch'),
            'staging_root': str(self.root / 'staging'), 'recovery_root': str(self.recovery),
            'durability': dict(declared_by='Issue 382 fixture owner', declaration_reference='Issue 382 process termination only',
                               failure_domain='process-termination'),
            'protected_inputs': sorted(protected, key=lambda r: r['path']), 'project_data_action': 'none'}

    def maintenance(self, label):
        return dict(declared_by='Issue 382 exclusive fixture owner', declaration_reference=label,
                    affected_capabilities=['lesson'], sessions_stopped=True, tools_stopped=True, external_writers_stopped=True)

    def apply_request(self, plan, result, label):
        return {**plan, 'operation': 'apply', 'expected_plan_sha256': result['plan_sha256'], 'maintenance': self.maintenance(label)}

    def verify_installed(self, project, protected):
        lock = json.loads((project / LOCK).read_bytes())
        check(lock['engine'] == self.pin and lock['candidate_identity'] == self.candidate['candidate_identity'], 'lock binding')
        check(lock['inventory'] == self.inventory and lock['selection'] == self.selection, 'complete inventory/selection mismatch')
        for member in self.inventory['files']:
            check((project / member['destination']).read_bytes() == (Path(self.candidate['candidate_root']) / member['path']).read_bytes(),
                  'managed byte mismatch: ' + member['destination'])
        check(not (project / MARKER).exists(), 'completion marker retained')
        for row in protected:
            check(digest(project / row['path']) == row['sha256'], 'protected input changed')
        check((project / 'unknown/keep.txt').read_bytes() == b'unknown subtree sentinel\n', 'unknown changed')
        return dict(managed_members=len(self.inventory['files']), lock_sha256=digest(project / LOCK), marker_sha256=None,
                    managed_state='managed-bytes-consistent', project_readiness='not-assessed')

    def verify_operation(self, path, project):
        path = Path(path)
        check(path.parent == self.recovery, 'operation escaped durable root')
        operation = json.loads((path / 'operation.json').read_bytes())
        check(operation['engine'] == self.pin and Path(operation['project_root']) == project, 'operation attribution')
        required = {operation['after_lock_sha256'], *operation['candidate_metadata'].values(),
                    *(m['sha256'] for m in self.inventory['files'])}
        if operation['before_lock_sha256'] is not None:
            required.add(operation['before_lock_sha256'])
        objects = {p.name for p in (path / 'objects').iterdir()}
        check(objects == required, 'durable object closure mismatch')
        for name in objects:
            check(digest(path / 'objects' / name) == name, 'durable object hash mismatch')
        check(json.loads((path / 'objects' / operation['after_lock_sha256']).read_bytes())['inventory'] == self.inventory, 'durable lock mismatch')
        return dict(path=str(path), sha256=digest(path / 'operation.json'), objects=len(objects))

    def case(self, name, action):
        row = dict(id=name, outcome='failed', evidence_class='actual-public-native')
        self.result['cases'].append(row)
        try:
            detail = action() or {}
            row.update(detail)
            if 'outcome' not in detail:
                row['outcome'] = 'passed'
        except Exception as exc:
            row.update(exception_type=type(exc).__name__, diagnostic=str(exc))
            raise
        finally:
            self.save()

    def selected(self):
        def entry():
            self.protected = self.project_fixture(self.project)
            before = snapshot(self.project)
            self.candidate, row = self.call([sys.executable, '-I', '-B', SOURCE / 'tools/build-development.py',
                '--repository', SOURCE, '--commit', self.commit, '--profile', 'lesson-minimal',
                '--output-root', self.root / 'candidates', '--scratch-root', self.root / 'build-scratch'], 'build-lesson')
            check(row['exit'] == 0 and self.candidate['outcome'] == 'assembled', 'real candidate build failed')
            candidate = Path(self.candidate['candidate_root'])
            self.inventory = json.loads((candidate / 'metadata/files.json').read_bytes())
            self.selection = json.loads((candidate / 'metadata/selection.json').read_bytes())
            self.candidate_before = snapshot(candidate)
            self.result['candidate'] = self.candidate
            inspect = {**self.base(self.project, 'inspect'), 'candidate_root': str(candidate)}
            observed = self.public('inspect-fresh', inspect, {'inspected'})
            check(observed['details']['project_readiness'] == 'not-assessed', 'readiness overclaim')
            self.first_plan = self.plan_request(self.project, self.protected)
            self.first_result = self.public('plan-fresh', self.first_plan, {'planned'})
            for name in ('hash', 'membership'):
                bad = json.loads(json.dumps(inspect))
                if name == 'hash':
                    bad['engine']['files'][0]['sha256'] = '0' * 64
                else:
                    bad['engine']['files'].pop()
                refused = self.public('refuse-pin-' + name, bad, {'blocked', 'unsupported'})
                check(any(d['code'] == 'source-bootstrap' for d in refused['diagnostics']), 'wrong pin refusal')
            check(snapshot(self.project) == before and snapshot(candidate) == self.candidate_before, 'read-only calls changed inputs')
            check(self.caches() == self.source_caches, 'source bytecode changed')
            return dict(candidate_identity=self.candidate['candidate_identity'], plan_sha256=self.first_result['plan_sha256'],
                ambient_source='public -I -B fixed bootstrap; no product imported by driver',
                cache_limitation='no new observed cache; adversarial cache substitution remains separately labelled synthetic evidence')
        self.case('entry-pin', entry)

        def fresh():
            result = self.public('apply-fresh', self.apply_request(self.first_plan, self.first_result, 'fresh fixture apply'), {'applied'})
            check(result['details']['managed_state'] == 'managed-bytes-consistent' and result['details']['project_readiness'] == 'not-assessed', 'apply state')
            detail = self.verify_installed(self.project, self.protected)
            detail['operation'] = self.verify_operation(result['details']['operation_root'], self.project)
            detail['reported_counts'] = result['details']['counts']
            check(detail['reported_counts'] == dict(added=len(self.inventory['files']), changed=0, removed=0, unchanged=0), 'fresh counts')
            return detail
        self.case('fresh-apply', fresh)

        def unchanged():
            roots = (self.project, self.recovery, self.root / 'scratch', self.root / 'staging')
            before = {str(p): snapshot(p) for p in roots}
            self.noop_plan = self.plan_request(self.project, self.protected)
            result = self.public('plan-same-content', self.noop_plan, {'planned'})
            self.noop_request = self.apply_request(self.noop_plan, result, 'same-content fixture apply')
            applied = self.public('apply-same-content', self.noop_request, {'unchanged'})
            check(applied['changed'] is False and applied['details']['operation_root'] is None, 'no-op churn reported')
            check(applied['details']['counts'] == dict(added=0, changed=0, removed=0, unchanged=len(self.inventory['files'])), 'no-op counts')
            check(before == {str(p): snapshot(p) for p in roots}, 'no-op bytes/mtime/mode/names churn')
            return dict(reported_counts=applied['details']['counts'], full_file_snapshot_unchanged=True)
        self.case('same-content', unchanged)

        def negatives():
            member = self.inventory['files'][0]
            drift = self.root / 'drift-project'
            drift.mkdir()
            # Bounded installed-state copy: synthetic setup, not another native apply.
            for name in snapshot(self.project):
                self.write(drift / name, (self.project / name).read_bytes())
            (drift / member['destination']).write_bytes(b'observed owned drift\n')
            before = snapshot(drift)
            refused = self.public('refuse-owned-drift', self.plan_request(drift, self.protected), {'conflict'})
            check(snapshot(drift) == before, 'drift refusal overwrote input')
            collision = self.root / 'collision-project'
            protected = self.project_fixture(collision)
            self.write(collision / member['destination'], (Path(self.candidate['candidate_root']) / member['path']).read_bytes())
            before = snapshot(collision)
            collided = self.public('refuse-unowned-same-bytes', self.plan_request(collision, protected), {'conflict'})
            check(snapshot(collision) == before, 'collision refusal overwrote input')
            return dict(setup='authored bounded copy/drift and same-byte unowned file; real public/native refusal',
                        drift_codes=[d['code'] for d in refused['diagnostics']], collision_codes=[d['code'] for d in collided['diagnostics']])
        self.case('drift-collision', negatives)
        self.case('writer-exclusion', self.exclusion)
        self.case('interruption-recovery', self.interrupt_once)
        check(snapshot(Path(self.candidate['candidate_root'])) == self.candidate_before, 'candidate changed')
        check(self.caches() == self.source_caches, 'source bytecode changed')
        check(self.git('rev-parse', 'HEAD').decode().strip() == self.commit and
              not self.git('status', '--porcelain=v1', '--untracked-files=all').strip(), 'fixed source drift')

    def exclusion(self):
        guard = self.project / GUARD
        identity = (guard.stat().st_dev, guard.stat().st_ino, guard.stat().st_mtime_ns)
        before = snapshot(self.project)
        process, row = self.start([sys.executable, '-I', '-B', Path(__file__).absolute(), '--hold-guard', guard], 'guard-helper')
        messages = queue.Queue()
        threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True).start()
        ready = b''
        try:
            ready = messages.get(timeout=10)
            check(json.loads(ready).get('held') is True, 'guard helper not ready')
            denied = self.public('apply-while-guard-held', {**self.noop_request, 'maintenance': self.maintenance('competing public apply')}, {'blocked'})
            check(process.poll() is None and any(d['code'] == 'writer-lock-unavailable' for d in denied['diagnostics']), 'wrong lock refusal')
            check(snapshot(self.project) == before, 'lock refusal mutated project')
        finally:
            if process.poll() is None:
                process.terminate()  # owned helper only; OS releases its native handle
            stdout, stderr = process.communicate(timeout=5)
            self.finish(process, row, ready + stdout, stderr)
        admitted = self.public('apply-after-native-release', {**self.noop_request, 'maintenance': self.maintenance('after owned helper termination')}, {'unchanged'})
        check(identity == (guard.stat().st_dev, guard.stat().st_ino, guard.stat().st_mtime_ns) and snapshot(self.project) == before,
              'guard removed/replaced or project churn')
        return dict(guard_identity_preserved=True, helper_release='owned process terminated; OS handle release',
                    subsequent_outcome=admitted['outcome'], nonblocking='returned writer-lock-unavailable while helper held')

    def interrupt_once(self):
        project = self.root / 'interrupt-project'
        protected = self.project_fixture(project)
        plan = self.plan_request(project, protected)
        preview = self.public('plan-interruption', plan, {'planned'})
        request = self.apply_request(plan, preview, 'one unmodified public interruption attempt')
        marker_seen, terminated, events = None, False, []
        self.result['interruption_attempts'] = 0
        with DirectoryWatch(project / '.ai') as watch:
            process, row = self.start([sys.executable, '-I', '-B', SOURCE / 'src/tools/maintain_framework.py'], 'apply-interruption-once', request)
            self.result['interruption_attempts'] = 1
            try:
                process.stdin.write(encoded(request))
                process.stdin.close()
                process.stdin = None
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline and process.poll() is None:
                    names = watch.next(process, max(1, int((deadline - time.monotonic()) * 1000)))
                    if names is None:
                        break
                    events.extend(names)
                    check(len(events) <= 256, 'notification event cap')
                    if any(name.lower() == 'framework.operation' for name in names):
                        try:
                            marker_seen = (project / MARKER).read_bytes()
                        except FileNotFoundError:
                            marker_seen = None
                        if marker_seen is not None:
                            if process.poll() is None:
                                process.terminate()
                                terminated = True
                            break
                    watch.arm()
                if process.poll() is None and not terminated:
                    process.wait(timeout=max(0.1, deadline - time.monotonic()))
                stdout, stderr = process.communicate(timeout=5)
            except BaseException:
                if process.poll() is None:
                    process.kill()
                stdout, stderr = process.communicate(timeout=5)
                self.finish(process, row, stdout, stderr)
                raise
            actual = self.finish(process, row, stdout, stderr)
        self.write(self.observations / 'interrupted-state.json', encoded(dict(files=snapshot(project), events=events,
            marker_observed_sha256=sha256(marker_seen).hexdigest() if marker_seen else None,
            terminated_owned_public_process=terminated, public_result=actual)))
        if not terminated or not (project / MARKER).exists():
            if actual is not None:
                check(actual.get('outcome') == 'applied', 'public apply failed without attributable marker: ' + str(actual))
                self.verify_installed(project, protected)
            return dict(outcome='not-observed', terminated=terminated, marker_event_observed=marker_seen is not None,
                        residual='No attributable incomplete marker remained. Coordinator disposition required; no retry.')
        check(marker_seen == (project / MARKER).read_bytes(), 'marker changed after termination')
        operation = json.loads(marker_seen)
        op_root = Path(operation['operation_root'])
        verified = self.verify_operation(op_root, project)
        check((op_root / 'operation.json').read_bytes() == marker_seen, 'marker/durable bytes differ')
        inspected = self.public('inspect-interrupted', self.base(project, 'inspect'), {'inspected'})
        check(inspected['details']['managed_state'] == 'recovery-needed', 'interrupted inspect did not expose recovery state')
        recovery = {**self.base(project, 'recover'), 'operation_root': str(op_root), 'operation_sha256': verified['sha256'],
            'direction': 'finish', 'expected_lock_sha256': digest(project / LOCK), 'expected_marker_sha256': digest(project / MARKER),
            'maintenance': self.maintenance('fresh declaration for exact observed same-engine finish')}
        recovered = self.public('recover-observed-finish', recovery, {'recovered'})
        result = self.verify_installed(project, protected)
        result.update(operation=verified, terminated=True, marker_event_observed=True,
                      recovered_counts=recovered['details']['counts'], native_attempts=1)
        return result


class Overlapped(ctypes.Structure):
    _fields_ = [('Internal', ctypes.c_size_t), ('InternalHigh', ctypes.c_size_t),
                ('Offset', w.DWORD), ('OffsetHigh', w.DWORD), ('hEvent', w.HANDLE)]


class DirectoryWatch:
    """Native asynchronous notification armed before sending public stdin."""
    def __init__(self, directory):
        direct(directory)
        k = self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        k.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
        k.CreateFileW.restype = w.HANDLE
        k.CreateEventW.argtypes = [ctypes.c_void_p, w.BOOL, w.BOOL, w.LPCWSTR]
        k.CreateEventW.restype = w.HANDLE
        k.ReadDirectoryChangesW.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD, w.BOOL, w.DWORD,
                                          ctypes.POINTER(w.DWORD), ctypes.POINTER(Overlapped), ctypes.c_void_p]
        k.ReadDirectoryChangesW.restype = w.BOOL
        k.WaitForMultipleObjects.argtypes = [w.DWORD, ctypes.POINTER(w.HANDLE), w.BOOL, w.DWORD]
        k.WaitForMultipleObjects.restype = w.DWORD
        k.GetOverlappedResult.argtypes = [w.HANDLE, ctypes.POINTER(Overlapped), ctypes.POINTER(w.DWORD), w.BOOL]
        k.GetOverlappedResult.restype = w.BOOL
        k.ResetEvent.argtypes = [w.HANDLE]
        k.CancelIoEx.argtypes = [w.HANDLE, ctypes.POINTER(Overlapped)]
        k.CloseHandle.argtypes = [w.HANDLE]
        self.handle = k.CreateFileW(str(directory), 1, 7, None, 3, 0x42000000, None)
        check(self.handle not in (None, ctypes.c_void_p(-1).value), 'native notification directory unavailable')
        self.event = k.CreateEventW(None, True, False, None)
        if not self.event:
            k.CloseHandle(self.handle)
            raise RuntimeError('native notification event unavailable')
        self.buffer = ctypes.create_string_buffer(8192)
        self.overlapped = Overlapped(hEvent=self.event)
        self.pending = False

    def arm(self):
        self.kernel.ResetEvent(self.event)
        check(self.kernel.ReadDirectoryChangesW(self.handle, self.buffer, len(self.buffer), False, 0x19,
              None, ctypes.byref(self.overlapped), None), 'native directory notification unsupported')
        self.pending = True

    def __enter__(self):
        try:
            self.arm()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def next(self, process, timeout_ms):
        handles = (w.HANDLE * 2)(self.event, int(process._handle))
        status = self.kernel.WaitForMultipleObjects(2, handles, False, timeout_ms)
        if status in (1, 258):
            return None
        check(status == 0, 'native notification wait failed')
        size = w.DWORD()
        check(self.kernel.GetOverlappedResult(self.handle, ctypes.byref(self.overlapped), ctypes.byref(size), False), 'native event result failed')
        self.pending = False
        check(0 < size.value <= len(self.buffer), 'native notification overflow')
        data, names, offset = self.buffer.raw[:size.value], [], 0
        while True:
            following, action, length = struct.unpack_from('<III', data, offset)
            check(offset + 12 + length <= len(data), 'invalid native notification')
            names.append(data[offset + 12:offset + 12 + length].decode('utf-16-le'))
            if not following:
                return names
            offset += following

    def __exit__(self, *unused):
        if self.pending:
            self.kernel.CancelIoEx(self.handle, ctypes.byref(self.overlapped))
            size = w.DWORD()
            self.kernel.GetOverlappedResult(self.handle, ctypes.byref(self.overlapped), ctypes.byref(size), True)
        self.kernel.CloseHandle(self.handle)
        self.kernel.CloseHandle(self.event)


def hold_guard(path):
    """Independent helper holds the real empty guard range using LockFileEx."""
    import msvcrt
    path = Path(path)
    check(os.name == 'nt' and path.is_relative_to(NATIVE) and path.name == 'installation.guard', 'helper outside selected fixture')
    direct(path.parent)
    before = path.lstat()
    check(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == 0, 'guard must be existing empty file')
    descriptor = os.open(path, os.O_RDWR | os.O_BINARY)
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.LockFileEx.argtypes = [w.HANDLE, w.DWORD, w.DWORD, w.DWORD, w.DWORD, ctypes.POINTER(Overlapped)]
    k.LockFileEx.restype = w.BOOL
    k.UnlockFileEx.argtypes = [w.HANDLE, w.DWORD, w.DWORD, w.DWORD, ctypes.POINTER(Overlapped)]
    k.UnlockFileEx.restype = w.BOOL
    overlap, handle, held = Overlapped(), w.HANDLE(msvcrt.get_osfhandle(descriptor)), False
    try:
        opened = os.fstat(descriptor)
        check((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino), 'guard changed while opening')
        held = bool(k.LockFileEx(handle, 3, 0, 1, 0, ctypes.byref(overlap)))
        check(held, 'helper lock refused')
        print(json.dumps(dict(held=True, pid=os.getpid(), device=opened.st_dev, inode=opened.st_ino)), flush=True)
        threading.Event().wait(45)  # finite lifetime if the driver is interrupted
    finally:
        if held:
            k.UnlockFileEx(handle, 0, 1, 0, ctypes.byref(overlap))
        os.close(descriptor)
    return 0


def main(native_root):
    run = NativeRun()
    try:
        run.prepare(native_root)
        run.selected()
        passed = len(run.result['cases']) == len(CASES) and all(row['outcome'] == 'passed' for row in run.result['cases'])
        run.result.update(outcome='passed' if passed else 'not-passed', exit=0 if passed else 1)
    except Exception as exc:
        run.result.update(outcome='not-passed', exit=1 if run.result['cases'] else 2,
                          exception_type=type(exc).__name__, diagnostic=str(exc))
    finally:
        for process in run.children:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)
                run.result.update(outcome='not-passed', exit=2, cleanup_failure='owned child needed final termination')
        done = {row['id'] for row in run.result['cases']}
        run.result['unexecuted_cases'] = [case for case in CASES if case not in done]
        try:
            run.save()
        except Exception as exc:
            run.result.update(outcome='not-passed', exit=2, accounting_failure=str(exc))
            if hasattr(run, 'observations') and run.observations.exists():
                (run.observations / 'result.json').write_bytes(encoded(run.result))
        print(json.dumps({'native_windows': run.result}, ensure_ascii=False, sort_keys=True))
    return run.result['exit']


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--hold-guard':
        raise SystemExit(hold_guard(sys.argv[2]))
    raise SystemExit('Use run.py --layer native-windows --native-root with the exact Issue 382 binding.')
