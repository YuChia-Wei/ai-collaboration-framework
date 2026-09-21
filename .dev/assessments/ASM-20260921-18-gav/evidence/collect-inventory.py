#!/usr/bin/env python3
"""Reproduce this assessment's fixed-source inventory; emit JSON, write nothing."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SOURCE = "8830cdfc252b8845efcbe6cce539041c17cf8e7a"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def nested_versions(value, prefix=""):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if key == "schema_version" and isinstance(item, (str, int, float)):
                found.append({"location": location, "value": item})
            elif key == "schema_version" and isinstance(item, dict) and "const" in item:
                found.append({"location": location + ".const", "value": item["const"]})
            found.extend(nested_versions(item, location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(nested_versions(item, f"{prefix}[{index}]"))
    return found


def collect(generated_at=None):
    paths = git("ls-tree", "-r", "--name-only", SOURCE, "--", ".ai", ".dev").decode().splitlines()
    schema_paths = [p for p in paths if Path(p).name.endswith(".schema.yaml") or Path(p).name == "evidence-schema.yaml"]
    historical = [p for p in paths if p.startswith(".dev/workflows/") and p.endswith("-schema.json")]
    schemas = []
    for path in schema_paths + historical:
        raw = git("show", f"{SOURCE}:{path}")
        data = yaml.safe_load(raw)
        models = data.get("record_models", {})
        schemas.append({
            "path": path,
            "scope_class": "historical-workflow-schema" if path in historical else "named-yaml-schema",
            "git_blob": git("rev-parse", f"{SOURCE}:{path}").decode().strip(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "dialect": data.get("$schema", "repository-contract-dsl"),
            "definition_schema_version": data.get("schema_version"),
            "top_level_keys": list(data),
            "record_models": {family: list(versions) for family, versions in models.items()},
            "record_types": data.get("record_types"),
            "nested_declared_versions": nested_versions(data),
        })
    templates = [p for p in paths if (p.startswith(".ai/assets/templates/") or (p.startswith(".ai/assets/skills/") and "/templates/" in p) or p.startswith(".dev/assessments/templates/") or p.startswith(".dev/problem-frames/templates/")) and p not in schema_paths and Path(p).name.lower() not in {"readme.md", "index.md"}]
    test_paths = [
        ".ai/scripts/tests/test_execution_artifacts.py",
        ".ai/scripts/tests/test_agent_execution_guardrails.py",
        ".ai/scripts/tests/test_assessment_artifacts.py",
        ".ai/assets/skills/software-development-orchestrator/scripts/tests/test_external_task_delegation_contract.py",
    ]
    tests = []
    for path in test_paths:
        raw = git("show", f"{SOURCE}:{path}")
        tree = ast.parse(raw.decode("utf-8-sig"))
        methods = [{"name": n.name, "line": n.lineno} for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")]
        tests.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "method_count": len(methods), "methods": methods})
    return {
        "artifact_kind": "assessment-source-inventory",
        "generator": ".dev/assessments/ASM-20260921-18-gav/evidence/collect-inventory.py",
        "generated_at": generated_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_commit": SOURCE,
        "scope": ["Git-tracked .ai/.dev named schemas", "Declared template roots", "Four explicitly selected framework test files"],
        "exclusions": ["Product source and tests", "Untracked/local artifacts", "Other history instances", "Unregistered implicit/code-defined models not proved by name matching"],
        "completeness": "Complete for the exact path selectors; not a count of all artifact kinds or proof of executable schema coverage.",
        "named_yaml_schema_count": len(schema_paths),
        "historical_json_schema_count": len(historical),
        "schemas": schemas,
        "template_path_count": len(templates),
        "template_paths": templates,
        "test_inventory": tests,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8-sig"))
        result = collect(expected["generated_at"])
        if expected != result:
            raise SystemExit("inventory differs from fixed-source regeneration")
        print("Fixed-source schema, template-path and test-method inventory matches.")
    else:
        result = collect()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
