"""Windows path API simulations; no public reader, apply or installation trial."""
from contextlib import ExitStack, contextmanager
from ctypes import wintypes as w
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
from distribution import installation_state as state, installation_io as io

SCRIPTS = {
    'lesson-author': 'lesson', 'adr-author': 'adr', 'standards-promotion': 'standards_promotion',
    'pr-author': 'pr', 'local-backlog': 'local_backlog',
    'problem-frame-author': 'problem_frame',
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
        for family in ('lesson-author', 'problem-frame-author', 'distribution'):
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
                    with self.assertRaises((OSError, ValueError, MODULES['lesson-author'].Fault, MODULES['problem-frame-author'].Fault)):
                        invoke()
                    if error != 144:
                        kernel.GetVolumeInformationByHandleW.assert_not_called()
            with simulated(Kernel(filesystem='ReFS')) as (kernel, _, _):
                if family == 'distribution':
                    self.assertTrue(invoke())
                else:
                    with self.assertRaises((MODULES['lesson-author'].Fault, MODULES['problem-frame-author'].Fault)):
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

if __name__ == "__main__":
    unittest.main()
