#!/usr/bin/env python3
"""GWT tests for source-only terminal and deferred GitHub Issue dispositions."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

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
        self.assert_error(data, "must remain open")

    def test_gwt_013_given_terminal_delivery_when_project_is_not_done_then_it_fails_closed(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["issues"][0]["read_back"]["project_status"] = "Verification"
        self.assert_error(data, "matching post-merge")

    def test_gwt_014_given_terminal_delivery_when_hosted_gate_is_non_success_then_it_fails_closed(self) -> None:
        for conclusion in ("failure", "cancelled", "timed_out"):
            with self.subTest(conclusion=conclusion):
                data = fixture("terminal-positive.yaml")
                data["pull_request"]["hosted_checks"][0]["conclusion"] = conclusion
                self.assert_error(data, "every hosted check to succeed")

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


if __name__ == "__main__":
    unittest.main()
