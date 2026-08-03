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
ROOT_ENTRIES = {
    "README.md",
    "README.en.md",
    "AGENTS.md",
    "AGENTS.zh-TW.md",
    "CLAUDE.md",
}
GOVERNED_PR_PATHS = {
    ".ai/**",
    ".agents/**",
    ".claude/**",
    ".codex/**",
    ".dev/TEAM-GIT-FLOW-RULES.MD",
    ".dev/adr/ADR-TEMPLATE.md",
    ".dev/adr/README.md",
    ".dev/adr/WHEN-TO-CREATE-ADR.MD",
    ".dev/assessments/README.MD",
    ".dev/assessments/templates/**",
    ".dev/backlog/**",
    ".dev/domain-language/README.MD",
    ".dev/domain-language/templates/**",
    ".dev/guides/**",
    ".dev/operations/**",
    ".dev/problem-frames/README.MD",
    ".dev/problem-frames/SEMANTICS.md",
    ".dev/problem-frames/templates/**",
    ".dev/requirement/REQUIREMENT-GUIDE.MD",
    ".dev/releases/**",
    ".dev/specs/**",
    ".dev/standards/**",
    ".dev/workflows/README.MD",
    ".dev/workflows/handoff-checkpoints.yaml",
    ".dev/workflows/**/handoff-checkpoints/**",
    ".github/agents/**",
    ".github/workflows/governance.yml",
    *ROOT_ENTRIES,
}
SOURCE_GOVERNANCE_COMMAND = "python .ai/scripts/validate-source-governance.py"
REQUIRED_COMMANDS = {
    "python .ai/scripts/validate-ai-context.py",
    "python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v",
    "python .ai/scripts/tests/test_ai_context_language_policy.py -v",
    "python .ai/scripts/tests/test_ai_context_sub_agent_adapters.py -v",
    "python .ai/scripts/validate-dependency-versions.py",
    "python .ai/scripts/tests/test_dependency_version_consistency.py -v",
    "python .ai/scripts/validate-shell-assets.py",
    "python .ai/scripts/tests/test_workflow_handoff.py -v",
    "python .ai/scripts/validate-workflow-handoff.py --all",
    "python .ai/scripts/tests/test_ai_context_release_state.py -v",
    "python .ai/scripts/tests/test_prepare_ai_context_release.py -v",
    "python .ai/scripts/tests/test_release_notes_renderer.py -v",
    SOURCE_GOVERNANCE_COMMAND,
    "python .ai/scripts/tests/test_file_disposition_manifest.py -v",
    "python .ai/scripts/tests/test_workflow_delivery_policy.py -v",
    "python .ai/scripts/tests/test_governance_workflow_contract.py -v",
}
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
        self.assertIn(".dev/releases/**", self.workflow["on"]["pull_request"]["paths"])

    def test_gwt_002_given_governance_workflow_when_checked_then_permissions_are_read_only(self) -> None:
        self.assertEqual({}, self.workflow.get("permissions"))
        for job_name, job in self.workflow["jobs"].items():
            with self.subTest(job=job_name):
                self.assertEqual({"contents": "read"}, job.get("permissions"))

    def test_gwt_003_given_governance_workflow_when_checked_then_runner_setup_is_pinned(self) -> None:
        steps = [step for job in self.workflow["jobs"].values() for step in job["steps"]]
        checkout = next(step for step in steps if step.get("uses") == "actions/checkout@v6")
        self.assertEqual(
            {"fetch-depth": "0", "persist-credentials": "false"},
            checkout.get("with"),
        )
        setup_python = next(step for step in steps if step.get("uses") == "actions/setup-python@v6")
        self.assertEqual({"python-version": "3.12"}, setup_python.get("with"))
        self.assertIn("python -m pip install --disable-pip-version-check -r requirements.txt", self.commands)

    def test_gwt_004_given_governance_workflow_when_checked_then_all_required_gates_run(self) -> None:
        command_text = "\n".join(self.commands)
        for command in REQUIRED_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, command_text)
        step_names = {
            step.get("name")
            for job in self.workflow["jobs"].values()
            for step in job["steps"]
        }
        self.assertIn("Validate registered source governance manifests", step_names)
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

    def test_gwt_007_given_source_registry_when_loaded_then_v050_manifest_is_exact(self) -> None:
        registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual("1.0", registry["schema_version"])
        self.assertEqual(
            [
                {
                    "id": "v050-published-path-disposition",
                    "path": (
                        ".dev/workflows/2026-07-21-v0-5-0-development/"
                        "evidence/v050-published-path-disposition.yaml"
                    ),
                }
            ],
            registry["manifests"],
        )


if __name__ == "__main__":
    unittest.main()
