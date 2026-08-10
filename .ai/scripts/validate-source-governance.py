#!/usr/bin/env python3
"""Run source-repository governance manifests from a stable registry."""

from __future__ import annotations

import re
import sys
from pathlib import Path, PurePosixPath

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-source-governance.py")

import subprocess
import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / ".ai/distribution/governance-checks.yaml"
DISPOSITION_VALIDATOR = ROOT / ".ai/scripts/validate-file-disposition-manifest.py"
IDENTITY_VALIDATOR = ROOT / ".ai/scripts/validate-repository-identity.py"
SOURCE_DISPOSITION_VALIDATOR = ROOT / ".ai/scripts/validate-source-dispositions.py"
REGISTRY_SCHEMA_VERSION = "1.3"
CURRENT_BYTE_AUTHORIZATION_SCHEMA_VERSION = "1.0"
SHA1 = re.compile(r"^[0-9a-f]{40}$")
ISSUE_178_AUTHORIZED_AT = "2026-08-09T16:37:38Z"
ISSUE_178_AUTHORIZATION_REF = (
    "https://github.com/YuChia-Wei/ai-collaboration-framework/issues/178"
    "#issuecomment-5232583247"
)
REGISTRY_KEYS = {
    "schema_version",
    "manifests",
    "repository_identity_policies",
    "source_disposition_contracts",
}
MANIFEST_RECORD_KEYS = {"id", "path", "current_byte_authorizations"}
MANIFEST_RECORD_REQUIRED_KEYS = {"id", "path"}
IDENTITY_POLICY_RECORD_KEYS = {"id", "path"}
SOURCE_DISPOSITION_RECORD_KEYS = {"id", "path"}
AUTHORIZATION_KEYS = {
    "schema_version",
    "authorization_id",
    "base_manifest",
    "authority",
    "issue",
    "authorized_at",
    "authorization_ref",
    "workflow_ref",
    "task_ref",
    "entries",
}
BASE_MANIFEST_KEYS = {"id", "path", "blob", "subject_commit"}
AUTHORIZATION_ENTRY_KEYS = {"path", "subject_blob", "authorized_blob", "reason"}


def valid_repo_file(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith(("/", "./")) or value.endswith("/"):
        return False
    path = PurePosixPath(value)
    return ".." not in path.parts and not any(
        marker in value for marker in ("*", "?", "[", "]", "{", "}")
    )


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def sha1(value: object) -> bool:
    return isinstance(value, str) and bool(SHA1.fullmatch(value))


def load_registry_paths() -> tuple[
    list[tuple[str, str, list[str]]],
    list[str],
    list[str],
]:
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load source governance registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise RuntimeError(
            "source governance registry schema_version must be "
            f"{REGISTRY_SCHEMA_VERSION}"
        )
    unknown_registry_keys = sorted(set(data) - REGISTRY_KEYS)
    if unknown_registry_keys:
        raise RuntimeError(
            "source governance registry has unknown fields: "
            f"{unknown_registry_keys}"
        )
    ids: set[str] = set()
    all_paths: set[str] = set()

    def load_group(
        key: str,
        label: str,
        *,
        allowed_record_keys: set[str],
        required_record_keys: set[str],
    ) -> list[dict]:
        records = data.get(key)
        if not isinstance(records, list) or not records:
            raise RuntimeError(f"source governance registry {key} must be non-empty")
        records_out: list[dict] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise RuntimeError(f"{key}[{index}] must be a mapping")
            unknown_record_keys = sorted(set(record) - allowed_record_keys)
            if unknown_record_keys:
                raise RuntimeError(
                    f"{key}[{index}] has unknown fields: {unknown_record_keys}"
                )
            missing_record_keys = sorted(required_record_keys - set(record))
            if missing_record_keys:
                raise RuntimeError(
                    f"{key}[{index}] is missing fields: {missing_record_keys}"
                )
            record_id = record.get("id")
            path = record.get("path")
            if not isinstance(record_id, str) or not record_id:
                raise RuntimeError(f"{key}[{index}].id must be a non-empty string")
            if record_id in ids:
                raise RuntimeError(f"duplicate source governance id: {record_id}")
            ids.add(record_id)
            if not valid_repo_file(path):
                raise RuntimeError(f"{key}[{index}].path must be a repository-relative file")
            if path in all_paths:
                raise RuntimeError(f"duplicate source governance path: {path}")
            all_paths.add(path)
            if not (ROOT / path).is_file():
                raise RuntimeError(f"source governance {label} does not exist: {path}")
            if key == "manifests":
                authorization_paths = record.get("current_byte_authorizations", [])
                if "current_byte_authorizations" in record:
                    if not isinstance(authorization_paths, list) or not authorization_paths:
                        raise RuntimeError(
                            f"{key}[{index}].current_byte_authorizations must be a non-empty list"
                        )
                    for authorization_path in authorization_paths:
                        if not valid_repo_file(authorization_path):
                            raise RuntimeError(
                                f"{key}[{index}].current_byte_authorizations must contain "
                                "exact repository-relative files"
                            )
                    if len(authorization_paths) != len(set(authorization_paths)):
                        raise RuntimeError(
                            f"{key}[{index}].current_byte_authorizations must not contain duplicates"
                        )
                    for authorization_path in authorization_paths:
                        if authorization_path in all_paths:
                            raise RuntimeError(
                                "duplicate source governance path: "
                                f"{authorization_path}"
                            )
                        all_paths.add(authorization_path)
                        if not (ROOT / authorization_path).is_file():
                            raise RuntimeError(
                                "source governance current byte authorization does not exist: "
                                f"{authorization_path}"
                            )
            records_out.append(record)
        return records_out

    manifests = load_group(
        "manifests",
        "manifest",
        allowed_record_keys=MANIFEST_RECORD_KEYS,
        required_record_keys=MANIFEST_RECORD_REQUIRED_KEYS,
    )
    identity_policies = load_group(
        "repository_identity_policies",
        "repository identity policy",
        allowed_record_keys=IDENTITY_POLICY_RECORD_KEYS,
        required_record_keys=IDENTITY_POLICY_RECORD_KEYS,
    )
    source_disposition_contracts = load_group(
        "source_disposition_contracts",
        "source disposition contract",
        allowed_record_keys=SOURCE_DISPOSITION_RECORD_KEYS,
        required_record_keys=SOURCE_DISPOSITION_RECORD_KEYS,
    )
    return (
        [
            (
                record["id"],
                record["path"],
                record.get("current_byte_authorizations", []),
            )
            for record in manifests
        ],
        [record["path"] for record in identity_policies],
        [record["path"] for record in source_disposition_contracts],
    )


def authorization_validation_errors(
    data: object,
    *,
    manifest_id: str,
    manifest_path: str,
    manifest_blob: str,
    subject_commit: str,
    candidates: set[str],
    subject_blobs: dict[str, str],
    current_blobs: dict[str, str],
) -> list[str]:
    """Validate one all-or-nothing source-only current-byte authorization."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["current byte authorization root must be a mapping"]
    unknown_keys = sorted(set(data) - AUTHORIZATION_KEYS)
    if unknown_keys:
        errors.append(f"current byte authorization has unknown fields: {unknown_keys}")
    missing_keys = sorted(AUTHORIZATION_KEYS - set(data))
    if missing_keys:
        errors.append(f"current byte authorization is missing fields: {missing_keys}")
    if data.get("schema_version") != CURRENT_BYTE_AUTHORIZATION_SCHEMA_VERSION:
        errors.append(
            "current byte authorization schema_version must be "
            f"{CURRENT_BYTE_AUTHORIZATION_SCHEMA_VERSION}"
        )
    if not isinstance(data.get("authorization_id"), str) or not data["authorization_id"].strip():
        errors.append("current byte authorization authorization_id must be a non-empty string")
    base_manifest = data.get("base_manifest")
    if not isinstance(base_manifest, dict):
        errors.append("current byte authorization base_manifest must be a mapping")
    else:
        unknown_base_keys = sorted(set(base_manifest) - BASE_MANIFEST_KEYS)
        missing_base_keys = sorted(BASE_MANIFEST_KEYS - set(base_manifest))
        if unknown_base_keys:
            errors.append(
                f"current byte authorization base_manifest has unknown fields: {unknown_base_keys}"
            )
        if missing_base_keys:
            errors.append(
                f"current byte authorization base_manifest is missing fields: {missing_base_keys}"
            )
        expected_base = {
            "id": manifest_id,
            "path": manifest_path,
            "blob": manifest_blob,
            "subject_commit": subject_commit,
        }
        for field, expected in expected_base.items():
            if base_manifest.get(field) != expected:
                errors.append(
                    "current byte authorization base_manifest."
                    f"{field} does not bind to the registered manifest"
                )
    if data.get("authority") != "repository-owner":
        errors.append("current byte authorization authority must be repository-owner")
    if data.get("issue") != 178:
        errors.append("current byte authorization issue must be 178")
    if data.get("authorized_at") != ISSUE_178_AUTHORIZED_AT:
        errors.append(
            "current byte authorization authorized_at must bind issue 178 owner approval "
            f"at {ISSUE_178_AUTHORIZED_AT}"
        )
    if data.get("authorization_ref") != ISSUE_178_AUTHORIZATION_REF:
        errors.append("current byte authorization authorization_ref must bind issue 178 owner approval")
    for field in ("workflow_ref", "task_ref"):
        value = data.get(field)
        if not valid_repo_file(value):
            errors.append(
                f"current byte authorization {field} must be an exact repository-relative file"
            )
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["current byte authorization entries must be a non-empty list"]

    seen: set[str] = set()
    authorized_paths: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"current byte authorization entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be a mapping")
            continue
        unknown_entry_keys = sorted(set(entry) - AUTHORIZATION_ENTRY_KEYS)
        missing_entry_keys = sorted(AUTHORIZATION_ENTRY_KEYS - set(entry))
        if unknown_entry_keys:
            errors.append(f"{label} has unknown fields: {unknown_entry_keys}")
        if missing_entry_keys:
            errors.append(f"{label} is missing fields: {missing_entry_keys}")
        path = entry.get("path")
        if not valid_repo_file(path):
            errors.append(f"{label}.path must be an exact repository-relative file")
            continue
        if path in seen:
            errors.append(f"{label}.path duplicates {path}")
        seen.add(path)
        authorized_paths.add(path)
        if path not in candidates:
            errors.append(f"{label}.path is not a registered manifest candidate: {path}")
        for field in ("subject_blob", "authorized_blob"):
            if not sha1(entry.get(field)):
                errors.append(f"{label}.{field} must be a full lowercase Git blob SHA")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            errors.append(f"{label}.reason must be a non-empty string")
        if path in candidates:
            if entry.get("subject_blob") != subject_blobs.get(path):
                errors.append(f"{label}.subject_blob differs from manifest subject bytes")
            if entry.get("authorized_blob") != current_blobs.get(path):
                errors.append(f"{label}.authorized_blob differs from current bytes")
            if subject_blobs.get(path) == current_blobs.get(path):
                errors.append(f"{label}.path does not currently differ from subject bytes")

    drift_paths = {
        path
        for path in candidates
        if path in subject_blobs
        and path in current_blobs
        and subject_blobs[path] != current_blobs[path]
    }
    if authorized_paths != drift_paths:
        errors.append(
            "current byte authorization must cover exactly all current subject drifts; "
            f"missing={sorted(drift_paths - authorized_paths)}, "
            f"extra={sorted(authorized_paths - drift_paths)}"
        )
    return errors


def current_byte_authorization_paths(
    *,
    manifest_id: str,
    manifest_path: str,
    authorization_paths: list[str],
) -> list[str]:
    """Verify every linked authorization before allowing any current-byte bypass."""
    try:
        manifest_data = yaml.safe_load((ROOT / manifest_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load registered manifest {manifest_path}: {exc}") from exc
    if not isinstance(manifest_data, dict):
        raise RuntimeError(f"registered manifest {manifest_path} must be a mapping")
    subject_commit = manifest_data.get("subject_commit")
    coverage = manifest_data.get("coverage")
    candidate_list = coverage.get("candidate_paths") if isinstance(coverage, dict) else None
    if not isinstance(subject_commit, str) or not sha1(subject_commit):
        raise RuntimeError(f"registered manifest {manifest_path} has no valid subject_commit")
    if not isinstance(candidate_list, list) or not all(
        valid_repo_file(candidate) for candidate in candidate_list
    ):
        raise RuntimeError(f"registered manifest {manifest_path} has invalid candidate_paths")
    candidates = set(candidate_list)
    if len(candidates) != len(candidate_list):
        raise RuntimeError(f"registered manifest {manifest_path} has duplicate candidate_paths")
    manifest_blob = run_git(ROOT, "hash-object", "--", manifest_path)
    subject_blobs: dict[str, str] = {}
    current_blobs: dict[str, str] = {}
    for candidate in candidates:
        subject_blobs[candidate] = run_git(
            ROOT, "rev-parse", f"{subject_commit}:{candidate}"
        )
        current_blobs[candidate] = run_git(ROOT, "hash-object", "--", candidate)

    errors: list[str] = []
    forwarded_paths: list[str] = []
    for authorization_path in authorization_paths:
        try:
            authorization_data = yaml.safe_load(
                (ROOT / authorization_path).read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            errors.append(f"cannot load current byte authorization {authorization_path}: {exc}")
            continue
        errors.extend(
            f"{authorization_path}: {error}"
            for error in authorization_validation_errors(
                authorization_data,
                manifest_id=manifest_id,
                manifest_path=manifest_path,
                manifest_blob=manifest_blob,
                subject_commit=subject_commit,
                candidates=candidates,
                subject_blobs=subject_blobs,
                current_blobs=current_blobs,
            )
        )
        if isinstance(authorization_data, dict):
            for field in ("workflow_ref", "task_ref"):
                reference = authorization_data.get(field)
                if valid_repo_file(reference) and not (ROOT / reference).is_file():
                    errors.append(
                        f"{authorization_path}: current byte authorization "
                        f"{field} does not exist: {reference}"
                    )
        if isinstance(authorization_data, dict) and isinstance(
            authorization_data.get("entries"), list
        ):
            forwarded_paths.extend(
                entry.get("path")
                for entry in authorization_data["entries"]
                if isinstance(entry, dict) and isinstance(entry.get("path"), str)
            )
    if len(forwarded_paths) != len(set(forwarded_paths)):
        errors.append("current byte authorization entries must not duplicate paths across records")
    if errors:
        raise RuntimeError("; ".join(errors))
    return forwarded_paths


def main() -> int:
    try:
        (
            manifest_records,
            identity_policy_paths,
            source_disposition_paths,
        ) = load_registry_paths()
    except RuntimeError as exc:
        print(f"Source governance validation failed: {exc}", file=sys.stderr)
        return 1

    for manifest_id, path, authorization_paths in manifest_records:
        try:
            authorized_paths = current_byte_authorization_paths(
                manifest_id=manifest_id,
                manifest_path=path,
                authorization_paths=authorization_paths,
            )
        except RuntimeError as exc:
            print(f"Source governance validation failed: {exc}", file=sys.stderr)
            return 1
        result = subprocess.run(
            [
                sys.executable,
                str(DISPOSITION_VALIDATOR),
                "--manifest",
                path,
                *[
                    item
                    for authorized_path in authorized_paths
                    for item in ("--current-byte-authorization", authorized_path)
                ],
            ],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
        print(
            "Source governance validated manifest "
            f"{manifest_id}: {path} "
            f"(current-byte authorizations: {len(authorized_paths)})."
        )
    for path in identity_policy_paths:
        result = subprocess.run(
            [
                sys.executable,
                str(IDENTITY_VALIDATOR),
                "--policy",
                path,
            ],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
    for path in source_disposition_paths:
        result = subprocess.run(
            [
                sys.executable,
                str(SOURCE_DISPOSITION_VALIDATOR),
                "--contract",
                path,
            ],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
    print(
        "Source governance validation passed for "
        f"{len(manifest_records)} manifest(s) and "
        f"{len(identity_policy_paths)} repository identity policy record(s) and "
        f"{len(source_disposition_paths)} source disposition contract(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
