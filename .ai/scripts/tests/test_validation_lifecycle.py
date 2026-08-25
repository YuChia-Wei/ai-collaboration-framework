#!/usr/bin/env python3
"""GWT coverage for validation freeze and content-addressed reuse."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/validate-validation-lifecycle.py"
SPEC = importlib.util.spec_from_file_location("validation_lifecycle", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("validator cannot be loaded")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
SCHEMA = yaml.safe_load((ROOT / ".ai/assets/shared/validation-evidence-lifecycle.schema.yaml").read_text(encoding="utf-8"))
PROVIDER = yaml.safe_load((ROOT / ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml").read_text(encoding="utf-8"))
D = "a" * 64
SHA1 = "1" * 40
SHA2 = "2" * 40


def pair(value: str = D) -> dict[str, str]:
    return {"original": value, "current": value}


def receipt(evidence_class: str = "input-sensitive", profile: str = "fast") -> dict[str, object]:
    dependency_paths = [".ai/scripts/tests/test_example.py"]
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "validation-reuse-receipt",
        "evidence_class": evidence_class,
        "subject": {"original_sha": SHA1, "current_sha": SHA2},
        "invocation": {"argv": ["python", "tests.py", "-v"], "working_directory": ".", "profile": profile},
        "original_result": {"outcome": "passed", "duration_seconds": 12.5, "evidence_refs": ["ignored:sealed/result.json"], "evidence_sha256": D},
        "dependencies": [{"path": ".ai/scripts/tests/test_example.py", "original_blob": D, "current_blob": D}],
        "dependency_closure": {
            "resolver_argv": ["bash", ".ai/scripts/check-all.sh", "--resolve-input-closure", "focused"],
            "complete": True,
            "unknown_paths": [],
            "path_count": len(dependency_paths),
            "original_paths_sha256": VALIDATOR.canonical_digest(dependency_paths),
            "current_paths_sha256": VALIDATOR.canonical_digest(dependency_paths),
        },
        "terminal_metadata": {"original_sha256": D, "current_sha256": D, "excluded_from_dependency_fingerprint": True},
        "authority": {name: pair() for name in SCHEMA["reuse_receipt"]["authority_dimensions"]},
        "command_fingerprint": pair(),
        "profile_fingerprint": pair(),
        "environment": {"original": {"class": "windows-native", "condition": "warm"}, "current": {"class": "windows-native", "condition": "warm"}},
        "fresh_gates": [{"gate": gate, "required": True, "replaceable_by_reuse": False} for gate in SCHEMA["reuse_receipt"]["required_fresh_gates"]],
        "decision": {"outcome": "reused-with-proof", "reason": "complete-byte-equivalence"},
    }
    value["receipt_sha256"] = VALIDATOR.canonical_digest(value)
    return value


def seal(value: dict[str, object], field: str) -> None:
    value[field] = VALIDATOR.canonical_digest({key: item for key, item in value.items() if key != field})


class ValidationLifecycleGwtTests(unittest.TestCase):
    def test_gwt_001_given_complete_input_closure_when_reuse_is_checked_then_it_passes(self) -> None:
        VALIDATOR.validate_reuse_receipt(receipt(), SCHEMA)

    def test_gwt_002_given_terminal_metadata_only_scenario_when_inputs_match_then_behavioral_reuse_remains_proven(self) -> None:
        value = receipt()
        value["terminal_metadata"]["current_sha256"] = "b" * 64
        self.assertNotIn(".dev/workflows/2026-08-24-perf-001/terminal-summary.yaml", [item["path"] for item in value["dependencies"]])
        seal(value, "receipt_sha256")
        VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_003_given_runtime_manifest_runner_policy_resolver_or_configuration_drift_when_checked_then_reexecution_is_required(self) -> None:
        for dimension in SCHEMA["reuse_receipt"]["authority_dimensions"]:
            with self.subTest(dimension=dimension):
                value = receipt()
                value["authority"][dimension]["current"] = "b" * 64
                value["decision"] = {"outcome": "re-executed", "reason": f"{dimension}-drift"}
                seal(value, "receipt_sha256")
                VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_004_given_unknown_dependency_when_checked_then_it_is_blocked_fail_closed(self) -> None:
        value = receipt()
        value["dependencies"] = []
        value["dependency_closure"]["complete"] = False
        value["dependency_closure"]["unknown_paths"] = ["unresolved-import"]
        value["decision"] = {"outcome": "blocked", "reason": "dependency-closure-unknown"}
        seal(value, "receipt_sha256")
        VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_005_given_unknown_dependency_claims_reuse_when_checked_then_it_fails(self) -> None:
        value = receipt()
        value["dependencies"] = []
        value["dependency_closure"]["complete"] = False
        value["dependency_closure"]["unknown_paths"] = ["unresolved-import"]
        seal(value, "receipt_sha256")
        with self.assertRaisesRegex(VALIDATOR.LifecycleError, "fail closed as blocked"):
            VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_006_given_environment_sensitive_evidence_when_environment_drifts_then_reexecution_is_required(self) -> None:
        value = receipt("environment-sensitive")
        value["environment"]["current"] = {"class": "linux-hosted", "condition": "cold"}
        value["decision"] = {"outcome": "re-executed", "reason": "environment-drift"}
        seal(value, "receipt_sha256")
        VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_006b_given_input_sensitive_evidence_when_environment_drifts_then_reexecution_is_required(self) -> None:
        value = receipt("input-sensitive")
        value["environment"]["current"] = {"class": "linux-hosted", "condition": "cold"}
        value["decision"] = {"outcome": "re-executed", "reason": "environment-drift"}
        seal(value, "receipt_sha256")
        VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_006c_given_partial_dependency_subset_when_claimed_complete_then_it_fails_closed(self) -> None:
        value = receipt()
        value["dependency_closure"]["path_count"] = 2
        value["decision"] = {"outcome": "blocked", "reason": "dependency-closure-unknown"}
        seal(value, "receipt_sha256")
        VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_007_given_identity_or_provider_evidence_when_reuse_is_claimed_then_it_fails(self) -> None:
        for evidence_class in ("identity-sensitive", "provider-sensitive"):
            with self.subTest(evidence_class=evidence_class):
                value = receipt(evidence_class)
                seal(value, "receipt_sha256")
                with self.assertRaisesRegex(VALIDATOR.LifecycleError, "re-executed"):
                    VALIDATOR.validate_reuse_receipt(value, SCHEMA)

    def test_gwt_008_given_active_freeze_when_tracked_mutation_appears_then_it_fails(self) -> None:
        value: dict[str, object] = {
            "schema_version": "1.0", "record_type": "validation-freeze", "state": "active",
            "subject_sha": SHA1, "clean_subject": True, "anticipated_tracked_mutations_complete": True,
            "terminal_declarations_before_freeze": True, "workflow_closeout_before_freeze": True,
            "tracked_mutations_after_freeze": [], "ignored_validation_artifacts_only": True,
            "identity_evidence_stale": False, "post_merge_source_repair_required": False,
        }
        seal(value, "record_sha256")
        VALIDATOR.validate_freeze(value)
        drift = copy.deepcopy(value)
        drift["tracked_mutations_after_freeze"] = ["tracked-report.md"]
        seal(drift, "record_sha256")
        with self.assertRaisesRegex(VALIDATOR.LifecycleError, "tracked drift"):
            VALIDATOR.validate_freeze(drift)

    def test_gwt_009_given_exact_head_audit_when_reuse_is_reported_then_proof_is_mandatory(self) -> None:
        audit = {"schema_version": "1.0", "record_type": "exact-head-validation-audit", "subject_sha": SHA2, "gates": [
            {"gate_id": "focused-tests", "disposition": "re-executed", "evidence_refs": ["ignored:focused.log"], "reuse_receipt_sha256": None},
            {"gate_id": "benchmark", "disposition": "reused-with-proof", "evidence_refs": ["ignored:reuse.json"], "reuse_receipt_sha256": D},
            {"gate_id": "linux-only", "disposition": "not-applicable", "evidence_refs": [], "reuse_receipt_sha256": None},
        ]}
        VALIDATOR.validate_audit(audit, SCHEMA)
        audit["gates"][1]["reuse_receipt_sha256"] = None
        with self.assertRaisesRegex(VALIDATOR.LifecycleError, "SHA-256"):
            VALIDATOR.validate_audit(audit, SCHEMA)

    def test_gwt_010_given_provider_required_contexts_when_one_is_path_filtered_away_then_it_fails(self) -> None:
        names = PROVIDER["work_item_binding"]["merge_gate"]["required_check_contexts"]
        record = {"schema_version": "1.0", "record_type": "hosted-required-contexts", "head_sha": SHA2, "contexts": [
            {"name": name, "outcome": "success", "executed": 1, "reused": 0, "reuse_provenance": []} for name in names
        ]}
        VALIDATOR.validate_required_contexts(record, PROVIDER, SCHEMA)
        record["contexts"].pop()
        with self.assertRaisesRegex(VALIDATOR.LifecycleError, "missing"):
            VALIDATOR.validate_required_contexts(record, PROVIDER, SCHEMA)


if __name__ == "__main__":
    unittest.main()
