#!/usr/bin/env python3
"""Validate exhaustive source-to-package disposition for omitted source files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-source-dispositions.py")

import yaml

from ai_context_package import (
    GitObjectReader,
    PackageError,
    REGULAR_MODES,
    collect_payload,
    commit_tree_sha,
    git_tree,
    is_excluded,
    load_yaml_blob,
    matches,
    resolve_commit,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ".ai/distribution/source-dispositions.yaml"
DEFAULT_PROFILE = ".ai/distribution/profiles/dotnet-backend.yaml"
SCHEMA_PATH = ".ai/distribution/schemas/source-dispositions.schema.yaml"
SCHEMA_VERSION = "1.0"
CONTRACT_KEYS = {
    "schema_version",
    "schema",
    "contract_id",
    "issue",
    "status",
    "owner_skill",
    "profile",
    "coverage",
    "dispositions",
}
PROFILE_KEYS = {"id", "path"}
COVERAGE_KEYS = {"source_patterns", "baseline_assessment", "derivation"}
RECORD_KEYS = {
    "id",
    "patterns",
    "classification",
    "owner",
    "reason",
    "retention",
    "package_behavior",
}
CLASSIFICATIONS = {
    "source-only",
    "target-owned",
    "historical-evidence",
    "generated-projection",
    "not-product-input",
}
RETENTIONS = {
    "retain-active",
    "retain-until-superseded",
    "retain-immutable",
    "retain-current-projection",
    "target-owner-decides",
}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SourceDispositionError(ValueError):
    """A fail-closed source disposition contract violation."""


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SourceDispositionError(f"{label} must be a mapping")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = sorted(set(value) - expected)
    missing = sorted(expected - set(value))
    if unknown:
        raise SourceDispositionError(f"{label} has unknown fields: {unknown}")
    if missing:
        raise SourceDispositionError(f"{label} is missing fields: {missing}")


def _non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceDispositionError(f"{label} must be a non-empty string")
    return value


def _valid_pattern(value: object, label: str) -> str:
    pattern = _non_empty_string(value, label)
    if "\\" in pattern or pattern.startswith(("/", "./")):
        raise SourceDispositionError(f"{label} must be a repository-relative POSIX pattern")
    if ".." in PurePosixPath(pattern).parts:
        raise SourceDispositionError(f"{label} must not traverse parent directories")
    return pattern


def load_contract(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise SourceDispositionError(f"cannot load source disposition contract: {exc}") from exc
    return _mapping(data, "source disposition contract")


def validate_contract_data(
    data: dict[str, Any],
    *,
    tracked_paths: set[str],
    packaged_paths: set[str],
    excluded_paths: set[str],
    source_ref: str,
    source_commit: str,
    source_tree: str,
    contract_path: str = DEFAULT_CONTRACT,
    profile_path: str = DEFAULT_PROFILE,
) -> dict[str, Any]:
    """Validate one already-derived source state and return deterministic read-back."""

    _exact_keys(data, CONTRACT_KEYS, "source disposition contract")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SourceDispositionError(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("schema") != SCHEMA_PATH:
        raise SourceDispositionError(f"schema must be {SCHEMA_PATH}")
    contract_id = _non_empty_string(data.get("contract_id"), "contract_id")
    if not ID_RE.fullmatch(contract_id):
        raise SourceDispositionError("contract_id must be a stable lowercase hyphenated ID")
    if data.get("issue") != 184:
        raise SourceDispositionError("issue must be 184")
    if data.get("status") != "active":
        raise SourceDispositionError("status must be active")
    if data.get("owner_skill") != "ai-context-governance":
        raise SourceDispositionError("owner_skill must be ai-context-governance")

    profile = _mapping(data.get("profile"), "profile")
    _exact_keys(profile, PROFILE_KEYS, "profile")
    if profile.get("id") != "dotnet-backend" or profile.get("path") != profile_path:
        raise SourceDispositionError(
            "profile must bind dotnet-backend to the validated distribution profile"
        )

    coverage = _mapping(data.get("coverage"), "coverage")
    _exact_keys(coverage, COVERAGE_KEYS, "coverage")
    source_patterns = coverage.get("source_patterns")
    if source_patterns != [".dev/**"]:
        raise SourceDispositionError("coverage.source_patterns must be exactly ['.dev/**']")
    if coverage.get("baseline_assessment") != "ASM-20260810-003#PKG-001":
        raise SourceDispositionError("coverage.baseline_assessment must bind ASM-20260810-003#PKG-001")
    if coverage.get("derivation") != "tracked-minus-packaged-minus-explicit-exclusion":
        raise SourceDispositionError(
            "coverage.derivation must be tracked-minus-packaged-minus-explicit-exclusion"
        )

    if packaged_paths - tracked_paths:
        raise SourceDispositionError("packaged scope contains paths outside tracked coverage")
    if excluded_paths - tracked_paths:
        raise SourceDispositionError("explicit-exclusion scope contains paths outside tracked coverage")
    overlap = packaged_paths & excluded_paths
    if overlap:
        raise SourceDispositionError(
            f"paths cannot be both packaged and explicitly excluded: {sorted(overlap)}"
        )
    implicit_paths = tracked_paths - packaged_paths - excluded_paths

    records = data.get("dispositions")
    if not isinstance(records, list) or not records:
        raise SourceDispositionError("dispositions must be a non-empty list")
    record_ids: set[str] = set()
    pattern_owners: dict[str, str] = {}
    normalized_records: list[dict[str, Any]] = []
    matches_by_path: dict[str, list[tuple[str, str]]] = {}

    for index, raw_record in enumerate(records):
        label = f"dispositions[{index}]"
        record = _mapping(raw_record, label)
        _exact_keys(record, RECORD_KEYS, label)
        record_id = _non_empty_string(record.get("id"), f"{label}.id")
        if not ID_RE.fullmatch(record_id):
            raise SourceDispositionError(f"{label}.id must be a stable lowercase hyphenated ID")
        if record_id in record_ids:
            raise SourceDispositionError(f"duplicate disposition id: {record_id}")
        record_ids.add(record_id)
        patterns = record.get("patterns")
        if not isinstance(patterns, list) or not patterns:
            raise SourceDispositionError(f"{label}.patterns must be a non-empty list")
        normalized_patterns: list[str] = []
        for pattern_index, raw_pattern in enumerate(patterns):
            pattern = _valid_pattern(raw_pattern, f"{label}.patterns[{pattern_index}]")
            if pattern in pattern_owners:
                raise SourceDispositionError(
                    f"duplicate disposition pattern {pattern!r} in {record_id} and {pattern_owners[pattern]}"
                )
            pattern_owners[pattern] = record_id
            matched = sorted(path for path in tracked_paths if matches(path, pattern))
            if not matched:
                raise SourceDispositionError(
                    f"stale disposition pattern matched no tracked coverage path: {pattern}"
                )
            normalized_patterns.append(pattern)
            for path in matched:
                matches_by_path.setdefault(path, []).append((record_id, pattern))
        classification = record.get("classification")
        if classification not in CLASSIFICATIONS:
            raise SourceDispositionError(
                f"{label}.classification must be one of {sorted(CLASSIFICATIONS)}"
            )
        retention = record.get("retention")
        if retention not in RETENTIONS:
            raise SourceDispositionError(f"{label}.retention must be one of {sorted(RETENTIONS)}")
        if record.get("package_behavior") != "exclude":
            raise SourceDispositionError(f"{label}.package_behavior must be exclude")
        owner = _non_empty_string(record.get("owner"), f"{label}.owner")
        reason = _non_empty_string(record.get("reason"), f"{label}.reason")
        normalized_records.append(
            {
                "id": record_id,
                "patterns": normalized_patterns,
                "classification": classification,
                "owner": owner,
                "reason": reason,
                "retention": retention,
                "package_behavior": "exclude",
            }
        )

    ambiguous = {
        path: entries for path, entries in matches_by_path.items() if len(entries) != 1
    }
    if ambiguous:
        rendered = {path: entries for path, entries in sorted(ambiguous.items())}
        raise SourceDispositionError(f"overlapping disposition matches: {rendered}")
    disposition_paths = set(matches_by_path)
    payload_conflicts = disposition_paths & packaged_paths
    if payload_conflicts:
        raise SourceDispositionError(
            f"dispositions must not overlap packaged source paths: {sorted(payload_conflicts)}"
        )
    exclusion_conflicts = disposition_paths & excluded_paths
    if exclusion_conflicts:
        raise SourceDispositionError(
            "dispositions must not overlap explicit profile exclusions: "
            f"{sorted(exclusion_conflicts)}"
        )
    missing = implicit_paths - disposition_paths
    extra = disposition_paths - implicit_paths
    if missing or extra:
        raise SourceDispositionError(
            "source dispositions must cover exactly all implicit omissions; "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )

    record_by_id = {record["id"]: record for record in normalized_records}
    path_records: list[dict[str, Any]] = []
    classification_counts = {classification: 0 for classification in sorted(CLASSIFICATIONS)}
    for path in sorted(implicit_paths, key=lambda item: item.encode("utf-8")):
        record_id, pattern = matches_by_path[path][0]
        record = record_by_id[record_id]
        classification_counts[record["classification"]] += 1
        path_records.append(
            {
                "path": path,
                "disposition_id": record_id,
                "matched_pattern": pattern,
                "classification": record["classification"],
                "owner": record["owner"],
                "reason": record["reason"],
                "retention": record["retention"],
                "package_behavior": record["package_behavior"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": contract_id,
        "contract_path": contract_path,
        "profile_id": profile["id"],
        "profile_path": profile_path,
        "source_ref": source_ref,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "coverage": {
            "tracked_paths": len(tracked_paths),
            "packaged_source_paths": len(packaged_paths),
            "explicitly_excluded_paths": len(excluded_paths),
            "disposition_paths": len(path_records),
            "implicit_omissions": 0,
        },
        "classification_counts": classification_counts,
        "paths": path_records,
    }


def validate_repository(
    root: Path,
    *,
    contract_path: str = DEFAULT_CONTRACT,
    profile_path: str = DEFAULT_PROFILE,
    source_ref: str = "HEAD",
) -> dict[str, Any]:
    contract = load_contract(root / contract_path)
    try:
        commit = resolve_commit(root, source_ref)
        tree = git_tree(root, commit)
        profile = load_yaml_blob(root, tree, profile_path)
        profile_id = profile.get("profile", {}).get("id")
        if profile_id != "dotnet-backend":
            raise SourceDispositionError("validated profile id must be dotnet-backend")
        coverage = _mapping(contract.get("coverage"), "coverage")
        patterns = coverage.get("source_patterns")
        if not isinstance(patterns, list) or not patterns:
            raise SourceDispositionError("coverage.source_patterns must be a non-empty list")
        tracked = {
            path for path in tree if any(matches(path, pattern) for pattern in patterns)
        }
        reader = GitObjectReader(root)
        reader.read_blobs_batch(
            entry
            for entry in tree.values()
            if entry.object_type == "blob" and entry.mode in REGULAR_MODES
        )
        payload = collect_payload(root, tree, profile, reader)
        packaged = {item.source_path for item in payload if item.source_path in tracked}
        exclusions = profile.get("exclusions")
        if not isinstance(exclusions, list):
            raise SourceDispositionError("profile exclusions must be a list")
        excluded = {path for path in tracked if is_excluded(path, exclusions)}
        tree_sha = commit_tree_sha(root, commit)
    except PackageError as exc:
        raise SourceDispositionError(f"cannot derive package disposition: {exc}") from exc
    return validate_contract_data(
        contract,
        tracked_paths=tracked,
        packaged_paths=packaged,
        excluded_paths=excluded,
        source_ref=source_ref,
        source_commit=commit,
        source_tree=tree_sha,
        contract_path=contract_path,
        profile_path=profile_path,
    )


def markdown_report(report: dict[str, Any]) -> str:
    counts = report["coverage"]
    lines = [
        "# Source Disposition Read-back",
        "",
        f"- Contract: `{report['contract_id']}`",
        f"- Source: `{report['source_ref']}` → `{report['source_commit']}`",
        f"- Tree: `{report['source_tree']}`",
        f"- Profile: `{report['profile_id']}`",
        f"- Tracked coverage paths: {counts['tracked_paths']}",
        f"- Packaged source paths: {counts['packaged_source_paths']}",
        f"- Explicitly excluded paths: {counts['explicitly_excluded_paths']}",
        f"- Disposition-covered paths: {counts['disposition_paths']}",
        f"- Remaining implicit omissions: {counts['implicit_omissions']}",
        "",
        "## Classification Counts",
        "",
        "| Classification | Paths |",
        "| --- | ---: |",
    ]
    for classification, count in report["classification_counts"].items():
        lines.append(f"| `{classification}` | {count} |")
    lines.extend(
        [
            "",
            "## Disposition Paths",
            "",
            "| Source Path | Disposition | Classification | Owner | Retention |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["paths"]:
        escaped_path = item["path"].replace("|", "\\|")
        lines.append(
            f"| `{escaped_path}` | `{item['disposition_id']}` | "
            f"`{item['classification']}` | `{item['owner']}` | `{item['retention']}` |"
        )
    return "\n".join(lines) + "\n"


def render_report(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output_format == "markdown":
        return markdown_report(report)
    coverage = report["coverage"]
    return (
        "Source disposition validation passed: "
        f"{coverage['tracked_paths']} tracked .dev paths = "
        f"{coverage['packaged_source_paths']} packaged + "
        f"{coverage['explicitly_excluded_paths']} explicit exclusions + "
        f"{coverage['disposition_paths']} governed dispositions; "
        "0 implicit omissions.\n"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--profile", default=DEFAULT_PROFILE)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--format", choices=("summary", "json", "markdown"), default="summary")
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_repository(
            ROOT,
            contract_path=args.contract,
            profile_path=args.profile,
            source_ref=args.ref,
        )
        rendered = render_report(report, args.format)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"Source disposition read-back written to {args.output}.")
        else:
            print(rendered, end="")
    except (OSError, SourceDispositionError) as exc:
        print(f"Source disposition validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
