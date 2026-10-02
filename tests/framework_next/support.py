"""Small fixtures for selected loader/maintenance unit tests, not installation trials.

Pure schema/projection tests do not use this helper. Count explicit writes as they
happen; do not repeatedly scan the fixture tree or launch Git for accounting.
"""
from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[2]
ACTIVE = None


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


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
        resolved = self.root.resolve(strict=True)
        info = self.root.stat()
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
