#!/usr/bin/env python3
"""Portable, fail-closed validation for an extracted AI-context package."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CHECKSUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)$")
EXPECTED_VALIDATOR_PATH = ".ai/scripts/validate-ai-context-payload.py"
ENTRYPOINT_REGISTRY_PATH = ".ai/scripts/python-entrypoints.json"
EXPECTED_VALIDATOR_ARGV = [
    "python",
    "payload/.ai/scripts/validate-ai-context-payload.py",
    "--package-root",
    ".",
]


class PackageValidationError(ValueError):
    """The extracted incoming package does not satisfy its portable contract."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise PackageValidationError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _fail(message: str) -> None:
    raise PackageValidationError(message)


def _safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty POSIX relative path")
    if "\\" in value:
        _fail(f"{label} must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        _fail(f"{label} is not a safe relative path: {value!r}")
    if path.as_posix() != value:
        _fail(f"{label} is not normalized: {value!r}")
    return value


def _path_under(root: Path, relative: str, label: str) -> Path:
    _safe_relative_path(relative, label)
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    try:
        candidate.relative_to(root)
    except ValueError as exc:  # Defensive: PurePosix validation above should prevent this.
        raise PackageValidationError(f"{label} escapes package root") from exc
    return candidate


def _require_mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        _fail(f"{label} must be a mapping with string keys")
    return value


def _require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{label} must be a list")
    return value


def _read_regular(path: Path, label: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        _fail(f"{label} must be a regular non-symlink file: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PackageValidationError(f"cannot read {label}: {path}") from exc


def _load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        document = yaml.load(_read_regular(path, label), Loader=_UniqueKeyLoader)
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise PackageValidationError(f"invalid {label} YAML") from exc
    return _require_mapping(document, label)


def _reject_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise PackageValidationError(f"duplicate JSON key: {key!r}")
        document[key] = value
    return document


def _load_json_object(content: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            content.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_pairs
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"invalid {label} JSON") from exc
    return _require_mapping(value, label)


def _validate_json_value(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        _fail(f"{label} must not contain floating-point values")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{label}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                _fail(f"{label} contains a non-string JSON key")
            _validate_json_value(item, f"{label}.{key}")
        return
    _fail(f"{label} contains an unsupported JSON value")


def canonical_json_bytes(document: dict[str, Any]) -> bytes:
    """Encode the package's selected-input proof canonical JSON bytes."""

    _validate_json_value(document, "canonical JSON")
    return json.dumps(
        document, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _walk_regular_files(root: Path) -> dict[str, Path]:
    if not root.is_dir() or root.is_symlink():
        _fail(f"package root must be a regular directory: {root}")
    files: dict[str, Path] = {}

    def walk(current: Path) -> None:
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.encode("utf-8"))
        except OSError as exc:
            raise PackageValidationError(f"cannot enumerate package path: {current}") from exc
        for child in children:
            relative = child.relative_to(root).as_posix()
            _safe_relative_path(relative, "extracted envelope path")
            if child.is_symlink():
                _fail(f"extracted envelope contains a symlink: {relative}")
            if child.is_dir():
                walk(child)
            elif child.is_file():
                if relative in files:
                    _fail(f"duplicate extracted envelope path: {relative}")
                files[relative] = child
            else:
                _fail(f"extracted envelope contains a non-regular member: {relative}")

    walk(root)
    _require_casefold_unique(files, "extracted envelope paths")
    return files


def _require_casefold_unique(paths: object, label: str) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        if not isinstance(path, str):
            _fail(f"{label} contain a non-string path")
        folded = path.casefold()
        previous = seen.get(folded)
        if previous is not None and previous != path:
            _fail(f"{label} have a case-fold collision: {previous!r} and {path!r}")
        seen[folded] = path


def _parse_checksums(content: bytes) -> dict[str, str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageValidationError("SHA256SUMS.txt is not UTF-8") from exc
    if not text.endswith("\n") or text.endswith("\n\n") or "\r" in text:
        _fail("SHA256SUMS.txt must use LF and exactly one terminal LF")
    records: dict[str, str] = {}
    for index, line in enumerate(text.splitlines(), 1):
        match = CHECKSUM_LINE_RE.fullmatch(line)
        if match is None:
            _fail(f"invalid SHA256SUMS line {index}")
        digest, relative = match.groups()
        _safe_relative_path(relative, f"SHA256SUMS line {index} path")
        if relative == "metadata/SHA256SUMS.txt":
            _fail("SHA256SUMS.txt must not checksum itself")
        if relative in records:
            _fail(f"duplicate SHA256SUMS entry: {relative}")
        records[relative] = digest
    _require_casefold_unique(records, "SHA256SUMS paths")
    return records


def _validate_checksum_coverage(package_root: Path) -> dict[str, Path]:
    files = _walk_regular_files(package_root)
    sums_path = "metadata/SHA256SUMS.txt"
    if sums_path not in files:
        _fail("missing metadata/SHA256SUMS.txt")
    checksums = _parse_checksums(_read_regular(files[sums_path], sums_path))
    expected_paths = set(files) - {sums_path}
    if set(checksums) != expected_paths:
        missing = sorted(expected_paths - set(checksums), key=lambda item: item.encode("utf-8"))
        extra = sorted(set(checksums) - expected_paths, key=lambda item: item.encode("utf-8"))
        _fail(f"SHA256SUMS coverage mismatch: missing={missing!r}; extra={extra!r}")
    for relative, expected in checksums.items():
        actual = _sha256(_read_regular(files[relative], relative))
        if actual != expected:
            _fail(f"SHA256SUMS digest mismatch: {relative}")
    return files


def _record_paths(records: list[Any], label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(records):
        record = _require_mapping(raw, f"{label}[{index}]")
        path = _safe_relative_path(record.get("path"), f"{label}[{index}].path")
        if path in indexed:
            _fail(f"duplicate {label} path: {path}")
        indexed[path] = record
    _require_casefold_unique(indexed, label)
    return indexed


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty string")
    return value


def _validate_inventory(
    package_root: Path, files: dict[str, Path], inventory: dict[str, Any], package_id: str
) -> dict[str, dict[str, Any]]:
    if inventory.get("schema_version") != "2.0.0":
        _fail("files.yaml must use schema 2.0.0")
    if inventory.get("package_id") != package_id:
        _fail("files.yaml package_id does not match package.yaml")
    records = _record_paths(_require_list(inventory.get("files"), "files.yaml files"), "files.yaml files")
    if list(records) != sorted(records, key=lambda item: item.encode("utf-8")):
        _fail("files.yaml files must be ordered by UTF-8 path")
    for relative, record in records.items():
        required = ("sha256", "size", "mode", "ownership", "install_behavior", "component_id")
        if not all(key in record for key in required):
            _fail(f"files.yaml record is incomplete: {relative}")
        if not _is_sha256(record["sha256"]):
            _fail(f"files.yaml record has invalid sha256: {relative}")
        if not isinstance(record["size"], int) or isinstance(record["size"], bool) or record["size"] < 0:
            _fail(f"files.yaml record has invalid size: {relative}")
        if record["mode"] not in {"0644", "0755"}:
            _fail(f"files.yaml record has invalid mode: {relative}")
        for key in ("ownership", "install_behavior", "component_id"):
            _require_string(record[key], f"files.yaml record {key}: {relative}")
        envelope_path = f"payload/{relative}"
        payload = files.get(envelope_path)
        if payload is None:
            _fail(f"payload file is missing from extracted envelope: {relative}")
        content = _read_regular(payload, envelope_path)
        if _sha256(content) != record["sha256"] or len(content) != record["size"]:
            _fail(f"payload digest or size does not match files.yaml: {relative}")
    actual_payload = {
        relative.removeprefix("payload/")
        for relative in files
        if relative.startswith("payload/")
    }
    if set(records) != actual_payload:
        _fail("payload paths and files.yaml paths differ")
    return records


def _payload_fingerprint(records: dict[str, dict[str, Any]]) -> str:
    content = "".join(
        f"{record['sha256']}  {path}\n"
        for path, record in sorted(records.items(), key=lambda item: item[0].encode("utf-8"))
    ).encode("utf-8")
    return _sha256(content)


def _validate_package_identity(
    package: dict[str, Any],
    files_bytes: bytes,
    migration_bytes: bytes,
    records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    identity = _require_mapping(package.get("identity"), "package.yaml identity")
    if identity.get("schema_version") != "1.0.0":
        _fail("package.yaml identity must use schema 1.0.0")
    expected = {
        "payload_fingerprint": _payload_fingerprint(records),
        "files_manifest_digest": _sha256(files_bytes),
        "migration_digest": _sha256(migration_bytes),
    }
    for key, digest in expected.items():
        if identity.get(key) != digest:
            _fail(f"package identity {key} does not match package bytes")
    payload = _require_mapping(package.get("payload"), "package.yaml payload")
    if (
        payload.get("root") != "payload"
        or payload.get("file_count") != len(records)
        or payload.get("sha256") != expected["payload_fingerprint"]
    ):
        _fail("package payload identity does not match files.yaml")
    return identity


def _validate_validation_manifest(
    package_root: Path,
    files: dict[str, Path],
    package: dict[str, Any],
    package_id: str,
    identity: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    package_validation = _require_mapping(package.get("validation"), "package.yaml validation")
    manifest_path = _safe_relative_path(
        package_validation.get("manifest"), "package.yaml validation manifest"
    )
    proof_path = _safe_relative_path(
        package_validation.get("selected_inputs"), "package.yaml validation selected_inputs"
    )
    if manifest_path != "metadata/validation.json" or proof_path != "metadata/selected-inputs.json":
        _fail("package.yaml validation paths are not the package-validation/v1 paths")
    manifest_bytes = _read_regular(
        _path_under(package_root, manifest_path, "validation manifest"), manifest_path
    )
    proof_bytes = _read_regular(
        _path_under(package_root, proof_path, "selected inputs proof"), proof_path
    )
    if files.get(manifest_path) is None or files.get(proof_path) is None:
        _fail("validation metadata is not part of the checksummed envelope")
    if package_validation.get("manifest_sha256") != _sha256(manifest_bytes):
        _fail("package.yaml validation manifest_sha256 does not match validation.json")
    if package_validation.get("selected_inputs_sha256") != _sha256(proof_bytes):
        _fail("package.yaml validation selected_inputs_sha256 does not match selected-inputs.json")
    validation = _load_json_object(manifest_bytes, "validation.json")
    proof = _load_json_object(proof_bytes, "selected-inputs.json")
    if canonical_json_bytes(validation) != manifest_bytes:
        _fail("validation.json is not canonical compact sorted JSON bytes")
    if validation.get("schema_version") != "package-validation/v1":
        _fail("validation.json must use schema package-validation/v1")
    if validation.get("package_id") != package_id:
        _fail("validation.json package_id does not match package.yaml")
    selected = _require_mapping(
        validation.get("selected_input_proof"), "validation.json selected_input_proof"
    )
    if selected.get("path") != proof_path or selected.get("sha256") != _sha256(proof_bytes):
        _fail("validation.json selected-input proof identity does not match package bytes")
    if identity.get("selected_input_fingerprint") != _sha256(proof_bytes):
        _fail("package identity selected_input_fingerprint does not match selected-inputs.json")
    if proof.get("schema_version") != "package-selected-input/v1":
        _fail("selected-inputs.json must use schema package-selected-input/v1")
    if canonical_json_bytes(proof) != proof_bytes:
        _fail("selected-inputs.json is not canonical compact sorted JSON bytes")
    return validation, proof, proof_bytes


def _validate_ordered_records(
    records: list[Any], label: str, key: str = "path"
) -> list[dict[str, Any]]:
    parsed = [_require_mapping(item, f"{label}[{index}]") for index, item in enumerate(records)]
    values = [_require_string(item.get(key), f"{label}[{index}].{key}") for index, item in enumerate(parsed)]
    if len(values) != len(set(values)):
        _fail(f"{label} contain duplicate {key} values")
    if values != sorted(values, key=lambda item: item.encode("utf-8")):
        _fail(f"{label} must be ordered by UTF-8 {key}")
    return parsed


def _validate_selected_input_proof(
    proof: dict[str, Any],
    identity: dict[str, Any],
    records: dict[str, dict[str, Any]],
    migration: dict[str, Any],
) -> None:
    source_inputs = _validate_ordered_records(
        _require_list(proof.get("source_inputs"), "selected-input source_inputs"),
        "selected-input source_inputs",
    )
    for index, source in enumerate(source_inputs):
        _safe_relative_path(source.get("path"), f"selected-input source_inputs[{index}].path")
        if not _is_sha256(source.get("sha256")) or set(source) != {"path", "sha256"}:
            _fail(f"selected-input source_inputs[{index}] is invalid")
    payload = _validate_ordered_records(
        _require_list(proof.get("payload"), "selected-input payload"), "selected-input payload"
    )
    proof_paths = [item["path"] for item in payload]
    _require_casefold_unique(proof_paths, "selected-input payload paths")
    expected_fields = {
        "path",
        "sha256",
        "mode",
        "ownership",
        "install_behavior",
        "component_id",
    }
    if set(proof_paths) != set(records):
        _fail("selected-input payload paths do not exactly match files.yaml")
    for item in payload:
        path = _safe_relative_path(item.get("path"), "selected-input payload path")
        if set(item) != expected_fields:
            _fail(f"selected-input payload record has unexpected fields: {path}")
        if not _is_sha256(item.get("sha256")) or item.get("mode") not in {"0644", "0755"}:
            _fail(f"selected-input payload record has invalid identity: {path}")
        for key in ("ownership", "install_behavior", "component_id"):
            _require_string(item.get(key), f"selected-input payload {key}: {path}")
        expected = records[path]
        for key in expected_fields - {"path"}:
            if item[key] != expected[key]:
                _fail(f"selected-input payload record differs from files.yaml: {path}")
    migration_sources = _require_list(
        proof.get("migration_sources"), "selected-input migration_sources"
    )
    expected_sources: list[dict[str, str]] = []
    for index, raw in enumerate(_require_list(migration.get("sources"), "migration.yaml sources")):
        source = _require_mapping(raw, f"migration.yaml sources[{index}]")
        version = _require_string(source.get("version"), f"migration.yaml sources[{index}].version")
        digest = source.get("manifest_sha256")
        if not _is_sha256(digest):
            _fail(f"migration.yaml sources[{index}] has invalid manifest_sha256")
        expected_sources.append({"version": version, "manifest_sha256": digest})
    if migration_sources != expected_sources:
        _fail("selected-input migration_sources do not exactly match migration.yaml")
    if not _is_sha256(identity.get("selected_input_fingerprint")):
        _fail("package identity selected_input_fingerprint is invalid")


def _validate_validator_identity(
    package_root: Path, validation: dict[str, Any]
) -> None:
    authority = _require_mapping(validation.get("authority"), "validation.json authority")
    if authority.get("kind") != "incoming-candidate":
        _fail("validation.json authority kind must be incoming-candidate")
    validator = _require_mapping(authority.get("validator"), "validation.json authority validator")
    if validator.get("path") != EXPECTED_VALIDATOR_PATH:
        _fail("validation.json validator path is not the portable incoming validator")
    if validator.get("argv") != EXPECTED_VALIDATOR_ARGV:
        _fail("validation.json validator argv is not deterministic")
    validator_path = _path_under(
        package_root, f"payload/{EXPECTED_VALIDATOR_PATH}", "portable validator"
    )
    content = _read_regular(validator_path, "portable validator")
    if validator.get("sha256") != _sha256(content):
        _fail("validation.json validator sha256 does not match payload bytes")


def _validate_source_only_tests(validation: dict[str, Any], records: dict[str, dict[str, Any]]) -> None:
    source_only = _require_mapping(validation.get("source_only_tests"), "validation.json source_only_tests")
    if (
        source_only.get("classification") != "source-only"
        or source_only.get("contributes_to_portable_success") is not False
    ):
        _fail("source-only tests must be classified source-only and excluded from portable success")
    patterns = _require_list(source_only.get("patterns"), "source-only test patterns")
    if not patterns or not all(isinstance(item, str) and item for item in patterns):
        _fail("source-only test patterns must be a non-empty string list")
    for relative in records:
        if any(PurePosixPath(relative).match(pattern) for pattern in patterns):
            _fail(f"source-only test is present in payload: {relative}")


def _validate_integrity_policy(
    package_root: Path,
    validation: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> None:
    policy = _require_mapping(validation.get("integrity_policy"), "validation.json integrity_policy")
    if policy.get("path_case") != "casefold-unique":
        _fail("integrity policy must require casefold-unique paths")
    if policy.get("payload_text") != "all":
        _fail("integrity policy must validate the complete payload as text")
    text = _require_mapping(policy.get("text"), "integrity policy text")
    if text.get("encoding") != "utf-8" or text.get("line_endings") != "lf-only" or text.get("terminal_lf") != "exactly-one":
        _fail("integrity policy text requirements are weakened or unsupported")
    modes = _require_mapping(policy.get("modes"), "integrity policy modes")
    if modes.get("allowed") != ["0644", "0755"]:
        _fail("integrity policy modes must allow exactly 0644 and 0755")
    _require_casefold_unique(records, "payload paths")
    for relative, record in records.items():
        if record["mode"] not in {"0644", "0755"}:
            _fail(f"payload record has unsupported mode: {relative}")
        content = _read_regular(
            _path_under(package_root, f"payload/{relative}", "payload text"),
            f"payload/{relative}",
        )
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageValidationError(f"payload text is not UTF-8: {relative}") from exc
        if b"\r" in content:
            _fail(f"payload text is not LF-only: {relative}")
        if not content.endswith(b"\n") or content.endswith(b"\n\n"):
            _fail(f"payload text must have exactly one terminal LF: {relative}")


def _validate_portable_entrypoints(
    package_root: Path,
    records: dict[str, dict[str, Any]],
    *,
    run: bool,
) -> int:
    registry_path = _path_under(
        package_root, f"payload/{ENTRYPOINT_REGISTRY_PATH}", "portable entrypoint registry"
    )
    registry = _load_json_object(_read_regular(registry_path, "portable entrypoint registry"), "portable entrypoint registry")
    if registry.get("schema_version") != "1.0":
        _fail("portable entrypoint registry must use schema 1.0")
    entrypoints = _require_list(registry.get("entrypoints"), "portable entrypoint registry entrypoints")
    all_paths: set[str] = set()
    portable: list[str] = []
    source_only: list[str] = []
    for index, raw in enumerate(entrypoints):
        entrypoint = _require_mapping(raw, f"portable entrypoint registry entrypoints[{index}]")
        relative = _safe_relative_path(entrypoint.get("path"), f"portable entrypoint registry entrypoints[{index}].path")
        if relative in all_paths:
            _fail(f"duplicate portable entrypoint registry path: {relative}")
        all_paths.add(relative)
        if not isinstance(entrypoint.get("portable"), bool):
            _fail(f"portable entrypoint registry portable flag is invalid: {relative}")
        (portable if entrypoint["portable"] else source_only).append(relative)
    _require_casefold_unique(all_paths, "portable entrypoint registry paths")
    for relative in portable:
        if relative not in records:
            _fail(f"portable entrypoint is absent from payload: {relative}")
    for relative in source_only:
        if relative in records:
            _fail(f"source-only entrypoint is present in payload: {relative}")
    if not run:
        return 0
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    for relative in portable:
        command = [
            sys.executable,
            str(_path_under(package_root, f"payload/{relative}", "portable entrypoint")),
            "--help",
        ]
        try:
            result = subprocess.run(
                command,
                cwd=package_root,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False,
            )
        except OSError as exc:
            raise PackageValidationError(f"cannot execute portable entrypoint: {relative}") from exc
        except subprocess.TimeoutExpired as exc:
            raise PackageValidationError(f"portable entrypoint timed out: {relative}") from exc
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            _fail(
                f"portable entrypoint --help failed: {relative}; exit={result.returncode}; "
                f"output={output[:1000]!r}"
            )
    return len(portable)


def validate_extracted_package(
    package_root: Path, *, run_portable_entrypoints: bool = True
) -> dict[str, object]:
    """Validate one freshly extracted schema-2.3.0 package without source-repo reads."""

    package_root = package_root.resolve()
    files = _validate_checksum_coverage(package_root)
    required = {
        "metadata/package.yaml",
        "metadata/files.yaml",
        "metadata/migration.yaml",
        "metadata/validation.json",
        "metadata/selected-inputs.json",
    }
    missing = sorted(required - set(files), key=lambda item: item.encode("utf-8"))
    if missing:
        _fail(f"missing required package metadata: {missing!r}")
    package_path = files["metadata/package.yaml"]
    files_path = files["metadata/files.yaml"]
    migration_path = files["metadata/migration.yaml"]
    package = _load_yaml_mapping(package_path, "package.yaml")
    inventory = _load_yaml_mapping(files_path, "files.yaml")
    migration = _load_yaml_mapping(migration_path, "migration.yaml")
    if package.get("schema_version") != "2.3.0":
        _fail("package.yaml must use schema 2.3.0")
    package_id = _require_string(package.get("package_id"), "package.yaml package_id")
    if migration.get("package_id") != package_id:
        _fail("migration.yaml package_id does not match package.yaml")
    records = _validate_inventory(package_root, files, inventory, package_id)
    files_bytes = _read_regular(files_path, "files.yaml")
    migration_bytes = _read_regular(migration_path, "migration.yaml")
    identity = _validate_package_identity(package, files_bytes, migration_bytes, records)
    validation, proof, _ = _validate_validation_manifest(
        package_root, files, package, package_id, identity
    )
    _validate_selected_input_proof(proof, identity, records, migration)
    _validate_validator_identity(package_root, validation)
    _validate_source_only_tests(validation, records)
    _validate_integrity_policy(package_root, validation, records)
    portable_verified = _validate_portable_entrypoints(
        package_root, records, run=run_portable_entrypoints
    )
    return {
        "package_id": package_id,
        "payload_file_count": len(records),
        "portable_entrypoints_verified": portable_verified,
        "portable_entrypoints_execution": "executed" if run_portable_entrypoints else "skipped",
        "source_only_tests": "excluded-from-portable-validation",
    }
