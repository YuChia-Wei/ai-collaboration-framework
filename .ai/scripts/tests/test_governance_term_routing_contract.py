#!/usr/bin/env python3
"""Fail-closed contracts for qualified governance terms and release projections."""

from __future__ import annotations

import copy
import runpy
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402


REGISTRY_PATH = Path(".dev/standards/AI-CONTEXT-OWNERSHIP.yaml")
SOURCE_RELEASE_POLICY = Path(
    ".dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md"
)
SOURCE_VERSION_ROUTER = Path(".dev/standards/AI-CONTEXT-VERSION-POLICY.md")
PORTABLE_VERSION_POLICY = Path(
    ".ai/assets/shared/governance/AI-CONTEXT-VERSION-POLICY.md"
)
PROFILE_PATH = Path(".ai/distribution/profiles/dotnet-backend.yaml")
PROJECTION_MANIFEST = Path(
    ".ai/assets/shared/governance/portable-policy-manifest.yaml"
)

EXPECTED_TERM_IDS = {
    "source-release.framework-version-candidate",
    "distribution.package-candidate",
    "target-upgrade.automatic-candidate",
    "source-release.release-source-status-validated",
    "git.repository-integration",
    "workflow.workflow-completion",
    "assessment.assessment-final",
    "hosted-release.hosted-publication",
    "source-release-validation.candidate-phase",
    "source-release-validation.tag-phase",
    "source-release-validation.publication-phase",
    "source-release-validation.finalization-phase",
    "source-release.historical-exception-closeout",
    "governance.subject-lifecycle",
    "capability-selection.subject-candidate",
}

SOURCE_ONLY_TERM_IDS = {
    "source-release.framework-version-candidate",
    "distribution.package-candidate",
    "source-release.release-source-status-validated",
    "hosted-release.hosted-publication",
    "source-release-validation.candidate-phase",
    "source-release-validation.tag-phase",
    "source-release-validation.publication-phase",
    "source-release-validation.finalization-phase",
    "source-release.historical-exception-closeout",
}

FORBIDDEN_PORTABLE_RELEASE_ACTIONS = {
    ".dev/releases/",
    "prepare-ai-context-release.py",
    "validate-ai-context-release-state.py",
    "reconcile-ai-context-release-provider.py",
    "render-ai-context-release-notes.py",
    "release-phase-checks.yaml",
    ".github/workflows",
    "Project credential",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def term_map() -> dict[str, dict]:
    terms = load_yaml(REGISTRY_PATH)["governance_term_routing"]["terms"]
    return {term["term_id"]: term for term in terms}


class GovernanceTermRoutingContractTests(unittest.TestCase):
    def test_gwt_001_given_active_inventory_when_loaded_then_qualified_routes_are_complete(self) -> None:
        routing = load_yaml(REGISTRY_PATH)["governance_term_routing"]
        terms = term_map()
        self.assertEqual("1.0", routing["schema_version"])
        self.assertEqual(
            "owner-route-index-not-definition-authority",
            routing["registry_role"],
        )
        self.assertEqual(EXPECTED_TERM_IDS, set(terms))
        self.assertEqual(
            SOURCE_ONLY_TERM_IDS,
            {
                term_id
                for term_id, term in terms.items()
                if term["distribution"] == "source-only"
            },
        )

    def test_gwt_002_given_owner_routes_when_resolved_then_each_definition_is_exact_and_context_bounded(self) -> None:
        for term_id, term in term_map().items():
            with self.subTest(term_id=term_id):
                owner = term["canonical_owner"]
                owner_text = (ROOT / owner["path"]).read_text(encoding="utf-8")
                self.assertIn(owner["anchor"], owner_text)
                self.assertTrue(term["namespace"])
                self.assertTrue(term["qualified_term"])
                self.assertTrue(term["contextual_shorthand"]["aliases"])
                self.assertTrue(term["contextual_shorthand"]["allowed_scope"])
                self.assertTrue(
                    term["contextual_shorthand"]["forbidden_authority_claims"]
                )
                expected = (
                    "available"
                    if term["distribution"] == "portable"
                    else "upstream-only-non-actionable"
                )
                self.assertEqual(expected, term["portable_disposition"])

    def test_gwt_003_given_machine_contracts_when_qualified_then_literals_are_preserved(self) -> None:
        terms = term_map()
        self.assertEqual(
            {"planned", "validated", "published", "superseded"},
            set(
                terms["source-release.release-source-status-validated"][
                    "machine_bindings"
                ][0]["literals"]
            ),
        )
        self.assertEqual(
            {"automatic-candidate", "reconcile", "exclude"},
            set(
                terms["target-upgrade.automatic-candidate"]["machine_bindings"][0][
                    "literals"
                ]
            ),
        )
        handoff = load_yaml(Path(".dev/standards/WORKFLOW-HANDOFF-POLICY.yaml"))
        self.assertEqual(
            ["candidate", "tag", "publication", "finalization"],
            handoff["release_phases"],
        )
        self.assertEqual(
            "validation-phase",
            handoff["release_phase_semantics"]["kind"],
        )
        release_phase_checks = load_yaml(
            Path(".dev/releases/v0.12.0/release-phase-checks.yaml")
        )
        self.assertEqual(
            {"candidate", "tag", "publication", "finalization"},
            set(release_phase_checks["phases"]),
        )
        for term_id in (
            "source-release-validation.candidate-phase",
            "source-release-validation.tag-phase",
            "source-release-validation.publication-phase",
            "source-release-validation.finalization-phase",
        ):
            with self.subTest(term_id=term_id):
                self.assertEqual(
                    "phases",
                    terms[term_id]["machine_bindings"][0]["field"],
                )

    def test_gwt_004_given_malformed_term_when_validated_then_registry_fails_closed(self) -> None:
        validator = runpy.run_path(
            str(SCRIPTS / "validate-ai-context.py"),
            run_name="governance_term_contract_validator",
        )
        data = copy.deepcopy(load_yaml(REGISTRY_PATH))
        del data["governance_term_routing"]["terms"][0]["namespace"]
        errors: list[str] = []
        validator["validate_governance_term_routing_data"](
            data,
            errors,
            root=ROOT,
            source_context=True,
        )
        self.assertTrue(any("namespace must be a non-empty string" in item for item in errors))

    def test_gwt_005_given_source_and_target_policies_when_read_then_authority_is_separated(self) -> None:
        source_policy = (ROOT / SOURCE_RELEASE_POLICY).read_text(encoding="utf-8")
        portable_policy = (ROOT / PORTABLE_VERSION_POLICY).read_text(
            encoding="utf-8"
        )
        source_router = (ROOT / SOURCE_VERSION_ROUTER).read_text(encoding="utf-8")
        scripts_readme = (ROOT / ".ai/scripts/README.md").read_text(encoding="utf-8")

        self.assertIn("## Source Release Validation Phases", source_policy)
        self.assertIn("prepare-ai-context-release.py", source_policy)
        self.assertIn("AI-CONTEXT-SOURCE-RELEASE-POLICY.md", source_router)
        self.assertIn(".dev/ai-context/provenance.yaml", portable_policy)
        self.assertIn(".dev/ai-context/customizations.yaml", portable_policy)
        self.assertIn(".dev/AI-CONTEXT-SOURCE.yaml", portable_policy)
        for forbidden in FORBIDDEN_PORTABLE_RELEASE_ACTIONS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, portable_policy)
                self.assertNotIn(forbidden, scripts_readme)

    def test_gwt_006_given_owner_policies_when_read_then_cross_owner_completion_is_disallowed(self) -> None:
        expectations = {
            ".dev/TEAM-GIT-FLOW-RULES.MD": "Repository integration is the reviewed Git event",
            ".dev/standards/WORKFLOW-ARTIFACT-POLICY.md": "## Workflow Completion",
            ".dev/standards/ASSESSMENT-ARTIFACT-POLICY.md": "means assessment final",
            ".dev/standards/WORKFLOW-HANDOFF-POLICY.md": "They select REL-owned validation phases",
            ".dev/standards/AI-CONTEXT-OWNERSHIP.md": "## Governance Term Routing",
        }
        for path, expected in expectations.items():
            with self.subTest(path=path):
                self.assertIn(
                    expected,
                    (ROOT / path).read_text(encoding="utf-8"),
                )

    def test_gwt_007_given_distribution_profile_when_read_then_source_policy_is_excluded_and_target_policy_is_mapped(self) -> None:
        profile = load_yaml(PROFILE_PATH)
        source_release = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "source-release-governance"
        )
        self.assertEqual(
            {
                ".dev/standards/AI-CONTEXT-VERSION-POLICY.md",
                ".dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md",
            },
            set(source_release["patterns"]),
        )
        mapping = next(
            item
            for item in load_yaml(PROJECTION_MANIFEST)["mappings"]
            if item["source"] == "AI-CONTEXT-VERSION-POLICY.md"
        )
        self.assertEqual(
            ".dev/standards/AI-CONTEXT-VERSION-POLICY.md",
            mapping["target"],
        )
        self.assertNotIn("component_id", mapping)
        projection_entry = next(
            item
            for item in profile["entries"]
            if item["id"] == "portable-governance-policy-projections"
        )
        component_ids = {
            item["component_id"] for item in profile["components"]
        }
        self.assertEqual(
            "ai-context-lifecycle-core",
            PACKAGE.resolve_entry_component(
                projection_entry,
                PORTABLE_VERSION_POLICY.as_posix(),
                projection_entry["component_id"],
                component_ids,
            ),
        )

    def test_gwt_008_given_committed_profile_when_projected_then_only_portable_version_policy_ships(self) -> None:
        tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile = load_yaml(PROFILE_PATH)
        payload = {
            item.path: item
            for item in PACKAGE.collect_payload(ROOT, tree, profile)
        }
        target = ".dev/standards/AI-CONTEXT-VERSION-POLICY.md"
        self.assertIn(target, payload)
        self.assertEqual(
            (ROOT / PORTABLE_VERSION_POLICY).read_bytes(),
            payload[target].content,
        )
        self.assertNotIn(
            ".dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md",
            payload,
        )
        self.assertNotEqual(
            (ROOT / SOURCE_VERSION_ROUTER).read_bytes(),
            payload[target].content,
        )


if __name__ == "__main__":
    unittest.main()
