#!/usr/bin/env python3
"""Fail-closed tests for the activated v0.6 skill transition."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / ".ai/scripts/validate-skill-transition.py"
SPEC = importlib.util.spec_from_file_location("validate_skill_transition", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SkillTransitionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        paths = [
            VALIDATOR.MANIFEST,
            VALIDATOR.RETIREMENT,
            VALIDATOR.FIXTURE,
            VALIDATOR.CANONICAL_REGISTRY,
            VALIDATOR.AGENTS_REGISTRY,
            VALIDATOR.CLAUDE_REGISTRY,
            Path(".ai/evaluation/corpus-manifest.yaml"),
            Path(".ai/evaluation/baselines/v1.yaml"),
        ]
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, target)
        evidence_paths = [VALIDATOR.MODEL_REPORT, *VALIDATOR.MODEL_EVIDENCE.values()]
        for evidence in evidence_paths:
            target = self.root / evidence
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n", encoding="utf-8")
        manifest = self.manifest()
        model = manifest["activation_gate"]["model_in_loop_evaluation"]
        model["report_sha256"] = VALIDATOR.sha256_file(
            self.root / VALIDATOR.MODEL_REPORT
        )
        model["retained_evidence_sha256"] = {
            name: VALIDATOR.sha256_file(self.root / path)
            for name, path in VALIDATOR.MODEL_EVIDENCE.items()
        }
        self.write_manifest(manifest)
        for current, (candidate, _) in VALIDATOR.EXPECTED_TRANSITIONS.items():
            active = self.root / ".ai/assets/skills" / candidate / "skill.yaml"
            active.parent.mkdir(parents=True, exist_ok=True)
            active.write_text(
                yaml.safe_dump(
                    {"asset_id": candidate, "status": "active"},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            for runtime in VALIDATOR.RUNTIME_ROOTS:
                wrapper = self.root / runtime / candidate / "SKILL.md"
                wrapper.parent.mkdir(parents=True, exist_ok=True)
                wrapper.write_text("# Active fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def manifest(self) -> dict:
        return yaml.safe_load((self.root / VALIDATOR.MANIFEST).read_text(encoding="utf-8"))

    def write_manifest(self, value: dict) -> None:
        (self.root / VALIDATOR.MANIFEST).write_text(
            yaml.safe_dump(value, sort_keys=False),
            encoding="utf-8",
        )

    def test_given_activated_transition_when_validated_then_it_passes(self) -> None:
        self.assertEqual([], VALIDATOR.validate(self.root))

    def test_given_missing_active_candidate_when_validated_then_it_fails(self) -> None:
        candidate = self.root / ".ai/assets/skills/ai-context-init/skill.yaml"
        candidate.unlink()
        self.assertTrue(
            any("active canonical skill is missing" in item for item in VALIDATOR.validate(self.root))
        )

    def test_given_non_atomic_activation_when_validated_then_it_fails(self) -> None:
        manifest = self.manifest()
        manifest["activation_mode"] = "rolling"
        self.write_manifest(manifest)
        self.assertTrue(
            any("activation_mode must be atomic" in item for item in VALIDATOR.validate(self.root))
        )

    def test_given_missing_compatibility_alias_when_validated_then_it_fails(self) -> None:
        fixture_path = self.root / VALIDATOR.FIXTURE
        fixture = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))
        del fixture["compatibility_entries"]["dev-workflow"]
        fixture_path.write_text(
            yaml.safe_dump(fixture, sort_keys=False),
            encoding="utf-8",
        )
        self.assertTrue(
            any("compatibility entry mapping drifted" in item for item in VALIDATOR.validate(self.root))
        )

    def test_given_scheduled_legacy_removal_when_validated_then_it_fails(self) -> None:
        manifest = self.manifest()
        manifest["transitions"][0]["removal_target"] = "v0.7.0"
        self.write_manifest(manifest)
        self.assertTrue(
            any("must not have a removal target" in item for item in VALIDATOR.validate(self.root))
        )

    def test_given_historical_rewrite_when_validated_then_it_fails(self) -> None:
        manifest = copy.deepcopy(self.manifest())
        manifest["transitions"][1]["historical_identifier_rewrite"] = True
        self.write_manifest(manifest)
        self.assertTrue(
            any("must not authorize historical rewrites" in item for item in VALIDATOR.validate(self.root))
        )

    def test_given_missing_model_evidence_when_validated_then_it_fails(self) -> None:
        (self.root / VALIDATOR.MODEL_EVIDENCE["terra-judge.yaml"]).unlink()
        self.assertTrue(
            any("retained evidence must resolve" in item for item in VALIDATOR.validate(self.root))
        )


if __name__ == "__main__":
    unittest.main()
