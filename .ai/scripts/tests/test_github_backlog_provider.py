#!/usr/bin/env python3
"""GWT compatibility tests for the frozen GitHub backlog migration adapter."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / ".ai/scripts/github_backlog_provider.py"
SPEC = importlib.util.spec_from_file_location("github_backlog_provider", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load provider module: {MODULE_PATH}")
PROVIDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROVIDER)
CONFIG = REPO_ROOT / ".dev/backlog/providers/github-legacy-migration.yaml"
ACTIVE_CONFIG = REPO_ROOT / ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml"


class HistoricalGitHubBacklogProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = PROVIDER.load_yaml_mapping(CONFIG)
        cls.plan = PROVIDER.build_plan(REPO_ROOT, CONFIG, "HEAD")
        cls.item_ids = [item["backlog_id"] for item in cls.plan["items"]]
        cls.items = {item["backlog_id"]: item for item in cls.plan["items"]}

    def test_gwt_001_given_canonical_backlog_when_projected_then_all_ids_are_unique(self) -> None:
        self.assertEqual(self.plan["counts"]["total"], len(self.item_ids))
        self.assertEqual(
            len(self.item_ids),
            len(self.items),
            f"duplicate backlog IDs in plan: {self.item_ids}",
        )

    def test_gwt_002_given_stage_a_when_planned_then_no_online_write_is_available(self) -> None:
        self.assertFalse(self.plan["online_writes_performed"])
        self.assertFalse(self.plan["stage_b_authorized"])

    def test_gwt_003_given_resolved_item_when_projected_then_it_closes_completed(self) -> None:
        item = self.items["AIC-007"]
        self.assertEqual("closed", item["issue"]["desired_state"])
        self.assertEqual("completed", item["issue"]["close_reason"])
        self.assertEqual("Done", item["project_fields"]["Status"])

    def test_gwt_004_given_declined_item_when_projected_then_it_closes_not_planned(self) -> None:
        item = self.items["UPG-001"]
        self.assertEqual("closed", item["issue"]["desired_state"])
        self.assertEqual("not planned", item["issue"]["close_reason"])
        self.assertIsNone(item["project_fields"]["Published in"])

    def test_gwt_005_given_open_item_when_projected_then_it_stays_open_inbox(self) -> None:
        item = self.items["DEVWF-001"]
        self.assertEqual("open", item["issue"]["desired_state"])
        self.assertEqual("Inbox", item["project_fields"]["Status"])
        self.assertEqual("Pending", item["project_fields"]["Owner review"])

    def test_gwt_006_given_source_repo_only_unpublished_item_then_publication_is_not_applicable(self) -> None:
        item = self.items["R042-005"]
        self.assertEqual("source-repo", item["classification"]["scope"])
        self.assertEqual(
            "Not applicable — source repository only",
            item["project_fields"]["Published in"],
        )

    def test_gwt_007_given_each_formal_issue_then_exactly_one_kind_and_scope_label_exist(self) -> None:
        for item in self.plan["items"]:
            labels = item["issue"]["labels"]
            self.assertEqual(1, sum(label.startswith("kind:") for label in labels))
            self.assertEqual(1, sum(label.startswith("scope:") for label in labels))

    def test_gwt_008_given_historical_issue_then_original_acceptance_and_markers_are_preserved(self) -> None:
        body = self.items["AIC-007"]["issue"]["body"]
        source = PROVIDER.load_yaml_mapping(REPO_ROOT / ".dev/backlog/items/CFG-001.yaml")
        body = self.items["CFG-001"]["issue"]["body"]
        for criterion in source["acceptance"]:
            self.assertIn(criterion, body)
        self.assertIn("<!-- canonical-backlog-id: CFG-001 -->", body)
        self.assertIn("<!-- migration-id: github-backlog-migration-2026-07 -->", body)

    def test_gwt_009_given_canaries_and_batches_then_every_item_appears_once(self) -> None:
        ordered = list(self.plan["canaries"])
        for batch in self.plan["remaining_batches"]:
            ordered.extend(batch)
        post_adoption = set(self.config["migration"]["post_adoption_backlog_ids"])
        expected_migration_ids = set(self.items) - post_adoption
        self.assertEqual(
            self.config["migration"]["expected_item_count"],
            len(ordered),
        )
        self.assertEqual(
            len(ordered),
            len(set(ordered)),
            f"duplicate migration backlog IDs: {ordered}",
        )
        self.assertEqual(expected_migration_ids, set(ordered))
        self.assertEqual(
            self.config["migration"]["remaining_batch_sizes"],
            [len(batch) for batch in self.plan["remaining_batches"]],
        )
        self.assertEqual(
            [
                "SKILL-002",
                "TOOL-002",
                "WIBIND-001",
                "GOV-004",
                "PKG-005",
                "EVAL-002",
                "VAL-002",
                "GOV-005",
                "CTX-004",
                "GOV-006",
                "CTX-005",
                "PKG-006",
                "VAL-003",
                "SAG-002",
            ],
            self.plan["post_adoption_items"],
        )

    def test_gwt_009a_given_post_adoption_items_when_projected_then_they_are_not_rewritten_into_the_completed_migration(self) -> None:
        skill_item = self.items["SKILL-002"]
        tool_item = self.items["TOOL-002"]
        binding_item = self.items["WIBIND-001"]

        self.assertEqual("enabler", skill_item["classification"]["kind"])
        self.assertEqual("story", tool_item["classification"]["kind"])
        self.assertEqual("enabler", binding_item["classification"]["kind"])
        for item in (skill_item, tool_item, binding_item):
            self.assertEqual("mixed", item["classification"]["scope"])
            self.assertEqual("v0.8.0", item["project_fields"]["Target release"])
            self.assertEqual("v0.8.0", item["project_fields"]["Published in"])

    def test_gwt_009b_given_v090_items_when_projected_then_each_appears_once_as_published(self) -> None:
        expected = {
            "CTX-004",
            "GOV-004",
            "PKG-005",
            "GOV-006",
            "CTX-005",
            "PKG-006",
            "SAG-002",
            "VAL-003",
        }
        projected = {
            backlog_id
            for backlog_id, item in self.items.items()
            if item["project_fields"]["Target release"] == "v0.9.0"
        }
        self.assertEqual(expected, projected)
        for backlog_id in expected:
            self.assertEqual("v0.9.0", self.items[backlog_id]["project_fields"]["Published in"])

    def test_gwt_010_given_same_revision_then_yaml_projection_is_deterministic(self) -> None:
        second = PROVIDER.build_plan(REPO_ROOT, CONFIG, self.plan["source_revision"])
        self.assertEqual(PROVIDER.dump_plan_yaml(self.plan), PROVIDER.dump_plan_yaml(second))

    def test_gwt_011_given_project_contract_then_only_approved_fields_views_and_automation_exist(self) -> None:
        config = PROVIDER.load_yaml_mapping(CONFIG)
        self.assertEqual(
            {"status", "priority", "owner_review", "target_release", "published_in"},
            set(config["fields"]),
        )
        self.assertEqual(
            ["Active Backlog", "Roadmap", "Owner Review", "History by Release"],
            [view["name"] for view in config["views"]],
        )
        expected_automation = {
            ("issue_opened_in_repository", "auto_add_to_project_and_initialize_status_inbox"),
            ("issue_closed", "set_status_done"),
        }
        actual_automation = [
            (entry["trigger"], entry["action"])
            for entry in config["automation"]["allowlist"]
        ]
        self.assertEqual(
            len(expected_automation),
            len(actual_automation),
            "automation allowlist must not contain duplicate or unapproved entries",
        )
        self.assertEqual(expected_automation, set(actual_automation))

    def test_gwt_012_given_public_intake_then_only_proposal_form_is_enabled(self) -> None:
        form = yaml.safe_load(
            (REPO_ROOT / ".github/ISSUE_TEMPLATE/proposal.yml").read_text(encoding="utf-8")
        )
        issue_config = yaml.safe_load(
            (REPO_ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(["kind:proposal"], form["labels"])
        self.assertFalse(issue_config["blank_issues_enabled"])

    def test_gwt_013_given_pr_template_then_it_requires_per_issue_disposition(self) -> None:
        template = (REPO_ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("Refs #", template)
        self.assertIn("terminal-close", template)
        self.assertIn("deferred", template)
        self.assertIn("closure_deferred_reason", template)
        self.assertIn("Next terminal gate or owner", template)

    def test_gwt_014_given_stage_b_receipt_then_every_recorded_mapping_is_verified_and_canonical(self) -> None:
        receipt = PROVIDER.load_yaml_mapping(
            REPO_ROOT / ".dev/backlog/provider-mappings/github-issues.yaml"
        )
        self.assertIn(receipt["stage"], {"stage-b-in-progress", "stage-b-read-back-complete"})
        self.assertEqual(
            "e83b759c8cf1deeb11af5ae748359f6a4c63b200",
            receipt["source_revision"],
        )
        mapped_ids = [item["backlog_id"] for item in receipt["items"]]
        self.assertTrue(
            {"DEVWF-001", "AIC-007", "R042-005", "UPG-001"}.issubset(mapped_ids)
        )
        self.assertEqual(len(mapped_ids), len(set(mapped_ids)))
        self.assertTrue(set(mapped_ids).issubset(self.items))
        self.assertTrue(all(item["read_back"]["labels_match"] for item in receipt["items"]))
        self.assertTrue(all(item["read_back"]["markers_match"] for item in receipt["items"]))
        if receipt["stage"] == "stage-b-read-back-complete":
            expected_migration_ids = set(self.items) - set(
                self.config["migration"]["post_adoption_backlog_ids"]
            )
            self.assertEqual(expected_migration_ids, set(mapped_ids))
            self.assertEqual(
                self.config["migration"]["expected_item_count"],
                len(mapped_ids),
            )
            self.assertIsNotNone(receipt["project"]["number"])

    def test_gwt_015_given_source_provider_tools_then_distribution_profile_excludes_them(self) -> None:
        profile = PROVIDER.load_yaml_mapping(
            REPO_ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"
        )
        excluded = {
            pattern
            for entry in profile["exclusions"]
            for pattern in entry.get("patterns", [])
        }
        self.assertTrue(
            {
                ".ai/scripts/github_backlog_provider.py",
                ".ai/scripts/plan-github-backlog-migration.py",
                ".ai/scripts/tests/test_github_backlog_provider.py",
            }.issubset(excluded)
        )

    def test_gwt_016_given_formal_issue_when_rendered_then_codex_label_and_hidden_marker_exist_once(self) -> None:
        marker = "<!-- created-by: OpenAI Codex (gpt-5.6-sol, max) <noreply@openai.com> -->"
        for item in self.plan["items"]:
            body = item["issue"]["body"]
            self.assertNotIn("## Creation Attribution", body)
            self.assertEqual(1, body.count(marker))
            self.assertEqual(1, item["issue"]["labels"].count("created-by:codex"))
            self.assertLess(body.index(marker), body.index("<!-- canonical-backlog-id:"))

    def test_gwt_017_given_proposal_creation_source_then_attribution_is_source_aware(self) -> None:
        form_text = (REPO_ROOT / ".github/ISSUE_TEMPLATE/proposal.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("created-by:codex", form_text)
        config = PROVIDER.load_yaml_mapping(CONFIG)
        proposal_policy = config["issue"]["creation_attribution"]["proposal_policy"]
        self.assertEqual(
            {
                "label_required": True,
                "hidden_marker_required": False,
                "application": "include the attribution label in the Issue creation request",
            },
            proposal_policy["ai_created"],
        )
        self.assertEqual(
            {
                "label_required": False,
                "hidden_marker_required": False,
                "application": "keep the public Proposal form attribution-neutral",
            },
            proposal_policy["human_submitted"],
        )

    def test_gwt_018_given_historical_adapter_then_original_exact_head_review_contract_is_preserved(self) -> None:
        config = PROVIDER.load_yaml_mapping(CONFIG)

        self.assertEqual(
            {
                "mode": "required",
                "purposes": ["traceability", "work-authorization"],
                "authorization": {
                    "requires_explicit_owner_approval": True,
                    "provider_state_alone_authorizes": False,
                    "missing_binding": "block material execution until an online GitHub Issue records the scope and explicit owner authorization",
                },
                "merge_gate": {
                    "mode": "required",
                    "disposition_required_per_issue": True,
                    "missing_binding_blocks_merge": True,
                    "review_gate": {
                        "mode": "single-maintainer-audit-receipt",
                        "maintainer_login": "YuChia-Wei",
                        "receipt_contract": "github-terminal-issue-closure-audit/v1",
                        "downstream_policy": "target-owned",
                    },
                    "required_check_contexts": [
                        "Read-only governance contract",
                        "Build and validate candidate",
                        "Ubuntu prerequisite contract",
                        "Windows prerequisite contract",
                        "Ubuntu PR profile gate",
                    ],
                },
            },
            config["work_item_binding"],
        )
        self.assertEqual(
            ["terminal-close", "deferred"],
            config["issue_closure"]["modes"],
        )
        self.assertEqual(
            "source-repository-only",
            config["issue_closure"]["distribution"],
        )

    def test_gwt_019_given_active_source_policy_then_v2_content_review_gate_is_required(self) -> None:
        config = PROVIDER.load_yaml_mapping(ACTIVE_CONFIG)

        self.assertEqual(
            {
                "mode": "single-maintainer-audit-receipt",
                "maintainer_login": "YuChia-Wei",
                "receipt_contract": "github-terminal-issue-closure-audit/v2",
                "legacy_receipt_contracts": ["github-terminal-issue-closure-audit/v1"],
                "binding_mode": "content-addressed-current-head",
                "downstream_policy": "target-owned",
            },
            config["work_item_binding"]["merge_gate"]["review_gate"],
        )


if __name__ == "__main__":
    unittest.main()
