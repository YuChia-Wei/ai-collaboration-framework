#!/usr/bin/env python3
"""Focused regression tests for external-task candidate custody receipts."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[6]
VALIDATOR_PATH = ROOT / ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py"
CONTEXT_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-ai-context.py"
PROFILE = ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
PACKET_FIXTURE = ROOT / ".ai/assets/skills/software-development-orchestrator/scripts/tests/fixtures/external-task-packet.yaml"
PACKET_REF = ".ai/assets/skills/software-development-orchestrator/scripts/tests/fixtures/external-task-packet.yaml"
SPEC = importlib.util.spec_from_file_location("external_task_delegation", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {VALIDATOR_PATH}")
DELEGATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DELEGATION)
CONTEXT_SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_for_delegation", CONTEXT_VALIDATOR_PATH
)
if CONTEXT_SPEC is None or CONTEXT_SPEC.loader is None:
    raise RuntimeError(f"Unable to load {CONTEXT_VALIDATOR_PATH}")
CONTEXT = importlib.util.module_from_spec(CONTEXT_SPEC)
CONTEXT_SPEC.loader.exec_module(CONTEXT)
SCHEMA = DELEGATION.load_mapping(DELEGATION.SCHEMA_PATH)
SHA = "5" * 40
ARTIFACT_ROOT = ".dev/ai-context/local/external-task/pr-195-hosted-gate-01"
DISPATCH_REF = f"{ARTIFACT_ROOT}/dispatch.yaml"
CANDIDATE_REF = f"{ARTIFACT_ROOT}/candidate.yaml"
RECEIPT_REF = f"{ARTIFACT_ROOT}/receipt.yaml"


def valid_dispatch() -> dict:
    return {
        "schema_version": "1.2", "record_type": "external-task-dispatch", "delegation_id": "pr-310-custody-01", "task_kind": "long-running-validation",
        "source": {"task_id_source": "runtime-injected", "task_id": None, "final_integration_owner": "source-task"},
        "objective": {"goal": "Run one exact command.", "non_goals": ["repair failures"]},
        "subject": {"repository_root": "C:/repo", "commit_sha": SHA, "clean_worktree_required": True},
        "execution": {"working_directory": "C:/repo", "argv": ["python", "focused-test.py", "-v"], "timeout_seconds": 300},
        "execution_packet": {"schema_ref": ".ai/assets/shared/agent-execution-guardrails.schema.yaml", "packet_ref": PACKET_REF, "packet_sha256": hashlib.sha256(PACKET_FIXTURE.read_bytes()).hexdigest(), "subject_sha": SHA, "validator_argv": ["python", ".ai/scripts/validate-agent-execution-guardrails.py", "--packet", PACKET_REF], "validation_outcome": "passed"},
        "permissions": {"read_scope": ["repository"], "write_scope": ["ignored-validation-artifacts"], "repair_allowed": False, "external_mutations": [], "secret_values": "prohibited"},
        "completion_delivery": {"primary": "source-task-callback", "fallback": "parent-event-wait", "destination": "source-task", "progress_updates": "terminal-only", "max_terminal_reports": 1, "report_schema": "same-contract#completion", "pre_send_validation": {"required": True, "receipt_writer_argv": DELEGATION.canonical_receipt_writer_argv(CANDIDATE_REF, DISPATCH_REF, RECEIPT_REF), "dispatch_ref": DISPATCH_REF, "candidate_ref": CANDIDATE_REF, "receipt_ref": RECEIPT_REF, "failure_action": "do-not-deliver-terminal-report", "payload_binding": "exact-candidate-bytes-with-independent-receipt"}},
        "stop_conditions": ["preflight mismatch", "terminal outcome"],
    }


def valid_candidate(outcome: str = "passed") -> dict:
    exit_code = 0 if outcome == "passed" else 1
    return {
        "schema_version": "1.2", "record_type": "external-task-completion", "delegation_id": "pr-310-custody-01", "source_task_id": "source-019f", "delegated_task_id": "worker-019f",
        "subject": {"expected_commit_sha": SHA, "observed_commit_sha": SHA},
        "preflight": {"commit_matches": True, "clean_worktree": True},
        "execution": {"working_directory": "C:/repo", "argv": ["python", "focused-test.py", "-v"]},
        "timing": {"started_at": "2026-09-20T01:00:00+08:00", "completed_at": "2026-09-20T01:00:02+08:00", "duration_seconds": 2},
        "result": {"outcome": outcome, "exit_code": exit_code, "counts": {"selected": 1, "failed": 0 if outcome == "passed" else 1}},
        "evidence": {"refs": ["runtime terminal"], "bounded_output": outcome},
        "final_state": {"clean_worktree": True, "tracked_changes": []},
        "delivery": {"mode": "source-task-callback", "destination": "source-task", "terminal_report_number": 1},
    }


class ExternalTaskDelegationContractTests(unittest.TestCase):
    def test_gwt_001_given_schema_1_2_when_loaded_then_candidate_and_receipt_are_separate(self) -> None:
        self.assertEqual([], DELEGATION.validate_schema_definition(SCHEMA))
        self.assertEqual("external-task-validation-receipt", SCHEMA["record_types"]["validation_receipt"])
        self.assertEqual("exact-candidate-bytes-with-independent-receipt", SCHEMA["transport_semantics"]["callback_payload"])

    def test_gwt_002_given_bootstrap_candidate_when_validated_then_it_never_self_asserts_validator_pass(self) -> None:
        candidate = valid_candidate()
        self.assertNotIn("schema_validation", candidate["delivery"])
        self.assertEqual([], DELEGATION.validate_completion(candidate, SCHEMA, valid_dispatch()))

    def test_gwt_002e_given_candidate_with_self_asserted_validation_then_it_is_rejected(self) -> None:
        candidate = valid_candidate()
        candidate["delivery"]["schema_validation"] = {"outcome": "passed", "exit_code": 0}
        errors = DELEGATION.validate_completion(candidate, SCHEMA, valid_dispatch())
        self.assertTrue(any("completion.delivery contains unsupported fields: schema_validation" in error for error in errors))

    def test_gwt_002a_given_one_marked_prompt_when_parsed_then_dispatch_is_valid(self) -> None:
        dispatch = valid_dispatch()
        prompt = (
            f"{DELEGATION.BEGIN_MARKER}\n"
            f"{yaml.safe_dump(dispatch, sort_keys=False)}"
            f"{DELEGATION.END_MARKER}\n"
        )
        self.assertEqual(dispatch, DELEGATION.extract_dispatch_from_prompt(prompt))
        self.assertEqual([], DELEGATION.validate_dispatch(dispatch, SCHEMA))

    def test_gwt_002b_given_duplicate_dispatch_envelope_then_it_fails_closed(self) -> None:
        message = (
            f"{DELEGATION.BEGIN_MARKER}\n{{}}\n{DELEGATION.END_MARKER}\n"
            f"{DELEGATION.BEGIN_MARKER}\n{{}}\n{DELEGATION.END_MARKER}\n"
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            DELEGATION.extract_dispatch_from_prompt(message)

    def test_gwt_002c_given_delivery_destination_or_limit_drift_then_dispatch_is_rejected(self) -> None:
        dispatch = valid_dispatch()
        dispatch["completion_delivery"]["destination"] = "delegated-task"
        dispatch["completion_delivery"]["max_terminal_reports"] = 2
        errors = DELEGATION.validate_dispatch(dispatch, SCHEMA)
        self.assertTrue(any("completion_delivery is invalid" in error for error in errors))

    def test_gwt_002d_given_event_wait_delivery_then_dispatch_remains_valid(self) -> None:
        dispatch = valid_dispatch()
        dispatch["completion_delivery"].update(
            primary="parent-event-wait", fallback="single-terminal-readback"
        )
        self.assertEqual([], DELEGATION.validate_dispatch(dispatch, SCHEMA))

    def test_gwt_002f_given_unsafe_or_unbound_pre_send_refs_then_dispatch_is_rejected(self) -> None:
        dispatch = valid_dispatch()
        pre_send = dispatch["completion_delivery"]["pre_send_validation"]
        pre_send["receipt_ref"] = "README.md"
        pre_send["receipt_writer_argv"] = DELEGATION.canonical_receipt_writer_argv(
            CANDIDATE_REF, DISPATCH_REF, "README.md"
        )
        errors = DELEGATION.validate_dispatch(dispatch, SCHEMA)
        self.assertTrue(any("receipt_ref must be actually ignored and untracked" in error for error in errors))
        self.assertTrue(any("receipt_ref must be beneath a declared ignored artifact root" in error for error in errors))

        dispatch = valid_dispatch()
        pre_send = dispatch["completion_delivery"]["pre_send_validation"]
        pre_send["candidate_ref"] = ".dev/ai-context/local/external-task/other/candidate.yaml"
        pre_send["receipt_writer_argv"] = DELEGATION.canonical_receipt_writer_argv(
            pre_send["candidate_ref"], DISPATCH_REF, RECEIPT_REF
        )
        errors = DELEGATION.validate_dispatch(dispatch, SCHEMA)
        self.assertTrue(any("candidate_ref must be beneath a declared ignored artifact root" in error for error in errors))

    def test_gwt_002g_given_writer_argv_does_not_bind_declared_refs_then_dispatch_is_rejected(self) -> None:
        dispatch = valid_dispatch()
        dispatch["completion_delivery"]["pre_send_validation"]["receipt_writer_argv"][-1] = CANDIDATE_REF
        errors = DELEGATION.validate_dispatch(dispatch, SCHEMA)
        self.assertTrue(any("receipt_writer_argv must exactly bind" in error for error in errors))

    def test_gwt_002h_given_receipt_write_args_drift_from_safe_refs_then_writing_is_rejected(self) -> None:
        dispatch = valid_dispatch()
        self.assertEqual(
            [],
            DELEGATION.validate_receipt_write_request(
                Path(CANDIDATE_REF), Path(DISPATCH_REF), Path(RECEIPT_REF), dispatch
            ),
        )
        errors = DELEGATION.validate_receipt_write_request(
            Path(CANDIDATE_REF), Path(DISPATCH_REF), ROOT / RECEIPT_REF, dispatch
        )
        self.assertTrue(any("--write-receipt path must exactly match" in error for error in errors))
        errors = DELEGATION.validate_receipt_write_request(
            Path("README.md"), Path("README.md"), Path(RECEIPT_REF), dispatch
        )
        self.assertTrue(any("--candidate path must exactly match" in error for error in errors))
        self.assertTrue(any("--dispatch path must exactly match" in error for error in errors))

    def test_gwt_002i_given_receipt_output_exists_then_it_is_not_overwritten(self) -> None:
        dispatch = valid_dispatch()
        with mock.patch.object(Path, "exists", return_value=True):
            errors = DELEGATION.validate_receipt_write_request(
                Path(CANDIDATE_REF), Path(DISPATCH_REF), Path(RECEIPT_REF), dispatch
            )
        self.assertEqual(["receipt writing refuses to overwrite a pre-existing output"], errors)

    def test_gwt_003_given_exact_candidate_bytes_when_receipt_is_issued_then_custody_releases(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate()
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(candidate, dispatch, CANDIDATE_REF, candidate_bytes, DISPATCH_REF, dispatch_bytes, RECEIPT_REF)
        self.assertEqual([], DELEGATION.validate_receipt(receipt, SCHEMA, candidate, candidate_bytes, dispatch, dispatch_bytes))
        self.assertEqual("released", receipt["custody"]["state"])

    def test_gwt_004_given_post_validation_candidate_mutation_when_receipt_checked_then_it_is_rejected(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate()
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(candidate, dispatch, CANDIDATE_REF, candidate_bytes, DISPATCH_REF, dispatch_bytes, RECEIPT_REF)
        mutated = copy.deepcopy(candidate); mutated["evidence"]["bounded_output"] = "changed after validation"
        mutated_bytes = yaml.safe_dump(mutated, sort_keys=False).encode()
        errors = DELEGATION.validate_receipt(receipt, SCHEMA, mutated, mutated_bytes, dispatch, dispatch_bytes)
        self.assertTrue(any("candidate.sha256 does not match exact candidate bytes" in error for error in errors))

    def test_gwt_004a_given_receipt_ref_or_writer_argv_drift_then_it_is_rejected(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate()
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(
            candidate, dispatch, CANDIDATE_REF, candidate_bytes,
            DISPATCH_REF, dispatch_bytes, RECEIPT_REF,
        )
        receipt["candidate"]["ref"] = ".external-task/other-candidate.yaml"
        receipt["dispatch"]["ref"] = ".external-task/other-dispatch.yaml"
        receipt["receipt_ref"] = ".external-task/other-receipt.yaml"
        receipt["validator"]["argv"] = ["python", "other-validator.py"]
        errors = DELEGATION.validate_receipt(
            receipt, SCHEMA, candidate, candidate_bytes, dispatch, dispatch_bytes
        )
        self.assertTrue(any("candidate.ref must match" in error for error in errors))
        self.assertTrue(any("dispatch.ref must match" in error for error in errors))
        self.assertTrue(any("receipt_ref must match" in error for error in errors))
        self.assertTrue(any("validator.argv must match" in error for error in errors))

    def test_gwt_004b_given_combined_terminal_delivery_then_receipt_is_required(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate()
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(
            candidate, dispatch, CANDIDATE_REF, candidate_bytes,
            DISPATCH_REF, dispatch_bytes, RECEIPT_REF,
        )
        message = (
            f"{DELEGATION.COMPLETION_BEGIN_MARKER}\n"
            f"{candidate_bytes.decode()}"
            f"{DELEGATION.COMPLETION_END_MARKER}\n"
            f"{DELEGATION.RECEIPT_BEGIN_MARKER}\n"
            f"{yaml.safe_dump(receipt, sort_keys=False)}"
            f"{DELEGATION.RECEIPT_END_MARKER}\n"
        )
        self.assertEqual(
            [], DELEGATION.validate_terminal_delivery_message(
                message, SCHEMA, dispatch, dispatch_bytes
            )
        )
        missing_receipt = message.split(DELEGATION.RECEIPT_BEGIN_MARKER, 1)[0]
        errors = DELEGATION.validate_terminal_delivery_message(
            missing_receipt, SCHEMA, dispatch, dispatch_bytes
        )
        self.assertTrue(errors)

    def test_gwt_004c_given_terminal_receipt_for_other_candidate_then_delivery_is_rejected(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate()
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(
            candidate, dispatch, CANDIDATE_REF, candidate_bytes,
            DISPATCH_REF, dispatch_bytes, RECEIPT_REF,
        )
        receipt["candidate"]["sha256"] = "f" * 64
        message = (
            f"{DELEGATION.COMPLETION_BEGIN_MARKER}\n{candidate_bytes.decode()}"
            f"{DELEGATION.COMPLETION_END_MARKER}\n"
            f"{DELEGATION.RECEIPT_BEGIN_MARKER}\n"
            f"{yaml.safe_dump(receipt, sort_keys=False)}"
            f"{DELEGATION.RECEIPT_END_MARKER}\n"
        )
        errors = DELEGATION.validate_terminal_delivery_message(
            message, SCHEMA, dispatch, dispatch_bytes
        )
        self.assertTrue(any("candidate.sha256" in error for error in errors))

    def test_gwt_005_given_blocked_terminal_candidate_when_receipt_is_issued_then_delivery_is_released_without_passing_execution(self) -> None:
        dispatch, candidate = valid_dispatch(), valid_candidate("blocked-by-environment")
        dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
        candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
        receipt = DELEGATION.build_validation_receipt(candidate, dispatch, CANDIDATE_REF, candidate_bytes, DISPATCH_REF, dispatch_bytes, RECEIPT_REF)
        self.assertEqual([], DELEGATION.validate_receipt(receipt, SCHEMA, candidate, candidate_bytes, dispatch, dispatch_bytes))
        self.assertEqual("blocked-by-environment", candidate["result"]["outcome"])
        self.assertEqual("released", receipt["custody"]["state"])

    def test_gwt_006_given_failed_or_interrupted_terminal_candidate_when_receipt_is_issued_then_delivery_is_released(self) -> None:
        for outcome in ("failed", "timed-out", "interrupted"):
            with self.subTest(outcome=outcome):
                dispatch, candidate = valid_dispatch(), valid_candidate(outcome)
                dispatch_bytes = yaml.safe_dump(dispatch, sort_keys=False).encode()
                candidate_bytes = yaml.safe_dump(candidate, sort_keys=False).encode()
                receipt = DELEGATION.build_validation_receipt(candidate, dispatch, CANDIDATE_REF, candidate_bytes, DISPATCH_REF, dispatch_bytes, RECEIPT_REF)
                self.assertEqual([], DELEGATION.validate_receipt(receipt, SCHEMA, candidate, candidate_bytes, dispatch, dispatch_bytes))

    def test_gwt_007_given_passed_candidate_subject_or_worktree_drift_then_it_is_rejected(self) -> None:
        candidate = valid_candidate()
        candidate["subject"]["observed_commit_sha"] = "6" * 40
        candidate["final_state"] = {"clean_worktree": False, "tracked_changes": ["tracked.txt"]}
        errors = DELEGATION.validate_completion(candidate, SCHEMA, valid_dispatch())
        self.assertTrue(any("matching expected and observed" in error for error in errors))
        self.assertTrue(any("clean final worktree" in error for error in errors))

    def test_gwt_008_given_execution_packet_drift_or_missing_then_dispatch_is_rejected(self) -> None:
        missing = valid_dispatch()
        del missing["execution_packet"]
        self.assertTrue(any("execution_packet is required" in error for error in DELEGATION.validate_dispatch(missing, SCHEMA)))
        drifted = valid_dispatch()
        drifted["execution_packet"]["packet_sha256"] = "f" * 64
        self.assertTrue(any("does not match packet file bytes" in error for error in DELEGATION.validate_dispatch(drifted, SCHEMA)))

    def test_gwt_009_given_profile_without_delegation_binding_then_capability_validation_rejects_it(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        del profile["capability_contracts"]["test-execution"]["long_running"]["delegation_contract"]
        skills = {skill_id: {"status": "active", "capability_slots": [slot]} for slot, skill_id in profile["mappings"].items()}
        errors: list[str] = []
        with mock.patch.object(CONTEXT, "load_yaml_mapping", return_value=profile):
            CONTEXT.validate_capability_profile(skills, errors)
        self.assertTrue(any("test-execution.long_running" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
