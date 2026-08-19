#!/usr/bin/env python3
"""Validate source-only GitHub terminal/deferred Issue disposition records."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-terminal-issue-closure.py")

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / ".dev/backlog/providers/github.yaml"
SHA = re.compile(r"^[0-9a-f]{40}$")
ISSUE_REFERENCE = re.compile(
    r"(?i)\b(refs?|close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+"
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#([1-9][0-9]*)\b"
)
STAGES = {"declaration", "merge-admission", "reconciliation"}


def load_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"{path}: cannot read YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalized_keyword(value: str) -> str:
    token = value.lower()
    if token.startswith("ref"):
        return "Refs"
    if token.startswith("clos"):
        return "Closes"
    if token.startswith("fix"):
        return "Fixes"
    return "Resolves"


def issue_references(body: str, number: int) -> list[str]:
    return [normalized_keyword(keyword) for keyword, value in ISSUE_REFERENCE.findall(body) if int(value) == number]


def runtime_from_event(path: Path) -> dict[str, Any]:
    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot read GitHub event JSON: {exc}") from exc
    pull_request = event.get("pull_request") if isinstance(event, dict) else None
    if not isinstance(pull_request, dict):
        raise ValueError(f"{path}: pull_request event payload is required")
    head = pull_request.get("head")
    return {
        "pr_number": event.get("number"),
        "head_sha": head.get("sha") if isinstance(head, dict) else None,
        "body": pull_request.get("body") or "",
    }


def validate_provider_evidence(pull_request: dict[str, Any], runtime: dict[str, Any] | None, errors: list[str]) -> None:
    number = pull_request.get("number")
    head_sha = pull_request.get("head_sha")
    if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
        errors.append("pull_request.number must be a positive integer for merge admission")
    if not isinstance(head_sha, str) or not SHA.fullmatch(head_sha):
        errors.append("pull_request.head_sha must be an exact 40-character SHA")
    if runtime is not None:
        if runtime.get("pr_number") != number:
            errors.append("record pull_request.number does not match current PR event")
        if runtime.get("head_sha") != head_sha:
            errors.append("record pull_request.head_sha does not match current PR event")
    review = pull_request.get("review")
    if not isinstance(review, dict) or review.get("status") != "approved":
        errors.append("merge admission requires approved review")
    elif review.get("head_sha") != head_sha:
        errors.append("approved review must be bound to pull_request.head_sha")
    required = pull_request.get("required_check_contexts")
    checks = pull_request.get("hosted_checks")
    if not isinstance(required, list) or not required or any(not non_empty(item) for item in required):
        errors.append("merge admission requires a non-empty required_check_contexts list")
        required = []
    if len(required) != len(set(required)):
        errors.append("required_check_contexts must be unique")
    if not isinstance(checks, list):
        errors.append("pull_request.hosted_checks must be a list")
        checks = []
    names: list[str] = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"hosted_checks[{index}] must be a mapping")
            continue
        name = check.get("name")
        if not non_empty(name):
            errors.append(f"hosted_checks[{index}].name must be non-empty")
            continue
        names.append(name)
        if check.get("required") is not True:
            errors.append(f"hosted check {name!r} must be marked required")
        if check.get("conclusion") != "success":
            errors.append(f"hosted check {name!r} must succeed")
        if check.get("head_sha") != head_sha:
            errors.append(f"hosted check {name!r} must be bound to pull_request.head_sha")
    if len(names) != len(set(names)):
        errors.append("hosted check names must be unique")
    if set(names) != set(required):
        errors.append("hosted checks must exactly cover required_check_contexts")


def validate_record(record: dict[str, Any], config: dict[str, Any], runtime: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    contract = config.get("issue_closure", {})
    approved = contract.get("approved_closing_keywords") if isinstance(contract, dict) else None
    if contract.get("modes") != ["terminal-close", "deferred"]:
        errors.append("provider issue_closure.modes must be exactly terminal-close and deferred")
    if approved != ["Closes", "Fixes", "Resolves"]:
        errors.append("provider approved closing keywords must be Closes, Fixes, Resolves")
    if contract.get("closing_keyword_authorizes_work") is not False:
        errors.append("provider closing_keyword_authorizes_work must be false")
    if contract.get("mixed_per_issue_dispositions") is not True:
        errors.append("provider must allow mixed per-Issue dispositions")
    if record.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if record.get("contract_id") != "github-terminal-issue-closure":
        errors.append("contract_id must be github-terminal-issue-closure")
    if record.get("repository") != config.get("repository"):
        errors.append("repository must match the selected GitHub provider")
    stage = record.get("validation_stage")
    if stage not in STAGES:
        errors.append("validation_stage must be declaration, merge-admission, or reconciliation")
    pull_request = record.get("pull_request")
    if not isinstance(pull_request, dict):
        return errors + ["pull_request must be a mapping"]
    body = runtime.get("body") if runtime is not None else pull_request.get("body")
    if not isinstance(body, str):
        return errors + ["pull_request.body must be a string"]
    integration = pull_request.get("integration", {})
    if not isinstance(integration, dict):
        errors.append("pull_request.integration must be a mapping")
        integration = {}
    if stage in {"merge-admission", "reconciliation"}:
        validate_provider_evidence(pull_request, runtime, errors)
    issues = record.get("issues")
    if not isinstance(issues, list) or not issues:
        return errors + ["issues must be a non-empty list"]
    numbers: set[int] = set()
    for index, issue in enumerate(issues):
        label = f"issues[{index}]"
        if not isinstance(issue, dict):
            errors.append(f"{label} must be a mapping")
            continue
        number = issue.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            errors.append(f"{label}.number must be a positive integer")
            continue
        if number in numbers:
            errors.append(f"Issue #{number} has duplicate dispositions")
        numbers.add(number)
        mode = issue.get("mode")
        if mode not in {"terminal-close", "deferred"}:
            errors.append(f"Issue #{number} has unsupported mode {mode!r}")
            continue
        authorization = issue.get("work_authorization", {})
        if not isinstance(authorization, dict) or authorization.get("online_issue_bound") is not True or authorization.get("explicit_owner_approval") is not True:
            errors.append(f"Issue #{number} requires binding and explicit owner approval independent of keywords")
        references = issue_references(body, number)
        read_back = issue.get("read_back", {})
        if not isinstance(read_back, dict):
            errors.append(f"Issue #{number} read_back must be a mapping")
            read_back = {}
        if mode == "deferred":
            if references != ["Refs"]:
                errors.append(f"deferred Issue #{number} requires exactly Refs #{number} and no closing keyword")
            if issue.get("closing_keyword") is not None:
                errors.append(f"deferred Issue #{number} closing_keyword must be null")
            if not non_empty(issue.get("closure_deferred_reason")):
                errors.append(f"deferred Issue #{number} requires closure_deferred_reason")
            if not non_empty(issue.get("next_terminal_gate_or_owner")):
                errors.append(f"deferred Issue #{number} requires next_terminal_gate_or_owner")
            if stage == "reconciliation":
                if integration.get("status") != "merged" or integration.get("merged_head_sha") != pull_request.get("head_sha"):
                    errors.append(f"deferred Issue #{number} reconciliation requires exact merged-head integration")
                if read_back.get("performed") is not True or read_back.get("issue_state") != "open" or read_back.get("project_status") == "Done":
                    errors.append(f"deferred Issue #{number} reconciliation must prove it remains open and not Done")
            continue
        closing_keyword = issue.get("closing_keyword")
        if closing_keyword not in approved:
            errors.append(f"terminal Issue #{number} requires an approved closing_keyword")
        if references != [closing_keyword]:
            errors.append(f"terminal Issue #{number} body must contain its matching closing keyword exactly once")
        workflow = issue.get("workflow", {})
        for field in ("scope_complete", "tasks_complete", "applicable_verification_complete"):
            if not isinstance(workflow, dict) or workflow.get(field) is not True:
                errors.append(f"terminal Issue #{number} requires workflow.{field}=true")
        if issue.get("final_accepted_delivery") is not True:
            errors.append(f"terminal Issue #{number} requires final_accepted_delivery=true")
        if stage == "reconciliation":
            head_sha = pull_request.get("head_sha")
            if integration.get("status") != "merged" or integration.get("expected_head_sha") != head_sha or integration.get("merged_head_sha") != head_sha:
                errors.append(f"terminal Issue #{number} reconciliation requires exact merged-head integration")
            expected_read_back = {"performed": True, "merged_head_sha": head_sha, "issue_state": "closed", "issue_state_reason": "completed", "project_status": "Done"}
            if read_back != expected_read_back:
                errors.append(f"terminal Issue #{number} requires matching post-merge Issue and Project read-back")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="append", type=Path)
    parser.add_argument("--event-path", type=Path)
    args = parser.parse_args(argv)
    config = load_mapping(CONFIG)
    paths = args.record or sorted(ROOT.glob(".dev/workflows/*/evidence/terminal-issue-closure*.yaml"))
    if not paths:
        print("Terminal Issue closure validation failed: no durable records found", file=sys.stderr)
        return 1
    event_path = args.event_path
    if event_path is None and os.environ.get("GITHUB_EVENT_PATH"):
        event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    runtime = runtime_from_event(event_path) if event_path is not None else None
    records: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    for path in paths:
        candidate = path if path.is_absolute() else ROOT / path
        try:
            records.append((candidate, load_mapping(candidate)))
        except ValueError as exc:
            errors.append(str(exc))
    if runtime is not None:
        records = [item for item in records if item[1].get("pull_request", {}).get("number") == runtime.get("pr_number")]
        if len(records) != 1:
            errors.append(f"current PR #{runtime.get('pr_number')} must have exactly one bound disposition record")
    for candidate, record in records:
        errors.extend(f"{candidate.relative_to(ROOT)}: {error}" for error in validate_record(record, config, runtime))
    if errors:
        print("Terminal Issue closure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    mode = "current PR event" if runtime is not None else "static contract"
    print(f"Terminal Issue closure {mode} validation passed for {len(records)} record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
