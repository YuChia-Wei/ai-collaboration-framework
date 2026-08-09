#!/usr/bin/env python3
"""Run source-repository governance manifests from a stable registry."""

from __future__ import annotations

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


def valid_repo_file(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith(("/", "./")) or value.endswith("/"):
        return False
    path = PurePosixPath(value)
    return ".." not in path.parts


def load_registry_paths() -> tuple[list[str], list[str]]:
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load source governance registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.1":
        raise RuntimeError("source governance registry schema_version must be 1.1")
    ids: set[str] = set()
    all_paths: set[str] = set()

    def load_group(key: str, label: str) -> list[str]:
        records = data.get(key)
        if not isinstance(records, list) or not records:
            raise RuntimeError(f"source governance registry {key} must be non-empty")
        paths: list[str] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise RuntimeError(f"{key}[{index}] must be a mapping")
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
            paths.append(path)
        return paths

    return (
        load_group("manifests", "manifest"),
        load_group("repository_identity_policies", "repository identity policy"),
    )


def main() -> int:
    try:
        manifest_paths, identity_policy_paths = load_registry_paths()
    except RuntimeError as exc:
        print(f"Source governance validation failed: {exc}", file=sys.stderr)
        return 1

    for path in manifest_paths:
        result = subprocess.run(
            [
                sys.executable,
                str(DISPOSITION_VALIDATOR),
                "--manifest",
                path,
            ],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
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
    print(
        "Source governance validation passed for "
        f"{len(manifest_paths)} manifest(s) and "
        f"{len(identity_policy_paths)} repository identity policy record(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
