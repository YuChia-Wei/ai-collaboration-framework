#!/usr/bin/env python3
"""GWT tests for prospective workflow lifecycle consistency."""

from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-workflow-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_workflow_lifecycle", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def task(status: str, summary: str = "done", finding_status: str = "resolved") -> dict:
    return {
        "status": status,
        "results": {"summary": summary, "finding_status": finding_status},
    }


def identified_task(task_id: str, status: str) -> dict:
    value = task(status)
    value["task_id"] = task_id
    return value


class WorkflowLifecycleContractTests(unittest.TestCase):
    def validate(self, status: str, phase: str, tasks: list[tuple[str, dict]]) -> list[str]:
        errors: list[str] = []
        locator = {
            "lifecycle_contract": "1.0",
            "status": status,
            "current_phase": phase,
        }
        VALIDATOR.validate_lifecycle_contract(locator, tasks, "workflow.yaml", errors)
        return errors

    def test_gwt_001_given_one_active_task_when_workflow_in_progress_then_passes(self) -> None:
        self.assertEqual([], self.validate("in_progress", "implementation", [("T1", task("in_progress"))]))

    def test_gwt_002_given_no_active_task_when_workflow_in_progress_then_fails(self) -> None:
        errors = self.validate("in_progress", "implementation", [("T1", task("pending"))])
        self.assertTrue(any("exactly one in_progress task" in error for error in errors))

    def test_gwt_003_given_unfinished_task_when_workflow_completed_then_fails(self) -> None:
        errors = self.validate("completed", "completed", [("T1", task("pending"))])
        self.assertTrue(any("completed workflow has unfinished tasks" in error for error in errors))

    def test_gwt_004_given_completed_workflow_with_open_phase_then_fails(self) -> None:
        errors = self.validate("completed", "verification", [("T1", task("completed"))])
        self.assertTrue(any("current_phase must be completed or closed" in error for error in errors))

    def test_gwt_005_given_completed_task_without_result_then_fails(self) -> None:
        errors = self.validate("completed", "completed", [("T1", task("completed", summary=""))])
        self.assertTrue(any("non-empty results.summary" in error for error in errors))

    def test_gwt_006_given_legacy_locator_without_contract_when_validated_then_is_compatible(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_lifecycle_contract(
            {"status": "completed", "current_phase": "legacy"},
            [("T1", task("pending"))],
            "legacy/workflow.yaml",
            errors,
        )
        self.assertEqual([], errors)

    def test_gwt_007_given_new_task_without_model_when_validated_then_fails(self) -> None:
        errors: list[str] = []
        value = {"status": "pending"}
        observed = datetime.fromisoformat("2026-07-27T10:00:00+08:00")
        VALIDATOR.validate_task_execution_provenance(
            value, "task.json", errors, observed, observed
        )
        self.assertTrue(any("model must be a non-empty string" in error for error in errors))
        self.assertTrue(any("reasoning_effort must be a non-empty string" in error for error in errors))

    def test_gwt_008_given_historical_active_task_updated_after_policy_when_missing_provenance_then_fails(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_task_execution_provenance(
            {"status": "in_progress"},
            "task.json",
            errors,
            datetime.fromisoformat("2026-07-20T10:00:00+08:00"),
            datetime.fromisoformat("2026-07-27T10:00:00+08:00"),
        )
        self.assertTrue(errors)

    def test_gwt_009_given_completed_historical_task_when_updated_after_policy_then_no_backfill_is_required(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_task_execution_provenance(
            {"status": "completed"},
            "task.json",
            errors,
            datetime.fromisoformat("2026-07-20T10:00:00+08:00"),
            datetime.fromisoformat("2026-07-27T10:00:00+08:00"),
        )
        self.assertEqual([], errors)

    def test_gwt_010_given_provider_original_values_when_validated_then_passes(self) -> None:
        errors: list[str] = []
        observed = datetime.fromisoformat("2026-07-27T10:00:00+08:00")
        VALIDATOR.validate_task_execution_provenance(
            {
                "status": "in_progress",
                "model": "claude-sonnet-5",
                "reasoning_effort": "extended thinking",
            },
            "task.json",
            errors,
            observed,
            observed,
        )
        self.assertEqual([], errors)

    def test_gwt_011_given_nested_development_locator_when_parsed_then_continuation_is_a_mapping(self) -> None:
        path = (
            REPO_ROOT
            / ".ai/assets/skills/software-development-orchestrator/templates/workflow-locator-template.yaml"
        )
        errors: list[str] = []
        locator = VALIDATOR.parse_yaml_mapping(path, "workflow-locator-template.yaml", errors)

        self.assertEqual([], errors)
        self.assertIsInstance(locator, dict)
        self.assertEqual("<current-task-id>", locator["continuation"]["current_task_id"])

    def validate_terminal_anchor(
        self,
        *,
        workflow_status: str,
        task_status: str,
        on_satisfied: str,
        continuation: dict | None = None,
        observed_state: str = "satisfied",
    ) -> list[str]:
        if observed_state != "satisfied":
            raise ValueError("The tracked fixture represents only the satisfied state.")
        evidence_ref = (
            ".ai/scripts/tests/fixtures/workflow-terminal-anchors/satisfied.yaml"
        )
        anchor = {
            "anchor_id": "hosted-publication",
            "anchor_kind": "external-lifecycle-evidence",
            "evidence_ref": evidence_ref,
            "on_satisfied": on_satisfied,
        }
        if continuation is not None:
            anchor["continuation"] = continuation
        locator = {
            "workflow_id": "synthetic-release-workflow",
            "status": workflow_status,
            "terminal_anchor_contract": {
                "schema_version": "1.0",
                "anchors": [anchor],
            },
        }
        errors: list[str] = []
        VALIDATOR.validate_terminal_anchor_contract(
            locator,
            [("tasks/REL-001.json", identified_task("REL-001", task_status))],
            "synthetic/workflow.yaml",
            errors,
            repo=REPO_ROOT,
        )
        return errors

    def test_gwt_012_given_satisfied_terminal_anchor_when_workflow_and_task_active_then_names_conflicts(self) -> None:
        errors = self.validate_terminal_anchor(
            workflow_status="in_progress",
            task_status="in_progress",
            on_satisfied="complete",
        )

        self.assertTrue(
            any(
                "synthetic-release-workflow" in error
                and "hosted-publication" in error
                and "workflow state 'in_progress'" in error
                for error in errors
            )
        )
        self.assertTrue(
            any(
                "REL-001" in error and "task 'REL-001' state 'in_progress'" in error
                for error in errors
            )
        )

    def test_gwt_013_given_satisfied_terminal_anchor_when_workflow_and_task_completed_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_terminal_anchor(
                workflow_status="completed",
                task_status="completed",
                on_satisfied="complete",
            ),
        )

    def test_gwt_014_given_active_postpublication_remediation_when_continuation_is_explicit_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_terminal_anchor(
                workflow_status="in_progress",
                task_status="in_progress",
                on_satisfied="continue",
                continuation={
                    "reason": "Publication starts a separately authorized remediation task.",
                    "task_ids": ["REL-001"],
                },
            ),
        )

    def test_gwt_015_given_active_continuation_when_unfinished_task_is_not_declared_then_fails_closed(self) -> None:
        errors = self.validate_terminal_anchor(
            workflow_status="in_progress",
            task_status="in_progress",
            on_satisfied="continue",
            continuation={
                "reason": "Publication starts a separately authorized remediation task.",
                "task_ids": ["REL-OTHER"],
            },
        )

        self.assertTrue(any("reference missing tasks" in error for error in errors))

    def test_gwt_016_given_no_declared_terminal_anchor_when_workflow_active_then_no_anchor_is_inferred(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_terminal_anchor_contract(
            {"workflow_id": "unbound", "status": "in_progress"},
            [("REL-001", identified_task("REL-001", "in_progress"))],
            "unbound/workflow.yaml",
            errors,
            repo=REPO_ROOT,
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
