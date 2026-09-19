#!/usr/bin/env python3
"""Fail-closed, read-only validation for a governed AI-context release phase.

This validator intentionally separates repository-local facts from hosted facts.
Hosted checks are opt-in and use only ``gh api`` GET endpoints; they never create
tags, releases, assets, or workflow runs.
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context-release-state.py")

import argparse
import importlib.util
import hashlib
import json
import math
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import yaml

from ai_context_package_identity import expected_artifacts, expected_package_id
from release_asset_identity import governed as asset_identity_required, load_admission, verify_provider, contained as contained_release_asset
from ai_context_package import PackageError

from ai_context_upgrade_routes import (
    MatrixValidationError,
    canonical_json as canonical_route_json,
    load_route_matrix,
    resolve_upgrade_route,
)


VERSION_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DIRECT_UPGRADE_RUNNERS = {
    "v0.17.0": ".github/scripts/validate-v017-direct-upgrades.py",
    "v0.18.0": ".github/scripts/validate-v018-direct-upgrades.py",
}
V018_REBIND_ARCHIVE_SHA256 = "90e403bde5e1e84767a4c00b67923780ebea76222b7956e598c814241c0f7db0"
V018_REBIND_SUBJECT_SHA = "f566a6014f0942a15b28a39f0b2f5df3303e6014"
V018_REBIND_RUNNER_PATH = ".github/scripts/validate-v018-direct-upgrades.py"
V018_REBIND_RUNNER_SHA256 = "60df0a1c2fc0217c104467d23a23b65245d3360fbc04291ff26387470b4e199b"
V018_REBIND_TERMINAL_SHA256 = "04885cbbb8c3dc6823867f7ed73be102c2c427b3b34602080204b0f12782a3ca"
V018_REBIND_CASE_INDEX_SHA256 = "3e4f5dab025e408f6588959f9bb8c328835721c9b2b5f6886dcee575c127978a"
V018_REBIND_BASELINE_MATRIX_SHA256 = "d95c5ee82b97013f46f9a52a54ec54e698f94706cb0c29280f44c93b84417c30"
V018_REBIND_CASE_EVIDENCE_COUNT = 236
V018_REBIND_PAYLOAD_DELTAS = (
    (
        ".ai/scripts/shell-assets.yaml",
        b"  - python .ai/scripts/tests/test_code_reviewer_routing_contract.py -v\n",
        b"  - python .ai/scripts/tests/test_runtime_skill_entries.py -v\n",
    ),
    (
        ".ai/scripts/validate-dependency-versions.py",
        b"    expected_exit_two = {\n",
        b"        \".ai/assets/skills/ai-context-upgrader/scripts/run-target-validation.py\",\n",
    ),
)
V018_REBIND_CASES = (
    "v0.6.0-pristine-resume",
    "v0.6.0-customized-none",
    "v0.6.0-customized-rollback",
    "v0.9.0-pristine-resume",
    "v0.9.0-customized-none",
    "v0.9.0-customized-rollback",
    "v0.17.0-pristine-resume",
    "v0.17.0-customized-none",
    "v0.17.0-customized-rollback",
)
ONLINE_ISSUE_REF_RE = re.compile(r"^#([1-9]\d*)$")
PHASES = ("candidate", "tag", "publication", "finalization")
V010_AGENT_PUBLICATION_AUTHORITY = {
    "tag_owner": "owner-authorized-terra-agent",
    "trigger": "owner-approved-v0.10.0-agent-tag",
    "automation": "github-actions",
    "creates_or_moves_tag": False,
    "authorization_source": "AI Collaboration Framework v0.10.0 Terra implementation work package",
    "authorized_issue": "#137",
    "authorized_actor": "OpenAI Codex Terra",
    "existing_tag_mutation": "forbidden",
}
V011_AGENT_PUBLICATION_AUTHORITY = {
    "tag_owner": "owner-authorized-sol-agent",
    "trigger": "owner-approved-v0.11.0-agent-tag",
    "automation": "manual-fast-path",
    "creates_or_moves_tag": False,
    "authorization_source": "AI framework v0.11.0 Sol MAX work package and online Issue #152",
    "authorized_issue": "#152",
    "authorized_actor": "OpenAI Codex Sol",
    "existing_tag_mutation": "forbidden",
}
V011_TAGGED_PUBLICATION_AUTHORITY = {
    **V011_AGENT_PUBLICATION_AUTHORITY,
    # The immutable tagged YAML left #152 unquoted, so YAML parsed it as a comment.
    "authorization_source": "AI framework v0.11.0 Sol MAX work package and online Issue",
}
V011_TAGGED_COMMIT = "05199ed0a9ed509ef1696df014fce244f8e7cffa"
V011_FAILED_PUBLICATION_RUN = "31268095541"
V011_PUBLICATION_FAILURE = (
    "tagged-tree release registry used unsupported candidate status and "
    "noncanonical publication ownership values"
)
PLACEHOLDER_RE = re.compile(r"\{\{.+?\}\}|<[^\n>]+>|\b(?:TODO|TBD|PLACEHOLDER)\b", re.I)
FORBIDDEN_AUTHORED_RE = re.compile(
    r"ai-context-release-automation:|^## Release provenance\s*$", re.I | re.M
)
RENDERER_PATH = ".ai/scripts/render-ai-context-release-notes.py"
PUBLISH_WORKFLOW_PATH = ".github/workflows/publish-release.yml"


class ReleaseStateError(ValueError):
    """Raised for invalid release-state inputs."""


def version_key(version: str) -> tuple[int, int, int]:
    if not VERSION_RE.fullmatch(version):
        raise ReleaseStateError("version must use stable vMAJOR.MINOR.PATCH form")
    return tuple(int(part) for part in version[1:].split("."))


def uses_online_issue_refs(version: str) -> bool:
    """Source releases from v0.10.0 onward use live GitHub Issue authority."""

    return version_key(version) >= (0, 10, 0)


def sanctioned_commands(version: str) -> dict[str, str]:
    if not VERSION_RE.fullmatch(version):
        raise ReleaseStateError("version must use stable vMAJOR.MINOR.PATCH form")
    base = (
        "python .ai/scripts/validate-ai-context-release-state.py "
        f"--phase {{phase}} --version {version}"
    )
    return {
        "candidate": base.format(phase="candidate"),
        "tag": base.format(phase="tag"),
        "publication": base.format(phase="publication") + " --hosted",
        "finalization": base.format(phase="finalization") + " --hosted",
    }


def load_mapping(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ReleaseStateError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseStateError(f"{path} must contain a YAML mapping")
    return value


def read_only_command_allowed(args: list[str]) -> bool:
    if args in (
        ["git", "rev-parse", "HEAD"],
        ["git", "branch", "--show-current"],
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        ["git", "config", "--get", "remote.origin.url"],
    ):
        return True
    if len(args) == 4 and args[:3] == ["git", "cat-file", "-t"]:
        return bool(re.fullmatch(r"refs/tags/v\d+\.\d+\.\d+", args[3]))
    if len(args) == 3 and args[:2] == ["git", "rev-parse"]:
        return bool(re.fullmatch(r"refs/tags/v\d+\.\d+\.\d+\^\{commit\}", args[2]))
    if len(args) == 3 and args[:2] == ["git", "show"]:
        return bool(
            re.fullmatch(
                r"refs/tags/v\d+\.\d+\.\d+:\.dev/releases/v\d+\.\d+\.\d+/"
                r"(?:release\.yaml|release-notes\.md|migration-guide\.md)",
                args[2],
            )
        )
    if len(args) == 5 and args[:4] == ["gh", "api", "--method", "GET"]:
        return bool(
            re.fullmatch(
                r"repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/"
                r"(?:issues/[1-9]\d*|pulls/[1-9]\d*|releases/tags/v\d+\.\d+\.\d+|actions/runs/\d+|"
                r"actions/workflows/publish-release\.yml/runs\?"
                r"event=push&head_sha=[0-9a-f]{40})",
                args[4],
            )
        )
    return False


def run_read_only(root: Path, args: list[str], runner=subprocess.run) -> str:
    if not read_only_command_allowed(args):
        raise ReleaseStateError(
            f"command is not in the read-only allowlist: {' '.join(args)}"
        )
    result = runner(args, cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ReleaseStateError(f"read-only command failed: {' '.join(args)}: {detail}")
    return result.stdout


def require_phase_contract(root: Path, phase: str, version: str) -> dict:
    commands = sanctioned_commands(version)
    path = root / ".dev" / "releases" / version / "release-phase-checks.yaml"
    data = load_mapping(path)
    if data.get("schema_version") != "1.0":
        raise ReleaseStateError(f"{path}: schema_version must be 1.0")
    if data.get("release") != version:
        raise ReleaseStateError(f"{path}: release must equal {version}")
    phases = data.get("phases")
    if not isinstance(phases, dict):
        raise ReleaseStateError(f"{path}: phases must be a mapping")
    missing = [item for item in PHASES if item not in phases]
    if missing:
        raise ReleaseStateError(f"{path}: missing sanctioned phases: {', '.join(missing)}")
    entry = phases.get(phase)
    if not isinstance(entry, dict):
        raise ReleaseStateError(f"{path}: phases.{phase} must be a mapping")
    expected = commands.get(phase)
    if entry.get("command") != expected:
        raise ReleaseStateError(
            f"{path}: phases.{phase}.command is not the sanctioned {version} command"
        )
    return entry


def release_record(root: Path, version: str) -> tuple[Path, dict, Path, Path]:
    if not VERSION_RE.fullmatch(version):
        raise ReleaseStateError("version must use stable vMAJOR.MINOR.PATCH form")
    directory = root / ".dev" / "releases" / version
    path = directory / "release.yaml"
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ReleaseStateError(f"cannot read {path}: {exc}") from exc
    if PLACEHOLDER_RE.search(raw):
        raise ReleaseStateError(f"{path}: unfilled placeholder is forbidden")
    data = load_mapping(path)
    if data.get("release_id") != f"REL-{version}" or data.get("version") != version:
        raise ReleaseStateError(f"{path}: release identity must be REL-{version} / {version}")
    notes = directory / "release-notes.md"
    migration = directory / "migration-guide.md"
    if not notes.is_file() or not migration.is_file():
        raise ReleaseStateError(f"{directory}: release-notes.md and migration-guide.md are required")
    return path, data, notes, migration


def assert_authored_sources(version: str, notes: Path, migration: Path) -> None:
    expected_headings = {
        notes: f"# REL-{version}",
        migration: f"# Migrate To {version}",
    }
    for path, expected_heading in expected_headings.items():
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ReleaseStateError(f"{path}: authored source must not be empty")
        if FORBIDDEN_AUTHORED_RE.search(text):
            raise ReleaseStateError(f"{path}: rendered release provenance belongs only in generated output")
        if PLACEHOLDER_RE.search(text):
            raise ReleaseStateError(f"{path}: unfilled placeholder is forbidden")
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if not first_line.startswith(expected_heading):
            raise ReleaseStateError(
                f"{path}: first heading must identify {expected_heading}; "
                "previous versions remain allowed only as compatibility or migration sources"
            )


def git_head(root: Path, runner=subprocess.run) -> str:
    value = run_read_only(root, ["git", "rev-parse", "HEAD"], runner).strip()
    if not SHA_RE.fullmatch(value):
        raise ReleaseStateError("git HEAD did not resolve to a full lowercase SHA")
    return value


def git_branch(root: Path, runner=subprocess.run) -> str:
    return run_read_only(
        root,
        ["git", "branch", "--show-current"],
        runner,
    ).strip()


def assert_clean_worktree(root: Path, runner=subprocess.run) -> None:
    status = run_read_only(
        root,
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        runner,
    )
    if status.strip():
        raise ReleaseStateError("candidate validation requires a clean source worktree")


def iso_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise ReleaseStateError(f"{label} must be an ISO 8601 timestamp with an offset")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReleaseStateError(
            f"{label} must be an ISO 8601 timestamp with an offset"
        ) from exc
    if parsed.tzinfo is None:
        raise ReleaseStateError(f"{label} must include an explicit UTC offset")
    if parsed.astimezone(timezone.utc) > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ReleaseStateError(f"{label} cannot be in the future")
    return parsed


def nested_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReleaseStateError(f"{label} must be a mapping")
    return value


def canonical_backlog_refs(root: Path, version: str) -> set[str]:
    """Return the complete backlog set accepted by one release train."""
    refs: set[str] = set()
    items = root / ".dev" / "backlog" / "items"
    for path in sorted(items.glob("*.yaml")):
        item = load_mapping(path)
        release = item.get("release")
        if not isinstance(release, dict):
            continue
        if item.get("status") == "resolved" and release.get("completed_in") == version:
            refs.add(path.relative_to(root).as_posix())
    return refs


def validate_backlog_refs(root: Path, version: str, data: dict[str, Any]) -> None:
    planning = nested_mapping(data.get("planning"), "planning")
    refs = planning.get("backlog_refs")
    if not isinstance(refs, list) or not refs:
        raise ReleaseStateError("planning.backlog_refs must be a non-empty list")
    if len(refs) != len(set(refs)):
        raise ReleaseStateError("planning.backlog_refs must not contain duplicates")
    for index, value in enumerate(refs):
        if not isinstance(value, str) or not re.fullmatch(
            r"\.dev/backlog/items/[A-Z][A-Z0-9-]+\.yaml", value
        ):
            raise ReleaseStateError(
                f"planning.backlog_refs[{index}] must be a backlog item path"
            )
        path = root / value
        item = load_mapping(path)
        release = nested_mapping(item.get("release"), f"{path}: release")
        if release.get("target") != version:
            raise ReleaseStateError(
                f"{path}: backlog target is unrelated to release {version}"
            )
        if item.get("status") != "resolved":
            raise ReleaseStateError(
                f"{path}: release candidate requires the backlog item to be resolved"
            )
        if release.get("completed_in") != version:
            raise ReleaseStateError(
                f"{path}: backlog completed_in must equal release {version}"
            )
        if release.get("published_in") is not None:
            raise ReleaseStateError(
                f"{path}: backlog published_in must remain null before publication"
            )

    canonical = canonical_backlog_refs(root, version)
    declared = set(refs)
    if declared != canonical:
        missing = sorted(canonical - declared)
        extra = sorted(declared - canonical)
        raise ReleaseStateError(
            "planning.backlog_refs must exactly equal the canonical completed backlog "
            f"set for {version}; missing={missing}, extra={extra}"
        )


def validate_online_issue_refs(
    root: Path,
    version: str,
    data: dict[str, Any],
    runner=subprocess.run,
) -> None:
    """Read the authoritative source-repository release scope from GitHub."""
    planning = nested_mapping(data.get("planning"), "planning")
    if "backlog_refs" in planning:
        raise ReleaseStateError(
            "source-repository releases from v0.10.0 onward must not use "
            "planning.backlog_refs"
        )
    refs = planning.get("github_issue_refs")
    if not isinstance(refs, list) or not refs:
        raise ReleaseStateError(
            "planning.github_issue_refs must be a non-empty online Issue list"
        )
    if len(refs) != len(set(refs)):
        raise ReleaseStateError("planning.github_issue_refs must not contain duplicates")
    numbers: list[str] = []
    for index, value in enumerate(refs):
        match = ONLINE_ISSUE_REF_RE.fullmatch(value) if isinstance(value, str) else None
        if match is None:
            raise ReleaseStateError(
                f"planning.github_issue_refs[{index}] must use #<issue-number>"
            )
        numbers.append(match.group(1))

    repository = origin_repository(root, runner)
    legacy_open_candidate = version == "v0.10.0"
    target_pattern = re.compile(
        rf"^## Target Release\s*$\s*^{re.escape(version)}\s*$", re.MULTILINE
    )
    for number in numbers:
        raw = run_read_only(
            root,
            ["gh", "api", "--method", "GET", f"repos/{repository}/issues/{number}"],
            runner,
        )
        try:
            issue = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ReleaseStateError(f"#{number}: GitHub Issue read-back is not JSON") from exc
        if not isinstance(issue, dict) or issue.get("number") != int(number):
            raise ReleaseStateError(f"#{number}: GitHub Issue read-back has a mismatched number")
        if legacy_open_candidate:
            if issue.get("state") != "open":
                raise ReleaseStateError(f"#{number}: v0.10.0 candidate Issue must remain open")
            body = issue.get("body")
            if not isinstance(body, str) or target_pattern.search(body) is None:
                raise ReleaseStateError(
                    f"#{number}: online Issue must declare Target Release {version}"
                )
        elif issue.get("state") != "closed" or issue.get("state_reason") != "completed":
            if version_key(version) >= (0, 14, 0) and pending_terminal_issue_delivery(
                root,
                repository,
                int(number),
                runner,
            ):
                continue
            raise ReleaseStateError(
                f"#{number}: release-ready Issue must be closed with completed reason "
                "or be the exact open terminal-close Issue of the current source-candidate PR"
            )


def pending_terminal_issue_delivery(
    root: Path,
    repository: str,
    issue_number: int,
    runner=subprocess.run,
) -> bool:
    """Allow only the exact current PR to carry its own final Included Work closure.

    This does not treat an open Issue as completed.  It permits pre-merge source
    validation only when one tracked terminal declaration is bound to a live open
    PR at the current HEAD.  Post-merge validation still requires the provider
    Issue to be closed/completed because the declaration PR is no longer open.
    """

    matches: list[dict[str, Any]] = []
    for path in sorted(
        root.glob(".dev/workflows/*/evidence/terminal-issue-closure*.yaml")
    ):
        try:
            record = load_mapping(path)
        except ReleaseStateError:
            continue
        if (
            record.get("schema_version") != "1.0"
            or record.get("contract_id") != "github-terminal-issue-closure"
            or record.get("repository") != repository
            or record.get("validation_stage") != "declaration"
        ):
            continue
        issues = record.get("issues")
        if not isinstance(issues, list):
            continue
        selected = [
            item
            for item in issues
            if isinstance(item, dict) and item.get("number") == issue_number
        ]
        if len(selected) != 1:
            continue
        issue = selected[0]
        workflow = issue.get("workflow")
        authorization = issue.get("work_authorization")
        read_back = issue.get("read_back")
        if (
            issue.get("mode") != "terminal-close"
            or issue.get("final_accepted_delivery") is not True
            or issue.get("closing_keyword") != "Closes"
            or issue.get("closure_deferred_reason") is not None
            or issue.get("next_terminal_gate_or_owner") is not None
            or workflow
            != {
                "scope_complete": True,
                "tasks_complete": True,
                "applicable_verification_complete": True,
            }
            or authorization
            != {"online_issue_bound": True, "explicit_owner_approval": True}
            or not isinstance(read_back, dict)
            or read_back.get("performed") is not False
        ):
            continue
        pull_request = record.get("pull_request")
        if not isinstance(pull_request, dict):
            continue
        pr_number = pull_request.get("number")
        body = pull_request.get("body")
        if (
            not isinstance(pr_number, int)
            or isinstance(pr_number, bool)
            or pr_number <= 0
            or not isinstance(body, str)
            or not re.search(rf"(?m)^Closes #{issue_number}\s*$", body)
        ):
            continue
        matches.append({"number": pr_number, "body": body})
    if len(matches) != 1:
        return False
    selected = matches[0]
    raw = run_read_only(
        root,
        ["gh", "api", "--method", "GET", f"repos/{repository}/pulls/{selected['number']}"],
        runner,
    )
    try:
        pull_request = json.loads(raw)
    except json.JSONDecodeError:
        return False
    if not isinstance(pull_request, dict):
        return False
    head = pull_request.get("head")
    base = pull_request.get("base")
    base_repository = base.get("repo") if isinstance(base, dict) else None
    return (
        pull_request.get("number") == selected["number"]
        and pull_request.get("state") == "open"
        and pull_request.get("merged_at") is None
        and pull_request.get("body") == selected["body"]
        and isinstance(head, dict)
        and head.get("sha") == git_head(root, runner)
        and isinstance(base_repository, dict)
        and base_repository.get("full_name") == repository
    )


def validate_skill_retirement_fixture(case, packet, fixture):
    """Bind retirement applicability to the selected source migration."""
    selected = packet.get("migration", {}).get("selected_input", {})
    contract = packet.get("migration", {}).get("contract", {})
    version = selected.get("previous_version")
    manifest = selected.get("previous_files_sha256")
    sources = contract.get("sources")
    if (not isinstance(version, str) or not isinstance(manifest, str)
            or not isinstance(sources, list)):
        raise ReleaseStateError("actual upgrade retirement fixture lacks selected source evidence")
    matching_sources = [source for source in sources if isinstance(source, dict)
                        and source.get("version") == version and source.get("manifest_sha256") == manifest]
    if len(matching_sources) != 1 or version.lstrip("v") != str(case.get("origin", "")).lstrip("v"):
        raise ReleaseStateError("actual upgrade retirement fixture source differs from its case")
    operations = matching_sources[0].get("operations")
    if not isinstance(operations, list) or not all(isinstance(operation, dict) for operation in operations):
        raise ReleaseStateError("actual upgrade retirement fixture source operations are invalid")
    removals = [operation["path"] for operation in operations
                if operation.get("kind") == "remove" and operation.get("ownership") == "framework-managed"
                and isinstance(operation.get("path"), str)]
    if len(removals) != sum(operation.get("kind") == "remove" and operation.get("ownership") == "framework-managed"
                            for operation in operations):
        raise ReleaseStateError("actual upgrade retirement fixture removal path is invalid")
    retired = [path for path in removals if "/dev-workflow/" in path or "/repo-structure-sync/" in path]
    applicability = "selected" if retired else "not-applicable-no-retired-skill-source-paths"
    expected = {
        "origin": version,
        "source_remove_count": len(removals),
        "fixture_paths": retired,
        "applicability": applicability,
        "rename_source_count": sum(operation.get("kind") == "rename" for operation in operations),
        "customized_retirement": "-customized-" in str(case.get("case", "")) and bool(retired),
    }
    if any(fixture.get(key) != value for key, value in expected.items()):
        raise ReleaseStateError("actual upgrade retirement fixture differs from selected source evidence")
    return "verified" if applicability == "selected" else applicability


def retained_case_artifact(actual_root, case, name, *, document=True):
    expected = f"evidence/{case['case']}/{name}"
    record = case.get("artifacts", {}).get(name)
    if not isinstance(record, dict) or record.get("path") != expected or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("sha256"))):
        raise ReleaseStateError("actual upgrade retained artifact binding is missing")
    try:
        raw = contained_release_asset(actual_root, expected).read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["sha256"]:
            raise ReleaseStateError("actual upgrade retained artifact digest differs")
        return json.loads(raw) if document else raw
    except ReleaseStateError:
        raise
    except (OSError, ValueError, PackageError) as exc:
        raise ReleaseStateError("actual upgrade retained artifact is unavailable or invalid") from exc


def validate_direct_case_artifacts(actual_root, case, origin_identity, target_identity):
    """Bind completion to retained target output, receipts and transaction states."""
    def digest(document):
        return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

    def retained(name, *, document=True):
        return retained_case_artifact(actual_root, case, name, document=document)

    transaction = case.get("transaction_id")
    if not re.fullmatch(r"[0-9a-f]{64}", str(transaction)):
        raise ReleaseStateError("actual upgrade transaction identity is missing")
    before = retained("prestate.json", document=False)
    after = retained("poststate.json", document=False)
    if hashlib.sha256(before).hexdigest() != case.get("prestate_sha256") or hashlib.sha256(after).hexdigest() != case.get("poststate_sha256"):
        raise ReleaseStateError("actual upgrade state snapshot digest differs")
    packet = retained("packet.json")
    decision = retained("decision.json")
    origin = packet.get("provenance", {}).get("source", {})
    selected = packet.get("migration", {}).get("selected_input", {})
    incoming = packet.get("package", {})
    if (packet.get("schema_version") != "upgrade-remediation-packet/v1"
            or origin.get("version") != case.get("origin") or origin.get("commit") != origin_identity["commit"]
            or selected.get("previous_version") != case["origin"].lstrip("v")
            or selected.get("previous_files_sha256") != origin_identity["manifest"]["sha256"]
            or incoming.get("source", {}).get("commit") != target_identity["commit"]
            or incoming.get("manifest_sha256") != target_identity["manifest"]["sha256"]):
        raise ReleaseStateError("actual upgrade origin or incoming packet identity differs")
    packet_unsigned = {key: value for key, value in packet.items() if key != "canonical_digest"}
    if (packet.get("transaction_id") != transaction or packet.get("plan_sha256") != transaction
            or digest(packet_unsigned) != packet.get("canonical_digest")
            or decision.get("packet_sha256") != packet.get("canonical_digest")
            or decision.get("transaction_id") != transaction or decision.get("status") != "approved"):
        raise ReleaseStateError("actual upgrade packet or decision binding differs")
    before_authority = retained("provenance-before.yaml", document=False)
    after_authority = retained("provenance-after.yaml", document=False)
    before_provenance = yaml.safe_load(before_authority)
    after_provenance = yaml.safe_load(after_authority)
    if (before_provenance.get("source") != packet["provenance"]["source"]
            or hashlib.sha256(before_authority).hexdigest() != packet["provenance"].get("sha256")):
        raise ReleaseStateError("actual upgrade prior provenance differs from its packet")
    if case["recovery"] != "none":
        interrupted = retained("interrupted.json", document=False)
        recovery = retained("recovery.json")
        if interrupted == before or recovery.get("transaction_id") != transaction:
            raise ReleaseStateError("actual upgrade interruption or recovery evidence is incomplete")
        expected_state = "rolled-back" if case["recovery"] == "rolled-back" else "awaiting-target-validation"
        if recovery.get("state", recovery.get("transaction_state")) != expected_state:
            raise ReleaseStateError("actual upgrade recovery did not reach the expected state")
    if case["recovery"] == "rolled-back":
        if before != after or before_authority != after_authority:
            raise ReleaseStateError("actual upgrade rollback snapshots differ")
        return
    if (after_provenance.get("source", {}).get("commit") != target_identity["commit"]
            or after_provenance.get("previous_source", {}).get("commit") != origin_identity["commit"]):
        raise ReleaseStateError("actual upgrade finalized provenance source differs")
    before_ledger = yaml.safe_load(retained("customizations-before.yaml", document=False))
    after_ledger = yaml.safe_load(retained("customizations-after.yaml", document=False))
    if {item["id"] for item in before_ledger["customizations"]} != {item["id"] for item in after_ledger["customizations"]}:
        raise ReleaseStateError("actual upgrade customization identities were not preserved")
    receipt = retained("supplied-target-validation.json")
    execution = case.get("target_validation", {})
    output = retained("target-validation.log", document=False)
    finalization = retained("finalization.json")
    if (receipt.get("schema_version") != "target-validation-receipt/v1"
            or receipt.get("transaction_id") != transaction or receipt.get("plan_sha256") != transaction
            or receipt.get("packet_sha256") != packet["canonical_digest"]
            or receipt.get("decision_sha256") != case["artifacts"]["decision.json"]["sha256"]
            or receipt.get("execution") != execution or finalization != case.get("finalization")):
        raise ReleaseStateError("actual upgrade validation receipt or finalization binding differs")
    profile = packet.get("target_validation_profile", {})
    if (not isinstance(execution.get("argv"), list) or not execution["argv"]
            or execution["argv"] != profile.get("argv") or receipt.get("target_validation_profile") != profile
            or receipt.get("target_validation_profile_digest") != packet.get("target_validation_profile_digest")
            or execution.get("outcome") != "passed" or type(execution.get("exit_code")) is not int or execution["exit_code"] != 0
            or not re.fullmatch(r"[0-9a-f]{64}", str(execution.get("output_sha256")))
            or hashlib.sha256(output).hexdigest() != execution["output_sha256"]
            or not isinstance(execution.get("evidence"), str) or transaction not in execution["evidence"]):
        raise ReleaseStateError("actual upgrade target command or output evidence differs")
    if iso_timestamp(execution.get("completed_at"), "target validation completed_at") < iso_timestamp(execution.get("started_at"), "target validation started_at"):
        raise ReleaseStateError("actual upgrade target validation timing is invalid")
    failed_receipt = retained("failed-target-validation.json")
    failed_output = retained("target-validation-rejected.log", document=False)
    failed_execution = case.get("failed_target_validation", {})
    if (any(failed_receipt.get(key) != receipt.get(key) for key in (
            "schema_version", "transaction_id", "plan_sha256", "packet_sha256",
            "decision_sha256", "target_validation_profile", "target_validation_profile_digest"))
            or failed_receipt.get("execution") != failed_execution
            or failed_execution.get("argv") != profile["argv"]
            or failed_execution.get("outcome") != "failed"
            or type(failed_execution.get("exit_code")) is not int or failed_execution["exit_code"] != 17
            or hashlib.sha256(failed_output).hexdigest() != failed_execution.get("output_sha256")
            or not isinstance(failed_execution.get("evidence"), str) or transaction not in failed_execution["evidence"]):
        raise ReleaseStateError("actual upgrade failed target execution evidence differs")
    if iso_timestamp(failed_execution.get("completed_at"), "failed target completed_at") < iso_timestamp(failed_execution.get("started_at"), "failed target started_at"):
        raise ReleaseStateError("actual upgrade failed target validation timing is invalid")
    for label in ("failed-target-validation-receipt", "target-validator-disagreement"):
        rejected = [item for item in case.get("negative_evidence", []) if item.get("case") == label]
        if (len(rejected) != 1 or rejected[0].get("outcome") != "passed"
                or not re.fullmatch(r"[0-9a-f]{64}", str(rejected[0].get("protected_state_sha256")))
                or not rejected[0].get("observed_rejection")):
            raise ReleaseStateError("actual upgrade failed validation lacks protected-state rejection evidence")


def load_v017_execution_set(root, actual_root):
    """Read the owner-selected, immutable seven-plus-two v0.17 evidence set.

    This is a release-specific exception, not a general runner-drift reuse rule.
    Original terminals remain native execution records, including the failure.
    """
    expected = (
        ("07", "327b4ca40a21cdbe06f3b6b6c36f30d3d1645c6cd2c71ca55b3ec9ec97babdfd",
         "9b6780514fb3cd299cf831b7be20931d2c157dde", "failed",
         "6e267374c93de67a70386475fb6dd88ed815efe2997dc44398ab84ba15ba85da"),
        ("09", "c75438f361a3ebd797cb0109dece3694a756099f83b91d7ea83da2c9122974a9",
         "a7b171df383ba416815275e81ed06f13e77b13ca", "passed",
         "7b83294b491465486070dcf0796e7485e229b37bfc417772b4d4f7f39590feba"),
    )
    archive = "b9e6b38515e8ac82731734b99bacb97b40ca0c7ad543d2b6f84390b4cdb94a22"
    runner_path = ".github/scripts/validate-v017-direct-upgrades.py"
    labels = [origin + suffix for origin in ("v0.6.0", "v0.9.0", "v0.16.0")
              for suffix in ("-pristine-resume", "-customized-none", "-customized-rollback")]
    try:
        record = json.loads(contained_release_asset(actual_root, "execution-set.json").read_bytes())
        if (record.get("schema_version") != "v017-direct-upgrade-evidence-set/v1"
                or record.get("release") != "v0.17.0"
                or record.get("authority") != "owner-selected-two-case-retest-and-publication"
                or record.get("archive_sha256") != archive
                or record.get("attempts") != [
                    {"id": item[0], "terminal": f"{item[0]}/terminal.json", "sha256": item[1],
                     "accepted_cases": labels[:7] if item[0] == "07" else labels[7:]}
                    for item in expected]):
            raise ReleaseStateError("v0.17 execution set differs from the bounded owner decision")
        if hashlib.sha256((root / runner_path).read_bytes()).hexdigest() != expected[1][4]:
            raise ReleaseStateError("v0.17 execution set cannot cover another runner change")
        cases, case_roots, terminals = [], {}, []
        for attempt, terminal_sha, subject, outcome, runner_sha in expected:
            attempt_root = actual_root / attempt
            raw = contained_release_asset(actual_root, f"{attempt}/terminal.json").read_bytes()
            if hashlib.sha256(raw).hexdigest() != terminal_sha:
                raise ReleaseStateError("v0.17 original execution terminal changed")
            terminal = json.loads(raw)
            native = subprocess.run(["git", "show", f"{subject}:{runner_path}"],
                                    cwd=root, capture_output=True, check=False)
            retained_runner = contained_release_asset(actual_root, f"{attempt}/runner.py").read_bytes()
            if (native.returncode != 0 or native.stdout != retained_runner
                    or hashlib.sha256(retained_runner).hexdigest() != runner_sha
                    or terminal.get("subject_sha") != subject or terminal.get("outcome") != outcome
                    or terminal.get("runner") != {"path": runner_path, "sha256": runner_sha}
                    or terminal.get("archive_sha256") != archive
                    or terminal.get("schema_version") != "direct-upgrade-execution/v1"
                    or terminal.get("evidence_kind") != "actual-isolated-target-execution"):
                raise ReleaseStateError("v0.17 native execution provenance differs")
            accepted = labels[:7] if attempt == "07" else labels[7:]
            if ([case.get("case") for case in terminal.get("cases", [])] != accepted
                    or any(case.get("outcome") != "passed" for case in terminal["cases"])):
                raise ReleaseStateError("v0.17 selected execution cases differ")
            if attempt == "09":
                selector = contained_release_asset(actual_root, "09/selected-cases.py").read_bytes()
                if (hashlib.sha256(selector).hexdigest() != terminal["selection_runner"]["sha256"]
                        or terminal["invocation"][1] != terminal["selection_runner"]["path"]
                        or terminal["selection"] != {"full_matrix": False,
                            "mode": "owner-selected-two-case-retest", "required_cases": labels[7:]}):
                    raise ReleaseStateError("v0.17 selected dispatcher identity differs")
            elif not terminal.get("failure") or terminal["invocation"][1] != runner_path:
                raise ReleaseStateError("v0.17 original failed outcome was not preserved")
            # Verify every declared retained artifact, including ancillary logs.
            for case in terminal["cases"]:
                for artifact in case.get("artifacts", {}).values():
                    data = contained_release_asset(attempt_root, artifact["path"]).read_bytes()
                    if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
                        raise ReleaseStateError("v0.17 retained execution artifact changed")
                cases.append(case)
                case_roots[case["case"]] = attempt_root
            terminals.append(terminal)
        if terminals[0]["package_source"] != terminals[1]["package_source"]:
            raise ReleaseStateError("v0.17 executions used different package sources")
        return cases, case_roots, terminals[0]["package_source"], archive
    except ReleaseStateError:
        raise
    except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
        raise ReleaseStateError("v0.17 execution set is missing or invalid") from exc


def v017_affected_only_case_matrix(root, matrix):
    """Keep native case identity while admitting the owner's exact two-line repair.

    This does not assert execution against replacement bytes. The owner's
    affected-only decision combines native cases with focused runner tests.
    No other archive, payload delta, origin or execution mechanism is covered.
    """
    import io
    import zipfile

    release = root / ".dev/releases/v0.17.0"
    actual = release / "route-assets/actual"
    old_hash = "b9e6b38515e8ac82731734b99bacb97b40ca0c7ad543d2b6f84390b4cdb94a22"
    new_hash = "66a731f04695386416d7eb92b8a4d49ea8daaf4b118d8c93825764315c982b1a"
    try:
        archives = {edge["artifacts"]["archive"]["sha256"] for route in matrix["routes"]
                    for edge in route["edges"] if edge["to_version"] == "v0.17.0"}
        baseline_raw = contained_release_asset(actual, "baseline-support-matrix.yaml").read_bytes()
        if hashlib.sha256(baseline_raw).hexdigest() != "3396cadfcddbc9d34bfcc513b927f53fc433e6b61e18ae028370cc56c090d06c":
            raise ReleaseStateError("v0.17 affected-only baseline matrix bytes differ")
        baseline = yaml.safe_load(baseline_raw)
        if (archives != {new_hash}
                or matrix["target"]["commit"] != "8eed3960f19c57050c8e8a8e1ecedbc3004aabc2"
                or matrix["retained_origins"] != baseline["retained_origins"]):
            raise ReleaseStateError("v0.17 affected-only archive or origin binding differs")

        payloads = []
        for path, expected in [(actual / "baseline.zip", old_hash),
                               (release / "route-assets/admitted/ai-collaboration-framework-v0.17.0.zip", new_hash)]:
            raw = contained_release_asset(release, path.relative_to(release).as_posix()).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ReleaseStateError("v0.17 affected-only archive bytes differ")
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                payloads.append({item.filename.split("/payload/", 1)[1]:
                                 (item.external_attr, archive.read(item))
                                 for item in archive.infolist()
                                 if "/payload/" in item.filename and not item.is_dir()})
        before, after = payloads
        path = ".ai/scripts/check-all.sh"
        changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
        if changed != {path} or before[path][0] != after[path][0]:
            raise ReleaseStateError("v0.17 affected-only payload delta differs")
        expected = before[path][1]
        for anchor, addition in [
            (b'            "AI Context Release State Fail-Closed Tests" \\\n',
             b'            "Release Asset Identity Contract Tests" \\\n'),
            (b'            "Validation Lifecycle Fail-Closed Tests" \\\n',
             b'            "Bounded Validation Dependency Observation" \\\n'),
        ]:
            if expected.count(anchor) != 1:
                raise ReleaseStateError("v0.17 affected-only repair anchor differs")
            expected = expected.replace(anchor, anchor + addition)
        if after[path][1] != expected:
            raise ReleaseStateError("v0.17 affected-only archived repair differs")
        return baseline
    except ReleaseStateError:
        raise
    except (OSError, ValueError, KeyError, TypeError, PackageError, zipfile.BadZipFile) as exc:
        raise ReleaseStateError("v0.17 affected-only evidence is missing or invalid") from exc


def v018_rebind_execution_set():
    """Return the one-version contract that preserves Candidate10 native evidence."""
    return {
        "schema_version": "v018-direct-upgrade-rebind/v1",
        "release": "v0.18.0",
        "authority": "user-authorized-excessive-validation-rebind",
        "original": {
            "archive_sha256": V018_REBIND_ARCHIVE_SHA256,
            "subject_sha": V018_REBIND_SUBJECT_SHA,
            "runner": {
                "path": V018_REBIND_RUNNER_PATH,
                "sha256": V018_REBIND_RUNNER_SHA256,
            },
            "terminal": {
                "path": "terminal.json",
                "sha256": V018_REBIND_TERMINAL_SHA256,
            },
            "case_evidence_index": {
                "path": "case-evidence-index.json",
                "sha256": V018_REBIND_CASE_INDEX_SHA256,
                "evidence_count": V018_REBIND_CASE_EVIDENCE_COUNT,
            },
            "baseline_support_matrix": {
                "path": "baseline-support-matrix.yaml",
                "sha256": V018_REBIND_BASELINE_MATRIX_SHA256,
            },
            "baseline_archive": {
                "path": "baseline.zip",
                "sha256": V018_REBIND_ARCHIVE_SHA256,
            },
        },
        "cases": list(V018_REBIND_CASES),
        "allowed_payload_deltas": [
            {
                "path": path,
                "mode": "0644",
                "anchor": anchor.decode("ascii"),
                "addition": addition.decode("ascii"),
            }
            for path, anchor, addition in V018_REBIND_PAYLOAD_DELTAS
        ],
    }


def v018_payload_entries(content):
    """Read one package payload as an unambiguous path-to-byte-and-mode map."""
    import io
    import zipfile

    try:
        entries = {}
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                name = item.filename
                marker = "/payload/"
                if marker not in name:
                    continue
                prefix, relative = name.split(marker, 1)
                pure = PurePosixPath(relative)
                if (
                    not prefix
                    or not relative
                    or name.count(marker) != 1
                    or "\\" in name
                    or pure.is_absolute()
                    or str(pure) != relative
                    or any(part in {"", ".", ".."} for part in pure.parts)
                ):
                    raise ReleaseStateError("v0.18 rebound payload path is invalid")
                key = pure.as_posix()
                if key in entries:
                    raise ReleaseStateError("v0.18 rebound payload has duplicate paths")
                entries[key] = (item.external_attr, archive.read(item))
        if not entries:
            raise ReleaseStateError("v0.18 rebound payload is empty")
        return entries
    except ReleaseStateError:
        raise
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise ReleaseStateError("v0.18 rebound payload cannot be read") from exc


def validate_v018_case_evidence_index(actual_root):
    """Bind every retained Candidate10 artifact through the checked-in index."""
    raw = contained_release_asset(actual_root, "case-evidence-index.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != V018_REBIND_CASE_INDEX_SHA256:
        raise ReleaseStateError("v0.18 native case evidence index changed")
    try:
        index = json.loads(raw)
    except ValueError as exc:
        raise ReleaseStateError("v0.18 native case evidence index is invalid") from exc
    terminal = {
        "asset_id": "actual-direct-v018-terminal",
        "path": "actual/terminal.json",
        "sha256": V018_REBIND_TERMINAL_SHA256,
    }
    entries = index.get("evidence") if isinstance(index, dict) else None
    if (
        not isinstance(index, dict)
        or set(index) != {"schema_version", "terminal", "evidence"}
        or index.get("schema_version") != "v018-direct-case-evidence-index/v1"
        or index.get("terminal") != terminal
        or not isinstance(entries, list)
        or len(entries) != V018_REBIND_CASE_EVIDENCE_COUNT
    ):
        raise ReleaseStateError("v0.18 native case evidence index differs")
    paths, asset_ids = set(), set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"staged", "terminal_path"}:
            raise ReleaseStateError("v0.18 native case evidence entry is invalid")
        staged = entry["staged"]
        path = entry["terminal_path"]
        if (
            not isinstance(staged, dict)
            or set(staged) != {"asset_id", "path", "sha256"}
            or not isinstance(staged.get("asset_id"), str)
            or not staged["asset_id"]
            or not isinstance(path, str)
            or not path
            or not SHA256_RE.fullmatch(str(staged.get("sha256")))
            or staged.get("path") != f"actual/{path}"
            or path in paths
            or staged["asset_id"] in asset_ids
        ):
            raise ReleaseStateError("v0.18 native case evidence entry differs")
        try:
            observed = contained_release_asset(actual_root, path).read_bytes()
        except (OSError, ValueError, PackageError) as exc:
            raise ReleaseStateError("v0.18 native case evidence path is unavailable") from exc
        if hashlib.sha256(observed).hexdigest() != staged["sha256"]:
            raise ReleaseStateError("v0.18 native case evidence bytes changed")
        paths.add(path)
        asset_ids.add(staged["asset_id"])


def validate_v018_rebound_payload_delta(baseline_archive, replacement_archive, current_payloads):
    """Validate the exact two-path C10-to-replacement repair from explicit bytes.

    This narrow helper deliberately has no current-admission or matrix authority.
    Derived route validators may use the same byte-level proof while their caller
    binds the replacement archive to the current route admission.
    """
    before = v018_payload_entries(baseline_archive)
    after = v018_payload_entries(replacement_archive)
    expected_paths = {path for path, _anchor, _addition in V018_REBIND_PAYLOAD_DELTAS}
    changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    if (
        changed != expected_paths
        or not isinstance(current_payloads, dict)
        or set(current_payloads) != expected_paths
    ):
        raise ReleaseStateError("v0.18 rebound payload delta differs")
    for path, anchor, addition in V018_REBIND_PAYLOAD_DELTAS:
        if path not in before or path not in after or before[path][0] != after[path][0]:
            raise ReleaseStateError("v0.18 rebound payload mode differs")
        expected = before[path][1]
        if expected.count(anchor) != 1:
            raise ReleaseStateError("v0.18 rebound payload anchor differs")
        expected = expected.replace(anchor, anchor + addition)
        if after[path][1] != expected or current_payloads[path] != expected:
            raise ReleaseStateError("v0.18 rebound payload bytes differ")


def load_v018_execution_set(root, actual_root):
    """Load the immutable Candidate10 matrix for the one v0.18 replacement path."""
    try:
        record = json.loads(contained_release_asset(actual_root, "execution-set.json").read_bytes())
        if record != v018_rebind_execution_set():
            raise ReleaseStateError("v0.18 execution set differs from the bounded user decision")
        terminal_raw = contained_release_asset(actual_root, "terminal.json").read_bytes()
        if hashlib.sha256(terminal_raw).hexdigest() != V018_REBIND_TERMINAL_SHA256:
            raise ReleaseStateError("v0.18 original execution terminal changed")
        terminal = json.loads(terminal_raw)
        validate_v018_case_evidence_index(actual_root)
        runner = terminal.get("runner", {})
        cases = terminal.get("cases")
        invocation = terminal.get("invocation")
        start = iso_timestamp(terminal.get("started_at"), "v0.18 native execution started_at")
        end = iso_timestamp(terminal.get("completed_at"), "v0.18 native execution completed_at")
        duration = terminal.get("duration_seconds")
        if (
            terminal.get("schema_version") != "direct-upgrade-execution/v1"
            or terminal.get("evidence_kind") != "actual-isolated-target-execution"
            or terminal.get("outcome") != "passed"
            or terminal.get("archive_sha256") != V018_REBIND_ARCHIVE_SHA256
            or terminal.get("subject_sha") != V018_REBIND_SUBJECT_SHA
            or terminal.get("package_source", {}).get("commit") != V018_REBIND_SUBJECT_SHA
            or runner != {"path": V018_REBIND_RUNNER_PATH, "sha256": V018_REBIND_RUNNER_SHA256}
            or end < start
            or type(duration) not in (int, float)
            or not math.isfinite(duration)
            or duration <= 0
            or not isinstance(invocation, list)
            or len(invocation) < 4
            or invocation[1] != V018_REBIND_RUNNER_PATH
            or not all(isinstance(arg, str) and arg for arg in invocation)
            or invocation.count("--subject-sha") != 1
            or invocation[-1] == "--subject-sha"
            or invocation[invocation.index("--subject-sha") + 1] != V018_REBIND_SUBJECT_SHA
            or not isinstance(cases, list)
            or [case.get("case") for case in cases if isinstance(case, dict)] != list(V018_REBIND_CASES)
            or any(not isinstance(case, dict) or case.get("outcome") != "passed" for case in cases)
        ):
            raise ReleaseStateError("v0.18 native execution provenance differs")
        retained_runner = contained_release_asset(
            actual_root, "validate-v018-direct-upgrades.py"
        ).read_bytes()
        native = subprocess.run(
            ["git", "show", f"{V018_REBIND_SUBJECT_SHA}:{V018_REBIND_RUNNER_PATH}"],
            cwd=root,
            capture_output=True,
            check=False,
        )
        current_runner = (root / V018_REBIND_RUNNER_PATH).read_bytes()
        if (
            native.returncode != 0
            or native.stdout != retained_runner
            or hashlib.sha256(retained_runner).hexdigest() != V018_REBIND_RUNNER_SHA256
            or current_runner != retained_runner
        ):
            raise ReleaseStateError("v0.18 native runner provenance differs")
        return cases, {case["case"]: actual_root for case in cases}, terminal["package_source"], V018_REBIND_ARCHIVE_SHA256
    except ReleaseStateError:
        raise
    except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
        raise ReleaseStateError("v0.18 execution set is missing or invalid") from exc


def v018_affected_only_case_matrix(root, matrix):
    """Prove the exact shell-assets repair without relabeling Candidate10 execution."""
    release = root / ".dev/releases/v0.18.0"
    actual = release / "route-assets/actual"
    try:
        archives = {
            edge["artifacts"]["archive"]["sha256"]
            for route in matrix["routes"]
            for edge in route["edges"]
            if edge["to_version"] == "v0.18.0"
        }
        current_subject = matrix["target"]["commit"]
        if (
            matrix["target"].get("version") != "v0.18.0"
            or not SHA_RE.fullmatch(str(current_subject))
            or current_subject == V018_REBIND_SUBJECT_SHA
            or len(archives) != 1
            or not all(SHA256_RE.fullmatch(str(value)) for value in archives)
            or V018_REBIND_ARCHIVE_SHA256 in archives
        ):
            raise ReleaseStateError("v0.18 rebound archive or source differs")
        baseline_raw = contained_release_asset(actual, "baseline-support-matrix.yaml").read_bytes()
        if hashlib.sha256(baseline_raw).hexdigest() != V018_REBIND_BASELINE_MATRIX_SHA256:
            raise ReleaseStateError("v0.18 rebound baseline matrix bytes differ")
        baseline = yaml.safe_load(baseline_raw)
        if (
            not isinstance(baseline, dict)
            or baseline.get("target", {}).get("version") != "v0.18.0"
            or baseline.get("target", {}).get("commit") != V018_REBIND_SUBJECT_SHA
            or baseline.get("retained_origins") != matrix.get("retained_origins")
        ):
            raise ReleaseStateError("v0.18 rebound baseline origin binding differs")
        baseline_archives = {
            edge["artifacts"]["archive"]["sha256"]
            for route in baseline["routes"]
            for edge in route["edges"]
            if edge["to_version"] == "v0.18.0"
        }
        if baseline_archives != {V018_REBIND_ARCHIVE_SHA256}:
            raise ReleaseStateError("v0.18 rebound baseline archive differs")
        baseline_archive = contained_release_asset(actual, "baseline.zip").read_bytes()
        replacement = contained_release_asset(
            release, "route-assets/admitted/ai-collaboration-framework-v0.18.0.zip"
        ).read_bytes()
        replacement_sha256 = hashlib.sha256(replacement).hexdigest()
        if (
            hashlib.sha256(baseline_archive).hexdigest() != V018_REBIND_ARCHIVE_SHA256
            or archives != {replacement_sha256}
        ):
            raise ReleaseStateError("v0.18 rebound archive bytes differ")
        validate_v018_rebound_payload_delta(
            baseline_archive,
            replacement,
            {path: (root / path).read_bytes() for path, _anchor, _addition in V018_REBIND_PAYLOAD_DELTAS},
        )
        return baseline
    except ReleaseStateError:
        raise
    except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
        raise ReleaseStateError("v0.18 rebound evidence is missing or invalid") from exc


def validate_direct_upgrade_execution(root, version, sources, matrix):
    """Require actual isolated target evidence for every prospective direct origin."""
    release_dir = root / ".dev/releases" / version
    actual_root = release_dir / "route-assets/actual"
    if version == "v0.17.0" and (actual_root / "execution-set.json").exists():
        cases, case_roots, package_source, archive = load_v017_execution_set(root, actual_root)
        archives = {edge["artifacts"]["archive"]["sha256"] for route in matrix["routes"]
                    for edge in route["edges"] if edge["to_version"] == version}
        case_matrix = matrix
        if archives != {archive} or package_source.get("commit") != matrix["target"]["commit"]:
            case_matrix = v017_affected_only_case_matrix(root, matrix)
        if package_source.get("commit") != case_matrix["target"]["commit"]:
            raise ReleaseStateError("v0.17 native execution set differs from its original route subject")
        validate_direct_upgrade_cases(cases, case_roots, sources, case_matrix)
        return
    if version == "v0.18.0" and (actual_root / "execution-set.json").exists():
        cases, case_roots, package_source, archive = load_v018_execution_set(root, actual_root)
        archives = {edge["artifacts"]["archive"]["sha256"] for route in matrix["routes"]
                    for edge in route["edges"] if edge["to_version"] == version}
        case_matrix = matrix
        if archives != {archive} or package_source.get("commit") != matrix["target"]["commit"]:
            case_matrix = v018_affected_only_case_matrix(root, matrix)
        if package_source.get("commit") != case_matrix["target"]["commit"]:
            raise ReleaseStateError("v0.18 native execution set differs from its original route subject")
        validate_direct_upgrade_cases(cases, case_roots, sources, case_matrix)
        return
    evidence_path = release_dir / "route-assets/actual/terminal.json"
    try:
        evidence = json.loads(evidence_path.read_bytes())
    except (OSError, ValueError) as exc:
        raise ReleaseStateError("actual direct upgrade terminal is missing or invalid") from exc
    if (evidence.get("schema_version") != "direct-upgrade-execution/v1"
            or evidence.get("evidence_kind") != "actual-isolated-target-execution"
            or evidence.get("outcome") != "passed"):
        raise ReleaseStateError("actual direct upgrade evidence must report passed execution")
    archives = {edge["artifacts"]["archive"]["sha256"] for route in matrix["routes"] for edge in route["edges"] if edge["to_version"] == version}
    if archives != {evidence.get("archive_sha256")}:
        raise ReleaseStateError("actual upgrade archive differs from the direct route subject")
    if evidence.get("package_source", {}).get("commit") != matrix["target"]["commit"]:
        raise ReleaseStateError("actual upgrade package source differs from the matrix")
    runner = evidence.get("runner", {})
    path = DIRECT_UPGRADE_RUNNERS.get(version, ".github/scripts/validate-v016-direct-upgrades.py")
    if runner.get("path") != path:
        raise ReleaseStateError("actual upgrade runner is not the canonical execution authority")
    if not SHA_RE.fullmatch(str(evidence.get("subject_sha"))):
        raise ReleaseStateError("actual upgrade subject SHA is invalid")
    start = iso_timestamp(evidence.get("started_at"), "actual execution started_at")
    end = iso_timestamp(evidence.get("completed_at"), "actual execution completed_at")
    duration = evidence.get("duration_seconds")
    invocation = evidence.get("invocation")
    if (end < start or type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0
            or not isinstance(invocation, list) or len(invocation) < 4
            or invocation[1] != path or not all(isinstance(arg, str) and arg for arg in invocation)
            or invocation.count("--subject-sha") != 1 or invocation[-1] == "--subject-sha"
            or invocation[invocation.index("--subject-sha") + 1] != evidence["subject_sha"]):
        raise ReleaseStateError("actual upgrade execution command or timing is incomplete")
    if hashlib.sha256((root / path).read_bytes()).hexdigest() != runner.get("sha256"):
        raise ReleaseStateError("actual upgrade runner content differs from execution")
    cases = evidence.get("cases")
    case_roots = {case.get("case"): actual_root for case in cases} if isinstance(cases, list) else {}
    validate_direct_upgrade_cases(cases, case_roots, sources, matrix)


def validate_direct_upgrade_cases(cases, case_roots, sources, matrix):
    """Apply the same acceptance checks to each native execution's artifact root."""
    required_negatives = {"missing-origin-manifest", "tampered-origin-manifest", "origin-version-disagreement", "tampered-incoming-validator", "fault-injected-incoming-validator-disagreement", "ambiguous-provenance-authority", "unresolved-customization", "missing-owner-decision", "tampered-owner-decision", "missing-target-validation", "failed-target-validation-receipt", "target-validator-disagreement", "tampered-target-validation-receipt", "candidate-authority-disagreement"}
    if not isinstance(cases, list) or len(cases) != 3 * len(sources):
        raise ReleaseStateError("actual upgrade matrix must contain three cases per origin")
    for origin in sources:
        selected = {case.get("case"): case for case in cases if case.get("origin") == origin}
        labels = {origin + suffix for suffix in ("-pristine-resume", "-customized-none", "-customized-rollback")}
        if set(selected) != labels or any(case.get("outcome") != "passed" for case in selected.values()):
            raise ReleaseStateError("actual upgrade origin cases are incomplete or failed")
        rollback = selected[origin + "-customized-rollback"]
        if (rollback.get("recovery") != "rolled-back"
                or not re.fullmatch(r"[0-9a-f]{64}", str(rollback.get("prestate_sha256")))
                or rollback.get("prestate_sha256") != rollback.get("poststate_sha256")):
            raise ReleaseStateError("actual upgrade rollback lacks exact restored prestate")
        origin_identity = next((item for item in matrix["retained_origins"] if item["version"] == origin), None)
        if origin_identity is None:
            raise ReleaseStateError("actual upgrade origin identity is missing from matrix")
        retirement_statuses = {}
        for suffix, recovery in (("-pristine-resume", "resume"), ("-customized-none", "none"), ("-customized-rollback", "rolled-back")):
            case = selected[origin + suffix]
            if case.get("recovery") != recovery:
                raise ReleaseStateError("actual upgrade recovery mode differs from its case")
            validate_direct_case_artifacts(case_roots[case["case"]], case, origin_identity, matrix["target"])
            if "retirement-fixture.json" in case.get("artifacts", {}):
                fixture = retained_case_artifact(case_roots[case["case"]], case, "retirement-fixture.json")
                if not isinstance(fixture, dict):
                    raise ReleaseStateError("actual upgrade retirement fixture is invalid")
                if fixture.get("applicability") == "not-applicable-no-retired-skill-source-paths":
                    retirement_statuses[case["case"]] = validate_skill_retirement_fixture(case, retained_case_artifact(
                        case_roots[case["case"]], case, "packet.json"), fixture)
        for suffix in ("-pristine-resume", "-customized-none"):
            case = selected[origin + suffix]
            final = case.get("finalization", {})
            validation = case.get("target_validation", {})
            if (final.get("status") != "finalized" or final.get("effective_rule_readiness", {}).get("action_ready") is not True
                    or validation.get("outcome") != "passed" or validation.get("exit_code") != 0):
                raise ReleaseStateError("actual upgrade requires passed target validation and finalized action readiness")
            cutovers = case.get("semantic_cutovers", {})
            if any(cutovers.get(key) != expected for key, expected in {"provider_component_selection": "preserved", "source_specific_managed_removals": "verified", "commit_grammar_adoption": "verified", "effective_rule_regeneration": "verified"}.items()):
                raise ReleaseStateError("actual upgrade semantic cutover evidence is incomplete")
            expected_retirement = retirement_statuses.get(case["case"], "verified")
            if cutovers.get("skill_retirement") != expected_retirement:
                raise ReleaseStateError("actual upgrade skill retirement applicability differs from retained evidence")
        if not selected[origin + "-customized-none"]["semantic_cutovers"].get("target_customization_ids"):
            raise ReleaseStateError("actual customized upgrade lacks retained semantic customization")
        negative = selected[origin + "-pristine-resume"].get("negative_evidence", [])
        if not required_negatives.issubset({item.get("case") for item in negative
                if item.get("outcome") == "passed" and item.get("observed_rejection")
                and re.fullmatch(r"[0-9a-f]{64}", str(item.get("protected_state_sha256")))}):
            raise ReleaseStateError("actual upgrade fail-closed boundary evidence is incomplete")


def validate_retained_origin_route_evidence(
    root: Path,
    version: str,
    artifacts: dict[str, Any],
    automatic_upgrade_sources: list[str],
) -> None:
    """Validate the v0.14+ source-only support matrix and canonical route receipts."""

    if version_key(version) < (0, 14, 0):
        expected = {
            "release_notes": "release-notes.md",
            "migration_guide": "migration-guide.md",
        }
        if artifacts != expected:
            raise ReleaseStateError("artifacts must name the two canonical authored files")
        return
    direct_required = version_key(version) >= (0, 16, 0)
    if direct_required:
        predecessors = []
        for path in (root / ".dev/releases").glob("v*/release.yaml"):
            try:
                record = yaml.safe_load(path.read_bytes())
            except (OSError, yaml.YAMLError) as exc:
                raise ReleaseStateError(f"cannot read governed predecessor: {path}") from exc
            if not isinstance(record, dict):
                raise ReleaseStateError(f"invalid governed predecessor: {path}")
            candidate = record.get("version")
            if record.get("distribution_kind") == "governed-package":
                if not isinstance(candidate, str):
                    raise ReleaseStateError(f"missing governed predecessor version: {path}")
                if version_key(candidate) < version_key(version):
                    predecessors.append(candidate)
        if not predecessors:
            raise ReleaseStateError("cannot establish the immediate previous governed package")
        previous = max(predecessors, key=version_key)
        expected_sources = ["v0.6.0", "v0.9.0", previous]
        if automatic_upgrade_sources != expected_sources:
            raise ReleaseStateError(
                f"v0.16+ automatic sources must exactly equal {expected_sources}"
            )
        origins = (previous, "v0.9.0", "v0.6.0")
    elif len(automatic_upgrade_sources) != 1:
        raise ReleaseStateError(
            "compatibility.automatic_upgrade_sources must contain exactly "
            "the immediate previous governed package version"
        )
    else:
        origins = (automatic_upgrade_sources[0], "v0.9.0", "v0.6.0")
    expected_evidence = [
        f"route-evidence/{origin}-to-{version}.json" for origin in origins
    ]
    expected = {
        "release_notes": "release-notes.md",
        "migration_guide": "migration-guide.md",
        "support_matrix": "support-matrix.yaml",
        "route_evidence": expected_evidence,
    }
    if artifacts != expected:
        raise ReleaseStateError(
            "v0.14+ artifacts must exactly name authored files, support matrix, "
            "and ordered retained-origin route evidence"
        )
    release_dir = root / ".dev" / "releases" / version
    matrix_path = release_dir / "support-matrix.yaml"
    try:
        matrix, matrix_bytes = load_route_matrix(matrix_path)
    except MatrixValidationError as exc:
        raise ReleaseStateError(f"{matrix_path}: {exc}") from exc
    target = matrix.get("target") if isinstance(matrix, dict) else None
    if (
        matrix.get("matrix_id") != f"upgrade-route-matrix-{version}"
        or not isinstance(target, dict)
        or target.get("version") != version
        or target.get("release_id") != f"REL-{version}"
    ):
        raise ReleaseStateError("support matrix identity must match the candidate release")
    matrix_reference = f".dev/releases/{version}/support-matrix.yaml"
    for origin, evidence_ref in zip(origins, expected_evidence, strict=True):
        try:
            result = resolve_upgrade_route(
                matrix,
                origin=origin,
                target=version,
                matrix_bytes=matrix_bytes,
                asset_root=release_dir,
                matrix_reference=matrix_reference,
            )
        except MatrixValidationError as exc:
            raise ReleaseStateError(
                f"{matrix_path}: cannot prove {origin} to {version}: {exc}"
            ) from exc
        if direct_required and result.get("route_kind") != "direct":
            raise ReleaseStateError(
                f"{origin} to {version} requires one direct edge; intermediate upgrades cannot satisfy retained support"
            )
        if result.get("route_kind") not in {"direct", "orchestrated-multi-hop"}:
            raise ReleaseStateError(
                f"{origin} to {version} must resolve direct or orchestrated-multi-hop"
            )
        evidence_path = release_dir / evidence_ref
        try:
            evidence_bytes = evidence_path.read_bytes()
        except OSError as exc:
            raise ReleaseStateError(f"cannot read {evidence_path}: {exc}") from exc
        expected_bytes = canonical_route_json(result).encode("utf-8")
        if evidence_bytes != expected_bytes:
            raise ReleaseStateError(
                f"{evidence_path}: route evidence differs from canonical resolver output"
            )

    if direct_required:
        validate_direct_upgrade_execution(root, version, automatic_upgrade_sources, matrix)


def validate_publication_authority(version: str, distribution: dict[str, Any]) -> None:
    """Keep owner-approved tag exceptions exact and non-transferable."""
    expected = {
        "v0.10.0": V010_AGENT_PUBLICATION_AUTHORITY,
        "v0.11.0": V011_AGENT_PUBLICATION_AUTHORITY,
    }.get(version)
    if expected is None:
        return
    publication = nested_mapping(
        distribution.get("publication"), "distribution.publication"
    )
    if publication != expected:
        actor = "Terra" if version == "v0.10.0" else "Sol"
        raise ReleaseStateError(
            f"{version} distribution.publication must equal the bounded "
            f"owner-authorized {actor} tag policy"
        )


def validate_candidate_record(
    root: Path,
    version: str,
    data: dict[str, Any],
    runner=subprocess.run,
) -> None:
    expected_package = expected_package_id(version)
    required_identity = {
        "schema_version": "1.0",
        "release_id": f"REL-{version}",
        "version": version,
        "status": "validated",
        "record_origin": "governed",
        "distribution_kind": "governed-package",
        "installable": True,
        "tag": None,
        "commit": None,
        "tagged_at": None,
        "recorded_at": None,
    }
    for field, expected in required_identity.items():
        if data.get(field) != expected:
            raise ReleaseStateError(
                f"release.{field} must be {expected!r} in candidate phase"
            )
    created = iso_timestamp(data.get("created_at"), "release.created_at")
    updated = iso_timestamp(data.get("updated_at"), "release.updated_at")
    if updated < created:
        raise ReleaseStateError("release.updated_at cannot precede release.created_at")

    compatibility = nested_mapping(data.get("compatibility"), "compatibility")
    sources = compatibility.get("automatic_upgrade_sources")
    if not isinstance(sources, list) or not sources or any(
        not isinstance(item, str) or not VERSION_RE.fullmatch(item)
        for item in sources
    ):
        raise ReleaseStateError(
            "compatibility.automatic_upgrade_sources must be non-empty stable versions"
        )
    artifacts = nested_mapping(data.get("artifacts"), "artifacts")
    validate_retained_origin_route_evidence(root, version, artifacts, sources)
    distribution = nested_mapping(data.get("distribution"), "distribution")
    if distribution.get("profile_id") != "dotnet-backend":
        raise ReleaseStateError("distribution.profile_id must be dotnet-backend")
    if distribution.get("package_id") != expected_package:
        raise ReleaseStateError(
            f"distribution.package_id must be {expected_package}"
        )
    validate_publication_authority(version, distribution)
    schema_versions = nested_mapping(
        distribution.get("schema_versions"), "distribution.schema_versions"
    )
    if (
        version_key(version) < (0, 6, 0)
        and len(sources) > 1
        and schema_versions.get("migration") != "2.0.0"
    ):
        raise ReleaseStateError(
            "multiple automatic sources require migration schema 2.0.0"
        )
    expected_package_schema = "2.4.0" if version_key(version) >= (0, 15, 0) else "2.3.0"
    if version_key(version) >= (0, 14, 0) and schema_versions != {
        "package": expected_package_schema,
        "files": "2.0.0",
        "migration": "3.0.0",
    }:
        raise ReleaseStateError(
            "v0.14+ release candidates require package/files/migration schemas "
            f"{expected_package_schema}/2.0.0/3.0.0"
        )
    expected_asset_names = expected_artifacts(version)
    if nested_mapping(distribution.get("artifacts"), "distribution.artifacts") != expected_asset_names:
        raise ReleaseStateError(
            "distribution.artifacts must exactly match the candidate package identity"
        )
    validation = nested_mapping(data.get("validation"), "validation")
    if validation.get("package_status") != "validated":
        raise ReleaseStateError("validation.package_status must be validated")
    for stale_field in (
        "failed_publication_run",
        "published_run",
        "public_release_url",
        "public_release_body_status",
        "public_release_body_corrected_at",
    ):
        if validation.get(stale_field) is not None:
            raise ReleaseStateError(
                f"validation.{stale_field} must be null or absent before publication"
            )
    if uses_online_issue_refs(version):
        validate_online_issue_refs(root, version, data, runner)
    else:
        validate_backlog_refs(root, version, data)


def assert_candidate(root: Path, version: str, data: dict, commit: str, branch: str, runner=subprocess.run) -> None:
    validate_candidate_record(root, version, data, runner)
    # The candidate commit cannot be stored in the record that it contains:
    # that would create a self-referential Git object.  It is observed from the
    # repository at gate time and must be pinned by the receiving checkpoint.
    if not SHA_RE.fullmatch(commit) or not branch:
        raise ReleaseStateError("candidate execution identity must be a full SHA and named branch")
    assert_clean_worktree(root, runner)


def peel_annotated_tag(root: Path, version: str, runner=subprocess.run) -> str:
    object_type = run_read_only(root, ["git", "cat-file", "-t", f"refs/tags/{version}"], runner).strip()
    if object_type != "tag":
        raise ReleaseStateError(f"{version}: release tag must exist and be annotated")
    commit = run_read_only(root, ["git", "rev-parse", f"refs/tags/{version}^{{commit}}"], runner).strip()
    if not SHA_RE.fullmatch(commit):
        raise ReleaseStateError(f"{version}: annotated tag did not peel to a full lowercase SHA")
    return commit


def tagged_release_record(
    root: Path,
    version: str,
    runner=subprocess.run,
) -> dict[str, Any]:
    raw = run_read_only(
        root,
        [
            "git",
            "show",
            f"refs/tags/{version}:.dev/releases/{version}/release.yaml",
        ],
        runner,
    )
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ReleaseStateError(
            f"{version}: tagged release record is invalid YAML"
        ) from exc
    if not isinstance(data, dict):
        raise ReleaseStateError(f"{version}: tagged release record must be a mapping")
    validated_skeleton = (
        data.get("release_id") != f"REL-{version}"
        or data.get("version") != version
        or data.get("status") != "validated"
        or data.get("tag") is not None
        or data.get("commit") is not None
    )
    v011_immutable_exception = (
        version == "v0.11.0"
        and data.get("release_id") == "REL-v0.11.0"
        and data.get("version") == "v0.11.0"
        and data.get("status") == "candidate"
        and data.get("tag") == "v0.11.0"
        and data.get("commit") == "pending-exact-candidate"
        and nested_mapping(data.get("distribution"), "distribution").get(
            "publication"
        )
        == V011_TAGGED_PUBLICATION_AUTHORITY
        and nested_mapping(data.get("validation"), "validation").get(
            "package_status"
        )
        == "deferred-with-owner"
    )
    if validated_skeleton and not v011_immutable_exception:
        raise ReleaseStateError(
            f"{version}: tagged tree must contain the validated registry skeleton"
        )
    return data


def assert_tag(
    root: Path,
    version: str,
    data: dict,
    runner=subprocess.run,
) -> str:
    commit = peel_annotated_tag(root, version, runner)
    if version == "v0.11.0" and commit != V011_TAGGED_COMMIT:
        raise ReleaseStateError(
            "v0.11.0 bounded tag exception is pinned to its original immutable commit"
        )
    tagged_release_record(root, version, runner)
    if data.get("status") not in {"validated", "published"}:
        raise ReleaseStateError("tag phase requires validated or published release status")
    if data.get("status") == "validated":
        if data.get("tag") is not None or data.get("commit") is not None:
            raise ReleaseStateError(
                "validated release record must leave tag and commit null"
            )
    elif data.get("commit") != commit or data.get("tag") != version:
        raise ReleaseStateError(
            "published release identity must equal the annotated tag and peel"
        )
    return commit


def expected_assets(data: dict, version: str) -> list[str]:
    distribution = data.get("distribution")
    artifacts = distribution.get("artifacts") if isinstance(distribution, dict) else None
    if not isinstance(artifacts, dict):
        raise ReleaseStateError("release distribution.artifacts must be a mapping")
    expected = [artifacts.get(key) for key in ("zip", "zip_checksum", "tar_gz", "tar_gz_checksum")]
    if any(not isinstance(value, str) or not value for value in expected):
        raise ReleaseStateError("release distribution must declare all four package assets")
    if len(set(expected)) != 4:
        raise ReleaseStateError("release package asset names must be distinct")
    return expected


def hosted_release(root: Path, repository: str, version: str, runner=subprocess.run) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ReleaseStateError("repository must use owner/repository form")
    raw = run_read_only(root, ["gh", "api", "--method", "GET", f"repos/{repository}/releases/tags/{version}"], runner)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseStateError("hosted release API did not return JSON") from exc
    if not isinstance(value, dict):
        raise ReleaseStateError("hosted release API response must be an object")
    return value


def origin_repository(root: Path, runner=subprocess.run) -> str:
    origin = run_read_only(root, ["git", "config", "--get", "remote.origin.url"], runner).strip()
    match = re.fullmatch(r"(?:git@github\.com:|https://github\.com/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", origin)
    if not match:
        raise ReleaseStateError("cannot infer GitHub owner/repository from remote.origin.url")
    return match.group(1)


def tagged_text(
    root: Path,
    version: str,
    name: str,
    runner=subprocess.run,
) -> str:
    return run_read_only(
        root,
        ["git", "show", f"refs/tags/{version}:.dev/releases/{version}/{name}"],
        runner,
    )


def render_governed_body(
    root: Path,
    version: str,
    commit: str,
    runner=subprocess.run,
) -> str:
    path = root / RENDERER_PATH
    spec = importlib.util.spec_from_file_location("release_notes_renderer", path)
    if spec is None or spec.loader is None:
        raise ReleaseStateError("cannot load governed release-body renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        data = tagged_release_record(root, version, runner)
        notes_text = tagged_text(
            root,
            version,
            "release-notes.md",
            runner,
        ).strip()
        migration_text = tagged_text(
            root,
            version,
            "migration-guide.md",
            runner,
        ).strip()
        return module.render_body_text(
            data,
            notes_text,
            migration_text,
            commit,
        )
    except (OSError, ReleaseStateError, module.ReleaseNotesError) as exc:
        raise ReleaseStateError(f"cannot render governed release body read-only: {exc}") from exc


def render_published_body(
    root: Path,
    version: str,
    commit: str,
) -> str:
    path = root / RENDERER_PATH
    spec = importlib.util.spec_from_file_location("release_notes_renderer", path)
    if spec is None or spec.loader is None:
        raise ReleaseStateError("cannot load published release-body renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        data, notes, migration = module.validate_release(
            root, version, commit, "published"
        )
        return module.render_body(data, notes, migration, commit)
    except (OSError, module.ReleaseNotesError) as exc:
        raise ReleaseStateError(
            f"cannot render published release body read-only: {exc}"
        ) from exc


def assert_hosted_release(root: Path, repository: str, version: str, commit: str, data: dict, expected_body: str, runner=subprocess.run) -> None:
    release = hosted_release(root, repository, version, runner)
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ReleaseStateError("hosted release must be published, stable, and non-draft")
    if release.get("tag_name") != version:
        raise ReleaseStateError("hosted release tag_name must equal the governed version")
    if release.get("name") != data.get("release_id"):
        raise ReleaseStateError("hosted release title must equal the governed release ID")
    if not isinstance(release.get("published_at"), str):
        raise ReleaseStateError("hosted release must expose a publication timestamp")
    if release.get("body", "").rstrip("\r\n") != expected_body.rstrip("\r\n"):
        raise ReleaseStateError("hosted release body differs from governed rendered body")
    actual_assets = sorted(item.get("name") for item in release.get("assets", []) if isinstance(item, dict))
    if actual_assets != sorted(expected_assets(data, version)):
        raise ReleaseStateError("hosted release asset set differs from governed package assets")
    if asset_identity_required(version):
        try:
            verify_provider(load_admission(root, version, commit), release, repository)
        except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
            raise ReleaseStateError(f"hosted asset identity blocked: {exc}") from exc


def assert_hosted_workflow(
    root: Path,
    repository: str,
    version: str,
    run_id: str,
    commit: str,
    runner=subprocess.run,
    *,
    allow_in_progress: bool = False,
) -> None:
    if not run_id.isdigit():
        raise ReleaseStateError("workflow run ID must be decimal digits")
    raw = run_read_only(root, ["gh", "api", "--method", "GET", f"repos/{repository}/actions/runs/{run_id}"], runner)
    try:
        run = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseStateError("hosted workflow API did not return JSON") from exc
    exact_identity = (
        isinstance(run, dict)
        and run.get("head_sha") == commit
        and run.get("event") == "push"
        and run.get("path") == PUBLISH_WORKFLOW_PATH
    )
    succeeded = exact_identity and run.get("conclusion") == "success"
    current_run = (
        exact_identity
        and allow_in_progress
        and run.get("status") == "in_progress"
        and run.get("conclusion") is None
    )
    v011_immutable_exception = (
        exact_identity
        and version == "v0.11.0"
        and commit == V011_TAGGED_COMMIT
        and run_id == V011_FAILED_PUBLICATION_RUN
        and run.get("conclusion") == "failure"
    )
    if not succeeded and not current_run and not v011_immutable_exception:
        raise ReleaseStateError("hosted workflow must have succeeded for the annotated tag commit")


def require_current_workflow_context(
    phase: str,
    hosted: bool,
    workflow_run_id: str | None,
    allow_current_workflow_run: bool,
) -> None:
    if not allow_current_workflow_run:
        return
    if phase != "finalization" or not hosted or workflow_run_id is None:
        raise ReleaseStateError(
            "--allow-current-workflow-run requires hosted finalization and --workflow-run-id"
        )
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise ReleaseStateError("--allow-current-workflow-run is restricted to GitHub Actions")
    if os.environ.get("GITHUB_RUN_ID") != workflow_run_id:
        raise ReleaseStateError(
            "--allow-current-workflow-run must identify the executing GITHUB_RUN_ID"
        )


def discover_workflow_run(root: Path, repository: str, commit: str, runner=subprocess.run) -> str:
    endpoint = f"repos/{repository}/actions/workflows/publish-release.yml/runs?event=push&head_sha={commit}"
    raw = run_read_only(root, ["gh", "api", "--method", "GET", endpoint], runner)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseStateError("workflow-run discovery API did not return JSON") from exc
    runs = value.get("workflow_runs") if isinstance(value, dict) else None
    if not isinstance(runs, list):
        raise ReleaseStateError("workflow-run discovery response lacks workflow_runs")
    successful = [
        run
        for run in runs
        if isinstance(run, dict)
        and run.get("conclusion") == "success"
        and run.get("head_sha") == commit
        and run.get("event") == "push"
        and run.get("path") == PUBLISH_WORKFLOW_PATH
        and isinstance(run.get("id"), int)
    ]
    if len(successful) != 1:
        raise ReleaseStateError("expected exactly one successful publish-release workflow run for the annotated tag commit")
    return str(successful[0]["id"])


def validate_published_record(
    version: str,
    data: dict[str, Any],
    tagged_commit: str,
) -> None:
    if data.get("status") != "published":
        raise ReleaseStateError("finalization phase requires release status published")
    if data.get("commit") != tagged_commit or data.get("tag") != version:
        raise ReleaseStateError(
            "published record must equal the immutable annotated tag and peel"
        )
    tagged_at = iso_timestamp(data.get("tagged_at"), "release.tagged_at")
    recorded_at = iso_timestamp(data.get("recorded_at"), "release.recorded_at")
    created_at = iso_timestamp(data.get("created_at"), "release.created_at")
    updated_at = iso_timestamp(data.get("updated_at"), "release.updated_at")
    if not created_at <= tagged_at <= recorded_at <= updated_at:
        raise ReleaseStateError(
            "published timestamps must order created_at <= tagged_at <= "
            "recorded_at <= updated_at"
        )
    validation = nested_mapping(data.get("validation"), "validation")
    published_run = validation.get("published_run")
    if not isinstance(published_run, str) or not published_run.isdigit():
        raise ReleaseStateError(
            "validation.published_run must record the successful workflow run"
        )
    if version == "v0.11.0" and (
        published_run != V011_FAILED_PUBLICATION_RUN
        or validation.get("published_run_outcome") != "failed"
        or validation.get("published_run_failure") != V011_PUBLICATION_FAILURE
    ):
        raise ReleaseStateError(
            "v0.11.0 must truthfully record its bounded failed publication run"
        )
    expected_url_suffix = f"/releases/tag/{version}"
    public_url = validation.get("public_release_url")
    if not isinstance(public_url, str) or not public_url.endswith(expected_url_suffix):
        raise ReleaseStateError(
            "validation.public_release_url must identify the governed release tag"
        )


def validate(
    root: Path,
    phase: str,
    version: str,
    commit: str | None = None,
    branch: str | None = None,
    repository: str | None = None,
    rendered_body: Path | None = None,
    workflow_run_id: str | None = None,
    hosted: bool = False,
    allow_current_workflow_run: bool = False,
    runner: Callable = subprocess.run,
) -> dict[str, str]:
    if phase not in PHASES:
        raise ReleaseStateError(f"phase must be one of: {', '.join(PHASES)}")
    require_current_workflow_context(
        phase,
        hosted,
        workflow_run_id,
        allow_current_workflow_run,
    )
    require_phase_contract(root, phase, version)
    _, data, notes, migration = release_record(root, version)
    assert_authored_sources(version, notes, migration)
    if phase == "candidate":
        observed_commit = git_head(root, runner)
        observed_branch = git_branch(root, runner)
        if commit is not None and commit != observed_commit:
            raise ReleaseStateError("--commit must equal current repository HEAD")
        if observed_branch and branch is not None and branch != observed_branch:
            raise ReleaseStateError("--branch must equal current repository branch")
        if not observed_branch:
            if not isinstance(branch, str) or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._/-]*",
                branch,
            ):
                raise ReleaseStateError(
                    "detached candidate validation requires a safe explicit --branch"
                )
            observed_branch = branch
        exact_commit = observed_commit
        exact_branch = observed_branch
        if not SHA_RE.fullmatch(exact_commit):
            raise ReleaseStateError("candidate commit must be a full lowercase SHA")
        assert_candidate(root, version, data, exact_commit, exact_branch, runner)
        if asset_identity_required(version):
            try:
                load_admission(root, version, exact_commit)
            except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
                raise ReleaseStateError(f"candidate asset admission blocked: {exc}") from exc
        return {"commit": exact_commit, "branch": exact_branch}
    tagged_commit = assert_tag(root, version, data, runner)
    if asset_identity_required(version):
        try:
            load_admission(root, version, tagged_commit)
        except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
            raise ReleaseStateError(f"tagged asset admission blocked: {exc}") from exc
    if phase in {"publication", "finalization"}:
        source_is_terminal_candidate = data.get("status") == "validated"
        if source_is_terminal_candidate:
            validate_candidate_record(root, version, data, runner)
        elif phase == "finalization":
            # Historical published source records remain readable. New releases
            # keep their source record terminal at the validated pre-tag state.
            validate_published_record(version, data, tagged_commit)
        else:
            raise ReleaseStateError(
                "publication phase requires the tagged validated registry skeleton"
            )
        if hosted:
            effective_repository = repository or origin_repository(root, runner)
            if phase == "finalization" and not source_is_terminal_candidate:
                expected_body = (
                    # The bounded manual v0.11.0 fast path published the immutable
                    # authored notes directly, before renderer provenance was added.
                    tagged_text(root, version, "release-notes.md", runner).strip()
                    if version == "v0.11.0" and tagged_commit == V011_TAGGED_COMMIT
                    else render_published_body(root, version, tagged_commit)
                )
                if rendered_body is not None:
                    supplied_body = rendered_body.read_text(encoding="utf-8")
                    if supplied_body.rstrip("\r\n") != expected_body.rstrip("\r\n"):
                        raise ReleaseStateError(
                            "finalization rendered body differs from the published-phase renderer"
                        )
            else:
                expected_body = (
                    rendered_body.read_text(encoding="utf-8")
                    if rendered_body is not None
                    else render_governed_body(root, version, tagged_commit, runner)
                )
            assert_hosted_release(root, effective_repository, version, tagged_commit, data, expected_body, runner)
            recorded_run = (
                nested_mapping(data.get("validation"), "validation").get(
                    "published_run"
                )
                if phase == "finalization" and not source_is_terminal_candidate
                else None
            )
            if workflow_run_id is not None and recorded_run is not None and workflow_run_id != recorded_run:
                raise ReleaseStateError(
                    "--workflow-run-id must equal validation.published_run"
                )
            effective_run = (
                workflow_run_id
                or recorded_run
                or discover_workflow_run(
                    root,
                    effective_repository,
                    tagged_commit,
                    runner,
                )
            )
            assert_hosted_workflow(
                root,
                effective_repository,
                version,
                effective_run,
                tagged_commit,
                runner,
                allow_in_progress=allow_current_workflow_run,
            )
        elif repository or rendered_body or workflow_run_id:
            raise ReleaseStateError("--repository, --rendered-body, and --workflow-run-id require --hosted")
    return {"commit": tagged_commit}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--phase", required=True, choices=PHASES)
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit")
    parser.add_argument("--branch")
    parser.add_argument("--repository")
    parser.add_argument("--rendered-body", type=Path)
    parser.add_argument("--workflow-run-id")
    parser.add_argument("--hosted", action="store_true", help="perform explicit read-only GitHub API checks")
    parser.add_argument(
        "--allow-current-workflow-run",
        action="store_true",
        help="accept only this executing GitHub Actions run as in-progress during hosted finalization",
    )
    args = parser.parse_args()
    try:
        result = validate(
            args.root.resolve(),
            args.phase,
            args.version,
            args.commit,
            args.branch,
            args.repository,
            args.rendered_body,
            args.workflow_run_id,
            args.hosted,
            args.allow_current_workflow_run,
        )
    except (OSError, ReleaseStateError) as exc:
        print(f"AI context release-state validation failed: {exc}", file=sys.stderr)
        return 1
    identity = f" at {result['commit']}" if result else ""
    branch = f" on {result['branch']}" if result and result.get("branch") else ""
    print(f"AI context release-state validation passed for {args.version} {args.phase} phase{identity}{branch}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
