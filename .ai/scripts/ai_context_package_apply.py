#!/usr/bin/env python3
"""Fail-closed planning and application for extracted AI context packages."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Iterator

import yaml

from ai_context_package_validation import (
    PackageValidationError,
    validate_extracted_package,
)
from ai_context_target_provenance import (
    TargetValidationError,
    framework_managed_ignore_message,
    git_ignore_rule,
)


VERSION_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
COMPONENT_PACKAGE_SCHEMAS = {"2.0.0", "2.1.0", "2.2.0", "2.3.0"}
IDENTITY_PACKAGE_SCHEMAS = {"1.1.0", "2.1.0", "2.2.0", "2.3.0"}


class ApplyError(ValueError):
    """A package application safety contract violation."""


DEFAULT_COMPONENT_SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": [
        "software-development-core",
        "ai-context-lifecycle-core",
    ],
    "profiles": ["dotnet-backend"],
    "providers": {
        "repo-backlog": {
            "enabled": False,
            "preservation": "preserve-existing-if-recorded",
        }
    },
}
LEGACY_COMPONENT_SELECTION = deepcopy(DEFAULT_COMPONENT_SELECTION)
LEGACY_COMPONENT_SELECTION["providers"]["repo-backlog"]["enabled"] = True
TARGET_EFFECTIVE_STATE_PATH = ".dev/ai-context/effective-rules.yaml"
TARGET_EFFECTIVE_PACKET_DIRECTORY = ".dev/ai-context/effective-rule-packets"
PENDING_RECEIPT_PATH = ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
APPLY_PLAN_SCHEMA_VERSION = "2.1.0"
PENDING_RECEIPT_SCHEMA_VERSION = "2.0.0"
JOURNAL_SCHEMA_VERSION = "ai-context-package-apply-journal/v3"
TRANSACTION_STATES = {
    "planned",
    "applying",
    "interrupted",
    "rolling-back",
    "rolled-back",
    "finalized",
}
WINDOWS_MOVEFILE_REPLACE_EXISTING = 0x1
WINDOWS_MOVEFILE_WRITE_THROUGH = 0x8
WINDOWS_ATOMIC_REPLACE_FLAGS = (
    WINDOWS_MOVEFILE_REPLACE_EXISTING | WINDOWS_MOVEFILE_WRITE_THROUGH
)


@dataclass(frozen=True)
class FileState:
    exists: bool
    sha256: str | None
    mode: str | None
    git_sha256: str | None = None
    normalized_text_sha256: str | None = None
    tracked: bool = False
    dirty: bool = False
    git_eol_only: bool = False


class InjectedInterruption(BaseException):
    """Deterministic test-only process interruption that bypasses rollback."""


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_digest(value: object) -> str:
    content = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(content)


def deterministic_yaml_bytes(value: object) -> bytes:
    return yaml.dump(
        value,
        Dumper=NoAliasSafeDumper,
        sort_keys=True,
        allow_unicode=True,
    ).encode("utf-8")


def normalized_text_digest(content: bytes) -> str | None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return sha256_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def normalize_version(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ApplyError(f"{label} must be a stable semantic version")
    match = VERSION_RE.fullmatch(value)
    if match is None:
        raise ApplyError(f"{label} must be a stable semantic version")
    return ".".join(match.groups())


def safe_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ApplyError(f"{label} must be a non-empty POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ApplyError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def is_target_effective_rule_path(path: str) -> bool:
    """Keep target-effective state and packets outside framework package control."""
    return (
        path in {TARGET_EFFECTIVE_STATE_PATH, TARGET_EFFECTIVE_PACKET_DIRECTORY}
        or path.startswith(f"{TARGET_EFFECTIVE_PACKET_DIRECTORY}/")
    )


def load_yaml(path: Path, label: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ApplyError(f"{label} root must be a mapping")
    return value


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )


def run_git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True
    )


def clean_target_head(root: Path) -> str:
    if not (root / ".git").exists():
        raise ApplyError("target must be a Git repository")
    head_result = run_git(root, "rev-parse", "--verify", "HEAD^{commit}")
    head = head_result.stdout.strip() if head_result.returncode == 0 else ""
    if len(head) != 40 or any(char not in "0123456789abcdef" for char in head):
        raise ApplyError("target must have a committed HEAD before planning or apply")
    status_result = run_git(root, "status", "--porcelain", "--untracked-files=all")
    if status_result.returncode != 0:
        raise ApplyError("cannot inspect target Git status")
    if status_result.stdout:
        raise ApplyError("target Git worktree must be clean before planning or apply")
    return head


def tracked_mode(root: Path, relative: str) -> str | None:
    result = run_git(root, "ls-files", "--stage", "--", relative)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    modes = {line.split(" ", 1)[0] for line in result.stdout.splitlines() if line}
    if len(modes) != 1:
        raise ApplyError(f"cannot determine one Git mode for {relative}")
    mode = next(iter(modes))
    if mode == "100644":
        return "0644"
    if mode == "100755":
        return "0755"
    raise ApplyError(f"unsupported target Git mode {mode} for {relative}")


def tracked_bytes(root: Path, relative: str) -> bytes | None:
    if tracked_mode(root, relative) is None:
        return None
    result = run_git_bytes(root, "show", f":{relative}")
    if result.returncode != 0:
        raise ApplyError(f"cannot read tracked Git bytes for {relative}")
    return result.stdout


def path_is_dirty(root: Path, relative: str) -> bool:
    result = run_git(root, "status", "--porcelain", "--untracked-files=all", "--", relative)
    if result.returncode != 0:
        raise ApplyError(f"cannot inspect target Git state for {relative}")
    return bool(result.stdout)


def has_no_git_content_transform(root: Path, relative: str) -> bool:
    result = run_git(
        root,
        "check-attr",
        "filter",
        "ident",
        "working-tree-encoding",
        "--",
        relative,
    )
    if result.returncode != 0:
        raise ApplyError(f"cannot inspect target Git attributes for {relative}")
    values = []
    for line in result.stdout.splitlines():
        parts = line.rsplit(": ", 1)
        if len(parts) != 2:
            raise ApplyError(f"cannot parse target Git attributes for {relative}")
        values.append(parts[1])
    return len(values) == 3 and all(value == "unspecified" for value in values)


def filesystem_mode(path: Path) -> str:
    return "0755" if path.stat().st_mode & stat.S_IXUSR else "0644"


def is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, FileNotFoundError):
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def file_state(root: Path, relative: str) -> FileState:
    path = root / Path(*PurePosixPath(relative).parts)
    if not path.exists():
        return FileState(False, None, None)
    if path.is_symlink() or is_reparse_point(path) or not path.is_file():
        raise ApplyError(f"target path must be a regular file: {relative}")
    content = path.read_bytes()
    tracked_git_mode = tracked_mode(root, relative)
    tracked = tracked_git_mode is not None
    dirty = path_is_dirty(root, relative)
    index_content = tracked_bytes(root, relative) if tracked else None
    return FileState(
        True,
        sha256_bytes(content),
        tracked_git_mode if tracked and not dirty else filesystem_mode(path),
        sha256_bytes(index_content) if index_content is not None else None,
        normalized_text_digest(content),
        tracked,
        dirty,
        index_content is not None
        and content != index_content
        and content.replace(b"\r\n", b"\n") == index_content,
    )


def state_record(state: FileState) -> dict:
    return {
        "exists": state.exists,
        "sha256": state.sha256,
        "mode": state.mode,
        "git_sha256": state.git_sha256,
        "normalized_text_sha256": state.normalized_text_sha256,
        "tracked": state.tracked,
        "dirty": state.dirty,
        "git_eol_only": state.git_eol_only,
    }


def reject_symlink_boundary(root: Path, relative: str) -> None:
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink() or is_reparse_point(current):
            raise ApplyError(f"symlink boundary or reparse-point boundary is not allowed: {relative}")


def existing_case_map(root: Path) -> dict[str, str]:
    paths: dict[str, str] = {}
    for directory, names, files in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        if directory_path == root / ".git":
            names[:] = []
            continue
        names[:] = [name for name in names if directory_path / name != root / ".git"]
        for name in [*names, *files]:
            relative = (directory_path / name).relative_to(root).as_posix()
            key = relative.casefold()
            previous = paths.get(key)
            if previous is not None and previous != relative:
                raise ApplyError(f"case-fold collision in target: {previous} and {relative}")
            paths[key] = relative
    return paths


def inventory_records(document: dict, label: str) -> tuple[dict[str, dict], list[str]]:
    schema_version = document.get("schema_version")
    if schema_version not in {"1.0.0", "2.0.0"}:
        raise ApplyError(f"{label} uses unsupported files schema: {schema_version!r}")
    records = document.get("files")
    if not isinstance(records, list):
        raise ApplyError(f"{label} files must be a list")
    output: dict[str, dict] = {}
    case_paths: dict[str, str] = {}
    order: list[str] = []
    for raw in records:
        if not isinstance(raw, dict):
            raise ApplyError(f"{label} file entries must be mappings")
        path = safe_path(raw.get("path"), f"{label} file path")
        if path in output:
            raise ApplyError(f"duplicate {label} path: {path}")
        parts = PurePosixPath(path).parts
        for index in range(1, len(parts) + 1):
            prefix = PurePosixPath(*parts[:index]).as_posix()
            folded = prefix.casefold()
            if folded in case_paths and case_paths[folded] != prefix:
                raise ApplyError(f"case-fold collision in {label}: {case_paths[folded]} and {prefix}")
            case_paths[folded] = prefix
        digest, mode = raw.get("sha256"), raw.get("mode")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ApplyError(f"invalid {label} sha256: {path}")
        if mode not in {"0644", "0755"}:
            raise ApplyError(f"invalid {label} mode: {path}")
        if schema_version == "2.0.0" and (
            not isinstance(raw.get("component_id"), str)
            or not raw["component_id"]
        ):
            raise ApplyError(f"missing {label} component_id: {path}")
        output[path] = raw
        order.append(path)
    if order != sorted(order, key=lambda item: item.encode("utf-8")):
        raise ApplyError(f"{label} paths must use UTF-8 bytewise order")
    return output, order


def validate_component_selection(selection: object, label: str) -> dict:
    if not isinstance(selection, dict):
        raise ApplyError(f"{label} must be a mapping")
    if selection.get("release_model") != "single-versioned-componentized-release":
        raise ApplyError(f"{label}.release_model is invalid")
    mandatory = selection.get("mandatory_components")
    if not isinstance(mandatory, list) or set(mandatory) != {
        "software-development-core",
        "ai-context-lifecycle-core",
    }:
        raise ApplyError(f"{label} must include both mandatory cores")
    if selection.get("profiles") != ["dotnet-backend"]:
        raise ApplyError(f"{label}.profiles must select dotnet-backend")
    providers = selection.get("providers")
    backlog = providers.get("repo-backlog") if isinstance(providers, dict) else None
    if (
        not isinstance(backlog, dict)
        or not isinstance(backlog.get("enabled"), bool)
        or backlog.get("preservation") != "preserve-existing-if-recorded"
        or set(backlog) != {"enabled", "preservation"}
    ):
        raise ApplyError(f"{label}.repo-backlog contract is invalid")
    return selection


def enabled_components(selection: dict) -> set[str]:
    selected = set(selection["mandatory_components"])
    selected.update(selection["profiles"])
    if selection["providers"]["repo-backlog"]["enabled"]:
        selected.add("repo-backlog")
    return selected


def inferred_component(path: str, record: dict | None = None) -> str:
    if isinstance(record, dict):
        component = record.get("component_id")
        if isinstance(component, str) and component:
            return component
        if record.get("entry_id") == "dotnet-validation-tools":
            return "dotnet-backend"
        if record.get("entry_id") in {
            "ai-entry-documents",
            "assessment-governance",
            "public-root-and-catalog-seeds",
        }:
            return "ai-context-lifecycle-core"
    if path.startswith(".dev/backlog/"):
        return "repo-backlog"
    return "software-development-core"


def inventory_schema(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(load_yaml(path, "previous files.yaml").get("schema_version"))


def resolve_effective_selection(
    package: dict,
    target: Path,
    previous_files_path: Path | None,
    enable_providers: Iterable[str] | None,
) -> tuple[dict, dict]:
    requested = sorted(set(enable_providers or []))
    unsupported = [provider for provider in requested if provider != "repo-backlog"]
    if unsupported:
        raise ApplyError(f"unsupported provider selection: {unsupported}")

    new_provenance = target / ".dev/ai-context/provenance.yaml"
    legacy_provenance = target / ".dev/AI-CONTEXT-SOURCE.yaml"
    if new_provenance.is_file() and legacy_provenance.is_file():
        raise ApplyError(
            "legacy and component-aware provenance authorities cannot coexist"
        )

    package_schema = package.get("schema_version")
    default = (
        validate_component_selection(package.get("selection"), "package selection")
        if package_schema in COMPONENT_PACKAGE_SCHEMAS
        else deepcopy(LEGACY_COMPONENT_SELECTION)
    )
    resolved = deepcopy(default)
    if previous_files_path is None:
        if "repo-backlog" in requested:
            resolved["providers"]["repo-backlog"]["enabled"] = True
        return resolved, {
            "source": (
                "explicit-cli-provider"
                if requested
                else (
                    "clean-install-default"
                    if package_schema in COMPONENT_PACKAGE_SCHEMAS
                    else "legacy-package-contract"
                )
            ),
            "evidence": [
                "metadata/package.yaml#selection"
                if package_schema in COMPONENT_PACKAGE_SCHEMAS
                else "legacy-package-schema"
            ]
            + [f"cli:--enable-provider={provider}" for provider in requested],
        }

    if requested:
        raise ApplyError(
            "--enable-provider is a clean-install choice; upgrades use provenance"
        )
    if new_provenance.is_file():
        content = new_provenance.read_bytes()
        provenance = load_yaml(new_provenance, "target provenance")
        resolved = deepcopy(
            validate_component_selection(
                provenance.get("selection"), "target provenance selection"
            )
        )
        return resolved, {
            "source": "target-provenance",
            "evidence": [
                {
                    "path": ".dev/ai-context/provenance.yaml",
                    "sha256": sha256_bytes(content),
                }
            ],
        }

    schema = inventory_schema(previous_files_path)
    if schema == "2.0.0":
        raise ApplyError(
            "component-aware upgrade requires .dev/ai-context/provenance.yaml"
        )
    if schema != "1.0.0":
        raise ApplyError(f"unsupported previous inventory schema: {schema!r}")
    content = previous_files_path.read_bytes()
    records, _ = inventory_records(
        load_yaml(previous_files_path, "previous files.yaml"), "previous inventory"
    )
    backlog_paths = sorted(
        path
        for path in records
        if inferred_component(path, records[path]) == "repo-backlog"
    )
    resolved["providers"]["repo-backlog"]["enabled"] = bool(backlog_paths)
    return resolved, {
        "source": "legacy-schema1-inventory",
        "evidence": [
            {
                "path": str(previous_files_path.resolve()),
                "sha256": sha256_bytes(content),
                "repo_backlog_path_count": len(backlog_paths),
            }
        ],
    }


def filter_component_records(
    records: dict[str, dict], selected: set[str]
) -> dict[str, dict]:
    return {
        path: record
        for path, record in records.items()
        if inferred_component(path, record) in selected
    }


def operation_component(operation: dict) -> str:
    component = operation.get("component_id")
    if isinstance(component, str) and component:
        return component
    return inferred_component(
        str(operation.get("path") or operation.get("from_path") or "")
    )


def count_components(operations: Iterable[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for operation in operations:
        component = operation_component(operation)
        counts[component] = counts.get(component, 0) + 1
    return dict(sorted(counts.items()))


def validate_extracted_checksums(package_root: Path) -> None:
    checksum_path = package_root / "metadata/SHA256SUMS.txt"
    if not checksum_path.is_file() or checksum_path.is_symlink():
        raise ApplyError("missing regular metadata/SHA256SUMS.txt")
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        try:
            digest, relative_value = line.split("  ", 1)
        except ValueError as exc:
            raise ApplyError("invalid SHA256SUMS entry") from exc
        relative = safe_path(relative_value, "SHA256SUMS path")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest) or relative in expected:
            raise ApplyError("invalid or duplicate SHA256SUMS entry")
        expected[relative] = digest
    actual: dict[str, str] = {}
    for directory, names, files in os.walk(package_root, followlinks=False):
        directory_path = Path(directory)
        for name in names:
            candidate = directory_path / name
            if candidate.is_symlink():
                raise ApplyError(f"symlink directory in extracted package: {candidate.relative_to(package_root).as_posix()}")
        for name in files:
            candidate = directory_path / name
            relative = candidate.relative_to(package_root).as_posix()
            if relative == "metadata/SHA256SUMS.txt":
                continue
            if candidate.is_symlink() or not candidate.is_file():
                raise ApplyError(f"non-regular extracted package member: {relative}")
            actual[relative] = sha256_bytes(candidate.read_bytes())
    if actual != expected:
        raise ApplyError("SHA256SUMS does not exactly cover the extracted package")


def validate_package_root(package_root: Path) -> tuple[dict, dict[str, dict], dict, str]:
    package_root = package_root.resolve()
    validate_extracted_checksums(package_root)
    package_path = package_root / "metadata/package.yaml"
    files_path = package_root / "metadata/files.yaml"
    migration_path = package_root / "metadata/migration.yaml"
    for path in (package_path, files_path, migration_path):
        if not path.is_file():
            raise ApplyError(f"missing extracted package metadata: {path.name}")
    package = load_yaml(package_path, "package.yaml")
    files_bytes = files_path.read_bytes()
    migration_bytes = migration_path.read_bytes()
    inventory = load_yaml(files_path, "files.yaml")
    migration = load_yaml(migration_path, "migration.yaml")
    package_id = package.get("package_id")
    if not isinstance(package_id, str) or not package_id:
        raise ApplyError("package.yaml package_id is required")
    if inventory.get("package_id") != package_id or migration.get("package_id") != package_id:
        raise ApplyError("package identity mismatch")
    package_schema = package.get("schema_version")
    if package_schema not in {"1.0.0", "1.1.0", *COMPONENT_PACKAGE_SCHEMAS}:
        raise ApplyError(f"unsupported package schema version: {package_schema!r}")
    if package_schema in COMPONENT_PACKAGE_SCHEMAS:
        selection = package.get("selection")
        if not isinstance(selection, dict):
            raise ApplyError("package selection must be a mapping")
        if migration.get("schema_version") == "3.0.0" and migration.get(
            "selection"
        ) != selection:
            raise ApplyError("package and migration selections must match")
    records, _ = inventory_records(inventory, "incoming inventory")
    for relative, record in records.items():
        payload = package_root / "payload" / Path(*PurePosixPath(relative).parts)
        reject_symlink_boundary(package_root / "payload", relative)
        if not payload.is_file() or payload.is_symlink():
            raise ApplyError(f"missing regular payload file: {relative}")
        content = payload.read_bytes()
        if record["sha256"] != sha256_bytes(content) or record.get("size") != len(content):
            raise ApplyError(f"payload hash or size mismatch: {relative}")
    manifest_sha = sha256_bytes(files_bytes)
    to_data = migration.get("to")
    if not isinstance(to_data, dict) or to_data.get("manifest_sha256") != manifest_sha:
        raise ApplyError("migration target manifest SHA does not match files.yaml")
    if package_schema in IDENTITY_PACKAGE_SCHEMAS:
        source = package.get("source")
        identity = package.get("identity")
        if not isinstance(source, dict) or not all(
            isinstance(source.get(key), str)
            and len(source[key]) == 40
            and all(char in "0123456789abcdef" for char in source[key])
            for key in ("commit", "tree")
        ):
            raise ApplyError("package source identity requires commit and tree SHA")
        if not isinstance(identity, dict) or identity.get("schema_version") != "1.0.0":
            raise ApplyError("package identity schema is missing or unsupported")
        payload_fingerprint = sha256_bytes(
            "".join(
                f"{record['sha256']}  {relative}\n"
                for relative, record in sorted(
                    records.items(), key=lambda item: item[0].encode("utf-8")
                )
            ).encode("utf-8")
        )
        expected_identity = {
            "payload_fingerprint": payload_fingerprint,
            "files_manifest_digest": manifest_sha,
            "migration_digest": sha256_bytes(migration_bytes),
        }
        for key, value in expected_identity.items():
            if identity.get(key) != value:
                raise ApplyError(f"package identity {key} does not match package bytes")
        selected = identity.get("selected_input_fingerprint")
        if not isinstance(selected, str) or len(selected) != 64 or any(
            char not in "0123456789abcdef" for char in selected
        ):
            raise ApplyError("package identity selected_input_fingerprint is invalid")
    if package_schema == "2.3.0":
        try:
            validate_extracted_package(
                package_root,
                run_portable_entrypoints=False,
            )
        except PackageValidationError as exc:
            raise ApplyError(f"portable package validation failed: {exc}") from exc
    return package, records, migration, manifest_sha


def schema_1_migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    from_data = migration.get("from")
    if not isinstance(from_data, dict):
        raise ApplyError("migration from must be a mapping")
    expected = from_data.get("manifest_sha256")
    version = from_data.get("version")
    if expected is None and version is None:
        if path is not None or previous_version_value is not None:
            raise ApplyError("clean install must not supply previous source identity")
        operations = migration.get("operations")
        if not isinstance(operations, list):
            raise ApplyError("migration operations must be a list")
        return {}, operations, None
    if not isinstance(expected, str) or len(expected) != 64 or not isinstance(version, str):
        raise ApplyError("upgrade migration requires previous version and manifest SHA")
    if path is None:
        raise ApplyError("upgrade migration requires --previous-files")
    declared_version = normalize_version(version, "migration source version")
    if (
        previous_version_value is not None
        and normalize_version(previous_version_value, "previous version") != declared_version
    ):
        raise ApplyError("previous version does not match migration.from")
    content = path.read_bytes()
    if sha256_bytes(content) != expected:
        raise ApplyError("previous files manifest SHA does not match migration.from")
    records, _ = inventory_records(load_yaml(path, "previous files.yaml"), "previous inventory")
    operations = migration.get("operations")
    if not isinstance(operations, list):
        raise ApplyError("migration operations must be a list")
    return records, operations, declared_version


def schema_2_migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    clean_install = migration.get("clean_install")
    sources = migration.get("sources")
    if not isinstance(clean_install, dict) or not isinstance(
        clean_install.get("operations"), list
    ):
        raise ApplyError("schema 2 migration clean_install.operations must be a list")
    if not isinstance(sources, list):
        raise ApplyError("schema 2 migration sources must be a list")
    normalized_sources: list[tuple[str, str, list[dict]]] = []
    versions: set[str] = set()
    identities: set[tuple[str, str]] = set()
    for raw in sources:
        if not isinstance(raw, dict):
            raise ApplyError("schema 2 migration sources must be mappings")
        version = normalize_version(raw.get("version"), "migration source version")
        if raw.get("version") != version:
            raise ApplyError("migration source version must omit the v prefix")
        digest = raw.get("manifest_sha256")
        operations = raw.get("operations")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise ApplyError("migration source manifest_sha256 must be lowercase SHA-256")
        if not isinstance(operations, list):
            raise ApplyError("migration source operations must be a list")
        identity = (version, digest)
        if version in versions or identity in identities:
            raise ApplyError(f"duplicate or ambiguous migration source: {version}")
        versions.add(version)
        identities.add(identity)
        normalized_sources.append((version, digest, operations))
    expected_order = sorted(
        normalized_sources,
        key=lambda item: tuple(int(part) for part in item[0].split(".")),
    )
    if normalized_sources != expected_order:
        raise ApplyError("migration sources must use semantic-version order")
    if path is None and previous_version_value is None:
        return {}, clean_install["operations"], None
    if path is None or previous_version_value is None:
        raise ApplyError(
            "schema 2 upgrade requires --previous-version and --previous-files"
        )
    selected_version = normalize_version(previous_version_value, "previous version")
    content = path.read_bytes()
    selected_sha = sha256_bytes(content)
    matches = [
        item
        for item in normalized_sources
        if item[0] == selected_version and item[1] == selected_sha
    ]
    if not matches:
        raise ApplyError(
            "previous version and files manifest SHA do not match a supported migration source"
        )
    if len(matches) != 1:
        raise ApplyError("previous source identity is ambiguous")
    records, _ = inventory_records(
        load_yaml(path, "previous files.yaml"), "previous inventory"
    )
    return records, matches[0][2], selected_version


def migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    schema_version = migration.get("schema_version")
    if schema_version == "1.0.0":
        return schema_1_migration_selection(
            path, previous_version_value, migration
        )
    if schema_version == "2.0.0":
        return schema_2_migration_selection(
            path, previous_version_value, migration
        )
    if schema_version == "3.0.0":
        return schema_2_migration_selection(
            path, previous_version_value, migration
        )
    raise ApplyError(f"unsupported migration schema version: {schema_version!r}")


def state_matches(root: Path, state: FileState, record: dict) -> bool:
    if not state.exists:
        return False
    raw_match = state.sha256 == record.get("sha256")
    canonical_match = (
        state.tracked
        and not state.dirty
        and state.git_eol_only
        and state.git_sha256 == record.get("sha256")
        and state.normalized_text_sha256 == record.get("sha256")
        and isinstance(record.get("path"), str)
        and has_no_git_content_transform(root, record["path"])
    )
    if not raw_match and not canonical_match:
        return False
    if state.mode == record.get("mode"):
        return True
    filemode = run_git(root, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        filemode.stdout.strip() == "false"
        and state.mode == "0644"
        and record.get("mode") == "0755"
    )


def observation(paths: Iterable[str], target: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(set(paths), key=lambda item: item.encode("utf-8")):
        reject_symlink_boundary(target, path)
        state = file_state(target, path)
        result[path] = state_record(state)
    return result


def required_framework_paths(incoming: dict[str, dict]) -> list[dict]:
    """Bind selected framework-managed package bytes to the pending receipt."""
    required: list[dict] = []
    for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
        record = incoming[path]
        if record.get("ownership") != "framework-managed":
            continue
        component_id = record.get("component_id")
        if not isinstance(component_id, str) or not component_id:
            component_id = "legacy-framework-core"
        required.append(
            {
                "path": path,
                "component_id": component_id,
                "ownership": "framework-managed",
                "sha256": record["sha256"],
                "mode": record["mode"],
            }
        )
    return required


def expected_operation_post_states(
    operations: Iterable[dict], incoming: dict[str, dict]
) -> list[dict]:
    """Seal the exact successful state of every active operation path."""
    absent = {"exists": False, "sha256": None, "mode": None}
    result: list[dict] = []
    for operation in operations:
        action = operation.get("action")
        if action not in {"add", "replace", "remove", "rename"}:
            continue
        paths: list[dict] = []
        if action in {"add", "replace", "rename"}:
            relative = operation["path"]
            record = incoming.get(relative)
            if not isinstance(record, dict):
                raise ApplyError(
                    f"active operation destination is absent from incoming inventory: {relative}"
                )
            paths.append(
                {"path": relative, "state": expected_present_state(record)}
            )
        if action == "remove":
            paths.append({"path": operation["path"], "state": absent})
        elif action == "rename":
            paths.append({"path": operation["from_path"], "state": absent})
        result.append({"operation_id": operation["id"], "paths": paths})
    return result


def selected_input_proof_identity(package: dict) -> dict | None:
    if package.get("schema_version") != "2.3.0":
        return None
    validation = package.get("validation")
    if not isinstance(validation, dict):
        raise ApplyError("package validation identity is missing")
    path = validation.get("selected_inputs")
    digest = validation.get("selected_inputs_sha256")
    if path != "metadata/selected-inputs.json" or not isinstance(digest, str) or not re.fullmatch(
        r"[0-9a-f]{64}", digest
    ):
        raise ApplyError("package selected-input proof identity is invalid")
    return {"path": path, "sha256": digest}


def ignored_framework_paths(target: Path, required: list[dict]) -> list[dict]:
    """Expose target-owned Git ignores without choosing an owner disposition."""
    unresolved: list[dict] = []
    for item in required:
        path = item["path"]
        component_id = item["component_id"]
        reject_symlink_boundary(target, path)
        try:
            rule = git_ignore_rule(target, path)
        except TargetValidationError as exc:
            raise ApplyError(str(exc)) from exc
        if rule is None:
            continue
        unresolved.append(
            {
                "path": path,
                "component_id": component_id,
                "ownership": "framework-managed",
                "ignore_rule": rule,
                "owner_dispositions": [
                    "preserve-target-rule",
                    "add-narrow-exception",
                    "disable-component",
                    "pending-owner-decision",
                ],
            }
        )
    return unresolved


def build_plan(
    package_root: Path,
    target_root: Path,
    previous_files_path: Path | None = None,
    previous_version_value: str | None = None,
    enable_providers: Iterable[str] | None = None,
) -> dict:
    target = target_root.resolve()
    head = clean_target_head(target)
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    previous, operations, selected_version = migration_selection(
        previous_files_path,
        previous_version_value,
        migration,
    )
    default_selection = (
        validate_component_selection(package.get("selection"), "package selection")
        if package.get("schema_version") in COMPONENT_PACKAGE_SCHEMAS
        else deepcopy(LEGACY_COMPONENT_SELECTION)
    )
    resolved_selection, selection_resolution = resolve_effective_selection(
        package,
        target,
        previous_files_path,
        enable_providers,
    )
    selected_components = enabled_components(resolved_selection)
    incoming = filter_component_records(incoming, selected_components)
    previous = filter_component_records(previous, selected_components)
    required_paths = required_framework_paths(incoming)
    ignored_paths = ignored_framework_paths(target, required_paths)
    ignored_by_path = {item["path"]: item for item in ignored_paths}
    skipped_by_selection = [
        raw
        for raw in operations
        if isinstance(raw, dict)
        and operation_component(raw) not in selected_components
    ]
    operations = [
        raw
        for raw in operations
        if not isinstance(raw, dict)
        or operation_component(raw) in selected_components
    ]
    ids: set[str] = set()
    touched_paths: dict[str, str] = {}
    operation_paths: list[str] = []
    normalized: list[dict] = []
    case_map = existing_case_map(target)
    for raw in operations:
        if not isinstance(raw, dict):
            raise ApplyError("migration operations must be mappings")
        operation_id, kind, ownership = raw.get("id"), raw.get("kind"), raw.get("ownership")
        component_id = raw.get("component_id")
        if not isinstance(operation_id, str) or not operation_id or operation_id in ids:
            raise ApplyError("migration operation IDs must be unique non-empty strings")
        ids.add(operation_id)
        if migration.get("schema_version") == "3.0.0" and (
            not isinstance(component_id, str) or not component_id
        ):
            raise ApplyError(
                f"schema 3 migration operation requires component_id: {operation_id}"
            )
        if kind not in {"add", "replace", "remove", "rename", "reconcile"}:
            raise ApplyError(f"unsupported migration operation kind: {kind}")
        required_preconditions = {
            "add": {"destination_absent"},
            "replace": {"current_sha256_equals_previous_release"},
            "remove": {"current_sha256_equals_previous_release"},
            "rename": {"source_sha256_equals_previous_release", "destination_absent"},
            "reconcile": {"human_acknowledgement"},
        }[kind]
        preconditions = raw.get("preconditions")
        if not isinstance(preconditions, list) or set(preconditions) != required_preconditions:
            raise ApplyError(f"operation preconditions do not match {kind}: {operation_id}")
        path = safe_path(raw.get("path"), "migration path")
        from_path = safe_path(raw.get("from_path"), "migration from_path") if kind == "rename" else None
        for candidate in [path, from_path]:
            if candidate in {
                ".dev/AI-CONTEXT-SOURCE.yaml",
                ".dev/AI-CONTEXT-APPLY-PENDING.yaml",
                ".dev/ai-context/provenance.yaml",
                ".dev/ai-context/customizations.yaml",
            } or (candidate is not None and is_target_effective_rule_path(candidate)):
                raise ApplyError(
                    f"migration cannot manage provenance, pending receipt, or target effective state: {candidate}"
                )
            if candidate is not None:
                owner = touched_paths.get(candidate)
                if owner is not None:
                    raise ApplyError(f"migration path is touched by multiple operations: {candidate} ({owner}, {operation_id})")
                touched_paths[candidate] = operation_id
        if ownership == "target-template" and kind not in {"add", "reconcile"}:
            raise ApplyError(f"target-template operation is not allowed: {operation_id}")
        if ownership == "target-owned" and kind != "reconcile":
            raise ApplyError(f"target-owned operation is not allowed: {operation_id}")
        if ownership not in {"framework-managed", "target-template", "target-owned"}:
            raise ApplyError(f"invalid operation ownership: {operation_id}")
        operation_paths.extend([path] + ([from_path] if from_path else []))
        for candidate in [path, from_path]:
            if candidate is None:
                continue
            parts = PurePosixPath(candidate).parts
            for index in range(1, len(parts) + 1):
                prefix = PurePosixPath(*parts[:index]).as_posix()
                existing = case_map.get(prefix.casefold())
                if existing is not None and existing != prefix:
                    raise ApplyError(f"case-fold collision for operation path: {existing} and {prefix}")
        normalized.append(
            {
                "id": operation_id,
                "kind": kind,
                "path": path,
                "from_path": from_path,
                "ownership": ownership,
                "component_id": component_id,
            }
        )
    if [item["id"] for item in normalized] != sorted(item["id"] for item in normalized):
        raise ApplyError("migration operations must be ordered by ID")
    destination_paths = {item["path"] for item in normalized if item["kind"] in {"add", "replace", "rename", "reconcile"}}
    source_paths = {item["from_path"] for item in normalized if item["kind"] == "rename"}
    removal_paths = {item["path"] for item in normalized if item["kind"] in {"remove", "reconcile"}}
    for path, record in incoming.items():
        previous_record = previous.get(path)
        unchanged = previous_record is not None and all(
            previous_record.get(key) == record.get(key) for key in ("sha256", "mode", "ownership")
        )
        if not unchanged and path not in destination_paths:
            raise ApplyError(f"changed incoming path has no migration operation: {path}")
    for path, record in previous.items():
        if path in incoming:
            continue
        if path not in removal_paths and path not in source_paths:
            raise ApplyError(f"removed previous path has no migration operation: {path}")
    observed_paths = [*operation_paths, *(item["path"] for item in required_paths)]
    observed = observation(observed_paths, target)
    managed_state_conflicts: list[dict] = []
    for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
        record = incoming[path]
        if record.get("ownership") != "framework-managed" or path not in previous:
            continue
        previous_record = previous[path]
        unchanged = all(
            previous_record.get(key) == record.get(key)
            for key in ("sha256", "mode", "ownership")
        )
        if unchanged and not state_matches(target, FileState(**observed[path]), previous_record):
            managed_state_conflicts.append(
                {
                    "path": path,
                    "component_id": record.get("component_id"),
                    "ownership": "framework-managed",
                    "reason": "selected managed path differs from the unchanged previous release identity",
                    "observed": observed[path],
                    "expected_previous": {
                        "sha256": previous_record["sha256"],
                        "mode": previous_record["mode"],
                    },
                }
            )
    planned: list[dict] = []
    for item in normalized:
        operation_id, kind, path, source = item["id"], item["kind"], item["path"], item["from_path"]
        current = FileState(**observed[path])
        action, reason = kind, "all safety preconditions match"
        if kind == "add":
            if path not in incoming:
                raise ApplyError(f"add destination absent from incoming inventory: {path}")
            if incoming[path].get("ownership") != item["ownership"]:
                raise ApplyError(f"add ownership differs from incoming inventory: {path}")
            if current.exists:
                action, reason = "reconcile", "destination already exists"
        elif kind == "replace":
            if item["ownership"] != "framework-managed" or path not in incoming or path not in previous:
                raise ApplyError(f"replace requires managed incoming and previous records: {path}")
            if incoming[path].get("ownership") != "framework-managed" or previous[path].get("ownership") != "framework-managed":
                raise ApplyError(f"replace inventory ownership must be framework-managed: {path}")
            if not state_matches(target, current, previous[path]):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "remove":
            if item["ownership"] != "framework-managed" or path not in previous:
                raise ApplyError(f"remove requires a previous managed record: {path}")
            if previous[path].get("ownership") != "framework-managed":
                raise ApplyError(f"remove previous ownership must be framework-managed: {path}")
            if not current.exists:
                action, reason = "noop", "path is already absent"
            elif not state_matches(target, current, previous[path]):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "rename":
            if item["ownership"] != "framework-managed" or source not in previous or path not in incoming:
                raise ApplyError(f"rename requires previous source and incoming destination: {operation_id}")
            if previous[source].get("ownership") != "framework-managed" or incoming[path].get("ownership") != "framework-managed":
                raise ApplyError(f"rename inventory ownership must be framework-managed: {operation_id}")
            source_state = FileState(**observed[source])
            if not state_matches(target, source_state, previous[source]):
                action, reason = "reconcile", "rename source hash or mode differs from previous release"
            elif current.exists:
                action, reason = "reconcile", "rename destination already exists"
        else:
            action, reason = "reconcile", "migration explicitly requires reconciliation"
        ignored = ignored_by_path.get(path)
        if ignored is not None:
            action = "unresolved"
            reason = framework_managed_ignore_message(
                path, ignored["component_id"], ignored["ignore_rule"]
            )
        planned.append({**item, "action": action, "reason": reason})
    would_apply = [
        item
        for item in planned
        if item["action"] in {"add", "replace", "remove", "rename"}
    ]
    would_skip = [
        item
        for item in planned
        if item["action"] in {"noop", "reconcile", "unresolved"}
    ]
    plan = {
        "schema_version": APPLY_PLAN_SCHEMA_VERSION,
        "package_id": package["package_id"],
        "package_version": package.get("version"),
        "package_manifest_sha256": manifest_sha,
        "migration_sha256": sha256_bytes(
            (package_root / "metadata/migration.yaml").read_bytes()
        ),
        "package_selected_input_proof": selected_input_proof_identity(package),
        "package_root": str(package_root.resolve()),
        "target_root": str(target),
        "target_starting_commit": head,
        "previous_files": str(previous_files_path.resolve()) if previous_files_path else None,
        "previous_version": selected_version,
        "selection": resolved_selection,
        "selection_default": default_selection,
        "selection_resolution": selection_resolution,
        "selection_request": {
            "enable_providers": sorted(set(enable_providers or [])),
        },
        "component_operation_counts": {
            "would_apply": count_components(would_apply),
            "would_skip": count_components(
                [*would_skip, *skipped_by_selection]
            ),
        },
        "required_framework_paths": required_paths,
        "ignored_framework_paths": ignored_paths,
        "managed_state_conflicts": managed_state_conflicts,
        "observed": observed,
        "operations": planned,
        "operation_post_states": expected_operation_post_states(planned, incoming),
    }
    plan["plan_sha256"] = canonical_digest(plan)
    return plan


def mode_int(mode: str) -> int:
    return 0o755 if mode == "0755" else 0o644


def fsync_directory(path: Path) -> None:
    """Persist a directory entry where the host exposes directory fsync.

    Windows namespace durability is supplied by MoveFileExW with
    MOVEFILE_WRITE_THROUGH at each atomic replacement or removal boundary.
    """
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def windows_move_path(source: Path, destination: Path, flags: int) -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file = kernel32.MoveFileExW
    move_file.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    move_file.restype = wintypes.BOOL
    if not move_file(str(source), str(destination), flags):
        raise ctypes.WinError(ctypes.get_last_error())


def atomic_replace(temporary: Path, destination: Path) -> None:
    if os.name == "nt":
        windows_move_path(temporary, destination, WINDOWS_ATOMIC_REPLACE_FLAGS)
        return
    os.replace(temporary, destination)


def atomic_write_bytes(
    path: Path,
    content: bytes,
    mode: int = 0o644,
    *,
    temporary_path: Path | None = None,
    hook: Callable[[str, dict], None] | None = None,
    boundary_details: dict | None = None,
) -> None:
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError(f"cannot atomically replace symlink or reparse point: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if temporary_path is None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary = Path(temporary_name)
    else:
        temporary = temporary_path
        if temporary.parent != path.parent:
            raise ApplyError(f"atomic staging path must share its destination parent: {path}")
        if temporary.exists() or temporary.is_symlink() or is_reparse_point(temporary):
            raise ApplyError(f"atomic staging path already exists or is unsafe: {temporary}")
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
    preserve_temporary = False
    try:
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            if written <= 0:
                raise ApplyError(f"short write while staging {path}")
            offset += written
        os.fsync(descriptor)
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        if hook is not None:
            invoke_boundary(
                hook,
                "after_target_staging_fsync",
                {**(boundary_details or {}), "staging_path": str(temporary)},
            )
        atomic_replace(temporary, path)
        fsync_directory(path.parent)
    except InjectedInterruption:
        preserve_temporary = True
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists() and not preserve_temporary:
            temporary.unlink()


def atomic_write_yaml(path: Path, value: dict) -> bytes:
    content = deterministic_yaml_bytes(value)
    atomic_write_bytes(path, content)
    return content


def durable_unlink(path: Path, transaction_root_path: Path) -> None:
    if os.name != "nt":
        path.unlink()
        fsync_directory(path.parent)
        return
    tombstone_root = transaction_root_path / "deleted"
    tombstone_root.mkdir(parents=True, exist_ok=True)
    if path.stat().st_dev != tombstone_root.stat().st_dev:
        raise ApplyError(
            f"cannot durably remove a target path across Windows volumes: {path}"
        )
    stem = sha256_bytes(str(path.resolve()).encode("utf-8"))
    index = 0
    while True:
        tombstone = tombstone_root / f"{stem}-{index:04d}.deleted"
        if not tombstone.exists():
            break
        index += 1
    windows_move_path(path, tombstone, WINDOWS_MOVEFILE_WRITE_THROUGH)
    try:
        tombstone.unlink()
    except OSError:
        # The write-through rename already made the governed source path
        # durably absent. A retained Git-admin tombstone is safe to collect
        # after recovery and must not weaken the journal boundary.
        pass


def write_payload(
    package_root: Path,
    target: Path,
    path: str,
    record: dict,
    journal: dict,
    hook: Callable[[str, dict], None] | None,
    boundary_details: dict,
) -> None:
    destination = target / Path(*PurePosixPath(path).parts)
    reject_symlink_boundary(target, path)
    source = package_root / "payload" / Path(*PurePosixPath(path).parts)
    content = source.read_bytes()
    if sha256_bytes(content) != record["sha256"]:
        raise ApplyError(f"package payload changed after validation: {path}")
    atomic_write_bytes(
        destination,
        content,
        mode_int(record["mode"]),
        temporary_path=target_staging_path(target, journal, path),
        hook=hook,
        boundary_details={**boundary_details, "destination": path, "purpose": "apply"},
    )


def plan_digest(plan: dict) -> str:
    unsigned = deepcopy(plan)
    declared = unsigned.pop("plan_sha256", None)
    digest = canonical_digest(unsigned)
    if declared != digest:
        raise ApplyError("apply plan digest is invalid")
    return digest


def transaction_id_for_plan(plan: dict) -> str:
    return plan_digest(plan)


def git_admin_transaction_base(target: Path) -> Path:
    result = run_git(target, "rev-parse", "--path-format=absolute", "--git-path", "ai-context-package-apply")
    if result.returncode != 0:
        result = run_git(target, "rev-parse", "--git-path", "ai-context-package-apply")
    if result.returncode != 0 or not result.stdout.strip():
        raise ApplyError("cannot resolve target Git administrative transaction directory")
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (target / value).resolve()


@contextmanager
def transaction_lock(target: Path) -> Iterator[None]:
    base = git_admin_transaction_base(target)
    base.mkdir(parents=True, exist_ok=True)
    lock_path = base / "transaction.lock"
    handle = lock_path.open("a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ApplyError("another AI context package transaction is active") from exc
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ApplyError("another AI context package transaction is active") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def transaction_root(target: Path, transaction_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        raise ApplyError("transaction ID must be a lowercase SHA-256")
    return git_admin_transaction_base(target) / transaction_id


def active_operations(plan: dict) -> list[dict]:
    return [
        item
        for item in plan.get("operations", [])
        if item.get("action") in {"add", "replace", "remove", "rename"}
    ]


def operation_post_state_map(plan: dict) -> dict[str, dict[str, dict]]:
    operations = active_operations(plan)
    records = plan.get("operation_post_states")
    if not isinstance(records, list) or len(records) != len(operations):
        raise ApplyError("apply plan operation post-state evidence is invalid")
    result: dict[str, dict[str, dict]] = {}
    for operation, record in zip(operations, records, strict=True):
        if not isinstance(record, dict) or record.get("operation_id") != operation["id"]:
            raise ApplyError("apply plan operation post-state order is invalid")
        paths = record.get("paths")
        expected_paths = [operation["path"]]
        if operation["action"] == "rename":
            expected_paths.append(operation["from_path"])
        if not isinstance(paths, list) or [
            item.get("path") if isinstance(item, dict) else None for item in paths
        ] != expected_paths:
            raise ApplyError(
                f"apply plan operation post-state paths are invalid: {operation['id']}"
            )
        by_path: dict[str, dict] = {}
        for item in paths:
            state = item.get("state")
            if not isinstance(state, dict) or set(state) != {
                "exists",
                "sha256",
                "mode",
            }:
                raise ApplyError(
                    f"apply plan operation post-state record is invalid: {operation['id']}"
                )
            if state.get("exists") is True:
                if not isinstance(state.get("sha256"), str) or not re.fullmatch(
                    r"[0-9a-f]{64}", state["sha256"]
                ) or state.get("mode") not in {"0644", "0755"}:
                    raise ApplyError(
                        f"apply plan present post-state identity is invalid: {operation['id']}"
                    )
            elif state.get("exists") is not False or state != {
                "exists": False,
                "sha256": None,
                "mode": None,
            }:
                raise ApplyError(
                    f"apply plan absent post-state identity is invalid: {operation['id']}"
                )
            by_path[item["path"]] = state
        result[operation["id"]] = by_path
    return result


def touched_paths(plan: dict) -> list[str]:
    values: set[str] = set()
    for item in active_operations(plan):
        values.add(item["path"])
        if item.get("from_path"):
            values.add(item["from_path"])
    return sorted(values, key=lambda value: value.encode("utf-8"))


def target_staging_records(plan: dict) -> list[dict[str, str]]:
    """Derive the only target-side staging paths authorized for a transaction."""
    transaction_id = transaction_id_for_plan(plan)
    destinations = set(touched_paths(plan)) | {PENDING_RECEIPT_PATH}
    records: list[dict[str, str]] = []
    staging_paths: set[str] = set()
    for destination in sorted(destinations, key=lambda value: value.encode("utf-8")):
        destination = safe_path(destination, "transaction staging destination")
        destination_path = PurePosixPath(destination)
        digest = sha256_bytes(
            f"{transaction_id}\0{destination}".encode("utf-8")
        )
        staging = (
            destination_path.parent / f".ai-context-apply-{digest}.staging"
        ).as_posix()
        if staging in destinations or staging in staging_paths:
            raise ApplyError("transaction staging path collision")
        staging_paths.add(staging)
        records.append({"destination": destination, "path": staging})
    return records


def target_staging_path(target: Path, journal: dict, destination: str) -> Path:
    records = journal.get("target_staging_paths")
    if not isinstance(records, list):
        raise ApplyError("transaction staging path evidence is invalid")
    matches = [
        item.get("path")
        for item in records
        if isinstance(item, dict) and item.get("destination") == destination
    ]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ApplyError(f"transaction staging path is missing: {destination}")
    staging = matches[0]
    reject_symlink_boundary(target, staging)
    return target / Path(*PurePosixPath(staging).parts)


def require_target_staging_absent(target: Path, records: list[dict[str, str]]) -> None:
    for item in records:
        relative = item["path"]
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.exists() or path.is_symlink() or is_reparse_point(path):
            raise ApplyError(f"transaction staging path already exists or is unsafe: {relative}")


def planned_created_parents(target: Path, plan: dict) -> list[str]:
    parents: set[str] = set()
    destinations = [
        item["path"]
        for item in active_operations(plan)
        if item["action"] in {"add", "replace", "rename"}
    ]
    destinations.append(PENDING_RECEIPT_PATH)
    for relative in destinations:
        parent = PurePosixPath(relative).parent
        lineage: list[PurePosixPath] = []
        while str(parent) not in {"", "."}:
            lineage.append(parent)
            parent = parent.parent
        for candidate in reversed(lineage):
            native = target / Path(*candidate.parts)
            if not native.exists():
                parents.add(candidate.as_posix())
            elif native.is_symlink() or is_reparse_point(native) or not native.is_dir():
                raise ApplyError(f"target parent boundary is unsafe: {candidate.as_posix()}")
    return sorted(parents, key=lambda value: (len(PurePosixPath(value).parts), value.encode("utf-8")))


def protected_target_paths(target: Path) -> list[str]:
    fixed = {
        ".dev/AI-CONTEXT-SOURCE.yaml",
        ".dev/ai-context/provenance.yaml",
        ".dev/ai-context/customizations.yaml",
        ".dev/ai-context/effective-rules.yaml",
    }
    packet_root = target / TARGET_EFFECTIVE_PACKET_DIRECTORY
    if packet_root.exists():
        if packet_root.is_symlink() or is_reparse_point(packet_root) or not packet_root.is_dir():
            raise ApplyError(f"target-owned packet boundary is unsafe: {TARGET_EFFECTIVE_PACKET_DIRECTORY}")
        for candidate in packet_root.rglob("*"):
            if candidate.is_symlink() or is_reparse_point(candidate):
                raise ApplyError(
                    f"target-owned packet boundary is unsafe: {candidate.relative_to(target).as_posix()}"
                )
            if candidate.is_file():
                fixed.add(candidate.relative_to(target).as_posix())
    return sorted(
        (path for path in fixed if (target / Path(*PurePosixPath(path).parts)).exists()),
        key=lambda value: value.encode("utf-8"),
    )


def preflight_writable(target: Path, plan: dict) -> None:
    for relative in touched_paths(plan):
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.exists() and not path.is_file():
            raise ApplyError(f"target path must be a regular file: {relative}")
        if path.exists() and not (path.stat().st_mode & stat.S_IWRITE):
            raise ApplyError(f"target path is read-only: {relative}")
    planned_created_parents(target, plan)
    require_target_staging_absent(target, target_staging_records(plan))


def verify_preparation_admission(target: Path, plan: dict) -> None:
    if clean_target_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed during transaction preparation")
    current_observed = observation(plan.get("observed", {}).keys(), target)
    if current_observed != plan.get("observed"):
        raise ApplyError("target file state changed during transaction preparation")
    require_target_staging_absent(target, target_staging_records(plan))


def verify_package_binding(plan: dict, package_root: Path) -> tuple[dict, dict[str, dict], dict, str]:
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    if manifest_sha != plan.get("package_manifest_sha256"):
        raise ApplyError("package manifest changed after planning")
    if sha256_bytes((package_root / "metadata/migration.yaml").read_bytes()) != plan.get(
        "migration_sha256"
    ):
        raise ApplyError("migration contract changed after planning")
    if selected_input_proof_identity(package) != plan.get("package_selected_input_proof"):
        raise ApplyError("package selected-input proof changed after planning")
    return package, incoming, migration, manifest_sha


def verify_plan_for_apply(
    plan: dict, acknowledgements: set[str]
) -> tuple[dict, dict[str, dict], str, set[str]]:
    if plan.get("schema_version") != APPLY_PLAN_SCHEMA_VERSION:
        raise ApplyError("unsupported apply plan schema")
    plan_digest(plan)
    target = Path(plan["target_root"])
    package_root = Path(plan["package_root"])
    package, incoming, _migration, manifest_sha = verify_package_binding(plan, package_root)
    if clean_target_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed after planning")
    previous_files_value = plan.get("previous_files")
    previous_files = Path(previous_files_value) if previous_files_value else None
    resolved_selection, selection_resolution = resolve_effective_selection(
        package,
        target,
        previous_files,
        plan.get("selection_request", {}).get("enable_providers", []),
    )
    if resolved_selection != plan.get("selection") or selection_resolution != plan.get(
        "selection_resolution"
    ):
        raise ApplyError("selection authority changed after planning")
    incoming = filter_component_records(incoming, enabled_components(resolved_selection))
    required_paths = required_framework_paths(incoming)
    if required_paths != plan.get("required_framework_paths"):
        raise ApplyError("required framework-managed path identity changed after planning")
    operation_post_states = expected_operation_post_states(
        plan.get("operations", []), incoming
    )
    if operation_post_states != plan.get("operation_post_states"):
        raise ApplyError("active operation post-state identity changed after planning")
    current_ignored = ignored_framework_paths(target, required_paths)
    if current_ignored != plan.get("ignored_framework_paths"):
        raise ApplyError("target Git ignore rules changed after planning")
    if current_ignored:
        paths = [item["path"] for item in current_ignored]
        raise ApplyError(
            "unresolved target Git ignore rules for selected framework-managed paths: "
            f"{paths}; owner must choose a recorded disposition before apply"
        )
    current_observed = observation(plan.get("observed", {}).keys(), target)
    if current_observed != plan.get("observed"):
        raise ApplyError("target file state changed after planning")
    conflicts = plan.get("managed_state_conflicts")
    if not isinstance(conflicts, list):
        raise ApplyError("apply plan managed-state conflicts are invalid")
    if conflicts:
        raise ApplyError(
            "selected unchanged framework-managed paths require reconciliation: "
            f"{[item.get('path') for item in conflicts]}"
        )
    reconciles = {item["id"] for item in plan["operations"] if item["action"] == "reconcile"}
    unknown = acknowledgements - reconciles
    if unknown:
        raise ApplyError(f"acknowledgements do not match reconciliation IDs: {sorted(unknown)}")
    missing = reconciles - acknowledgements
    if missing:
        raise ApplyError(f"unacknowledged reconciliation items: {sorted(missing)}")
    receipt_path = target / PENDING_RECEIPT_PATH
    if receipt_path.exists() or receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError(f"pending receipt already exists: {PENDING_RECEIPT_PATH}")
    preflight_writable(target, plan)
    return package, incoming, manifest_sha, reconciles


def prepare_transaction(
    target: Path,
    plan: dict,
    acknowledgements: set[str],
    hook: Callable[[str, dict], None] | None = None,
) -> tuple[Path, dict]:
    transaction_id = transaction_id_for_plan(plan)
    verify_preparation_admission(target, plan)
    root = transaction_root(target, transaction_id)
    if root.exists():
        raise ApplyError(
            f"transaction evidence already exists; resume or roll back {transaction_id}"
        )
    base = root.parent
    preparation = Path(
        tempfile.mkdtemp(prefix=f".{transaction_id}.preparing-", dir=base)
    )
    try:
        invoke_boundary(
            hook, "after_preparation_root", {"transaction_id": transaction_id}
        )
        (preparation / "prestate").mkdir()
        plan_bytes = json.dumps(
            plan,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8") + b"\n"
        atomic_write_bytes(preparation / "plan.json", plan_bytes)
        invoke_boundary(hook, "after_preparation_plan", {"transaction_id": transaction_id})
        pre_state: list[dict] = []
        for index, relative in enumerate(touched_paths(plan)):
            state = file_state(target, relative)
            recorded_state = state_record(state)
            if recorded_state != plan.get("observed", {}).get(relative):
                raise ApplyError(
                    f"target file state changed during transaction preparation: {relative}"
                )
            backup_path = None
            backup_sha = None
            if state.exists:
                content = (target / Path(*PurePosixPath(relative).parts)).read_bytes()
                if sha256_bytes(content) != state.sha256:
                    raise ApplyError(
                        f"target file changed while transaction backup was captured: {relative}"
                    )
                backup_name = (
                    f"{index:04d}-{sha256_bytes(relative.encode('utf-8'))}.bin"
                )
                backup = preparation / "prestate" / backup_name
                atomic_write_bytes(backup, content, mode_int(state.mode or "0644"))
                backup_path = f"prestate/{backup_name}"
                backup_sha = sha256_bytes(content)
            pre_state.append(
                {
                    "path": relative,
                    "state": recorded_state,
                    "backup_path": backup_path,
                    "backup_sha256": backup_sha,
                }
            )
            invoke_boundary(
                hook,
                "after_preparation_backup",
                {"transaction_id": transaction_id, "index": index, "path": relative},
            )
        journal = {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "state": "planned",
            "transition_sequence": 0,
            "plan_sha256": plan["plan_sha256"],
            "operation_order_sha256": canonical_digest(
                [item["id"] for item in active_operations(plan)]
            ),
            "next_apply_index": 0,
            "completed_operation_ids": [],
            "rollback_next_index": 0,
            "rollback_completed_paths": [],
            "rollback_start_state": None,
            "acknowledgements": sorted(acknowledgements),
            "pre_state": pre_state,
            "protected_state": observation(protected_target_paths(target), target),
            "planned_created_parents": planned_created_parents(target, plan),
            "target_staging_paths": target_staging_records(plan),
            "last_error": None,
            "final_receipt_sha256": None,
        }
        verify_preparation_admission(target, plan)
        atomic_write_yaml(preparation / "journal.yaml", journal)
        fsync_directory(preparation)
        invoke_boundary(
            hook, "after_preparation_journal", {"transaction_id": transaction_id}
        )
        verify_preparation_admission(target, plan)
        if root.exists():
            raise ApplyError(
                f"transaction evidence already exists; resume or roll back {transaction_id}"
            )
        atomic_replace(preparation, root)
        fsync_directory(base)
        return root, journal
    except Exception:
        if preparation.exists():
            shutil.rmtree(preparation)
            fsync_directory(base)
        raise


def persist_journal(root: Path, journal: dict) -> None:
    journal["transition_sequence"] = int(journal.get("transition_sequence", 0)) + 1
    atomic_write_yaml(root / "journal.yaml", journal)


def exact_state_matches(target: Path, relative: str, expected: dict) -> bool:
    reject_symlink_boundary(target, relative)
    current = file_state(target, relative)
    return (
        current.exists == expected.get("exists")
        and current.sha256 == expected.get("sha256")
        and current.mode == expected.get("mode")
    )


def expected_present_state(record: dict) -> dict:
    return {"exists": True, "sha256": record["sha256"], "mode": record["mode"]}


def prestate_by_path(journal: dict) -> dict[str, dict]:
    return {item["path"]: item for item in journal["pre_state"]}


def validate_journal_progress(plan: dict, journal: dict) -> None:
    operations = active_operations(plan)
    operation_post_state_map(plan)
    expected_staging = target_staging_records(plan)
    if journal.get("target_staging_paths") != expected_staging:
        raise ApplyError("transaction journal staging path evidence is invalid")
    next_index = journal.get("next_apply_index")
    if type(next_index) is not int or not 0 <= next_index <= len(operations):
        raise ApplyError("transaction journal next operation index is invalid")
    completed = journal.get("completed_operation_ids")
    expected_completed = [item["id"] for item in operations[:next_index]]
    if completed != expected_completed:
        raise ApplyError("transaction journal completed operation prefix is invalid")
    transition_sequence = journal.get("transition_sequence")
    if type(transition_sequence) is not int or transition_sequence < 0:
        raise ApplyError("transaction journal transition sequence is invalid")
    state = journal.get("state")
    rollback_paths = [
        item.get("path")
        for item in reversed(journal.get("pre_state", []))
        if isinstance(item, dict)
    ]
    rollback_next_index = journal.get("rollback_next_index")
    if (
        type(rollback_next_index) is not int
        or not 0 <= rollback_next_index <= len(rollback_paths)
    ):
        raise ApplyError("transaction journal rollback index is invalid")
    rollback_completed = journal.get("rollback_completed_paths")
    if rollback_completed != rollback_paths[:rollback_next_index]:
        raise ApplyError("transaction journal rollback path prefix is invalid")
    rollback_start_state = journal.get("rollback_start_state")
    if state in {"rolling-back", "rolled-back"}:
        if (
            not isinstance(rollback_start_state, dict)
            or list(sorted(rollback_start_state, key=lambda item: item.encode("utf-8")))
            != touched_paths(plan)
        ):
            raise ApplyError("transaction journal rollback start state is invalid")
        for relative, value in rollback_start_state.items():
            if (
                not isinstance(relative, str)
                or not isinstance(value, dict)
                or set(value)
                != {
                    "exists",
                    "sha256",
                    "mode",
                    "git_sha256",
                    "normalized_text_sha256",
                    "tracked",
                    "dirty",
                    "git_eol_only",
                }
            ):
                raise ApplyError("transaction journal rollback start state is invalid")
    elif (
        rollback_next_index != 0
        or rollback_completed != []
        or rollback_start_state is not None
    ):
        raise ApplyError("non-rollback journal contains rollback progress")
    if state == "rolled-back" and rollback_next_index != len(rollback_paths):
        raise ApplyError("rolled-back transaction journal is incomplete")
    receipt_digest = journal.get("final_receipt_sha256")
    if state == "planned" and next_index != 0:
        raise ApplyError("planned transaction journal cannot contain progress")
    if state == "finalized":
        if next_index != len(operations) or not isinstance(
            receipt_digest, str
        ) or not re.fullmatch(r"[0-9a-f]{64}", receipt_digest):
            raise ApplyError("finalized transaction journal is incomplete")
        minimum_sequence = len(operations) + 2
        if (
            transition_sequence < minimum_sequence
            or (transition_sequence - minimum_sequence) % 2 != 0
        ):
            raise ApplyError("finalized transaction transition sequence is impossible")
    elif receipt_digest is not None:
        raise ApplyError("non-finalized transaction journal has a receipt identity")


def transaction_state_matches(
    target: Path, relative: str, expected: dict
) -> bool:
    if expected.get("exists") is not True:
        return exact_state_matches(target, relative, expected)
    reject_symlink_boundary(target, relative)
    current = file_state(target, relative)
    if not current.exists or current.sha256 != expected.get("sha256"):
        return False
    if current.mode == expected.get("mode"):
        return True
    filemode = run_git(target, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        filemode.stdout.strip() == "false"
        and current.mode == "0644"
        and expected.get("mode") == "0755"
    )


def states_match(target: Path, states: dict[str, dict]) -> bool:
    return all(
        transaction_state_matches(target, relative, expected)
        for relative, expected in states.items()
    )


def recorded_transaction_state_matches(
    target: Path, current: dict, expected: dict
) -> bool:
    if current.get("exists") != expected.get("exists"):
        return False
    if current.get("sha256") != expected.get("sha256"):
        return False
    if current.get("mode") == expected.get("mode"):
        return True
    filemode = run_git(target, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        expected.get("exists") is True
        and filemode.stdout.strip() == "false"
        and current.get("mode") == "0644"
        and expected.get("mode") == "0755"
    )


def recorded_states_match(
    target: Path, current: dict[str, dict], expected: dict[str, dict]
) -> bool:
    return all(
        relative in current
        and recorded_transaction_state_matches(target, current[relative], state)
        for relative, state in expected.items()
    )


def operation_pre_states(
    operation: dict, prestate: dict[str, dict]
) -> dict[str, dict]:
    paths = [operation["path"]]
    if operation["action"] == "rename":
        paths.append(operation["from_path"])
    return {relative: prestate[relative]["state"] for relative in paths}


def current_operation_state_matches(
    target: Path,
    operation: dict,
    pre_states: dict[str, dict],
    post_states: dict[str, dict],
) -> bool:
    if states_match(target, pre_states) or states_match(target, post_states):
        return True
    if operation["action"] != "rename":
        return False
    intermediate = {
        operation["path"]: post_states[operation["path"]],
        operation["from_path"]: pre_states[operation["from_path"]],
    }
    return states_match(target, intermediate)


def validate_transaction_surface(target: Path, plan: dict, journal: dict) -> None:
    validate_journal_progress(plan, journal)
    if journal["state"] in {"rolling-back", "rolled-back"}:
        validate_rollback_start_surface(target, plan, journal)
        validate_rollback_surface(target, journal)
        return
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    poststate = operation_post_state_map(plan)
    state = journal["state"]
    next_index = journal["next_apply_index"]
    for index, operation in enumerate(operations):
        before = operation_pre_states(operation, prestate)
        after = poststate[operation["id"]]
        if state in {"planned", "rolled-back"}:
            matches = states_match(target, before)
        elif state == "finalized" or index < next_index:
            matches = states_match(target, after)
        elif index == next_index:
            matches = current_operation_state_matches(
                target, operation, before, after
            )
        else:
            matches = states_match(target, before)
        if not matches:
            raise ApplyError(
                f"target state does not match transaction progress: {operation['id']}"
            )


def validate_rollback_surface(target: Path, journal: dict) -> None:
    prestate = prestate_by_path(journal)
    start_state = journal["rollback_start_state"]
    rollback_paths = [item["path"] for item in reversed(journal["pre_state"])]
    next_index = journal["rollback_next_index"]
    for index, relative in enumerate(rollback_paths):
        before = prestate[relative]["state"]
        started = start_state[relative]
        if journal["state"] == "rolled-back" or index < next_index:
            matches = exact_state_matches(target, relative, before)
        elif index == next_index:
            matches = exact_state_matches(
                target, relative, started
            ) or exact_state_matches(target, relative, before)
        else:
            matches = exact_state_matches(target, relative, started)
        if not matches:
            raise ApplyError(
                f"target state does not match rollback progress: {relative}"
            )


def validate_rollback_start_surface(
    target: Path, plan: dict, journal: dict
) -> None:
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    poststate = operation_post_state_map(plan)
    start_state = journal["rollback_start_state"]
    next_index = journal["next_apply_index"]
    for index, operation in enumerate(operations):
        before = operation_pre_states(operation, prestate)
        after = poststate[operation["id"]]
        if index < next_index:
            matches = recorded_states_match(target, start_state, after)
        elif index > next_index:
            matches = recorded_states_match(target, start_state, before)
        elif recorded_states_match(target, start_state, before) or recorded_states_match(
            target, start_state, after
        ):
            matches = True
        elif operation["action"] == "rename":
            intermediate = {
                operation["path"]: after[operation["path"]],
                operation["from_path"]: before[operation["from_path"]],
            }
            matches = recorded_states_match(target, start_state, intermediate)
        else:
            matches = False
        if not matches:
            raise ApplyError(
                f"rollback start state does not match transaction progress: {operation['id']}"
            )


def invoke_boundary(
    hook: Callable[[str, dict], None] | None, name: str, details: dict
) -> None:
    if hook is not None:
        hook(name, details)


def execute_operation(
    root: Path,
    package_root: Path,
    target: Path,
    incoming: dict[str, dict],
    journal: dict,
    operation: dict,
    index: int,
    prestate: dict[str, dict],
    hook: Callable[[str, dict], None] | None,
) -> None:
    action = operation["action"]
    relative = operation["path"]
    expected = expected_present_state(incoming[relative]) if action in {"add", "replace", "rename"} else None
    if action in {"add", "replace"}:
        if exact_state_matches(target, relative, expected):
            return
        if not exact_state_matches(target, relative, prestate[relative]["state"]):
            raise ApplyError(f"ambiguous transaction state for {relative}")
        write_payload(
            package_root,
            target,
            relative,
            incoming[relative],
            journal,
            hook,
            {"index": index, "operation_id": operation["id"]},
        )
        invoke_boundary(hook, "after_destination_replace", {"index": index, "operation_id": operation["id"]})
        return
    if action == "remove":
        if exact_state_matches(target, relative, {"exists": False, "sha256": None, "mode": None}):
            return
        if not exact_state_matches(target, relative, prestate[relative]["state"]):
            raise ApplyError(f"ambiguous transaction state for {relative}")
        durable_unlink(target / Path(*PurePosixPath(relative).parts), root)
        invoke_boundary(hook, "after_source_remove", {"index": index, "operation_id": operation["id"]})
        return
    if action == "rename":
        source_relative = operation["from_path"]
        source_pre = prestate[source_relative]["state"]
        destination_pre = prestate[relative]["state"]
        source_absent = {"exists": False, "sha256": None, "mode": None}
        source_is_pre = exact_state_matches(target, source_relative, source_pre)
        source_is_absent = exact_state_matches(target, source_relative, source_absent)
        destination_is_pre = exact_state_matches(target, relative, destination_pre)
        destination_is_post = exact_state_matches(target, relative, expected)
        if source_is_absent and destination_is_post:
            return
        if not source_is_pre or not (destination_is_pre or destination_is_post):
            raise ApplyError(f"ambiguous rename transaction state for {source_relative} -> {relative}")
        if destination_is_pre:
            write_payload(
                package_root,
                target,
                relative,
                incoming[relative],
                journal,
                hook,
                {"index": index, "operation_id": operation["id"]},
            )
            invoke_boundary(hook, "after_destination_replace", {"index": index, "operation_id": operation["id"]})
        durable_unlink(target / Path(*PurePosixPath(source_relative).parts), root)
        invoke_boundary(hook, "after_source_remove", {"index": index, "operation_id": operation["id"]})
        return
    raise ApplyError(f"unsupported active operation action: {action}")


def verify_protected_state(target: Path, journal: dict) -> None:
    current = observation(journal.get("protected_state", {}).keys(), target)
    if current != journal.get("protected_state"):
        raise ApplyError("target-owned authority changed during package transaction")


def build_final_receipt(
    plan: dict,
    journal: dict,
    incoming: dict[str, dict],
    reconciles: set[str],
) -> dict:
    target = Path(plan["target_root"])
    if journal.get("next_apply_index") != len(active_operations(plan)):
        raise ApplyError("transaction operations are incomplete before receipt")
    validate_transaction_surface(target, plan, journal)
    artifacts: list[dict] = []
    removed: list[dict] = []
    for item in active_operations(plan):
        if item["action"] in {"add", "replace", "rename"}:
            state = file_state(target, item["path"])
            artifacts.append(
                {
                    "operation_id": item["id"],
                    "path": item["path"],
                    "raw_sha256": state.sha256,
                    "git_mode": incoming[item["path"]]["mode"],
                    "observed_filesystem_mode": state.mode,
                }
            )
        if item["action"] == "remove":
            if file_state(target, item["path"]).exists:
                raise ApplyError(
                    f"removed operation path is still present: {item['path']}"
                )
            removed.append({"operation_id": item["id"], "path": item["path"], "result": "absent"})
        elif item["action"] == "rename":
            if file_state(target, item["from_path"]).exists:
                raise ApplyError(
                    f"renamed operation source is still present: {item['from_path']}"
                )
            removed.append({"operation_id": item["id"], "path": item["from_path"], "result": "absent"})
    results: list[dict] = []
    reconciliation_paths = {
        item["path"] for item in plan["operations"] if item["action"] == "reconcile"
    }
    for item in plan["required_framework_paths"]:
        state = file_state(target, item["path"])
        matches_incoming = state_matches(target, state, item)
        if not matches_incoming and item["path"] not in reconciliation_paths:
            raise ApplyError(f"required framework-managed result differs: {item['path']}")
        results.append(
            {
                "path": item["path"],
                "expected_raw_sha256": item["sha256"],
                "expected_git_mode": item["mode"],
                "observed_raw_sha256": state.sha256,
                "observed_git_mode": item["mode"] if matches_incoming else state.mode,
                "observed_filesystem_mode": state.mode,
                "disposition": "package-identical" if matches_incoming else "reconciliation-preserved",
                "match_basis": (
                    "raw"
                    if state.sha256 == item["sha256"]
                    else "git-eol-canonical"
                    if matches_incoming
                    else "mismatch"
                ),
            }
        )
    return {
        "schema_version": PENDING_RECEIPT_SCHEMA_VERSION,
        "status": "pending-validation",
        "transaction_state": "finalized",
        "transaction_id": journal["transaction_id"],
        "plan_sha256": plan["plan_sha256"],
        "package_id": plan["package_id"],
        "package_version": plan.get("package_version"),
        "package_manifest_sha256": plan["package_manifest_sha256"],
        "migration_sha256": plan["migration_sha256"],
        "selected_input_proof": plan.get("package_selected_input_proof"),
        "target_starting_commit": plan["target_starting_commit"],
        "operation_order": [item["id"] for item in active_operations(plan)],
        "applied_operation_ids": [item["id"] for item in active_operations(plan)],
        "skipped_reconciliation_ids": sorted(reconciles),
        "selection": plan["selection"],
        "selection_default": plan["selection_default"],
        "selection_resolution": plan["selection_resolution"],
        "component_operation_counts": {
            "applied": count_components(active_operations(plan)),
            "skipped": plan["component_operation_counts"]["would_skip"],
        },
        "applied_artifacts": artifacts,
        "removed_paths": removed,
        "required_framework_paths": plan["required_framework_paths"],
        "selected_managed_path_results": results,
        "provenance_updated": False,
    }


def expected_rollback_receipt_bytes(plan: dict, journal: dict) -> bytes:
    """Rebuild the only pending receipt rollback may remove without a package."""
    post_states = operation_post_state_map(plan)
    incoming: dict[str, dict] = {}
    for operation in active_operations(plan):
        if operation["action"] in {"add", "replace", "rename"}:
            state = post_states[operation["id"]][operation["path"]]
            incoming[operation["path"]] = {"mode": state["mode"]}
    reconciles = {
        item["id"] for item in plan["operations"] if item["action"] == "reconcile"
    }
    return deterministic_yaml_bytes(
        build_final_receipt(plan, journal, incoming, reconciles)
    )


def recovery_receipt_path(target: Path) -> Path:
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    receipt_path = target / PENDING_RECEIPT_PATH
    if receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError("unsafe pending receipt blocks recovery")
    if receipt_path.exists() and not receipt_path.is_file():
        raise ApplyError("pending receipt must be a regular file during recovery")
    return receipt_path


def run_transaction(
    root: Path,
    journal: dict,
    plan: dict,
    package_root: Path,
    incoming: dict[str, dict],
    reconciles: set[str],
    hook: Callable[[str, dict], None] | None = None,
) -> dict:
    target = Path(plan["target_root"])
    require_target_staging_absent(target, journal["target_staging_paths"])
    verify_recovery_surface(target, plan, journal)
    admitted_journal = deepcopy(journal)
    admitted_journal["state"] = "applying"
    admitted_journal["last_error"] = None
    persist_journal(root, admitted_journal)
    journal.clear()
    journal.update(admitted_journal)
    invoke_boundary(hook, "after_applying_journal", {"transaction_id": journal["transaction_id"]})
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    for index in range(int(journal["next_apply_index"]), len(operations)):
        verify_recovery_surface(target, plan, journal)
        operation = operations[index]
        execute_operation(
            root,
            package_root,
            target,
            incoming,
            journal,
            operation,
            index,
            prestate,
            hook,
        )
        invoke_boundary(hook, "after_operation", {"index": index, "operation_id": operation["id"]})
        journal["completed_operation_ids"] = [item["id"] for item in operations[: index + 1]]
        journal["next_apply_index"] = index + 1
        persist_journal(root, journal)
        invoke_boundary(
            hook,
            "after_progress_journal",
            {
                "index": index,
                "operation_id": operation["id"],
                "next_apply_index": index + 1,
            },
        )
    verify_recovery_surface(target, plan, journal)
    verify_protected_state(target, journal)
    receipt = build_final_receipt(plan, journal, incoming, reconciles)
    receipt_path = target / PENDING_RECEIPT_PATH
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    expected_bytes = deterministic_yaml_bytes(receipt)
    if receipt_path.exists():
        if receipt_path.is_symlink() or is_reparse_point(receipt_path):
            raise ApplyError("pending receipt is ambiguous after interruption")
        existing_bytes = receipt_path.read_bytes()
        if existing_bytes != expected_bytes:
            try:
                existing_receipt = yaml.safe_load(existing_bytes)
            except yaml.YAMLError as exc:
                raise ApplyError(
                    "pending receipt is ambiguous after interruption"
                ) from exc
            if not isinstance(existing_receipt, dict) or not all(
                isinstance(key, str) for key in existing_receipt
            ):
                raise ApplyError("pending receipt is ambiguous after interruption")
            differing_fields = sorted(
                key
                for key in set(existing_receipt) | set(receipt)
                if existing_receipt.get(key) != receipt.get(key)
            )
            detail = (
                f" fields differ: {differing_fields}"
                if differing_fields
                else " deterministic bytes differ"
            )
            raise ApplyError(
                f"pending receipt is ambiguous after interruption;{detail}"
            )
    else:
        atomic_write_bytes(
            receipt_path,
            expected_bytes,
            temporary_path=target_staging_path(
                target, journal, PENDING_RECEIPT_PATH
            ),
            hook=hook,
            boundary_details={
                "transaction_id": journal["transaction_id"],
                "destination": PENDING_RECEIPT_PATH,
                "purpose": "receipt",
            },
        )
    invoke_boundary(hook, "after_receipt", {"transaction_id": journal["transaction_id"]})
    verify_recovery_surface(target, plan, journal)
    journal["final_receipt_sha256"] = sha256_bytes(expected_bytes)
    journal["state"] = "finalized"
    persist_journal(root, journal)
    invoke_boundary(hook, "after_finalized_journal", {"transaction_id": journal["transaction_id"]})
    return receipt


def load_transaction(target: Path, transaction_id: str) -> tuple[Path, dict, dict]:
    root = transaction_root(target, transaction_id)
    plan_path = root / "plan.json"
    journal_path = root / "journal.yaml"
    if not plan_path.is_file() or plan_path.is_symlink() or not journal_path.is_file() or journal_path.is_symlink():
        raise ApplyError(f"transaction evidence is missing: {transaction_id}")
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError("transaction evidence cannot be parsed") from exc
    if not isinstance(plan, dict) or not isinstance(journal, dict):
        raise ApplyError("transaction evidence must contain mappings")
    if plan.get("schema_version") != APPLY_PLAN_SCHEMA_VERSION:
        raise ApplyError("unsupported transaction apply plan schema")
    if plan_digest(plan) != transaction_id:
        raise ApplyError("transaction plan identity does not match transaction ID")
    plan_target = plan.get("target_root")
    if not isinstance(plan_target, str) or Path(plan_target).resolve() != target.resolve():
        raise ApplyError("transaction target root does not match recovery target")
    if journal.get("schema_version") != JOURNAL_SCHEMA_VERSION:
        raise ApplyError("unsupported transaction journal schema")
    if journal.get("transaction_id") != transaction_id or journal.get("plan_sha256") != transaction_id:
        raise ApplyError("transaction journal identity is invalid")
    if journal.get("state") not in TRANSACTION_STATES:
        raise ApplyError("transaction journal state is invalid")
    if journal.get("operation_order_sha256") != canonical_digest(
        [item["id"] for item in active_operations(plan)]
    ):
        raise ApplyError("transaction operation order changed")
    pre_state = journal.get("pre_state")
    if not isinstance(pre_state, list) or [item.get("path") for item in pre_state] != touched_paths(plan):
        raise ApplyError("transaction pre-state path set is invalid")
    for item in pre_state:
        state = item.get("state")
        if not isinstance(state, dict):
            raise ApplyError("transaction pre-state record is invalid")
        if state.get("exists"):
            backup_value = item.get("backup_path")
            backup = root / str(backup_value)
            if not isinstance(backup_value, str) or not backup.is_file() or backup.is_symlink():
                raise ApplyError(f"transaction backup is missing: {item.get('path')}")
            if sha256_bytes(backup.read_bytes()) != item.get("backup_sha256") or item.get("backup_sha256") != state.get("sha256"):
                raise ApplyError(f"transaction backup identity differs: {item.get('path')}")
        elif item.get("backup_path") is not None or item.get("backup_sha256") is not None:
            raise ApplyError(f"absent pre-state has a backup: {item.get('path')}")
    validate_journal_progress(plan, journal)
    return root, plan, journal


def changed_target_paths(target: Path) -> set[str]:
    changed: set[str] = set()
    for arguments in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        result = run_git_bytes(target, *arguments)
        if result.returncode != 0:
            raise ApplyError("cannot inspect recovery worktree state")
        changed.update(
            value.decode("utf-8", errors="surrogateescape")
            for value in result.stdout.split(b"\0")
            if value
        )
    return changed


def cleanup_transaction_staging(
    target: Path, root: Path, plan: dict, journal: dict
) -> None:
    expected = target_staging_records(plan)
    if journal.get("target_staging_paths") != expected:
        raise ApplyError("transaction journal staging path evidence is invalid")
    for item in expected:
        relative = item["path"]
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.is_symlink() or is_reparse_point(path):
            raise ApplyError(f"transaction staging path is unsafe: {relative}")
        if not path.exists():
            continue
        if not path.is_file():
            raise ApplyError(f"transaction staging path is not a regular file: {relative}")
        durable_unlink(path, root)


def verify_recovery_surface(
    target: Path,
    plan: dict,
    journal: dict,
    *,
    allow_target_staging: bool = False,
) -> None:
    if run_git(target, "rev-parse", "HEAD").stdout.strip() != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed after transaction planning")
    allowed = set(touched_paths(plan)) | {PENDING_RECEIPT_PATH}
    if allow_target_staging:
        expected_staging = target_staging_records(plan)
        if journal.get("target_staging_paths") != expected_staging:
            raise ApplyError("transaction journal staging path evidence is invalid")
        allowed.update(item["path"] for item in expected_staging)
    unrelated = changed_target_paths(target) - allowed
    if unrelated:
        raise ApplyError(f"unrelated target changes block recovery: {sorted(unrelated)}")
    verify_protected_state(target, journal)
    validate_transaction_surface(target, plan, journal)


def rollback_loaded_transaction(
    root: Path,
    plan: dict,
    journal: dict,
    hook: Callable[[str, dict], None] | None = None,
) -> dict:
    target = Path(plan["target_root"])
    receipt_path = recovery_receipt_path(target)
    if journal["state"] == "rolled-back":
        if not all(exact_state_matches(target, item["path"], item["state"]) for item in journal["pre_state"]):
            raise ApplyError("rolled-back transaction no longer matches its exact pre-state")
        if receipt_path.exists():
            raise ApplyError("rolled-back transaction still has a pending receipt")
        return journal
    if journal["state"] == "finalized":
        raise ApplyError("finalized transaction cannot be rolled back")
    validate_transaction_surface(target, plan, journal)
    if receipt_path.exists():
        reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
        if journal["state"] == "rolling-back":
            raise ApplyError("rolling-back transaction still has a pending receipt")
        expected_receipt = expected_rollback_receipt_bytes(plan, journal)
        if receipt_path.read_bytes() != expected_receipt:
            raise ApplyError("pending receipt does not match rollback transaction")
        reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
        durable_unlink(receipt_path, root)
    rollback_items = list(reversed(journal["pre_state"]))
    if journal["state"] != "rolling-back":
        journal["state"] = "rolling-back"
        journal["last_error"] = None
        journal["rollback_next_index"] = 0
        journal["rollback_completed_paths"] = []
        journal["rollback_start_state"] = observation(touched_paths(plan), target)
        persist_journal(root, journal)
        invoke_boundary(
            hook,
            "after_rollback_start_journal",
            {"transaction_id": journal["transaction_id"]},
        )
    for index in range(journal["rollback_next_index"], len(rollback_items)):
        verify_recovery_surface(target, plan, journal)
        item = rollback_items[index]
        relative = item["path"]
        path = target / Path(*PurePosixPath(relative).parts)
        if exact_state_matches(target, relative, item["state"]):
            pass
        elif item["state"]["exists"]:
            backup = root / item["backup_path"]
            atomic_write_bytes(
                path,
                backup.read_bytes(),
                mode_int(item["state"]["mode"]),
                temporary_path=target_staging_path(target, journal, relative),
                hook=hook,
                boundary_details={
                    "transaction_id": journal["transaction_id"],
                    "destination": relative,
                    "purpose": "rollback",
                },
            )
        elif path.exists():
            durable_unlink(path, root)
        invoke_boundary(hook, "after_rollback_restore", {"path": relative})
        journal["rollback_next_index"] = index + 1
        journal["rollback_completed_paths"] = [
            record["path"] for record in rollback_items[: index + 1]
        ]
        persist_journal(root, journal)
        invoke_boundary(
            hook,
            "after_rollback_progress_journal",
            {"index": index, "path": relative},
        )
    for relative in reversed(journal.get("planned_created_parents", [])):
        directory = target / Path(*PurePosixPath(relative).parts)
        if directory.exists() and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
            fsync_directory(directory.parent)
    if not all(exact_state_matches(target, item["path"], item["state"]) for item in journal["pre_state"]):
        raise ApplyError("rollback did not restore the exact transaction pre-state")
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    if receipt_path.exists() or receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError("rollback did not remove the pending receipt boundary")
    journal["state"] = "rolled-back"
    journal["last_error"] = None
    persist_journal(root, journal)
    invoke_boundary(hook, "after_rollback_journal", {"transaction_id": journal["transaction_id"]})
    return journal


def recover_transaction(
    target: Path,
    transaction_id: str,
    action: str,
    package_root: Path | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    if action not in {"resume", "rollback"}:
        raise ApplyError("recovery action must be resume or rollback")
    with transaction_lock(target):
        root, plan, journal = load_transaction(target, transaction_id)
        verify_recovery_surface(
            target, plan, journal, allow_target_staging=True
        )
        receipt_path = recovery_receipt_path(target)
        reconciles = {
            item["id"] for item in plan["operations"] if item["action"] == "reconcile"
        }
        if action == "rollback" and journal["state"] == "finalized":
            raise ApplyError("finalized transaction cannot be rolled back")
        if action == "rollback" and receipt_path.exists():
            if journal["state"] == "rolling-back":
                raise ApplyError("rolling-back transaction still has a pending receipt")
            if journal["state"] == "rolled-back":
                raise ApplyError("rolled-back transaction still has a pending receipt")
            if receipt_path.read_bytes() != expected_rollback_receipt_bytes(
                plan, journal
            ):
                raise ApplyError("pending receipt does not match rollback transaction")
        if action == "resume" and journal["state"] in {"rolling-back", "rolled-back"}:
            raise ApplyError(
                f"{journal['state']} transaction cannot be resumed"
            )
        incoming: dict[str, dict] | None = None
        if action == "resume":
            if package_root is None:
                raise ApplyError("resume requires the exact extracted package root")
            _package, incoming, _migration, _manifest_sha = verify_package_binding(
                plan, package_root
            )
            incoming = filter_component_records(
                incoming, enabled_components(plan["selection"])
            )
            if journal["state"] == "finalized" and not receipt_path.is_file():
                raise ApplyError("finalized transaction receipt identity differs")
            if receipt_path.exists():
                if (
                    journal["state"] not in {"applying", "interrupted", "finalized"}
                    or journal["next_apply_index"] != len(active_operations(plan))
                ):
                    raise ApplyError("pending receipt is ambiguous after interruption")
                expected_receipt = build_final_receipt(
                    plan, journal, incoming, reconciles
                )
                expected_receipt_bytes = deterministic_yaml_bytes(expected_receipt)
                if receipt_path.read_bytes() != expected_receipt_bytes:
                    raise ApplyError("pending receipt is ambiguous after interruption")
                if (
                    journal["state"] == "finalized"
                    and sha256_bytes(expected_receipt_bytes)
                    != journal.get("final_receipt_sha256")
                ):
                    raise ApplyError("finalized transaction receipt identity differs")
        verify_recovery_surface(
            target, plan, journal, allow_target_staging=True
        )
        cleanup_transaction_staging(target, root, plan, journal)
        verify_recovery_surface(target, plan, journal)
        if action == "rollback":
            return rollback_loaded_transaction(root, plan, journal, boundary_hook)
        if journal["state"] == "applying":
            journal["state"] = "interrupted"
            journal["last_error"] = "recovered an abandoned applying state"
            persist_journal(root, journal)
        if journal["state"] == "finalized":
            if not receipt_path.is_file() or sha256_bytes(receipt_path.read_bytes()) != journal.get("final_receipt_sha256"):
                raise ApplyError("finalized transaction receipt identity differs")
            receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            if not isinstance(receipt, dict):
                raise ApplyError("finalized transaction receipt is invalid")
            return receipt
        if incoming is None:
            raise ApplyError("resume package binding is unavailable")
        return run_transaction(
            root, journal, plan, package_root, incoming, reconciles, boundary_hook
        )


def apply_plan(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    acknowledgements = acknowledgements or set()
    target = Path(plan["target_root"])
    package_root = Path(plan["package_root"])
    with transaction_lock(target):
        _package, incoming, _manifest_sha, reconciles = verify_plan_for_apply(
            plan, acknowledgements
        )
        root, journal = prepare_transaction(
            target, plan, acknowledgements, boundary_hook
        )
        invoke_boundary(
            boundary_hook,
            "after_planned_journal",
            {"transaction_id": journal["transaction_id"]},
        )
        try:
            return run_transaction(
                root,
                journal,
                plan,
                package_root,
                incoming,
                reconciles,
                boundary_hook,
            )
        except Exception as exc:
            if journal["state"] == "planned":
                raise ApplyError(
                    f"package apply rejected before target mutation; recover transaction {journal['transaction_id']}: {exc}"
                ) from exc
            journal["state"] = "interrupted"
            journal["last_error"] = str(exc)
            persist_journal(root, journal)
            try:
                rollback_loaded_transaction(root, plan, journal, boundary_hook)
            except Exception as rollback_exc:
                if journal["state"] == "rolling-back":
                    journal["last_error"] = (
                        f"{exc}; rollback failed: {rollback_exc}"
                    )
                    persist_journal(root, journal)
                raise ApplyError(
                    f"package apply interrupted and rollback failed; recover transaction {journal['transaction_id']}: {rollback_exc}"
                ) from exc
            raise ApplyError(
                f"package apply rolled back transaction {journal['transaction_id']}: {exc}"
            ) from exc
