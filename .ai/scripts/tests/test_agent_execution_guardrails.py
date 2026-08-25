#!/usr/bin/env python3
"""GWT coverage for agent execution packets, leases, evidence, retry, and discovery."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/validate-agent-execution-guardrails.py"
SPEC = importlib.util.spec_from_file_location("agent_guardrails", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("validator cannot be loaded")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
SCHEMA = yaml.safe_load((ROOT / ".ai/assets/shared/agent-execution-guardrails.schema.yaml").read_text(encoding="utf-8"))
SHA = "1" * 40
D = "a" * 64


def seal(value: dict[str, object], field: str) -> dict[str, object]:
    value[field] = VALIDATOR.digest({key: item for key, item in value.items() if key != field})
    return value


def packet(kind: str = "delegated") -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "agent-execution-packet",
        "packet_id": "GOV014-PACKET-001",
        "execution_kind": kind,
        "owning_skill": "ai-context-governance",
        "role": {"path": ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml", "applicability": "applies", "reason": "Exact-head governance audit applies."},
        "subject": {"repository": "ai-collaboration-framework", "exact_sha": SHA},
        "invocation": {"argv": ["python", ".ai/scripts/check.py", "-v"], "cwd": "."},
        "permissions": {"network": "deny", "tracked_write": "deny", "provider_mutation": "deny"},
        "ignored_artifact_roots": [".dev/ai-context/local/validation/GOV014-PACKET-001"],
        "terminal": {"schema_ref": ".ai/assets/shared/external-terminal.schema.yaml", "mode": "event-wait", "destination": "parent-thread", "max_terminal_messages": 1},
        "integration_owner": "parent-orchestrator",
        "stop_conditions": ["subject drift", "permission expansion", "missing evidence"],
        "retry": {"attempt": 1, "budget": 2, "authorization_refs": []},
    }
    return seal(value, "packet_sha256")


def lease(state: str = "active") -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "worktree-snapshot-lease",
        "lease_id": "GOV014-LEASE-001",
        "worktree": ".dev/ai-context/local/worktrees/issue-249-253",
        "subject_sha": SHA,
        "snapshot_sha256": D,
        "state": state,
        "holder": {"packet_id": "GOV014-PACKET-001", "access": "tracked-writer"},
        "observed_other_tracked_writers": [],
        "ignored_artifacts": [{"path": ".dev/ai-context/local/validation/GOV014-PACKET-001/result.json", "state": "open" if state == "active" else "sealed", "sha256": None if state == "active" else D}],
        "tracked_mutations": [],
        "terminal_release": {"released": state == "released", "reason": "active holder" if state == "active" else "clean release"},
    }
    return seal(value, "lease_sha256")


def ledger() -> dict[str, object]:
    entries = [
        {"acceptance_id": "GOV014-AC-01", "issue": 253, "requires_actual_execution": True, "evidence_kind": "actual-execution", "command": "python test.py -v", "profile": "focused", "subject_sha": SHA, "outcome": "passed", "evidence_refs": ["ignored:validation/result.json"], "evidence_sha256": D},
        {"acceptance_id": "GOV013-AC-02", "issue": 249, "requires_actual_execution": False, "evidence_kind": "unit", "command": "python unit.py -v", "profile": "focused", "subject_sha": SHA, "outcome": "passed", "evidence_refs": ["fixture:unit-negative"], "evidence_sha256": "b" * 64},
    ]
    report_entries = [{"acceptance_id": item["acceptance_id"], "outcome": item["outcome"], "evidence_sha256": item["evidence_sha256"]} for item in entries]
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "acceptance-evidence-ledger",
        "subject_sha": SHA,
        "entries": entries,
        "human_report": {"entries": report_entries, "report_sha256": VALIDATOR.digest(report_entries)},
    }
    return seal(value, "ledger_sha256")


def retry(attempt: int = 2, decision: str = "retry") -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "agent-retry-decision",
        "attempt": attempt,
        "failure": {"failure_class": "validator-failure", "command_sha256": D, "subject_sha": SHA, "environment_class": "windows-native", "diagnostic_codes": ["EXIT-1"]},
        "prior_failure_sha256": D,
        "material_state_change_sha256": "b" * 64,
        "new_authorization_refs": ["workflow:fresh-retry-authorization"] if attempt >= 3 else [],
        "decision": decision,
    }
    return seal(value, "retry_sha256")


def graph(state: str = "fresh", coverage: str = "complete") -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "1.0",
        "record_type": "code-graph-freshness",
        "project": "issue-249-253",
        "head_sha": SHA,
        "indexed_sha": SHA if state == "fresh" else None,
        "index_state": state,
        "coverage": coverage,
        "reindex_attempted": state != "fresh",
        "fallback": "none",
        "fallback_paths": [],
        "absence_claim": True,
    }
    return seal(value, "freshness_sha256")


class AgentExecutionGuardrailsGwtTests(unittest.TestCase):
    def test_gwt_001_given_complete_fixed_head_packet_when_validated_then_it_passes(self) -> None:
        VALIDATOR.validate_packet(packet("fixed-head-audit"), SCHEMA)

    def test_gwt_002_given_external_packet_with_tracked_write_when_validated_then_it_fails(self) -> None:
        value = packet("external")
        value["permissions"]["tracked_write"] = "allow"
        seal(value, "packet_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "read-only"):
            VALIDATOR.validate_packet(value, SCHEMA)

    def test_gwt_003_given_attempt_three_without_fresh_authorization_when_packet_is_validated_then_it_fails(self) -> None:
        value = packet()
        value["retry"] = {"attempt": 3, "budget": 3, "authorization_refs": []}
        seal(value, "packet_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "attempt 3"):
            VALIDATOR.validate_packet(value, SCHEMA)

    def test_gwt_004_given_active_writer_lease_when_another_writer_appears_then_it_fails(self) -> None:
        value = lease()
        value["observed_other_tracked_writers"] = ["GOV014-PACKET-OTHER"]
        seal(value, "lease_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "another tracked writer"):
            VALIDATOR.validate_lease(value, SCHEMA)

    def test_gwt_005_given_released_lease_when_ignored_output_is_sealed_then_it_passes(self) -> None:
        VALIDATOR.validate_lease(lease("released"), SCHEMA)

    def test_gwt_006_given_actual_acceptance_and_human_projection_when_bound_then_they_pass(self) -> None:
        VALIDATOR.validate_evidence(ledger(), SCHEMA)

    def test_gwt_007_given_synthetic_evidence_for_actual_acceptance_when_validated_then_it_fails(self) -> None:
        value = ledger()
        value["entries"][0]["evidence_kind"] = "synthetic-test"
        seal(value, "ledger_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "cannot satisfy actual execution"):
            VALIDATOR.validate_evidence(value, SCHEMA)

    def test_gwt_008_given_human_report_digest_drifts_when_compared_then_it_fails(self) -> None:
        value = ledger()
        value["human_report"]["entries"][0]["outcome"] = "failed"
        value["human_report"]["report_sha256"] = VALIDATOR.digest(value["human_report"]["entries"])
        seal(value, "ledger_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "does not match"):
            VALIDATOR.validate_evidence(value, SCHEMA)

    def test_gwt_009_given_unchanged_failure_when_retry_is_requested_then_it_fails(self) -> None:
        value = retry()
        value["material_state_change_sha256"] = None
        seal(value, "retry_sha256")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "material state change"):
            VALIDATOR.validate_retry(value, SCHEMA)

    def test_gwt_010_given_attempt_three_with_fresh_authorization_when_retry_is_validated_then_it_passes(self) -> None:
        VALIDATOR.validate_retry(retry(3), SCHEMA)

    def test_gwt_011_given_stale_graph_without_tracked_fallback_when_absence_is_claimed_then_it_fails(self) -> None:
        value = graph("stale", "partial")
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "search absence"):
            VALIDATOR.validate_graph(value, SCHEMA)

    def test_gwt_012_given_stale_graph_with_tracked_fallback_when_absence_is_claimed_then_it_passes(self) -> None:
        value = graph("stale", "partial")
        value["fallback"] = "tracked-search"
        value["fallback_paths"] = [".ai/scripts", ".ai/assets/shared"]
        seal(value, "freshness_sha256")
        VALIDATOR.validate_graph(value, SCHEMA)

    def test_gwt_013_given_powershell_host_assignment_when_scanned_then_it_fails_case_insensitively(self) -> None:
        with self.assertRaisesRegex(VALIDATOR.GuardrailError, "reserved automatic variable"):
            VALIDATOR.validate_powershell_source("$HOST = 'runner'\n", SCHEMA)

    def test_gwt_014_given_purpose_specific_powershell_variable_when_scanned_then_it_passes(self) -> None:
        VALIDATOR.validate_powershell_source("$taskHost = 'runner'\n$processIdentifier = 42\n", SCHEMA)


if __name__ == "__main__":
    unittest.main()
