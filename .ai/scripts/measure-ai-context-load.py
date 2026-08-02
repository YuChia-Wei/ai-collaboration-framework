#!/usr/bin/env python3
"""Measure repository-backed AI context load events at one immutable Git commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/measure-ai-context-load.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "1.0"
REQUIRED_FAMILIES = {
    "runtime",
    "skill-routing",
    "release",
    "handoff",
    "development",
}
EVENT_KINDS = {"runtime", "full-file"}
FULL_OBJECT_ID = re.compile(r"^[0-9a-f]{40,64}$")


class MeasurementError(ValueError):
    """Raised when a context-load trace cannot be proven from Git."""


def run_git(repository: Path, *args: str, binary: bool = False) -> str | bytes:
    command = ["git", "-C", str(repository), *args]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=not binary,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (
            exc.stderr.decode("utf-8", errors="replace")
            if isinstance(exc.stderr, bytes)
            else exc.stderr
        )
        raise MeasurementError(
            f"Git command failed ({' '.join(command)}): {stderr.strip()}"
        ) from exc
    return completed.stdout


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MeasurementError(f"{path}: expected a YAML mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )


def require_clean_subject(repository: Path, subject_commit: object) -> str:
    if not isinstance(subject_commit, str) or not FULL_OBJECT_ID.fullmatch(
        subject_commit
    ):
        raise MeasurementError("subject_commit must be a full lowercase Git object id")
    head = str(run_git(repository, "rev-parse", "HEAD")).strip()
    if subject_commit != head:
        raise MeasurementError(
            f"subject_commit must equal repository HEAD ({head}), got {subject_commit}"
        )
    object_type = str(run_git(repository, "cat-file", "-t", subject_commit)).strip()
    if object_type != "commit":
        raise MeasurementError("subject_commit must resolve to a commit")
    dirty = str(
        run_git(repository, "status", "--porcelain=v1", "--untracked-files=all")
    )
    if dirty:
        raise MeasurementError("repository must be clean before measuring context load")
    return head


def safe_repo_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MeasurementError(f"{label}: path must be a non-empty string")
    if "\\" in value:
        raise MeasurementError(f"{label}: path must use repository POSIX separators")
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or value != candidate.as_posix()
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or candidate.parts[0] == ".git"
    ):
        raise MeasurementError(f"{label}: unsafe repository-relative path {value!r}")
    return candidate.as_posix()


def whitespace_words(payload: bytes) -> int:
    """Count non-whitespace byte runs without making an encoding claim."""

    return len(re.findall(rb"\S+", payload))


def list_commit_blobs(repository: Path, subject_commit: str) -> dict[str, str]:
    raw = run_git(
        repository,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        subject_commit,
        binary=True,
    )
    assert isinstance(raw, bytes)
    blobs: dict[str, str] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, object_type, object_id = metadata.decode("ascii").split(" ", 2)
            path = path_bytes.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise MeasurementError("subject tree contains an unsupported entry") from exc
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise MeasurementError(
                f"subject tree entry {path!r} is not a regular tracked file"
            )
        blobs[path] = object_id
    if not blobs:
        raise MeasurementError("subject tree contains no tracked files")
    return blobs


def blob_payload(repository: Path, object_id: str) -> bytes:
    payload = run_git(repository, "cat-file", "blob", object_id, binary=True)
    assert isinstance(payload, bytes)
    return payload


def validate_prompt_accounting(
    value: object, repository_loaded_bytes: int
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MeasurementError("prompt_accounting must be a mapping")
    total_tokens = value.get("total_prompt_tokens")
    total_source = value.get("total_prompt_tokens_source")
    if total_tokens is None:
        if total_source is not None:
            raise MeasurementError(
                "total_prompt_tokens_source must be null when total_prompt_tokens is null"
            )
    elif (
        isinstance(total_tokens, bool)
        or not isinstance(total_tokens, int)
        or total_tokens < 0
        or total_source != "provider_reported"
    ):
        raise MeasurementError(
            "total_prompt_tokens must be null or a non-negative provider_reported integer"
        )
    if value.get("repository_corpus_is_prompt") is not False:
        raise MeasurementError(
            "repository_corpus_is_prompt must be false; corpus size is not prompt load"
        )
    heuristic = value.get("repository_token_heuristic")
    if not isinstance(heuristic, dict):
        raise MeasurementError("repository_token_heuristic must be a mapping")
    if (
        heuristic.get("method") != "ceil-utf8-bytes-divided-by-four"
        or heuristic.get("scope") != "repository_loaded"
        or heuristic.get("is_total_prompt_tokens") is not False
    ):
        raise MeasurementError(
            "repository token heuristic must be explicitly scoped to "
            "repository_loaded and marked as not total prompt tokens"
        )
    return {
        "total_prompt_tokens": total_tokens,
        "total_prompt_tokens_source": total_source,
        "repository_corpus_is_prompt": False,
        "repository_token_heuristic": {
            "method": "ceil-utf8-bytes-divided-by-four",
            "scope": "repository_loaded",
            "approximate_tokens": math.ceil(repository_loaded_bytes / 4),
            "is_total_prompt_tokens": False,
        },
    }


def measure(repository: Path, traces_path: Path) -> dict[str, Any]:
    repository = repository.resolve()
    manifest = load_yaml_mapping(traces_path)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise MeasurementError(f"schema_version must be {SCHEMA_VERSION}")
    measurement_id = manifest.get("measurement_id")
    if not isinstance(measurement_id, str) or not measurement_id.strip():
        raise MeasurementError("measurement_id must be a non-empty string")
    subject_commit = require_clean_subject(repository, manifest.get("subject_commit"))
    tree = list_commit_blobs(repository, subject_commit)

    corpus_file_count = 0
    corpus_skipped_non_utf8 = 0
    corpus_bytes = 0
    corpus_words = 0
    payload_cache: dict[str, bytes] = {}
    for path, object_id in sorted(tree.items()):
        payload = blob_payload(repository, object_id)
        payload_cache[object_id] = payload
        try:
            payload.decode("utf-8")
        except UnicodeDecodeError:
            corpus_skipped_non_utf8 += 1
            continue
        corpus_file_count += 1
        byte_count = len(payload)
        word_count = whitespace_words(payload)
        corpus_bytes += byte_count
        corpus_words += word_count

    traces = manifest.get("traces")
    if not isinstance(traces, list):
        raise MeasurementError("traces must be a list")
    seen_families: set[str] = set()
    seen_event_kinds: set[str] = set()
    family_results: list[dict[str, Any]] = []
    loaded_bytes = 0
    loaded_words = 0
    loaded_events = 0

    for trace_index, trace in enumerate(traces):
        if not isinstance(trace, dict):
            raise MeasurementError(f"traces[{trace_index}] must be a mapping")
        family = trace.get("family")
        if not isinstance(family, str) or family not in REQUIRED_FAMILIES:
            raise MeasurementError(f"traces[{trace_index}].family is invalid")
        if family in seen_families:
            raise MeasurementError(f"duplicate trace family {family!r}")
        seen_families.add(family)
        events = trace.get("events")
        if not isinstance(events, list) or not events:
            raise MeasurementError(f"{family}: events must be a non-empty list")
        seen_paths: set[str] = set()
        normalized_events: list[dict[str, Any]] = []
        family_bytes = 0
        family_words = 0
        for event_index, event in enumerate(events):
            label = f"{family}.events[{event_index}]"
            if not isinstance(event, dict):
                raise MeasurementError(f"{label}: expected a mapping")
            event_kind = event.get("event_kind")
            if event_kind not in EVENT_KINDS:
                raise MeasurementError(
                    f"{label}.event_kind must be runtime or full-file"
                )
            seen_event_kinds.add(str(event_kind))
            path = safe_repo_path(event.get("path"), f"{label}.path")
            if path in seen_paths:
                raise MeasurementError(f"{family}: duplicate loaded path {path!r}")
            seen_paths.add(path)
            if path not in tree:
                raise MeasurementError(
                    f"{label}.path is not a regular file at subject_commit"
                )
            object_id = tree[path]
            payload = payload_cache[object_id]
            expected = {
                "git_blob": object_id,
                "bytes": len(payload),
                "whitespace_words": whitespace_words(payload),
            }
            for field, expected_value in expected.items():
                if event.get(field) != expected_value:
                    raise MeasurementError(
                        f"{label}.{field} drifted: expected {expected_value!r}, "
                        f"got {event.get(field)!r}"
                    )
            normalized = {
                "event_kind": event_kind,
                "path": path,
                **expected,
            }
            normalized_events.append(normalized)
            family_bytes += expected["bytes"]
            family_words += expected["whitespace_words"]
        loaded_events += len(normalized_events)
        loaded_bytes += family_bytes
        loaded_words += family_words
        family_results.append(
            {
                "family": family,
                "event_count": len(normalized_events),
                "bytes": family_bytes,
                "whitespace_words": family_words,
                "events": normalized_events,
            }
        )

    if seen_families != REQUIRED_FAMILIES:
        missing = sorted(REQUIRED_FAMILIES - seen_families)
        extra = sorted(seen_families - REQUIRED_FAMILIES)
        raise MeasurementError(
            f"trace families must be exactly {sorted(REQUIRED_FAMILIES)}; "
            f"missing={missing}, extra={extra}"
        )
    if seen_event_kinds != EVENT_KINDS:
        raise MeasurementError("trace events must exercise runtime and full-file kinds")

    result = {
        "schema_version": SCHEMA_VERSION,
        "measurement_id": measurement_id,
        "subject_commit": subject_commit,
        "repository_corpus": {
            "scope": "regular-tracked-utf8-files-at-subject-commit",
            "file_count": corpus_file_count,
            "skipped_non_utf8_file_count": corpus_skipped_non_utf8,
            "bytes": corpus_bytes,
            "whitespace_words": corpus_words,
        },
        "repository_loaded": {
            "scope": "declared-repository-backed-load-events-only",
            "family_count": len(family_results),
            "event_count": loaded_events,
            "bytes": loaded_bytes,
            "whitespace_words": loaded_words,
            "families": sorted(family_results, key=lambda item: item["family"]),
        },
        "prompt_accounting": validate_prompt_accounting(
            manifest.get("prompt_accounting"), loaded_bytes
        ),
    }
    canonical = json.dumps(
        result, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    result["measurement_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--repository", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = measure(args.repository, args.traces)
        if args.output:
            write_yaml(args.output, result)
        print(
            "AI context load measurement passed "
            f"({result['repository_loaded']['family_count']} families, "
            f"{result['repository_loaded']['event_count']} events, "
            f"{result['repository_loaded']['bytes']} repository-loaded bytes)."
        )
    except (MeasurementError, OSError, yaml.YAMLError) as exc:
        print(f"AI context load measurement failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
