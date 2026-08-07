#!/usr/bin/env python3
"""Fail-closed, read-only validation for a governed AI-context release phase.

This validator intentionally separates repository-local facts from hosted facts.
Hosted checks are opt-in and use only ``gh api`` GET endpoints; they never create
tags, releases, assets, or workflow runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context-release-state.py")

import argparse
import importlib.util
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import yaml


VERSION_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
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
PLACEHOLDER_RE = re.compile(r"\{\{.+?\}\}|<[^\n>]+>|\b(?:TODO|TBD|PLACEHOLDER)\b", re.I)
FORBIDDEN_AUTHORED_RE = re.compile(
    r"ai-context-release-automation:|^## Release provenance\s*$", re.I | re.M
)
RENDERER_PATH = ".ai/scripts/render-ai-context-release-notes.py"
PUBLISH_WORKFLOW_PATH = ".github/workflows/publish-release.yml"


class ReleaseStateError(ValueError):
    """Raised for invalid release-state inputs."""


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
                r"(?:releases/tags/v\d+\.\d+\.\d+|actions/runs/\d+|"
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


def validate_publication_authority(version: str, distribution: dict[str, Any]) -> None:
    """Keep the owner-approved v0.10.0 tag exception exact and non-transferable."""
    if version != "v0.10.0":
        return
    publication = nested_mapping(
        distribution.get("publication"), "distribution.publication"
    )
    if publication != V010_AGENT_PUBLICATION_AUTHORITY:
        raise ReleaseStateError(
            "v0.10.0 distribution.publication must equal the bounded owner-authorized Terra tag policy"
        )


def validate_candidate_record(
    root: Path,
    version: str,
    data: dict[str, Any],
) -> None:
    expected_package = f"ai-context-dotnet-backend-{version}"
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
    if artifacts != {
        "release_notes": "release-notes.md",
        "migration_guide": "migration-guide.md",
    }:
        raise ReleaseStateError("artifacts must name the two canonical authored files")
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
    if len(sources) > 1 and schema_versions.get("migration") != "2.0.0":
        raise ReleaseStateError(
            "multiple automatic sources require migration schema 2.0.0"
        )
    expected_asset_names = {
        "zip": f"{expected_package}.zip",
        "zip_checksum": f"{expected_package}.zip.sha256",
        "tar_gz": f"{expected_package}.tar.gz",
        "tar_gz_checksum": f"{expected_package}.tar.gz.sha256",
    }
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
    validate_backlog_refs(root, version, data)


def assert_candidate(root: Path, version: str, data: dict, commit: str, branch: str, runner=subprocess.run) -> None:
    validate_candidate_record(root, version, data)
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
    if (
        data.get("release_id") != f"REL-{version}"
        or data.get("version") != version
        or data.get("status") != "validated"
        or data.get("tag") is not None
        or data.get("commit") is not None
    ):
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


def assert_hosted_workflow(root: Path, repository: str, run_id: str, commit: str, runner=subprocess.run) -> None:
    if not run_id.isdigit():
        raise ReleaseStateError("workflow run ID must be decimal digits")
    raw = run_read_only(root, ["gh", "api", "--method", "GET", f"repos/{repository}/actions/runs/{run_id}"], runner)
    try:
        run = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseStateError("hosted workflow API did not return JSON") from exc
    if (
        not isinstance(run, dict)
        or run.get("conclusion") != "success"
        or run.get("head_sha") != commit
        or run.get("event") != "push"
        or run.get("path") != PUBLISH_WORKFLOW_PATH
    ):
        raise ReleaseStateError("hosted workflow must have succeeded for the annotated tag commit")


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
    runner: Callable = subprocess.run,
) -> dict[str, str]:
    if phase not in PHASES:
        raise ReleaseStateError(f"phase must be one of: {', '.join(PHASES)}")
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
        return {"commit": exact_commit, "branch": exact_branch}
    tagged_commit = assert_tag(root, version, data, runner)
    if phase in {"publication", "finalization"}:
        if phase == "publication":
            if data.get("status") != "validated":
                raise ReleaseStateError(
                    "publication phase requires the tagged validated registry "
                    "skeleton before local finalization"
                )
        else:
            validate_published_record(version, data, tagged_commit)
        if hosted:
            effective_repository = repository or origin_repository(root, runner)
            if phase == "finalization":
                expected_body = render_published_body(root, version, tagged_commit)
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
                if phase == "finalization"
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
            assert_hosted_workflow(root, effective_repository, effective_run, tagged_commit, runner)
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
    args = parser.parse_args()
    try:
        result = validate(args.root.resolve(), args.phase, args.version, args.commit, args.branch, args.repository, args.rendered_body, args.workflow_run_id, args.hosted)
    except (OSError, ReleaseStateError) as exc:
        print(f"AI context release-state validation failed: {exc}", file=sys.stderr)
        return 1
    identity = f" at {result['commit']}" if result else ""
    branch = f" on {result['branch']}" if result and result.get("branch") else ""
    print(f"AI context release-state validation passed for {args.version} {args.phase} phase{identity}{branch}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
