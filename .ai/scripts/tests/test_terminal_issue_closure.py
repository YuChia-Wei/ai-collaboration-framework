#!/usr/bin/env python3
"""GWT tests for source-only terminal and deferred GitHub Issue dispositions."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
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


def audit_review_body(**overrides: object) -> str:
    payload = {
        "repository": "YuChia-Wei/ai-collaboration-framework",
        "pull_request": 300,
        "base_sha": "b" * 40,
        "head_sha": "a" * 40,
        "outcome": "passed",
        "blocking_findings": 0,
        "audit_scope": "fresh-exact-head-independent",
    }
    payload.update(overrides)
    return (
        "<!-- github-terminal-issue-closure-audit/v1\n"
        f"{json.dumps(payload, separators=(',', ':'))}\n"
        "-->"
    )


class TerminalIssueClosureGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ROOT / ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.commit_messages_patcher = mock.patch.object(VALIDATOR, "commit_messages", return_value="")
        cls.commit_messages_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.commit_messages_patcher.stop()

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
        data["pull_request"]["integration"]["admitted_head_sha"] = "b" * 40
        self.assert_error(data, "bind the admitted PR head")

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
        self.assert_error(data, "requires a passing single-maintainer audit receipt")

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
                    self.assert_error(data, "audit receipt must be bound")
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
                {
                    "pr_number": 300,
                    "repository": "YuChia-Wei/ai-collaboration-framework",
                    "base_repository": "YuChia-Wei/ai-collaboration-framework",
                    "base_sha": "b" * 40,
                    "head_sha": "a" * 40,
                    "body": "Refs #212",
                },
                self.config,
                "test-token",
            )
        self.assertEqual("github", evidence["provider"])
        self.assertEqual("github-terminal-issue-closure-admission", evidence["contract_id"])
        self.assertEqual(pull_request, evidence["pull_request"])

    def test_gwt_035_given_comment_after_change_request_when_read_live_then_block_remains(self) -> None:
        metadata = {
            "number": 300,
            "body": "Refs #212",
            "head": {"sha": "a" * 40},
            "base": {
                "sha": "b" * 40,
                "repo": {"full_name": "YuChia-Wei/ai-collaboration-framework"},
            },
        }
        reviews = [
            {"id": 10, "state": "CHANGES_REQUESTED", "commit_id": "a" * 40, "user": {"login": "alice"}},
            {"id": 11, "state": "COMMENTED", "commit_id": "a" * 40, "user": {"login": "alice"}},
            {"id": 12, "state": "APPROVED", "commit_id": "a" * 40, "user": {"login": "bob"}},
        ]
        checks = [
            {
                "id": item["provider_check_run_id"],
                "name": item["name"],
                "conclusion": item["conclusion"],
                "head_sha": item["head_sha"],
                "completed_at": item["completed_at"],
            }
            for item in fixture("admission-positive.yaml")["pull_request"]["hosted_checks"]
        ]
        required = self.config["work_item_binding"]["merge_gate"]["required_check_contexts"]
        review_gate = self.config["work_item_binding"]["merge_gate"]["review_gate"]
        with (
            mock.patch.object(VALIDATOR, "github_api_json", return_value=(metadata, None)),
            mock.patch.object(VALIDATOR, "github_api_paginated", side_effect=[reviews, checks]),
        ):
            facts = VALIDATOR.read_live_provider_facts(
                "YuChia-Wei/ai-collaboration-framework",
                300,
                "a" * 40,
                required,
                review_gate,
                "test-token",
            )
        self.assertEqual("blocked", facts["review"]["status"])
        self.assertEqual([10], facts["review"]["blocking_provider_review_ids"])
        self.assertEqual("b" * 40, facts["base_sha"])
        self.assertEqual("Refs #212", facts["body"])

    def test_gwt_036_given_provider_next_link_when_read_then_all_pages_are_combined(self) -> None:
        next_url = "https://api.github.com/example?page=2"
        with mock.patch.object(
            VALIDATOR,
            "github_api_json",
            side_effect=[([{"id": 1}], f'<{next_url}>; rel="next"'), ([{"id": 2}], None)],
        ):
            self.assertEqual(
                [{"id": 1}, {"id": 2}],
                VALIDATOR.github_api_paginated("https://api.github.com/example?page=1", "test-token"),
            )

    def test_gwt_037_given_full_provider_page_without_completion_proof_when_read_then_it_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "github_api_json", return_value=([{"id": value} for value in range(100)], None)):
            with self.assertRaisesRegex(ValueError, "pagination is incomplete"):
                VALIDATOR.github_api_paginated("https://api.github.com/example", "test-token")

    def test_gwt_038_given_live_capture_when_admitted_then_no_output_path_is_accepted_or_written(self) -> None:
        evidence = fixture("admission-positive.yaml")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40),
            mock.patch.object(VALIDATOR, "build_live_admission_evidence", return_value=evidence),
            mock.patch.dict(VALIDATOR.os.environ, {"GITHUB_TOKEN": "test-token"}),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            self.assertEqual(
                0,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-deferred.json"),
                        "--capture-admission-evidence",
                    ]
                ),
            )
        self.assertEqual(evidence, yaml.safe_load(stdout.getvalue()))
        self.assertIn("validation passed", stderr.getvalue())

    def test_gwt_039_given_malformed_provider_link_header_when_read_then_it_fails(self) -> None:
        with mock.patch.object(VALIDATOR, "github_api_json", return_value=([{"id": 1}], "malformed-link-header")):
            with self.assertRaisesRegex(ValueError, "malformed pagination Link"):
                VALIDATOR.github_api_paginated("https://api.github.com/example", "test-token")

    def test_gwt_040_given_short_check_page_disagrees_with_total_count_when_read_then_it_fails(self) -> None:
        payload = {"total_count": 200, "check_runs": [{"id": 1}]}
        with mock.patch.object(VALIDATOR, "github_api_json", return_value=(payload, None)):
            with self.assertRaisesRegex(ValueError, "does not match total_count"):
                VALIDATOR.github_api_paginated(
                    "https://api.github.com/example", "test-token", "check_runs"
                )

    def test_gwt_041_given_duplicate_next_relations_when_read_then_it_fails_without_skipping(self) -> None:
        link = (
            '<https://api.github.com/example?page=2>; rel="next", '
            '<https://api.github.com/example?page=3>; rel="next"'
        )
        with mock.patch.object(VALIDATOR, "github_api_json", return_value=([{"id": 1}], link)):
            with self.assertRaisesRegex(ValueError, "duplicate pagination relation 'next'"):
                VALIDATOR.github_api_paginated("https://api.github.com/example?page=1", "test-token")

    def test_gwt_042_given_multi_token_link_relation_when_read_then_it_fails_closed(self) -> None:
        link = '<https://api.github.com/example?page=2>; rel="next last"'
        with mock.patch.object(VALIDATOR, "github_api_json", return_value=([{"id": 1}], link)):
            with self.assertRaisesRegex(ValueError, "unsupported pagination relation"):
                VALIDATOR.github_api_paginated("https://api.github.com/example?page=1", "test-token")

    def test_gwt_043_given_body_references_undeclared_issue_when_validated_then_it_fails(self) -> None:
        data = fixture("deferred-positive.yaml")
        data["pull_request"]["body"] = "Refs #212\nCloses #999"
        self.assert_error(data, "Issue #999 is referenced without exactly one disposition")

    def test_gwt_044_given_body_closes_foreign_same_number_when_validated_then_it_fails(self) -> None:
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["body"] = "Closes attacker/other#212"
        self.assert_error(data, "references foreign repository Issue attacker/other#212")

    def test_gwt_045_given_deferred_issue_when_commit_message_closes_it_then_it_fails(self) -> None:
        data = fixture("deferred-positive.yaml")
        errors = VALIDATOR.validate_record(
            data,
            self.config,
            {
                "pr_number": 300,
                "head_sha": "a" * 40,
                "body": "Refs #212",
                "commit_messages": "fix: complete work\n\nCloses #212",
            },
        )
        self.assertTrue(any("commit messages must not contain closing keyword" in error for error in errors), errors)

    def test_gwt_046_given_stale_event_body_when_live_capture_runs_then_it_fails_closed(self) -> None:
        live = fixture("admission-positive.yaml")["pull_request"]
        runtime = {
            "pr_number": 300,
            "repository": "YuChia-Wei/ai-collaboration-framework",
            "base_repository": "YuChia-Wei/ai-collaboration-framework",
            "base_sha": "b" * 40,
            "head_sha": "a" * 40,
            "body": "Closes #999",
        }
        with mock.patch.object(VALIDATOR, "read_live_provider_facts", return_value=live):
            with self.assertRaisesRegex(ValueError, "body does not match fresh GitHub"):
                VALIDATOR.build_live_admission_evidence(
                    fixture("declaration-bound.yaml"), runtime, self.config, "test-token"
                )

    def test_gwt_047_given_fabricated_event_base_when_live_replay_runs_then_it_fails_closed(self) -> None:
        evidence = fixture("admission-positive.yaml")
        runtime = {
            "pr_number": 300,
            "repository": "YuChia-Wei/ai-collaboration-framework",
            "base_repository": "YuChia-Wei/ai-collaboration-framework",
            "base_sha": "a" * 40,
            "head_sha": "a" * 40,
            "body": "Refs #212",
        }
        with (
            mock.patch.object(VALIDATOR, "read_live_provider_facts", return_value=evidence["pull_request"]),
            mock.patch.dict(VALIDATOR.os.environ, {"GITHUB_TOKEN": "test-token"}),
        ):
            errors = VALIDATOR.validate_live_provider_evidence(
                evidence, fixture("declaration-bound.yaml"), runtime, self.config
            )
        self.assertTrue(any("base_sha does not match fresh GitHub" in error for error in errors), errors)

    def test_gwt_048_given_live_pr_identity_or_head_mismatch_when_read_then_it_fails_closed(self) -> None:
        candidates = [
            (
                {
                    "number": 999,
                    "body": "Refs #212",
                    "head": {"sha": "a" * 40},
                    "base": {
                        "sha": "b" * 40,
                        "repo": {"full_name": "YuChia-Wei/ai-collaboration-framework"},
                    },
                },
                "mismatched pull request metadata",
            ),
            (
                {
                    "number": 300,
                    "body": "Refs #212",
                    "head": {"sha": "a" * 40},
                    "base": {"sha": "b" * 40, "repo": {"full_name": "attacker/other"}},
                },
                "base repository does not match",
            ),
            (
                {
                    "number": 300,
                    "body": "Refs #212",
                    "head": {"sha": "c" * 40},
                    "base": {
                        "sha": "b" * 40,
                        "repo": {"full_name": "YuChia-Wei/ai-collaboration-framework"},
                    },
                },
                "head does not match the current event head",
            ),
        ]
        required = self.config["work_item_binding"]["merge_gate"]["required_check_contexts"]
        review_gate = self.config["work_item_binding"]["merge_gate"]["review_gate"]
        for metadata, fragment in candidates:
            with self.subTest(fragment=fragment):
                with mock.patch.object(VALIDATOR, "github_api_json", return_value=(metadata, None)):
                    with self.assertRaisesRegex(ValueError, fragment):
                        VALIDATOR.read_live_provider_facts(
                            "YuChia-Wei/ai-collaboration-framework",
                            300,
                            "a" * 40,
                            required,
                            review_gate,
                            "test-token",
                        )

    def test_gwt_050_given_exact_source_maintainer_audit_receipt_when_read_then_review_gate_passes(self) -> None:
        metadata = {
            "number": 300,
            "body": "Refs #212",
            "head": {"sha": "a" * 40},
            "base": {
                "sha": "b" * 40,
                "repo": {"full_name": "YuChia-Wei/ai-collaboration-framework"},
            },
        }
        reviews = [{
            "id": 7001,
            "state": "COMMENTED",
            "body": audit_review_body(),
            "commit_id": "a" * 40,
            "submitted_at": "2026-08-20T01:00:00Z",
            "user": {"login": "YuChia-Wei"},
        }]
        checks = [
            {
                "id": item["provider_check_run_id"],
                "name": item["name"],
                "conclusion": item["conclusion"],
                "head_sha": item["head_sha"],
                "completed_at": item["completed_at"],
            }
            for item in fixture("admission-positive.yaml")["pull_request"]["hosted_checks"]
        ]
        gate = self.config["work_item_binding"]["merge_gate"]
        with (
            mock.patch.object(VALIDATOR, "github_api_json", return_value=(metadata, None)),
            mock.patch.object(VALIDATOR, "github_api_paginated", side_effect=[reviews, checks]),
        ):
            facts = VALIDATOR.read_live_provider_facts(
                "YuChia-Wei/ai-collaboration-framework",
                300,
                "a" * 40,
                gate["required_check_contexts"],
                gate["review_gate"],
                "test-token",
            )
        self.assertEqual("single-maintainer-audit-passed", facts["review"]["status"])
        self.assertEqual("YuChia-Wei", facts["review"]["reviewer_login"])

    def test_gwt_051_given_non_receipt_or_wrong_identity_when_read_then_review_remains_pending(self) -> None:
        metadata = {
            "number": 300,
            "body": "Refs #212",
            "head": {"sha": "a" * 40},
            "base": {
                "sha": "b" * 40,
                "repo": {"full_name": "YuChia-Wei/ai-collaboration-framework"},
            },
        }
        candidates = [
            {"id": 1, "state": "COMMENTED", "body": "audit passed", "commit_id": "a" * 40, "user": {"login": "YuChia-Wei"}},
            {"id": 2, "state": "COMMENTED", "body": audit_review_body(), "commit_id": "a" * 40, "user": {"login": "attacker"}},
            {"id": 3, "state": "COMMENTED", "body": audit_review_body(head_sha="c" * 40), "commit_id": "a" * 40, "user": {"login": "YuChia-Wei"}},
            {"id": 4, "state": "COMMENTED", "body": audit_review_body(blocking_findings=False), "commit_id": "a" * 40, "user": {"login": "YuChia-Wei"}},
        ]
        gate = self.config["work_item_binding"]["merge_gate"]
        with (
            mock.patch.object(VALIDATOR, "github_api_json", return_value=(metadata, None)),
            mock.patch.object(VALIDATOR, "github_api_paginated", side_effect=[candidates, []]),
        ):
            facts = VALIDATOR.read_live_provider_facts(
                "YuChia-Wei/ai-collaboration-framework",
                300,
                "a" * 40,
                gate["required_check_contexts"],
                gate["review_gate"],
                "test-token",
            )
        self.assertEqual({"status": "pending"}, facts["review"])

    def test_gwt_052_given_review_gate_identity_drifts_when_validated_then_it_fails_closed(self) -> None:
        config = yaml.safe_load(yaml.safe_dump(self.config))
        config["work_item_binding"]["merge_gate"]["review_gate"]["maintainer_login"] = "someone-else"
        errors = VALIDATOR.validate_record(fixture("terminal-positive.yaml"), config)
        self.assertTrue(any("source single-maintainer audit receipt contract" in error for error in errors), errors)

    def test_gwt_053_given_supported_integration_topology_when_commit_identity_follows_topology_then_it_passes(self) -> None:
        for topology in ("fast-forward", "rebase", "squash", "merge-commit"):
            with self.subTest(topology=topology):
                data = fixture("terminal-positive.yaml")
                data["pull_request"]["integration"]["topology"] = topology
                if topology == "fast-forward":
                    head_sha = data["pull_request"]["head_sha"]
                    data["pull_request"]["integration"]["integration_commit_sha"] = head_sha
                    data["issues"][0]["read_back"]["integration_commit_sha"] = head_sha
                else:
                    self.assertNotEqual(
                        data["pull_request"]["head_sha"],
                        data["pull_request"]["integration"]["integration_commit_sha"],
                    )
                self.assertEqual([], self.errors(data))

    def test_gwt_054_given_unknown_topology_or_missing_provider_readback_when_reconciled_then_it_fails(self) -> None:
        candidates = [("topology", "custom"), ("provider_read_back", False)]
        for field, value in candidates:
            with self.subTest(field=field):
                data = fixture("terminal-positive.yaml")
                data["pull_request"]["integration"][field] = value
                self.assertTrue(self.errors(data))
        data = fixture("terminal-positive.yaml")
        data["pull_request"]["integration"]["topology"] = "fast-forward"
        self.assert_error(data, "fast-forward reconciliation requires")

    def test_gwt_049_given_fabricated_event_repository_when_validated_then_it_fails_closed(self) -> None:
        runtime = VALIDATOR.runtime_from_event(FIXTURES / "pr-event-foreign-repository.json")
        live = fixture("admission-positive.yaml")["pull_request"]
        errors = VALIDATOR.validate_live_runtime(live, runtime)
        self.assertTrue(any("event repository does not match fresh GitHub" in error for error in errors), errors)
        self.assertTrue(any("event base_repository does not match fresh GitHub" in error for error in errors), errors)
        with mock.patch.object(VALIDATOR, "checkout_head", return_value="a" * 40):
            self.assertEqual(
                1,
                VALIDATOR.main(
                    [
                        "--record",
                        str(FIXTURES / "declaration-bound.yaml"),
                        "--event-path",
                        str(FIXTURES / "pr-event-foreign-repository.json"),
                    ]
                ),
            )


if __name__ == "__main__":
    unittest.main()
