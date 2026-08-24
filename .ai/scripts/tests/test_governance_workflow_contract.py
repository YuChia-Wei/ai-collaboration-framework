#!/usr/bin/env python3
"""GWT contract tests for the dedicated governance pull-request workflow."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/governance.yml"
REGISTRY_PATH = REPO_ROOT / ".ai/distribution/governance-checks.yaml"
GOVERNED_PR_PATHS = {"**"}
CANONICAL_FAST_PROFILE = "args=(--profile fast)"
CANONICAL_PROFILE_RUNNER = 'bash .ai/scripts/check-all.sh "${args[@]}"'
MUTATING_COMMAND = re.compile(
    r"(?:\bgh\s+release\b|\bgit\s+(?:push|commit)\b|"
    r"\bgit\s+tag\s+(?:--(?:annotate|delete)|-[ad])\b|"
    r"\b(?:git|gh)\s+.*\b(?:create|delete|publish)\b.*\b(?:tag|release)\b)",
    re.IGNORECASE,
)


def load_workflow() -> dict:
    """Load YAML without coercing the GitHub ``on`` key to a boolean."""
    return yaml.load(WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def run_commands(workflow: dict) -> list[str]:
    return [
        step["run"]
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
        if isinstance(step, dict) and "run" in step
    ]


class GovernanceWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(WORKFLOW_PATH.is_file(), f"Missing workflow: {WORKFLOW_PATH}")
        self.workflow = load_workflow()
        self.commands = run_commands(self.workflow)

    def test_gwt_001_given_governance_workflow_when_loaded_then_triggers_and_paths_are_exact(self) -> None:
        self.assertEqual({"pull_request", "workflow_dispatch"}, set(self.workflow["on"]))
        self.assertEqual(
            GOVERNED_PR_PATHS,
            set(self.workflow["on"]["pull_request"]["paths"]),
        )
        self.assertEqual(["**"], self.workflow["on"]["pull_request"]["paths"])
        self.assertEqual(
            ["opened", "synchronize", "reopened", "edited"],
            self.workflow["on"]["pull_request"]["types"],
        )

    def test_gwt_002_given_governance_workflow_when_checked_then_permissions_are_read_only(self) -> None:
        self.assertEqual({}, self.workflow.get("permissions"))
        for job_name, job in self.workflow["jobs"].items():
            with self.subTest(job=job_name):
                self.assertEqual({"contents": "read"}, job.get("permissions"))

    def test_gwt_003_given_governance_workflow_when_checked_then_runner_setup_is_pinned(self) -> None:
        steps = [step for job in self.workflow["jobs"].values() for step in job["steps"]]
        checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v6")
        self.assertEqual(
            {
                "fetch-depth": "0",
                "persist-credentials": "false",
                "ref": "${{ github.event_name == 'pull_request' && github.event.pull_request.head.sha || github.sha }}",
            },
            checkout.get("with"),
        )
        setup_python = next(step for step in steps if step.get("uses") == "actions/setup-python@v6")
        self.assertEqual({"python-version": "3.12"}, setup_python.get("with"))
        self.assertIn("python -m pip install --disable-pip-version-check -r requirements.txt", self.commands)

    def test_gwt_004_given_governance_workflow_when_checked_then_membership_comes_from_the_canonical_profile(self) -> None:
        command_text = "\n".join(self.commands)
        self.assertIn(CANONICAL_FAST_PROFILE, command_text)
        self.assertIn(CANONICAL_PROFILE_RUNNER, command_text)
        self.assertIn("github.event.pull_request.base.sha", command_text)
        self.assertIn("github.event.pull_request.head.sha", command_text)
        self.assertNotIn("python .ai/scripts/validate-ai-context.py", command_text)
        step_names = {
            step.get("name")
            for job in self.workflow["jobs"].values()
            for step in job["steps"]
        }
        self.assertIn("Run the canonical fast governance profile", step_names)
        self.assertNotIn("Validate v0.5.0 path disposition", step_names)

    def test_gwt_005_given_governance_workflow_when_checked_then_release_mutation_is_absent(self) -> None:
        command_text = "\n".join(self.commands)
        self.assertIsNone(MUTATING_COMMAND.search(command_text))
        self.assertNotIn("contents: write", command_text.lower())

    def test_gwt_006_given_general_governance_when_checked_then_release_phase_execution_is_absent(self) -> None:
        command_text = "\n".join(self.commands)
        self.assertNotIn(
            "python .ai/scripts/validate-ai-context-release-state.py",
            command_text,
        )
        self.assertNotIn("--phase candidate", command_text)
        self.assertNotIn("--phase finalization", command_text)

    def test_gwt_007_given_source_registry_when_loaded_then_governance_inputs_are_exact(self) -> None:
        registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual("1.4", registry["schema_version"])
        self.assertEqual(
            [
                {
                    "id": "v050-published-path-disposition",
                    "path": (
                        ".dev/workflows/2026-07-21-v0-5-0-development/"
                        "evidence/v050-published-path-disposition.yaml"
                    ),
                    "current_byte_authorizations": [
                        ".dev/workflows/2026-08-10-current-context-remediation/"
                        "evidence/v050-current-byte-authorization.yaml"
                    ],
                }
            ],
            registry["manifests"],
        )
        self.assertEqual(
            [
                {
                    "id": "repository-rename-retired-identity",
                    "path": ".ai/distribution/repository-identity-policy.yaml",
                }
            ],
            registry["repository_identity_policies"],
        )
        self.assertEqual(
            [
                {
                    "id": "dotnet-backend-source-dispositions",
                    "path": ".ai/distribution/source-dispositions.yaml",
                }
            ],
            registry["source_disposition_contracts"],
        )
        self.assertEqual(
            [
                {
                    "id": "source-work-management-authority",
                    "path": ".dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml",
                }
            ],
            registry["source_work_management_contracts"],
        )


if __name__ == "__main__":
    unittest.main()
