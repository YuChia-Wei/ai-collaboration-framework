#!/usr/bin/env python3
"""Fail-closed tests for the deterministic AI behavior evaluation."""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / ".ai/scripts/validate-ai-behavior-evaluation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ai_behavior_evaluation", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVAL = load_module()


def fixture(case_id: str) -> dict:
    manifest = EVAL.load_yaml_mapping(EVAL.MANIFEST_PATH)
    case = next(item for item in manifest["cases"] if item["case_id"] == case_id)
    return EVAL.load_yaml_mapping(ROOT / case["input"])


class AiBehaviorEvaluationTests(unittest.TestCase):
    def test_given_full_corpus_when_run_then_exact_baseline_matches_without_model(self):
        result = EVAL.run_corpus()
        EVAL.compare_results(EVAL.load_yaml_mapping(EVAL.BASELINE_PATH), result)
        self.assertEqual(
            EVAL.REQUIRED_FAMILIES,
            {item["family"] for item in result["results"]},
        )

    def test_given_same_result_when_compared_then_it_is_equivalent(self):
        baseline = EVAL.load_yaml_mapping(EVAL.BASELINE_PATH)
        EVAL.compare_results(baseline, copy.deepcopy(baseline))

    def test_given_missing_initialization_route_when_run_then_it_fails_closed(self):
        facts = fixture("empty-repository")
        facts["requested_capability"] = "unknown"
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"empty-repository": facts})

    def test_given_implementation_without_pause_when_run_then_it_fails_closed(self):
        facts = fixture("software-development")
        facts["activation_fixture"] = (
            ".ai/evaluation/mutants/software-development-authorized.yaml"
        )
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"software-development": facts})

    def test_given_false_test_success_when_run_then_baseline_drift_fails_closed(self):
        facts = fixture("software-development")
        facts["test_execution"]["outcomes"]["integration"] = {
            "status": "passed",
            "evidence": ["fabricated success"],
        }
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"software-development": facts})

    def test_given_copied_truth_preservation_when_run_then_it_fails_closed(self):
        facts = fixture("copied-template-repository")
        facts["source_truth_disposition"] = "preserve"
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"copied-template-repository": facts})

    def test_given_dual_provenance_when_run_then_it_fails_closed(self):
        facts = fixture("customization-upgrade")
        facts["provenance_records"].append(".dev/AI-CONTEXT-SOURCE.yaml")
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"customization-upgrade": facts})

    def test_given_missing_compatibility_alias_when_run_then_it_fails_closed(self):
        facts = fixture("identifier-compatibility")
        del facts["compatibility_entries"]["dev-workflow"]
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.run_corpus(overrides={"identifier-compatibility": facts})

    def test_given_candidate_digest_drift_when_compared_then_it_fails_closed(self):
        candidate = copy.deepcopy(EVAL.load_yaml_mapping(EVAL.BASELINE_PATH))
        candidate["sha256"] = "0" * 64
        with self.assertRaises(EVAL.EvaluationError):
            EVAL.compare_results(EVAL.load_yaml_mapping(EVAL.BASELINE_PATH), candidate)

    def test_given_normalized_result_when_written_then_yaml_round_trip_is_exact(self):
        result = EVAL.run_corpus()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.yaml"
            EVAL.write_yaml(path, result)
            self.assertEqual(result, yaml.safe_load(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
