#!/usr/bin/env python3
"""Given-When-Then tests for release provider reconciliation."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/reconcile-ai-context-release-provider.py"
SPEC = importlib.util.spec_from_file_location("release_provider_reconciliation", MODULE_PATH)
assert SPEC and SPEC.loader
RECONCILIATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECONCILIATION)


VERSION = "v0.12.0"
REPOSITORY = "YuChia-Wei/ai-collaboration-framework"


def expectation(*, state: str, reason: str | None, status: str, published: str) -> dict:
    return {
        "issue_state": state,
        "state_reason": reason,
        "project": {
            "Status": status,
            "Priority": "P1 High",
            "Owner review": "Approved",
            "Target release": VERSION,
            "Published in": published,
        },
    }


def release_record() -> dict:
    return {
        "version": VERSION,
        "status": "validated",
        "planning": {"github_issue_refs": ["#10", "#11"]},
        "provider_reconciliation": {
            "schema_version": "1.0",
            "provider": "github",
            "repository": REPOSITORY,
            "project_owner": "YuChia-Wei",
            "project_number": 3,
            "included_issue_refs_source": "planning.github_issue_refs",
            "included_work": {
                "prepublication": expectation(
                    state="closed",
                    reason="completed",
                    status="Done",
                    published="Not yet published",
                ),
                "postpublication": expectation(
                    state="closed",
                    reason="completed",
                    status="Done",
                    published=VERSION,
                ),
            },
            "coordination": {
                "issue_refs": ["#169"],
                "prepublication": expectation(
                    state="open",
                    reason=None,
                    status="Planned",
                    published="Not applicable — not a release item",
                ),
                "postpublication": expectation(
                    state="closed",
                    reason="completed",
                    status="Done",
                    published="Not applicable — not a release item",
                ),
            },
        },
    }


def scoped_release_record() -> dict:
    data = release_record()
    contract = data["provider_reconciliation"]
    contract["schema_version"] = "1.1"
    contract["included_work"]["prepublication"]["project"] = {"Status": "Done"}
    contract["included_work"]["postpublication"]["project"] = {"Status": "Done"}
    contract["coordination"]["prepublication"]["project"] = {}
    contract["coordination"]["postpublication"]["project"] = {"Status": "Done"}
    return data


class FixtureRepo:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        release_dir = self.root / ".dev/releases" / VERSION
        release_dir.mkdir(parents=True)
        self.write(release_record())

    def write(self, data: dict) -> None:
        path = self.root / ".dev/releases" / VERSION / "release.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def close(self) -> None:
        self.temp.cleanup()


class FakeGh:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []
        self.mutations: list[list[str]] = []
        self.project = {"id": "project-id", "closed": False}
        self.fields = []
        for index, (field, options) in enumerate(
            {
                "Status": ["Planned", "Done"],
                "Priority": ["P1 High"],
                "Owner review": ["Approved"],
                "Target release": [VERSION],
                "Published in": [
                    "Not yet published",
                    "Not applicable — not a release item",
                    VERSION,
                ],
            }.items()
        ):
            self.fields.append(
                {
                    "id": f"field-{index}",
                    "name": field,
                    "options": [
                        {"id": f"option-{index}-{option_index}", "name": name}
                        for option_index, name in enumerate(options)
                    ],
                }
            )
        self.issues = {
            10: {"number": 10, "state": "CLOSED", "stateReason": "COMPLETED"},
            11: {"number": 11, "state": "CLOSED", "stateReason": "COMPLETED"},
            169: {"number": 169, "state": "OPEN", "stateReason": ""},
        }
        self.items = {
            10: self.item(10, "Done", "Not yet published"),
            11: self.item(11, "Done", "Not yet published"),
            169: self.item(169, "Planned", "Not applicable — not a release item"),
        }
        self.release = {
            "isDraft": False,
            "isPrerelease": False,
            "tagName": VERSION,
            "url": f"https://github.com/{REPOSITORY}/releases/tag/{VERSION}",
        }

    @staticmethod
    def item(number: int, status: str, published: str) -> dict:
        return {
            "id": f"item-{number}",
            "content": {"number": number, "repository": REPOSITORY},
            "status": status,
            "priority": "P1 High",
            "owner review": "Approved",
            "target release": VERSION,
            "published in": published,
        }

    def __call__(self, command: list[str]) -> str:
        self.commands.append(command)
        if command[1:3] == ["project", "view"]:
            return json.dumps(self.project)
        if command[1:3] == ["project", "field-list"]:
            return json.dumps({"fields": self.fields})
        if command[1:3] == ["project", "item-list"]:
            return json.dumps({"items": list(self.items.values())})
        if command[1:3] == ["issue", "view"]:
            return json.dumps(self.issues[int(command[3])])
        if command[1:3] == ["release", "view"]:
            return json.dumps(self.release)
        if command[1:3] == ["project", "item-edit"]:
            self.mutations.append(command)
            item_id = command[command.index("--id") + 1]
            field_id = command[command.index("--field-id") + 1]
            option_id = command[command.index("--single-select-option-id") + 1]
            field = next(value for value in self.fields if value["id"] == field_id)
            option = next(value for value in field["options"] if value["id"] == option_id)
            item = next(value for value in self.items.values() if value["id"] == item_id)
            item[field["name"].lower()] = option["name"]
            return ""
        if command[1:3] == ["issue", "close"]:
            self.mutations.append(command)
            issue = self.issues[int(command[3])]
            issue["state"] = "CLOSED"
            issue["stateReason"] = "COMPLETED"
            return ""
        raise AssertionError(f"unexpected command: {command}")


class ReleaseProviderReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self.gh = FakeGh()

    def tearDown(self) -> None:
        self.fixture.close()

    def execute(self, phase: str) -> dict:
        return RECONCILIATION.execute(
            root=self.fixture.root,
            version=VERSION,
            phase=phase,
            runner=self.gh,
        )

    def test_gwt_001_given_exact_prepublication_state_when_preflight_runs_then_it_is_read_only(self) -> None:
        result = self.execute("preflight")
        self.assertEqual("passed", result["status"])
        self.assertEqual([], self.gh.mutations)
        self.assertIsNone(result["release_url"])

    def test_gwt_001a_given_a_valid_contract_when_checked_on_a_pr_then_no_provider_command_runs(self) -> None:
        result = self.execute("contract")
        self.assertEqual("passed", result["status"])
        self.assertEqual("contract", result["phase"])
        self.assertEqual([], self.gh.commands)

    def test_gwt_002_given_project_drift_when_preflight_runs_then_it_fails_closed(self) -> None:
        self.gh.items[10]["priority"] = "P2 Normal"
        with self.assertRaisesRegex(
            RECONCILIATION.ProviderReconciliationError,
            "Project field 'Priority' must be 'P1 High'",
        ):
            self.execute("preflight")

    def test_gwt_003_given_project_cli_owner_type_failure_when_preflight_runs_then_it_reports_secret_free_access_guidance(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["gh", "project", "view", "3"],
            returncode=1,
            stdout="",
            stderr="unknown owner type: super-secret",
        )
        with mock.patch.object(RECONCILIATION.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(
                RECONCILIATION.ProviderReconciliationError,
                "GitHub Projects v2 read access",
            ) as captured:
                RECONCILIATION.subprocess_runner(["gh", "project", "view", "3"])
        self.assertNotIn("super-secret", str(captured.exception))

    def test_gwt_003_given_stable_release_when_apply_runs_then_items_and_coordination_converge(self) -> None:
        result = self.execute("apply")
        self.assertEqual("passed", result["status"])
        self.assertEqual(VERSION, self.gh.items[10]["published in"])
        self.assertEqual(VERSION, self.gh.items[11]["published in"])
        self.assertEqual("CLOSED", self.gh.issues[169]["state"])
        self.assertEqual("Done", self.gh.items[169]["status"])
        self.assertEqual(4, len(self.gh.mutations))

    def test_gwt_004_given_draft_release_when_apply_runs_then_no_provider_state_is_mutated(self) -> None:
        self.gh.release["isDraft"] = True
        with self.assertRaisesRegex(
            RECONCILIATION.ProviderReconciliationError,
            "requires a stable hosted release",
        ):
            self.execute("apply")
        self.assertEqual([], self.gh.mutations)

    def test_gwt_005_given_already_reconciled_state_when_apply_retries_then_it_is_idempotent(self) -> None:
        self.execute("apply")
        self.gh.mutations.clear()
        result = self.execute("apply")
        self.assertEqual("passed", result["status"])
        self.assertEqual([], self.gh.mutations)

    def test_gwt_006_given_coordination_ref_in_included_scope_when_loaded_then_it_fails_closed(self) -> None:
        data = release_record()
        data["provider_reconciliation"]["coordination"]["issue_refs"] = ["#10"]
        self.fixture.write(copy.deepcopy(data))
        with self.assertRaisesRegex(
            RECONCILIATION.ProviderReconciliationError,
            "must be disjoint",
        ):
            self.execute("preflight")

    def test_gwt_007_given_v11_scoped_fields_when_advisory_values_are_absent_then_preflight_passes(self) -> None:
        self.fixture.write(scoped_release_record())
        for item in self.gh.items.values():
            item["priority"] = None
            item["owner review"] = None
            item["target release"] = None
            item["published in"] = None
        self.gh.items[169]["status"] = "Inbox"

        result = self.execute("preflight")

        self.assertEqual("passed", result["status"])
        self.assertEqual([], self.gh.mutations)

    def test_gwt_008_given_v11_scoped_fields_when_apply_runs_then_only_required_state_converges(self) -> None:
        self.fixture.write(scoped_release_record())
        self.gh.items[169]["status"] = "Inbox"

        result = self.execute("apply")

        self.assertEqual("passed", result["status"])
        self.assertEqual("CLOSED", self.gh.issues[169]["state"])
        self.assertEqual("Done", self.gh.items[169]["status"])
        self.assertEqual(2, len(self.gh.mutations))
        self.assertFalse(
            any(
                command[1:3] == ["project", "item-edit"] and "field-4" in command
                for command in self.gh.mutations
            )
        )

    def test_gwt_009_given_v10_contract_when_a_project_field_is_missing_then_it_still_fails_closed(self) -> None:
        data = release_record()
        del data["provider_reconciliation"]["included_work"]["prepublication"]["project"][
            "Target release"
        ]
        self.fixture.write(data)

        with self.assertRaisesRegex(
            RECONCILIATION.ProviderReconciliationError,
            "project is missing fields:.*Target release",
        ):
            self.execute("contract")

    def test_given_reconciled_release_when_verify_runs_then_it_never_mutates_provider_state(self) -> None:
        self.gh.items[10]["published in"] = VERSION
        self.gh.items[11]["published in"] = VERSION
        self.gh.issues[169]["state"] = "CLOSED"
        self.gh.issues[169]["stateReason"] = "COMPLETED"
        self.gh.items[169]["status"] = "Done"

        result = self.execute("verify")

        self.assertEqual("passed", result["status"])
        self.assertEqual("verify", result["phase"])
        self.assertIsNotNone(result["release_url"])
        self.assertEqual([], self.gh.mutations)

    def test_given_unreconciled_release_when_verify_runs_then_it_fails_without_repair(self) -> None:
        before_issues = copy.deepcopy(self.gh.issues)
        before_items = copy.deepcopy(self.gh.items)

        with self.assertRaises(RECONCILIATION.ProviderReconciliationError):
            self.execute("verify")

        self.assertEqual([], self.gh.mutations)
        self.assertEqual(before_issues, self.gh.issues)
        self.assertEqual(before_items, self.gh.items)

    def test_gwt_010_given_v11_contract_when_an_unknown_project_field_is_present_then_it_fails_closed(self) -> None:
        data = scoped_release_record()
        data["provider_reconciliation"]["included_work"]["prepublication"]["project"][
            "Release train"
        ] = VERSION
        self.fixture.write(data)

        with self.assertRaisesRegex(
            RECONCILIATION.ProviderReconciliationError,
            "project has unknown fields:.*Release train",
        ):
            self.execute("contract")


class HostedProviderCheckTests(unittest.TestCase):
    def test_hosted_probe_distinguishes_rest_access_from_project_access_without_live_credentials(self) -> None:
        if os.name == "nt":
            bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
            if not bash.is_file():
                self.skipTest("Git Bash is required for the hosted shell regression")
        else:
            bash = shutil.which("bash")
            if not bash:
                self.skipTest("Bash is required for the hosted shell regression")
        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release-provider-preflight.yml").read_text(encoding="utf-8")
        )
        step = next(step for step in workflow["jobs"]["provider-check"]["steps"] if step.get("id") == "provider")
        interceptors = '''gh() {
          echo "intercepted-gh:$*"
          if [[ "$1" == "api" ]]; then return "$MOCK_REST_EXIT"; fi
        }
        python() { echo "intercepted-provider"; return "$MOCK_PROVIDER_EXIT"; }
        '''
        cases = [
            ("missing-token", "", "0", "0", False, False, False),
            ("rest-failure", "synthetic-provider-token", "1", "0", False, True, False),
            ("project-failure", "synthetic-provider-token", "0", "1", False, True, True),
            ("verified", "synthetic-provider-token", "0", "0", True, True, True),
        ]
        for label, token, rest_exit, provider_exit, success, rest_called, provider_called in cases:
            with self.subTest(label=label):
                env = dict(os.environ, GH_TOKEN=token, MOCK_REST_EXIT=rest_exit,
                           MOCK_PROVIDER_EXIT=provider_exit, VERSION=VERSION,
                           PHASE="verify", RUNNER_TEMP="/unused-intercepted-output")
                result = subprocess.run(
                    [str(bash), "--noprofile", "--norc", "-e"],
                    input=interceptors + step["run"], env=env,
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(success, result.returncode == 0, result.stderr)
                self.assertEqual(rest_called, "intercepted-gh:api rate_limit --silent" in result.stdout)
                self.assertEqual(provider_called, "intercepted-provider" in result.stdout)
                self.assertNotIn("synthetic-provider-token", result.stdout + result.stderr)
                if label == "rest-failure":
                    self.assertIn("REST probe failed before Project lookup", result.stderr)
                if provider_called:
                    self.assertIn("Projects access is still unverified", result.stdout)

    def test_dispatch_keeps_existing_credential_on_main_and_read_only_phases(self) -> None:
        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release-provider-preflight.yml").read_text(encoding="utf-8")
        )
        # PyYAML's YAML 1.1 loader treats the Actions key "on" as True.
        triggers = workflow.get("on", workflow.get(True))
        self.assertEqual({"workflow_dispatch"}, set(triggers))
        phase = triggers["workflow_dispatch"]["inputs"]["phase"]
        self.assertEqual({"preflight", "verify"}, set(phase["options"]))
        self.assertEqual("verify", phase["default"])
        self.assertEqual({}, workflow["permissions"])
        job = workflow["jobs"]["provider-check"]
        self.assertEqual("github.ref == 'refs/heads/main'", job["if"])
        self.assertEqual("ai-context-release", job["environment"])
        self.assertEqual({"contents": "read"}, job["permissions"])
        self.assertEqual("${{ github.sha }}", job["steps"][0]["with"]["ref"])
        self.assertIs(False, job["steps"][0]["with"]["persist-credentials"])
        secret_steps = [step for step in job["steps"] if "GH_TOKEN" in step.get("env", {})]
        self.assertEqual(1, len(secret_steps))
        self.assertEqual("provider", secret_steps[0]["id"])
        self.assertEqual("${{ secrets.RELEASE_PROVIDER_TOKEN }}", secret_steps[0]["env"]["GH_TOKEN"])
        request = next(step for step in job["steps"] if step["name"] == "Validate read-only request")
        self.assertIn("preflight|verify) ;;", request["run"])
        self.assertIn('*) echo "Only read-only preflight or verify is allowed." >&2; exit 1', request["run"])
        self.assertFalse(secret_steps[0].get("continue-on-error", False))
        self.assertNotIn("--phase apply", secret_steps[0]["run"])
        retention = job["steps"][-1]
        self.assertEqual("always()", retention["if"])
        self.assertEqual("${{ runner.temp }}/provider-check/*.json", retention["with"]["path"])


if __name__ == "__main__":
    unittest.main()
