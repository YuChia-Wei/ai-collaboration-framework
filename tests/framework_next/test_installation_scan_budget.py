"""Issue #386 bounded lookup regression; no public-entry or native-backend substitute."""
from __future__ import annotations

from contextlib import contextmanager
import io as streams
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).absolute().parents[2]
sys.path.insert(0, str(SOURCE / "src"))
from distribution import installation_io as native
from distribution import installation_state as state

MEASUREMENTS = []


class ObservationBackend:
    """Focused namespace/read checks only; actual public trial uses native Backend."""
    windows = True

    def flush_directory(self, directory):
        state._no_links(directory)

    def move(self, source, target, replace):
        if replace:
            os.replace(source, target)
        else:
            source.rename(target)


class LegacyIO(native.IO):
    def locate(self, root, name):
        self.reader.listings.clear()
        return super().locate(root, name)


@contextmanager
def scans():
    counts = {"listings": 0}
    original = os.scandir

    def counted(directory):
        counts["listings"] += 1
        return original(directory)

    with patch.object(state.os, "scandir", counted):
        yield counts


class ScanBudgetTests(unittest.TestCase):
    root: Path
    baseline: Path

    def folder(self):
        target = self.root / self._testMethodName
        target.mkdir()
        return target

    def writer(self, cls=native.IO):
        return cls(ObservationBackend(), state._Reader(), native.Changes())

    def refused(self, code, action):
        with self.assertRaises(state.InstallationError) as error:
            action()
        self.assertEqual(error.exception.diagnostic["code"], code)

    def test_repeated_lookup_budget_legacy_and_repaired(self):
        # The 131-object baseline was created with the original IO.create loop.
        # Same real directory, same 200 requested observations, same 20,000 cap.
        self.assertEqual(len(list((self.baseline / "objects").iterdir())), 131)
        for cls in (LegacyIO, native.IO):
            writer = self.writer(cls)
            completed = 0
            failure = None
            with scans() as counts:
                try:
                    for _ in range(200):
                        self.assertEqual(writer.raw(self.baseline, "objects/" + "0" * 64), b"x")
                        completed += 1
                except state.InstallationError as error:
                    failure = error.diagnostic["code"]
            row = dict(implementation=cls.__name__, requested=200, completed=completed,
                       entries=writer.reader.entries, bytes_read=writer.reader.bytes,
                       entry_limit=state.LIMITS["entries"], failure=failure, **counts)
            MEASUREMENTS.append(row)
            if cls is LegacyIO:
                self.assertEqual(failure, "scan-limit")
                self.assertEqual(writer.reader.entries, 20001)
                self.assertLess(completed, 200)
            else:
                self.assertIsNone(failure)
                self.assertEqual(completed, 200)
                self.assertEqual(counts["listings"], 2)
                self.assertEqual(writer.reader.entries, 132)

    def test_own_mutations_invalidate_even_with_unchanged_clock(self):
        root = self.folder()
        writer = self.writer()
        # The clock/identity signature is deliberately held constant per path.
        # Every own namespace mutation must still invalidate its parent.
        signatures = {}
        original = writer.reader._directory_observation

        def constant(directory):
            current = original(directory)  # retain real direct-directory checks
            return signatures.setdefault(directory, current)

        with patch.object(writer.reader, "_directory_observation", constant):
            self.assertIsNone(writer.locate(root, "objects"))
            writer.create(root, "objects/one", b"one", "recovery")
            self.assertEqual(writer.raw(root, "objects/one"), b"one")
            writer.publish(root, "objects/two", b"two", None, "0" * 32)
            self.assertEqual(writer.raw(root, "objects/two"), b"two")
            writer.publish(root, "objects/two", b"new", b"two", "0" * 32)
            self.assertEqual(writer.raw(root, "objects/two"), b"new")
            writer.remove(root, "objects/two", b"new")
            self.assertIsNone(writer.raw(root, "objects/two"))
            writer.directory(root, "empty", "scratch")
            self.assertIsNotNone(writer.locate(root, "empty"))

    def test_case_spelling_and_exclusive_create(self):
        root = self.folder()
        (root / "Exact").write_bytes(b"original")
        writer = self.writer()
        self.assertEqual(writer.raw(root, "Exact"), b"original")
        self.refused("path-alias", lambda: writer.create(root, "exact", b"bad", "project"))
        self.refused("exclusive-file", lambda: writer.create(root, "Exact", b"bad", "project"))
        self.assertFalse(writer.changes.changed)
        self.assertEqual((root / "Exact").read_bytes(), b"original")

    def test_case_alias_collision_and_overflow_are_not_cached(self):
        root = self.folder()
        for names, code, count in ((["a", "A"], "path-alias", 2),
                                   ((f"n{i}" for i in range(20001)), "scan-limit", 20001)):
            reader = state._Reader()

            @contextmanager
            def listing(directory):
                yield (SimpleNamespace(name=name) for name in names)

            with patch.object(state.os, "scandir", listing):
                self.refused(code, lambda: reader.listing(root))
            self.assertNotIn(root, reader.listings)
            self.assertEqual(reader.entries, count)

    def test_external_directory_change_refreshes_absence_and_spelling(self):
        root = self.folder()
        writer = self.writer()
        self.assertIsNone(writer.locate(root, "absent"))
        before = root.stat()
        (root / "Absent").write_bytes(b"new")
        os.utime(root, ns=(before.st_atime_ns, before.st_mtime_ns + 2_000_000_000))
        self.refused("path-alias", lambda: writer.locate(root, "absent"))

    def test_directory_drift_during_listing_is_refused(self):
        root = self.folder()
        (root / "one").write_bytes(b"1")
        reader = state._Reader()
        original = os.scandir

        @contextmanager
        def changing(directory):
            before = directory.stat()
            with original(directory) as rows:
                yield rows
            (directory / "two").write_bytes(b"2")
            os.utime(directory, ns=(before.st_atime_ns, before.st_mtime_ns + 2_000_000_000))

        with patch.object(state.os, "scandir", changing):
            self.refused("directory-drift", lambda: reader.listing(root))
        self.assertNotIn(root, reader.listings)

    def test_replaced_ancestor_does_not_reuse_old_children(self):
        root = self.folder()
        parent = root / "parent"
        parent.mkdir()
        (parent / "one").write_bytes(b"1")
        writer = self.writer()
        self.assertEqual(writer.raw(root, "parent/one"), b"1")
        parent.rename(root / "retired")
        parent.mkdir()
        self.assertIsNone(writer.raw(root, "parent/one"))

    def test_links_and_reparse_attributes_refused_on_reuse(self):
        root = self.folder()
        reader = state._Reader()
        reader.listing(root)
        original = Path.lstat
        for mode, attributes in ((stat.S_IFLNK | 0o777, 0), (stat.S_IFDIR | 0o755, 0x400)):
            def changed(path, *args, **kwargs):
                info = original(path, *args, **kwargs)
                if path != root:
                    return info
                return SimpleNamespace(st_mode=mode, st_file_attributes=attributes)
            with patch.object(Path, "lstat", changed):
                self.refused("linked-path", lambda: reader.listing(root))

    def test_hardlink_and_exact_byte_readback(self):
        root = self.folder()
        target = root / "one"
        target.write_bytes(b"one")
        os.link(target, root / "hardlink")
        self.refused("hardlinked-file", lambda: self.writer().raw(root, "one"))
        writer = self.writer()
        original = writer.backend.flush_directory

        def changed(directory):
            original(directory)
            if (root / "written").exists():
                (root / "written").write_bytes(b"drift")

        with patch.object(writer.backend, "flush_directory", changed):
            self.refused("write-readback", lambda: writer.create(root, "written", b"exact", "project"))
        self.assertTrue(writer.changes.changed)

    def test_exact_read_and_file_limit_remain_enforced(self):
        root = self.folder()
        (root / "one").write_bytes(b"one")
        writer = self.writer()
        self.refused("file-limit", lambda: writer.raw(root, "one", limit=2))
        self.refused("current-drift", lambda: writer.expect(root, "one", b"different"))
        self.assertEqual(writer.raw(root, "one"), b"one")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    selected = Path("F:/framework-next/p7-runs/scan-budget-386")
    if not args.root.is_relative_to(selected) or not args.baseline.is_relative_to(selected):
        raise ValueError("use only the owner-selected fixture root")
    if not args.result.is_relative_to(Path("C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n386/observations")):
        raise ValueError("use only the owner-selected evidence root")
    args.root.mkdir()
    ScanBudgetTests.root, ScanBudgetTests.baseline = args.root, args.baseline
    transcript = streams.StringIO()
    result = unittest.TextTestRunner(stream=transcript, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ScanBudgetTests))
    evidence = dict(tests=result.testsRun, success=result.wasSuccessful(), failures=len(result.failures),
                    errors=len(result.errors), skipped=len(result.skipped), measurements=MEASUREMENTS,
                    limits=dict(state.LIMITS), transcript=transcript.getvalue(),
                    scope="focused observations; mock backend/alias/reparse rows are not native/public acceptance")
    with args.result.open("x", encoding="utf-8") as stream:
        json.dump(evidence, stream, indent=2)
    print(json.dumps(evidence, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
