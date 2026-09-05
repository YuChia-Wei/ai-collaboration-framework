#!/usr/bin/env python3
"""Validate the evidence-bound direct route from v0.14.0 into v0.15.0.

This validator is deliberately source-only and self-contained: it reads only
the explicitly named release-local assets, uses the Python standard library,
extracts only into an isolated temporary directory, executes the archive's
declared incoming-candidate validator, and never mutates a target repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


EXPECTED_ARCHIVE_SHA256 = "efd2509f6c869dcadfea7f58fcb942efa9f2c46ab7ae181f4160d47fd4112a92"
EXPECTED_PACKAGE_ID = "ai-collaboration-framework-v0.15.0"
EXPECTED_SOURCE_COMMIT = "5fedaceef7e18b4cdcde3cb665adcc97070db2df"
EXPECTED_TARGET_VERSION = "v0.15.0"
EXPECTED_CUTOVER_ID = "remediation-packet-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SIDECAR_RE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)\n$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

ORIGIN_SPECS = {
    "v0.14.0": {
        "commit": "412bb14a16fe75ee65a020b16680def0acc0ff1b",
        "manifest_sha256": "ac1d4ca062d79e0bc3fbe40ff6762a5022969fe63dbdfa42c74fe3ce369fa1c4",
    },
}


class ValidationError(ValueError):
    """Raised for a closed validation gate."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any, *, newline: bool = False) -> bytes:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + ("\n" if newline else "")).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("JSON object has a duplicate key")
        result[key] = value
    return result


def _reject_json_constant(_value: str) -> None:
    raise ValidationError("JSON uses a non-standard numeric constant")


def strict_json_object(raw: bytes, label: str, *, canonical: bool) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{label} is not UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{label} is not a strict JSON object") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{label} root must be an object")
    if canonical and raw != canonical_json_bytes(value):
        raise ValidationError(f"{label} does not use canonical JSON bytes")
    return value


def release_asset_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_asset_path(value: str, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty relative path")
    if "\\" in value or "\x00" in value:
        raise ValidationError(f"{label} is not a safe POSIX relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValidationError(f"{label} is not a safe POSIX relative path")
    if pure.as_posix() != value:
        raise ValidationError(f"{label} is not a normalized POSIX relative path")
    root = release_asset_root()
    candidate = root.joinpath(*pure.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValidationError(f"{label} does not resolve beneath the release directory") from exc
    if candidate.is_symlink() or not stat.S_ISREG(resolved.stat().st_mode):
        raise ValidationError(f"{label} must name a regular non-symlink file")
    return resolved


def decode_yaml_lines(raw: bytes, label: str) -> list[str]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{label} is not UTF-8 YAML") from exc
    if "\r" in text or "\t" in text or "\x00" in text:
        raise ValidationError(f"{label} uses unsupported YAML whitespace or control bytes")
    if not text.endswith("\n"):
        raise ValidationError(f"{label} must end in one LF")
    return text.splitlines()


def yaml_scalar(raw: str, label: str) -> str:
    if not raw:
        raise ValidationError(f"{label} must have a scalar value")
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise ValidationError(f"{label} has an invalid single-quoted scalar")
        return raw[1:-1].replace("''", "'")
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{label} has an invalid double-quoted scalar") from exc
        if not isinstance(value, str):
            raise ValidationError(f"{label} double-quoted scalar is not a string")
        return value
    if raw.startswith(("[", "{", "&", "*", "!", "|", ">")):
        raise ValidationError(f"{label} uses unsupported YAML scalar syntax")
    return raw


def root_scalar(lines: list[str], key: str, label: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}:(?: (.*))?$")
    values = [match.group(1) for line in lines if (match := pattern.fullmatch(line))]
    if len(values) != 1:
        raise ValidationError(f"{label}.{key} must occur exactly once")
    return yaml_scalar(values[0] or "", f"{label}.{key}")


def root_block(lines: list[str], key: str, label: str) -> list[str]:
    indexes = [index for index, line in enumerate(lines) if line == f"{key}:"]
    if len(indexes) != 1:
        raise ValidationError(f"{label}.{key} block must occur exactly once")
    start = indexes[0] + 1
    result: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith(" ") and not line.startswith("-"):
            break
        result.append(line)
    return result


def block_scalar(lines: list[str], block: str, key: str, label: str) -> str:
    values: list[str | None] = []
    pattern = re.compile(rf"^  {re.escape(key)}:(?: (.*))?$")
    for line in root_block(lines, block, label):
        match = pattern.fullmatch(line)
        if match:
            values.append(match.group(1))
    if len(values) != 1:
        raise ValidationError(f"{label}.{block}.{key} must occur exactly once")
    return yaml_scalar(values[0] or "", f"{label}.{block}.{key}")


def safe_payload_path(value: str, label: str) -> str:
    if not value or "\\" in value or "\x00" in value:
        raise ValidationError(f"{label} is not a safe payload path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValidationError(f"{label} is not a safe payload path")
    if pure.as_posix() != value:
        raise ValidationError(f"{label} is not a normalized payload path")
    return value


def parse_files_manifest(raw: bytes, label: str, expected_package_id: str) -> list[dict[str, Any]]:
    lines = decode_yaml_lines(raw, label)
    if root_scalar(lines, "schema_version", label) != "2.0.0":
        raise ValidationError(f"{label}.schema_version must be 2.0.0")
    if root_scalar(lines, "package_id", label) != expected_package_id:
        raise ValidationError(f"{label}.package_id does not match the requested package")
    block = root_block(lines, "files", label)
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    start_pattern = re.compile(r"^- ([a-z0-9_]+): (.+)$")
    field_pattern = re.compile(r"^  ([a-z0-9_]+): (.+)$")
    allowed = {
        "path",
        "source_path",
        "sha256",
        "size",
        "mode",
        "ownership",
        "install_behavior",
        "entry_id",
        "component_id",
    }
    for line in block:
        if not line:
            continue
        start = start_pattern.fullmatch(line)
        if start:
            if current is not None:
                records.append(current)
            key, value = start.groups()
            if key != "path":
                raise ValidationError(f"{label}.files record must begin with path")
            current = {key: yaml_scalar(value, f"{label}.files.path")}
            continue
        field = field_pattern.fullmatch(line)
        if field and current is not None:
            key, value = field.groups()
            if key not in allowed or key in current:
                raise ValidationError(f"{label}.files record has an invalid field")
            current[key] = yaml_scalar(value, f"{label}.files.{key}")
            continue
        raise ValidationError(f"{label}.files uses unsupported YAML structure")
    if current is not None:
        records.append(current)
    if not records:
        raise ValidationError(f"{label}.files must not be empty")

    required = {
        "path",
        "sha256",
        "size",
        "mode",
        "ownership",
        "install_behavior",
        "component_id",
    }
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not required.issubset(record):
            raise ValidationError(f"{label}.files[{index}] is missing a required field")
        path = safe_payload_path(record["path"], f"{label}.files[{index}].path")
        if path in seen:
            raise ValidationError(f"{label}.files contains a duplicate path")
        seen.add(path)
        digest = record["sha256"]
        if not SHA256_RE.fullmatch(digest):
            raise ValidationError(f"{label}.files[{index}].sha256 is invalid")
        try:
            size = int(record["size"])
        except ValueError as exc:
            raise ValidationError(f"{label}.files[{index}].size is invalid") from exc
        if size < 0:
            raise ValidationError(f"{label}.files[{index}].size is invalid")
        mode = record["mode"]
        if mode not in {"0644", "0755"}:
            raise ValidationError(f"{label}.files[{index}].mode is invalid")
        if not all(record[field] for field in ("ownership", "install_behavior", "component_id")):
            raise ValidationError(f"{label}.files[{index}] has an empty identity field")
        normalized.append(
            {
                "path": path,
                "sha256": digest,
                "size": size,
                "mode": mode,
                "ownership": record["ownership"],
                "install_behavior": record["install_behavior"],
                "component_id": record["component_id"],
            }
        )
    if [item["path"] for item in normalized] != sorted(
        (item["path"] for item in normalized), key=lambda item: item.encode("utf-8")
    ):
        raise ValidationError(f"{label}.files are not ordered deterministically")
    return normalized


def parse_migration(raw: bytes, expected_package_id: str) -> dict[str, Any]:
    label = "internal migration"
    lines = decode_yaml_lines(raw, label)
    if root_scalar(lines, "schema_version", label) != "3.0.0":
        raise ValidationError("internal migration schema must be 3.0.0")
    if root_scalar(lines, "package_id", label) != expected_package_id:
        raise ValidationError("internal migration package identity does not match")
    to_version = block_scalar(lines, "to", "version", label)
    to_manifest_sha256 = block_scalar(lines, "to", "manifest_sha256", label)
    if not VERSION_RE.fullmatch(to_version) or not SHA256_RE.fullmatch(to_manifest_sha256):
        raise ValidationError("internal migration target identity is invalid")

    sources_block = root_block(lines, "sources", label)
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    item_indent: int | None = None
    item_pattern = re.compile(r"^( *)(?:- version: )(.+)$")
    for line in sources_block:
        if not line:
            continue
        item = item_pattern.fullmatch(line)
        if item:
            indent, version = item.groups()
            if item_indent is None:
                item_indent = len(indent)
            if len(indent) != item_indent:
                raise ValidationError("internal migration sources have inconsistent indentation")
            if current is not None:
                records.append(current)
            current = {"version": yaml_scalar(version, "internal migration source version")}
            continue
        if current is not None and item_indent is not None:
            prefix = " " * (item_indent + 2)
            match = re.fullmatch(rf"{re.escape(prefix)}manifest_sha256: (.+)", line)
            if match:
                if "manifest_sha256" in current:
                    raise ValidationError("internal migration source repeats manifest_sha256")
                current["manifest_sha256"] = yaml_scalar(
                    match.group(1), "internal migration source manifest_sha256"
                )
    if current is not None:
        records.append(current)
    if not records:
        raise ValidationError("internal migration sources must not be empty")
    seen_versions: set[str] = set()
    for record in records:
        version = record.get("version")
        digest = record.get("manifest_sha256")
        if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
            raise ValidationError("internal migration source version is invalid")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ValidationError("internal migration source digest is invalid")
        if version in seen_versions:
            raise ValidationError("internal migration has duplicate source versions")
        seen_versions.add(version)
    return {"to_version": to_version, "to_manifest_sha256": to_manifest_sha256, "sources": records}


def parse_package(raw: bytes) -> dict[str, str]:
    label = "internal package"
    lines = decode_yaml_lines(raw, label)
    values = {
        "schema_version": root_scalar(lines, "schema_version", label),
        "package_id": root_scalar(lines, "package_id", label),
        "version": root_scalar(lines, "version", label),
        "release_id": root_scalar(lines, "release_id", label),
        "source_ref": block_scalar(lines, "source", "ref", label),
        "source_commit": block_scalar(lines, "source", "commit", label),
        "files_manifest_digest": block_scalar(lines, "identity", "files_manifest_digest", label),
        "migration_digest": block_scalar(lines, "identity", "migration_digest", label),
        "selected_input_fingerprint": block_scalar(
            lines, "identity", "selected_input_fingerprint", label
        ),
        "payload_fingerprint": block_scalar(lines, "identity", "payload_fingerprint", label),
        "payload_file_count": block_scalar(lines, "payload", "file_count", label),
        "payload_sha256": block_scalar(lines, "payload", "sha256", label),
        "validation_schema_version": block_scalar(lines, "validation", "schema_version", label),
        "validation_manifest": block_scalar(lines, "validation", "manifest", label),
        "validation_manifest_sha256": block_scalar(lines, "validation", "manifest_sha256", label),
        "validation_selected_inputs": block_scalar(lines, "validation", "selected_inputs", label),
        "validation_selected_inputs_sha256": block_scalar(
            lines, "validation", "selected_inputs_sha256", label
        ),
    }
    return values


def safe_zip_members(path: Path) -> dict[str, tuple[bytes, int]]:
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValidationError("archive is not a readable ZIP") from exc
    try:
        if archive.comment:
            raise ValidationError("archive must not have a ZIP comment")
        infos = archive.infolist()
        if not infos or len(infos) > 10000:
            raise ValidationError("archive member count is unsafe")
        members: dict[str, tuple[bytes, int]] = {}
        folded: set[str] = set()
        directories: set[str] = set()
        total_size = 0
        for info in infos:
            name = info.filename
            is_directory = info.is_dir()
            normalized_name = name[:-1] if is_directory and name.endswith("/") else name
            if (
                not name
                or "\\" in name
                or "\x00" in name
                or name.startswith("/")
                or not normalized_name
                or normalized_name != PurePosixPath(normalized_name).as_posix()
            ):
                raise ValidationError("archive has an unsafe member name")
            parts = PurePosixPath(normalized_name).parts
            if not parts or parts[0] != EXPECTED_PACKAGE_ID or any(
                part in {"", ".", ".."} for part in parts
            ):
                raise ValidationError("archive member escapes the expected package envelope")
            if info.flag_bits & 0x1:
                raise ValidationError("archive member encryption is not allowed")
            raw_mode = (info.external_attr >> 16) & 0xFFFF
            if is_directory:
                if (raw_mode & 0o170000) != stat.S_IFDIR:
                    raise ValidationError("archive directory member is not a directory")
                folded_name = normalized_name.casefold()
                if normalized_name in directories or folded_name in folded:
                    raise ValidationError("archive has duplicate or case-colliding directory names")
                directories.add(normalized_name)
                folded.add(folded_name)
                continue
            if len(parts) < 2:
                raise ValidationError("archive file is outside the package envelope")
            relative = "/".join(parts[1:])
            folded_name = normalized_name.casefold()
            if relative in members or folded_name in folded:
                raise ValidationError("archive has duplicate or case-colliding member names")
            if (raw_mode & 0o170000) != stat.S_IFREG:
                raise ValidationError("archive member is not a regular file")
            mode = raw_mode & 0o777
            try:
                content = archive.read(info)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                raise ValidationError("archive member cannot be read safely") from exc
            if len(content) != info.file_size:
                raise ValidationError("archive member size does not match the ZIP header")
            total_size += len(content)
            if total_size > 128 * 1024 * 1024:
                raise ValidationError("archive exceeds the safe uncompressed size limit")
            members[relative] = (content, mode)
            folded.add(folded_name)
    finally:
        archive.close()
    required = {
        "INSTALL.md",
        "requirements.txt",
        "metadata/package.yaml",
        "metadata/files.yaml",
        "metadata/migration.yaml",
        "metadata/SHA256SUMS.txt",
        "metadata/selected-inputs.json",
        "metadata/validation.json",
    }
    missing = sorted(required - set(members))
    if missing:
        raise ValidationError("archive is missing required members")
    return members


def validate_internal_checksum_manifest(members: dict[str, tuple[bytes, int]]) -> None:
    raw = members["metadata/SHA256SUMS.txt"][0]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("internal SHA256SUMS is not UTF-8") from exc
    if "\r" in text or not text.endswith("\n"):
        raise ValidationError("internal SHA256SUMS is not LF-terminated")
    expected: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        if match is None:
            raise ValidationError("internal SHA256SUMS has an invalid record")
        digest, path = match.groups()
        if path in expected or path == "metadata/SHA256SUMS.txt":
            raise ValidationError("internal SHA256SUMS has a duplicate or self record")
        safe_payload_path(path, "internal SHA256SUMS path")
        expected[path] = digest
    actual = {
        path: sha256_bytes(content)
        for path, (content, _mode) in members.items()
        if path != "metadata/SHA256SUMS.txt"
    }
    if expected != actual:
        raise ValidationError("internal SHA256SUMS does not exactly cover archive bytes")


def validate_external_checksum(path: Path, archive: Path, archive_bytes: bytes) -> None:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("external checksum sidecar is not UTF-8") from exc
    match = SIDECAR_RE.fullmatch(text)
    if match is None:
        raise ValidationError("external checksum sidecar must be exactly one sha256sum record")
    digest, filename = match.groups()
    if filename != archive.name or digest != sha256_bytes(archive_bytes):
        raise ValidationError("external checksum sidecar does not bind the archive")


def validate_payload(
    members: dict[str, tuple[bytes, int]], records: list[dict[str, Any]], package: dict[str, str]
) -> list[dict[str, str]]:
    payload_paths = {
        path[len("payload/") :]
        for path in members
        if path.startswith("payload/")
    }
    record_paths = {record["path"] for record in records}
    if payload_paths != record_paths:
        raise ValidationError("payload members and files manifest paths differ")
    selected_projection: list[dict[str, str]] = []
    for record in records:
        content, mode = members[f"payload/{record['path']}"]
        if sha256_bytes(content) != record["sha256"] or len(content) != record["size"]:
            raise ValidationError("payload byte or size does not match files manifest")
        if f"{mode:04o}" != record["mode"]:
            raise ValidationError("payload mode does not match files manifest")
        selected_projection.append(
            {
                "path": record["path"],
                "sha256": record["sha256"],
                "mode": record["mode"],
                "ownership": record["ownership"],
                "install_behavior": record["install_behavior"],
                "component_id": record["component_id"],
            }
        )
    try:
        file_count = int(package["payload_file_count"])
    except ValueError as exc:
        raise ValidationError("package payload file count is invalid") from exc
    payload_digest = sha256_bytes(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in records).encode("utf-8")
    )
    if file_count != len(records) or package["payload_sha256"] != payload_digest:
        raise ValidationError("package payload identity does not match files manifest")
    return selected_projection


def validate_selected_inputs(
    members: dict[str, tuple[bytes, int]],
    package: dict[str, str],
    payload_projection: list[dict[str, str]],
    migration_sources: list[dict[str, str]],
) -> dict[str, Any]:
    selected_raw = members["metadata/selected-inputs.json"][0]
    validation_raw = members["metadata/validation.json"][0]
    selected = strict_json_object(selected_raw, "selected-inputs", canonical=True)
    validation = strict_json_object(validation_raw, "validation", canonical=True)
    if selected.get("schema_version") != "package-selected-input/v1":
        raise ValidationError("selected-inputs schema is invalid")
    if selected.get("payload") != payload_projection:
        raise ValidationError("selected-inputs payload projection differs from files manifest")
    if selected.get("migration_sources") != migration_sources:
        raise ValidationError("selected-inputs migration projection differs from migration.yaml")
    if package["selected_input_fingerprint"] != sha256_bytes(selected_raw):
        raise ValidationError("package selected-input identity does not match selected-inputs bytes")
    if package["validation_schema_version"] != "package-validation/v1":
        raise ValidationError("package validation schema is invalid")
    if package["validation_manifest"] != "metadata/validation.json" or package[
        "validation_manifest_sha256"
    ] != sha256_bytes(validation_raw):
        raise ValidationError("package validation manifest pointer does not match")
    if package["validation_selected_inputs"] != "metadata/selected-inputs.json" or package[
        "validation_selected_inputs_sha256"
    ] != sha256_bytes(selected_raw):
        raise ValidationError("package selected-input pointer does not match")
    if validation.get("schema_version") != "package-validation/v1" or validation.get(
        "selected_input_proof"
    ) != {"path": "metadata/selected-inputs.json", "sha256": sha256_bytes(selected_raw)}:
        raise ValidationError("validation selected-input proof does not match")
    return validation


def execute_portable_validation(
    members: dict[str, tuple[bytes, int]],
    package: dict[str, str],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Execute and record the archive-declared incoming validation authority."""

    if validation.get("package_id") != package["package_id"]:
        raise ValidationError("portable validation package identity does not match")
    authority = validation.get("authority")
    if not isinstance(authority, dict) or set(authority) != {"kind", "validator"}:
        raise ValidationError("portable validation authority is incomplete")
    if authority.get("kind") != "incoming-candidate":
        raise ValidationError("portable validation authority is not incoming-candidate")
    validator = authority.get("validator")
    if not isinstance(validator, dict) or set(validator) != {"argv", "path", "sha256"}:
        raise ValidationError("portable validator identity is incomplete")
    validator_path = safe_payload_path(validator.get("path"), "portable validator path")
    validator_sha256 = validator.get("sha256")
    if not isinstance(validator_sha256, str) or not SHA256_RE.fullmatch(validator_sha256):
        raise ValidationError("portable validator SHA-256 is invalid")
    argv = validator.get("argv")
    expected_argv = ["python", f"payload/{validator_path}", "--package-root", "."]
    if argv != expected_argv:
        raise ValidationError("portable validator argv is not deterministic")
    validator_member = f"payload/{validator_path}"
    validator_bytes = members.get(validator_member)
    if validator_bytes is None or sha256_bytes(validator_bytes[0]) != validator_sha256:
        raise ValidationError("portable validator payload identity differs")

    with tempfile.TemporaryDirectory(prefix="retained-origin-edge-") as temporary:
        package_root = Path(temporary) / EXPECTED_PACKAGE_ID
        for relative, (content, mode) in members.items():
            destination = package_root / Path(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            destination.chmod(mode)
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PYTHONPATH", "PYTHONHOME"}
        }
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONNOUSERSITE"] = "1"
        try:
            result = subprocess.run(
                [sys.executable, *argv[1:]],
                cwd=package_root,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
        except OSError as exc:
            raise ValidationError("portable validator could not start") from exc
        except subprocess.TimeoutExpired as exc:
            raise ValidationError("portable validator timed out") from exc
    output_sha256 = sha256_bytes(
        (result.stdout + "\0" + result.stderr).encode("utf-8")
    )
    if result.returncode != 0:
        raise ValidationError(
            "incoming portable validation failed: "
            f"exit={result.returncode}; output_sha256={output_sha256}"
        )
    return {
        "schema_version": "incoming-package-validation/v1",
        "authority": {
            "kind": "incoming-candidate",
            "manifest": {
                "path": "metadata/validation.json",
                "sha256": sha256_bytes(members["metadata/validation.json"][0]),
            },
            "validator": {
                "path": validator_path,
                "sha256": validator_sha256,
                "argv": argv,
            },
        },
        "package_identity": {
            "package_id": package["package_id"],
            "release_id": package["release_id"],
            "payload_fingerprint": package["payload_fingerprint"],
        },
        "execution": {
            "outcome": "passed",
            "exit_code": 0,
            "output_sha256": output_sha256,
        },
    }


def validate_edge(args: argparse.Namespace) -> dict[str, Any]:
    if args.cutover_id != EXPECTED_CUTOVER_ID:
        raise ValidationError("requested semantic cutover is not the v0.15 cutover")
    origin = args.origin_version
    origin_spec = ORIGIN_SPECS.get(origin)
    if origin_spec is None:
        raise ValidationError("requested origin is not a retained direct-route origin")
    if args.edge_id != f"{origin}-to-{EXPECTED_TARGET_VERSION}":
        raise ValidationError("edge id does not match the requested origin and target")

    archive_path = safe_asset_path(args.archive, "archive")
    checksum_path = safe_asset_path(args.checksum, "checksum")
    target_manifest_path = safe_asset_path(args.target_manifest, "target manifest")
    origin_manifest_path = safe_asset_path(args.origin_manifest, "origin manifest")
    migration_path = safe_asset_path(args.migration, "migration")
    if archive_path.suffix.lower() != ".zip":
        raise ValidationError("archive must be a ZIP file")

    archive_raw = archive_path.read_bytes()
    archive_sha256 = sha256_bytes(archive_raw)
    if archive_sha256 != EXPECTED_ARCHIVE_SHA256:
        raise ValidationError("archive does not match the exact v0.15 release candidate ZIP")
    validate_external_checksum(checksum_path, archive_path, archive_raw)

    members = safe_zip_members(archive_path)
    validate_internal_checksum_manifest(members)
    package_raw = members["metadata/package.yaml"][0]
    files_raw = members["metadata/files.yaml"][0]
    migration_raw = members["metadata/migration.yaml"][0]
    package = parse_package(package_raw)
    if (
        package["schema_version"] != "2.4.0"
        or package["package_id"] != EXPECTED_PACKAGE_ID
        or package["version"] != EXPECTED_TARGET_VERSION[1:]
        or package["release_id"] != f"REL-{EXPECTED_TARGET_VERSION}"
        or package["source_ref"] != EXPECTED_SOURCE_COMMIT
        or package["source_commit"] != EXPECTED_SOURCE_COMMIT
    ):
        raise ValidationError("internal package version or source identity does not match v0.15")
    if not all(
        SHA256_RE.fullmatch(package[key])
        for key in (
            "files_manifest_digest",
            "migration_digest",
            "selected_input_fingerprint",
            "payload_fingerprint",
            "payload_sha256",
        )
    ):
        raise ValidationError("internal package identity digest is invalid")
    if package["files_manifest_digest"] != sha256_bytes(files_raw) or package[
        "migration_digest"
    ] != sha256_bytes(migration_raw):
        raise ValidationError("internal package identity does not match metadata bytes")

    target_manifest_raw = target_manifest_path.read_bytes()
    copied_migration_raw = migration_path.read_bytes()
    if target_manifest_raw != files_raw:
        raise ValidationError("copied target manifest differs from archive metadata/files.yaml")
    if copied_migration_raw != migration_raw:
        raise ValidationError("copied migration differs from archive metadata/migration.yaml")
    records = parse_files_manifest(files_raw, "target files manifest", EXPECTED_PACKAGE_ID)
    migration = parse_migration(migration_raw, EXPECTED_PACKAGE_ID)
    if (
        migration["to_version"] != EXPECTED_TARGET_VERSION[1:]
        or migration["to_manifest_sha256"] != sha256_bytes(files_raw)
    ):
        raise ValidationError("internal migration target does not match target manifest")

    payload_projection = validate_payload(members, records, package)
    if package["payload_fingerprint"] != package["payload_sha256"]:
        raise ValidationError("package payload fingerprints disagree")
    validation = validate_selected_inputs(
        members, package, payload_projection, migration["sources"]
    )
    portable_validation = execute_portable_validation(members, package, validation)

    origin_manifest_raw = origin_manifest_path.read_bytes()
    origin_sha256 = sha256_bytes(origin_manifest_raw)
    if origin_sha256 != origin_spec["manifest_sha256"]:
        raise ValidationError("requested origin manifest does not have its exact retained digest")
    parse_files_manifest(
        origin_manifest_raw,
        f"{origin} files manifest",
        f"ai-context-dotnet-backend-{origin}",
    )
    expected_source = {"version": origin[1:], "manifest_sha256": origin_sha256}
    matching_sources = [source for source in migration["sources"] if source["version"] == origin[1:]]
    if matching_sources != [expected_source]:
        raise ValidationError("internal migration does not contain the exact requested origin source entry")

    return {
        "archive_sha256": archive_sha256,
        "cutover_id": EXPECTED_CUTOVER_ID,
        "edge_id": args.edge_id,
        "from_version": origin,
        "origin_manifest_sha256": origin_sha256,
        "origin_source_commit": origin_spec["commit"],
        "package_id": EXPECTED_PACKAGE_ID,
        "portable_validation": portable_validation,
        "source_commit": EXPECTED_SOURCE_COMMIT,
        "target_manifest_sha256": sha256_bytes(target_manifest_raw),
        "to_version": EXPECTED_TARGET_VERSION,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge-id", required=True)
    parser.add_argument("--origin-version", required=True)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--checksum", required=True)
    parser.add_argument("--target-manifest", required=True)
    parser.add_argument("--origin-manifest", required=True)
    parser.add_argument("--migration", required=True)
    parser.add_argument("--cutover-id", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = validate_edge(args)
    except (OSError, ValidationError, zipfile.BadZipFile) as exc:
        sys.stderr.buffer.write(canonical_json_bytes({"error": str(exc)}, newline=True))
        return 1
    except Exception:
        sys.stderr.buffer.write(canonical_json_bytes({"error": "internal-validator-error"}, newline=True))
        return 1
    sys.stdout.buffer.write(canonical_json_bytes(result, newline=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
