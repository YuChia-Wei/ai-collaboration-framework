#!/usr/bin/env python3
"""Validate source-only GitHub terminal/deferred Issue disposition records."""

from __future__ import annotations

import argparse
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
REFERENCE = re.compile(
    r"(?im)^\s*(?:-\s*)?(Refs|Closes|Fixes|Resolves)\s+#([1-9][0-9]*)\s*$"
)


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


def issue_references(body: str, number: int) -> list[str]:
    return [keyword for keyword, value in REFERENCE.findall(body) if int(value) == number]


def validate_record(record: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = config.get("issue_closure", {})
    modes = contract.get("modes") if isinstance(contract, dict) else None
    approved = contract.get("approved_closing_keywords") if isinstance(contract, dict) else None
    if modes != ["terminal-close", "deferred"]:
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

    pull_request = record.get("pull_request")
    if not isinstance(pull_request, dict):
        return errors + ["pull_request must be a mapping"]
    body = pull_request.get("body")
    if not isinstance(body, str):
        return errors + ["pull_request.body must be a string"]
    integration = pull_request.get("integration", {})
    review = pull_request.get("review", {})
    checks = pull_request.get("hosted_checks", [])
    if not isinstance(integration, dict):
        errors.append("pull_request.integration must be a mapping")
        integration = {}
    if not isinstance(review, dict):
        errors.append("pull_request.review must be a mapping")
        review = {}
    if not isinstance(checks, list):
        errors.append("pull_request.hosted_checks must be a list")
        checks = []

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
            if read_back.get("performed") is True:
                if read_back.get("issue_state") != "open":
                    errors.append(f"deferred Issue #{number} read-back must remain open")
                if read_back.get("project_status") == "Done":
                    errors.append(f"deferred Issue #{number} Project status must not be Done")
            elif integration.get("status") == "merged":
                errors.append(f"merged deferred Issue #{number} requires post-merge read-back")
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
        expected_head = integration.get("expected_head_sha")
        merged_head = integration.get("merged_head_sha")
        if integration.get("status") != "merged" or not isinstance(expected_head, str) or not SHA.fullmatch(expected_head) or expected_head != merged_head:
            errors.append(f"terminal Issue #{number} requires exact merged-head integration")
        if review.get("status") != "approved":
            errors.append(f"terminal Issue #{number} requires approved review")
        if not checks or any(not isinstance(check, dict) or check.get("conclusion") != "success" for check in checks):
            errors.append(f"terminal Issue #{number} requires every hosted check to succeed")
        expected_read_back = {
            "performed": True,
            "merged_head_sha": merged_head,
            "issue_state": "closed",
            "issue_state_reason": "completed",
            "project_status": "Done",
        }
        if read_back != expected_read_back:
            errors.append(f"terminal Issue #{number} requires matching post-merge Issue and Project read-back")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="append", type=Path)
    args = parser.parse_args(argv)
    config = load_mapping(CONFIG)
    paths = args.record or sorted(
        ROOT.glob(".dev/workflows/*/evidence/terminal-issue-closure*.yaml")
    )
    if not paths:
        print("Terminal Issue closure validation failed: no durable records found", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in paths:
        candidate = path if path.is_absolute() else ROOT / path
        try:
            record = load_mapping(candidate)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        errors.extend(f"{candidate.relative_to(ROOT)}: {error}" for error in validate_record(record, config))
    if errors:
        print("Terminal Issue closure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Terminal Issue closure validation passed for {len(paths)} record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
