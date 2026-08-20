#!/usr/bin/env python3
"""GWT lifecycle tests for semantic customization governance."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
import ai_context_target_provenance as TARGET  # noqa: E402
import ai_context_effective_rules as RULES  # noqa: E402


SOURCE_V060 = {
    "repository": "owner/framework",
    "release_id": "REL-v0.6.0",
    "version": "v0.6.0",
    "tag": "v0.6.0",
    "commit": "a" * 40,
}
SOURCE_V070 = {
    "repository": "owner/framework",
    "release_id": "REL-v0.7.0",
    "version": "v0.7.0",
    "tag": "v0.7.0",
    "commit": "b" * 40,
}
SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": [
        "software-development-core",
        "ai-context-lifecycle-core",
    ],
    "profiles": ["dotnet-backend"],
    "providers": {
        "repo-backlog": {
            "enabled": False,
            "preservation": "preserve-existing-if-recorded",
        }
    },
}
AT = "2026-07-24T08:00:00+08:00"


def valid_customization() -> dict:
    return {
        "id": "CUST-TEAM-001",
        "subject": {"kind": "contract", "id": "enterprise-test-execution"},
        "relationship": "deviates",
        "reason": "Enterprise execution controls change the framework test contract.",
        "paths": [".dev/operations/test-policy.md"],
        "base_framework": {
            "version": "v0.6.0",
            "commit": "a" * 40,
            "evidence": [".dev/ai-context/provenance.yaml#source"],
        },
        "dependencies": {"customization_ids": [], "subject_refs": []},
        "owner_reconciliation": {
            "status": "approved",
            "owner": "platform-team",
            "decided_at": "2026-07-24T08:10:00+08:00",
            "evidence": ".dev/workflows/customization/plan.md#approval",
        },
        "decision_evidence": {
            "requirements": [".dev/requirement/test-policy.md"],
            "adrs": [],
            "workflows": [".dev/workflows/customization/plan.md"],
        },
        "active_context_audit": {
            "assessment_id": "ASM-20260724-001",
            "status": "verified",
            "evidence": ".dev/assessments/ASM-20260724-001/report.md",
        },
        "incoming": {
            "version": "v0.7.0",
            "status": "equivalent-candidate",
            "evidence": ".dev/workflows/customization/equivalence.md",
        },
        "disposition": "merge",
        "post_upgrade_audit": {
            "assessment_id": "ASM-20260724-002",
            "status": "verified",
            "evidence": ".dev/assessments/ASM-20260724-002/report.md",
        },
        "validation": ["python .ai/scripts/validate-ai-context-target.py"],
    }


class SemanticCustomizationLifecycleTests(unittest.TestCase):
    def test_gwt_001_given_credible_init_and_verified_reconciliation_when_finalized_then_target_validates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-lifecycle-") as value:
            root = Path(value)
            initialized = TARGET.initialize_context(
                root, SOURCE_V060, SELECTION, AT
            )
            self.assertEqual("initialized", initialized["status"])

            provenance_path = root / ".dev/ai-context/provenance.yaml"
            ledger_path = root / ".dev/ai-context/customizations.yaml"
            provenance = TARGET.load_mapping(provenance_path, [])
            assert provenance is not None
            customization = valid_customization()
            customization["owner_reconciliation"] = {
                "status": "pending",
                "owner": "",
                "decided_at": None,
                "evidence": "",
            }
            customization["active_context_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            customization["incoming"] = {
                "version": "v0.7.0",
                "status": "absent",
                "evidence": ".dev/workflows/customization/equivalence.md",
            }
            customization["disposition"] = "unresolved"
            customization["post_upgrade_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            # Governance records semantic intent before paths are used for comparison.
            ledger = {
                "schema_version": "1.0",
                "customizations": [customization],
            }
            # The auditor records an independent active-context baseline.
            customization["active_context_audit"] = {
                "assessment_id": "ASM-20260724-001",
                "status": "verified",
                "evidence": ".dev/assessments/ASM-20260724-001/report.md",
            }
            # The upgrader records incoming equivalence.
            customization["incoming"]["status"] = "equivalent-candidate"
            # Governance records the explicit owner reconciliation.
            customization["owner_reconciliation"] = {
                "status": "approved",
                "owner": "platform-team",
                "decided_at": "2026-07-24T08:10:00+08:00",
                "evidence": ".dev/workflows/customization/plan.md#approval",
            }
            customization["disposition"] = "merge"
            # A separate auditor assessment verifies the post-upgrade active context.
            customization["post_upgrade_audit"] = {
                "assessment_id": "ASM-20260724-002",
                "status": "verified",
                "evidence": ".dev/assessments/ASM-20260724-002/report.md",
            }
            # This exercise finalizes reconciliation on an unchanged validated
            # source. A source advance is separately packet-gated below.
            upgraded = copy.deepcopy(provenance)

            # Target validation succeeds before provenance finalization.
            ledger_candidate = root / "ledger-candidate.yaml"
            ledger_candidate.write_text(
                __import__("yaml").safe_dump(ledger, sort_keys=False),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(ledger_candidate, errors)
            self.assertEqual([], errors)
            # Finalization publishes both validated documents.
            TARGET.finalize_context(root, upgraded, ledger)
            self.assertEqual([], TARGET.validate_target(root))
            self.assertIn(
                "CUST-TEAM-001", ledger_path.read_text(encoding="utf-8")
            )

    def test_gwt_001b_given_source_advance_without_a_sealed_remediation_packet_when_finalized_then_prior_provenance_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-upgrade-gate-") as value:
            root = Path(value)
            TARGET.initialize_context(root, SOURCE_V060, SELECTION, AT)
            provenance_path = root / ".dev/ai-context/provenance.yaml"
            before = provenance_path.read_bytes()
            candidate = TARGET.load_mapping(provenance_path, [])
            assert candidate is not None
            candidate["previous_source"] = candidate["source"]
            candidate["source"] = {
                "repository": "owner/framework",
                "release_id": "REL-v0.7.0",
                "version": "v0.7.0",
                "tag": "v0.7.0",
                "commit": "b" * 40,
            }
            candidate["installation"]["last_upgraded_at"] = AT
            candidate["last_migration"] = {
                "status": "completed",
                "from_version": "v0.6.0",
                "to_version": "v0.7.0",
                "completed_at": AT,
                "evidence": ".dev/assessments/ASM-20260724-002/report.md",
            }

            with self.assertRaisesRegex(
                TARGET.TargetValidationError,
                "upgrade finalization requires a finalized pending apply receipt",
            ):
                TARGET.finalize_context(
                    root,
                    candidate,
                    {"schema_version": "1.0", "customizations": []},
                )

            self.assertEqual(before, provenance_path.read_bytes())

    def test_gwt_002_given_failed_post_upgrade_verification_when_finalized_then_prior_provenance_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-rollback-") as value:
            root = Path(value)
            TARGET.initialize_context(root, SOURCE_V060, SELECTION, AT)
            provenance_path = root / ".dev/ai-context/provenance.yaml"
            before = provenance_path.read_bytes()
            provenance = TARGET.load_mapping(provenance_path, [])
            assert provenance is not None
            customization = valid_customization()
            customization["disposition"] = "retire"
            customization["post_upgrade_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            with self.assertRaises(TARGET.TargetValidationError):
                TARGET.finalize_context(
                    root,
                    provenance,
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                )
            self.assertEqual(before, provenance_path.read_bytes())

    def test_gwt_003_given_legacy_overrides_when_converted_then_each_becomes_one_unresolved_item_without_semantics(self) -> None:
        legacy = {
            "schema_version": "1.0",
            "local_overrides": [
                {
                    "id": "LOCAL-1",
                    "paths": [".ai/rule.md"],
                    "owner": "team",
                    "reason": "local policy",
                    "disposition": "preserve",
                },
                {
                    "id": "LOCAL-2",
                    "paths": [".dev/operations/runbook.md"],
                    "owner": "ops",
                    "reason": "operations truth",
                    "disposition": "preserve",
                },
            ],
        }
        unresolved = TARGET.legacy_override_reconciliation(legacy)
        self.assertEqual(2, len(unresolved))
        self.assertTrue(
            all(item["reason"] == "legacy-local-override" for item in unresolved)
        )
        self.assertTrue(all("subject" not in item for item in unresolved))

    def test_gwt_004_given_unproven_source_when_initialized_then_no_authority_is_written(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-unresolved-") as value:
            root = Path(value)
            result = TARGET.initialize_context(
                root, {"repository": "owner/framework"}, SELECTION, AT
            )
            self.assertEqual("unresolved", result["status"])
            self.assertFalse((root / ".dev/ai-context/provenance.yaml").exists())
            self.assertFalse(
                (root / ".dev/ai-context/customizations.yaml").exists()
            )

    def test_gwt_005_given_unsafe_path_or_missing_dependency_when_validated_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-invalid-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            customization["paths"] = [
                "../outside.md",
                "C:/outside.md",
                ".dev//operations/policy.md",
            ]
            customization["dependencies"]["customization_ids"] = ["CUST-MISSING"]
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors)
            self.assertTrue(any(".paths" in error for error in errors))
            self.assertTrue(any("missing customization dependency" in error for error in errors))

    def test_gwt_006_given_unfinalized_retirement_without_owner_approval_when_validated_then_it_still_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-retire-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            customization["disposition"] = "retire"
            customization["owner_reconciliation"] = {
                "status": "pending",
                "owner": "platform-team",
                "decided_at": None,
                "evidence": "",
            }
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors, require_finalized=False)
            self.assertTrue(
                any(
                    "requires approved owner reconciliation" in error
                    for error in errors
                )
            )

    def test_gwt_007_given_customization_reason_is_missing_when_validated_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-reason-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            del customization["reason"]
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors)
            self.assertTrue(any(".reason must be a non-empty string" in error for error in errors))

    def test_gwt_008_given_effective_publication_before_a_terminal_link_failure_when_finalization_aborts_then_prior_effective_bytes_are_restored(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-terminal-rollback-") as value:
            root = Path(value)
            TARGET.initialize_context(root, SOURCE_V060, SELECTION, AT)
            for relative in (
                ".ai/assets/shared/governance/engineering-rule-catalog.yaml",
                ".ai/assets/tech-stacks/dotnet-backend/engineering-rule-catalog.yaml",
            ):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / relative).read_bytes())

            provenance_path = root / ".dev/ai-context/provenance.yaml"
            ledger_path = root / ".dev/ai-context/customizations.yaml"
            provenance = TARGET.load_mapping(provenance_path, [])
            ledger = TARGET.load_mapping(ledger_path, [])
            assert provenance is not None and ledger is not None
            provenance["effective_rules"] = dict(TARGET.PROVENANCE_EFFECTIVE_RULES_LINKAGE)
            provenance_path.write_text(
                yaml.safe_dump(provenance, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            def effective_candidate(source: dict, selectors: list[dict]) -> dict:
                return {
                    "schema_version": "1.0",
                    "framework": {
                        "version": source["version"],
                        "commit": source["commit"],
                        "selected_technology_profile": "dotnet-backend",
                    },
                    "rule_dispositions": [
                        {
                            "rule_id": "AICTX-EVIDENCE-001",
                            "effective_disposition": "baseline-effective",
                            "applicability": "target uses repository discovery evidence",
                            "evidence": [".dev/workflows/customization/plan.md"],
                            "baseline_acceptance": {
                                "explicit": True,
                                "verification": {
                                    "status": "verified",
                                    "evidence": [".dev/workflows/customization/plan.md"],
                                },
                            },
                        },
                        {
                            "rule_id": "TEST-GWT-001",
                            "effective_disposition": "baseline-effective",
                            "applicability": "target test work uses GWT",
                            "evidence": [".dev/workflows/customization/plan.md"],
                            "baseline_acceptance": {
                                "explicit": True,
                                "verification": {
                                    "status": "verified",
                                    "evidence": [".dev/workflows/customization/plan.md"],
                                },
                            },
                        },
                    ],
                    "routing": [
                        {
                            "selector": selector,
                            "required_rule_ids": [
                                "AICTX-EVIDENCE-001",
                                "TEST-GWT-001",
                            ],
                            "reported_not_applicable_rule_ids": [],
                        }
                        for selector in selectors
                    ],
                }

            original_selector = {
                "capability": "local-change",
                "execution_mode": "remediation",
                "technology_profile": "dotnet-backend",
                "file_type": "python",
            }
            additional_selector = {
                **original_selector,
                "execution_mode": "terminal-recovery",
            }
            original_state, original_packets = TARGET.build_effective_state_and_packets(
                root,
                effective_candidate(SOURCE_V060, [original_selector]),
                resolver_evidence=[".dev/workflows/customization/plan.md"],
            )
            TARGET.write_effective_state_and_packets(root, original_state, original_packets)
            original_packet_path = root / next(iter(original_packets))
            state_path = root / TARGET.EFFECTIVE_STATE_PATH
            prior = {
                provenance_path: provenance_path.read_bytes(),
                ledger_path: ledger_path.read_bytes(),
                state_path: state_path.read_bytes(),
                original_packet_path: original_packet_path.read_bytes(),
            }

            upgraded_provenance = copy.deepcopy(provenance)
            upgraded_provenance["previous_source"] = copy.deepcopy(provenance["source"])
            upgraded_provenance["source"] = copy.deepcopy(SOURCE_V070)
            upgraded_provenance["installation"]["last_upgraded_at"] = AT
            upgraded_provenance["last_migration"] = {
                "status": "completed",
                "from_version": "v0.6.0",
                "to_version": "v0.7.0",
                "completed_at": AT,
                "evidence": ".dev/assessments/ASM-20260724-002/report.md",
            }
            additional_packet_path = (
                root
                / RULES.PACKET_DIRECTORY
                / f"{RULES.route_id_for_selector(additional_selector)}.yaml"
            )
            self.assertFalse(additional_packet_path.exists())

            with (
                mock.patch.object(
                    TARGET,
                    "validate_upgrade_finalization_evidence",
                    return_value={"authority_already_advanced": False},
                ),
                mock.patch.object(
                    TARGET,
                    "write_terminal_receipt",
                    return_value=(root / "terminal-receipt.json", "f" * 64, False),
                ),
                mock.patch.object(
                    TARGET,
                    "link_terminal_receipt_in_journal",
                    side_effect=TARGET.TargetValidationError("terminal journal link failed"),
                ),
            ):
                with self.assertRaisesRegex(
                    TARGET.TargetValidationError, "terminal journal link failed"
                ):
                    TARGET.finalize_context(
                        root,
                        upgraded_provenance,
                        ledger,
                        effective_state_candidate=effective_candidate(
                            SOURCE_V070,
                            [original_selector, additional_selector],
                        ),
                        effective_resolver_evidence=[
                            ".dev/workflows/customization/plan.md"
                        ],
                    )

            self.assertEqual(prior[provenance_path], provenance_path.read_bytes())
            self.assertEqual(prior[ledger_path], ledger_path.read_bytes())
            self.assertEqual(prior[state_path], state_path.read_bytes())
            self.assertEqual(
                prior[original_packet_path], original_packet_path.read_bytes()
            )
            self.assertFalse(additional_packet_path.exists())

    def test_gwt_009_given_an_absent_profile_when_an_upgrade_finalization_receipt_is_validated_then_it_requires_an_executable_profile_but_historical_validation_stays_compatible(self) -> None:
        profile = {
            "path": ".dev/project-config.yaml",
            "sha256": None,
            "argv": [],
            "snapshot": {"status": "absent"},
        }
        packet = {
            "target_validation_profile": profile,
            "target_validation_profile_digest": TARGET.canonical_json_digest(profile),
        }
        with tempfile.TemporaryDirectory(prefix="customization-profile-gate-") as value:
            root = Path(value)
            historical_errors: list[str] = []
            self.assertIsNotNone(
                TARGET.validate_target_validation_profile(
                    root,
                    packet,
                    historical_errors,
                    require_current_target=False,
                )
            )
            self.assertEqual([], historical_errors)

            finalization_errors: list[str] = []
            self.assertIsNone(
                TARGET.validate_target_validation_profile(
                    root,
                    packet,
                    finalization_errors,
                    require_executable_profile=True,
                )
            )
            self.assertIn(
                "upgrade finalization requires a present executable target validation profile",
                finalization_errors,
            )


if __name__ == "__main__":
    unittest.main()
