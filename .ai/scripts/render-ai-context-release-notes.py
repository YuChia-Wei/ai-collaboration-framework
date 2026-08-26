#!/usr/bin/env python3
"""Validate a governed release phase and render its GitHub Release body."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/render-ai-context-release-notes.py")

from ai_context_package_identity import expected_package_id
import yaml


VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RELEASE_RECORD_PATH_RE = re.compile(
    r"^\.dev/releases/(v\d+\.\d+\.\d+)/release\.yaml$"
)
ALLOWED_CANDIDATE_STATUSES = {"planned", "validated"}
CANDIDATE_NOT_APPLICABLE_EXIT_CODE = 3
BACKLOG_REF_RE = re.compile(r"^\.dev/backlog/items/([A-Z][A-Z0-9-]+)\.yaml$")
ONLINE_ISSUE_REF_RE = re.compile(r"^#([1-9]\d*)$")
PHASE_NEUTRAL_RELEASE_NOTES_FROM = (0, 13, 0)
PUBLICATION_SAFE_SECTION_ORDER = (
    "Highlights",
    "Practical Effect",
    "Compatibility",
    "Release Validation",
    "Known Limitations",
    "Support Status",
)
PUBLICATION_CONTENT_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
PUBLICATION_TRANSIENT_CLAIM_RULES = (
    (
        "release identity denial",
        re.compile(
            r"\b(?:it|this\s+(?:governed\s+)?source\s+candidate|this\s+release)\s+"
            r"is\s+not\s+(?:a\s+)?(?:tag|GitHub\s+Release|publication\s+record)\b|"
            r"\bno\s+(?:hosted\s+)?(?:admission|merge|tag|GitHub\s+Release|publication)"
            r".{0,160}\bis\s+claimed\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "pending release lifecycle",
        re.compile(
            r"\b(?:admission|merge|tag|GitHub\s+Release|publication)\b.{0,160}"
            r"\b(?:absent|pending|unperformed|not\s+published|requires?|still\s+needs?)\b|"
            r"\b(?:pending|unperformed|requires?|still\s+needs?)\b.{0,160}"
            r"\b(?:admission|merge|tag|GitHub\s+Release|publication)\b|"
            r"\bPublication\s+仍需\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "open pull request state",
        re.compile(
            r"\bPR\s+#\d+\b.{0,160}\b(?:draft|open|pending|unmerged)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "temporary execution identifier",
        re.compile(
            r"\b[0-9a-f]{40}\b|\b(?:run|job)\s+`?\d{5,}`?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "failed-attempt chronology",
        re.compile(
            r"\b(?:preceding|previous|earlier|later|then|retry|attempt)\b.{0,200}"
            r"\b(?:failed|failure)\b|"
            r"\b(?:failed|failure)\b.{0,200}"
            r"\b(?:preceding|previous|earlier|later|then|retry|attempt)\b",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
)
TRANSIENT_PUBLICATION_CLAIM_RE = re.compile(
    r"\bnot tagged or published\b|"
    r"\b(?:tag|publication|finalization).{0,240}\b(?:remain|remains)\s+unperformed\b|"
    r"\bpublication\s+(?:still\s+)?requires?\b|"
    r"\bpublication\s+(?:is\s+)?(?:still\s+)?pending\b|"
    r"\bPublication\s+仍需\b|"
    r"^Owner 推送.{0,240}後.{0,240}才會建立 GitHub Release|"
    r"^Not published\.",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
LEGACY_PUBLISHED_REQUIRED_BODY_SECTIONS = (
    "## Status",
    "## Release Validation",
    "## Publication Completion",
)


class ReleaseNotesError(ValueError):
    """Raised when release metadata cannot safely produce a release body."""


class CandidateNotApplicable(ReleaseNotesError):
    """Raised when a PR changes no eligible governed release candidate."""


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
    online_refs = planning.get("github_issue_refs")
    if online_refs is not None:
        if "backlog_refs" in planning:
            raise ReleaseNotesError(
                "planning must not mix github_issue_refs and backlog_refs"
            )
        if not isinstance(online_refs, list) or not online_refs:
            raise ReleaseNotesError(
                "planning.github_issue_refs must be a non-empty list"
            )
        if len(online_refs) != len(set(online_refs)):
            raise ReleaseNotesError("planning.github_issue_refs must not contain duplicates")
        ids: list[str] = []
        for index, value in enumerate(online_refs):
            match = ONLINE_ISSUE_REF_RE.fullmatch(value) if isinstance(value, str) else None
            if match is None:
                raise ReleaseNotesError(
                    f"planning.github_issue_refs[{index}] must use #<issue-number>"
                )
            ids.append(value)
        return ids

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


def normalize_git_sha(value: str, label: str) -> str:
    sha = value.strip()
    if not SHA_RE.fullmatch(sha):
        raise ReleaseNotesError(
            f"{label} must be a full lowercase 40-character Git SHA"
        )
    return sha


def changed_release_record_paths(
    root: Path, base_commit: str, head_commit: str
) -> list[Path]:
    base = normalize_git_sha(base_commit, "base commit")
    head = normalize_git_sha(head_commit, "head commit")
    try:
        completed = subprocess.run(
            [
                "git",
                "diff",
                "--name-status",
                "--no-renames",
                f"{base}...{head}",
                "--",
                ".dev/releases/*/release.yaml",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise ReleaseNotesError(
            f"cannot inspect changed release records: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = (
            completed.stderr.strip()
            or completed.stdout.strip()
            or "git diff failed"
        )
        raise ReleaseNotesError(f"cannot inspect changed release records: {detail}")

    paths: list[Path] = []
    for line in completed.stdout.splitlines():
        fields = line.split("\t", 1)
        if len(fields) != 2:
            raise ReleaseNotesError(
                f"unexpected changed release record entry: {line!r}"
            )
        status, relative_value = fields
        if status == "D":
            raise ReleaseNotesError(
                f"changed release record must not be deleted: {relative_value}"
            )
        if status not in {"A", "M", "T"}:
            raise ReleaseNotesError(
                f"unsupported changed release record status {status!r}: {relative_value}"
            )
        if RELEASE_RECORD_PATH_RE.fullmatch(relative_value) is None:
            raise ReleaseNotesError(
                f"changed release record path is not canonical: {relative_value}"
            )
        paths.append(root / Path(relative_value))
    return paths


def discover_candidate(root: Path, base_commit: str, head_commit: str) -> str:
    candidates: list[str] = []
    for path in changed_release_record_paths(root, base_commit, head_commit):
        data = load_mapping(path)
        relative = path.relative_to(root).as_posix()
        match = RELEASE_RECORD_PATH_RE.fullmatch(relative)
        if match is None:
            raise ReleaseNotesError(f"release record path is not canonical: {relative}")
        path_version = match.group(1)
        if (
            data.get("record_origin") == "governed"
            and data.get("status") in ALLOWED_CANDIDATE_STATUSES
        ):
            if data.get("version") != path_version:
                raise ReleaseNotesError(
                    f"{relative} version does not match its release directory"
                )
            candidates.append(path_version)
    candidates = sorted(set(candidates), key=version_tuple)
    if not candidates:
        raise CandidateNotApplicable(
            "no governed planned or validated release record changed between "
            f"{base_commit} and {head_commit}"
        )
    if len(candidates) > 1:
        raise ReleaseNotesError(
            "PR candidate selection requires exactly one changed governed planned or "
            f"validated release record; found {', '.join(candidates)}"
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


def assert_published_body_source(
    data: dict, notes: Path, version: str, commit: str
) -> None:
    if data.get("status") != "published":
        raise ReleaseNotesError("published mode requires release status published")
    if data.get("tag") != version or data.get("commit") != commit:
        raise ReleaseNotesError(
            "published mode requires the immutable annotated tag and peeled commit"
        )
    validation = data.get("validation")
    if not isinstance(validation, dict):
        raise ReleaseNotesError("published mode requires validation evidence")
    published_run = validation.get("published_run")
    if not isinstance(published_run, str) or not published_run.isdigit():
        raise ReleaseNotesError("published mode requires validation.published_run")
    public_url = validation.get("public_release_url")
    if not isinstance(public_url, str) or not public_url.endswith(
        f"/releases/tag/{version}"
    ):
        raise ReleaseNotesError(
            "published mode requires validation.public_release_url for the tag"
        )
    text = notes.read_text(encoding="utf-8").strip()
    if version_tuple(version) < PHASE_NEUTRAL_RELEASE_NOTES_FROM:
        missing = [
            section
            for section in LEGACY_PUBLISHED_REQUIRED_BODY_SECTIONS
            if section not in text
        ]
        if missing:
            raise ReleaseNotesError(
                "legacy published release notes must contain phase-owned sections: "
                + ", ".join(missing)
            )
        if "## Status\n\nPublished." not in text:
            raise ReleaseNotesError("legacy published release notes must state Published.")
    if TRANSIENT_PUBLICATION_CLAIM_RE.search(text):
        raise ReleaseNotesError(
            "published release notes must not retain candidate-only publication claims"
        )


def assert_phase_neutral_publication_claims(
    data: dict, artifact: Path, artifact_label: str
) -> None:
    version = data.get("version")
    if (
        not isinstance(version, str)
        or version_tuple(version) < PHASE_NEUTRAL_RELEASE_NOTES_FROM
    ):
        return
    text = artifact.read_text(encoding="utf-8").strip()
    publication_blocks = []
    for block in re.split(r"\n\s*\n", text):
        content_lines = []
        for line in block.splitlines():
            heading = PUBLICATION_CONTENT_HEADING_RE.fullmatch(line.strip())
            content_lines.append(heading.group(2) if heading is not None else line)
        normalized = re.sub(r"\s+", " ", "\n".join(content_lines)).strip()
        if normalized:
            publication_blocks.append(normalized)
    for rule_name, rule in PUBLICATION_TRANSIENT_CLAIM_RULES:
        if any(rule.search(block) for block in publication_blocks):
            raise ReleaseNotesError(
                f"v0.13.0+ {artifact_label} violate the publication-content contract: "
                f"{rule_name}"
            )
    if TRANSIENT_PUBLICATION_CLAIM_RE.search(text):
        raise ReleaseNotesError(
            f"v0.13.0+ {artifact_label} must not retain candidate-only publication claims"
        )


def assert_phase_neutral_release_notes(data: dict, notes: Path) -> None:
    version = data.get("version")
    if (
        not isinstance(version, str)
        or version_tuple(version) < PHASE_NEUTRAL_RELEASE_NOTES_FROM
    ):
        return
    text = notes.read_text(encoding="utf-8").strip()
    headings = PUBLICATION_CONTENT_HEADING_RE.findall(text)
    h1_headings = [title for marker, title in headings if marker == "#"]
    if len(h1_headings) != 1 or not h1_headings[0].startswith(data["release_id"]):
        raise ReleaseNotesError(
            "v0.13.0+ release notes must contain exactly one release-ID H1 heading"
        )
    unsupported_heading = next(
        (title for marker, title in headings if marker not in {"#", "##"}),
        None,
    )
    if unsupported_heading is not None:
        raise ReleaseNotesError(
            "v0.13.0+ release notes may contain only the release H1 and allowlisted H2 sections"
        )
    sections = [title for marker, title in headings if marker == "##"]
    if len(sections) != len(set(sections)):
        raise ReleaseNotesError("v0.13.0+ release-note sections must not be duplicated")
    unknown_sections = [
        section for section in sections if section not in PUBLICATION_SAFE_SECTION_ORDER
    ]
    if unknown_sections:
        raise ReleaseNotesError(
            "v0.13.0+ release-note sections must use the publication-content allowlist; "
            f"unsupported: {', '.join(unknown_sections)}"
        )
    section_positions = [PUBLICATION_SAFE_SECTION_ORDER.index(section) for section in sections]
    if section_positions != sorted(section_positions):
        raise ReleaseNotesError(
            "v0.13.0+ release-note sections must follow publication-content order"
        )
    assert_phase_neutral_publication_claims(data, notes, "release notes")


def validate_release(root: Path, version: str, commit: str, mode: str) -> tuple[dict, Path, Path]:
    commit = normalize_git_sha(commit, "commit")
    release_dir = root / ".dev" / "releases" / version
    record_path = release_dir / "release.yaml"
    data = load_mapping(record_path)
    expected_id = f"REL-{version}"
    if data.get("version") != version or data.get("release_id") != expected_id:
        raise ReleaseNotesError(f"{record_path} identity does not match {expected_id}")
    if data.get("record_origin") != "governed":
        raise ReleaseNotesError("automatic publication accepts governed releases only")
    if mode not in {"candidate", "publish", "published"}:
        raise ReleaseNotesError("mode must be candidate, publish, or published")
    status = data.get("status")
    allowed = (
        {"validated"}
        if mode == "publish"
        else {"published"}
        if mode == "published"
        else ALLOWED_CANDIDATE_STATUSES
    )
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
    required_multi_source_schema = (
        "3.0.0" if version_tuple(version) >= (0, 14, 0) else "2.0.0"
    )
    if (
        len(automatic_sources) > 1
        and migration_schema_version != required_multi_source_schema
    ):
        raise ReleaseNotesError(
            "multiple automatic upgrade sources require migration schema "
            f"{required_multi_source_schema}"
        )
    included_work_ids(data)
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ReleaseNotesError("artifacts must be a mapping")
    notes = resolve_artifact(artifacts.get("release_notes"), release_dir, "release_notes")
    migration = resolve_artifact(
        artifacts.get("migration_guide"), release_dir, "migration_guide"
    )
    assert_phase_neutral_release_notes(data, notes)
    assert_phase_neutral_publication_claims(data, migration, "migration guide")
    if mode == "published":
        assert_published_body_source(data, notes, version, commit)
    return data, notes, migration


def render_body_text(
    data: dict,
    notes_text: str,
    migration_text: str,
    commit: str,
) -> str:
    version = data["version"]
    release_id = data["release_id"]
    package_id = expected_package_id(version)
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
    parser.add_argument("--base-commit")
    parser.add_argument("--head-commit")
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--mode", choices=("candidate", "publish", "published"), default="candidate"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    try:
        root = args.root.resolve()
        if args.version:
            if args.base_commit or args.head_commit:
                raise ReleaseNotesError(
                    "explicit version must not be combined with base/head candidate selection"
                )
            version = normalize_version(args.version)
        else:
            if not args.base_commit or not args.head_commit:
                raise ReleaseNotesError(
                    "candidate selection requires both --base-commit and --head-commit"
                )
            version = discover_candidate(root, args.base_commit, args.head_commit)
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
            "package_id": expected_package_id(version),
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
    except CandidateNotApplicable as exc:
        print(f"Release-note rendering not applicable: {exc}", file=sys.stderr)
        return CANDIDATE_NOT_APPLICABLE_EXIT_CODE
    except (OSError, ReleaseNotesError) as exc:
        print(f"Release-note rendering failed: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered {data['release_id']} release body to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
