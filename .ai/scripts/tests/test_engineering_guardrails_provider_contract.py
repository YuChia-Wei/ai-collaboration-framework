#!/usr/bin/env python3
"""GWT contracts for the optional Engineering Guardrails provider binding."""

from __future__ import annotations

from copy import deepcopy
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
RECIPE_ROOT = REPO_ROOT / (
    ".ai/assets/tech-stacks/dotnet-backend/tooling/"
    "on-demand-mechanical-validation"
)
CONTRACT_PATH = RECIPE_ROOT / "provider-contract.yaml"
SCHEMA_PATH = RECIPE_ROOT / "provider-contract.schema.yaml"
SELECTION_TEMPLATE_PATH = RECIPE_ROOT / "templates/provider-selection.template.yaml"
ANALYZER_TEMPLATE_PATH = RECIPE_ROOT / "templates/minimal-diagnostic-analyzer.cs.template"
ANALYZER_TEST_TEMPLATE_PATH = (
    RECIPE_ROOT / "templates/minimal-diagnostic-analyzer-test.cs.template"
)
CODE_FIX_TEMPLATE_PATH = RECIPE_ROOT / "templates/code-fix-decision.md"
README_PATH = RECIPE_ROOT / "README.md"
MANIFEST_PATH = RECIPE_ROOT / "recipe-manifest.yaml"
RECIPE_PATH = RECIPE_ROOT / "recipes/analyzer-project.md"


def load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError(f"{path.relative_to(REPO_ROOT)} must contain a mapping")
    return loaded


def nested_value(document: dict, dotted_path: str) -> object:
    current: object = document
    for segment in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current


def contract_errors(contract: dict, schema: dict) -> list[str]:
    """Validate the shipped reference contract without simulating a provider."""
    errors: list[str] = []
    contract_rules = schema["contract"]
    for field in contract_rules["required_fields"]:
        if field not in contract:
            errors.append(f"contract is missing required field: {field}")
    for field, expected in contract_rules["required_literals"].items():
        if contract.get(field) != expected:
            errors.append(f"contract.{field} must be {expected!r}")

    capability = contract.get("capability", {})
    for field in schema["capability"]["required_fields"]:
        if not capability.get(field):
            errors.append(f"capability.{field} must be non-empty")
    if schema["capability"]["package_identity_independent"] and any(
        term in str(capability.get("id", "")).lower()
        for term in ("nuget", "package", "version", "feed")
    ):
        errors.append("capability.id must not depend on provider package identity")

    recommendation = contract.get("recommendation", {})
    for field, expected in schema["recommendation"]["required_literals"].items():
        if recommendation.get(field) != expected:
            errors.append(f"recommendation.{field} must be {expected!r}")

    package_identity = contract.get("provider_package_identity", {})
    package_rules = schema["canonical_provider_package_identity"]
    for field in package_rules["required_fields"]:
        if field not in package_identity:
            errors.append(f"provider_package_identity is missing required field: {field}")
    for field, expected in package_rules["required_literals"].items():
        if package_identity.get(field) != expected:
            errors.append(f"provider_package_identity.{field} must be {expected!r}")
    for field in package_rules["required_null_fields"]:
        if package_identity.get(field) is not None:
            errors.append(f"canonical provider_package_identity.{field} must remain null")

    states = contract.get("state_semantics", {}).get("states", {})
    state_rules = schema["state_semantics"]
    for state in state_rules["required_states"]:
        if state not in states:
            errors.append(f"state_semantics.states is missing required state: {state}")
            continue
        for dotted_path, expected in state_rules["state_requirements"][state].items():
            actual = nested_value(states[state], dotted_path)
            if actual != expected:
                errors.append(
                    f"{state}.{dotted_path} must be {expected!r}, found {actual!r}"
                )

    receipt_contracts = contract.get("evidence_receipt_contracts", {})
    receipt_rules = schema["evidence_receipt_contracts"]
    receipt_types: list[str] = []
    for kind in receipt_rules["required_kinds"]:
        record = receipt_contracts.get(kind)
        if not isinstance(record, dict):
            errors.append(f"missing {kind} receipt contract")
            continue
        for field in receipt_rules["required_receipt_fields"]:
            if field not in record:
                errors.append(f"{kind} receipt contract is missing field: {field}")
        digest = record.get("digest", {})
        for field, expected in receipt_rules["digest_literals"].items():
            if digest.get(field) != expected:
                errors.append(f"{kind} receipt digest.{field} must be {expected!r}")
        receipt_type = record.get("receipt_type")
        if not isinstance(receipt_type, str) or not receipt_type:
            errors.append(f"{kind} receipt_type must be non-empty")
        else:
            receipt_types.append(receipt_type)
        if "receipt_sha256" not in record.get("required_fields", []):
            errors.append(f"{kind} receipt contract must require receipt_sha256")
    if len(receipt_types) != len(set(receipt_types)):
        errors.append("readiness, compatibility, and execution receipt types must differ")

    return errors


class EngineeringGuardrailsProviderContractGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_yaml(CONTRACT_PATH)
        cls.schema = load_yaml(SCHEMA_PATH)
        cls.selection_template = load_yaml(SELECTION_TEMPLATE_PATH)

    def test_gwt_001_given_the_shipped_contract_when_checked_then_the_unavailable_provider_states_are_complete(self) -> None:
        self.assertEqual([], contract_errors(self.contract, self.schema))
        self.assertEqual(
            "not-selected", self.contract["state_semantics"]["default_state"]
        )
        self.assertFalse(self.contract["framework_delivery"]["supplied_executable"])
        self.assertFalse(self.contract["framework_delivery"]["supplied_readiness_receipt"])
        self.assertFalse(self.contract["framework_delivery"]["supplied_compatibility_receipt"])
        self.assertFalse(self.contract["framework_delivery"]["supplied_execution_receipt"])

    def test_gwt_002_given_invented_identity_or_synthetic_execution_claim_when_checked_then_it_fails_closed(self) -> None:
        with self.subTest("invented provider package identity"):
            candidate = deepcopy(self.contract)
            candidate["provider_package_identity"]["nuget_id"] = "Invented.Provider"
            errors = contract_errors(candidate, self.schema)
            self.assertIn(
                "canonical provider_package_identity.nuget_id must remain null", errors
            )

        with self.subTest("synthetic readiness cannot become real execution"):
            candidate = deepcopy(self.contract)
            candidate["state_semantics"]["states"]["synthetic-readiness-proven"][
                "execution"
            ]["status"] = "proven"
            errors = contract_errors(candidate, self.schema)
            self.assertTrue(
                any(
                    error.startswith("synthetic-readiness-proven.execution.status")
                    for error in errors
                ),
                errors,
            )

    def test_gwt_003_given_the_selection_template_when_checked_then_it_starts_target_owned_and_not_selected(self) -> None:
        template_rules = self.schema["provider_selection_template"]
        for field in template_rules["required_fields"]:
            self.assertIn(field, self.selection_template)
        for dotted_path, expected in template_rules["required_literals"].items():
            self.assertEqual(expected, nested_value(self.selection_template, dotted_path))
        for dotted_path in template_rules["required_null_paths"]:
            self.assertIsNone(nested_value(self.selection_template, dotted_path))
        self.assertEqual([], self.selection_template["selection"]["selected_diagnostic_subset"])
        self.assertTrue(self.selection_template["execution"]["required_real_receipt"])

    def test_gwt_004_given_the_starting_templates_when_read_then_they_remain_reference_only_and_target_owned(self) -> None:
        source_templates = (
            ANALYZER_TEMPLATE_PATH,
            ANALYZER_TEST_TEMPLATE_PATH,
            CODE_FIX_TEMPLATE_PATH,
        )
        forbidden = (
            ".csproj",
            ".sln",
            ".slnx",
            "global.json",
            "packagereference",
            "dotnet ",
        )
        for path in source_templates:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("reference-only", content.lower())
                self.assertIn("target-owned after copy", content.lower())
                self.assertFalse(
                    any(fragment in content.lower() for fragment in forbidden), path
                )

        analyzer = ANALYZER_TEMPLATE_PATH.read_text(encoding="utf-8")
        analyzer_test = ANALYZER_TEST_TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn("DiagnosticAnalyzer", analyzer)
        self.assertIn("DiagnosticDescriptor", analyzer)
        self.assertIn("GivenTargetSource", analyzer_test)
        self.assertIn("WhenAnalyzerRuns", analyzer_test)
        self.assertIn("ThenExpectedDiagnosticIsObserved", analyzer_test)

    def test_gwt_005_given_recipe_material_when_read_then_contract_fallback_and_documentation_agree(self) -> None:
        manifest = load_yaml(MANIFEST_PATH)
        expected_paths = {
            "provider_contract": "provider-contract.yaml",
            "provider_contract_schema": "provider-contract.schema.yaml",
            "provider_selection_template": "templates/provider-selection.template.yaml",
            "minimal_diagnostic_analyzer_template": "templates/minimal-diagnostic-analyzer.cs.template",
            "minimal_diagnostic_analyzer_test_template": "templates/minimal-diagnostic-analyzer-test.cs.template",
            "code_fix_decision_template": "templates/code-fix-decision.md",
        }
        self.assertEqual("reference-only", manifest["delivery_state"])
        self.assertEqual("not-selected", manifest["default_selection_state"])
        self.assertEqual("official-recommended", manifest["provider_contract"]["recommendation_status"])
        self.assertEqual("unknown", manifest["provider_contract"]["canonical_provider_package_identity"])
        self.assertEqual("real-provider-unavailable", manifest["provider_contract"]["framework_delivery"])
        for material, path in expected_paths.items():
            self.assertEqual(path, manifest["materials"][material]["path"])
            self.assertEqual("reference-only", manifest["materials"][material]["evidence_tier"])

        readme = README_PATH.read_text(encoding="utf-8")
        recipe = RECIPE_PATH.read_text(encoding="utf-8")
        for state in self.schema["state_semantics"]["required_states"]:
            self.assertIn(f"`{state}`", readme)
            self.assertIn(f"`{state}`", recipe)
        self.assertIn("separate types and", readme)
        self.assertIn("separately typed and digested", recipe)


if __name__ == "__main__":
    unittest.main()
