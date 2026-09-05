#!/usr/bin/env python3
"""GWT tests for canonical subject manifests and final-head rebind."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/validation_subject.py"
FIXTURES = ROOT / ".ai/scripts/tests/fixtures/validation-subject-digest/scenarios.yaml"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("validation_subject_under_test", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("subject identity implementation cannot be loaded")
SUBJECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUBJECT)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


class SubjectRepositoryFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="validation-subject-")
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-q")
        self._git("config", "user.name", "Subject Fixture")
        self._git("config", "user.email", "subject-fixture@example.invalid")
        self._write(".gitignore", "artifacts/\n.dev/ai-context/local/\n")
        self._write(".ai/input.txt", "governed input\n")
        self._write(SUBJECT.CONTRACT_REF, "fixture contract\n")
        self._write(SUBJECT.SCHEMA_REF, "fixture schema\n")
        self._write(SUBJECT.EVIDENCE_REF, "# fixture evidence helper\n")
        self._write(SUBJECT.LIFECYCLE_VALIDATOR_REF, "# fixture lifecycle validator\n")
        self._write(SUBJECT.SUBJECT_IMPLEMENTATION_REF, "# fixture subject implementation\n")
        self._write(
            SUBJECT.REGISTRY_REF,
            "\n".join(
                [
                    'register_profile fast "fixture-fast" 30 report-and-warn',
                    'register_profile pr "fixture-pr" 90 report-and-warn',
                    'register_check multi-hop-upgrade-transaction "Fixture multi-hop" required "upgrade,tests" "fast pr" ".ai/input.txt" "" "python>=3.11 git" 360 io reuse-by-input portable "python .ai/tests.py -v" always',
                    "",
                ]
            ),
        )
        closure_paths = sorted(
            {
                ".ai/input.txt",
                SUBJECT.CLASSIFICATION_REF,
                SUBJECT.CONTRACT_REF,
                SUBJECT.EVIDENCE_REF,
                SUBJECT.LIFECYCLE_VALIDATOR_REF,
                SUBJECT.REGISTRY_REF,
                SUBJECT.RUNNER_REF,
                SUBJECT.SCHEMA_REF,
                SUBJECT.SUBJECT_IMPLEMENTATION_REF,
            }
        )
        self._write(
            SUBJECT.RUNNER_REF,
            "#!/bin/bash\nset -e\n"
            'if [ "$1" != "--resolve-input-closure" ] || [ "$2" != "multi-hop-upgrade-transaction" ] || [ "$3" != "--subject" ] || [ -z "$4" ]; then exit 2; fi\n'
            + "\n".join(f"printf '%s\\n' '{path}'" for path in closure_paths)
            + "\n",
        )
        self._write(
            SUBJECT.CLASSIFICATION_REF,
            yaml.safe_dump(self._classification(), sort_keys=False, allow_unicode=True),
        )
        self._commit("fixture baseline")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _classification(self, *, eligibility: str = "pilot-approved") -> dict[str, Any]:
        reusable_profiles = ["fast", "pr"] if eligibility == "pilot-approved" else []
        return {
            "schema_version": SUBJECT.CLASSIFICATION_SCHEMA,
            "authority_id": "fixture-validation-gates",
            "repository_identity": SUBJECT.REPOSITORY_IDENTITY,
            "sensitivities": SUBJECT.SENSITIVITIES,
            "reuse_eligibility_values": SUBJECT.ELIGIBILITY,
            "groups": [
                {
                    "group_id": "subject-digest-pilot",
                    "sensitivities": ["input", "environment"],
                    "reuse_eligibility": eligibility,
                    "reusable_profiles": reusable_profiles,
                    "environment_contract": "multi-hop-upgrade-environment/v1",
                    "gate_ids": ["multi-hop-upgrade-transaction"],
                    "reason": "fixture decision",
                }
            ],
            "external_fresh_gates": [
                {
                    "gate_id": gate,
                    "sensitivities": ["provider"] if gate == "mutable-provider-state" else ["identity"],
                    "reason": "fixture fresh gate",
                }
                for gate in SUBJECT.REQUIRED_FRESH_GATES
            ],
        }

    def _write(self, relative: str, content: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def _git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def _commit(self, message: str) -> None:
        self._git("add", "-A")
        self._git("commit", "-q", "-m", message)

    def _evidence(self, root: str = "original") -> Path:
        path = self.repo / f"artifacts/{root}/evidence.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": "2.0.0",
                    "validator_id": "multi-hop-upgrade-transaction",
                    "profile": "pr",
                    "outcome": "passed",
                    "execution_disposition": "executed",
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return path

    def _manifest(self, root: str, *, evidence: Path | None) -> tuple[dict[str, Any], set[Path]]:
        return SUBJECT.build_subject_manifest(
            self.repo,
            gate_id="multi-hop-upgrade-transaction",
            profile="pr",
            output=f"artifacts/{root}/subject-manifest.json",
            closure_output=f"artifacts/{root}/closure.json",
            runtime_output=f"artifacts/{root}/runtime.json",
            source_evidence=evidence,
        )

    def _seal(self, root: str, manifest: dict[str, Any], paths: set[Path]) -> tuple[Path, str]:
        identity = manifest["provenance"]
        artifacts = []
        for path in sorted(paths, key=lambda item: item.relative_to(self.repo).as_posix()):
            content = path.read_bytes()
            artifacts.append(
                {
                    "ref": path.relative_to(self.repo).as_posix(),
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "bytes": len(content),
                }
            )
        core = {
            "schema_version": "validation-invocation/v1",
            "invocation_id": "fixture-original",
            "profile": "pr",
            "outcome": "passed",
            "sealed_at": "2026-09-03T00:00:00Z",
            "repository": {
                "pre_identity_digest": "a" * 64,
                "post_identity_digest": "a" * 64,
                "verified_identity_digest": "a" * 64,
                "commit": identity["commit"],
                "tree": identity["tree"],
                "clean": True,
            },
            "cardinality": {"events": 1, "evidence_records": 1},
            "control_plane": [],
            "terminal_supervision": {"mode": "direct"},
            "artifacts": artifacts,
        }
        seal = {**core, "manifest_digest": canonical_sha256(core)}
        path = self.repo / f"artifacts/{root}/invocation-seal.json"
        path.write_text(json.dumps(seal, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        return path, hashlib.sha256(path.read_bytes()).hexdigest()


class ValidationSubjectDigestGwtTests(SubjectRepositoryFixture):
    def test_gwt_001_given_history_only_commit_change_when_rebound_then_expensive_evidence_is_reused_truthfully(self) -> None:
        evidence = self._evidence()
        original, original_paths = self._manifest("original", evidence=evidence)
        original_manifest_path = self.repo / "artifacts/original/subject-manifest.json"
        self.assertEqual(
            original_paths,
            SUBJECT.sealable_subject_manifest_paths(
                self.repo, [original_manifest_path], evidence
            ),
        )
        seal_path, seal_digest = self._seal("original", original, original_paths)
        original_commit = original["provenance"]["commit"]
        self.assertTrue(
            original["provenance"]["repository"].startswith(
                f"{SUBJECT.REPOSITORY_IDENTITY}:"
            )
        )
        self.assertNotIn("YuChia-Wei", original["provenance"]["repository"])

        self._git("commit", "--amend", "-q", "-m", "history-only identity change")
        current, _current_paths = self._manifest("current", evidence=None)
        self.assertNotEqual(original_commit, current["provenance"]["commit"])
        self.assertEqual(original["subject_digest"], current["subject_digest"])

        receipt = SUBJECT.build_rebind_receipt(
            self.repo,
            original_manifest_value=original_manifest_path,
            current_manifest_value="artifacts/current/subject-manifest.json",
            original_seal_value=seal_path,
            original_seal_sha256=seal_digest,
            output="artifacts/current/rebind.json",
        )

        self.assertEqual("reused-with-proof", receipt["decision"]["outcome"])
        self.assertIn(original_commit, receipt["decision"]["truthful_statement"])
        self.assertIn("not executed or audited at", receipt["decision"]["truthful_statement"])
        self.assertEqual(SUBJECT.REQUIRED_FRESH_GATES, [item["gate"] for item in receipt["verification"]["required_fresh_gates"]])
        SUBJECT.validate_rebind_receipt(receipt)
        normalized, authenticated_paths = SUBJECT.validated_rebind_source(
            self.repo,
            "artifacts/current/rebind.json",
            expected_gate_id="multi-hop-upgrade-transaction",
            expected_profile="pr",
        )
        self.assertEqual("subject-rebind", normalized["kind"])
        self.assertEqual("multi-hop-upgrade-transaction", normalized["gate_id"])
        self.assertEqual("pr", normalized["profile"])
        self.assertIn(self.repo / "artifacts/original/invocation-seal.json", authenticated_paths)
        self.assertIn(self.repo / "artifacts/current/subject-manifest.json", authenticated_paths)
        inspection = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".ai/scripts/validation-evidence.py"),
                "inspect-subject-rebind",
                "--repo",
                str(self.repo),
                "--receipt",
                "artifacts/current/rebind.json",
                "--expected-gate-id",
                "multi-hop-upgrade-transaction",
                "--profile",
                "pr",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        self.assertEqual(0, inspection.returncode, inspection.stderr)
        self.assertEqual("multi-hop-upgrade-transaction\tpr", inspection.stdout.strip())

    def test_gwt_002_given_tracked_subject_drift_when_rebound_then_reexecution_is_required(self) -> None:
        evidence = self._evidence()
        original, original_paths = self._manifest("original", evidence=evidence)
        seal_path, seal_digest = self._seal("original", original, original_paths)
        self._write(".ai/input.txt", "changed governed input\n")
        self._commit("tracked input drift")
        current, _current_paths = self._manifest("current", evidence=None)

        receipt = SUBJECT.build_rebind_receipt(
            self.repo,
            original_manifest_value="artifacts/original/subject-manifest.json",
            current_manifest_value="artifacts/current/subject-manifest.json",
            original_seal_value=seal_path,
            original_seal_sha256=seal_digest,
            output="artifacts/current/rebind.json",
        )

        self.assertNotEqual(original["subject_digest"], current["subject_digest"])
        self.assertEqual("re-executed", receipt["decision"]["outcome"])
        self.assertEqual("tracked-input-or-dependency-drift", receipt["decision"]["reason"])

    def test_gwt_003_given_unsealed_or_tampered_original_when_rebound_then_it_fails_closed(self) -> None:
        evidence = self._evidence()
        original, original_paths = self._manifest("original", evidence=evidence)
        seal_path, seal_digest = self._seal("original", original, original_paths)
        self._git("commit", "--amend", "-q", "-m", "history-only identity change")
        self._manifest("current", evidence=None)

        with self.assertRaisesRegex(SUBJECT.SubjectError, "seal bytes are not authenticated"):
            SUBJECT.build_rebind_receipt(
                self.repo,
                original_manifest_value="artifacts/original/subject-manifest.json",
                current_manifest_value="artifacts/current/subject-manifest.json",
                original_seal_value=seal_path,
                original_seal_sha256="0" * 64,
                output="artifacts/current/rebind.json",
            )
        self.assertFalse((self.repo / "artifacts/current/rebind.json").exists())
        self.assertTrue(seal_digest)

    def test_gwt_004_given_candidate_disabled_classification_when_rebind_is_requested_then_it_is_blocked(self) -> None:
        self._write(
            SUBJECT.CLASSIFICATION_REF,
            yaml.safe_dump(self._classification(eligibility="candidate-disabled"), sort_keys=False),
        )
        self._commit("disable candidate")
        evidence = self._evidence()
        original, original_paths = self._manifest("original", evidence=evidence)
        seal_path, seal_digest = self._seal("original", original, original_paths)
        self._git("commit", "--amend", "-q", "-m", "candidate history change")
        self._manifest("current", evidence=None)

        with self.assertRaisesRegex(SUBJECT.SubjectError, "not allowlisted"):
            SUBJECT.build_rebind_receipt(
                self.repo,
                original_manifest_value="artifacts/original/subject-manifest.json",
                current_manifest_value="artifacts/current/subject-manifest.json",
                original_seal_value=seal_path,
                original_seal_sha256=seal_digest,
                output="artifacts/current/rebind.json",
            )

    def test_gwt_005_given_unknown_closure_when_manifest_is_requested_then_it_fails_before_claiming_identity(self) -> None:
        self._write(SUBJECT.RUNNER_REF, "#!/bin/bash\nexit 2\n")
        self._commit("break closure authority")
        evidence = self._evidence()

        with self.assertRaisesRegex(SUBJECT.SubjectError, "closure is unresolved"):
            self._manifest("blocked", evidence=evidence)
        self.assertFalse((self.repo / "artifacts/blocked/subject-manifest.json").exists())

    def test_gwt_005b_given_invalid_external_fresh_sensitivities_when_authority_is_loaded_then_it_fails_closed(self) -> None:
        invalid_values = [
            [],
            ["not-a-valid-sensitivity"],
            ["identity", "identity"],
            ["provider", "identity"],
        ]
        for invalid in invalid_values:
            with self.subTest(sensitivities=invalid):
                authority = self._classification()
                authority["external_fresh_gates"][0]["sensitivities"] = invalid
                self._write(
                    SUBJECT.CLASSIFICATION_REF,
                    yaml.safe_dump(authority, sort_keys=False, allow_unicode=True),
                )
                with self.assertRaisesRegex(
                    SUBJECT.SubjectError,
                    "external fresh gate sensitivities are invalid",
                ):
                    SUBJECT.load_classification_authority(self.repo)


class ValidationSubjectClassificationGwtTests(unittest.TestCase):
    def test_gwt_006_given_current_registry_when_classified_then_every_gate_occurs_once_and_only_one_is_enabled(self) -> None:
        classifications, _authority = SUBJECT.load_classification_authority(ROOT)

        self.assertEqual(76, len(classifications))
        self.assertEqual(
            ["multi-hop-upgrade-transaction"],
            sorted(gate for gate, item in classifications.items() if item["reuse_eligibility"] == "pilot-approved"),
        )
        self.assertEqual("candidate-disabled", classifications["incident-fault-injection"]["reuse_eligibility"])
        self.assertEqual("candidate-disabled", classifications["validation-dependency-observation-contract"]["reuse_eligibility"])

    def test_gwt_007_given_change_fixture_matrix_when_decided_then_history_and_provider_only_changes_do_not_mask_subject_drift(self) -> None:
        fixture = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        self.assertEqual("subject-rebind-fixtures/v1", fixture["schema_version"])
        self.assertEqual(
            ["provider-drift"],
            [scenario["id"] for scenario in fixture["scenarios"] if "fresh_gate" in scenario],
        )
        _classifications, authority = SUBJECT.load_classification_authority(ROOT)
        external_fresh = {
            item["gate_id"]: item for item in authority["external_fresh_gates"]
        }
        base_projection = {
            "schema_version": SUBJECT.IDENTITY_SCHEMA,
            "gate_id": "multi-hop-upgrade-transaction",
            "classification_digest": "1" * 64,
            "tracked_closure_digest": "2" * 64,
            "invocation_digest": "3" * 64,
            "authority_digest": "4" * 64,
            "runtime_digest": "5" * 64,
            "environment_digest": "6" * 64,
        }
        original = {"identity_projection": base_projection, "subject_digest": canonical_sha256(base_projection)}
        for scenario in fixture["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                current_projection = copy.deepcopy(base_projection)
                changed = scenario.get("changed_component")
                if changed:
                    current_projection[changed] = "f" * 64
                current = {"identity_projection": current_projection, "subject_digest": canonical_sha256(current_projection)}
                outcome, _reason = SUBJECT.decide_rebind(
                    original,
                    current,
                    classification_approved=True,
                    profile_allowlisted=True,
                    original_authentication_valid=scenario.get("original_authentication_valid", True),
                    current_closure_complete=scenario.get("current_closure_complete", True),
                    current_unknown_paths=[],
                )
                self.assertEqual(scenario["expected_outcome"], outcome)
                fresh_gate = scenario.get("fresh_gate")
                if fresh_gate is not None:
                    self.assertIn(fresh_gate, external_fresh)
                    self.assertIn("provider", external_fresh[fresh_gate]["sensitivities"])
                    requirement = next(
                        item
                        for item in [
                            {
                                "gate": gate,
                                "required": True,
                                "replaceable_by_reuse": False,
                            }
                            for gate in SUBJECT.REQUIRED_FRESH_GATES
                        ]
                        if item["gate"] == fresh_gate
                    )
                    self.assertTrue(requirement["required"])
                    self.assertFalse(requirement["replaceable_by_reuse"])


if __name__ == "__main__":
    unittest.main()
