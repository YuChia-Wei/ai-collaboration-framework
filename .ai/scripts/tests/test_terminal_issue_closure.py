#!/usr/bin/env python3
"""GWT tests for source-only terminal and deferred GitHub Issue dispositions."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/validate-terminal-issue-closure.py"
SPEC = importlib.util.spec_from_file_location("terminal_issue_closure", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {MODULE_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
FIXTURES = Path(__file__).parent / "fixtures/terminal-issue-closure"


def fixture(name: str) -> dict:
    value = yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"invalid fixture {name}")
    return value


class TerminalIssueClosureGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ROOT / ".dev/backlog/providers/github.yaml").read_text(encoding="utf-8")
        )

    def errors(self, candidate: dict) -> list[str]:
        return VALIDATOR.validate_record(candidate, self.config)

    def assert_error(self, candidate: dict, fragment: str) -> None:
        errors = self.errors(candidate)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_gwt_001_given_terminal_delivery_when_all_gates_and_readback_match_then_it_passes(self) -> None:
        self.assertEqual([], self.errors(fixture("terminal-positive.yaml")))

    def test_gwt_002_given_terminal_delivery_when_keyword_is_missing_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["body"] = "Refs #212"
        self.assert_error(data, "matching closing keyword")

    def test_gwt_003_given_terminal_delivery_when_keyword_mismatches_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["body"] = "Fixes #212"
        self.assert_error(data, "matching closing keyword")

    def test_gwt_004_given_terminal_delivery_when_workflow_or_verification_is_incomplete_then_it_fails_closed(self) -> None:
        for field in ("scope_complete", "tasks_complete", "applicable_verification_complete"):
            with self.subTest(field=field):
                data = fixture("terminal-positive.yaml")
                data["issues"][0]["workflow"][field] = False
                self.assert_error(data, f"workflow.{field}=true")

    def test_gwt_005_given_deferred_delivery_when_reason_and_next_gate_exist_then_it_passes(self) -> None:
        self.assertEqual([], self.errors(fixture("deferred-positive.yaml")))

    def test_gwt_006_given_deferred_delivery_when_closing_keyword_exists_then_it_fails_closed(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["pull_request"]["body"] = "Closes #212"
        self.assert_error(data, "requires exactly Refs")

    def test_gwt_007_given_deferred_delivery_when_reason_is_missing_then_it_fails_closed(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["issues"][0]["closure_deferred_reason"] = ""
        self.assert_error(data, "requires closure_deferred_reason")

    def test_gwt_008_given_deferred_delivery_when_next_gate_is_missing_then_it_fails_closed(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["issues"][0]["next_terminal_gate_or_owner"] = None
        self.assert_error(data, "requires next_terminal_gate_or_owner")

    def test_gwt_009_given_mixed_per_issue_dispositions_when_each_is_valid_then_they_pass(self) -> None:
        self.assertEqual([], self.errors(fixture("mixed-positive.yaml")))

    def test_gwt_010_given_terminal_delivery_when_merged_head_drifts_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["integration"]["merged_head_sha"] = "b" * 40
        self.assert_error(data, "exact merged-head integration")

    def test_gwt_011_given_terminal_delivery_when_issue_remains_open_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["issues"][0]["read_back"]["issue_state"] = "open"
        self.assert_error(data, "matching post-merge")

    def test_gwt_012_given_merged_deferred_delivery_when_issue_is_closed_then_it_fails_closed(self) -> None:
        data = fixture("mixed-positive.yaml")
        data["issues"][1]["read_back"]["issue_state"] = "closed"
        self.assert_error(data, "must prove it remains open")

    def test_gwt_013_given_terminal_delivery_when_project_is_not_done_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["issues"][0]["read_back"]["project_status"] = "Verification"
        self.assert_error(data, "matching post-merge")

    def test_gwt_014_given_terminal_delivery_when_hosted_gate_is_non_success_then_it_fails_closed(self) -> None:
        for conclusion in ("failure", "cancelled", "timed_out"):
            with self.subTest(conclusion=conclusion):
                data = fixture("terminal-positive.yaml")
                data["pull_request"]["hosted_checks"][0]["conclusion"] = conclusion
                self.assert_error(data, "must succeed")

    def test_gwt_015_given_terminal_delivery_when_review_is_blocked_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["review"]["status"] = "blocked"
        self.assert_error(data, "requires approved review")

    def test_gwt_016_given_terminal_delivery_when_readback_is_missing_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["issues"][0]["read_back"] = {"performed": False}
        self.assert_error(data, "matching post-merge")

    def test_gwt_017_given_closing_keyword_without_authorization_then_it_does_not_authorize_work(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["issues"][0]["work_authorization"]["explicit_owner_approval"] = False
        self.assert_error(data, "independent of keywords")

    def test_gwt_018_given_downstream_profile_when_inspected_then_github_closure_assets_are_excluded(self) -> None:
        profile = yaml.safe_load(
            (ROOT / ".ai/distribution/profiles/dotnet-backend.yaml").read_text(encoding="utf-8")
        )
        included = {source for entry in profile["components"] for source in entry.get("source", []) if isinstance(source, str)}
        excluded = {pattern for entry in profile["exclusions"] for pattern in entry.get("patterns", [])}
        self.assertNotIn(".github/pull_request_template.md", included)
        self.assertTrue({
            ".github/pull_request_template.md",
            ".dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md",
            ".ai/scripts/validate-terminal-issue-closure.py",
        }.issubset(excluded))

    def test_gwt_019_given_deferred_body_when_inline_closing_keyword_exists_then_it_fails_closed(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["pull_request"]["body"] = "Refs #212\n\nThis work Closes #212 after review."
        self.assert_error(data, "requires exactly Refs")

    def test_gwt_020_given_deferred_body_when_qualified_closing_keyword_exists_then_it_fails_closed(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["pull_request"]["body"] = "Refs #212\nFixes YuChia-Wei/ai-collaboration-framework#212"
        self.assert_error(data, "requires exactly Refs")

    def test_gwt_021_given_review_or_check_head_drift_when_admitted_then_it_fails_closed(self) -> None:
        for target in ("review", "check"):
            with self.subTest(target=target):
                data = fixture("terminal-positive.yaml")
                if target == "review":
                    data["pull_request"]["review"]["head_sha"] = "b" * 40
                    self.assert_error(data, "approved review must be bound")
                else:
                    data["pull_request"]["hosted_checks"][0]["head_sha"] = "b" * 40
                    self.assert_error(data, "hosted check 'governance' must be bound")

    def test_gwt_022_given_required_context_is_missing_when_admitted_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["required_check_contexts"].append("portable")
        self.assert_error(data, "exactly cover required_check_contexts")

    def test_gwt_023_given_current_pr_event_when_number_or_head_mismatches_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        runtime = {"pr_number": 999, "head_sha": "b" * 40, "body": "Closes #212"}
        errors = VALIDATOR.validate_record(data, self.config, runtime)
        self.assertTrue(any("number does not match" in error for error in errors), errors)
        self.assertTrue(any("head_sha does not match" in error for error in errors), errors)

    def test_gwt_024_given_current_pr_event_when_exact_record_is_selected_then_cli_passes(self) -> None:
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40):
            self.assertEqual(
                0,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                    ]
                ),
            )

    def test_gwt_025_given_current_pr_event_when_no_bound_record_exists_then_cli_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "deferred-positive.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-terminal.json"),
                    ]
                ),
            )

    def test_gwt_026_given_current_pr_event_when_checkout_head_drifts_then_cli_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="b" * 40):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                    ]
                ),
            )

    def test_gwt_027_given_declaration_check_when_record_claims_later_stage_then_cli_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "terminal-positive.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-terminal.json"),
                    ]
                ),
            )

    def test_gwt_028_given_untracked_admission_snapshot_when_exact_head_evidence_passes_then_cli_passes(self) -> None:
        evidence = fixture("admission-positive.yaml")
        with (
            mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40),
            mock.patch.object(VALIDATOR, "read_live_provider_facts", return_value=evidence["pull_request"]),
            mock.patch.dict(VALIDATOR.os.environ, {"GITHUB_TOKEN": "test-token"}),
        ):
            self.assertEqual(
                0,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                        "--admission-evidence",
                        str(FIXTURES / "admission-positive.yaml"),
                        "--verify-provider-live",
                    ]
                ),
            )

    def test_gwt_029_given_admission_snapshot_when_head_drifts_then_cli_fails(self) -> None:
        evidence = fixture("admission-positive.yaml")
        evidence["pull_request"]["head_sha"] = "b" * 40
        bound, errors = VALIDATOR.bind_admission_evidence(fixture("declaration-bound.yaml"), evidence, self.config)
        errors.extend(
            VALIDATOR.validate_record(
                bound,
                self.config,
                {"pr_number": 300, "head_sha": "a" * 40, "body": "Refs #212"},
            )
        )
        self.assertTrue(any("head_sha does not match" in error for error in errors), errors)

    def test_gwt_030_given_later_lifecycle_record_when_admission_is_supplied_then_downgrade_fails(self) -> None:
        _, errors = VALIDATOR.bind_admission_evidence(
            fixture("terminal-positive.yaml"), fixture("admission-positive.yaml"), self.config
        )
        self.assertTrue(any("only overlay a tracked declaration" in error for error in errors), errors)

    def test_gwt_031_given_snapshot_omits_provider_owned_context_when_bound_then_it_fails(self) -> None:
        evidence = fixture("admission-positive.yaml")
        evidence["pull_request"]["required_check_contexts"] = ["Read-only governance contract"]
        evidence["pull_request"]["hosted_checks"] = evidence["pull_request"]["hosted_checks"][:1]
        _, errors = VALIDATOR.bind_admission_evidence(fixture("declaration-bound.yaml"), evidence, self.config)
        self.assertTrue(any("provider-owned required_check_contexts" in error for error in errors), errors)

    def test_gwt_032_given_snapshot_without_live_provider_verification_when_admitted_then_it_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                        "--admission-evidence",
                        str(FIXTURES / "admission-positive.yaml"),
                    ]
                ),
            )

    def test_gwt_033_given_snapshot_differs_from_fresh_provider_readback_when_admitted_then_it_fails(self) -> None:
        evidence = fixture("admission-positive.yaml")
        live = fixture("admission-positive.yaml")["pull_request"]
        live["hosted_checks"][0]["provider_check_run_id"] = 9999
        with (
            mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40),
            mock.patch.object(VALIDATOR, "read_live_provider_facts", return_value=live),
            mock.patch.dict(VALIDATOR.os.environ, {"GITHUB_TOKEN": "test-token"}),
        ):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                        "--admission-evidence",
                        str(FIXTURES / "admission-positive.yaml"),
                        "--verify-provider-live",
                    ]
                ),
            )

    def test_gwt_034_given_live_provider_facts_when_built_then_snapshot_has_provider_identity(self) -> None:
        pull_request = fixture("admission-positive.yaml")["pull_request"]
        with mock.patch.object(VALIDATOR, "read_live_provider_facts", return_value=pull_request):
            evidence = VALIDATOR.build_live_admission_evidence(
                fixture("declaration-bound.yaml"),
                {"pr_number": 300, "head_sha": "a" * 40, "body": "Refs #212"},
                self.config,
                "test-token",
            )
        self.assertEqual("github", evidence["provider"])
        self.assertEqual("github-terminal-issue-closure-admission", evidence["contract_id"])
        self.assertEqual(pull_request, evidence["pull_request"])

    def test_gwt_035_given_capture_path_outside_ignored_evidence_root_when_requested_then_it_fails(self) -> None:
        with mock.patch.dict(VALIDATOR.os.environ, {"GITHUB_TOKEN": "test-token"}):
            with self.assertRaisesRegex(ValueError, "directly under artifacts/validation"):
                VALIDATOR.capture_live_admission_evidence(
                    ROOT / "admission.yaml",
                    fixture("declaration-bound.yaml"),
                    {"pr_number": 300, "head_sha": "a" * 40, "body": "Refs #212"},
                    self.config,
                )


if __name__ == "__main__":
    unittest.main()
