#!/usr/bin/env python3
"""Validate and reconcile GitHub Issue/Project state for a governed release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/reconcile-ai-context-release-provider.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
OWNER_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ISSUE_REF_RE = re.compile(r"^#([1-9]\d*)$")
CONTRACT_KEYS = {
    "schema_version",
    "provider",
    "repository",
    "project_owner",
    "project_number",
    "included_issue_refs_source",
    "included_work",
    "coordination",
}
TRANSITION_KEYS = {"prepublication", "postpublication"}
EXPECTATION_KEYS = {"issue_state", "state_reason", "project"}
PROJECT_FIELDS = {
    "Status",
    "Priority",
    "Owner review",
    "Target release",
    "Published in",
}


class ProviderReconciliationError(ValueError):
    """A fail-closed provider reconciliation violation."""


Runner = Callable[[list[str]], str]


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProviderReconciliationError(f"{label} must be a mapping")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = sorted(set(value) - expected)
    missing = sorted(expected - set(value))
    if unknown:
        raise ProviderReconciliationError(f"{label} has unknown fields: {unknown}")
    if missing:
        raise ProviderReconciliationError(f"{label} is missing fields: {missing}")


def _non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProviderReconciliationError(f"{label} must be a non-empty string")
    return value


def _issue_number(value: object, label: str) -> int:
    issue_ref = _non_empty_string(value, label)
    match = ISSUE_REF_RE.fullmatch(issue_ref)
    if not match:
        raise ProviderReconciliationError(f"{label} must be a #<positive-integer> reference")
    return int(match.group(1))


def _expectation(value: object, label: str) -> dict[str, Any]:
    data = _mapping(value, label)
    _exact_keys(data, EXPECTATION_KEYS, label)
    issue_state = _non_empty_string(data.get("issue_state"), f"{label}.issue_state").lower()
    if issue_state not in {"open", "closed"}:
        raise ProviderReconciliationError(f"{label}.issue_state must be open or closed")
    state_reason = data.get("state_reason")
    if state_reason is not None:
        state_reason = _non_empty_string(state_reason, f"{label}.state_reason").lower()
        if state_reason not in {"completed", "not_planned", "reopened"}:
            raise ProviderReconciliationError(
                f"{label}.state_reason must be completed, not_planned, reopened, or null"
            )
    project = _mapping(data.get("project"), f"{label}.project")
    unknown = sorted(set(project) - PROJECT_FIELDS)
    if unknown:
        raise ProviderReconciliationError(f"{label}.project has unknown fields: {unknown}")
    if set(project) != PROJECT_FIELDS:
        missing = sorted(PROJECT_FIELDS - set(project))
        raise ProviderReconciliationError(f"{label}.project is missing fields: {missing}")
    normalized_project = {
        field: _non_empty_string(project.get(field), f"{label}.project.{field}")
        for field in sorted(PROJECT_FIELDS)
    }
    return {
        "issue_state": issue_state,
        "state_reason": state_reason,
        "project": normalized_project,
    }


def _transition(value: object, label: str) -> dict[str, dict[str, Any]]:
    data = _mapping(value, label)
    _exact_keys(data, TRANSITION_KEYS, label)
    return {
        phase: _expectation(data.get(phase), f"{label}.{phase}")
        for phase in sorted(TRANSITION_KEYS)
    }


def load_release_contract(root: Path, version: str) -> tuple[dict[str, Any], list[int]]:
    if not VERSION_RE.fullmatch(version):
        raise ProviderReconciliationError("version must be stable vMAJOR.MINOR.PATCH")
    release_path = root / ".dev" / "releases" / version / "release.yaml"
    try:
        release = yaml.safe_load(release_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ProviderReconciliationError(f"cannot load governed release record: {exc}") from exc
    release = _mapping(release, "release record")
    if release.get("version") != version:
        raise ProviderReconciliationError("release record version does not match the requested version")
    if release.get("status") != "validated":
        raise ProviderReconciliationError("provider reconciliation requires terminal source status validated")

    contract = _mapping(release.get("provider_reconciliation"), "provider_reconciliation")
    _exact_keys(contract, CONTRACT_KEYS, "provider_reconciliation")
    if contract.get("schema_version") != "1.0":
        raise ProviderReconciliationError("provider_reconciliation.schema_version must be 1.0")
    if contract.get("provider") != "github":
        raise ProviderReconciliationError("provider_reconciliation.provider must be github")
    repository = _non_empty_string(contract.get("repository"), "provider_reconciliation.repository")
    if not REPOSITORY_RE.fullmatch(repository):
        raise ProviderReconciliationError("provider_reconciliation.repository is invalid")
    owner = _non_empty_string(contract.get("project_owner"), "provider_reconciliation.project_owner")
    if not OWNER_RE.fullmatch(owner):
        raise ProviderReconciliationError("provider_reconciliation.project_owner is invalid")
    project_number = contract.get("project_number")
    if not isinstance(project_number, int) or isinstance(project_number, bool) or project_number < 1:
        raise ProviderReconciliationError("provider_reconciliation.project_number must be positive")
    if contract.get("included_issue_refs_source") != "planning.github_issue_refs":
        raise ProviderReconciliationError(
            "provider_reconciliation.included_issue_refs_source must be planning.github_issue_refs"
        )

    planning = _mapping(release.get("planning"), "planning")
    raw_included = planning.get("github_issue_refs")
    if not isinstance(raw_included, list) or not raw_included:
        raise ProviderReconciliationError("planning.github_issue_refs must be a non-empty list")
    included = [
        _issue_number(value, f"planning.github_issue_refs[{index}]")
        for index, value in enumerate(raw_included)
    ]
    if len(included) != len(set(included)):
        raise ProviderReconciliationError("planning.github_issue_refs must not contain duplicates")

    included_work = _transition(contract.get("included_work"), "provider_reconciliation.included_work")
    coordination = _mapping(contract.get("coordination"), "provider_reconciliation.coordination")
    _exact_keys(coordination, {"issue_refs", *TRANSITION_KEYS}, "provider_reconciliation.coordination")
    raw_coordination = coordination.get("issue_refs")
    if not isinstance(raw_coordination, list) or not raw_coordination:
        raise ProviderReconciliationError(
            "provider_reconciliation.coordination.issue_refs must be a non-empty list"
        )
    coordination_numbers = [
        _issue_number(value, f"provider_reconciliation.coordination.issue_refs[{index}]")
        for index, value in enumerate(raw_coordination)
    ]
    if len(coordination_numbers) != len(set(coordination_numbers)):
        raise ProviderReconciliationError("coordination issue_refs must not contain duplicates")
    if set(included) & set(coordination_numbers):
        raise ProviderReconciliationError("included and coordination issue refs must be disjoint")

    normalized = {
        "schema_version": "1.0",
        "provider": "github",
        "repository": repository,
        "project_owner": owner,
        "project_number": project_number,
        "included_work": included_work,
        "coordination": {
            "issue_numbers": coordination_numbers,
            "prepublication": _expectation(
                coordination.get("prepublication"),
                "provider_reconciliation.coordination.prepublication",
            ),
            "postpublication": _expectation(
                coordination.get("postpublication"),
                "provider_reconciliation.coordination.postpublication",
            ),
        },
    }
    return normalized, included


def subprocess_runner(command: list[str]) -> str:
    if not command or command[0] != "gh":
        raise ProviderReconciliationError("provider runner accepts only gh commands")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        diagnostics = "\n".join(
            part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
        )
        suffix = f": {diagnostics}" if diagnostics else ""
        raise ProviderReconciliationError(
            f"provider command failed ({' '.join(command[:3])}) with exit {completed.returncode}{suffix}"
        )
    return completed.stdout


def _json_command(runner: Runner, command: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(runner(command))
    except json.JSONDecodeError as exc:
        raise ProviderReconciliationError(f"{label} did not return valid JSON") from exc
    return _mapping(value, label)


def collect_snapshot(
    contract: dict[str, Any],
    included: list[int],
    runner: Runner,
    *,
    require_release: bool,
    version: str,
) -> dict[str, Any]:
    repository = contract["repository"]
    owner = contract["project_owner"]
    project_number = str(contract["project_number"])
    project = _json_command(
        runner,
        ["gh", "project", "view", project_number, "--owner", owner, "--format", "json"],
        "GitHub Project",
    )
    if project.get("closed") is not False:
        raise ProviderReconciliationError("governed GitHub Project must be open")
    fields_data = _json_command(
        runner,
        ["gh", "project", "field-list", project_number, "--owner", owner, "--format", "json"],
        "GitHub Project fields",
    )
    items_data = _json_command(
        runner,
        [
            "gh",
            "project",
            "item-list",
            project_number,
            "--owner",
            owner,
            "--limit",
            "1000",
            "--format",
            "json",
        ],
        "GitHub Project items",
    )
    raw_fields = fields_data.get("fields")
    raw_items = items_data.get("items")
    if not isinstance(raw_fields, list) or not isinstance(raw_items, list):
        raise ProviderReconciliationError("GitHub Project fields/items response is incomplete")

    issue_numbers = included + contract["coordination"]["issue_numbers"]
    issues: dict[int, dict[str, Any]] = {}
    items: dict[int, dict[str, Any]] = {}
    for issue_number in issue_numbers:
        issue = _json_command(
            runner,
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                repository,
                "--json",
                "number,state,stateReason,url",
            ],
            f"GitHub Issue #{issue_number}",
        )
        if issue.get("number") != issue_number:
            raise ProviderReconciliationError(f"GitHub Issue #{issue_number} identity mismatch")
        issues[issue_number] = issue
        matches = [
            item
            for item in raw_items
            if isinstance(item, dict)
            and isinstance(item.get("content"), dict)
            and item["content"].get("number") == issue_number
            and item["content"].get("repository") == repository
        ]
        if len(matches) != 1:
            raise ProviderReconciliationError(
                f"GitHub Project must contain exactly one item for Issue #{issue_number}; found {len(matches)}"
            )
        items[issue_number] = matches[0]

    release: dict[str, Any] | None = None
    if require_release:
        release = _json_command(
            runner,
            [
                "gh",
                "release",
                "view",
                version,
                "--repo",
                repository,
                "--json",
                "isDraft,isPrerelease,tagName,url",
            ],
            f"GitHub Release {version}",
        )
        if release.get("tagName") != version:
            raise ProviderReconciliationError("hosted release tag does not match the governed version")
        if release.get("isDraft") is not False or release.get("isPrerelease") is not False:
            raise ProviderReconciliationError("provider reconciliation requires a stable hosted release")

    return {
        "project": project,
        "fields": raw_fields,
        "issues": issues,
        "items": items,
        "release": release,
    }


def _actual_project_value(item: dict[str, Any], field: str) -> object:
    return item.get(field.lower())


def _validate_one(
    snapshot: dict[str, Any],
    issue_number: int,
    expectation: dict[str, Any],
    label: str,
) -> None:
    issue = snapshot["issues"][issue_number]
    actual_state = str(issue.get("state", "")).lower()
    if actual_state != expectation["issue_state"]:
        raise ProviderReconciliationError(
            f"{label} Issue #{issue_number} state must be {expectation['issue_state']}; got {actual_state or 'missing'}"
        )
    expected_reason = expectation["state_reason"]
    actual_reason = str(issue.get("stateReason", "")).lower() or None
    if expected_reason is not None and actual_reason != expected_reason:
        raise ProviderReconciliationError(
            f"{label} Issue #{issue_number} state reason must be {expected_reason}; got {actual_reason}"
        )
    item = snapshot["items"][issue_number]
    for field, expected in expectation["project"].items():
        actual = _actual_project_value(item, field)
        if actual != expected:
            raise ProviderReconciliationError(
                f"{label} Issue #{issue_number} Project field {field!r} must be {expected!r}; got {actual!r}"
            )


def validate_snapshot(
    contract: dict[str, Any],
    included: list[int],
    snapshot: dict[str, Any],
    phase: str,
) -> None:
    if phase not in TRANSITION_KEYS:
        raise ProviderReconciliationError(f"unknown provider phase: {phase}")
    for issue_number in included:
        _validate_one(snapshot, issue_number, contract["included_work"][phase], "included")
    for issue_number in contract["coordination"]["issue_numbers"]:
        _validate_one(snapshot, issue_number, contract["coordination"][phase], "coordination")


def validate_transition_snapshot(
    contract: dict[str, Any],
    included: list[int],
    snapshot: dict[str, Any],
) -> None:
    groups = [
        (included, contract["included_work"], "included"),
        (
            contract["coordination"]["issue_numbers"],
            contract["coordination"],
            "coordination",
        ),
    ]
    for issue_numbers, transition, label in groups:
        before = transition["prepublication"]
        after = transition["postpublication"]
        for issue_number in issue_numbers:
            issue = snapshot["issues"][issue_number]
            actual_state = str(issue.get("state", "")).lower()
            allowed_states = {before["issue_state"], after["issue_state"]}
            if actual_state not in allowed_states:
                raise ProviderReconciliationError(
                    f"{label} Issue #{issue_number} state {actual_state!r} is outside the governed transition"
                )
            if actual_state == after["issue_state"] and after["state_reason"] is not None:
                actual_reason = str(issue.get("stateReason", "")).lower() or None
                if actual_reason != after["state_reason"]:
                    raise ProviderReconciliationError(
                        f"{label} Issue #{issue_number} terminal reason must be {after['state_reason']}"
                    )
            item = snapshot["items"][issue_number]
            for field in PROJECT_FIELDS:
                actual = _actual_project_value(item, field)
                allowed = {before["project"][field], after["project"][field]}
                if actual not in allowed:
                    raise ProviderReconciliationError(
                        f"{label} Issue #{issue_number} Project field {field!r} value {actual!r} is outside the governed transition"
                    )


def _field_option(snapshot: dict[str, Any], field_name: str, option_name: str) -> tuple[str, str]:
    fields = [field for field in snapshot["fields"] if field.get("name") == field_name]
    if len(fields) != 1:
        raise ProviderReconciliationError(
            f"GitHub Project must contain exactly one {field_name!r} field"
        )
    field = fields[0]
    options = field.get("options")
    if not isinstance(options, list):
        raise ProviderReconciliationError(f"GitHub Project field {field_name!r} has no options")
    matches = [option for option in options if option.get("name") == option_name]
    if len(matches) != 1:
        raise ProviderReconciliationError(
            f"GitHub Project field {field_name!r} must contain option {option_name!r}"
        )
    field_id = _non_empty_string(field.get("id"), f"Project field {field_name}.id")
    option_id = _non_empty_string(matches[0].get("id"), f"Project option {option_name}.id")
    return field_id, option_id


def _edit_project_field(
    runner: Runner,
    snapshot: dict[str, Any],
    issue_number: int,
    field_name: str,
    option_name: str,
) -> None:
    field_id, option_id = _field_option(snapshot, field_name, option_name)
    item_id = _non_empty_string(snapshot["items"][issue_number].get("id"), "Project item id")
    project_id = _non_empty_string(snapshot["project"].get("id"), "Project id")
    runner(
        [
            "gh",
            "project",
            "item-edit",
            "--id",
            item_id,
            "--project-id",
            project_id,
            "--field-id",
            field_id,
            "--single-select-option-id",
            option_id,
        ]
    )


def apply_reconciliation(
    contract: dict[str, Any],
    included: list[int],
    snapshot: dict[str, Any],
    runner: Runner,
) -> None:
    validate_transition_snapshot(contract, included, snapshot)
    repository = contract["repository"]
    included_after = contract["included_work"]["postpublication"]
    for issue_number in included:
        item = snapshot["items"][issue_number]
        desired = included_after["project"]["Published in"]
        if _actual_project_value(item, "Published in") != desired:
            _edit_project_field(runner, snapshot, issue_number, "Published in", desired)

    coordination_after = contract["coordination"]["postpublication"]
    for issue_number in contract["coordination"]["issue_numbers"]:
        issue = snapshot["issues"][issue_number]
        if str(issue.get("state", "")).lower() != coordination_after["issue_state"]:
            runner(
                [
                    "gh",
                    "issue",
                    "close",
                    str(issue_number),
                    "--repo",
                    repository,
                    "--reason",
                    coordination_after["state_reason"],
                ]
            )
        item = snapshot["items"][issue_number]
        desired_status = coordination_after["project"]["Status"]
        if _actual_project_value(item, "Status") != desired_status:
            _edit_project_field(runner, snapshot, issue_number, "Status", desired_status)


def report(contract: dict[str, Any], included: list[int], snapshot: dict[str, Any], phase: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "provider": contract["provider"],
        "repository": contract["repository"],
        "project": {
            "owner": contract["project_owner"],
            "number": contract["project_number"],
            "id": snapshot["project"].get("id"),
        },
        "phase": phase,
        "included_issues": [f"#{number}" for number in included],
        "coordination_issues": [
            f"#{number}" for number in contract["coordination"]["issue_numbers"]
        ],
        "release_url": (snapshot.get("release") or {}).get("url"),
        "status": "passed",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--phase",
        choices=("contract", "preflight", "apply", "verify"),
        required=True,
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def execute(
    *,
    root: Path,
    version: str,
    phase: str,
    runner: Runner = subprocess_runner,
) -> dict[str, Any]:
    contract, included = load_release_contract(root, version)
    if phase == "contract":
        return {
            "schema_version": "1.0",
            "provider": contract["provider"],
            "repository": contract["repository"],
            "project": {
                "owner": contract["project_owner"],
                "number": contract["project_number"],
                "id": None,
            },
            "phase": "contract",
            "included_issues": [f"#{number}" for number in included],
            "coordination_issues": [
                f"#{number}" for number in contract["coordination"]["issue_numbers"]
            ],
            "release_url": None,
            "status": "passed",
        }
    require_release = phase in {"apply", "verify"}
    snapshot = collect_snapshot(
        contract,
        included,
        runner,
        require_release=require_release,
        version=version,
    )
    if phase == "preflight":
        validate_snapshot(contract, included, snapshot, "prepublication")
    elif phase == "apply":
        apply_reconciliation(contract, included, snapshot, runner)
        snapshot = collect_snapshot(
            contract,
            included,
            runner,
            require_release=True,
            version=version,
        )
        validate_snapshot(contract, included, snapshot, "postpublication")
    else:
        validate_snapshot(contract, included, snapshot, "postpublication")
    return report(contract, included, snapshot, phase)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = execute(root=ROOT, version=args.version, phase=args.phase)
        rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"Provider reconciliation read-back written to {args.output}.")
        else:
            print(rendered, end="")
    except (OSError, ProviderReconciliationError) as exc:
        print(f"Provider reconciliation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
