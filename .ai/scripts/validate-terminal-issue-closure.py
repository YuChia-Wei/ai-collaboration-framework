#!/usr/bin/env python3
"""Validate source-only GitHub terminal/deferred Issue disposition records."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
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
    r"(?:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#([1-9][0-9]*)\b"
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


def parsed_issue_references(text: str) -> list[tuple[str, str | None, int]]:
    return [
        (normalized_keyword(keyword), repository or None, int(value))
        for keyword, repository, value in ISSUE_REFERENCE.findall(text)
    ]


def issue_references(body: str, repository: str, number: int) -> list[str]:
    return [
        keyword
        for keyword, qualified_repository, value in parsed_issue_references(body)
        if value == number and (qualified_repository is None or qualified_repository.casefold() == repository.casefold())
    ]


def runtime_from_event(path: Path) -> dict[str, Any]:
    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot read GitHub event JSON: {exc}") from exc
    pull_request = event.get("pull_request") if isinstance(event, dict) else None
    if not isinstance(pull_request, dict):
        raise ValueError(f"{path}: pull_request event payload is required")
    head = pull_request.get("head")
    base = pull_request.get("base")
    return {
        "pr_number": event.get("number"),
        "head_sha": head.get("sha") if isinstance(head, dict) else None,
        "base_sha": base.get("sha") if isinstance(base, dict) else None,
        "body": pull_request.get("body") or "",
    }


def checkout_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not SHA.fullmatch(result.stdout.strip()):
        raise ValueError("unable to resolve the current checkout HEAD")
    return result.stdout.strip()


def commit_messages(base_sha: str, head_sha: str) -> str:
    if not SHA.fullmatch(base_sha or "") or not SHA.fullmatch(head_sha or ""):
        raise ValueError("current PR event requires exact base and head SHAs")
    merge_base_result = subprocess.run(
        ["git", "merge-base", base_sha, head_sha], cwd=ROOT, capture_output=True, text=True, check=False
    )
    merge_base = merge_base_result.stdout.strip()
    if merge_base_result.returncode != 0 or not SHA.fullmatch(merge_base):
        raise ValueError("unable to resolve the current PR merge base")
    result = subprocess.run(
        ["git", "log", "--format=%B", f"{merge_base}..{head_sha}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("unable to read current PR commit messages")
    return result.stdout


def bind_admission_evidence(
    record: dict[str, Any], evidence: dict[str, Any], config: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if record.get("validation_stage") != "declaration":
        errors.append("admission evidence may only overlay a tracked declaration record")
    if evidence.get("schema_version") != "1.0":
        errors.append("admission evidence schema_version must be 1.0")
    if evidence.get("contract_id") != "github-terminal-issue-closure-admission":
        errors.append("admission evidence contract_id must be github-terminal-issue-closure-admission")
    if evidence.get("repository") != record.get("repository"):
        errors.append("admission evidence repository must match the disposition record")
    if evidence.get("provider") != "github":
        errors.append("admission evidence provider must be github")
    durable_pr = record.get("pull_request")
    evidence_pr = evidence.get("pull_request")
    if not isinstance(durable_pr, dict) or not isinstance(evidence_pr, dict):
        return record, errors + ["admission evidence pull_request must be a mapping"]
    if evidence_pr.get("number") != durable_pr.get("number"):
        errors.append("admission evidence pull_request.number must match the disposition record")
    required = config.get("work_item_binding", {}).get("merge_gate", {}).get("required_check_contexts")
    if not isinstance(required, list) or not required:
        errors.append("provider merge gate must own a non-empty required_check_contexts list")
    elif evidence_pr.get("required_check_contexts") != required:
        errors.append("admission evidence must exactly match provider-owned required_check_contexts")
    review = evidence_pr.get("review")
    review_id = review.get("provider_review_id") if isinstance(review, dict) else None
    if not isinstance(review_id, int) or isinstance(review_id, bool) or review_id <= 0:
        errors.append("admission evidence review requires a positive provider_review_id")
    if not isinstance(review, dict) or not non_empty(review.get("submitted_at")):
        errors.append("admission evidence review requires provider submitted_at")
    checks = evidence_pr.get("hosted_checks")
    if not isinstance(checks, list):
        checks = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            continue
        check_id = check.get("provider_check_run_id")
        if not isinstance(check_id, int) or isinstance(check_id, bool) or check_id <= 0:
            errors.append(f"admission evidence hosted_checks[{index}] requires a positive provider_check_run_id")
        if not non_empty(check.get("completed_at")):
            errors.append(f"admission evidence hosted_checks[{index}] requires provider completed_at")
    bound = copy.deepcopy(record)
    bound["validation_stage"] = "merge-admission"
    bound_pr = bound["pull_request"]
    for field in ("number", "base_sha", "head_sha", "body", "review", "required_check_contexts", "hosted_checks"):
        bound_pr[field] = copy.deepcopy(evidence_pr.get(field))
    return bound, errors


def github_api_json(url: str, token: str) -> tuple[Any, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "terminal-issue-closure-validator",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), response.headers.get("Link")
    except (OSError, urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ValueError(f"GitHub provider read-back failed: {exc}") from exc


def github_api_paginated(url: str, token: str, item_key: str | None = None) -> list[Any]:
    items: list[Any] = []
    visited: set[str] = set()
    next_url: str | None = url
    while next_url is not None:
        parsed = urllib.parse.urlparse(next_url)
        if parsed.scheme != "https" or parsed.hostname != "api.github.com":
            raise ValueError("GitHub pagination next link must remain on https://api.github.com")
        if next_url in visited or len(visited) >= 100:
            raise ValueError("GitHub pagination loop or page limit exceeded")
        visited.add(next_url)
        payload, link = github_api_json(next_url, token)
        page = payload.get(item_key) if item_key is not None and isinstance(payload, dict) else payload
        if not isinstance(page, list):
            raise ValueError("GitHub provider read-back returned an unexpected paginated schema")
        items.extend(page)
        candidate: str | None = None
        relations: set[str] = set()
        if link:
            for part in link.split(","):
                match = re.fullmatch(r'\s*<([^>]+)>;\s*rel="([^"]+)"\s*', part)
                if not match:
                    raise ValueError("GitHub provider returned a malformed pagination Link header")
                relation = match.group(2)
                if not re.fullmatch(r"[a-z]+", relation):
                    raise ValueError(f"GitHub provider returned unsupported pagination relation {relation!r}")
                if relation in relations:
                    raise ValueError(f"GitHub provider returned duplicate pagination relation {relation!r}")
                relations.add(relation)
                if relation == "next":
                    candidate = match.group(1)
        total = payload.get("total_count") if isinstance(payload, dict) else None
        if item_key is not None and (not isinstance(total, int) or isinstance(total, bool) or total < 0):
            raise ValueError("GitHub provider paginated mapping requires a valid total_count")
        if candidate is None and isinstance(total, int) and len(items) != total:
            raise ValueError("GitHub provider pagination does not match total_count")
        if candidate is None and len(page) == 100 and not isinstance(total, int):
            if item_key is None:
                raise ValueError("GitHub provider pagination is incomplete at the page limit")
        next_url = candidate
    return items


def read_live_provider_facts(
    repository: str, pr_number: int, head_sha: str, required_contexts: list[str], token: str
) -> dict[str, Any]:
    api_root = f"https://api.github.com/repos/{repository}"
    metadata, metadata_link = github_api_json(f"{api_root}/pulls/{pr_number}", token)
    if metadata_link is not None:
        raise ValueError("GitHub pull request metadata returned an unexpected pagination Link header")
    if not isinstance(metadata, dict) or metadata.get("number") != pr_number:
        raise ValueError("GitHub provider returned mismatched pull request metadata")
    live_head = metadata.get("head")
    live_base = metadata.get("base")
    live_base_repository = live_base.get("repo") if isinstance(live_base, dict) else None
    live_base_repository_name = (
        live_base_repository.get("full_name") if isinstance(live_base_repository, dict) else None
    )
    live_head_sha = live_head.get("sha") if isinstance(live_head, dict) else None
    live_base_sha = live_base.get("sha") if isinstance(live_base, dict) else None
    if not isinstance(live_base_repository_name, str) or live_base_repository_name.casefold() != repository.casefold():
        raise ValueError("GitHub pull request base repository does not match the governed repository")
    if not isinstance(live_head_sha, str) or not SHA.fullmatch(live_head_sha):
        raise ValueError("GitHub provider returned an invalid pull request head SHA")
    if live_head_sha != head_sha:
        raise ValueError("GitHub pull request head does not match the current event head")
    if not isinstance(live_base_sha, str) or not SHA.fullmatch(live_base_sha):
        raise ValueError("GitHub provider returned an invalid pull request base SHA")
    live_body = metadata.get("body") or ""
    if not isinstance(live_body, str):
        raise ValueError("GitHub provider returned an invalid pull request body")
    reviews = github_api_paginated(f"{api_root}/pulls/{pr_number}/reviews?per_page=100", token)
    runs = github_api_paginated(f"{api_root}/commits/{live_head_sha}/check-runs?per_page=100", token, "check_runs")
    latest_by_reviewer: dict[str, dict[str, Any]] = {}
    for item in reviews:
        if not isinstance(item, dict) or item.get("commit_id") != live_head_sha or item.get("state") not in {"APPROVED", "CHANGES_REQUESTED"}:
            continue
        user = item.get("user")
        login = user.get("login") if isinstance(user, dict) else None
        if not non_empty(login):
            continue
        current = latest_by_reviewer.get(login)
        if current is None or int(item.get("id", 0)) > int(current.get("id", 0)):
            latest_by_reviewer[login] = item
    blocking = [item for item in latest_by_reviewer.values() if item.get("state") == "CHANGES_REQUESTED"]
    approved = [item for item in latest_by_reviewer.values() if item.get("state") == "APPROVED"]
    approved.sort(key=lambda item: int(item.get("id", 0)))
    review = {"status": "pending"}
    if blocking:
        review = {
            "status": "blocked",
            "blocking_provider_review_ids": sorted(item.get("id") for item in blocking),
        }
    elif approved:
        latest = approved[-1]
        review = {
            "status": "approved",
            "head_sha": live_head_sha,
            "provider_review_id": latest.get("id"),
            "submitted_at": latest.get("submitted_at"),
        }
    latest_by_name: dict[str, dict[str, Any]] = {}
    for item in runs:
        if not isinstance(item, dict) or item.get("name") not in required_contexts:
            continue
        current = latest_by_name.get(item["name"])
        if current is None or int(item.get("id", 0)) > int(current.get("id", 0)):
            latest_by_name[item["name"]] = item
    hosted_checks = [
        {
            "name": name,
            "conclusion": latest_by_name.get(name, {}).get("conclusion"),
            "required": True,
            "head_sha": latest_by_name.get(name, {}).get("head_sha"),
            "provider_check_run_id": latest_by_name.get(name, {}).get("id"),
            "completed_at": latest_by_name.get(name, {}).get("completed_at"),
        }
        for name in required_contexts
    ]
    return {
        "number": pr_number,
        "base_sha": live_base_sha,
        "head_sha": live_head_sha,
        "body": live_body,
        "review": review,
        "required_check_contexts": required_contexts,
        "hosted_checks": hosted_checks,
    }


def validate_live_runtime(live: dict[str, Any], runtime: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("pr_number", "base_sha", "head_sha", "body"):
        live_field = "number" if field == "pr_number" else field
        if live.get(live_field) != runtime.get(field):
            errors.append(f"current PR event {field} does not match fresh GitHub pull request metadata")
    return errors


def build_live_admission_evidence(
    record: dict[str, Any], runtime: dict[str, Any], config: dict[str, Any], token: str
) -> dict[str, Any]:
    required = config.get("work_item_binding", {}).get("merge_gate", {}).get("required_check_contexts")
    if not isinstance(required, list) or not required:
        raise ValueError("provider merge gate must own a non-empty required_check_contexts list")
    pull_request = read_live_provider_facts(
        record.get("repository"), runtime.get("pr_number"), runtime.get("head_sha"), required, token
    )
    runtime_errors = validate_live_runtime(pull_request, runtime)
    if runtime_errors:
        raise ValueError("; ".join(runtime_errors))
    return {
        "schema_version": "1.0",
        "contract_id": "github-terminal-issue-closure-admission",
        "repository": record.get("repository"),
        "provider": "github",
        "pull_request": pull_request,
    }


def validate_live_provider_evidence(
    evidence: dict[str, Any], record: dict[str, Any], runtime: dict[str, Any], config: dict[str, Any]
) -> list[str]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return ["live provider verification requires GITHUB_TOKEN"]
    required = config.get("work_item_binding", {}).get("merge_gate", {}).get("required_check_contexts")
    if not isinstance(required, list) or not required:
        return ["provider merge gate must own a non-empty required_check_contexts list"]
    try:
        live = read_live_provider_facts(
            record.get("repository"), runtime.get("pr_number"), runtime.get("head_sha"), required, token
        )
    except ValueError as exc:
        return [str(exc)]
    if evidence.get("pull_request") != live:
        return ["admission evidence does not exactly match fresh GitHub provider read-back"]
    return validate_live_runtime(live, runtime)


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
        references = issue_references(body, config["repository"], number)
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
    commit_text = runtime.get("commit_messages", "") if runtime is not None else ""
    if not isinstance(commit_text, str):
        errors.append("current PR commit messages must be text")
        commit_text = ""
    body_refs = parsed_issue_references(body)
    commit_refs = parsed_issue_references(commit_text)
    all_refs = [("PR body", item) for item in body_refs] + [("commit message", item) for item in commit_refs]
    referenced_numbers: set[int] = set()
    for source, (keyword, qualified_repository, number) in all_refs:
        if qualified_repository is not None and qualified_repository.casefold() != config["repository"].casefold():
            errors.append(f"{source} references foreign repository Issue {qualified_repository}#{number}")
            continue
        referenced_numbers.add(number)
        if source == "commit message" and keyword != "Refs":
            errors.append(f"commit messages must not contain closing keyword {keyword} for Issue #{number}")
    for number in sorted(referenced_numbers - numbers):
        errors.append(f"Issue #{number} is referenced without exactly one disposition record")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="append", type=Path)
    parser.add_argument("--event-path", type=Path)
    admission = parser.add_mutually_exclusive_group()
    admission.add_argument("--admission-evidence", type=Path)
    admission.add_argument("--capture-admission-evidence", action="store_true")
    parser.add_argument("--verify-provider-live", action="store_true")
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
    admission_evidence: dict[str, Any] | None = None
    if args.capture_admission_evidence and runtime is None:
        print("Terminal Issue closure validation failed:\n- admission capture requires a current PR event snapshot", file=sys.stderr)
        return 1
    if args.admission_evidence is not None:
        try:
            admission_evidence = load_mapping(args.admission_evidence)
        except ValueError as exc:
            print(f"Terminal Issue closure validation failed:\n- {exc}", file=sys.stderr)
            return 1
        if runtime is None:
            print("Terminal Issue closure validation failed:\n- admission evidence requires a current PR event snapshot", file=sys.stderr)
            return 1
        if not args.verify_provider_live:
            print("Terminal Issue closure validation failed:\n- admission evidence requires --verify-provider-live", file=sys.stderr)
            return 1
    records: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    for path in paths:
        candidate = path if path.is_absolute() else ROOT / path
        try:
            records.append((candidate, load_mapping(candidate)))
        except ValueError as exc:
            errors.append(str(exc))
    if runtime is not None:
        try:
            if runtime.get("head_sha") != checkout_head():
                errors.append("current PR event head does not match checkout HEAD")
            runtime["commit_messages"] = commit_messages(runtime.get("base_sha"), runtime.get("head_sha"))
        except ValueError as exc:
            errors.append(str(exc))
        records = [item for item in records if item[1].get("pull_request", {}).get("number") == runtime.get("pr_number")]
        if len(records) != 1:
            errors.append(f"current PR #{runtime.get('pr_number')} must have exactly one bound disposition record")
    for candidate, record in records:
        effective = record
        binding_errors: list[str] = []
        if args.capture_admission_evidence and runtime is not None:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                binding_errors.append("live provider capture requires GITHUB_TOKEN")
            else:
                try:
                    admission_evidence = build_live_admission_evidence(record, runtime, config, token)
                except ValueError as exc:
                    binding_errors.append(str(exc))
        if admission_evidence is not None:
            effective, binding_errors = bind_admission_evidence(record, admission_evidence, config)
            if runtime is not None and args.admission_evidence is not None:
                binding_errors.extend(validate_live_provider_evidence(admission_evidence, record, runtime, config))
        elif runtime is not None and record.get("validation_stage") != "declaration":
            binding_errors.append("current PR required check validates declaration only; merge admission requires --admission-evidence")
        errors.extend(f"{candidate.relative_to(ROOT)}: {error}" for error in binding_errors)
        errors.extend(f"{candidate.relative_to(ROOT)}: {error}" for error in validate_record(effective, config, runtime))
    if errors:
        print("Terminal Issue closure validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.capture_admission_evidence and admission_evidence is not None:
        print(yaml.safe_dump(admission_evidence, sort_keys=False), end="")
    if admission_evidence is not None or args.capture_admission_evidence:
        mode = "non-mutating merge admission"
    elif runtime is not None:
        mode = "current PR declaration"
    else:
        mode = "static contract"
    status_stream = sys.stderr if args.capture_admission_evidence else sys.stdout
    print(f"Terminal Issue closure {mode} validation passed for {len(records)} record(s).", file=status_stream)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
