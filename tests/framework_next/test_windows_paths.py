"""Issue 378 only: labelled Windows API simulations and tiny actual observations.

Run with python -I -B tests/framework_next/test_windows_paths.py --mode regressions.
Use --mode bootstrap-regressions for the approved pre-pin path continuation,
and --mode public-plan for its one fresh actual reader/complete public plan.
Actual modes require an explicit --output-root and retain their unique run.
No full family matrix, installation/apply, native-runner replacement or CI gate.
"""
from contextlib import ExitStack, contextmanager
from ctypes import wintypes as w
from hashlib import sha256
import argparse
import ast
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).absolute().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / 'src')]
import support
from distribution import assembly, installation_state as state, installation_io as io

SCRIPTS = {
    'lesson': 'lesson', 'adr': 'adr', 'standards-promotion': 'standards_promotion',
    'pr': 'pr', 'local-backlog': 'local_backlog',
    'software-development-orchestrator': 'workflow', 'problem-frame-author': 'problem_frame',
}
MODULES = {}
for family, script in SCRIPTS.items():
    spec = importlib.util.spec_from_file_location('wpc_' + script, support.REPOSITORY / 'src/skills' / family / 'scripts' / (script + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    MODULES[family] = module


BOOTSTRAP_SPEC = importlib.util.spec_from_file_location('wpc_bootstrap', support.REPOSITORY / 'src/tools/maintain_framework.py')
bootstrap = importlib.util.module_from_spec(BOOTSTRAP_SPEC)
BOOTSTRAP_SPEC.loader.exec_module(bootstrap)


def info(*, device=123, inode=456, mode=stat.S_IFDIR, attributes=16, links=1, size=0):
    return SimpleNamespace(st_dev=device, st_ino=inode, st_mode=mode, st_file_attributes=attributes,
                           st_nlink=links, st_size=size)


class Kernel:
    """Synthetic API returns only; never a native-volume acceptance fixture."""
    def __init__(self, *, error=144, filesystem='NTFS', kind=3, long_name=None,
                 long_result=None, query_ok=True, serial=123, volume=None, open_ok=True, device=r'\Device\SyntheticVolume', device_result=None):
        self.error, self.filesystem, self.kind = error, filesystem, kind
        self.long_name, self.long_result, self.query_ok = long_name, long_result, query_ok
        self.serial, self.volume, self.open_ok = serial, volume, open_ok
        self.device, self.device_result = device, device_result
        for name in ('GetVolumePathNameW', 'GetVolumeInformationW', 'GetVolumeInformationByHandleW',
                     'QueryDosDeviceW', 'GetLongPathNameW', 'CreateFileW', 'CloseHandle', 'GetDriveTypeW', 'MoveFileExW'):
            setattr(self, name, Mock(side_effect=getattr(self, '_' + name, lambda *a: 1)))

    def _GetVolumePathNameW(self, path, out, length):
        out.value = self.volume or str(Path(path).parent) + '\\'
        return 1

    def _GetVolumeInformationW(self, path, label, size, serial, maximum, flags, out, length):
        if self.error:
            ctypes.set_last_error(self.error)
            return 0
        out.value = self.filesystem
        return 1

    def _GetVolumeInformationByHandleW(self, handle, label, size, serial, maximum, flags, out, length):
        out.value = self.filesystem
        ctypes.cast(serial, ctypes.POINTER(w.DWORD))[0] = self.serial
        return int(self.query_ok)

    def _QueryDosDeviceW(self, drive, out, length):
        out.value = self.device
        return len(out.value) + 2 if self.device_result is None else self.device_result

    def _GetLongPathNameW(self, path, out, length):
        out.value = self.long_name if self.long_name is not None else path
        return len(out.value) if self.long_result is None else self.long_result

    def _CreateFileW(self, *args):
        return 12345 if self.open_ok else ctypes.c_void_p(-1).value

    def _GetDriveTypeW(self, path):
        return self.kind


def windows_error(code):
    error = OSError('synthetic API failure')
    error.winerror = code
    return error


@contextmanager
def simulated(kernel=None, *, path_info=None, opened=None, resolve_error=1):
    import msvcrt
    kernel = kernel or Kernel()
    with ExitStack() as stack:
        stack.enter_context(patch.object(ctypes, 'WinDLL', return_value=kernel))
        stack.enter_context(patch.object(Path, 'lstat', side_effect=path_info or (lambda: info())))
        stack.enter_context(patch.object(Path, 'stat', return_value=info()))
        stack.enter_context(patch.object(Path, 'exists', return_value=True))
        stack.enter_context(patch.object(Path, 'resolve', side_effect=windows_error(resolve_error)))
        stack.enter_context(patch.object(os, 'fstat', return_value=opened or info()))
        transfer = stack.enter_context(patch.object(msvcrt, 'open_osfhandle', return_value=99))
        close = stack.enter_context(patch.object(os, 'close'))
        yield kernel, transfer, close


DIRECT = Path('Z:/direct/child')


class SimulatedWindowsPaths(unittest.TestCase):
    def test_reader_error_one_and_ordinary_resolve(self):
        with simulated():
            self.assertEqual(state._root(str(DIRECT)), DIRECT)
        with simulated(), patch.object(Path, 'resolve', return_value=DIRECT):
            self.assertEqual(state._root(str(DIRECT)), DIRECT)

    def test_fallbacks_refuse_drive_aliases_and_unavailable_mapping(self):
        for kernel in (Kernel(device=r'\??\Z:\elsewhere'), Kernel(device=r'\Device\Volume\subdir'),
                       Kernel(device_result=0), Kernel(device_result=32768)):
            with self.subTest(device=kernel.device), simulated(kernel):
                with self.assertRaises(state.InstallationError):
                    state._root(str(DIRECT))
                with self.assertRaises(OSError):
                    io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel)
                kernel.CreateFileW.assert_not_called()
        with simulated(Kernel(kind=4)), self.assertRaises(state.InstallationError):
            state._root(str(DIRECT))
        with simulated() as (kernel, _, _), patch.object(state, 'os', SimpleNamespace(name='posix')):
            with self.assertRaises(OSError):
                state._root(str(DIRECT))
            kernel.QueryDosDeviceW.assert_not_called()

    def test_reader_other_errors_do_not_fall_back(self):
        for code in (2, 5, 50, 144):
            with self.subTest(code=code), simulated(resolve_error=code) as (kernel, _, _):
                with self.assertRaises(OSError) as caught:
                    state._root(str(DIRECT))
                self.assertEqual(caught.exception.winerror, code)
                kernel.GetLongPathNameW.assert_not_called()

    def test_reader_alias_and_long_name_errors(self):
        for kernel in (Kernel(long_name='Z:/direct/long-child'), Kernel(long_result=0), Kernel(long_result=32768)):
            with self.subTest(kernel=kernel), simulated(kernel):
                with self.assertRaises(state.InstallationError):
                    state._root(str(DIRECT))
        for path in ('relative', 'Z:/', 'Z:/direct/../child', 'Z:/direct/./child',
                     '//host/share/root', '//?/Z:/direct', 'Z:/direct/NUL.txt', 'Z:/direct/child.', 'Z:/direct/child '):
            with self.subTest(path=path), self.assertRaises(state.InstallationError):
                state._root(path)

    def test_reader_ancestor_reparse_missing_identity_and_drift(self):
        for bad in (info(mode=stat.S_IFLNK), info(attributes=0x410), info(inode=0), info(mode=stat.S_IFREG)):
            rows = [info(), bad, info()] * 2
            with self.subTest(bad=bad), simulated(path_info=iter(rows)):
                with self.assertRaises(state.InstallationError):
                    state._root(str(DIRECT))
        with simulated(path_info=iter([info()] * 3 + [info(inode=999), info(), info()])):
            with self.assertRaises(state.InstallationError) as caught:
                state._root(str(DIRECT))
            self.assertEqual(caught.exception.diagnostic['code'], 'root-drift')

    def test_all_eight_helpers_have_identical_ast_and_six_backends_match(self):
        helpers, backends = [], []
        for module in [io, *MODULES.values()]:
            tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
            helpers.append(ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_windows_handle_filesystem')))
            if module not in (io, MODULES['problem-frame-author']):
                backends.append(ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'local_write_backend')))
        self.assertEqual(len(set(helpers)), 1)
        self.assertEqual(len(set(backends)), 1)

    def test_handle_success_binds_metadata_and_closes_descriptor(self):
        with simulated() as (kernel, transfer, close):
            self.assertEqual(io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel), 'NTFS')
            kernel.CreateFileW.assert_called_once_with(str(DIRECT), 0, 7, None, 3, 0x02200000, None)
            transfer.assert_called_once_with(12345, os.O_RDONLY)
            close.assert_called_once_with(99)
            kernel.CloseHandle.assert_not_called()

    def test_handle_refuses_reparse_alias_and_cross_volume_before_open(self):
        for bad in (info(mode=stat.S_IFLNK), info(attributes=0x410), info(inode=0), info(device=321), info(mode=stat.S_IFREG)):
            with self.subTest(bad=bad), simulated(path_info=iter([info(), bad, info()])) as (kernel, _, _):
                with self.assertRaises(OSError):
                    io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel)
                kernel.CreateFileW.assert_not_called()
        for kernel in (Kernel(long_name='Z:/direct/long-child'), Kernel(long_result=0), Kernel(long_result=32768)):
            with simulated(kernel):
                with self.assertRaises(OSError):
                    io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel)
                kernel.CreateFileW.assert_not_called()
        for directory, volume in ((DIRECT, 'Y:/'), (Path('//host/share/path'), '//host/share/'),
                                  (Path('Z:/direct/../child'), 'Z:/'), (Path('relative'), '.')):
            with simulated() as (kernel, _, _), self.assertRaises(OSError):
                io._windows_handle_filesystem(directory, volume, kernel)

    def test_handle_refuses_open_query_identity_serial_and_drift(self):
        cases = [(Kernel(open_ok=False), {}, False), (Kernel(query_ok=False), {}, True),
                 (Kernel(serial=321), {}, True), (Kernel(), {'opened': info(inode=999)}, True),
                 (Kernel(), {'opened': info(attributes=0x410)}, True),
                 (Kernel(), {'path_info': iter([info()] * 3 + [info(inode=999), info(), info()])}, True)]
        for kernel, kwargs, owns_fd in cases:
            with self.subTest(kwargs=kwargs), simulated(kernel, **kwargs) as (_, _, close):
                with self.assertRaises(OSError):
                    io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel)
                self.assertEqual(close.call_count, int(owns_fd))
        with simulated() as (kernel, transfer, close):
            transfer.side_effect = OSError('synthetic transfer failure')
            with self.assertRaises(OSError):
                io._windows_handle_filesystem(DIRECT, str(DIRECT.parent), kernel)
            kernel.CloseHandle.assert_called_once_with(12345)
            close.assert_not_called()

    def test_three_backend_dispatches_preserve_filesystems_and_error_filter(self):
        for family in ('lesson', 'problem-frame-author', 'distribution'):
            def invoke():
                if family == 'distribution':
                    backend = io.Backend.__new__(io.Backend)
                    backend.windows, backend.native = True, kernel
                    return backend._volume(DIRECT)
                module = MODULES[family]
                return (module.local_backend if family == 'problem-frame-author' else module.local_write_backend)(DIRECT)
            for error in (0, 144):
                with self.subTest(family=family, error=error), simulated(Kernel(error=error)) as (kernel, _, _):
                    self.assertTrue(invoke())
                    self.assertEqual(kernel.GetVolumeInformationByHandleW.call_count, int(error == 144))
            for error, filesystem, kind in ((5, 'NTFS', 3), (1, 'NTFS', 3), (144, 'FAT32', 3), (144, 'NTFS', 4), (144, 'NTFS', 0)):
                with self.subTest(family=family, error=error, fs=filesystem, kind=kind), simulated(Kernel(error=error, filesystem=filesystem, kind=kind)) as (kernel, _, _):
                    with self.assertRaises((OSError, ValueError, MODULES['lesson'].Fault, MODULES['problem-frame-author'].Fault)):
                        invoke()
                    if error != 144:
                        kernel.GetVolumeInformationByHandleW.assert_not_called()
            with simulated(Kernel(filesystem='ReFS')) as (kernel, _, _):
                if family == 'distribution':
                    self.assertTrue(invoke())
                else:
                    with self.assertRaises((MODULES['lesson'].Fault, MODULES['problem-frame-author'].Fault)):
                        invoke()

    def test_distribution_recovery_failure_domain_is_still_enforced(self):
        declaration = {'declared_by': 'fixture', 'declaration_reference': 'synthetic:378', 'failure_domain': 'project-volume-loss'}
        with simulated(), self.assertRaises(state.InstallationError) as caught:
            io.Backend({'project': DIRECT, 'recovery': DIRECT.parent}, declaration)
        self.assertEqual(caught.exception.diagnostic['code'], 'recovery-failure-domain')


@contextmanager
def bootstrap_simulated(target, *, kernel=None, selected=None, ancestor=None, error=1, after=None):
    """All path metadata and native API answers here are explicit simulations."""
    kernel = kernel or Kernel()
    calls = {}
    def observe(path):
        calls[path] = calls.get(path, 0) + 1
        if after is not None and calls[path] > 1:
            changed = after(path)
            if changed is not None:
                return changed
        return (selected or info(mode=stat.S_IFREG)) if path == target else (ancestor or info())
    with ExitStack() as stack:
        stack.enter_context(patch.object(ctypes, 'WinDLL', return_value=kernel))
        stat_call = stack.enter_context(patch.object(Path, 'lstat', autospec=True, side_effect=observe))
        stack.enter_context(patch.object(Path, 'resolve', side_effect=windows_error(error)))
        yield kernel, stat_call


class SimulatedBootstrapPaths(unittest.TestCase):
    def test_file_and_directory_error_one_and_ordinary_resolution(self):
        for directory in (False, True):
            target = DIRECT if directory else DIRECT / 'entry.py'
            selected = info(mode=stat.S_IFDIR if directory else stat.S_IFREG, size=bootstrap.FILE_LIMIT)
            with self.subTest(directory=directory), bootstrap_simulated(target, selected=selected):
                self.assertIsNone(bootstrap._direct(target, directory=directory))
            with bootstrap_simulated(target, selected=selected) as (kernel, _), patch.object(Path, 'resolve', return_value=target):
                self.assertIsNone(bootstrap._direct(target, directory=directory))
                kernel.QueryDosDeviceW.assert_not_called()

    def test_other_errors_and_non_windows_do_not_fall_back(self):
        target = DIRECT / 'entry.py'
        for code in (2, 5, 50, 144):
            with self.subTest(code=code), bootstrap_simulated(target, error=code) as (kernel, _):
                with self.assertRaises(OSError) as caught:
                    bootstrap._direct(target)
                self.assertEqual(caught.exception.winerror, code)
                kernel.QueryDosDeviceW.assert_not_called()
        with bootstrap_simulated(target) as (kernel, _), patch.object(bootstrap, 'os', SimpleNamespace(name='posix')):
            with self.assertRaises(OSError):
                bootstrap._direct(target)
            kernel.QueryDosDeviceW.assert_not_called()

    def test_kinds_links_hardlinks_and_file_budget(self):
        target = DIRECT / 'entry.py'
        for selected in (info(mode=stat.S_IFDIR), info(mode=stat.S_IFLNK),
                         info(mode=stat.S_IFREG, attributes=0x400), info(mode=stat.S_IFREG, links=2),
                         info(mode=stat.S_IFREG, size=bootstrap.FILE_LIMIT + 1),
                         info(mode=stat.S_IFREG, inode=0), info(mode=stat.S_IFREG, device=0)):
            with self.subTest(selected=selected), bootstrap_simulated(target, selected=selected), self.assertRaises(ValueError):
                bootstrap._direct(target)
        for ancestor in (info(mode=stat.S_IFREG), info(mode=stat.S_IFLNK), info(attributes=0x410), info(inode=0)):
            with self.subTest(ancestor=ancestor), bootstrap_simulated(target, ancestor=ancestor), self.assertRaises(ValueError):
                bootstrap._direct(target)
        with bootstrap_simulated(target), self.assertRaises(ValueError):
            bootstrap._direct(target, directory=True)

    def test_identity_or_protection_drift_is_refused(self):
        target = DIRECT / 'entry.py'
        for selected in (info(mode=stat.S_IFREG, inode=999), info(mode=stat.S_IFREG, device=999),
                         info(mode=stat.S_IFREG, links=2), info(mode=stat.S_IFREG, attributes=0x400),
                         info(mode=stat.S_IFREG, size=bootstrap.FILE_LIMIT + 1)):
            with self.subTest(selected=selected), bootstrap_simulated(target, after=lambda p: selected if p == target else None), self.assertRaises(ValueError):
                bootstrap._direct(target)
        for ancestor in (info(inode=999), info(attributes=0x400), info(mode=stat.S_IFREG)):
            with self.subTest(ancestor=ancestor), bootstrap_simulated(target, after=lambda p: ancestor if p == target.parent else None), self.assertRaises(ValueError):
                bootstrap._direct(target)

    def test_fallback_rejects_lexical_and_canonical_aliases(self):
        for value in ('relative.py', 'Z:/direct/../entry.py', '//host/share/entry.py', '//?/Z:/direct/entry.py',
                      'Z:/direct/entry.', 'Z:/direct/entry ', 'Z:/direct/entry.py:stream', 'Z:/direct/NUL.txt'):
            target = Path(value)
            with self.subTest(value=value), bootstrap_simulated(target), self.assertRaises(ValueError):
                bootstrap._direct(target)
        target = DIRECT / 'SHORT~1.PY'
        with bootstrap_simulated(target, kernel=Kernel(long_name=str(DIRECT / 'long-entry.py'))), self.assertRaisesRegex(ValueError, 'noncanonical'):
            bootstrap._direct(target)
        target = DIRECT / 'entry.py'
        for kernel in (Kernel(device=r'\??\Z:\alias'), Kernel(device=r'\Device\Volume\subdir'), Kernel(kind=4), Kernel(kind=0),
                       Kernel(device_result=0), Kernel(device_result=32768), Kernel(long_result=0), Kernel(long_result=32768)):
            with self.subTest(kernel=kernel), bootstrap_simulated(target, kernel=kernel), self.assertRaises(ValueError):
                bootstrap._direct(target)

    def test_path_budget_precedes_metadata_and_fallback(self):
        for value in ('Z:/' + 'a' * 240, 'Z:/' + '\U0001f600' * 120):
            target = Path(value)
            with self.subTest(value=value), bootstrap_simulated(target) as (kernel, stat_call):
                with self.assertRaisesRegex(ValueError, 'path budget'):
                    bootstrap._direct(target)
                stat_call.assert_not_called()
                kernel.QueryDosDeviceW.assert_not_called()

    def test_pre_pin_root_binding_and_path_refusals_never_reach_loader(self):
        import builtins
        import io as streams
        target = DIRECT / 'src/tools/maintain_framework.py'
        request = {'operation': 'plan', 'engine_root': str(DIRECT.parent / 'wrong-root'),
                   'engine': {'id': 'framework-managed-installation', 'version': '1.0.0', 'source_commit': 'a' * 40,
                              'files': [{'path': p, 'sha256': '0' * 64} for p in bootstrap.ENGINE_FILES]}}
        original_import = builtins.__import__
        def guarded_import(name, *args, **kwargs):
            if name == 'distribution' or name.startswith('distribution.'):
                raise AssertionError('pre-pin product import')
            return original_import(name, *args, **kwargs)
        for defect in ('root-binding', 'reparse', 'access-error'):
            stdout = streams.BytesIO()
            selected = info(mode=stat.S_IFREG, attributes=0x400 if defect == 'reparse' else 0)
            with self.subTest(defect=defect), bootstrap_simulated(target, selected=selected, error=5 if defect == 'access-error' else 1), \
                    patch.object(bootstrap, '__file__', str(target)), patch.object(sys, 'argv', [str(target)]), \
                    patch.object(sys, 'stdin', SimpleNamespace(buffer=streams.BytesIO(json.dumps(request).encode()))), \
                    patch.object(sys, 'stdout', SimpleNamespace(buffer=stdout)), \
                    patch.object(bootstrap, '_VerifiedSourceFinder', side_effect=AssertionError('premature loader')) as loader, \
                    patch.object(builtins, '__import__', side_effect=guarded_import):
                code = bootstrap.main()
            result = json.loads(stdout.getvalue())
            self.assertEqual((code, result['outcome'], result['changed']), (1, 'unsupported', False))
            self.assertEqual(result['diagnostics'][0]['code'], 'source-bootstrap')
            loader.assert_not_called()


def public(run, family, project, operation, **values):
    package = support.REPOSITORY / 'src/skills' / family
    request = dict(operation=operation, project_root=str(project), package_root=str(package), **values)
    request_path = run.write(run.root / (family + '-' + operation + '-request.json'), json.dumps(request).encode())
    argv = [support.PYTHON, '-I', '-B', package / 'scripts' / (SCRIPTS[family] + '.py'), '--request', request_path]
    result = support.run_process(argv, cwd=project)
    with (run.root / 'public-transcript.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'family': family, 'request': request, 'exit': result.returncode,
                                 'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()}) + '\n')
    response = json.loads(result.stdout)
    support.check(result.returncode == 0 and response['outcome'] == ('ok' if family == 'problem-frame-author' else 'succeeded'), str(response))
    print(json.dumps({'public': family, 'operation': operation, 'exit': result.returncode, 'outcome': response['outcome']}), flush=True)
    run.measure()
    return response


def actual_reader(run):
    output = run.case('assembly')
    commit = support.git('rev-parse', 'HEAD').decode().strip()
    built = assembly.assemble(support.REPOSITORY, commit, 'lesson-minimal', output, output)
    candidate = state.read_candidate(built['candidate_root'])
    support.check(candidate.root == Path(built['candidate_root']), 'candidate root mismatch')
    support.check(len(candidate.members) == 10, 'unexpected Lesson member count')
    print(json.dumps({'actual_reader': 'passed', 'source_commit': commit, 'candidate_root': str(candidate.root),
                      'candidate_identity': candidate.identity, 'members': len(candidate.members),
                      'reader_source_sha256': sha256(Path(state.__file__).read_bytes()).hexdigest()}), flush=True)
    return candidate


def actual_lesson(run):
    from test_knowledge import lesson_content
    project = run.case('lesson-project')
    explained = public(run, 'lesson', project, 'explain')
    store = project / explained['settings']['store']['root']
    store.mkdir(parents=True)
    query = public(run, 'lesson', project, 'query', text='selected fixture')
    support.check(not query['partial'], 'partial query')
    created = public(run, 'lesson', project, 'create', text='selected fixture', content=lesson_content(), decision={
        'action': 'new', 'query_sha256': query['query_sha256'], 'acknowledge_partial': False,
        'reason': 'Bounded Issue 378 synthetic record after actual query.'})
    path = store / (created['reference']['id'] + '.lesson.json')
    before = path.read_bytes()
    inspected = public(run, 'lesson', project, 'inspect', reference=created['reference'])
    support.check(inspected['sha256'] == sha256(before).hexdigest() and path.read_bytes() == before, 'read changed published record')
    support.check(not list(store.glob('.*')), 'unexpected writer residue')
    print(json.dumps({'actual_lesson': 'passed', 'record_bytes': len(before), 'fixture': 'direct source package, synthetic content, actual public CLI'}), flush=True)


def actual_cbf(run):
    project = run.case('cbf-project')
    explained = public(run, 'problem-frame-author', project, 'explain')
    (project / explained['result']['settings']['store']['root']).mkdir(parents=True)
    record = {'family': 'problem-frame.cbf', 'schema_version': '1.0.0', 'id': 'cbf-' + '3' * 32,
              'frame_key': 'bounded-fixture', 'title': 'Synthetic path compatibility observation', 'derived_from': None,
              'sources': [{'id': 'SRC1', 'kind': 'requirement', 'reference': 'synthetic:378', 'revision': None,
                           'locator': 'Fictional input', 'sha256': None, 'authority': 'proposed', 'authority_reference': None}],
              'statements': [{'id': name, 'category': category, 'text': text, 'basis': 'stated', 'source_ids': ['SRC1']}
                             for name, category, text in [('ACTOR1', 'actor', 'A caller.'), ('CMD1', 'command', 'Observe a value.'),
                                                          ('DOMAIN1', 'controlled-domain', 'Local fixture state.')]],
              'scenarios': [{'id': 'SC1', 'title': 'Observe one result', 'source_ids': ['SRC1'], 'given': ['A fixture'],
                             'when': ['The caller requests a value'], 'then': [{'id': 'THEN1', 'text': 'Observe a value.',
                             'basis': 'stated', 'source_ids': ['SRC1'], 'statement_ids': ['CMD1']}], 'tests_anchor': []}],
              'open_questions': []}
    created = public(run, 'problem-frame-author', project, 'create', reference='cbf-' + '3' * 32 + '.cbf.json', record=record)
    inspected = public(run, 'problem-frame-author', project, 'inspect', reference='cbf-' + '3' * 32 + '.cbf.json', expected_sha256=created['subject_sha256'])
    support.check(inspected['subject_sha256'] == created['subject_sha256'], 'CBF read mismatch')


def actual_plan(run, candidate):
    roots = {role: run.case('plan-' + role) for role in ('project', 'scratch', 'recovery')}
    commit = support.git('rev-parse', 'HEAD').decode().strip()
    pin = {'id': 'framework-managed-installation', 'version': '1.0.0', 'source_commit': commit,
           'files': [{'path': name, 'sha256': sha256((support.REPOSITORY / name).read_bytes()).hexdigest()} for name in state.ENGINE_FILES]}
    request = {'api_version': 1, 'operation': 'plan', 'engine_root': str(support.REPOSITORY), 'engine': pin,
               'project_root': str(roots['project']), 'scratch_root': str(roots['scratch']), 'staging_root': str(roots['scratch']),
               'recovery_root': str(roots['recovery']), 'candidate_root': str(candidate.root), 'candidate_identity': candidate.identity,
               'expected_lock_sha256': None, 'mode_policy': 'windows-inventory-only', 'project_data_action': 'none',
               'protected_inputs': [], 'durability': {'declared_by': 'Issue 378 fixture',
                    'declaration_reference': 'synthetic:378', 'failure_domain': 'process-termination'}}
    # Direct actual backend observation is supporting evidence, not a public plan.
    backend = io.Backend(roots, request['durability'])
    print(json.dumps({'actual_distribution_backend': 'passed', 'volume': backend._volume(roots['project']),
                      'evidence_kind': 'actual direct component, not public acceptance'}), flush=True)
    result = support.run_process([support.PYTHON, '-I', '-B', support.REPOSITORY / 'src/tools/maintain_framework.py'],
                                  cwd=support.REPOSITORY, input=json.dumps(request).encode())
    for name, raw in [('plan-request.json', json.dumps(request, indent=2).encode()), ('plan-response.json', result.stdout), ('plan-stderr.txt', result.stderr)]:
        run.write(run.root / name, raw)
    response = json.loads(result.stdout)
    support.check(result.returncode == 0 and response['outcome'] == 'planned', str(response))
    plan = response['plan']
    support.check(plan['engine'] == pin and plan['candidate_identity'] == candidate.identity, 'plan source binding mismatch')
    support.check(sha256(state.json_bytes(plan)).hexdigest() == response['plan_sha256'], 'plan digest mismatch')
    prerequisites = {row['id']: row['status'] for row in plan['prerequisites']}
    support.check(prerequisites['native-writer-backend'] == 'satisfied' and prerequisites['writer-engine-closure'] == 'satisfied',
                  'plan did not establish native backend and pinned source closure')
    support.check(all(not list(root.iterdir()) for root in roots.values()), 'plan mutated fixture roots')
    print(json.dumps({'actual_distribution_plan': 'passed', 'exit': result.returncode, 'outcome': response['outcome'],
                      'engine_source_commit': commit, 'plan_sha256': response['plan_sha256'], 'delta_members': len(plan['delta']),
                      'prerequisites': prerequisites, 'native_apply': 'not-executed'}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=['regressions', 'bootstrap-regressions', 'actual', 'public-plan'])
    parser.add_argument('--output-root', type=Path)
    args = parser.parse_args()
    support.check(os.name == 'nt' and sys.flags.isolated and sys.dont_write_bytecode, 'requires Windows and -I -B')
    if args.mode in {'regressions', 'bootstrap-regressions'}:
        print('Evidence kind: simulated Windows API/path responses; not native acceptance.', flush=True)
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SimulatedBootstrapPaths if args.mode == 'bootstrap-regressions' else SimulatedWindowsPaths))
        return 0 if result.wasSuccessful() and not result.skipped else 1
    support.check(args.output_root is not None, 'actual observations require explicit --output-root')
    run = support.FixtureRun(args.output_root)
    success = False
    try:
        with support.use_run(run):
            print(json.dumps({'actual_run': str(run.root), 'runtime': support.runtime_versions()}), flush=True)
            candidate = actual_reader(run)
            if args.mode == 'actual':
                actual_lesson(run)
                # The first actual writer setup succeeded before another backend runs.
                actual_cbf(run)
            actual_plan(run, candidate)
            success = True
    finally:
        # Keep this explicitly selected evidence; close(False) means retained,
        # not a fabricated test failure and not permission to delete prior runs.
        observation = run.close(False)
        observation.update(selected_checks_passed=success, retention='requested diagnostic evidence')
        print(json.dumps({'observation': observation}), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
