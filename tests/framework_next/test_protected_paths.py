"""Protected input path simulations; no native plan or installation trial."""
from contextlib import ExitStack, contextmanager
from hashlib import sha256
import ctypes
import io
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

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


if __name__ == "__main__":
    unittest.main()
