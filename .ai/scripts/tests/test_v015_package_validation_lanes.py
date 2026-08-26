#!/usr/bin/env python3
"""GWT contracts for the independent v0.15 package validation lanes."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
