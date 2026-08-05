#!/usr/bin/env python3
"""Source-only GWT coverage for the Architecture Kit readiness evaluator."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


PROVIDER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROVIDER_ROOT.parents[5]
EVALUATOR_PATH = PROVIDER_ROOT / "scripts/evaluate-architecture-kit-readiness.py"
FIXTURE_PATH = PROVIDER_ROOT / "fixtures/architecture-kit-unavailable/readiness-record.yaml"
MANIFEST_PATH = PROVIDER_ROOT / "provider-manifest.yaml"


def load_evaluator() -> object:
    specification = importlib.util.spec_from_file_location("architecture_kit_readiness_evaluator", EVALUATOR_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load Architecture Kit readiness evaluator")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


EVALUATOR = load_evaluator()


class ArchitectureKitReadinessEvaluatorTests(unittest.TestCase):
    """Prove readiness evidence never becomes selection or execution authority."""

    @staticmethod
    def load(path: Path) -> dict[str, object]:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise AssertionError(f"{path} must be a mapping")
        return value

    def evaluate(self, record: dict[str, object], manifest: dict[str, object] | None = None) -> dict[str, object]:
        return EVALUATOR.evaluate(
            record,
            self.load(MANIFEST_PATH) if manifest is None else manifest,
            provider_manifest_bytes=MANIFEST_PATH.read_bytes(),
            repository_root=REPOSITORY_ROOT,
            provider_root=PROVIDER_ROOT,
        )

    @staticmethod
    def payload(criterion: str, record: dict[str, object]) -> dict[str, object]:
        package = record["architecture_kit"]
        if criterion == "immutable_package_identity":
            return {"package_id": package["package_id"], "package_version": package["package_version"], "package_digest": "a" * 64, "publication_reference": "synthetic://publication"}
        if criterion == "diagnostic_constraint_crosswalk":
            return {"bindings": [{"diagnostic_id": "AK1001", "constraint_id": "CONSTRAINT-TEST"}], "unmapped_diagnostics": []}
        if criterion == "behavior_parity":
            return {"scenarios": [{"scenario_id": "synthetic-parity", "result": "passed"}], "failed_scenarios": [], "mismatched_scenarios": [], "equivalence": "equivalent"}
        if criterion == "consumer_guidance":
            return {"guidance_reference": "synthetic://guidance", "guidance_digest": "b" * 64}
        if criterion == "compatible_profile_range":
            return {"profile": "dotnet-backend", "compatibility_range": ">=1.0 <2.0"}
        if criterion == "real_target_proof":
            return {"target_identity": "synthetic-target", "target_commit": "1" * 40, "invocation": "synthetic invocation", "result": "passed"}
        if criterion == "migration_rollback_proof":
            return {"migration": {"plan_reference": "synthetic://migration", "result": "passed"}, "rollback": {"plan_reference": "synthetic://rollback", "result": "passed"}}
        if criterion == "owner_cutover_approval":
            return {"decision_reference": "synthetic://readiness-decision", "decision_digest": "c" * 64, "scope": "readiness-gate", "execution_authorization": False}
        raise AssertionError(f"unexpected criterion {criterion}")

    def prepare_verified_evidence(self, record: dict[str, object], root: Path, verified: set[str]) -> None:
        package = record["architecture_kit"]
        package["package_id"] = "Example.ArchitectureKit"
        package["package_version"] = "1.0.0"
        package["package_version_status"] = "available"
        record["evidence"]["root"] = root.relative_to(REPOSITORY_ROOT).as_posix()
        binding = record["provider_binding"]
        records: list[dict[str, str]] = []
        for criterion in record["criteria"]:
            identifier = criterion["id"]
            if identifier not in verified:
                continue
            criterion["state"] = "verified"
            evidence_id = f"{identifier}-proof"
            criterion["evidence_ids"] = [evidence_id]
            metadata = {
                "schema_version": "1.0",
                "evidence_id": evidence_id,
                "provider_id": "ai-context-dotnet-bundled-mechanical-validation",
                "framework_version": binding["framework_version"],
                "framework_commit": binding["framework_commit"],
                "provider_manifest_sha256": binding["provider_manifest_sha256"],
                "criterion": identifier,
                "status": "verified",
                "payload": self.payload(identifier, record),
            }
            raw = yaml.safe_dump(metadata, sort_keys=True).encode("utf-8")
            path = root / f"{evidence_id}.yaml"
            path.write_bytes(raw)
            records.append({"id": evidence_id, "path": path.name, "sha256": hashlib.sha256(raw).hexdigest()})
        record["evidence"]["records"] = records

    def test_gwt_001_given_current_unavailable_fixture_when_evaluated_then_it_is_valid_but_gate_fails_closed(self) -> None:
        result = self.evaluate(self.load(FIXTURE_PATH))
        self.assertTrue(result["valid"])
        self.assertEqual("unsupported", result["readiness"])
        self.assertEqual("unavailable", result["availability"])
        self.assertFalse(result["selectable"])
        self.assertEqual(1, EVALUATOR.exit_code(result))

    def test_gwt_002_given_missing_duplicate_or_unknown_criterion_when_evaluated_then_it_fails_closed(self) -> None:
        missing = copy.deepcopy(self.load(FIXTURE_PATH))
        missing["criteria"].pop()
        self.assertIn("criteria: missing required criteria ['owner_cutover_approval']", self.evaluate(missing)["errors"])
        duplicate = copy.deepcopy(self.load(FIXTURE_PATH))
        duplicate["criteria"].append(copy.deepcopy(duplicate["criteria"][0]))
        self.assertIn("criteria[9].id: duplicate criterion 'immutable_package_identity'", self.evaluate(duplicate)["errors"])
        unknown = copy.deepcopy(self.load(FIXTURE_PATH))
        unknown["criteria"][0]["id"] = "unknown-proof"
        self.assertIn("criteria[1].id: unknown criterion 'unknown-proof'", self.evaluate(unknown)["errors"])

    def test_gwt_003_given_mixed_verified_criterion_with_bad_sha_when_evaluated_then_it_verifies_that_evidence_immediately(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            self.prepare_verified_evidence(record, Path(temporary), {"immutable_package_identity"})
            record["evidence"]["records"][0]["sha256"] = "0" * 64
            result = self.evaluate(record)
        self.assertFalse(result["valid"])
        self.assertIn("evidence[immutable_package_identity-proof]: recorded sha256 does not match raw file bytes", result["errors"])

    def test_gwt_004_given_unsafe_evidence_root_or_path_when_evaluated_then_it_fails_closed(self) -> None:
        unsupported_root_escape = copy.deepcopy(self.load(FIXTURE_PATH))
        unsupported_root_escape["evidence"]["root"] = "../escape"
        self.assertIn(
            "evidence.root: must not contain empty, '.' or '..' path segments",
            self.evaluate(unsupported_root_escape)["errors"],
        )
        root_escape = copy.deepcopy(self.load(FIXTURE_PATH))
        root_escape["criteria"][0]["state"] = "verified"
        root_escape["criteria"][0]["evidence_ids"] = ["proof"]
        root_escape["evidence"]["root"] = "../escape"
        root_escape["evidence"]["records"] = [{"id": "proof", "path": "proof.yaml", "sha256": "0" * 64}]
        self.assertIn("evidence.root: must not contain empty, '.' or '..' path segments", self.evaluate(root_escape)["errors"])
        path_escape = copy.deepcopy(root_escape)
        path_escape["evidence"]["root"] = "fixtures/architecture-kit-unavailable"
        path_escape["evidence"]["records"][0]["path"] = "../escape.yaml"
        self.assertIn("evidence.records[1].path: must not contain empty, '.' or '..' path segments", self.evaluate(path_escape)["errors"])

    @unittest.skipUnless(hasattr(os, "symlink"), "platform does not expose symlink creation")
    def test_gwt_005_given_symlinked_evidence_root_when_evaluated_then_it_fails_closed(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            link = root / "link"
            try:
                os.symlink(root, link, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            self.prepare_verified_evidence(record, root, {"immutable_package_identity"})
            record["evidence"]["root"] = link.relative_to(REPOSITORY_ROOT).as_posix()
            self.assertIn("evidence.root: must not traverse symlink", "\n".join(self.evaluate(record)["errors"]))

    def test_gwt_006_given_duplicate_unknown_or_unreferenced_evidence_when_evaluated_then_it_fails_closed(self) -> None:
        duplicate = copy.deepcopy(self.load(FIXTURE_PATH))
        duplicate["evidence"]["records"] = [{"id": "unused", "path": "unused.yaml", "sha256": "0" * 64}, {"id": "unused", "path": "unused-two.yaml", "sha256": "0" * 64}]
        self.assertIn("evidence.records[2].id: duplicate evidence ID 'unused'", self.evaluate(duplicate)["errors"])
        self.assertIn("evidence.records: non-verified readiness records must not declare evidence entries", self.evaluate(duplicate)["errors"])
        missing = copy.deepcopy(self.load(FIXTURE_PATH))
        missing["criteria"][0]["state"] = "verified"
        missing["criteria"][0]["evidence_ids"] = ["missing-proof"]
        missing_result = self.evaluate(missing)
        self.assertFalse(missing_result["valid"])
        self.assertIn(
            "evidence.records: referenced evidence IDs are not declared ['missing-proof']",
            missing_result["errors"],
        )
        all_missing = copy.deepcopy(self.load(FIXTURE_PATH))
        all_missing["architecture_kit"] = {
            "package_id": "Example.ArchitectureKit",
            "package_version": "1.0.0",
            "package_version_status": "available",
        }
        for criterion in all_missing["criteria"]:
            criterion["state"] = "verified"
            criterion["evidence_ids"] = [f"{criterion['id']}-missing"]
        all_missing_result = self.evaluate(all_missing)
        self.assertFalse(all_missing_result["valid"])
        self.assertEqual(1, EVALUATOR.exit_code(all_missing_result))
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            self.prepare_verified_evidence(record, Path(temporary), {"immutable_package_identity"})
            record["evidence"]["records"].append({"id": "unknown-entry", "path": "unknown.yaml", "sha256": "0" * 64})
            result = self.evaluate(record)
        self.assertIn("evidence.records: unreferenced evidence IDs ['unknown-entry']", result["errors"])

    def test_gwt_007_given_invalid_typed_payload_or_metadata_when_evaluated_then_it_fails_closed(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            self.prepare_verified_evidence(record, root, {"behavior_parity"})
            entry = record["evidence"]["records"][0]
            path = root / entry["path"]
            metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
            metadata["payload"]["equivalence"] = "mismatched"
            metadata["provider_id"] = "wrong-provider"
            raw = yaml.safe_dump(metadata, sort_keys=True).encode("utf-8")
            path.write_bytes(raw)
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
            result = self.evaluate(record)
        self.assertIn("evidence[behavior_parity-proof].provider_id: must match the readiness record", result["errors"])
        self.assertIn("evidence[behavior_parity-proof].payload: requires empty failed/mismatched scenarios and equivalence 'equivalent'", result["errors"])
        immutable = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            self.prepare_verified_evidence(immutable, root, {"immutable_package_identity"})
            immutable["architecture_kit"] = {
                "package_id": "unavailable",
                "package_version": "unavailable",
                "package_version_status": "unavailable",
            }
            entry = immutable["evidence"]["records"][0]
            path = root / entry["path"]
            metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
            metadata["payload"]["package_id"] = "unavailable"
            metadata["payload"]["package_version"] = "unavailable"
            raw = yaml.safe_dump(metadata, sort_keys=True).encode("utf-8")
            path.write_bytes(raw)
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
            immutable_result = self.evaluate(immutable)
        self.assertIn(
            "evidence[immutable_package_identity-proof].payload: immutable package identity requires package_version_status 'available'",
            immutable_result["errors"],
        )

    def test_gwt_008_given_split_brain_manifest_mapping_when_evaluated_then_it_fails_closed(self) -> None:
        manifest = copy.deepcopy(self.load(MANIFEST_PATH))
        manifest["architecture_kit_readiness_contract"]["evaluator"] = "scripts/other.py"
        result = self.evaluate(self.load(FIXTURE_PATH), manifest)
        self.assertFalse(result["valid"])
        self.assertIn("provider-manifest: supplied mapping differs from the raw canonical manifest", result["errors"])

    def test_gwt_009_given_all_verified_typed_evidence_when_evaluated_then_exit_zero_but_no_selection_authorization_or_side_effects(self) -> None:
        record = copy.deepcopy(self.load(FIXTURE_PATH))
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            self.prepare_verified_evidence(record, Path(temporary), set(EVALUATOR.CRITERIA))
            result = self.evaluate(record)
        self.assertTrue(result["valid"])
        self.assertEqual("evidence-complete", result["readiness"])
        self.assertEqual(0, EVALUATOR.exit_code(result))
        self.assertEqual("not-selected", result["selection"])
        self.assertEqual("not-granted", result["cutover_authorization"])
        self.assertEqual("none", result["side_effects"])

    def test_gwt_010_given_current_fixture_when_evaluated_then_output_echoes_exact_binding_and_package_status(self) -> None:
        result = self.evaluate(self.load(FIXTURE_PATH))
        binding = result["binding"]
        self.assertEqual("ai-context-dotnet-bundled-mechanical-validation", binding["provider_id"])
        self.assertEqual("v0.8.0-36-g08f24eb", binding["framework_version"])
        self.assertEqual("08f24eba9f35cd3365277e566b89d3e82ae2dc83", binding["framework_commit"])
        self.assertEqual(hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(), binding["provider_manifest_sha256"])
        self.assertEqual("unavailable", binding["architecture_kit_package_id"])
        self.assertEqual("unavailable", binding["architecture_kit_package_version"])
        self.assertEqual("unavailable", binding["architecture_kit_package_version_status"])
        placeholder = copy.deepcopy(self.load(FIXTURE_PATH))
        placeholder["provider_binding"]["framework_version"] = "<exact-framework-version>"
        self.assertIn(
            "provider_binding.framework_version: must be an exact concrete framework version",
            self.evaluate(placeholder)["errors"],
        )


if __name__ == "__main__":
    unittest.main()
