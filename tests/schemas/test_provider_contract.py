"""Consistency of the custom provider YAML baseline, not JSON Schema.

This twentieth source schema is declarative. No current production validator is
available for it. These source assertions check required fields/literals, digest
bindings and references only; they do not validate provider execution, readiness,
compatibility, target selection, or restore the removed Issue #205 helper.
"""
from hashlib import sha256
import json
import unittest

from schemas.schema_support import PROVIDER_ROOT, PROVIDER_SCHEMA, ROOT, document


def dotted(value, path):
    for key in path.split("."):
        value = value[key]
    return value


class ProviderContractConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = document(PROVIDER_SCHEMA)
        cls.contract = document(PROVIDER_ROOT + "/provider-contract.yaml")
        cls.template = document(PROVIDER_ROOT + "/templates/provider-selection.template.yaml")

    def assert_literals(self, value, literals):
        for path, expected in literals.items():
            with self.subTest(path=path):
                observed = dotted(value, path)
                self.assertEqual(type(observed), type(expected))
                self.assertEqual(observed, expected)

    def test_schema_identity_and_artifact_scope(self):
        self.assertEqual(self.schema["schema_version"], "1.0")
        self.assertEqual(self.schema["schema_id"], "dotnet-engineering-guardrails-provider-contract-schema")
        self.assertEqual(self.schema["applies_to"], ["provider-contract.yaml", "templates/provider-selection.template.yaml"])
        self.assertNotIn("$schema", self.schema)

    def test_contract_sections_match_declared_required_fields_and_literals(self):
        sections = {"contract": self.contract,
                    **{key: self.contract[key] for key in ["capability", "recommendation", "framework_delivery", "fallback", "state_semantics"]},
                    "canonical_provider_package_identity": self.contract["provider_package_identity"]}
        for name, value in sections.items():
            definition = self.schema[name]
            with self.subTest(section=name):
                self.assertLessEqual(set(definition["required_fields"]), value.keys())
                self.assert_literals(value, definition["required_literals"])
        self.assertEqual(self.contract["prohibitions"], self.schema["prohibitions"]["required_exact_values"])

    def test_state_names_and_each_typed_receipt_claim_match_schema(self):
        definition = self.schema["state_semantics"]
        states = self.contract["state_semantics"]["states"]
        self.assertEqual(set(states), set(definition["required_states"]))
        self.assertEqual(set(states), set(definition["state_requirements"]))
        for name, state in states.items():
            with self.subTest(state=name):
                self.assert_literals(state, definition["state_requirements"][name])
                for phase in ("readiness", "compatibility", "execution"):
                    self.assertIsNone(state[phase]["receipt"])
        synthetic = states["synthetic-readiness-proven"]
        self.assertEqual(synthetic["readiness"]["proof_scope"], "schema-transition-only")
        self.assertEqual(synthetic["execution"]["status"], "rejected")
        self.assertIs(synthetic["execution"]["required_real_receipt"], True)

    def test_receipt_kinds_fields_and_digest_references_are_distinct(self):
        definition = self.schema["evidence_receipt_contracts"]
        receipts = self.contract["evidence_receipt_contracts"]
        self.assertEqual(set(receipts), set(definition["required_kinds"]))
        types = []
        for name, receipt in receipts.items():
            with self.subTest(receipt=name):
                self.assertLessEqual(set(definition["required_receipt_fields"]), receipt.keys())
                self.assert_literals(receipt, definition["receipt_requirements"][name])
                self.assertLessEqual(set(definition["digest_required_fields"]), receipt["digest"].keys())
                self.assert_literals(receipt["digest"], definition["digest_literals"])
                fields = receipt["required_fields"]
                self.assertEqual(len(fields), len(set(fields)))
                self.assertIn(receipt["digest"]["field"], fields)
                types.append(receipt["receipt_type"])
        self.assertEqual(len(types), len(set(types)))
        synthetic_type = self.contract["state_semantics"]["states"]["synthetic-readiness-proven"]["readiness"]["receipt_type"]
        self.assertEqual(synthetic_type, receipts["readiness"]["receipt_type"])

    def test_template_preserves_unselected_null_and_empty_fields(self):
        definition = self.schema["provider_selection_template"]
        self.assertLessEqual(set(definition["required_fields"]), self.template.keys())
        self.assert_literals(self.template, definition["required_literals"])
        for path in definition["required_null_paths"]:
            with self.subTest(path=path):
                self.assertIsNone(dotted(self.template, path))
        for path in definition["required_empty_list_paths"]:
            with self.subTest(path=path):
                self.assertEqual(dotted(self.template, path), [])

    def test_baseline_digests_match_canonical_source_data(self):
        authority = self.schema["baseline_authority"]
        canonicalization = authority["canonicalization"]
        self.assertEqual(canonicalization["input"], "YAML-loaded document data")
        self.assertEqual(canonicalization["array_order"], "preserved")
        self.assertEqual(canonicalization["encoding"], "UTF-8")
        self.assertEqual(canonicalization["digest_algorithm"], "sha256")
        options = canonicalization["json_options"]
        for key, value in [("provider_contract_sha256", self.contract), ("provider_selection_template_sha256", self.template)]:
            raw = json.dumps(value, **options).encode("utf-8")
            with self.subTest(artifact=key):
                self.assertEqual(sha256(raw).hexdigest(), authority["artifact_digests"][key])

    def test_fallback_material_references_exist_in_source(self):
        directory = ROOT / PROVIDER_ROOT
        for relative in self.contract["fallback"]["materials"]:
            with self.subTest(material=relative):
                self.assertTrue((directory / relative).is_file())
        for key in ("analyzer_template", "analyzer_test_template", "code_fix_decision_template"):
            self.assertTrue((directory / "templates" / self.template["fallback"][key]).is_file())


if __name__ == "__main__":
    unittest.main()
