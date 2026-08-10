#!/usr/bin/env python3
"""Exact lifecycle contracts for the repository's four GitHub workflows."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / ".github/workflows"
WORKFLOW_NAMES = {
    "governance.yml",
    "portable-gates.yml",
    "package-candidate.yml",
    "publish-release.yml",
}
PR_CONCURRENCY = {
    "group": "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}",
    "cancel-in-progress": "${{ github.event_name == 'pull_request' }}",
}
PUBLISH_CONCURRENCY = {
    "group": "ai-context-release-${{ github.ref_name }}",
    "cancel-in-progress": "false",
}
EXPECTED_TRIGGERS = {
    "governance.yml": {"pull_request", "workflow_dispatch"},
    "portable-gates.yml": {"pull_request", "workflow_dispatch"},
    "package-candidate.yml": {"pull_request", "workflow_dispatch"},
    "publish-release.yml": {"push"},
}
EXPECTED_PR_PATHS = {
    "portable-gates.yml": {
        ".ai/**",
        ".agents/**",
        ".claude/**",
        ".codex/**",
        ".dev/assessments/**",
        ".dev/backlog/**",
        ".dev/standards/**",
        ".dev/workflows/**",
        ".github/agents/**",
        ".github/workflows/**",
        "tools/**",
        "global.json",
        "requirements.txt",
    },
    "package-candidate.yml": {
        ".ai/distribution/**",
        ".ai/scripts/**",
        ".dev/releases/**",
        ".github/workflows/package-candidate.yml",
        ".github/workflows/publish-release.yml",
    },
}
EXPECTED_ARTIFACT_ACTIONS = {
    "governance.yml": ["actions/upload-artifact@v7"],
    "portable-gates.yml": ["actions/upload-artifact@v7"],
    "package-candidate.yml": ["actions/upload-artifact@v7"],
    "publish-release.yml": [
        "actions/upload-artifact@v7",
        "actions/download-artifact@v8",
        "actions/upload-artifact@v7",
    ],
}
MUTATING_COMMAND = re.compile(
    r"(?:\bgh\s+release\s+(?:create|delete(?:-asset)?|edit|upload)\b|"
    r"\bgh\s+issue\s+close\b|"
    r"\bgh\s+project\s+item-edit\b|"
    r"\bgit\s+(?:push|commit)\b|"
    r"\bgit\s+tag\s+(?:--(?:annotate|delete)|-[ad])\b)",
    re.IGNORECASE,
)


def load_workflow(name: str) -> dict:
    """Load YAML without coercing GitHub's ``on`` key to a boolean."""
    path = WORKFLOW_DIR / name
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def steps(workflow: dict) -> list[dict]:
    return [
        step
        for job in workflow["jobs"].values()
        for step in job.get("steps", [])
        if isinstance(step, dict)
    ]


class GitHubWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        actual_names = {path.name for path in WORKFLOW_DIR.glob("*.yml")}
        self.assertEqual(WORKFLOW_NAMES, actual_names)
        self.workflows = {
            name: load_workflow(name)
            for name in sorted(WORKFLOW_NAMES)
        }

    def test_gwt_001_given_four_workflows_when_loaded_then_triggers_are_exact(self) -> None:
        for name, workflow in self.workflows.items():
            with self.subTest(workflow=name):
                self.assertEqual(EXPECTED_TRIGGERS[name], set(workflow["on"]))

        self.assertEqual(
            ["v*"],
            self.workflows["publish-release.yml"]["on"]["push"]["tags"],
        )
        self.assertIn(
            ".dev/assessments/**",
            self.workflows["portable-gates.yml"]["on"]["pull_request"]["paths"],
        )
        for name, expected_paths in EXPECTED_PR_PATHS.items():
            with self.subTest(workflow=name):
                self.assertEqual(
                    expected_paths,
                    set(self.workflows[name]["on"]["pull_request"]["paths"]),
                )
        governance_paths = self.workflows["governance.yml"]["on"]["pull_request"]["paths"]
        self.assertFalse(
            any("v0-5-0-development" in path for path in governance_paths),
            "General governance triggers must not encode a concrete release workflow",
        )

    def test_gwt_002_given_overlapping_pr_checks_when_superseded_then_only_latest_run_continues(self) -> None:
        for name in (
            "governance.yml",
            "portable-gates.yml",
            "package-candidate.yml",
        ):
            with self.subTest(workflow=name):
                self.assertEqual(PR_CONCURRENCY, self.workflows[name].get("concurrency"))

        self.assertEqual(
            PUBLISH_CONCURRENCY,
            self.workflows["publish-release.yml"].get("concurrency"),
        )

    def test_gwt_003_given_workflow_jobs_when_permissions_checked_then_only_publish_mutates(self) -> None:
        for name, workflow in self.workflows.items():
            self.assertEqual({}, workflow.get("permissions"), name)
            for job_name, job in workflow["jobs"].items():
                with self.subTest(workflow=name, job=job_name):
                    if name == "publish-release.yml" and job_name == "publish":
                        expected = {"contents": "write"}
                    elif (
                        name == "package-candidate.yml" and job_name == "package"
                    ) or (
                        name == "publish-release.yml" and job_name == "build"
                    ):
                        expected = {"contents": "read", "issues": "read"}
                    else:
                        expected = {"contents": "read"}
                    self.assertEqual(expected, job.get("permissions"))

        for name in WORKFLOW_NAMES - {"publish-release.yml"}:
            command_text = "\n".join(
                step["run"] for step in steps(self.workflows[name]) if "run" in step
            )
            self.assertIsNone(MUTATING_COMMAND.search(command_text), name)

    def test_gwt_003a_given_release_commands_when_classified_then_download_is_read_only(self) -> None:
        self.assertIsNone(
            MUTATING_COMMAND.search('gh release download "v0.6.0" --pattern "*.zip"')
        )
        for command in (
            "gh release create v0.7.0",
            "gh release delete v0.7.0",
            "gh release delete-asset v0.7.0 package.zip",
            "gh release edit v0.7.0",
            "gh release upload v0.7.0 package.zip",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(MUTATING_COMMAND.search(command))

    def test_gwt_004_given_artifact_handoff_when_actions_checked_then_node24_versions_are_exact(self) -> None:
        for name, workflow in self.workflows.items():
            artifact_actions = [
                step["uses"]
                for step in steps(workflow)
                if step.get("uses", "").startswith(
                    ("actions/upload-artifact@", "actions/download-artifact@")
                )
            ]
            with self.subTest(workflow=name):
                self.assertEqual(EXPECTED_ARTIFACT_ACTIONS[name], artifact_actions)

        candidate_upload = next(
            step
            for step in steps(self.workflows["package-candidate.yml"])
            if step.get("uses") == "actions/upload-artifact@v7"
        )
        self.assertEqual(
            {
                "name": "${{ steps.release.outputs.package_id }}-${{ github.sha }}",
                "retention-days": "14",
                "compression-level": "0",
                "if-no-files-found": "error",
                "path": (
                    "dist/${{ steps.release.outputs.package_id }}.zip\n"
                    "dist/${{ steps.release.outputs.package_id }}.zip.sha256\n"
                    "dist/${{ steps.release.outputs.package_id }}.tar.gz\n"
                    "dist/${{ steps.release.outputs.package_id }}.tar.gz.sha256\n"
                    "${{ runner.temp }}/release-body.md\n"
                    "${{ runner.temp }}/source-dispositions.json\n"
                    "${{ runner.temp }}/source-dispositions.md\n"
                ),
            },
            candidate_upload["with"],
        )

        publish_steps = steps(self.workflows["publish-release.yml"])
        publish_upload = next(
            step
            for step in publish_steps
            if step.get("uses") == "actions/upload-artifact@v7"
        )
        self.assertEqual("7", publish_upload["with"]["retention-days"])
        self.assertEqual("0", publish_upload["with"]["compression-level"])
        self.assertEqual("error", publish_upload["with"]["if-no-files-found"])
        self.assertEqual(
            "release-${{ steps.release.outputs.package_id }}-${{ steps.tag.outputs.commit }}",
            publish_upload["with"]["name"],
        )
        publish_download = next(
            step
            for step in publish_steps
            if step.get("uses") == "actions/download-artifact@v8"
        )
        self.assertEqual(
            {
                "name": (
                    "release-${{ needs.build.outputs.package_id }}-"
                    "${{ needs.build.outputs.commit }}"
                ),
                "path": "dist",
            },
            publish_download["with"],
        )
        reconciliation_upload = [
            step
            for step in publish_steps
            if step.get("uses") == "actions/upload-artifact@v7"
        ][1]
        self.assertEqual(
            {
                "name": (
                    "provider-reconciliation-${{ needs.build.outputs.version }}-"
                    "${{ needs.build.outputs.commit }}"
                ),
                "retention-days": "30",
                "compression-level": "0",
                "if-no-files-found": "error",
                "path": "${{ runner.temp }}/provider-reconciliation.json",
            },
            reconciliation_upload["with"],
        )

    def test_gwt_005_given_jobs_when_cost_and_responsibility_checked_then_matrix_is_exact(self) -> None:
        expected_jobs = {
            "governance.yml": {"governance": ("15", "ubuntu-latest")},
            "portable-gates.yml": {
                "prerequisite-posix": ("15", "ubuntu-latest"),
                "prerequisite-windows": ("15", "windows-latest"),
                "quick": ("30", "ubuntu-latest"),
            },
            "package-candidate.yml": {"package": ("15", "ubuntu-latest")},
            "publish-release.yml": {
                "build": ("15", "ubuntu-latest"),
                "publish": ("15", "ubuntu-latest"),
                "reconcile-provider": ("15", "ubuntu-latest"),
            },
        }
        for name, jobs in expected_jobs.items():
            self.assertEqual(set(jobs), set(self.workflows[name]["jobs"]), name)
            for job_name, (timeout, runner) in jobs.items():
                job = self.workflows[name]["jobs"][job_name]
                self.assertEqual(timeout, job["timeout-minutes"])
                self.assertEqual(runner, job["runs-on"])
        self.assertEqual(
            "ai-context-release",
            self.workflows["publish-release.yml"]["jobs"]["publish"]["environment"],
        )
        self.assertEqual(
            "ai-context-release",
            self.workflows["publish-release.yml"]["jobs"]["reconcile-provider"]["environment"],
        )

    def test_gwt_006_given_candidate_state_requires_online_issue_readback_when_run_then_token_is_available(self) -> None:
        candidate_step = next(
            step
            for step in steps(self.workflows["package-candidate.yml"])
            if step.get("name") == "Validate exact candidate state"
        )
        self.assertEqual({"GH_TOKEN": "${{ github.token }}"}, candidate_step.get("env"))

    def test_gwt_007_given_project_write_token_when_workflows_checked_then_only_tag_jobs_receive_it(self) -> None:
        for name in WORKFLOW_NAMES - {"publish-release.yml"}:
            workflow_text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
            self.assertNotIn("RELEASE_PROVIDER_TOKEN", workflow_text, name)

        publish = self.workflows["publish-release.yml"]
        preflight_step = next(
            step
            for step in publish["jobs"]["publish"]["steps"]
            if step.get("name") == "Validate provider prepublication state"
        )
        self.assertEqual(
            {"GH_TOKEN": "${{ secrets.RELEASE_PROVIDER_TOKEN }}"},
            preflight_step.get("env"),
        )
        reconcile = publish["jobs"]["reconcile-provider"]
        self.assertNotIn("GH_TOKEN", reconcile["env"])
        privileged_steps = [
            step
            for step in reconcile["steps"]
            if step.get("env", {}).get("GH_TOKEN")
            == "${{ secrets.RELEASE_PROVIDER_TOKEN }}"
        ]
        self.assertEqual(
            [
                "Verify hosted publication without source closeout",
                "Reconcile and read back Issues and Project",
            ],
            [step["name"] for step in privileged_steps],
        )
        command_text = "\n".join(
            step["run"] for step in reconcile["steps"] if "run" in step
        )
        self.assertIn("--phase finalization", command_text)
        self.assertIn("--allow-current-workflow-run", command_text)
        self.assertIn("--phase apply", command_text)
        self.assertNotIn("git commit", command_text)

        candidate_contract = next(
            step
            for step in self.workflows["package-candidate.yml"]["jobs"]["package"]["steps"]
            if step.get("name") == "Validate provider reconciliation contract"
        )
        self.assertNotIn("env", candidate_contract)
        self.assertIn("--phase contract", candidate_contract["run"])


if __name__ == "__main__":
    unittest.main()
