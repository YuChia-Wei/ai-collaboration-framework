#!/usr/bin/env python3
"""Create and verify fail-closed source immutable-history validation receipts.

``refresh`` is intentionally the expensive operation: it runs every native
full validator declared by the source contract and records Git-object bindings.
``verify`` is the routine operation. It never walks or hashes workflow or
assessment history; it verifies the receipt's containing-commit provenance,
rechecks the comparatively small release-declaration set for tag completeness,
and classifies a bounded ``git diff --name-status`` from the recorded source
revision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-immutable-history.py")

import yaml


FULL_REQUIRED_EXIT = 10
ERROR_EXIT = 2
GIT_COMMAND_TIMEOUT_SECONDS = 30
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
HEX_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
RELEASE_TAG_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
SOURCE_HISTORY_ROOTS = (
    ".dev/workflows",
    ".dev/assessments",
    ".dev/releases",
)
SOURCE_HISTORY_INDEXES = (
    ".dev/workflows/INDEX.MD",
    ".dev/assessments/INDEX.MD",
    ".dev/releases/INDEX.MD",
)
SOURCE_PROTECTED_PATHS = (
    ".dev/backlog/**",
    ".dev/ai-context/**",
    ".dev/AI-CONTEXT-SOURCE.yaml",
)
REUSABLE_CHECK_IDS = (
    "workflow-artifacts",
    "assessment-artifacts",
    "source-ai-context-version",
)
ROUTINE_PROFILES = ("fast", "pr")
FULL_PROFILES = ("release", "nightly-full")
FULL_GATES = (
    "release-candidate",
    "scheduled-governance",
    "validator-schema-change",
    "immutable-history-change",
)
ROUTINE_ALLOWLIST = (
    ".ai/distribution/validation/immutable-history-receipt.yaml",
    ".ai/assets/**",
    ".ai/scripts/README.md",
    ".ai/scripts/tests/**",
    ".dev/guides/**",
    "docs/**",
    "src/**",
    "tests/**",
    "tools/**",
    "README.md",
    "README.en.md",
    "AGENTS.md",
    "AGENTS.zh-TW.md",
    "CLAUDE.md",
)


class ImmutableHistoryError(Exception):
    """A declared contract, invocation, or repository precondition failed."""


class ReceiptUnavailable(ImmutableHistoryError):
    """A receipt cannot safely be reused and requires a full validation."""

    def __init__(self, reason: str, *, source_revision: str | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.source_revision = source_revision


class DuplicateKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.YAMLError(f"duplicate mapping key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DuplicateKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


@dataclass(frozen=True)
class NativeFullValidator:
    check_id: str
    command: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class Contract:
    contract_id: str
    history_roots: tuple[str, ...]
    history_indexes: tuple[str, ...]
    protected_paths: tuple[str, ...]
    validator_fingerprint_paths: tuple[str, ...]
    schema_fingerprint_paths: tuple[str, ...]
    receipt_path: str
    allowed_diff_paths: tuple[str, ...]
    routine_profiles: tuple[str, ...]
    full_profiles: tuple[str, ...]
    full_gates: tuple[str, ...]
    native_full_validators: tuple[NativeFullValidator, ...]
    downstream_target_command: tuple[str, ...]


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def digest_records(kind: str, records: Iterable[dict[str, str]]) -> str:
    payload = {"digest_schema_version": "1.0", "kind": kind, "objects": sorted(records, key=lambda item: item["path"])}
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ImmutableHistoryError(f"{label} must be a non-empty repository-relative path")
    if "\\" in value or value.startswith("/") or ":" in value:
        raise ImmutableHistoryError(f"{label} must use a portable repository-relative path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ImmutableHistoryError(f"{label} contains an unsafe path segment")
    return value


def safe_allowlist_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ImmutableHistoryError(f"{label} must be a non-empty path or /** prefix")
    if value.endswith("/**"):
        safe_relative_path(value[:-3], label)
        return value
    if "*" in value:
        raise ImmutableHistoryError(f"{label} supports only a terminal /** prefix")
    return safe_relative_path(value, label)


def require_exact_keys(value: object, required: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ImmutableHistoryError(f"{label} must be a mapping")
    actual = set(value)
    missing = sorted(required - actual)
    unknown = sorted(actual - required)
    if missing or unknown:
        detail: list[str] = []
        if missing:
            detail.append("missing=" + ",".join(missing))
        if unknown:
            detail.append("unknown=" + ",".join(unknown))
        raise ImmutableHistoryError(f"{label} has invalid keys ({'; '.join(detail)})")
    return value


def strict_string_list(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ImmutableHistoryError(f"{label} must be a non-empty list of strings")
    values = tuple(value)
    if len(values) != len(set(values)):
        raise ImmutableHistoryError(f"{label} must not contain duplicates")
    return values


def load_yaml_mapping(path: Path, label: str, *, receipt: bool) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=DuplicateKeySafeLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        if receipt:
            raise ReceiptUnavailable("receipt-malformed") from exc
        raise ImmutableHistoryError(f"{label} cannot be parsed: {exc}") from exc
    if not isinstance(value, dict):
        if receipt:
            raise ReceiptUnavailable("receipt-malformed")
        raise ImmutableHistoryError(f"{label} must be a YAML mapping")
    return value


def load_contract(path: Path) -> Contract:
    data = load_yaml_mapping(path, str(path), receipt=False)
    root = require_exact_keys(data, {"schema_version", "contract_id", "source", "downstream"}, "contract")
    if root["schema_version"] != "1.0":
        raise ImmutableHistoryError("contract.schema_version must be 1.0")
    if root["contract_id"] != "immutable-history-validation":
        raise ImmutableHistoryError("contract.contract_id must be immutable-history-validation")

    source = require_exact_keys(
        root["source"],
        {"history_roots", "history_indexes", "protected_paths", "fingerprint_paths", "receipt", "profiles", "native_full_validators"},
        "contract.source",
    )
    roots = tuple(safe_relative_path(item, "contract.source.history_roots") for item in strict_string_list(source["history_roots"], "contract.source.history_roots"))
    if roots != SOURCE_HISTORY_ROOTS:
        raise ImmutableHistoryError("contract.source.history_roots must declare the exact source immutable-history roots")
    indexes = tuple(safe_relative_path(item, "contract.source.history_indexes") for item in strict_string_list(source["history_indexes"], "contract.source.history_indexes"))
    if indexes != SOURCE_HISTORY_INDEXES:
        raise ImmutableHistoryError("contract.source.history_indexes must declare the exact source immutable-history indexes")
    protected_paths = tuple(safe_allowlist_path(item, "contract.source.protected_paths") for item in strict_string_list(source["protected_paths"], "contract.source.protected_paths"))
    if protected_paths != SOURCE_PROTECTED_PATHS:
        raise ImmutableHistoryError("contract.source.protected_paths must declare the governed source-validator inputs")

    fingerprints = require_exact_keys(source["fingerprint_paths"], {"validators", "schema"}, "contract.source.fingerprint_paths")
    validators = tuple(safe_relative_path(item, "contract.source.fingerprint_paths.validators") for item in strict_string_list(fingerprints["validators"], "contract.source.fingerprint_paths.validators"))
    schemas = tuple(safe_relative_path(item, "contract.source.fingerprint_paths.schema") for item in strict_string_list(fingerprints["schema"], "contract.source.fingerprint_paths.schema"))
    if set(validators) & set(schemas):
        raise ImmutableHistoryError("validator and schema fingerprint paths must be disjoint")

    receipt = require_exact_keys(source["receipt"], {"path", "schema_version", "allowed_diff_paths"}, "contract.source.receipt")
    receipt_path = safe_relative_path(receipt["path"], "contract.source.receipt.path")
    if receipt["schema_version"] != "1.0":
        raise ImmutableHistoryError("contract.source.receipt.schema_version must be 1.0")
    allowed_diff_paths = tuple(safe_allowlist_path(item, "contract.source.receipt.allowed_diff_paths") for item in strict_string_list(receipt["allowed_diff_paths"], "contract.source.receipt.allowed_diff_paths"))
    if allowed_diff_paths != ROUTINE_ALLOWLIST:
        raise ImmutableHistoryError("contract.source.receipt.allowed_diff_paths must declare the governed closed routine allowlist")
    if receipt_path != allowed_diff_paths[0]:
        raise ImmutableHistoryError("contract.source.receipt.allowed_diff_paths must begin with the receipt path")
    protected = set(validators) | set(schemas) | set(indexes)
    if receipt_path in protected:
        raise ImmutableHistoryError("receipt path must not be a fingerprint path")
    if any(receipt_path == root_path or receipt_path.startswith(root_path + "/") for root_path in roots):
        raise ImmutableHistoryError("receipt path must be outside immutable-history roots")

    profiles = require_exact_keys(source["profiles"], {"routine", "full", "full_gates"}, "contract.source.profiles")
    routine_profiles = strict_string_list(profiles["routine"], "contract.source.profiles.routine")
    full_profiles = strict_string_list(profiles["full"], "contract.source.profiles.full")
    full_gates = strict_string_list(profiles["full_gates"], "contract.source.profiles.full_gates")
    if routine_profiles != ROUTINE_PROFILES or full_profiles != FULL_PROFILES or full_gates != FULL_GATES:
        raise ImmutableHistoryError("contract.source.profiles must declare the governed routine/full profile and gate sets")

    raw_validators = source["native_full_validators"]
    if not isinstance(raw_validators, list) or not raw_validators:
        raise ImmutableHistoryError("contract.source.native_full_validators must be a non-empty list")
    native_validators: list[NativeFullValidator] = []
    for index, item in enumerate(raw_validators):
        validator = require_exact_keys(
            item,
            {"check_id", "command", "timeout_seconds"},
            f"contract.source.native_full_validators[{index}]",
        )
        check_id = validator["check_id"]
        if not isinstance(check_id, str) or not check_id:
            raise ImmutableHistoryError(f"contract.source.native_full_validators[{index}].check_id must be a string")
        command = strict_string_list(validator["command"], f"contract.source.native_full_validators[{index}].command")
        timeout_seconds = validator["timeout_seconds"]
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ImmutableHistoryError(
                f"contract.source.native_full_validators[{index}].timeout_seconds must be a positive integer"
            )
        if any("\x00" in argument for argument in command):
            raise ImmutableHistoryError(f"contract.source.native_full_validators[{index}].command contains NUL")
        if (
            len(command) != 2
            or command[0] != "python"
            or command[1] not in validators
            or not command[1].startswith(".ai/scripts/")
            or not command[1].endswith(".py")
        ):
            raise ImmutableHistoryError(
                f"contract.source.native_full_validators[{index}].command must invoke one fingerprinted Python validator"
            )
        native_validators.append(
            NativeFullValidator(
                check_id=check_id,
                command=command,
                timeout_seconds=timeout_seconds,
            )
        )
    if tuple(item.check_id for item in native_validators) != REUSABLE_CHECK_IDS:
        raise ImmutableHistoryError("contract.source.native_full_validators must declare the governed reusable check IDs in order")

    downstream = require_exact_keys(root["downstream"], {"mode", "source_history_receipt", "target_local_validation"}, "contract.downstream")
    if downstream["mode"] != "target-local-ai-context-only" or downstream["source_history_receipt"] != "forbidden":
        raise ImmutableHistoryError("contract.downstream must forbid a source-history receipt and select target-local AI-context validation")
    target_command = strict_string_list(downstream["target_local_validation"], "contract.downstream.target_local_validation")

    return Contract(
        contract_id=root["contract_id"],
        history_roots=roots,
        history_indexes=indexes,
        protected_paths=protected_paths,
        validator_fingerprint_paths=validators,
        schema_fingerprint_paths=schemas,
        receipt_path=receipt_path,
        allowed_diff_paths=allowed_diff_paths,
        routine_profiles=routine_profiles,
        full_profiles=full_profiles,
        full_gates=full_gates,
        native_full_validators=tuple(native_validators),
        downstream_target_command=target_command,
    )


def git_bytes(repo: Path, arguments: Sequence[str], *, error: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repo,
            check=False,
            capture_output=True,
            timeout=GIT_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ImmutableHistoryError(
            f"{error}: git command timed out after {GIT_COMMAND_TIMEOUT_SECONDS} seconds"
        ) from exc
    except OSError as exc:
        raise ImmutableHistoryError(f"{error}: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ImmutableHistoryError(f"{error}: {detail or 'git command failed'}")
    return result.stdout


def git_text(repo: Path, arguments: Sequence[str], *, error: str) -> str:
    return git_bytes(repo, arguments, error=error).decode("utf-8", errors="strict").strip()


def committed_revision(repo: Path, reference: str) -> str:
    if reference != "HEAD" and not SHA_RE.fullmatch(reference):
        raise ImmutableHistoryError("--head must be HEAD or a 40-character lowercase Git SHA")
    value = git_text(repo, ["rev-parse", "--verify", f"{reference}^{{commit}}"], error="cannot resolve committed head")
    if not SHA_RE.fullmatch(value):
        raise ImmutableHistoryError("cannot resolve a 40-character committed head")
    return value


def worktree_dirty(repo: Path) -> bool:
    return bool(git_bytes(repo, ["status", "--porcelain=v1", "--untracked-files=all"], error="cannot inspect worktree").strip())


def object_id(repo: Path, revision: str, path: str, expected_type: str) -> str:
    try:
        oid = git_text(repo, ["rev-parse", "--verify", f"{revision}:{path}"], error=f"cannot resolve {path} at {revision}")
        object_type = git_text(repo, ["cat-file", "-t", oid], error=f"cannot inspect {path} at {revision}")
    except ImmutableHistoryError as exc:
        raise ReceiptUnavailable("source-object-missing", source_revision=revision) from exc
    if not SHA_RE.fullmatch(oid) or object_type != expected_type:
        raise ReceiptUnavailable("source-object-missing", source_revision=revision)
    return oid


def release_ref_records(repo: Path, revision: str) -> list[dict[str, str]]:
    paths = git_text(
        repo,
        ["ls-tree", "-r", "--name-only", revision, "--", ".dev/releases"],
        error="cannot enumerate release records",
    ).splitlines()
    records: list[dict[str, str]] = []
    seen_tags: set[str] = set()
    for path in sorted(path for path in paths if re.fullmatch(r"\.dev/releases/[^/]+/release\.yaml", path)):
        raw = git_bytes(repo, ["show", f"{revision}:{path}"], error=f"cannot read release record {path}")
        try:
            release = yaml.load(raw.decode("utf-8"), Loader=DuplicateKeySafeLoader)
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            raise ReceiptUnavailable("release-reference-malformed", source_revision=revision) from exc
        if not isinstance(release, dict):
            raise ReceiptUnavailable("release-reference-malformed", source_revision=revision)
        if release.get("status") in {"planned", "validated"}:
            continue
        tag = release.get("tag")
        declared_commit = release.get("commit")
        path_match = re.fullmatch(r"\.dev/releases/([^/]+)/release\.yaml", path)
        if (
            path_match is None
            or not isinstance(tag, str)
            or not RELEASE_TAG_RE.fullmatch(tag)
            or tag != path_match.group(1)
            or tag in seen_tags
            or not isinstance(declared_commit, str)
            or not SHA_RE.fullmatch(declared_commit)
        ):
            raise ReceiptUnavailable("release-reference-malformed", source_revision=revision)
        try:
            resolved_commit = git_text(repo, ["rev-parse", "--verify", f"{tag}^{{commit}}"], error=f"cannot resolve release tag {tag}")
        except ImmutableHistoryError as exc:
            raise ReceiptUnavailable("release-reference-drift", source_revision=revision) from exc
        if not SHA_RE.fullmatch(resolved_commit) or resolved_commit != declared_commit:
            raise ReceiptUnavailable("release-reference-drift", source_revision=revision)
        seen_tags.add(tag)
        records.append(
            {
                "path": path,
                "tag": tag,
                "declared_commit": declared_commit,
                "resolved_commit": resolved_commit,
            }
        )
    return records


def source_bindings(repo: Path, revision: str, contract: Contract, *, include_release_refs: bool) -> dict[str, Any]:
    try:
        tree = git_text(repo, ["rev-parse", "--verify", f"{revision}^{{tree}}"], error=f"cannot resolve source tree {revision}")
    except ImmutableHistoryError as exc:
        raise ReceiptUnavailable("source-tree-missing", source_revision=revision) from exc
    if not SHA_RE.fullmatch(tree):
        raise ReceiptUnavailable("source-tree-missing", source_revision=revision)
    history = [
        {"path": path, "object_id": object_id(repo, revision, path, "tree")}
        for path in contract.history_roots
    ]
    validators = [
        {"path": path, "object_id": object_id(repo, revision, path, "blob")}
        for path in contract.validator_fingerprint_paths
    ]
    schemas = [
        {"path": path, "object_id": object_id(repo, revision, path, "blob")}
        for path in contract.schema_fingerprint_paths
    ]
    indexes = [
        {"path": path, "object_id": object_id(repo, revision, path, "blob")}
        for path in contract.history_indexes
    ]
    bindings: dict[str, Any] = {
        "revision": revision,
        "tree": tree,
        "history_digest": digest_records("history-roots", history),
        "validator_digest": digest_records("validator-fingerprints", validators),
        "schema_digest": digest_records("schema-fingerprints", schemas),
        "index_digest": digest_records("history-indexes", indexes),
    }
    if include_release_refs:
        release_refs = release_ref_records(repo, revision)
        bindings["release_ref_digest"] = digest_records("release-tag-refs", release_refs)
        bindings["release_refs"] = release_refs
    return bindings


def load_receipt(repo: Path, contract: Contract) -> dict[str, Any]:
    path = repo / contract.receipt_path
    if path.is_symlink() or not path.is_file():
        raise ReceiptUnavailable("receipt-missing")
    data = load_yaml_mapping(path, contract.receipt_path, receipt=True)
    try:
        root = require_exact_keys(data, {"schema_version", "contract_id", "source"}, "receipt")
        if root["schema_version"] != "1.0" or root["contract_id"] != contract.contract_id:
            raise ReceiptUnavailable("receipt-schema-mismatch")
        source = require_exact_keys(
            root["source"],
            {"revision", "tree", "history_digest", "validator_digest", "schema_digest", "index_digest", "release_ref_digest", "release_refs"},
            "receipt.source",
        )
        values = {key: source[key] for key in ("revision", "tree", "history_digest", "validator_digest", "schema_digest", "index_digest", "release_ref_digest")}
        if not all(isinstance(value, str) for value in values.values()):
            raise ReceiptUnavailable("receipt-malformed")
        if not SHA_RE.fullmatch(values["revision"]) or not SHA_RE.fullmatch(values["tree"]):
            raise ReceiptUnavailable("receipt-malformed")
        if any(not HEX_DIGEST_RE.fullmatch(values[key]) for key in ("history_digest", "validator_digest", "schema_digest", "index_digest", "release_ref_digest")):
            raise ReceiptUnavailable("receipt-malformed")
        release_refs = source["release_refs"]
        if not isinstance(release_refs, list):
            raise ReceiptUnavailable("receipt-malformed")
        validated_refs: list[dict[str, str]] = []
        seen_paths: set[str] = set()
        seen_tags: set[str] = set()
        for index, item in enumerate(release_refs):
            record = require_exact_keys(item, {"path", "tag", "declared_commit", "resolved_commit"}, f"receipt.source.release_refs[{index}]")
            if not all(isinstance(record[key], str) for key in record):
                raise ReceiptUnavailable("receipt-malformed")
            path_match = re.fullmatch(r"\.dev/releases/([^/]+)/release\.yaml", record["path"])
            if (
                path_match is None
                or not RELEASE_TAG_RE.fullmatch(record["tag"])
                or record["tag"] != path_match.group(1)
                or record["path"] in seen_paths
                or record["tag"] in seen_tags
            ):
                raise ReceiptUnavailable("receipt-malformed")
            if not SHA_RE.fullmatch(record["declared_commit"]) or not SHA_RE.fullmatch(record["resolved_commit"]):
                raise ReceiptUnavailable("receipt-malformed")
            if record["declared_commit"] != record["resolved_commit"]:
                raise ReceiptUnavailable("receipt-malformed")
            seen_paths.add(record["path"])
            seen_tags.add(record["tag"])
            validated_refs.append(dict(record))
        if validated_refs != sorted(validated_refs, key=lambda item: item["path"]):
            raise ReceiptUnavailable("receipt-malformed")
        if digest_records("release-tag-refs", validated_refs) != values["release_ref_digest"]:
            raise ReceiptUnavailable("receipt-release-ref-digest-mismatch")
        values["release_refs"] = validated_refs
        return values
    except ImmutableHistoryError as exc:
        raise ReceiptUnavailable("receipt-schema-mismatch") from exc


def receipt_containing_commit(repo: Path, head: str, receipt_path: str) -> str:
    value = git_text(
        repo,
        ["log", "--first-parent", "--format=%H", "-n", "1", head, "--", receipt_path],
        error="cannot resolve receipt containing commit",
    )
    if not SHA_RE.fullmatch(value):
        raise ReceiptUnavailable("receipt-not-committed")
    return value


def bounded_continuation_commits(repo: Path, receipt_commit: str, head: str) -> tuple[str, ...]:
    values = git_text(
        repo,
        ["rev-list", "--first-parent", "--reverse", f"{receipt_commit}..{head}"],
        error="cannot resolve bounded first-parent continuation",
    )
    commits = tuple(value for value in values.splitlines() if value)
    if not all(SHA_RE.fullmatch(value) for value in commits):
        raise ImmutableHistoryError("cannot resolve a bounded first-parent continuation")
    return commits


def name_status(repo: Path, arguments: Sequence[str], *, error: str) -> tuple[tuple[str, str], ...]:
    raw = git_bytes(repo, [*arguments, "--name-status", "--no-renames", "-z"], error=error)
    tokens = raw.split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    if len(tokens) % 2:
        raise ImmutableHistoryError(f"{error}: malformed Git name-status output")
    pairs: list[tuple[str, str]] = []
    for index in range(0, len(tokens), 2):
        status = tokens[index].decode("ascii", errors="strict")
        path = tokens[index + 1].decode("utf-8", errors="strict")
        pairs.append((status, path))
    return tuple(pairs)


def verify_containing_commit(repo: Path, receipt_commit: str, receipt: dict[str, Any], contract: Contract) -> None:
    parents = git_text(repo, ["rev-list", "--parents", "-n", "1", receipt_commit], error="cannot inspect receipt commit parents").split()
    if len(parents) != 2 or parents[0] != receipt_commit:
        raise ReceiptUnavailable("receipt-commit-parent-invalid", source_revision=receipt["revision"])
    if parents[1] != receipt["revision"]:
        raise ReceiptUnavailable("receipt-source-not-first-parent", source_revision=receipt["revision"])
    changes = name_status(repo, ["diff-tree", "--no-commit-id", "-r", receipt_commit], error="cannot inspect receipt commit")
    if changes != (("A", contract.receipt_path),) and changes != (("M", contract.receipt_path),):
        raise ReceiptUnavailable("receipt-commit-not-receipt-only", source_revision=receipt["revision"])


def classify_diff(contract: Contract, changes: tuple[tuple[str, str], ...], source_revision: str) -> None:
    for status, path in changes:
        if status not in {"A", "M", "D"}:
            raise ReceiptUnavailable("closed-allowlist-mismatch", source_revision=source_revision)
        if any(path == root or path.startswith(root + "/") for root in contract.history_roots):
            raise ReceiptUnavailable("immutable-history-change", source_revision=source_revision)
        if path in contract.history_indexes:
            raise ReceiptUnavailable("history-index-change", source_revision=source_revision)
        if path in contract.validator_fingerprint_paths:
            raise ReceiptUnavailable("validator-change", source_revision=source_revision)
        if path in contract.schema_fingerprint_paths:
            raise ReceiptUnavailable("schema-change", source_revision=source_revision)
        if any(path == protected or (protected.endswith("/**") and path.startswith(protected[:-2])) for protected in contract.protected_paths):
            raise ReceiptUnavailable("protected-source-input-change", source_revision=source_revision)
        if status == "D":
            raise ReceiptUnavailable("deleted-continuation-path", source_revision=source_revision)
        if not any(
            path == allowed or (allowed.endswith("/**") and path.startswith(allowed[:-2]))
            for allowed in contract.allowed_diff_paths
        ):
            raise ReceiptUnavailable("closed-allowlist-mismatch", source_revision=source_revision)


def receipt_payload(contract: Contract, bindings: dict[str, Any]) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "contract_id": contract.contract_id,
        "source": {
            "revision": bindings["revision"],
            "tree": bindings["tree"],
            "history_digest": bindings["history_digest"],
            "validator_digest": bindings["validator_digest"],
            "schema_digest": bindings["schema_digest"],
            "index_digest": bindings["index_digest"],
            "release_ref_digest": bindings["release_ref_digest"],
            "release_refs": bindings["release_refs"],
        },
    }


def write_receipt(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(payload, allow_unicode=True, default_flow_style=False, sort_keys=False)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".immutable-history-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
        os.replace(temporary_name, path)
    except OSError as exc:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise ImmutableHistoryError(f"cannot write receipt: {exc}") from exc


def result_payload(
    outcome: str,
    reason: str,
    *,
    source_revision: str | None,
    source_tree: str | None,
    receipt_commit: str | None,
    reusable_check_ids: Sequence[str] = (),
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "outcome": outcome,
        "reason": reason,
        "source_revision": source_revision,
        "source_tree": source_tree,
        "receipt_commit": receipt_commit,
        "reusable_check_ids": list(reusable_check_ids),
    }
    if extra:
        payload.update(extra)
    return payload


def emit(payload: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
        return
    check_ids = payload.get("reusable_check_ids", [])
    values = (
        str(payload.get("outcome") or ""),
        str(payload.get("reason") or ""),
        str(payload.get("source_revision") or ""),
        str(payload.get("source_tree") or ""),
        str(payload.get("receipt_commit") or ""),
        ",".join(check_ids) if isinstance(check_ids, list) else "",
    )
    print("\t".join(values))


def verify_source(
    repo: Path,
    contract: Contract,
    profile: str,
    gates: Sequence[str],
    head_reference: str,
) -> tuple[dict[str, object], int]:
    head = committed_revision(repo, head_reference)
    if head != committed_revision(repo, "HEAD"):
        raise ImmutableHistoryError("--head must resolve to the checked-out HEAD")
    if profile not in contract.routine_profiles + contract.full_profiles:
        raise ImmutableHistoryError(f"unsupported validation profile: {profile}")
    unsupported_gates = [gate for gate in gates if gate not in contract.full_gates]
    if unsupported_gates:
        raise ImmutableHistoryError("unsupported full-validation gate: " + ",".join(unsupported_gates))
    if profile in contract.full_profiles:
        return result_payload("full-required", "profile-requires-full-validation", source_revision=None, source_tree=None, receipt_commit=None), FULL_REQUIRED_EXIT
    if gates:
        return result_payload("full-required", "gate-requires-full-validation", source_revision=None, source_tree=None, receipt_commit=None), FULL_REQUIRED_EXIT
    if worktree_dirty(repo):
        return result_payload("full-required", "dirty-worktree", source_revision=None, source_tree=None, receipt_commit=None), FULL_REQUIRED_EXIT

    receipt: dict[str, Any] | None = None
    receipt_commit: str | None = None
    try:
        receipt = load_receipt(repo, contract)
        source_revision = receipt["revision"]
        receipt_commit = receipt_containing_commit(repo, head, contract.receipt_path)
        verify_containing_commit(repo, receipt_commit, receipt, contract)
        bindings = source_bindings(repo, source_revision, contract, include_release_refs=False)
        for key in ("tree", "history_digest", "validator_digest", "schema_digest", "index_digest"):
            if bindings[key] != receipt[key]:
                raise ReceiptUnavailable(f"receipt-{key.replace('_', '-')}-mismatch", source_revision=source_revision)
        source_release_refs = release_ref_records(repo, source_revision)
        if source_release_refs != receipt["release_refs"]:
            raise ReceiptUnavailable("receipt-release-ref-set-mismatch", source_revision=source_revision)
        changes = name_status(
            repo,
            ["diff", f"{source_revision}..{head}"],
            error="cannot inspect bounded source diff",
        )
        classify_diff(contract, changes, source_revision)
        for commit in bounded_continuation_commits(repo, receipt_commit, head):
            parents = git_text(
                repo,
                ["rev-list", "--parents", "-n", "1", commit],
                error="cannot inspect continuation commit parents",
            ).split()
            if len(parents) != 2 or parents[0] != commit:
                raise ReceiptUnavailable("merge-continuation-requires-full", source_revision=source_revision)
            classify_diff(
                contract,
                name_status(repo, ["diff-tree", "--no-commit-id", "-r", commit], error="cannot inspect continuation commit"),
                source_revision,
            )
        return (
            result_payload(
                "routine-reusable",
                "receipt-valid",
                source_revision=source_revision,
                source_tree=receipt["tree"],
                receipt_commit=receipt_commit,
                reusable_check_ids=REUSABLE_CHECK_IDS,
            ),
            0,
        )
    except ReceiptUnavailable as exc:
        source_revision = exc.source_revision or (receipt["revision"] if receipt else None)
        source_tree = receipt["tree"] if receipt else None
        return (
            result_payload(
                "full-required",
                exc.reason,
                source_revision=source_revision,
                source_tree=source_tree,
                receipt_commit=receipt_commit,
            ),
            FULL_REQUIRED_EXIT,
        )


def refresh_source(
    repo: Path,
    contract: Contract,
    profile: str,
    gates: Sequence[str],
    head_reference: str,
) -> tuple[dict[str, object], int]:
    if profile not in contract.routine_profiles + contract.full_profiles:
        raise ImmutableHistoryError(f"unsupported validation profile: {profile}")
    unsupported_gates = [gate for gate in gates if gate not in contract.full_gates]
    if unsupported_gates:
        raise ImmutableHistoryError("unsupported full-validation gate: " + ",".join(unsupported_gates))
    if worktree_dirty(repo):
        raise ImmutableHistoryError("refresh requires a clean committed source revision")
    source_revision = committed_revision(repo, head_reference)
    if source_revision != committed_revision(repo, "HEAD"):
        raise ImmutableHistoryError("--head must resolve to the checked-out HEAD")

    executed: list[str] = []
    executed_commands: list[list[str]] = []
    executed_timeout_seconds: list[int] = []
    for validator in contract.native_full_validators:
        runtime_command = (sys.executable, *validator.command[1:])
        try:
            result = subprocess.run(
                runtime_command,
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=validator.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise ImmutableHistoryError(
                f"native validator {validator.check_id} timed out after {validator.timeout_seconds} seconds"
            ) from exc
        except OSError as exc:
            raise ImmutableHistoryError(f"native validator {validator.check_id} could not start: {exc}") from exc
        if result.returncode != 0:
            raise ImmutableHistoryError(f"native validator {validator.check_id} failed with exit {result.returncode}")
        executed.append(validator.check_id)
        executed_commands.append(list(runtime_command))
        executed_timeout_seconds.append(validator.timeout_seconds)

    bindings = source_bindings(repo, source_revision, contract, include_release_refs=True)
    write_receipt(repo / contract.receipt_path, receipt_payload(contract, bindings))
    return (
        result_payload(
            "full-refreshed",
            "native-full-validation-passed",
            source_revision=source_revision,
            source_tree=bindings["tree"],
            receipt_commit=None,
            extra={
                "executed_check_ids": executed,
                "executed_commands": executed_commands,
                "executed_timeout_seconds": executed_timeout_seconds,
                "receipt_path": contract.receipt_path,
            },
        ),
        0,
    )


def downstream_result(contract: Contract) -> dict[str, object]:
    return result_payload(
        "downstream-target-local",
        "source-history-receipt-forbidden",
        source_revision=None,
        source_tree=None,
        receipt_commit=None,
        extra={"target_local_validation": list(contract.downstream_target_command)},
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "refresh"))
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository root (default: current directory)")
    parser.add_argument("--contract", type=Path, help="contract path relative to --repo or absolute")
    parser.add_argument("--receipt", type=Path, help="receipt path; must exactly match the contract declaration")
    parser.add_argument("--head", default="HEAD", help="HEAD or an exact 40-character commit SHA (default: HEAD)")
    parser.add_argument("--profile", default="fast", help="validation profile")
    parser.add_argument("--full-gate", action="append", default=[], help="explicit full-validation gate; may be repeated")
    parser.add_argument("--mode", choices=("source", "downstream"), default="source")
    parser.add_argument("--output-format", choices=("json", "tsv"), default="json")
    return parser


def resolve_contract_path(repo: Path, value: Path | None) -> Path:
    canonical_declared = repo / ".ai/distribution/validation/immutable-history-validation.yaml"
    if canonical_declared.is_symlink():
        raise ImmutableHistoryError("--contract and canonical contract must not be symlinks")
    canonical = canonical_declared.resolve()
    supplied = value if value is not None else Path(".ai/distribution/validation/immutable-history-validation.yaml")
    candidate = supplied if supplied.is_absolute() else repo / supplied
    if candidate.is_symlink():
        raise ImmutableHistoryError("--contract and canonical contract must not be symlinks")
    if candidate.resolve() != canonical:
        raise ImmutableHistoryError("--contract must resolve to the canonical immutable-history validation contract")
    if not canonical.is_file():
        raise ImmutableHistoryError("canonical immutable-history validation contract is missing")
    return canonical


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        arguments = parser.parse_args(argv)
        repo = arguments.repo.resolve()
        if not repo.is_dir():
            raise ImmutableHistoryError("--repo must be an existing directory")
        contract = load_contract(resolve_contract_path(repo, arguments.contract))
        if arguments.receipt is not None:
            supplied = arguments.receipt
            if supplied.is_absolute():
                try:
                    supplied = supplied.resolve().relative_to(repo).as_posix()
                except ValueError as exc:
                    raise ImmutableHistoryError("--receipt must remain inside --repo") from exc
            else:
                supplied = safe_relative_path(supplied.as_posix(), "--receipt")
            if supplied != contract.receipt_path:
                raise ImmutableHistoryError("--receipt must exactly match contract.source.receipt.path")
        if arguments.mode == "downstream":
            if arguments.command == "refresh":
                raise ImmutableHistoryError("downstream mode forbids source-history receipt refresh")
            payload, exit_code = downstream_result(contract), 0
        elif arguments.command == "verify":
            payload, exit_code = verify_source(repo, contract, arguments.profile, arguments.full_gate, arguments.head)
        else:
            payload, exit_code = refresh_source(repo, contract, arguments.profile, arguments.full_gate, arguments.head)
    except ImmutableHistoryError as exc:
        payload = result_payload("error", str(exc), source_revision=None, source_tree=None, receipt_commit=None)
        exit_code = ERROR_EXIT
    emit(payload, getattr(arguments, "output_format", "json"))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
