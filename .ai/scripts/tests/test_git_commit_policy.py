#!/usr/bin/env python3
"""GWT tests for executable Git commit-message policy."""

from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-git-commits.py"
POLICY_PATH = REPO_ROOT / ".dev/standards/GIT-COMMIT-POLICY.yaml"
SPEC = importlib.util.spec_from_file_location("validate_git_commits", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
POLICY = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
WORKFLOW_ID = "2026-07-15-example"


def workflow_message(subject: str = "fix(ai-context): enforce policy") -> str:
    return f"""{subject}

Why
Policy prose alone cannot fail closed.

What
Add executable validation.

Validation
- policy GWT

Workflow
{WORKFLOW_ID} / TASK-001

Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""


def subject_grammar_adoption(tip: str) -> dict[str, str]:
    return {
        "policy_id": "git-commit-subject/v2",
        "legacy_history_tip": tip,
        "adopted_at": "2026-08-20T09:00:00+08:00",
        "incoming_policy_sha256": VALIDATOR.policy_sha256(POLICY_PATH),
        "decision_evidence": ".dev/workflows/upgrade/decision.md#commit-grammar",
    }


class GitCommitPolicyTests(unittest.TestCase):
    def validate(self, message: str, workflow_id: str | None = WORKFLOW_ID) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_message("abc123", message, POLICY, errors, workflow_id)
        return errors

    def validate_at(
        self,
        message: str,
        committed_at: str,
        workflow_id: str | None = WORKFLOW_ID,
    ) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_message(
            "abc123",
            message,
            POLICY,
            errors,
            workflow_id,
            committed_at=datetime.fromisoformat(committed_at),
        )
        return errors

    def test_gwt_001_given_valid_workflow_commit_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(workflow_message()))

    def test_gwt_002_given_invalid_subject_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message("updated some files"))
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_003_given_missing_section_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message().replace("\nValidation\n", "\nChecks\n"))
        self.assertTrue(any("missing workflow body sections: Validation" in error for error in errors))

    def test_gwt_004_given_wrong_workflow_identity_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message().replace(WORKFLOW_ID, "2026-07-15-other"))
        self.assertTrue(any("does not identify" in error for error in errors))

    def test_gwt_005_given_nonfinal_ai_trailer_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message() + "Unexpected final line\n")
        self.assertTrue(any("final non-empty line" in error for error in errors))

    def test_gwt_006_given_merge_commit_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(workflow_message("merge(ai-context): integrate workflow")))

    def test_gwt_007_given_assessment_subject_without_matching_trailer_when_validated_then_fails(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        errors = self.validate(message, workflow_id=None)
        self.assertTrue(any("lacks matching Assessment-Id trailer" in error for error in errors))

    def test_gwt_008_given_assessment_subject_and_matching_trailer_when_validated_then_passes(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Assessment-Id: ASM-20260715-001
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        self.assertEqual([], self.validate(message, workflow_id=None))

    def test_gwt_009_given_standalone_assessment_in_workflow_range_when_validated_then_assessment_contract_applies(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Assessment-Id: ASM-20260715-001
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        self.assertEqual([], self.validate(message, workflow_id=WORKFLOW_ID))

    def test_gwt_010_given_workflow_range_when_selected_then_first_parent_excludes_merged_branch_history(self) -> None:
        with mock.patch.object(VALIDATOR, "git", return_value="abc123\ndef456\n") as git:
            commits = VALIDATOR.selected_commits(
                "base..HEAD",
                None,
                first_parent=True,
            )

        self.assertEqual(["abc123", "def456"], commits)
        git.assert_called_once_with(
            "rev-list",
            "--first-parent",
            "--reverse",
            "base..HEAD",
            root=VALIDATOR.ROOT,
        )

    def test_gwt_011_given_signature_without_reasoning_when_validated_then_fails(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "OpenAI Codex (gpt-5.6-sol)",
        )
        errors = self.validate(message)
        self.assertTrue(any("valid Co-Authored-By" in error for error in errors))

    def test_gwt_012_given_marked_subagent_contributor_when_validated_then_passes(self) -> None:
        message = workflow_message().replace(
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>",
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>\n"
            "Co-Authored-By: OpenAI Codex Sub-Agent (gpt-5.6-terra, medium) <noreply@openai.com>",
        )
        self.assertEqual([], self.validate(message))

    def test_gwt_013_given_unmarked_additional_contributor_when_validated_then_fails(self) -> None:
        message = workflow_message().replace(
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>",
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>\n"
            "Co-Authored-By: Claude Code (claude-sonnet-5, extended) <noreply@anthropic.com>",
        )
        errors = self.validate(message)
        self.assertTrue(any("must mark the runtime with Sub-Agent" in error for error in errors))

    def test_gwt_014_given_provider_reasoning_label_when_validated_then_preserves_original(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "Claude Code (claude-sonnet-5, extended thinking)",
        ).replace("noreply@openai.com", "noreply@anthropic.com")
        self.assertEqual([], self.validate(message))

    def test_gwt_015_given_pre_policy_signature_when_validated_then_legacy_shape_passes(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "OpenAI Codex (GPT-5)",
        )
        errors: list[str] = []
        VALIDATOR.validate_message(
            "abc123",
            message,
            POLICY,
            errors,
            WORKFLOW_ID,
            committed_at=datetime.fromisoformat("2026-07-27T09:00:00+08:00"),
        )
        self.assertEqual([], errors)

    def test_gwt_016_given_current_issue_form_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#176): clarify validation contract"),
                "2026-08-10T00:40:00+08:00",
            ),
        )

    def test_gwt_017_given_current_multiple_issue_form_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#175,#176): reconcile validation boundaries"),
                "2026-08-10T00:40:00+08:00",
            ),
        )

    def test_gwt_018_given_literal_pipe_after_cutover_when_validated_then_fails(self) -> None:
        errors = self.validate_at(
            workflow_message("docs(#176|validation): reject literal pipe"),
            "2026-08-10T00:40:00+08:00",
        )
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_019_given_literal_pipe_before_cutover_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#176|validation): retain historical title"),
                "2026-08-10T00:39:59+08:00",
            ),
        )

    def test_gwt_020_given_validated_target_adoption_when_legacy_commit_is_reachable_then_legacy_subject_passes(self) -> None:
        legacy_sha = "a" * 40

        def git_result(*args: str, root: Path) -> str:
            if "--format=%B" in args and args[-1] == legacy_sha:
                return workflow_message("docs(#176|legacy): preserve target history")
            return "2026-08-20T09:00:00+08:00\n"

        with (
            mock.patch.object(VALIDATOR, "git", side_effect=git_result),
            mock.patch.object(VALIDATOR, "git_returncode", return_value=0),
        ):
            errors = VALIDATOR.validate_commits(
                [legacy_sha],
                POLICY,
                workflow_id=WORKFLOW_ID,
                adoption_evidence=subject_grammar_adoption(legacy_sha),
                incoming_policy_sha256=VALIDATOR.policy_sha256(POLICY_PATH),
            )

        self.assertEqual([], errors)

    def test_gwt_021_given_validated_target_adoption_when_post_boundary_commit_uses_legacy_subject_then_it_fails(self) -> None:
        legacy_sha = "a" * 40
        post_adoption_sha = "b" * 40

        def git_result(*args: str, root: Path) -> str:
            if "--format=%B" in args and args[-1] == post_adoption_sha:
                return workflow_message("docs(#177|legacy): reject after adoption")
            return "2026-08-10T00:39:59+08:00\n"

        def reachability(*args: str, root: Path) -> int:
            return 1 if args[:3] == ("merge-base", "--is-ancestor", post_adoption_sha) else 0

        with (
            mock.patch.object(VALIDATOR, "git", side_effect=git_result),
            mock.patch.object(VALIDATOR, "git_returncode", side_effect=reachability),
        ):
            errors = VALIDATOR.validate_commits(
                [post_adoption_sha],
                POLICY,
                workflow_id=WORKFLOW_ID,
                adoption_evidence=subject_grammar_adoption(legacy_sha),
                incoming_policy_sha256=VALIDATOR.policy_sha256(POLICY_PATH),
            )

        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_022_given_nonexistent_or_unreachable_target_boundary_when_validated_then_it_fails_closed(self) -> None:
        for return_codes, expected in (
            ([1], "does not resolve"),
            ([0, 0, 1], "not reachable"),
        ):
            with self.subTest(return_codes=return_codes):
                with mock.patch.object(
                    VALIDATOR,
                    "git_returncode",
                    side_effect=return_codes,
                ):
                    errors = VALIDATOR.validate_commits(
                        ["b" * 40],
                        POLICY,
                        workflow_id=WORKFLOW_ID,
                        adoption_evidence=subject_grammar_adoption("a" * 40),
                        incoming_policy_sha256=VALIDATOR.policy_sha256(POLICY_PATH),
                    )
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_gwt_023_given_explicit_target_boundary_when_timestamp_predates_source_cutover_then_boundary_still_selects_canonical(self) -> None:
        pattern = VALIDATOR.subject_pattern_for_commit(
            POLICY,
            datetime.fromisoformat("2026-08-10T00:39:59+08:00"),
            use_legacy_subject_grammar=False,
        )

        self.assertEqual(POLICY["subject_pattern"], pattern)


if __name__ == "__main__":
    unittest.main()
