#!/usr/bin/env python3
"""Fail-closed tests for bounded validation dependency observation."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import uuid
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/observe-validation-dependencies.py"
FIXTURES = ROOT / ".ai/scripts/tests/fixtures/validation-dependency-observation"
SCHEMA = ROOT / ".ai/assets/shared/validation-dependency-observation.schema.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "validation_dependency_observation", SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OBSERVATION = load_module()


def request(name: str) -> dict:
    value = yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"Fixture {name} is not a mapping")
    return value


class ValidationDependencyObservationTests(unittest.TestCase):
    def test_given_representative_harness_when_observed_then_all_dimensions_are_explicit_and_lower_bound(self):
        with mock.patch.dict(os.environ, {"VAL012_MODE": "private-value-not-for-report"}):
            report = OBSERVATION.observe_request(request("representative.yaml"), ROOT)

        self.assertEqual("passed", report["decision"]["outcome"])
        self.assertEqual("partial", report["observation_boundary"]["coverage_state"])
        self.assertEqual("lower-bound-only", report["observation_boundary"]["closure_claim"])
        self.assertFalse(report["observation_boundary"]["complete_transitive_closure"])
        self.assertEqual(
            set(OBSERVATION.DIMENSIONS), set(report["coverage"])
        )
        self.assertTrue(
            all(
                value["status"] == "partial" and value["complete"] is False
                for value in report["coverage"].values()
            )
        )
        observed = report["observed_dependencies"]
        self.assertIn(
            ".ai/scripts/tests/fixtures/validation-dependency-observation/declared.txt",
            observed["file"],
        )
        self.assertEqual(["git", "python"], observed["subprocess"])
        self.assertEqual(["git:rev-parse"], observed["git"])
        self.assertEqual(["VAL012_MODE"], observed["environment"])
        self.assertEqual(["module:decimal", "python"], observed["runtime"])
        self.assertTrue(report["worktree"]["tracked_state_unchanged"])
        self.assertFalse(report["decision"]["automatic_registry_edits"])
        self.assertFalse(report["decision"]["declarations_removed"])
        self.assertEqual(list(OBSERVATION.FRESH_GATES), report["decision"]["fresh_gates"])
        serialized = json.dumps(report, sort_keys=True)
        self.assertNotIn(str(ROOT), serialized)
        self.assertNotIn("private-value-not-for-report", serialized)

    def test_given_undeclared_file_when_observed_then_boundary_fails(self):
        report = OBSERVATION.observe_request(request("undeclared-file.yaml"), ROOT)

        self.assertEqual("failed", report["decision"]["outcome"])
        self.assertEqual([
            ".ai/scripts/tests/fixtures/validation-dependency-observation/declared.txt"
        ], report["drift"]["observed_but_undeclared"]["file"])
        self.assertIn("observed-but-undeclared", report["decision"]["reasons"])

    def test_given_undeclared_tool_when_observed_then_boundary_fails(self):
        report = OBSERVATION.observe_request(
            request("undeclared-subprocess.yaml"), ROOT
        )

        self.assertEqual("failed", report["decision"]["outcome"])
        self.assertEqual(
            ["python"],
            report["drift"]["observed_but_undeclared"]["subprocess"],
        )

    def test_given_unsupported_harness_when_reported_then_it_is_blocked_not_complete(self):
        report = OBSERVATION.observe_request(
            request("unsupported-harness.yaml"), ROOT
        )

        self.assertEqual("blocked", report["decision"]["outcome"])
        self.assertEqual(
            "unsupported", report["observation_boundary"]["coverage_state"]
        )
        self.assertTrue(
            all(value["status"] == "unsupported" for value in report["coverage"].values())
        )
        self.assertFalse(report["observation_boundary"]["complete_transitive_closure"])
        self.assertEqual("unsupported-harness", report["diagnostics"]["target_error"])

    def test_given_untaken_branch_and_broad_input_when_observed_then_both_stay_advisory(self):
        report = OBSERVATION.observe_request(request("representative.yaml"), ROOT)
        unobserved = report["drift"]["declared_but_unobserved"]["file"]

        self.assertEqual("advisory-retain", report["drift"]["declared_but_unobserved_disposition"])
        self.assertIn(
            ".ai/scripts/tests/fixtures/validation-dependency-observation/broad.txt",
            unobserved,
        )
        self.assertIn(
            ".ai/scripts/tests/fixtures/validation-dependency-observation/untaken.txt",
            unobserved,
        )
        self.assertEqual("passed", report["decision"]["outcome"])

        taken = request("representative.yaml")
        taken["argv"] = ["--take-branch"]
        taken_report = OBSERVATION.observe_request(taken, ROOT)
        self.assertNotIn(
            ".ai/scripts/tests/fixtures/validation-dependency-observation/untaken.txt",
            taken_report["drift"]["declared_but_unobserved"]["file"],
        )

    def test_given_noncanonical_declarations_when_validated_then_the_request_fails_closed(self):
        malformed = request("representative.yaml")
        malformed["declared_dependencies"]["subprocess"] = ["python", "git"]

        with self.assertRaisesRegex(
            OBSERVATION.ObservationError, "sorted and unique"
        ):
            OBSERVATION.validate_request(malformed, ROOT)

    def test_given_report_when_digest_is_recomputed_then_normalized_bytes_match(self):
        report = OBSERVATION.observe_request(request("representative.yaml"), ROOT)
        digest = report.pop("report_digest")

        self.assertEqual(digest, OBSERVATION.canonical_digest(report))

    def test_given_cli_output_when_run_then_it_is_create_only_ignored_and_status_stable(self):
        local_root = ROOT / ".dev/ai-context/local/validation"
        local_root.mkdir(parents=True, exist_ok=True)
        before = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        output = local_root / f"val012-cli-{uuid.uuid4().hex}.yaml"
        output_relative = output.relative_to(ROOT).as_posix()
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--request",
                    ".ai/scripts/tests/fixtures/validation-dependency-observation/representative.yaml",
                    "--output",
                    output_relative,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            output_report = yaml.safe_load(output.read_text(encoding="utf-8"))
            self.assertEqual("passed", output_report["decision"]["outcome"])
            second = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--request",
                    ".ai/scripts/tests/fixtures/validation-dependency-observation/representative.yaml",
                    "--output",
                    output_relative,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(2, second.returncode)
            self.assertIn("create-only", second.stderr)
        finally:
            output.unlink(missing_ok=True)
        after = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        self.assertEqual(before, after)

    def test_given_schema_when_loaded_then_no_coverage_dimension_can_claim_complete(self):
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(list(OBSERVATION.DIMENSIONS), schema["report"]["coverage_dimensions"])
        self.assertEqual(["partial", "unsupported"], schema["report"]["coverage_states"])
        self.assertFalse(schema["report"]["complete_transitive_closure"])
        self.assertFalse(schema["report"]["automatic_registry_edits"])


if __name__ == "__main__":
    unittest.main()
