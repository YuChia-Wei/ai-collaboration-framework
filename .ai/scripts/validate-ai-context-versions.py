#!/usr/bin/env python3
"""Validate AI context release records and optional target provenance."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context-versions.py")

import argparse
import re
import subprocess
from datetime import datetime

import yaml

import ai_context_target_provenance as target_provenance


VERSION_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
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


def load_mapping(path: Path, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{path}: cannot parse YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be a mapping")
        return None
    return value


def expected_publication(version: str) -> dict:
    """Return the only allowed tag authority for one release version."""
    if version == "v0.10.0":
        return V010_AGENT_PUBLICATION_AUTHORITY
    if version == "v0.11.0":
        return V011_AGENT_PUBLICATION_AUTHORITY
    return {
        "tag_owner": "user",
        "trigger": "user-created-tag",
        "automation": "github-actions",
        "creates_or_moves_tag": False,
    }


def iso_with_offset(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def resolve_tag(root: Path, tag: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-list", "-n", "1", tag],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def validate_distribution(
    path: Path,
    version: str,
    compatibility: dict,
    distribution: object,
    errors: list[str],
) -> None:
    if not isinstance(distribution, dict):
        errors.append(f"{path}: governed release distribution must be a mapping")
        return

    bare_version = version.removeprefix("v")
    expected_package_id = f"ai-context-dotnet-backend-v{bare_version}"
    if distribution.get("profile_id") != "dotnet-backend":
        errors.append(f"{path}: distribution.profile_id must be dotnet-backend")
    if distribution.get("package_id") != expected_package_id:
        errors.append(
            f"{path}: distribution.package_id must be {expected_package_id}"
        )

    schemas = distribution.get("schema_versions")
    if not isinstance(schemas, dict):
        errors.append(f"{path}: distribution.schema_versions must be a mapping")
    else:
        for name in ("package", "files", "migration"):
            value = schemas.get(name)
            if not isinstance(value, str) or not SEMVER_RE.fullmatch(value):
                errors.append(
                    f"{path}: distribution.schema_versions.{name} must be MAJOR.MINOR.PATCH"
                )

    expected_artifacts = {
        "zip": f"{expected_package_id}.zip",
        "zip_checksum": f"{expected_package_id}.zip.sha256",
        "tar_gz": f"{expected_package_id}.tar.gz",
        "tar_gz_checksum": f"{expected_package_id}.tar.gz.sha256",
    }
    artifacts = distribution.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(f"{path}: distribution.artifacts must be a mapping")
    else:
        for name, expected in expected_artifacts.items():
            if artifacts.get(name) != expected:
                errors.append(
                    f"{path}: distribution.artifacts.{name} must be {expected}"
                )

    migration = distribution.get("migration")
    if not isinstance(migration, dict):
        errors.append(f"{path}: distribution.migration must be a mapping")
    else:
        if migration.get("default_mode") != "dry-run":
            errors.append(f"{path}: distribution.migration.default_mode must be dry-run")
        for field in (
            "apply_requires_clean_worktree",
            "apply_requires_acknowledged_reconciliation",
        ):
            if migration.get(field) is not True:
                errors.append(f"{path}: distribution.migration.{field} must be true")

    publication = distribution.get("publication")
    if not isinstance(publication, dict):
        errors.append(f"{path}: distribution.publication must be a mapping")
    else:
        expected = expected_publication(version)
        if version in {"v0.10.0", "v0.11.0"} and publication != expected:
            actor = "Terra" if version == "v0.10.0" else "Sol"
            errors.append(
                f"{path}: distribution.publication must equal the bounded {version} owner-authorized {actor} policy"
            )
        for field, value in expected.items():
            if publication.get(field) != value:
                errors.append(
                    f"{path}: distribution.publication.{field} must be {value!r}"
                )

    reconciliation_sources = compatibility.get("reconciliation_sources")
    automatic_sources = compatibility.get("automatic_upgrade_sources")
    minimum_source = compatibility.get("minimum_source_version")
    if not isinstance(reconciliation_sources, list) or not reconciliation_sources:
        errors.append(
            f"{path}: compatibility.reconciliation_sources must be a non-empty list"
        )
    else:
        invalid = [
            item
            for item in reconciliation_sources
            if not isinstance(item, str) or not VERSION_RE.fullmatch(item)
        ]
        if invalid:
            errors.append(
                f"{path}: compatibility.reconciliation_sources contains invalid versions"
            )
        if minimum_source not in reconciliation_sources:
            errors.append(
                f"{path}: compatibility.minimum_source_version must be a reconciliation source"
            )
    if not isinstance(automatic_sources, list):
        errors.append(
            f"{path}: compatibility.automatic_upgrade_sources must be a list"
        )
    else:
        invalid_automatic = [
            item
            for item in automatic_sources
            if not isinstance(item, str) or not VERSION_RE.fullmatch(item)
        ]
        if invalid_automatic:
            errors.append(
                f"{path}: compatibility.automatic_upgrade_sources contains invalid versions"
            )
        if isinstance(reconciliation_sources, list) and any(
            item not in reconciliation_sources for item in automatic_sources
        ):
            errors.append(
                f"{path}: compatibility.automatic_upgrade_sources must be reconciliation sources"
            )


def validate_release(path: Path, root: Path, errors: list[str], verify_git: bool) -> None:
    data = load_mapping(path, errors)
    if data is None:
        return
    version = data.get("version")
    status = data.get("status")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        errors.append(f"{path}: version must be vMAJOR.MINOR.PATCH")
        return
    if path.parent.name != version:
        errors.append(f"{path}: directory must equal version {version}")
    if data.get("release_id") != f"REL-{version}":
        errors.append(f"{path}: release_id must be REL-{version}")
    if status not in {"planned", "validated", "published", "superseded"}:
        errors.append(f"{path}: unsupported status {status!r}")
    for artifact in ("release-notes.md", "migration-guide.md"):
        if not (path.parent / artifact).is_file():
            errors.append(f"{path}: missing {artifact}")
    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict) or not isinstance(compatibility.get("breaking_changes"), bool):
        errors.append(f"{path}: compatibility.breaking_changes must be boolean")
    distribution_kind = data.get("distribution_kind")
    installable = data.get("installable")
    if distribution_kind not in {"source-snapshot-only", "governed-package"}:
        errors.append(f"{path}: distribution_kind must be source-snapshot-only or governed-package")
    if not isinstance(installable, bool):
        errors.append(f"{path}: installable must be boolean")
    if distribution_kind == "source-snapshot-only":
        if installable is not False:
            errors.append(f"{path}: source-snapshot-only releases must not be installable")
        if "distribution" in data:
            errors.append(f"{path}: source-snapshot-only releases must not declare governed distribution metadata")
    if distribution_kind == "governed-package":
        if installable is not True:
            errors.append(f"{path}: governed-package releases must be installable")
        if isinstance(compatibility, dict):
            validate_distribution(path, version, compatibility, data.get("distribution"), errors)
    if data.get("record_origin") == "retrospective" and distribution_kind != "source-snapshot-only":
        errors.append(f"{path}: retrospective releases must be source-snapshot-only")
    if data.get("record_origin") == "governed" and distribution_kind != "governed-package":
        errors.append(f"{path}: governed releases must use governed-package distribution_kind")
    if status in {"planned", "validated"}:
        if data.get("tag") is not None or data.get("commit") is not None:
            errors.append(f"{path}: {status} release tag and commit must remain null")
    if status == "published":
        tag, commit = data.get("tag"), data.get("commit")
        if tag != version:
            errors.append(f"{path}: published tag must equal version")
        if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
            errors.append(f"{path}: published commit must be a full lowercase Git SHA")
        elif verify_git:
            resolved = resolve_tag(root, tag)
            if resolved != commit:
                errors.append(f"{path}: tag {tag} resolves to {resolved!r}, expected {commit}")


def validate_manifest(path: Path, errors: list[str]) -> None:
    data = load_mapping(path, errors)
    if data is None:
        return
    if data.get("schema_version") == "2.0":
        target_provenance.validate_manifest(path, errors)
        return
    source = data.get("source")
    installation = data.get("installation")
    migration = data.get("last_migration")
    if not isinstance(source, dict):
        errors.append(f"{path}: source must be a mapping")
        return
    version = source.get("version")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        errors.append(f"{path}: source.version must be vMAJOR.MINOR.PATCH")
    else:
        if source.get("release_id") != f"REL-{version}":
            errors.append(f"{path}: source.release_id must be REL-{version}")
        if source.get("tag") != version:
            errors.append(f"{path}: source.tag must equal source.version")
    if not isinstance(source.get("repository"), str) or not source["repository"].strip():
        errors.append(f"{path}: source.repository is required")
    if not isinstance(source.get("commit"), str) or not SHA_RE.fullmatch(source["commit"]):
        errors.append(f"{path}: source.commit must be a full lowercase Git SHA")
    if not isinstance(installation, dict) or not iso_with_offset(installation.get("imported_at")):
        errors.append(f"{path}: installation.imported_at must use ISO 8601 with an offset")
    if not isinstance(migration, dict) or migration.get("status") != "completed" or migration.get("to_version") != version:
        errors.append(f"{path}: completed last_migration.to_version must equal source.version")
    schema_version = data.get("schema_version")
    if schema_version == "1.0":
        overrides = data.get("local_overrides")
        if not isinstance(overrides, list):
            errors.append(f"{path}: local_overrides must be a list")
            return
        ids: set[str] = set()
        for index, item in enumerate(overrides):
            if not isinstance(item, dict):
                errors.append(f"{path}: local_overrides[{index}] must be a mapping")
                continue
            override_id = item.get("id")
            if not isinstance(override_id, str) or not override_id or override_id in ids:
                errors.append(f"{path}: local_overrides[{index}].id must be unique and non-empty")
            else:
                ids.add(override_id)
            if not isinstance(item.get("paths"), list) or not item["paths"]:
                errors.append(f"{path}: local_overrides[{index}].paths must be non-empty")
            for field in ("reason", "owner", "disposition"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    errors.append(f"{path}: local_overrides[{index}].{field} is required")
        return
    if schema_version != "2.0":
        errors.append(f"{path}: schema_version must be 1.0 or 2.0")
        return
    selection = data.get("selection")
    if not isinstance(selection, dict):
        errors.append(f"{path}: selection must be a mapping")
    else:
        if selection.get("release_model") != "single-versioned-componentized-release":
            errors.append(f"{path}: selection.release_model is invalid")
        components = selection.get("mandatory_components")
        required_components = {"software-development-core", "ai-context-lifecycle-core"}
        if not isinstance(components, list) or set(components) != required_components:
            errors.append(f"{path}: selection.mandatory_components must contain both mandatory cores")
        profiles = selection.get("profiles")
        if (
            not isinstance(profiles, list)
            or not profiles
            or len(profiles) != len(set(profiles))
            or not all(isinstance(item, str) and item for item in profiles)
        ):
            errors.append(f"{path}: selection.profiles must be a non-empty string list")
        providers = selection.get("providers")
        if not isinstance(providers, dict):
            errors.append(f"{path}: selection.providers must be a mapping")
        else:
            backlog = providers.get("repo-backlog")
            if not isinstance(backlog, dict):
                errors.append(f"{path}: selection.providers.repo-backlog must be a mapping")
            else:
                if not isinstance(backlog.get("enabled"), bool):
                    errors.append(f"{path}: selection.providers.repo-backlog.enabled must be boolean")
                if backlog.get("preservation") not in {
                    "preserve-existing-if-recorded",
                    "explicit-reconciliation-required",
                }:
                    errors.append(f"{path}: selection.providers.repo-backlog.preservation is invalid")
    customizations = data.get("customizations")
    if not isinstance(customizations, dict):
        errors.append(f"{path}: customizations must be a mapping")
    else:
        if customizations.get("ledger") != ".dev/ai-context/customizations.yaml":
            errors.append(f"{path}: customizations.ledger must be .dev/ai-context/customizations.yaml")
        if customizations.get("schema_version") != "1.0":
            errors.append(f"{path}: customizations.schema_version must be 1.0")


def validate_customizations(path: Path, errors: list[str]) -> None:
    target_provenance.validate_customizations(path, errors, require_finalized=True)


def validate(root: Path, manifest: Path | None = None, verify_git: bool = True) -> list[str]:
    errors: list[str] = []
    release_files = sorted((root / ".dev" / "releases").glob("v*/release.yaml"))
    for path in release_files:
        validate_release(path, root, errors, verify_git)
    effective_manifest = manifest
    provenance = root / ".dev" / "ai-context" / "provenance.yaml"
    legacy_manifest = root / ".dev" / "AI-CONTEXT-SOURCE.yaml"
    if provenance.is_file() and legacy_manifest.is_file():
        errors.append(f"{root}: provenance.yaml and AI-CONTEXT-SOURCE.yaml cannot both be active")
    if effective_manifest is None and provenance.is_file():
        effective_manifest = provenance
    if effective_manifest is None and legacy_manifest.is_file():
        effective_manifest = legacy_manifest
    if effective_manifest is not None:
        validate_manifest(effective_manifest, errors)
        if effective_manifest.resolve() == provenance.resolve():
            ledger = root / ".dev" / "ai-context" / "customizations.yaml"
            if not ledger.is_file():
                errors.append(f"{root}: provenance schema 2 requires .dev/ai-context/customizations.yaml")
            else:
                validate_customizations(ledger, errors)
    if not release_files and effective_manifest is None:
        errors.append(f"{root}: expected source release records or target provenance")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--no-git", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.manifest, not args.no_git)
    if errors:
        print("AI context version validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    count = len(list((args.root / ".dev" / "releases").glob("v*/release.yaml")))
    manifest = args.manifest or (args.root / ".dev" / "ai-context" / "provenance.yaml")
    if not manifest.is_file():
        manifest = args.root / ".dev" / "AI-CONTEXT-SOURCE.yaml"
    suffix = f" and target manifest {manifest}" if manifest.is_file() else ""
    print(f"AI context version validation passed for {count} release record(s){suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
