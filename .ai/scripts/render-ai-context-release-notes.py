#!/usr/bin/env python3
"""Validate a governed release candidate and render its GitHub Release body."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_CANDIDATE_STATUSES = {"planned", "validated"}
BACKLOG_REF_RE = re.compile(r"^\.dev/backlog/items/([A-Z][A-Z0-9-]+)\.yaml$")


class ReleaseNotesError(ValueError):
    """Raised when release metadata cannot safely produce a release body."""


def load_mapping(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ReleaseNotesError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseNotesError(f"{path} must contain a YAML mapping")
    return value


def normalize_version(value: str) -> str:
    version = value.strip()
    if not VERSION_RE.fullmatch(version):
        raise ReleaseNotesError("version must use stable vMAJOR.MINOR.PATCH form")
    return version


def version_tuple(version: str) -> tuple[int, int, int]:
    normalized = normalize_version(version)
    return tuple(int(part) for part in normalized.removeprefix("v").split("."))


def included_work_ids(data: dict) -> list[str]:
    """Read the prospective generated Included Work contract."""
    version = data.get("version")
    if not isinstance(version, str) or version_tuple(version) < (0, 7, 0):
        return []
    planning = data.get("planning")
    if not isinstance(planning, dict):
        raise ReleaseNotesError("planning must be a mapping from v0.7.0 onward")
    refs = planning.get("backlog_refs")
    if not isinstance(refs, list) or not refs:
        raise ReleaseNotesError(
            "planning.backlog_refs must be a non-empty list from v0.7.0 onward"
        )
    if len(refs) != len(set(refs)):
        raise ReleaseNotesError("planning.backlog_refs must not contain duplicates")
    ids: list[str] = []
    for index, value in enumerate(refs):
        match = BACKLOG_REF_RE.fullmatch(value) if isinstance(value, str) else None
        if match is None:
            raise ReleaseNotesError(
                f"planning.backlog_refs[{index}] must be a backlog item path"
            )
        ids.append(match.group(1))
    if len(ids) != len(set(ids)):
        raise ReleaseNotesError("Included Work IDs must not contain duplicates")
    return ids


def discover_candidate(root: Path) -> str:
    candidates: list[str] = []
    releases = root / ".dev" / "releases"
    for path in sorted(releases.glob("v*/release.yaml")):
        data = load_mapping(path)
        version = data.get("version")
        if (
            isinstance(version, str)
            and VERSION_RE.fullmatch(version)
            and data.get("record_origin") == "governed"
            and data.get("status") in ALLOWED_CANDIDATE_STATUSES
        ):
            candidates.append(version)
    if len(candidates) != 1:
        joined = ", ".join(candidates) if candidates else "none"
        raise ReleaseNotesError(
            "candidate discovery requires exactly one governed planned or "
            f"validated release; found {joined}"
        )
    return candidates[0]


def resolve_artifact(path: Path, release_dir: Path, label: str) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise ReleaseNotesError(f"artifacts.{label} must be a repository file name")
    candidate = (release_dir / path).resolve()
    resolved_dir = release_dir.resolve()
    if candidate.parent != resolved_dir or not candidate.is_file():
        raise ReleaseNotesError(
            f"artifacts.{label} must resolve to an existing file in {release_dir}"
        )
    return candidate


def validate_release(root: Path, version: str, commit: str, mode: str) -> tuple[dict, Path, Path]:
    if not SHA_RE.fullmatch(commit):
        raise ReleaseNotesError("commit must be a full lowercase 40-character Git SHA")
    release_dir = root / ".dev" / "releases" / version
    record_path = release_dir / "release.yaml"
    data = load_mapping(record_path)
    expected_id = f"REL-{version}"
    if data.get("version") != version or data.get("release_id") != expected_id:
        raise ReleaseNotesError(f"{record_path} identity does not match {expected_id}")
    if data.get("record_origin") != "governed":
        raise ReleaseNotesError("automatic publication accepts governed releases only")
    status = data.get("status")
    allowed = {"validated"} if mode == "publish" else ALLOWED_CANDIDATE_STATUSES
    if status not in allowed:
        raise ReleaseNotesError(
            f"release status {status!r} is not allowed in {mode} mode; expected {sorted(allowed)}"
        )
    if mode == "publish" and (data.get("tag") is not None or data.get("commit") is not None):
        raise ReleaseNotesError(
            "the validated tagged-tree record must leave tag and commit unset until publication"
        )
    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict) or not isinstance(
        compatibility.get("breaking_changes"), bool
    ):
        raise ReleaseNotesError("compatibility.breaking_changes must be boolean")
    automatic_sources = compatibility.get("automatic_upgrade_sources", [])
    if not isinstance(automatic_sources, list) or any(
        not isinstance(item, str) or not VERSION_RE.fullmatch(item)
        for item in automatic_sources
    ):
        raise ReleaseNotesError(
            "compatibility.automatic_upgrade_sources must contain stable versions"
        )
    migration_schema = (
        data.get("distribution", {})
        if isinstance(data.get("distribution"), dict)
        else {}
    )
    schema_versions = migration_schema.get("schema_versions", {})
    migration_schema_version = (
        schema_versions.get("migration") if isinstance(schema_versions, dict) else None
    )
    if len(automatic_sources) > 1 and migration_schema_version != "2.0.0":
        raise ReleaseNotesError(
            "multiple automatic upgrade sources require migration schema 2.0.0"
        )
    included_work_ids(data)
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ReleaseNotesError("artifacts must be a mapping")
    notes = resolve_artifact(artifacts.get("release_notes"), release_dir, "release_notes")
    migration = resolve_artifact(
        artifacts.get("migration_guide"), release_dir, "migration_guide"
    )
    return data, notes, migration


def render_body_text(
    data: dict,
    notes_text: str,
    migration_text: str,
    commit: str,
) -> str:
    version = data["version"]
    release_id = data["release_id"]
    package_id = f"ai-context-dotnet-backend-{version}"
    body = [
            f"<!-- ai-context-release-automation: {release_id} -->",
            "",
            notes_text,
            "",
    ]
    work_ids = included_work_ids(data)
    if work_ids:
        body.extend(
            [
                "## Included Work",
                "",
                *[f"- `{work_id}`" for work_id in work_ids],
                "",
            ]
        )
    body.extend(
        [
            "## Release provenance",
            "",
            f"- Release ID: `{release_id}`",
            f"- Tag: `{version}`",
            f"- Commit: `{commit}`",
            "- Distribution profile: `dotnet-backend`",
            f"- Package: `{package_id}`",
            "- Archive integrity: verify each archive against its adjacent `.sha256` asset.",
            "",
            "## Migration guide",
            "",
            migration_text,
            "",
        ]
    )
    return "\n".join(body)


def render_body(data: dict, notes: Path, migration: Path, commit: str) -> str:
    return render_body_text(
        data,
        notes.read_text(encoding="utf-8").strip(),
        migration.read_text(encoding="utf-8").strip(),
        commit,
    )


def append_github_outputs(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise ReleaseNotesError(f"GitHub output {key} must be single-line")
            stream.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--version")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--mode", choices=("candidate", "publish"), default="candidate")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    try:
        root = args.root.resolve()
        version = normalize_version(args.version) if args.version else discover_candidate(root)
        commit = args.commit.strip()
        data, notes, migration = validate_release(root, version, commit, args.mode)
        body = render_body(data, notes, migration, commit)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8", newline="\n")
        outputs = {
            "version": version,
            "package_version": version.removeprefix("v"),
            "release_id": data["release_id"],
            "title": data["release_id"],
            "commit": commit,
            "package_id": f"ai-context-dotnet-backend-{version}",
            "migration_source": next(
                iter(data["compatibility"].get("automatic_upgrade_sources", [])),
                "",
            ),
            "migration_sources": " ".join(
                data["compatibility"].get("automatic_upgrade_sources", [])
            ),
        }
        if args.github_output:
            append_github_outputs(args.github_output, outputs)
    except (OSError, ReleaseNotesError) as exc:
        print(f"Release-note rendering failed: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered {data['release_id']} release body to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
