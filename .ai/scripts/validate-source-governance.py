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


def valid_repo_file(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith(("/", "./")) or value.endswith("/"):
        return False
    path = PurePosixPath(value)
    return ".." not in path.parts


def load_manifest_paths() -> list[str]:
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load source governance registry: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise RuntimeError("source governance registry schema_version must be 1.0")
    records = data.get("manifests")
    if not isinstance(records, list) or not records:
        raise RuntimeError("source governance registry manifests must be non-empty")

    ids: set[str] = set()
    paths: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise RuntimeError(f"manifests[{index}] must be a mapping")
        manifest_id = record.get("id")
        path = record.get("path")
        if not isinstance(manifest_id, str) or not manifest_id:
            raise RuntimeError(f"manifests[{index}].id must be a non-empty string")
        if manifest_id in ids:
            raise RuntimeError(f"duplicate source governance manifest id: {manifest_id}")
        ids.add(manifest_id)
        if not valid_repo_file(path):
            raise RuntimeError(
                f"manifests[{index}].path must be a repository-relative file"
            )
        if path in paths:
            raise RuntimeError(f"duplicate source governance manifest path: {path}")
        if not (ROOT / path).is_file():
            raise RuntimeError(f"source governance manifest does not exist: {path}")
        paths.append(path)
    return paths


def main() -> int:
    try:
        paths = load_manifest_paths()
    except RuntimeError as exc:
        print(f"Source governance validation failed: {exc}", file=sys.stderr)
        return 1

    for path in paths:
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
    print(f"Source governance validation passed for {len(paths)} manifest(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
