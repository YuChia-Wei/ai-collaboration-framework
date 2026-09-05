#!/usr/bin/env python3
"""Semantic lifecycle contracts for the repository's governed workflows."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / ".github/workflows"
WORKFLOW_NAMES = {
    "governance.yml",
    "nightly-full-readiness.yml",
    "portable-gates.yml",
    "package-candidate.yml",
    "publish-release.yml",
    "test-fixture-acceleration.yml",
}
PR_CONCURRENCY = {
    "group": "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}",
    "cancel-in-progress": "${{ github.event_name == 'pull_request' }}",
}
PUBLISH_CONCURRENCY = {
    "group": "ai-context-release-${{ github.ref_name }}",
    "cancel-in-progress": "false",
}
NIGHTLY_READINESS_CONCURRENCY = {
    "group": "ai-context-nightly-full-readiness",
    "cancel-in-progress": "false",
}
FIXTURE_ACCELERATION_CONCURRENCY = {
    "group": "portable-test-fixture-${{ github.run_id }}",
    "cancel-in-progress": "false",
}
EXPECTED_TRIGGERS = {
    "governance.yml": {"pull_request", "workflow_dispatch"},
    "nightly-full-readiness.yml": {"schedule", "workflow_dispatch"},
    "portable-gates.yml": {"pull_request", "workflow_dispatch"},
    "package-candidate.yml": {"pull_request", "workflow_dispatch"},
    "publish-release.yml": {"push"},
    "test-fixture-acceleration.yml": {"workflow_dispatch"},
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
        "requirements.txt",
    },
    "package-candidate.yml": {
        ".agents/**",
        ".ai/distribution/**",
        ".ai/assets/**",
        ".ai/scripts/**",
        ".claude/**",
        ".dev/guides/**",
        ".dev/releases/**",
        ".dev/workflows/**",
        ".github/scripts/**",
        ".github/workflows/package-candidate.yml",
        ".github/workflows/publish-release.yml",
    },
}
EXPECTED_ARTIFACT_ACTIONS = {
    "governance.yml": ["actions/upload-artifact@v7"],
    "nightly-full-readiness.yml": ["actions/upload-artifact@v7"],
    "portable-gates.yml": ["actions/upload-artifact@v7"],
    "package-candidate.yml": ["actions/upload-artifact@v7"],
    "publish-release.yml": [
        "actions/upload-artifact@v7",
        "actions/download-artifact@v8",
        "actions/upload-artifact@v7",
        "actions/upload-artifact@v7",
    ],
    "test-fixture-acceleration.yml": ["actions/upload-artifact@v7"],
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
    def test_rel018_promotion_and_provider_comparison_gate_publication(self):
        candidate = {s["name"]: s for s in steps(load_workflow("package-candidate.yml"))}
        self.assertIn("steps.promotion.outputs.required == 'false'", candidate["Build deterministic archives"]["if"])
        self.assertIn('"true"', candidate["Stage admitted candidate archives"]["run"])
        self.assertIn("manage-release-asset-identity.py stage", candidate["Stage admitted candidate archives"]["run"])
        publication = load_workflow("publish-release.yml")
        build = {s["name"]: s for s in publication["jobs"]["build"]["steps"]}
        self.assertEqual("steps.promotion.outputs.required == 'false'", build["Build deterministic archives from legacy tag"]["if"])
        self.assertEqual("steps.promotion.outputs.required == 'true'", build["Stage admitted archives without rebuilding"]["if"])
        self.assertNotIn("build-ai-context-package", build["Stage admitted archives without rebuilding"]["run"])
        publish = publication["jobs"]["publish"]["steps"]
        names = [step["name"] for step in publish]
        uploaded = next(step for step in publish if step["name"] == "Upload or verify release assets")
        observed = next(step for step in publish if step["name"] == "Read back published asset identity")
        self.assertIn("manage-release-asset-identity.py provider", uploaded["run"])
        self.assertIn("--allow-draft", uploaded["run"])
        self.assertLess(names.index("Upload or verify release assets"), names.index("Publish verified draft"))
        self.assertLess(names.index("Publish verified draft"), names.index("Read back published asset identity"))
        self.assertIn("manage-release-asset-identity.py provider", observed["run"])
        self.assertNotIn("--allow-draft", observed["run"])
        self.assertIn('--raw-provider-output "${RUNNER_TEMP}/uploaded-provider.json"', uploaded["run"])
        self.assertIn('--raw-provider-output "${RUNNER_TEMP}/published-provider.json"', observed["run"])
        retained = next(step for step in publish if step["name"] == "Retain asset publication read-back")
        self.assertEqual("always()", retained["if"])
        self.assertIn("uploaded-provider.json", retained["with"]["path"])
        self.assertIn("published-provider.json", retained["with"]["path"])
        for job in ("publish", "reconcile-provider"):
            for step in publication["jobs"][job]["steps"]:
                if step.get("uses") == "actions/upload-artifact@v7":
                    self.assertIn("${{ github.run_attempt }}", step["with"]["name"])

    def setUp(self) -> None:
        actual_names = {path.name for path in WORKFLOW_DIR.glob("*.yml")}
        missing_contract_workflows = WORKFLOW_NAMES - actual_names
        self.assertFalse(
            missing_contract_workflows,
            f"Missing governed workflows: {sorted(missing_contract_workflows)}",
        )
        self.workflows = {
            name: load_workflow(name)
            for name in sorted(WORKFLOW_NAMES)
        }

    def test_gwt_001_given_governed_workflows_when_loaded_then_triggers_match_their_contracts(self) -> None:
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
        expected_disposition_activities = ["opened", "synchronize", "reopened", "edited"]
        for name in ("governance.yml", "portable-gates.yml"):
            with self.subTest(workflow=name):
                self.assertEqual(
                    expected_disposition_activities,
                    self.workflows[name]["on"]["pull_request"]["types"],
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
        self.assertEqual(
            NIGHTLY_READINESS_CONCURRENCY,
            self.workflows["nightly-full-readiness.yml"].get("concurrency"),
        )
        self.assertEqual(
            FIXTURE_ACCELERATION_CONCURRENCY,
            self.workflows["test-fixture-acceleration.yml"].get("concurrency"),
        )

    def test_gwt_002a_given_portable_gate_when_steps_are_read_then_no_dotnet_sdk_is_selected(self) -> None:
        workflow = self.workflows["portable-gates.yml"]
        serialized_steps = "\n".join(
            str(value)
            for step in steps(workflow)
            for value in step.values()
        )
        self.assertNotIn("setup-dotnet", serialized_steps)
        self.assertNotIn("global-json-file", serialized_steps)
        self.assertNotIn("global.json", workflow["on"]["pull_request"]["paths"])
        self.assertNotIn("tools/**", workflow["on"]["pull_request"]["paths"])

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
                "name": "${{ steps.release.outputs.package_id }}-${{ env.CANDIDATE_COMMIT }}",
                "retention-days": "14",
                "compression-level": "0",
                "if-no-files-found": "error",
                "path": (
                    "${{ runner.temp }}/candidate-assets/${{ steps.release.outputs.package_id }}.zip\n"
                    "${{ runner.temp }}/candidate-assets/${{ steps.release.outputs.package_id }}.zip.sha256\n"
                    "${{ runner.temp }}/candidate-assets/${{ steps.release.outputs.package_id }}.tar.gz\n"
                    "${{ runner.temp }}/candidate-assets/${{ steps.release.outputs.package_id }}.tar.gz.sha256\n"
                    "${{ runner.temp }}/release-body.md\n"
                    "${{ runner.temp }}/source-dispositions.json\n"
                    "${{ runner.temp }}/source-dispositions.md\n"
                    "${{ runner.temp }}/v0151-actual-admission/**\n"
                    "${{ runner.temp }}/v016-actual-admission/**\n"
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
        ][2]
        self.assertEqual(
            {
                "name": (
                    "provider-reconciliation-${{ needs.build.outputs.version }}-"
                    "${{ needs.build.outputs.commit }}-attempt-${{ github.run_attempt }}"
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
            "nightly-full-readiness.yml": {
                "nightly-full-readiness": ("60", "ubuntu-latest")
            },
            "portable-gates.yml": {
                "prerequisite-posix": ("15", "ubuntu-latest"),
                "prerequisite-windows": ("15", "windows-latest"),
                "quick": ("30", "ubuntu-latest"),
            },
            "package-candidate.yml": {"package": ("30", "ubuntu-latest")},
            "publish-release.yml": {
                "build": ("15", "ubuntu-latest"),
                "publish": ("15", "ubuntu-latest"),
                "reconcile-provider": ("15", "ubuntu-latest"),
            },
            "test-fixture-acceleration.yml": {
                "benchmark": ("30", "self-hosted")
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
        selected_commit = "${{ github.event.pull_request.head.sha || github.sha }}"
        candidate_workflow = self.workflows["package-candidate.yml"]
        candidate_job = candidate_workflow["jobs"]["package"]
        candidate_checkout = next(
            step
            for step in steps(candidate_workflow)
            if step.get("name") == "Check out candidate commit"
        )
        self.assertEqual({"CANDIDATE_COMMIT": selected_commit}, candidate_job.get("env"))
        self.assertEqual("${{ env.CANDIDATE_COMMIT }}", candidate_checkout["with"].get("ref"))
        self.assertEqual(
            "${{ env.CANDIDATE_COMMIT }}",
            candidate_checkout["with"]["ref"],
        )

        expected_commands = {
            "Resolve candidate and render release body": ('--commit "${CANDIDATE_COMMIT}"', 1),
            "Validate exact candidate state": ('--commit "${CANDIDATE_COMMIT}"', 1),
            "Build deterministic archives": ('--ref "${CANDIDATE_COMMIT}"', 1),
            "Validate v0.15.1 actual clean install and v0.15.0 upgrade": (
                '--subject-sha "${CANDIDATE_COMMIT}"',
                1,
            ),
            "Render source disposition read-back": ('--ref "${CANDIDATE_COMMIT}"', 2),
        }
        candidate_steps = {step["name"]: step for step in steps(candidate_workflow)}
        for step_name, (expected_argument, expected_count) in expected_commands.items():
            with self.subTest(step=step_name):
                step = candidate_steps[step_name]
                command = step["run"]
                self.assertEqual(expected_count, command.count(expected_argument))
                self.assertNotIn("${GITHUB_SHA}", command)
                self.assertNotIn("${{ github.sha }}", command)
                self.assertNotIn(selected_commit, command)

        candidate_state_step = candidate_steps["Validate exact candidate state"]
        self.assertEqual({"GH_TOKEN": "${{ github.token }}"}, candidate_state_step.get("env"))

        actual_upgrade_step = candidate_steps[
            "Validate v0.15.1 actual clean install and v0.15.0 upgrade"
        ]
        self.assertEqual(
            "steps.release.outputs.available == 'true' && "
            "steps.release.outputs.version == 'v0.15.1'",
            actual_upgrade_step["if"],
        )
        self.assertIn(
            '--candidate-archive "${RUNNER_TEMP}/candidate-assets/${{ steps.release.outputs.package_id }}.zip"',
            actual_upgrade_step["run"],
        )
        self.assertIn(
            '--previous-archive "${RUNNER_TEMP}/previous-package-0.15.0/'
            'ai-collaboration-framework-v0.15.0.zip"',
            actual_upgrade_step["run"],
        )

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
        incoming_validation = next(
            step
            for step in self.workflows["package-candidate.yml"]["jobs"]["package"]["steps"]
            if step.get("name") == "Validate freshly extracted incoming candidate"
        )
        self.assertIn("python -m zipfile -e", incoming_validation["run"])
        self.assertIn("validate-ai-context-payload.py", incoming_validation["run"])
        self.assertIn("--package-root .", incoming_validation["run"])

    def test_gwt_008_given_nightly_readiness_when_inspected_then_execution_requires_a_tracked_gate_change(self) -> None:
        workflow = self.workflows["nightly-full-readiness.yml"]
        self.assertEqual(
            [{"cron": "23 17 * * *"}],
            workflow["on"]["schedule"],
        )

        job = workflow["jobs"]["nightly-full-readiness"]
        self.assertEqual("${{ false }}", job.get("if"))
        self.assertNotIn("strategy", job)
        self.assertNotIn("needs", job)
        self.assertEqual({"contents": "read"}, job.get("permissions"))

        aggregate_steps = [
            step
            for step in job["steps"]
            if ".ai/scripts/check-all.sh" in step.get("run", "")
        ]
        self.assertEqual(
            ["bash .ai/scripts/check-all.sh --profile nightly-full"],
            [step["run"] for step in aggregate_steps],
        )

        checkout = next(
            step
            for step in job["steps"]
            if step.get("uses") == "actions/checkout@v6"
        )
        self.assertEqual(
            {"fetch-depth": "0", "persist-credentials": "false"},
            checkout.get("with"),
        )

        evidence_upload = next(
            step
            for step in job["steps"]
            if step.get("uses") == "actions/upload-artifact@v7"
        )
        self.assertEqual("always()", evidence_upload.get("if"))
        self.assertEqual(
            {
                "name": (
                    "ai-context-validation-nightly-full-"
                    "${{ github.run_id }}-${{ github.run_attempt }}"
                ),
                "retention-days": "30",
                "compression-level": "0",
                "if-no-files-found": "error",
                "path": "artifacts/validation",
            },
            evidence_upload.get("with"),
        )

    def test_gwt_009_given_existing_admission_output_when_helper_runs_then_terminal_evidence_is_not_overwritten(self) -> None:
        helper = REPO_ROOT / ".github/scripts/validate-v0151-actual-upgrade.py"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing-output"
            output.mkdir()
            terminal = output / "terminal.json"
            original = b'{"outcome":"retained"}\n'
            terminal.write_bytes(original)
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--candidate-archive",
                    str(Path(temporary) / "missing-candidate.zip"),
                    "--previous-archive",
                    str(Path(temporary) / "missing-previous.zip"),
                    "--subject-sha",
                    "1" * 40,
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            self.assertEqual(1, result.returncode)
            self.assertEqual(original, terminal.read_bytes())
            self.assertIn("output-already-exists", result.stderr)


if __name__ == "__main__":
    unittest.main()
