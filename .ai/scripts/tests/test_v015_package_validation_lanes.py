#!/usr/bin/env python3
"""GWT contracts for the independent v0.15 package validation lanes."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))

import ai_context_v015_validation as VALIDATION


CONTRACT = ROOT / ".ai/distribution/validation/v015-package-validation-lanes.yaml"
SCHEMA = ROOT / ".ai/distribution/schemas/v015-package-validation-terminal.schema.yaml"


def terminal(lane: str, outcome: str, platform_id: str = "windows", trusted: bool = False) -> dict[str, object]:
    evidence: dict[str, object] = {"actual_upgrade": False}
    phases: dict[str, dict[str, object]] = {}
    if lane == "fast":
        evidence.update({"material_target_mutation": False, "legacy_immutable": True})
    elif lane == "medium":
        evidence.update({"synthetic_clean_install": True, "legacy_immutable": True})
    elif outcome == "passed":
        evidence.update(
            {
                "actual_upgrade": True,
                "consumed_ai_context_test_tmp_root": False,
                "legacy_immutable": True,
                "git_inspection": {"process_count": {}},
            }
        )
        phases = {
            name: {"outcome": "passed", "duration_ms": 1.0}
            for name in ("build", "extract", "snapshot", "plan", "decision", "apply", "receipt", "cleanup")
        }
    return {
        "schema_version": VALIDATION.SCHEMA_VERSION,
        "lane": lane,
        "outcome": outcome,
        "subject": {
            "commit": "a" * 40,
            "source_version": "0.14.0",
            "candidate_version": "0.15.0",
        },
        "command": {"id": f"lane-{lane}", "digest": "b" * 64, "budget_seconds": 1},
        "execution": {
            "platform": platform_id,
            "attempt": 1,
            "trusted_reference": trusted,
            "duration_ms": 1.0,
        },
        "evidence": evidence,
        "phases": phases,
        "cleanup": {"outcome": "passed", "work_root_removed": True},
        "failure_fingerprint": None if outcome == "passed" else "c" * 64,
    }


class V015PackageValidationLaneGwtTests(unittest.TestCase):
    def test_gwt_001_given_lane_contract_when_read_then_commands_budgets_and_outcomes_are_independent(self) -> None:
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(
            ["passed", "failed", "blocked-by-environment", "not-applicable", "deferred-with-owner"],
            contract["outcomes"],
        )
        self.assertEqual({"fast", "medium", "long"}, set(contract["lanes"]))
        self.assertEqual({"fast": 90, "medium": 240, "long": 1200}, {
            lane: record["budget_seconds"] for lane, record in contract["lanes"].items()
        })
        self.assertEqual(3, len({record["command"] for record in contract["lanes"].values()}))
        self.assertFalse(contract["lanes"]["fast"]["material_target_mutation"])
        self.assertFalse(contract["lanes"]["fast"]["proves_actual_upgrade"])
        self.assertFalse(contract["lanes"]["medium"]["proves_actual_upgrade"])
        self.assertTrue(contract["lanes"]["long"]["proves_actual_upgrade"])
        self.assertIn("run-v015-package-validation-wsl.py", contract["lanes"]["long"]["windows_to_linux_command"])
        self.assertEqual("exact-head-git-bundle-over-stdin", contract["lanes"]["long"]["wsl_execution"]["transport"])
        self.assertEqual("forbidden", contract["lanes"]["long"]["wsl_execution"]["shared_windows_mount"])
        self.assertEqual(contract["outcomes"], schema["properties"]["outcome"]["enum"])

    def test_gwt_002_given_fast_and_medium_pass_when_aggregated_without_long_then_actual_upgrade_stays_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for index, record in enumerate((terminal("fast", "passed"), terminal("medium", "passed"))):
                path = root / f"terminal-{index}.json"
                path.write_text(json.dumps(record), encoding="utf-8")
                paths.append(path)

            return_code, aggregate = VALIDATION.aggregate_terminals(paths, root / "aggregate.json")

            self.assertEqual(1, return_code)
            self.assertEqual("blocked-by-environment", aggregate["actual_upgrade_outcome"])
            self.assertFalse(aggregate["projection"]["fast_or_medium_can_prove_actual_upgrade"])
            self.assertEqual("blocked-by-environment", aggregate["trusted_actual_upgrade"]["windows"]["outcome"])
            self.assertEqual("blocked-by-environment", aggregate["trusted_actual_upgrade"]["linux"]["outcome"])

    def test_gwt_003_given_only_one_trusted_platform_when_aggregated_then_the_other_platform_is_not_substituted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = [
                terminal("fast", "passed"),
                terminal("medium", "passed"),
                terminal("long", "passed", "windows", True),
            ]
            paths = []
            for index, record in enumerate(records):
                path = root / f"terminal-{index}.json"
                path.write_text(json.dumps(record), encoding="utf-8")
                paths.append(path)

            return_code, aggregate = VALIDATION.aggregate_terminals(paths, root / "aggregate.json")

            self.assertEqual(1, return_code)
            self.assertEqual("passed", aggregate["trusted_actual_upgrade"]["windows"]["outcome"])
            self.assertEqual("blocked-by-environment", aggregate["trusted_actual_upgrade"]["linux"]["outcome"])
            self.assertNotEqual("passed", aggregate["actual_upgrade_outcome"])

    def test_gwt_004_given_both_trusted_actual_upgrades_when_aggregated_then_the_projection_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            records = [
                terminal("fast", "passed"),
                terminal("medium", "passed"),
                terminal("long", "passed", "windows", True),
                terminal("long", "passed", "linux", True),
            ]
            paths = []
            for index, record in enumerate(records):
                path = root / f"terminal-{index}.json"
                path.write_text(json.dumps(record), encoding="utf-8")
                paths.append(path)

            return_code, aggregate = VALIDATION.aggregate_terminals(paths, root / "aggregate.json")

            self.assertEqual(0, return_code)
            self.assertEqual("passed", aggregate["actual_upgrade_outcome"])
            self.assertEqual("passed", aggregate["outcome"])

    def test_gwt_005_given_same_failure_retry_when_no_material_change_or_new_attempt_three_authority_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            prior_path = Path(temporary) / "prior.json"
            prior = terminal("long", "failed", "windows", True)
            prior["subject"]["commit"] = "d" * 40
            prior_path.write_text(json.dumps(prior), encoding="utf-8")

            with self.assertRaisesRegex(VALIDATION.ValidationError, "retry-material-state-change-required"):
                VALIDATION.validate_retry(
                    lane="long",
                    subject_commit="d" * 40,
                    attempt=2,
                    prior_terminal=prior_path,
                    material_state_change=None,
                    authorization_ref=None,
                )
            with self.assertRaisesRegex(VALIDATION.ValidationError, "attempt-three-authorization-required"):
                VALIDATION.validate_retry(
                    lane="long",
                    subject_commit="d" * 40,
                    attempt=3,
                    prior_terminal=prior_path,
                    material_state_change="environment-access-restored",
                    authorization_ref=None,
                )
            accepted = VALIDATION.validate_retry(
                lane="long",
                subject_commit="d" * 40,
                attempt=3,
                prior_terminal=prior_path,
                material_state_change="environment-access-restored",
                authorization_ref="workflow-owner-authorization-2",
            )
            self.assertTrue(accepted["retry"])

    def test_gwt_006_given_long_lane_when_tmp_opt_in_is_present_then_the_lane_records_non_consumption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "lane"
            output.mkdir()

            def fake_long(root: Path, commit: str, lane_output: Path, phases: dict) -> dict[str, object]:
                (lane_output / "work").mkdir()
                phases.update(
                    {
                        name: {"outcome": "passed", "duration_ms": 1.0}
                        for name in ("build", "extract", "snapshot", "plan", "decision", "apply", "receipt")
                    }
                )
                return {
                    "actual_upgrade": True,
                    "consumed_ai_context_test_tmp_root": False,
                    "legacy_immutable": True,
                    "git_inspection": {"process_count": {}},
                }

            with mock.patch.object(VALIDATION, "validate_output_root", return_value=output), mock.patch.object(
                VALIDATION,
                "validate_subject",
                return_value={"commit": "e" * 40, "tree": "f" * 40, "status_sha256": "0" * 64},
            ), mock.patch.object(
                VALIDATION, "validate_lane_runtime"
            ), mock.patch.object(VALIDATION, "long_lane", side_effect=fake_long), mock.patch.dict(
                os.environ, {"AI_CONTEXT_TEST_TMP_ROOT": str(Path(temporary) / "ram-root")}
            ):
                return_code, record = VALIDATION.execute_lane(
                    root=ROOT,
                    lane="long",
                    expected_commit="e" * 40,
                    output_dir=output,
                    trusted_reference=True,
                )

            self.assertEqual(0, return_code)
            self.assertTrue(record["execution"]["ai_context_test_tmp_root_present"])
            self.assertFalse(record["evidence"]["consumed_ai_context_test_tmp_root"])
            self.assertTrue(record["cleanup"]["work_root_removed"])

    def test_gwt_007_given_source_only_lane_runner_when_profile_is_projected_then_it_is_excluded_from_payload(self) -> None:
        profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        )
        source_only = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "repository-and-local-runtime-state"
        )

        self.assertIn(".ai/scripts/ai_context_v015_validation.py", source_only["patterns"])
        self.assertIn(".ai/scripts/run-v015-package-validation.py", source_only["patterns"])
        self.assertIn(".ai/scripts/run-v015-package-validation-wsl.py", source_only["patterns"])

    @unittest.skipUnless(os.name == "nt", "Windows read-only cleanup semantics")
    def test_gwt_008_given_readonly_git_fixture_bytes_when_cleaned_then_no_work_root_remains(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary) / "work"
            work.mkdir()
            readonly = work / "readonly.fixture"
            readonly.write_text("fixture\n", encoding="utf-8")
            readonly.chmod(0o444)

            VALIDATION.remove_tree(work)

            self.assertFalse(work.exists())

    def test_gwt_009_given_archive_member_bytes_when_evidence_is_canonicalized_then_only_digests_are_serialized(self) -> None:
        members = {
            "z.txt": (b"z\n", 0o644),
            "a.sh": (b"#!/bin/sh\n", 0o755),
        }
        canonical = [
            {"path": path, "sha256": VALIDATION.sha256_bytes(content), "mode": mode}
            for path, (content, mode) in sorted(
                members.items(), key=lambda item: item[0].encode("utf-8")
            )
        ]

        encoded = VALIDATION.canonical_json_bytes(canonical)

        self.assertNotIn(b"#!/bin/sh", encoded)
        self.assertEqual(["a.sh", "z.txt"], [item["path"] for item in canonical])

    def test_gwt_010_given_admitted_lane_when_interrupted_then_cleanup_and_nonpassing_terminal_are_retained(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "lane"
            output.mkdir()

            def interrupted(root: Path, commit: str, lane_output: Path, phases: dict) -> dict[str, object]:
                (lane_output / "work").mkdir()
                raise KeyboardInterrupt()

            with mock.patch.object(VALIDATION, "validate_output_root", return_value=output), mock.patch.object(
                VALIDATION,
                "validate_subject",
                return_value={"commit": "1" * 40, "tree": "2" * 40, "status_sha256": "3" * 64},
            ), mock.patch.object(
                VALIDATION, "validate_lane_runtime"
            ), mock.patch.object(VALIDATION, "medium_lane", side_effect=interrupted):
                return_code, record = VALIDATION.execute_lane(
                    root=ROOT,
                    lane="medium",
                    expected_commit="1" * 40,
                    output_dir=output,
                )

            self.assertEqual(1, return_code)
            self.assertEqual("failed", record["outcome"])
            self.assertEqual("execution-interrupted", record["evidence"]["reason_code"])
            self.assertTrue(record["cleanup"]["work_root_removed"])
            self.assertTrue((output / "terminal.json").is_file())

    def test_gwt_011_given_distinct_process_failures_when_fingerprinted_then_they_do_not_collapse(self) -> None:
        def diagnostic(stderr: str) -> dict[str, object]:
            encoded = stderr.encode("utf-8")
            return {
                "exit_code": 1,
                "stdout_sha256": VALIDATION.sha256_bytes(b""),
                "stdout_bytes": 0,
                "stderr_sha256": VALIDATION.sha256_bytes(encoded),
                "stderr_bytes": len(encoded),
                "stdout": "",
                "stderr": stderr,
            }

        first = VALIDATION.ValidationError(
            "long-upgrade-plan-failed",
            process_diagnostic=diagnostic("first planner failure"),
        )
        second = VALIDATION.ValidationError(
            "long-upgrade-plan-failed",
            process_diagnostic=diagnostic("second planner failure"),
        )

        self.assertNotEqual(
            VALIDATION.failure_details("long", "a" * 40, first)[2],
            VALIDATION.failure_details("long", "a" * 40, second)[2],
        )

    def test_gwt_012_given_process_failure_when_persisted_then_paths_are_redacted_and_bytes_are_digest_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "lane"
            private = f"{root.as_posix()}/private-input"
            stderr = f"AI context package apply failed: {private}; /home/operator/private\n"
            encoded = stderr.encode("utf-8")
            error = VALIDATION.ValidationError(
                "long-upgrade-plan-failed",
                process_diagnostic={
                    "exit_code": 1,
                    "stdout_sha256": VALIDATION.sha256_bytes(b""),
                    "stdout_bytes": 0,
                    "stderr_sha256": VALIDATION.sha256_bytes(encoded),
                    "stderr_bytes": len(encoded),
                    "stdout": "",
                    "stderr": stderr,
                },
            )

            evidence = VALIDATION.persist_failure_diagnostic(
                error,
                root=root,
                output=output,
                reason_code="long-upgrade-plan-failed",
            )

            self.assertIsNotNone(evidence)
            artifact = output / "artifacts/failure-diagnostic.json"
            content = artifact.read_text(encoding="utf-8")
            self.assertNotIn(str(root), content)
            self.assertNotIn("/home/operator", content)
            self.assertEqual(VALIDATION.sha256_file(artifact), evidence["sha256"])

    @unittest.skipIf(os.name == "nt", "POSIX archive mode semantics")
    def test_gwt_013_given_zip_executable_mode_when_extracted_then_mode_is_restored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "candidate.zip"
            info = zipfile.ZipInfo("payload/tool.sh")
            info.external_attr = 0o755 << 16
            with zipfile.ZipFile(archive, "w") as opened:
                opened.writestr(info, "#!/bin/sh\n")

            destination = root / "extracted"
            VALIDATION.extract_zip(archive, destination)

            self.assertEqual(0o755, stat.S_IMODE((destination / "payload/tool.sh").stat().st_mode))

    def test_gwt_014_given_exact_subject_when_synthetic_release_is_added_then_parent_tree_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
            (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
            (root / "ignored.txt").write_text("tracked despite ignore\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-f", ".gitignore", "ignored.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "subject"], check=True)
            expected_commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            work = Path(temporary) / "work"
            work.mkdir()
            synthetic, _ = VALIDATION.create_synthetic_source(
                root,
                expected_commit,
                work,
            )

            parent = subprocess.run(
                ["git", "-C", str(synthetic), "rev-parse", "HEAD^"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(expected_commit, parent)
            longpaths = subprocess.run(
                ["git", "-C", str(synthetic), "config", "--bool", "core.longpaths"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual("true", longpaths)

    def test_gwt_015_given_runtime_pin_mismatch_when_lane_starts_then_it_is_environment_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "lane"
            output.mkdir()
            with mock.patch.object(VALIDATION, "validate_output_root", return_value=output), mock.patch.object(
                VALIDATION,
                "validate_subject",
                return_value={"commit": "4" * 40, "tree": "5" * 40, "status_sha256": "6" * 64},
            ), mock.patch.object(
                VALIDATION.importlib_metadata, "version", return_value="6.0.1"
            ):
                return_code, record = VALIDATION.execute_lane(
                    root=ROOT,
                    lane="fast",
                    expected_commit="4" * 40,
                    output_dir=output,
                )

            self.assertEqual(1, return_code)
            self.assertEqual("blocked-by-environment", record["outcome"])
            self.assertEqual(
                "runtime-dependency-version-mismatch",
                record["evidence"]["reason_code"],
            )
            self.assertEqual("6.0.3", record["evidence"]["environment"]["expected_version"])
            self.assertEqual("6.0.1", record["evidence"]["environment"]["observed_version"])
            self.assertTrue((output / "terminal.json").is_file())


if __name__ == "__main__":
    unittest.main()
