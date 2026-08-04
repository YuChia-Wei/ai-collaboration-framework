#!/usr/bin/env python3
"""GWT tests for the bundled mechanical-validation activation evaluator."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import yaml


PROVIDER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROVIDER_ROOT.parents[5]
EVALUATOR_PATH = PROVIDER_ROOT / "scripts/evaluate-provider-activation.py"
FIXTURE_PATH = PROVIDER_ROOT / "fixtures/controlled-reference-in-place/activation-record.yaml"
MANIFEST_PATH = PROVIDER_ROOT / "provider-manifest.yaml"
TARGET_PROJECT_PATH = PROVIDER_ROOT / "fixtures/controlled-reference-in-place/target/ControlledReferenceInPlace.csproj"


def load_evaluator() -> object:
    specification = importlib.util.spec_from_file_location("provider_activation_evaluator", EVALUATOR_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load provider activation evaluator")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


EVALUATOR = load_evaluator()


class ProviderActivationEvaluatorTests(unittest.TestCase):
    """Prove active claims require fresh, typed, file-backed evidence."""

    @staticmethod
    def load(path: Path) -> dict[str, object]:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise AssertionError(f"{path} must be a mapping")
        return value

    @staticmethod
    def activate(record: dict[str, object]) -> dict[str, object]:
        record["outcome"] = "active-reference-in-place"
        record["freshness"] = "fresh"
        capabilities = record["capabilities"]
        if not isinstance(capabilities, dict):
            raise AssertionError("fixture capabilities must be a mapping")
        for capability in capabilities.values():
            if not isinstance(capability, dict):
                raise AssertionError("fixture capability must be a mapping")
            capability["state"] = "active-reference-in-place"
        return record

    def evaluate_active(self, record: dict[str, object]) -> list[str]:
        return EVALUATOR.evaluate(
            record,
            self.load(MANIFEST_PATH),
            provider_manifest_bytes=MANIFEST_PATH.read_bytes(),
            repository_root=REPOSITORY_ROOT,
            provider_root=PROVIDER_ROOT,
        )

    def test_gwt_001_given_unresolved_controlled_fixture_when_evaluated_then_it_stays_unresolved_without_reading_evidence(self) -> None:
        record = self.load(FIXTURE_PATH)
        self.assertEqual([], EVALUATOR.evaluate(record, self.load(MANIFEST_PATH)))

    def test_gwt_002_given_controlled_target_when_read_then_it_references_both_provider_projects_in_place(self) -> None:
        project = TARGET_PROJECT_PATH.read_text(encoding="utf-8")
        self.assertIn("..\\..\\..\\analyzers\\DotnetBackendAnalyzers.csproj", project)
        self.assertIn("..\\..\\..\\runtime-validation\\DotnetBackendValidation.csproj", project)
        self.assertFalse((TARGET_PROJECT_PATH.parent / "DotnetBackendAnalyzers").exists())
        self.assertFalse((TARGET_PROJECT_PATH.parent / "DotnetBackendValidation").exists())

    def test_gwt_003_given_active_claim_without_verification_context_when_evaluated_then_it_fails_closed(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        errors = EVALUATOR.evaluate(record, self.load(MANIFEST_PATH))
        self.assertIn(
            "active-reference-in-place: verified evidence context requires repository_root, provider_root, and raw provider manifest bytes",
            errors,
        )

    def test_gwt_004_given_out_of_place_provider_root_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        errors = EVALUATOR.evaluate(
            record,
            self.load(MANIFEST_PATH),
            provider_manifest_bytes=MANIFEST_PATH.read_bytes(),
            repository_root=REPOSITORY_ROOT,
            provider_root=REPOSITORY_ROOT,
        )
        self.assertIn(
            "provider_root: must resolve to the canonical provider root under repository_root",
            errors,
        )

    def test_gwt_005_given_plan_only_evidence_when_marked_active_then_not_run_invocation_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        errors = self.evaluate_active(record)
        self.assertIn(
            "evidence[analyzers-invocation].status: must be one of ['passed'] for invocation",
            errors,
        )
        self.assertIn(
            "evidence[runtime-validation-invocation].status: must be one of ['passed'] for invocation",
            errors,
        )

    def test_gwt_006_given_mismatched_provider_manifest_digest_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        record["provider_manifest_sha256"] = "0" * 64
        self.assertIn(
            "provider_manifest_sha256: must match raw provider-manifest.yaml bytes",
            self.evaluate_active(record),
        )

    def test_gwt_007_given_mismatched_target_plan_digest_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        record["target_plan_sha256"] = "0" * 64
        self.assertIn(
            "target_plan_sha256: must match the deterministic target_plan digest",
            self.evaluate_active(record),
        )

    def test_gwt_008_given_mismatched_evidence_digest_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        evidence = record["evidence"]
        self.assertIsInstance(evidence, dict)
        records = evidence["records"]
        self.assertIsInstance(records, list)
        self.assertIsInstance(records[0], dict)
        records[0]["sha256"] = "0" * 64
        self.assertIn(
            "evidence[analyzers-wiring]: recorded sha256 does not match raw file bytes",
            self.evaluate_active(record),
        )

    def test_gwt_009_given_undeclared_evidence_reference_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        capabilities = record["capabilities"]
        self.assertIsInstance(capabilities, dict)
        analyzers = capabilities["analyzers"]
        self.assertIsInstance(analyzers, dict)
        evidence_ids = analyzers["evidence_ids"]
        self.assertIsInstance(evidence_ids, dict)
        evidence_ids["wiring"] = "missing-wiring"
        self.assertIn(
            "capabilities.analyzers.evidence_ids.wiring: evidence ID 'missing-wiring' is not declared",
            self.evaluate_active(record),
        )

    def test_gwt_010_given_mismatched_evidence_kind_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        capabilities = record["capabilities"]
        self.assertIsInstance(capabilities, dict)
        analyzers = capabilities["analyzers"]
        self.assertIsInstance(analyzers, dict)
        evidence_ids = analyzers["evidence_ids"]
        self.assertIsInstance(evidence_ids, dict)
        evidence_ids["wiring"] = "analyzers-configuration"
        self.assertIn(
            "evidence[analyzers-configuration].kind: must match the activation record",
            self.evaluate_active(record),
        )

    def test_gwt_011_given_unsafe_evidence_path_when_active_then_it_is_rejected(self) -> None:
        record = self.activate(copy.deepcopy(self.load(FIXTURE_PATH)))
        evidence = record["evidence"]
        self.assertIsInstance(evidence, dict)
        records = evidence["records"]
        self.assertIsInstance(records, list)
        self.assertIsInstance(records[0], dict)
        records[0]["path"] = "../outside.yaml"
        self.assertIn(
            "evidence[analyzers-wiring].path: must not contain empty, '.' or '..' path segments",
            self.evaluate_active(record),
        )

    def test_gwt_012_given_materialization_request_when_evaluated_then_it_fails_even_with_prerequisites(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        record["outcome"] = "active-materialized"
        target_plan = record["target_plan"]
        self.assertIsInstance(target_plan, dict)
        target_plan["activation_mode"] = "materialize-to-tools"
        target_plan["target_limitation_evidence"] = ["target limitation record"]
        target_plan["separate_authorization"] = "separate owner authorization"
        errors = EVALUATOR.evaluate(record, self.load(MANIFEST_PATH))
        self.assertIn(
            "active-materialized: unsupported because materialization implementation is unavailable",
            errors,
        )
        self.assertIn(
            "materialize-to-tools: unsupported because implementation is unavailable",
            errors,
        )

    def test_gwt_013_given_unexpected_nested_key_when_evaluated_then_it_fails_closed(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        capabilities = record["capabilities"]
        self.assertIsInstance(capabilities, dict)
        analyzers = capabilities["analyzers"]
        self.assertIsInstance(analyzers, dict)
        configuration = analyzers["configuration"]
        self.assertIsInstance(configuration, dict)
        configuration["unexpected"] = "value"
        errors = EVALUATOR.evaluate(record, self.load(MANIFEST_PATH))
        self.assertIn("capabilities.analyzers.configuration: unexpected keys ['unexpected']", errors)

    def test_gwt_014_given_manifest_project_path_drift_when_evaluated_then_it_fails_closed(self) -> None:
        manifest = copy.deepcopy(self.load(MANIFEST_PATH))
        capabilities = manifest["capabilities"]
        self.assertIsInstance(capabilities, dict)
        analyzers = capabilities["analyzers"]
        self.assertIsInstance(analyzers, dict)
        analyzers["project"] = "../../untrusted/DotnetBackendAnalyzers.csproj"
        errors = EVALUATOR.evaluate(self.load(FIXTURE_PATH), manifest)
        self.assertIn(
            "provider-manifest.capabilities.analyzers.project: "
            "must be 'analyzers/DotnetBackendAnalyzers.csproj'",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
