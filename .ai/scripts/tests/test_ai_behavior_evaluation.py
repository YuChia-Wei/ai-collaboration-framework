#!/usr/bin/env python3
"""Fail-closed tests for the deterministic AI behavior evaluation."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
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


class IncidentFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = EVAL.run_incident_fault_injection()

    def test_given_incident_manifest_when_validated_then_known_incidents_categories_and_inputs_are_complete(self):
        manifest = EVAL.load_yaml_mapping(EVAL.FAULT_MANIFEST_PATH)
        mutants, inputs = EVAL.validate_fault_manifest(manifest)

        self.assertEqual(EVAL.CRITICAL_INCIDENTS, {
            item["incident_reference"]
            for item in mutants
            if item["criticality"] == "critical"
            and item["incident_reference"] in EVAL.CRITICAL_INCIDENTS
        })
        self.assertEqual(EVAL.CRITICAL_MUTANT_CATEGORIES, {
            item["category"]
            for item in mutants
            if item["criticality"] == "critical"
        })
        self.assertEqual(
            set(inputs),
            {reference for item in mutants for reference in item["input_refs"]},
        )
        self.assertTrue(
            all(
                {"category", "expected_detector", "actual_detector", "outcome"}
                <= set(item)
                for item in self.result["results"]
            )
        )

    def test_given_all_critical_incident_mutants_when_executed_then_every_expected_detector_kills_its_mutant(self):
        critical = [
            item for item in self.result["results"] if item["criticality"] == "critical"
        ]

        self.assertEqual(5, len(critical))
        self.assertTrue(all(item["outcome"] == "detected" for item in critical))
        self.assertTrue(
            all(item["actual_detector"] == item["expected_detector"] for item in critical)
        )
        self.assertEqual(100, self.result["effectiveness"]["critical_detection_percent"])
        self.assertEqual([], self.result["effectiveness"]["critical_survivors"])

    def test_given_exploratory_survivor_when_reported_then_it_is_not_represented_as_detected_or_passed(self):
        exploratory = [
            item
            for item in self.result["results"]
            if item["criticality"] == "exploratory"
        ]

        self.assertEqual(1, len(exploratory))
        self.assertEqual("survived", exploratory[0]["outcome"])
        self.assertIsNone(exploratory[0]["actual_detector"])
        self.assertTrue(exploratory[0]["follow_up"])
        self.assertEqual(
            "passed-with-exploratory-survivors",
            self.result["decision"]["outcome"],
        )
        self.assertEqual(
            "follow-up-required",
            self.result["decision"]["exploratory_disposition"],
        )
        self.assertEqual(
            [{
                "mutant_id": exploratory[0]["mutant_id"],
                "summary": exploratory[0]["follow_up"],
            }],
            self.result["effectiveness"]["follow_up_candidates"],
        )

    def test_given_one_disabled_critical_detector_when_gate_runs_then_the_survivor_fails_the_gate(self):
        result = EVAL.run_incident_fault_injection(
            disabled_detectors={"required-test-evidence"}
        )
        survivor = next(
            item
            for item in result["results"]
            if item["mutant_id"] == "required-test-evidence-omission"
        )

        self.assertEqual("survived", survivor["outcome"])
        self.assertEqual("failed", result["decision"]["outcome"])
        self.assertEqual("failed", result["decision"]["critical_gate"])
        self.assertIn(
            "required-test-evidence-omission",
            result["effectiveness"]["critical_survivors"],
        )

    def test_given_incident_execution_when_completed_then_tracked_worktree_is_unchanged(self):
        worktree = self.result["worktree"]

        self.assertTrue(worktree["tracked_state_unchanged"])
        self.assertEqual(
            worktree["before_tracked_status_digest"],
            worktree["after_tracked_status_digest"],
        )

    def test_given_normalized_incident_report_when_digest_recomputed_then_it_matches(self):
        report = copy.deepcopy(self.result)
        digest = report.pop("report_digest")

        self.assertEqual(digest, EVAL.canonical_json_sha256(report))
        self.assertTrue(
            all(
                EVAL.SHA256.fullmatch(item["diagnostic_fingerprint"])
                for item in report["results"]
            )
        )
        self.assertNotIn(str(ROOT), json.dumps(report, sort_keys=True))

    def test_given_candidate_input_digest_drift_when_manifest_validated_then_it_fails_before_mutant_execution(self):
        manifest = EVAL.load_yaml_mapping(EVAL.FAULT_MANIFEST_PATH)
        manifest["candidate_inputs"][0]["sha256"] = "0" * 64

        with self.assertRaisesRegex(
            EVAL.EvaluationError, "differs from its declared SHA-256"
        ):
            EVAL.validate_fault_manifest(manifest)

    def test_given_cli_output_when_written_then_it_is_create_only_ignored_and_normalized(self):
        local_root = ROOT / ".dev/ai-context/local/validation"
        local_root.mkdir(parents=True, exist_ok=True)
        output = local_root / f"val011-{uuid.uuid4().hex}.yaml"
        relative = output.relative_to(ROOT).as_posix()
        try:
            first = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "fault-injection",
                    "--output",
                    relative,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(0, first.returncode, first.stderr)
            report = yaml.safe_load(output.read_text(encoding="utf-8"))
            self.assertEqual(
                "passed-with-exploratory-survivors",
                report["decision"]["outcome"],
            )
            second = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "fault-injection",
                    "--output",
                    relative,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(1, second.returncode)
            self.assertIn("create-only", second.stderr)
        finally:
            output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
