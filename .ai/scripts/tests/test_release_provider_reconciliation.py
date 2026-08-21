#!/usr/bin/env python3
"""Given-When-Then tests for release provider reconciliation."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
