#!/usr/bin/env python3
"""GWT contract tests for the source-only GitHub backlog provider projection."""

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
CONFIG = REPO_ROOT / ".dev/backlog/providers/github.yaml"


class GitHubBacklogProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = PROVIDER.build_plan(REPO_ROOT, CONFIG, "HEAD")
        cls.items = {item["backlog_id"]: item for item in cls.plan["items"]}

    def test_gwt_001_given_canonical_backlog_when_projected_then_all_42_ids_are_unique(self) -> None:
        self.assertEqual(42, self.plan["counts"]["total"])
        self.assertEqual(42, len(self.items))

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
        self.assertEqual(41, len(ordered))
        self.assertEqual(set(self.items) - {"SKILL-002"}, set(ordered))
        self.assertEqual([10, 10, 10, 7], [len(batch) for batch in self.plan["remaining_batches"]])
        self.assertEqual(["SKILL-002"], self.plan["post_adoption_items"])

    def test_gwt_009a_given_post_adoption_item_when_projected_then_it_is_not_rewritten_into_the_completed_migration(self) -> None:
        item = self.items["SKILL-002"]

        self.assertEqual("enabler", item["classification"]["kind"])
        self.assertEqual("mixed", item["classification"]["scope"])
        self.assertEqual("v0.8.0", item["project_fields"]["Target release"])
        self.assertEqual("Not yet published", item["project_fields"]["Published in"])

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
        self.assertEqual(2, len(config["automation"]["allowlist"]))
        self.assertEqual(
            "auto_add_to_project_and_initialize_status_inbox",
            config["automation"]["allowlist"][0]["action"],
        )

    def test_gwt_012_given_public_intake_then_only_proposal_form_is_enabled(self) -> None:
        form = yaml.safe_load(
            (REPO_ROOT / ".github/ISSUE_TEMPLATE/proposal.yml").read_text(encoding="utf-8")
        )
        issue_config = yaml.safe_load(
            (REPO_ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(["kind:proposal"], form["labels"])
        self.assertFalse(issue_config["blank_issues_enabled"])

    def test_gwt_013_given_pr_template_then_it_references_but_never_auto_closes_issues(self) -> None:
        template = (REPO_ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("Refs #", template)
        for keyword in ("Closes #", "Fixes #", "Resolves #"):
            self.assertNotIn(keyword, template)

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
            self.assertEqual(41, len(mapped_ids))
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
        marker = "<!-- created-by: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com> -->"
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


if __name__ == "__main__":
    unittest.main()
