#!/usr/bin/env python3
"""Validate source work-management authority and frozen backlog compatibility."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-source-work-management.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / ".dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^v([0-9]+)\.([0-9]+)\.([0-9]+)$")


def load_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"{path}: cannot read YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def run_git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout


def head_blob_bytes(root: Path, path: str) -> bytes:
    return run_git_bytes(root, "cat-file", "blob", f"HEAD:{path}")


def git_diff_is_clean(root: Path, *args: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", *args],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode not in (0, 1):
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git diff --quiet {' '.join(args)} failed")
    return result.returncode == 0


def aggregate_digest(
    paths: Iterable[str], read_bytes: Callable[[str], bytes]
) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(read_bytes(path))
        digest.update(b"\0")
    return digest.hexdigest()


def version_tuple(value: str) -> tuple[int, int, int] | None:
    match = VERSION.fullmatch(value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def offset_datetime(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be an ISO 8601 timestamp with an explicit offset")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            f"{label} must be an ISO 8601 timestamp with an explicit offset"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must be an ISO 8601 timestamp with an explicit offset")
    return parsed


def prospective_locator_errors(
    locator: dict[str, Any],
    *,
    effective_at: object,
    exception: str,
    forbidden_keys: set[str],
    forbidden_paths: tuple[str, ...],
) -> tuple[bool, list[str]]:
    if locator.get("workflow_id") == exception:
        return False, []
    try:
        effective_time = offset_datetime(effective_at, "prospective_workflow.effective_at")
        created_time = offset_datetime(locator.get("created_at"), "workflow.created_at")
    except ValueError as exc:
        return False, [str(exc)]
    if created_time < effective_time:
        return False, []
    return True, forbidden_structured_references(
        locator,
        forbidden_keys=forbidden_keys,
        forbidden_paths=forbidden_paths,
    )


def forbidden_structured_references(
    value: object,
    *,
    forbidden_keys: set[str],
    forbidden_paths: tuple[str, ...],
    location: str = "$",
) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key in forbidden_keys:
                errors.append(f"{child_location}: retired structured key is forbidden")
            errors.extend(
                forbidden_structured_references(
                    child,
                    forbidden_keys=forbidden_keys,
                    forbidden_paths=forbidden_paths,
                    location=child_location,
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(
                forbidden_structured_references(
                    child,
                    forbidden_keys=forbidden_keys,
                    forbidden_paths=forbidden_paths,
                    location=f"{location}[{index}]",
                )
            )
    elif isinstance(value, str) and any(
        value == path or value.startswith(path) for path in forbidden_paths
    ):
        errors.append(f"{location}: retired current-planning path is forbidden")
    return errors


def release_scope_errors(
    releases: dict[str, dict[str, Any]],
    *,
    legacy_versions: set[str],
    frozen_paths: set[str],
    online_from: tuple[int, int, int],
) -> list[str]:
    errors: list[str] = []
    for version in sorted(legacy_versions):
        release = releases.get(version)
        if not isinstance(release, dict):
            errors.append(f"{version}: legacy release record is missing")
            continue
        planning = release.get("planning")
        refs = planning.get("backlog_refs") if isinstance(planning, dict) else None
        if not isinstance(refs, list) or not refs:
            errors.append(f"{version}: planning.backlog_refs must remain non-empty")
            continue
        if len(refs) != len(set(refs)):
            errors.append(f"{version}: planning.backlog_refs must remain unique")
        for ref in refs:
            if not isinstance(ref, str) or ref not in frozen_paths:
                errors.append(f"{version}: unresolved frozen backlog ref {ref!r}")

    for version, release in sorted(releases.items()):
        parsed = version_tuple(version)
        if parsed is None or parsed < online_from:
            continue
        planning = release.get("planning")
        if not isinstance(planning, dict):
            errors.append(f"{version}: planning must be a mapping")
            continue
        if "backlog_refs" in planning:
            errors.append(f"{version}: planning.backlog_refs is forbidden from v0.10.0 onward")
        issue_refs = planning.get("github_issue_refs")
        if not isinstance(issue_refs, list) or not issue_refs:
            errors.append(f"{version}: planning.github_issue_refs must be non-empty")
    return errors


def validate_contract(data: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if data.get("contract_id") != "source-work-management-authority":
        errors.append("contract_id must be source-work-management-authority")
    if data.get("rule_id") != "SOURCE-WORK-MANAGEMENT-001":
        errors.append("rule_id must be SOURCE-WORK-MANAGEMENT-001")
    if data.get("issue") != 245 or data.get("status") != "active":
        errors.append("contract must bind active Issue 245")

    authority = data.get("authority")
    expected_authority = {
        "work_items": "live-github-issues",
        "current_views": "live-github-project-3",
        "execution_evidence": ".dev/workflows/",
        "integrated_truth": "main",
        "provider_state_alone_authorizes": False,
        "ordinary_validation_requires_github_credentials": False,
    }
    if authority != expected_authority:
        errors.append("authority must exactly separate live provider, workflow, and main truth")

    provider = data.get("current_provider")
    if not isinstance(provider, dict):
        errors.append("current_provider must be a mapping")
        return errors
    active_config = provider.get("config")
    retired_config = provider.get("retired_config")
    if active_config != ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml":
        errors.append("current_provider.config must use the canonical standards owner")
    if retired_config != ".dev/backlog/providers/github.yaml":
        errors.append("current_provider.retired_config must bind the retired path")
    if provider.get("current_state_mode") != "explicit-live-read-back-required":
        errors.append("current provider state must require explicit live read-back")
    if isinstance(active_config, str) and not (root / active_config).is_file():
        errors.append(f"active provider config is missing: {active_config}")
    if isinstance(retired_config, str) and (root / retired_config).exists():
        errors.append(f"retired provider config must remain absent: {retired_config}")

    compatibility = data.get("historical_compatibility")
    if not isinstance(compatibility, dict):
        errors.append("historical_compatibility must be a mapping")
        return errors
    backlog_root = compatibility.get("root")
    if backlog_root != ".dev/backlog":
        errors.append("historical_compatibility.root must be .dev/backlog")
        return errors
    tracked = [
        line
        for line in run_git(root, "ls-files", "--", backlog_root).splitlines()
        if line
    ]
    if len(tracked) != compatibility.get("tracked_file_count"):
        errors.append(
            "frozen backlog tracked-file count differs: "
            f"expected={compatibility.get('tracked_file_count')} actual={len(tracked)}"
        )
    expected_digest = compatibility.get("aggregate_sha256")
    if not isinstance(expected_digest, str) or not SHA256.fullmatch(expected_digest):
        errors.append("historical_compatibility.aggregate_sha256 must be a lowercase SHA-256")
    else:
        if not git_diff_is_clean(root, "--", backlog_root):
            errors.append("frozen backlog has unstaged worktree drift")
        if not git_diff_is_clean(root, "--cached", "--", backlog_root):
            errors.append("frozen backlog has staged index drift")
        actual_digest = aggregate_digest(
            tracked, lambda path: head_blob_bytes(root, path)
        )
        if actual_digest != expected_digest:
            errors.append(
                "frozen backlog HEAD path/blob-byte digest differs: "
                f"expected={expected_digest} actual={actual_digest}"
            )

    legacy_config = compatibility.get("legacy_provider_config")
    if not isinstance(legacy_config, str) or not (root / legacy_config).is_file():
        errors.append("historical legacy provider config is missing")
    else:
        try:
            legacy_data = load_mapping(root / legacy_config)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if legacy_data.get("status") != "historical-only":
                errors.append("legacy provider config must be historical-only")

    receipt = compatibility.get("historical_project_receipt")
    if not isinstance(receipt, str) or not (root / receipt).is_file():
        errors.append("historical Project receipt is missing")
    else:
        try:
            receipt_data = load_mapping(root / receipt)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            disposition = receipt_data.get("disposition")
            if (
                receipt_data.get("record_type") != "historical-provider-state-read-back"
                or not isinstance(disposition, dict)
                or disposition.get("status") != "historical-point-in-time"
            ):
                errors.append("Project receipt must be frozen historical point-in-time evidence")

    release_records: dict[str, dict[str, Any]] = {}
    for path in sorted((root / ".dev/releases").glob("v*/release.yaml")):
        try:
            release_records[path.parent.name] = load_mapping(path)
        except ValueError as exc:
            errors.append(str(exc))
    legacy_versions = compatibility.get("legacy_release_versions")
    online_from = compatibility.get("online_issue_release_scope_from")
    online_version = version_tuple(online_from) if isinstance(online_from, str) else None
    if (
        not isinstance(legacy_versions, list)
        or not all(isinstance(item, str) for item in legacy_versions)
        or online_version is None
    ):
        errors.append("release compatibility boundary is malformed")
    else:
        errors.extend(
            release_scope_errors(
                release_records,
                legacy_versions=set(legacy_versions),
                frozen_paths=set(tracked),
                online_from=online_version,
            )
        )

    prospective = data.get("prospective_workflow")
    if not isinstance(prospective, dict):
        errors.append("prospective_workflow must be a mapping")
        return errors
    effective_at = prospective.get("effective_at")
    exception = prospective.get("remediation_workflow_exception")
    forbidden_keys = prospective.get("forbidden_structured_keys")
    forbidden_paths = prospective.get("forbidden_current_planning_paths")
    if (
        not isinstance(effective_at, str)
        or not isinstance(exception, str)
        or not isinstance(forbidden_keys, list)
        or not all(isinstance(item, str) for item in forbidden_keys)
        or not isinstance(forbidden_paths, list)
        or not all(isinstance(item, str) for item in forbidden_paths)
    ):
        errors.append("prospective_workflow boundary is malformed")
        return errors
    for locator_path in sorted((root / ".dev/workflows").glob("*/workflow.yaml")):
        try:
            locator = load_mapping(locator_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        scan_tasks, locator_errors = prospective_locator_errors(
            locator,
            effective_at=effective_at,
            exception=exception,
            forbidden_keys=set(forbidden_keys),
            forbidden_paths=tuple(forbidden_paths),
        )
        errors.extend(
            f"{locator_path.relative_to(root)}: {error}" for error in locator_errors
        )
        if not scan_tasks:
            continue
        artifact_root = locator.get("artifact_root")
        if not isinstance(artifact_root, str):
            errors.append(f"{locator_path}: artifact_root must be a string")
            continue
        task_root = root / artifact_root / "tasks"
        for task_path in sorted(task_root.glob("*.json")) if task_root.is_dir() else []:
            try:
                task_data = json.loads(task_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"{task_path}: cannot read task JSON: {exc}")
                continue
            errors.extend(
                f"{task_path.relative_to(root)}: {error}"
                for error in forbidden_structured_references(
                    task_data,
                    forbidden_keys=set(forbidden_keys),
                    forbidden_paths=tuple(forbidden_paths),
                )
            )
    return errors


def main() -> int:
    parser = ArgumentParser(
        description="Validate source work-management authority and frozen compatibility."
    )
    parser.add_argument(
        "--contract",
        default=".dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml",
        help="Repository-relative authority contract path.",
    )
    args = parser.parse_args()
    contract = ROOT / args.contract
    try:
        data = load_mapping(contract)
        errors = validate_contract(data)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Source work-management validation failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Source work-management validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    compatibility = data["historical_compatibility"]
    print(
        "Source work-management validation passed: live GitHub authority, "
        f"{compatibility['tracked_file_count']} frozen backlog files, "
        "v0.5.0-v0.9.0 legacy refs, and v0.10.0+ online Issue scope."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
