"""Small fixtures for selected loader/maintenance unit tests, not installation trials.

Pure schema/projection tests do not use this helper. Count explicit writes as they
happen; do not repeatedly scan the fixture tree or launch Git for accounting.
"""
from contextlib import contextmanager
from pathlib import Path
import os
import re
import stat
import shutil
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[2]
ACTIVE = None


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def _fixture_root(path):
    """Resolve one captured cleanup root; only native Windows error 1 has a fallback."""
    check(path.is_absolute() and ".." not in path.parts, "unsafe fixture root; cleanup refused")
    def ancestry():
        rows = []
        for part in (path, *path.parents):
            info = part.lstat()
            check(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
                  and not getattr(info, "st_file_attributes", 0) & 0x400,
                  "linked fixture ancestry; cleanup refused")
            rows.append((info.st_dev, info.st_ino))
        return rows
    before = ancestry()
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        if os.name != "nt" or getattr(exc, "winerror", None) != 1:
            raise
        check(re.fullmatch(r"[A-Za-z]:", path.drive) and all(device and inode for device, inode in before),
              "native fixture identity unavailable; cleanup refused")
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.QueryDosDeviceW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        kernel.QueryDosDeviceW.restype = wintypes.DWORD
        device = ctypes.create_unicode_buffer(32768)
        size = kernel.QueryDosDeviceW(path.drive, device, len(device))
        check(0 < size < len(device) and re.fullmatch(r"\\Device\\[^\\]+", device.value),
              "aliased fixture drive; cleanup refused")
        kernel.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
        kernel.GetDriveTypeW.restype = wintypes.UINT
        check(kernel.GetDriveTypeW(path.anchor) in {2, 3, 5, 6}, "nonlocal fixture drive; cleanup refused")
        kernel.GetLongPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        kernel.GetLongPathNameW.restype = wintypes.DWORD
        canonical = ctypes.create_unicode_buffer(32768)
        size = kernel.GetLongPathNameW(str(path), canonical, len(canonical))
        check(0 < size < len(canonical), "canonical fixture name unavailable; cleanup refused")
        resolved = Path(canonical.value)
    check(resolved == path and ancestry() == before, "fixture ancestry changed; cleanup refused")
    return resolved


class FixtureRun:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="aicf-tests-")).resolve()
        info = self.root.stat()
        self.identity = (info.st_dev, info.st_ino)
        self.authored_bytes = 0
        self.files_written = 0

    def case(self, name):
        check(name and Path(name).name == name and name not in {".", ".."}, "unsafe fixture name")
        target = self.root / name
        target.mkdir()
        return target

    def write(self, path, raw):
        path = Path(path).absolute()
        check(path.is_relative_to(self.root) and ".." not in path.parts, "fixture write escaped run")
        check(type(raw) is bytes, "fixture bytes required")
        with path.open("xb") as stream:
            stream.write(raw)
        self.authored_bytes += len(raw)
        self.files_written += 1
        return path

    def measure(self):
        # Explicit helper writes only, not OS/durability or total filesystem I/O.
        return {"helper_written_files": self.files_written, "helper_written_bytes": self.authored_bytes}

    def close(self):
        resolved = _fixture_root(self.root)
        info = self.root.lstat()
        check(resolved == self.root and (info.st_dev, info.st_ino) == self.identity,
              "fixture root identity changed; cleanup refused")
        shutil.rmtree(resolved)


@contextmanager
def use_run(run):
    global ACTIVE
    previous, ACTIVE = ACTIVE, run
    try:
        yield run
    finally:
        ACTIVE = previous


def active_run():
    check(ACTIVE is not None, "fixture requires FixtureTestCase")
    return ACTIVE


class FixtureTestCase(unittest.TestCase):
    def setUp(self):
        self.fixture_run = FixtureRun()
        self.addCleanup(self.fixture_run.close)
        context = use_run(self.fixture_run)
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
