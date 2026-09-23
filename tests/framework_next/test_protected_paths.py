"""Issue 383: focused path simulations and one explicitly selected real F: plan.

python -I -B tests/framework_next/test_protected_paths.py --mode regressions
python -I -B tests/framework_next/test_protected_paths.py --mode actual-plan
Simulation results are not native acceptance. Actual mode retains every output.
"""
from contextlib import ExitStack, contextmanager
from hashlib import sha256
import argparse
import base64
import ctypes
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import stat
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import uuid

REPOSITORY = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(REPOSITORY / 'src'))
from distribution import installation_plan as planning, installation_state as state

ROOT = Path('Z:/direct/project')
NAME = '.ai/custom/framework.json'
TARGET = ROOT / NAME
RAW = b'{"preserve":"exact bytes"}\r\n'


def info(path, **changes):
    result = dict(st_dev=123, st_ino=456, st_mode=stat.S_IFREG if path == TARGET else stat.S_IFDIR,
                  st_file_attributes=0, st_nlink=1, st_size=len(RAW), st_mtime_ns=789)
    result.update(changes)
    return SimpleNamespace(**result)


def winerror(code):
    error = OSError('synthetic path API failure')
    error.winerror = code
    return error


class Kernel:
    """Only simulated API values; no claim about native links or aliases."""
    def __init__(self, *, name=lambda value: value, length=None, device=r'\Device\SyntheticVolume',
                 device_length=None, kind=3, after=None):
        def long_name(value, buffer, size):
            buffer.value = name(value)
            if after:
                after()
            return len(buffer.value) if length is None else length
        def drive(value, buffer, size):
            buffer.value = device
            return len(device) + 2 if device_length is None else device_length
        self.GetLongPathNameW = Mock(side_effect=long_name)
        self.QueryDosDeviceW = Mock(side_effect=drive)
        self.GetDriveTypeW = Mock(return_value=kind)


@contextmanager
def simulated(*, kernel=None, metadata=None, error=1, missing=None):
    kernel = kernel or Kernel()
    def lstat(path):
        if path == missing:
            raise FileNotFoundError('selected absent fixture')
        return metadata(path) if metadata else info(path)
    def resolve(path, strict=False):
        if error is not None:
            raise winerror(error)
        return path
    with ExitStack() as stack:
        stack.enter_context(patch.object(Path, 'lstat', autospec=True, side_effect=lstat))
        stack.enter_context(patch.object(Path, 'resolve', autospec=True, side_effect=resolve))
        stack.enter_context(patch.object(ctypes, 'WinDLL', return_value=kernel))
        stack.enter_context(patch.object(os, 'scandir', side_effect=AssertionError('protected path enumerated siblings')))
        yield kernel


class ProtectedPaths(unittest.TestCase):
    def test_ordinary_and_error_one_resolve_all_selected_components(self):
        for error in (None, 1):
            with self.subTest(error=error), simulated(error=error) as kernel:
                self.assertEqual(planning._protected_path(ROOT, NAME), TARGET)
                self.assertEqual(kernel.GetLongPathNameW.call_count, 0 if error is None else 3)

    def test_existing_root_guard_reuses_same_query(self):
        for error in (None, 1):
            with self.subTest(error=error), simulated(error=error):
                self.assertEqual(state._root(str(ROOT)), ROOT)

    def test_other_errors_and_non_windows_do_not_fall_back(self):
        for code in (2, 5, 50, 144, None):
            with self.subTest(code=code), simulated(error=code or 1) as kernel:
                with patch.object(planning, 'os', SimpleNamespace(name='posix' if code is None else 'nt')):
                    with self.assertRaises(OSError) as caught:
                        planning._protected_path(ROOT, NAME)
                self.assertEqual(caught.exception.winerror, code or 1)
                kernel.GetLongPathNameW.assert_not_called()

    def test_canonical_case_short_alias_and_containment_refusals(self):
        for transform in (lambda p: p.replace('.ai', '.AI'), lambda p: p.replace('.ai', 'long-directory'),
                          lambda p: p.replace('project', 'outside')):
            with self.subTest(transform=transform), simulated(kernel=Kernel(name=transform)):
                with self.assertRaises(state.InstallationError) as caught:
                    planning._protected_path(ROOT, NAME)
                self.assertEqual(caught.exception.diagnostic['code'], 'path-alias')
        with simulated(error=None), patch.object(Path, 'resolve', return_value=ROOT.parent / 'outside'):
            with self.assertRaises(state.InstallationError):
                planning._protected_path(ROOT, NAME)

    def test_unavailable_long_name_drive_alias_and_remote_mapping_refused(self):
        kernels = [Kernel(length=n) for n in (0, 32768)]
        kernels += [Kernel(device_length=n) for n in (0, 32768)]
        kernels += [Kernel(device=d) for d in (r'\??\Z:\other', r'\Device\Volume\subdir')]
        kernels += [Kernel(kind=k) for k in (0, 4)]
        for kernel in kernels:
            with self.subTest(kernel=kernel), simulated(kernel=kernel):
                with self.assertRaises(state.InstallationError):
                    planning._protected_path(ROOT, NAME)

    def test_symlink_reparse_parent_collision_and_missing_identity_refused(self):
        defects = ({'st_mode': stat.S_IFLNK}, {'st_file_attributes': 0x400},
                   {'st_mode': stat.S_IFREG}, {'st_dev': 0}, {'st_ino': 0})
        for selected in (ROOT / '.ai', ROOT.parent):
            for defect in defects:
                def metadata(path):
                    return info(path, **defect) if path == selected else info(path)
                with self.subTest(selected=selected, defect=defect), simulated(metadata=metadata):
                    with self.assertRaises(state.InstallationError):
                        planning._protected_path(ROOT, NAME)
        for defect in ({'st_mode': stat.S_IFLNK}, {'st_file_attributes': 0x400}):
            with self.subTest(leaf=defect), simulated(metadata=lambda p: info(p, **defect) if p == TARGET else info(p)):
                with self.assertRaises(state.InstallationError):
                    planning._protected_path(ROOT, NAME)

    def test_ancestor_identity_drift_and_new_reparse_refused(self):
        for changed in (ROOT / '.ai', ROOT, ROOT.parent):
            for defect in ({'st_ino': 999}, {'st_file_attributes': 0x400}):
                queried = []
                kernel = Kernel(after=lambda: queried.append(True))
                def metadata(path):
                    return info(path, **defect) if queried and path == changed else info(path)
                with self.subTest(changed=changed, defect=defect), simulated(kernel=kernel, metadata=metadata):
                    with self.assertRaises(state.InstallationError):
                        planning._protected_path(ROOT, NAME)

    def test_missing_and_present_absence_bindings(self):
        for missing in (ROOT / '.ai', TARGET):
            with self.subTest(missing=missing), simulated(missing=missing):
                rows = [{'path': NAME, 'sha256': None}]
                self.assertEqual(planning._protected(state._Reader(), ROOT, rows, set()), rows)
                with self.assertRaises(state.InstallationError):
                    planning._protected(state._Reader(), ROOT, [{'path': NAME, 'sha256': sha256(RAW).hexdigest()}], set())
        with simulated(), self.assertRaises(state.InstallationError):
            planning._protected(state._Reader(), ROOT, [{'path': NAME, 'sha256': None}], set())

    def test_raw_bytes_match_mismatch_and_hardlink_refusal(self):
        class Stream(io.BytesIO):
            def fileno(self):
                return 123
        rows = [{'path': NAME, 'sha256': sha256(RAW).hexdigest()}]
        with simulated(), patch.object(Path, 'open', side_effect=lambda *a, **k: Stream(RAW)), \
                patch.object(os, 'fstat', return_value=info(TARGET)):
            self.assertEqual(planning._protected(state._Reader(), ROOT, rows, set()), rows)
            with self.assertRaises(state.InstallationError) as caught:
                planning._protected(state._Reader(), ROOT, [{'path': NAME, 'sha256': sha256(RAW + b'x').hexdigest()}], set())
            self.assertEqual(caught.exception.diagnostic['code'], 'protected-input-conflict')
        with simulated(metadata=lambda p: info(p, st_nlink=2) if p == TARGET else info(p)), \
                patch.object(Path, 'open', side_effect=AssertionError('hardlink opened')):
            with self.assertRaises(state.InstallationError) as caught:
                planning._protected(state._Reader(), ROOT, rows, set())
            self.assertEqual(caught.exception.diagnostic['code'], 'hardlinked-file')


PROTECTED = [
    {'path': '.ai/custom/framework.json', 'sha256': 'f8274586a3700171876908e948d5f54391fc40e90491c94fdab5fae25f7ca187'},
    {'path': '.gitattributes', 'sha256': '705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da'},
    {'path': '.gitignore', 'sha256': 'c77f5b0571f5cbbe73d7300782a8f27bf338699a3f057e0cafc8ba72655d3948'},
    {'path': 'AGENTS.md', 'sha256': '1e847654544fb51cc0dcd736b4ca2849e06bf0f4d77e9fcb0c944c4c643f4d58'},
    {'path': 'protected-absent.txt', 'sha256': None},
]


def actual_plan():
    # Reuse only existing direct-path/process helpers, not another owner's driver.
    sys.path.insert(0, str(REPOSITORY / 'tests/framework_next'))
    import support
    check = support.check
    check(REPOSITORY == Path('F:/framework-next/383') and os.name == 'nt', 'assigned Windows worktree required')
    parent = support.output_parent(Path('F:/framework-next/p7-runs/protected-path-383'))
    root = parent / uuid.uuid4().hex[:8]
    root.mkdir(mode=0o700)  # exclusive, never retry a collision or delete a prior run
    identity = root.lstat()
    seen, calls = {}, []
    print(json.dumps({'retained_run': str(root)}), flush=True)

    def measure():
        current = root.lstat()
        check(support.direct_directory(root).parent == parent and
              (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino), 'run identity drift')
        files = []
        pending = [root]
        while pending:
            for path in pending.pop().iterdir():
                entry = path.lstat()
                check(not stat.S_ISLNK(entry.st_mode) and not getattr(entry, 'st_file_attributes', 0) & 0x400,
                      'non-direct residue retained')
                if stat.S_ISDIR(entry.st_mode):
                    pending.append(path)
                else:
                    check(stat.S_ISREG(entry.st_mode), 'nonregular residue retained')
                    name = path.relative_to(root).as_posix()
                    seen[name] = max(seen.get(name, 0), entry.st_size)
                    files.append({'path': name, 'size': entry.st_size})
                    check(len(seen) <= 96 and sum(seen.values()) <= 4 * 1024 * 1024, 'selected file/byte cap exceeded')
        return {'files': sorted(files, key=lambda row: row['path']), 'observed_files': len(seen),
                'observed_logical_bytes': sum(seen.values()), 'helper_launches': len(calls)}

    def save(name, value):
        raw = value if isinstance(value, bytes) else (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
        with (root / name).open('xb') as stream:
            stream.write(raw)
        measure()

    def call(label, argv, request=None):
        check(len(calls) < 8, 'selected process cap exceeded')
        started = time.monotonic()
        record = {'label': label, 'argv': [str(x) for x in argv], 'cwd': str(REPOSITORY),
                  'request': request, 'started_at': datetime.now(timezone.utc).isoformat()}
        calls.append(record)
        try:
            result = support.run_process(argv, cwd=REPOSITORY,
                                         input=None if request is None else json.dumps(request).encode(), timeout=60)
            record.update(exit=result.returncode, stdout_base64=base64.b64encode(result.stdout).decode(),
                          stderr_base64=base64.b64encode(result.stderr).decode())
            return result
        except Exception as exc:
            record.update(exception_type=type(exc).__name__, outcome='interrupted-or-blocked')
            raise
        finally:
            record['elapsed_seconds'] = round(time.monotonic() - started, 4)
            with (root / 'calls.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(record, sort_keys=True) + '\n')
            measure()

    passed = False
    try:
        head = call('source-head', ['git', 'rev-parse', 'HEAD'])
        branch = call('source-branch', ['git', 'branch', '--show-current'])
        status = call('source-status', ['git', 'status', '--porcelain'])
        check(all(r.returncode == 0 for r in (head, branch, status)) and not status.stdout, 'clean source required')
        commit = head.stdout.decode().strip()
        check(branch.stdout.decode().strip() == 'codex/2026-09-23-protected-path-repair', 'assigned branch required')
        dirs = {}
        for role in ('project', 'scratch', 'staging', 'recovery', 'c', 'b'):
            dirs[role] = root / role
            dirs[role].mkdir(mode=0o700)
            support.direct_directory(dirs[role])
        previous = Path('F:/framework-next/p7-runs/native-w01/382/63bb8cce/project')
        for row in PROTECTED:
            old, new = previous / row['path'], dirs['project'] / row['path']
            if row['sha256'] is None:
                check(not old.exists() and not new.exists(), 'protected absence changed')
                continue
            raw = state._Reader().read(old, row['path'])
            check(sha256(raw).hexdigest() == row['sha256'], 'prior protected raw bytes changed')
            new.parent.mkdir(parents=True, exist_ok=True)
            with new.open('xb') as stream:
                stream.write(raw)
        pin = {'id': 'framework-managed-installation', 'version': '1.0.0', 'source_commit': commit,
               'files': [{'path': name, 'sha256': sha256((REPOSITORY / name).read_bytes()).hexdigest()}
                         for name in state.ENGINE_FILES]}
        check(len(pin['files']) == 10, 'full ten-file raw engine pin required')
        save('engine-pin.json', pin)
        primitive = []
        for name in ('.ai', '.ai/custom', '.ai/custom/framework.json'):
            try:
                resolved = (dirs['project'] / name).resolve(strict=True)
                primitive.append({'path': name, 'strict_resolve': str(resolved)})
            except OSError as exc:
                primitive.append({'path': name, 'error_type': type(exc).__name__, 'winerror': getattr(exc, 'winerror', None)})
        save('preflight.json', {'source_commit': commit, 'branch': branch.stdout.decode().strip(), 'clean': True,
             'runtime': sys.version, 'run': str(root), 'root_identity': [identity.st_dev, identity.st_ino],
             'caps': {'files': 96, 'logical_bytes': 4194304, 'helper_launches': 8},
             'protected_inputs': PROTECTED, 'protected_source': str(previous), 'strict_resolve_observations': primitive,
             'before': measure(), 'retention': 'all outputs retained, no cleanup',
             'failure_domain': 'process-termination; no apply/recovery selected'})
        built = call('build-lesson', [sys.executable, '-I', '-B', REPOSITORY / 'tools/build-development.py',
                     '--repository', REPOSITORY, '--commit', commit, '--profile', 'lesson-minimal',
                     '--output-root', dirs['c'], '--scratch-root', dirs['b']])
        check(built.returncode == 0, 'real candidate build failed; retain raw transcript')
        candidate = json.loads(built.stdout)
        request = {'api_version': 1, 'operation': 'plan', 'engine_root': str(REPOSITORY), 'engine': pin,
                   'project_root': str(dirs['project']), 'scratch_root': str(dirs['scratch']),
                   'staging_root': str(dirs['staging']), 'recovery_root': str(dirs['recovery']),
                   'candidate_root': candidate['candidate_root'], 'candidate_identity': candidate['candidate_identity'],
                   'expected_lock_sha256': None, 'mode_policy': 'windows-inventory-only', 'project_data_action': 'none',
                   'protected_inputs': PROTECTED, 'durability': {'declared_by': 'Issue 383 fixture owner',
                   'declaration_reference': 'Issue 383 plan only', 'failure_domain': 'process-termination'}}
        save('plan-request.json', request)
        result = call('public-plan', [sys.executable, '-I', '-B', REPOSITORY / 'src/tools/maintain_framework.py'], request)
        save('plan-response.json', result.stdout)
        save('plan-stderr.txt', result.stderr)
        response = json.loads(result.stdout)
        check(result.returncode == 0 and response['outcome'] == 'planned', 'actual public plan failed; retain raw transcript')
        plan = response['plan']
        check(plan['protected_inputs'] == PROTECTED and plan['engine'] == pin and
              plan['candidate_identity'] == candidate['candidate_identity'], 'plan bindings changed')
        check(sha256(state.json_bytes(plan)).hexdigest() == response['plan_sha256'], 'plan hash differs')
        prerequisites = {row['id']: row['status'] for row in plan['prerequisites']}
        check(prerequisites['native-writer-backend'] == 'satisfied' and
              prerequisites['writer-engine-closure'] == 'satisfied', 'plan prerequisites unresolved')
        for row in PROTECTED:
            path = dirs['project'] / row['path']
            check((sha256(path.read_bytes()).hexdigest() if path.exists() else None) == row['sha256'], 'protected input mutated')
        check(all(not (dirs['project'] / name).exists() for name in (state.LOCK_PATH, state.GUARD_PATH, *state.MARKERS)),
              'plan created a control file')
        check(all(not list(dirs[role].iterdir()) for role in ('scratch', 'staging', 'recovery')), 'plan allocated writer storage')
        passed = True
        save('result.json', {'outcome': 'passed', 'evidence_kind': 'actual F: public plan; no apply/recover',
             'source_commit': commit, 'candidate_identity': candidate['candidate_identity'],
             'plan_sha256': response['plan_sha256'], 'prerequisites': prerequisites, 'protected_inputs_unchanged': True})
    finally:
        save('inventory.json', {'outcome': 'passed' if passed else 'not-passed', 'snapshot_excludes': 'inventory.json',
                               'observations': measure(), 'nested_product_git_launches': 'unavailable'})
        print(json.dumps({'selected_passed': passed, 'run': str(root), 'final_counts': measure()}), flush=True)
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('regressions', 'actual-plan'))
    args = parser.parse_args()
    if not (os.name == 'nt' and sys.flags.isolated and sys.dont_write_bytecode):
        parser.error('Windows with -I -B is required')
    if args.mode == 'actual-plan':
        return actual_plan()
    print('Evidence: simulated Windows paths/APIs and byte streams; not native acceptance.', flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProtectedPaths))
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(main())
