#!/usr/bin/env python3
"""GWT tests for portable classified test-fixture routing."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
import test_fixture_runtime as FIXTURES  # noqa: E402


class WorkspaceTemporaryDirectory:
    """Use inherited workspace ACLs so the test is deterministic on Windows."""

    def __init__(self, prefix: str = "perf001-") -> None:
        base = ROOT / ".tmp/perf001-runtime-tests"
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / f"{prefix}{uuid.uuid4().hex[:12]}"
        self.path.mkdir()
        self.name = str(self.path)

    def cleanup(self) -> None:
        if self.path.exists():
            shutil.rmtree(self.path)

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, *_: object) -> None:
        self.cleanup()


class TestFixtureRuntimeGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_root = os.environ.pop(FIXTURES.ENVIRONMENT_VARIABLE, None)
        self.previous_diagnostics = os.environ.pop(FIXTURES.DIAGNOSTICS_VARIABLE, None)
        FIXTURES.close_process_session()

    def tearDown(self) -> None:
        FIXTURES.close_process_session()
        if self.previous_root is not None:
            os.environ[FIXTURES.ENVIRONMENT_VARIABLE] = self.previous_root
        else:
            os.environ.pop(FIXTURES.ENVIRONMENT_VARIABLE, None)
        if self.previous_diagnostics is not None:
            os.environ[FIXTURES.DIAGNOSTICS_VARIABLE] = self.previous_diagnostics
        else:
            os.environ.pop(FIXTURES.DIAGNOSTICS_VARIABLE, None)

    def test_gwt_001_given_no_configuration_when_resolved_then_os_default_is_preserved(self) -> None:
        resolution = FIXTURES.resolve_fixture_root(environ={})
        self.assertEqual("default", resolution.route)
        self.assertEqual("os-default", resolution.source)
        self.assertIsNone(resolution.preflight)

    def test_gwt_002_given_runner_and_environment_roots_when_resolved_then_runner_wins(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            explicit = Path(parent) / "explicit"
            environment = Path(parent) / "environment"
            explicit.mkdir()
            environment.mkdir()
            resolution = FIXTURES.resolve_fixture_root(
                explicit, environ={FIXTURES.ENVIRONMENT_VARIABLE: str(environment)}
            )
            self.assertEqual("runner-parameter", resolution.source)
            self.assertEqual(explicit.resolve(), resolution.preflight.root)

    def test_gwt_003_given_environment_root_when_resolved_then_it_is_selected(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            resolution = FIXTURES.resolve_fixture_root(
                environ={FIXTURES.ENVIRONMENT_VARIABLE: str(root)}
            )
            self.assertEqual("accelerated", resolution.route)
            self.assertEqual("repository-environment", resolution.source)

    def test_gwt_004_given_invalid_roots_when_preflight_runs_then_it_fails_fast(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            missing = Path(parent) / "missing"
            file_root = Path(parent) / "file"
            file_root.write_text("not a directory", encoding="utf-8")
            cases = (
                (Path("relative"), "absolute"),
                (missing, "does not exist"),
                (file_root, "not a directory"),
                (Path(parent).anchor, "filesystem or volume root"),
            )
            for value, expected in cases:
                with self.subTest(value=str(value)):
                    with self.assertRaisesRegex(FIXTURES.FixtureRootError, expected):
                        FIXTURES.preflight_fixture_root(value)

    def test_gwt_005_given_unwritable_or_reparse_root_when_preflight_runs_then_it_fails(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            with mock.patch.object(FIXTURES, "_is_reparse_point", return_value=True):
                with self.assertRaisesRegex(FIXTURES.FixtureRootError, "symlink or reparse"):
                    FIXTURES.preflight_fixture_root(root)
            parent_reparse = Path(parent) / "reparse-parent"
            child_root = parent_reparse / "fixtures"
            child_root.mkdir(parents=True)
            with mock.patch.object(
                FIXTURES,
                "_is_reparse_point",
                side_effect=lambda path: path.name == "reparse-parent",
            ):
                with self.assertRaisesRegex(FIXTURES.FixtureRootError, "traverse"):
                    FIXTURES.preflight_fixture_root(child_root)
            with mock.patch.object(Path, "write_bytes", side_effect=PermissionError("denied")):
                with self.assertRaisesRegex(FIXTURES.FixtureRootError, "not writable"):
                    FIXTURES.preflight_fixture_root(root)

    def test_gwt_006_given_valid_root_when_session_created_then_run_is_unique_and_contained(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            first = FIXTURES.FixtureRunSession(FIXTURES.resolve_fixture_root(root, environ={}))
            second = FIXTURES.FixtureRunSession(FIXTURES.resolve_fixture_root(root, environ={}))
            try:
                self.assertNotEqual(first.run_directory, second.run_directory)
                self.assertTrue(FIXTURES.is_contained_run_directory(root, first.run_directory))
                self.assertTrue(FIXTURES.is_contained_run_directory(root, second.run_directory))
            finally:
                first.close()
                second.close()

    def test_gwt_007_given_contained_run_and_sibling_when_cleaned_then_only_run_is_removed(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            sentinel = root / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            session = FIXTURES.FixtureRunSession(FIXTURES.resolve_fixture_root(root, environ={}))
            run = session.run_directory
            session.close()
            self.assertFalse(run.exists())
            self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))

    def test_gwt_008_given_outside_or_root_path_when_cleaned_then_deletion_is_refused(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            outside = Path(parent) / f"{FIXTURES.RUN_PREFIX}outside"
            outside.mkdir()
            sentinel = outside / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            for value in (root, outside):
                with self.subTest(value=value.name):
                    with self.assertRaisesRegex(FIXTURES.FixtureRootError, "outside"):
                        FIXTURES.cleanup_run_directory(root, value)
            self.assertEqual("keep", sentinel.read_text(encoding="utf-8"))

    def test_gwt_009_given_acceleration_when_ephemeral_fixture_created_then_it_uses_root(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            with mock.patch.dict(os.environ, {FIXTURES.ENVIRONMENT_VARIABLE: str(root)}):
                with FIXTURES.TemporaryDirectory(prefix="ephemeral-") as temporary:
                    fixture = Path(temporary).resolve()
                    self.assertEqual(root.resolve(), fixture.parents[1])

    def test_gwt_010_given_acceleration_when_semantic_fixtures_created_then_they_bypass_root(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "fixtures"
            root.mkdir()
            with mock.patch.dict(os.environ, {FIXTURES.ENVIRONMENT_VARIABLE: str(root)}):
                with mock.patch.object(
                    FIXTURES.system_tempfile,
                    "TemporaryDirectory",
                    side_effect=lambda *args, **kwargs: WorkspaceTemporaryDirectory("semantic-default-"),
                ):
                    for classification in (
                        FIXTURES.FixtureClassification.DURABILITY,
                        FIXTURES.FixtureClassification.PLATFORM,
                        FIXTURES.FixtureClassification.UNCLASSIFIED,
                    ):
                        with self.subTest(classification=classification.value):
                            with FIXTURES.TemporaryDirectory(classification=classification) as temporary:
                                self.assertNotIn(root.resolve(), Path(temporary).resolve().parents)

    def test_gwt_011_given_unknown_classification_when_routed_then_it_fails_closed(self) -> None:
        with self.assertRaisesRegex(FIXTURES.FixtureRootError, "unknown fixture classification"):
            FIXTURES.TemporaryDirectory(classification="unknown")

    def test_gwt_012_given_platform_paths_when_classified_then_stable_types_are_returned(self) -> None:
        self.assertEqual(
            "windows-local-filesystem",
            FIXTURES.path_type_for_diagnostics(
                f"{chr(81)}{chr(58)}\\fixtures", platform_kind="windows"
            ),
        )
        self.assertEqual(
            "wsl-mounted-windows-filesystem",
            FIXTURES.path_type_for_diagnostics("/mnt/q/fixtures", platform_kind="wsl"),
        )
        self.assertEqual(
            "wsl-native-filesystem",
            FIXTURES.path_type_for_diagnostics("/dev/shm/fixtures", platform_kind="wsl"),
        )
        self.assertEqual(
            "linux-native-filesystem",
            FIXTURES.path_type_for_diagnostics("/tmp/fixtures", platform_kind="linux"),
        )

    def test_gwt_013_given_wsl_mount_when_guidance_rendered_then_warning_is_non_blocking(self) -> None:
        warning = FIXTURES.wsl_mount_guidance(
            workspace="/mnt/q/source", fixture_path="/dev/shm/fixtures", platform_kind="wsl"
        )
        self.assertIn("non-blocking", warning)
        self.assertIn("WSL-native", warning)

    def test_gwt_014_given_wsl_native_paths_when_guidance_rendered_then_no_warning_is_emitted(self) -> None:
        self.assertIsNone(
            FIXTURES.wsl_mount_guidance(
                workspace="/home/source", fixture_path="/dev/shm/fixtures", platform_kind="wsl"
            )
        )

    def test_gwt_015_given_private_root_when_diagnostic_rendered_then_path_is_absent(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            root = Path(parent) / "private-user" / "fixtures"
            root.mkdir(parents=True)
            diagnostic = FIXTURES.resolve_fixture_root(root, environ={}).diagnostic(workspace=ROOT)
            rendered = json.dumps(diagnostic)
            self.assertNotIn(str(root), rendered)
            self.assertNotIn("private-user", rendered)
            self.assertEqual("accelerated", diagnostic["route"])

    def test_gwt_016_given_manifest_when_loaded_then_only_tracked_ephemeral_tests_are_selected(self) -> None:
        manifest = FIXTURES.load_classification_manifest(ROOT)
        tests = manifest["tests"]
        self.assertEqual(3, len(tests))
        self.assertTrue(all(item["classification"] == "ephemeral-fixture-io" for item in tests))
        excluded = {item["path"]: item for item in manifest["excluded_semantic_suites"]}
        self.assertEqual(
            ["durability-storage-semantics", "platform-filesystem-semantics"],
            excluded[".ai/scripts/tests/test_ai_context_package_apply.py"]["classifications"],
        )
        self.assertEqual(
            "existing-default",
            excluded[".ai/scripts/tests/test_ai_context_package_apply.py"]["route"],
        )

    def test_gwt_017_given_insufficient_benchmark_runs_when_invoked_then_it_fails_before_tests(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                ".ai/scripts/run-test-fixture-profile.py",
                "benchmark",
                "--mode",
                "default",
                "--condition",
                "warm",
                "--runs",
                "2",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("at least three runs", completed.stderr)

    def test_gwt_018_given_manual_ci_profile_when_inspected_then_root_is_explicit_only(self) -> None:
        workflow = (ROOT / ".github/workflows/test-fixture-acceleration.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("fixture_root:", workflow)
        self.assertIn("AI_CONTEXT_TEST_TMP_ROOT: ${{ inputs.fixture_root }}", workflow)
        self.assertIn("runs-on: self-hosted", workflow)
        self.assertNotIn("--fixture-root", workflow)
        self.assertNotIn("${{ vars.", workflow)

    def test_gwt_019_given_guidance_when_inspected_then_private_host_details_are_not_contract(self) -> None:
        guide = (
            ROOT
            / ".dev/guides/implementation-guides/PORTABLE-TEST-FIXTURE-ACCELERATION-GUIDE.md"
        ).read_text(encoding="utf-8")
        self.assertIn("<absolute-disposable-root>", guide)
        self.assertNotRegex(guide, r"(?i)\b[A-Z]:\\")
        self.assertNotIn("/dev/shm/ai-context-tests", guide)

    def test_gwt_020_given_default_ephemeral_fixture_when_created_then_phase_is_counted(self) -> None:
        with mock.patch.object(
            FIXTURES.system_tempfile,
            "TemporaryDirectory",
            side_effect=lambda *args, **kwargs: WorkspaceTemporaryDirectory("counted-default-"),
        ):
            with FIXTURES.TemporaryDirectory():
                pass
        self.assertEqual(1, FIXTURES._DEFAULT_FIXTURE_COUNT)
        self.assertGreaterEqual(FIXTURES._DEFAULT_FIXTURE_SECONDS, 0.0)

    def test_gwt_021_given_private_invalid_root_when_rejected_then_error_omits_path(self) -> None:
        with WorkspaceTemporaryDirectory() as parent:
            private_root = Path(parent) / "private-fragment" / "missing"
            with self.assertRaises(FIXTURES.FixtureRootError) as captured:
                FIXTURES.preflight_fixture_root(private_root)
            self.assertNotIn(str(private_root), str(captured.exception))
            self.assertNotIn("private-fragment", str(captured.exception))

    def test_gwt_022_given_accelerated_mode_without_root_when_run_then_it_fails_before_tests(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                ".ai/scripts/run-test-fixture-profile.py",
                "run",
                "--mode",
                "accelerated",
                "--condition",
                "warm",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={key: value for key, value in os.environ.items() if key != FIXTURES.ENVIRONMENT_VARIABLE},
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("requires --fixture-root or AI_CONTEXT_TEST_TMP_ROOT", completed.stderr)


if __name__ == "__main__":
    unittest.main()
