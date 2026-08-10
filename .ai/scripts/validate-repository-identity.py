#!/usr/bin/env python3
"""Fail closed when a retired repository identity is not explicitly classified."""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path, PurePosixPath

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-repository-identity.py")

import yaml

IDENTITY_VALIDATOR_ROOT = SCRIPT_ROOT.parent / "distribution" / "validators"
sys.path.insert(0, str(IDENTITY_VALIDATOR_ROOT))

from product_identity_registry import (
    IdentityRegistryError,
    alias_by_id,
    load_identity_registry,
    records_by_id,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ".ai/distribution/repository-identity-policy.yaml"
EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "policy_id",
    "issue",
    "status",
    "identity_registry",
    "scan",
    "allowed_classifications",
    "forbidden_classifications",
    "rules",
}
IDENTITY_REGISTRY_REF_KEYS = {
    "path",
    "current_repository_id",
    "retired_alias_refs",
}
RETIRED_ALIAS_REF_KEYS = {"identity_id", "alias_id"}
RULE_KEYS = {
    "id",
    "classification",
    "disposition",
    "paths",
    "path_globs",
    "excluded_patterns",
    "minimum_occurrence_lines",
    "minimum_files",
    "rationale",
}


class PolicyError(RuntimeError):
    """Raised when the policy or repository scan cannot be trusted."""


def valid_repo_pattern(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith(("/", "./")) or value.endswith("/"):
        return False
    return ".." not in PurePosixPath(value).parts


def string_list(value: object, location: str, *, non_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (non_empty and not value):
        qualifier = "non-empty " if non_empty else ""
        raise PolicyError(f"{location} must be a {qualifier}list")
    if any(not isinstance(item, str) or not item for item in value):
        raise PolicyError(f"{location} entries must be non-empty strings")
    if len(value) != len(set(value)):
        raise PolicyError(f"{location} must not contain duplicates")
    return list(value)


def require_exact_keys(
    value: object,
    required: set[str],
    optional: set[str],
    location: str,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PolicyError(f"{location} must be a mapping")
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required - optional)
    if missing:
        raise PolicyError(f"{location} is missing required keys: {', '.join(missing)}")
    if unknown:
        raise PolicyError(f"{location} has unknown keys: {', '.join(unknown)}")
    return value


def resolve_policy_path(root: Path, value: str) -> Path:
    if not valid_repo_pattern(value) or any(character in value for character in "*?["):
        raise PolicyError("policy path must be a literal repository-relative file")
    root = root.resolve()
    path = (root / value).resolve()
    if root not in path.parents:
        raise PolicyError("policy path resolves outside the repository root")
    if not path.is_file():
        raise PolicyError(f"policy file does not exist: {value}")
    return path


def load_policy(root: Path, relative_policy: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    policy_path = resolve_policy_path(root, relative_policy)
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PolicyError(f"cannot load repository identity policy: {exc}") from exc
    policy = require_exact_keys(raw, EXPECTED_TOP_LEVEL_KEYS, set(), "policy")
    if policy["schema_version"] != "1.0":
        raise PolicyError("policy.schema_version must be 1.0")
    if not isinstance(policy["policy_id"], str) or not policy["policy_id"]:
        raise PolicyError("policy.policy_id must be a non-empty string")
    if not isinstance(policy["issue"], int) or policy["issue"] < 1:
        raise PolicyError("policy.issue must be a positive integer")
    if policy["status"] != "active":
        raise PolicyError("policy.status must be active")

    registry_ref = require_exact_keys(
        policy["identity_registry"],
        IDENTITY_REGISTRY_REF_KEYS,
        set(),
        "policy.identity_registry",
    )
    registry_path = registry_ref["path"]
    if not isinstance(registry_path, str):
        raise PolicyError("policy.identity_registry.path must be a string")
    try:
        registry = load_identity_registry(root, registry_path)
    except IdentityRegistryError as exc:
        raise PolicyError(f"product identity registry is invalid: {exc}") from exc
    identities = records_by_id(registry)
    current_id = registry_ref["current_repository_id"]
    current_record = identities.get(current_id)
    if (
        current_record is None
        or current_record.get("kind") != "repository"
        or current_record.get("status") != "active"
    ):
        raise PolicyError(
            "policy.identity_registry.current_repository_id must reference "
            "an active repository identity"
        )
    current_forms = current_record.get("forms")
    if not isinstance(current_forms, dict) or not all(
        isinstance(current_forms.get(key), str) and current_forms[key]
        for key in ("slug", "coordinate", "url")
    ):
        raise PolicyError(
            "the current repository identity must define slug, coordinate, and url forms"
        )
    current_values = {
        current_record["canonical_value"],
        *current_forms.values(),
    }

    retired_records = registry_ref["retired_alias_refs"]
    if not isinstance(retired_records, list) or not retired_records:
        raise PolicyError(
            "policy.identity_registry.retired_alias_refs must be a non-empty list"
        )
    retired_ids: set[str] = set()
    retired_literals: set[str] = set()
    normalized_retired: list[dict[str, str]] = []
    for index, record in enumerate(retired_records):
        item = require_exact_keys(
            record,
            RETIRED_ALIAS_REF_KEYS,
            set(),
            f"policy.identity_registry.retired_alias_refs[{index}]",
        )
        identity_id = item["identity_id"]
        alias_id = item["alias_id"]
        identity = identities.get(identity_id)
        if identity is None or identity.get("kind") != "repository":
            raise PolicyError(
                "policy.identity_registry.retired_alias_refs "
                f"references unknown repository identity: {identity_id}"
            )
        alias = alias_by_id(identity, alias_id) if isinstance(alias_id, str) else None
        if alias is None:
            raise PolicyError(
                "policy.identity_registry.retired_alias_refs "
                f"references unknown alias: {alias_id}"
            )
        literal = alias["value"]
        if alias_id in retired_ids or literal in retired_literals:
            raise PolicyError("retired identity ids and literals must be unique")
        if literal in current_values:
            raise PolicyError("a retired identity cannot equal the current identity")
        retired_ids.add(alias_id)
        retired_literals.add(literal)
        normalized_retired.append({"id": alias_id, "literal": literal})

    scan = require_exact_keys(
        policy["scan"],
        {"source", "case_sensitive", "match_unit"},
        set(),
        "policy.scan",
    )
    if scan != {
        "source": "git-index-and-untracked-nonignored",
        "case_sensitive": True,
        "match_unit": "line",
    }:
        raise PolicyError(
            "policy.scan must select the case-sensitive Git index/untracked, line-based contract"
        )

    allowed = string_list(policy["allowed_classifications"], "policy.allowed_classifications")
    forbidden = string_list(
        policy["forbidden_classifications"], "policy.forbidden_classifications"
    )
    if set(allowed) & set(forbidden):
        raise PolicyError("allowed and forbidden classifications must be disjoint")
    if "current-operational" not in forbidden:
        raise PolicyError("current-operational must remain a forbidden classification")

    records = policy["rules"]
    if not isinstance(records, list) or not records:
        raise PolicyError("policy.rules must be a non-empty list")
    rule_ids: set[str] = set()
    rules: list[dict[str, object]] = []
    for index, record in enumerate(records):
        rule = require_exact_keys(
            record,
            {"id", "classification", "disposition", "rationale"},
            RULE_KEYS - {"id", "classification", "disposition", "rationale"},
            f"policy.rules[{index}]",
        )
        rule_id = rule["id"]
        classification = rule["classification"]
        if not isinstance(rule_id, str) or not rule_id:
            raise PolicyError(f"policy.rules[{index}].id must be non-empty")
        if rule_id in rule_ids:
            raise PolicyError(f"duplicate policy rule id: {rule_id}")
        rule_ids.add(rule_id)
        if classification in forbidden:
            raise PolicyError(f"rule {rule_id} uses forbidden classification: {classification}")
        if classification not in allowed:
            raise PolicyError(f"rule {rule_id} uses undeclared classification: {classification}")
        if any(
            not isinstance(rule[key], str) or not rule[key]
            for key in ("disposition", "rationale")
        ):
            raise PolicyError(f"rule {rule_id} disposition and rationale must be non-empty")

        paths = string_list(rule.get("paths", []), f"rule {rule_id}.paths", non_empty=False)
        globs = string_list(
            rule.get("path_globs", []), f"rule {rule_id}.path_globs", non_empty=False
        )
        excluded = string_list(
            rule.get("excluded_patterns", []),
            f"rule {rule_id}.excluded_patterns",
            non_empty=False,
        )
        if not paths and not globs:
            raise PolicyError(f"rule {rule_id} must declare paths or path_globs")
        for pattern in [*paths, *globs, *excluded]:
            if not valid_repo_pattern(pattern):
                raise PolicyError(f"rule {rule_id} has an invalid repository pattern: {pattern}")
        if any(any(character in path for character in "*?[") for path in paths):
            raise PolicyError(f"rule {rule_id}.paths entries must be literal paths")

        minimum_lines = rule.get("minimum_occurrence_lines", 1)
        minimum_files = rule.get("minimum_files", 1)
        if not isinstance(minimum_lines, int) or minimum_lines < 1:
            raise PolicyError(f"rule {rule_id}.minimum_occurrence_lines must be positive")
        if not isinstance(minimum_files, int) or minimum_files < 1:
            raise PolicyError(f"rule {rule_id}.minimum_files must be positive")
        rules.append(
            {
                **rule,
                "paths": paths,
                "path_globs": globs,
                "excluded_patterns": excluded,
                "minimum_occurrence_lines": minimum_lines,
                "minimum_files": minimum_files,
            }
        )

    policy["current_identity"] = {
        "repository_slug": current_forms["slug"],
        "repository": current_forms["coordinate"],
        "url": current_forms["url"],
    }
    policy["retired_identities"] = normalized_retired
    policy["_identity_registry_summary"] = {
        "records": len(registry["identity_records"]),
        "aliases": sum(
            len(record["aliases"]) for record in registry["identity_records"]
        ),
        "bindings": len(registry["bindings"]),
        "future_namespaces": len(registry["future_namespaces"]),
        "consumers": len(registry["consumer_contracts"]),
    }
    return policy, rules


def git_candidate_paths(root: Path) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        diagnostic = result.stderr.decode("utf-8", errors="replace").strip()
        raise PolicyError(f"cannot enumerate repository files through Git: {diagnostic}")
    try:
        paths = [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    except UnicodeDecodeError as exc:
        raise PolicyError(f"Git returned a non-UTF-8 repository path: {exc}") from exc
    if len(paths) != len(set(paths)):
        raise PolicyError("Git returned duplicate repository paths")
    return sorted(paths)


def rule_matches_path(rule: dict[str, object], path: str) -> bool:
    included = path in rule["paths"] or any(
        fnmatch.fnmatchcase(path, pattern) for pattern in rule["path_globs"]
    )
    excluded = any(
        fnmatch.fnmatchcase(path, pattern) for pattern in rule["excluded_patterns"]
    )
    return included and not excluded


def find_retired_lines(
    root: Path,
    paths: list[str],
    identities: list[dict[str, str]],
) -> dict[str, dict[int, set[str]]]:
    matches: dict[str, dict[int, set[str]]] = {}
    root = root.resolve()
    needles = [(item["id"], item["literal"].encode("utf-8")) for item in identities]
    for relative in paths:
        if not valid_repo_pattern(relative) or any(character in relative for character in "*?["):
            raise PolicyError(f"Git returned an invalid repository path: {relative}")
        path = (root / relative).resolve()
        if root not in path.parents:
            raise PolicyError(f"Git path resolves outside the repository root: {relative}")
        if not path.is_file():
            continue
        try:
            lines = path.read_bytes().splitlines()
        except OSError as exc:
            raise PolicyError(f"cannot read repository file {relative}: {exc}") from exc
        for line_number, line in enumerate(lines, start=1):
            matched_ids = {identity_id for identity_id, needle in needles if needle in line}
            if matched_ids:
                matches.setdefault(relative, {})[line_number] = matched_ids
    return matches


def validate(
    root: Path,
    policy_path: str,
) -> tuple[list[str], dict[str, tuple[int, int]], dict[str, int]]:
    policy, rules = load_policy(root, policy_path)
    matches = find_retired_lines(root, git_candidate_paths(root), policy["retired_identities"])
    errors: list[str] = []
    rule_lines: dict[str, int] = {str(rule["id"]): 0 for rule in rules}
    rule_files: dict[str, set[str]] = {str(rule["id"]): set() for rule in rules}

    for path, line_records in sorted(matches.items()):
        selected = [rule for rule in rules if rule_matches_path(rule, path)]
        identity_ids = sorted({item for ids in line_records.values() for item in ids})
        if not selected:
            errors.append(
                f"unclassified retired identity at {path}:{min(line_records)} ({', '.join(identity_ids)})"
            )
            continue
        if len(selected) > 1:
            errors.append(
                f"overlapping rules for {path}: {', '.join(str(rule['id']) for rule in selected)}"
            )
            continue
        rule_id = str(selected[0]["id"])
        rule_lines[rule_id] += len(line_records)
        rule_files[rule_id].add(path)

    for rule in rules:
        rule_id = str(rule["id"])
        if rule_lines[rule_id] < rule["minimum_occurrence_lines"]:
            errors.append(
                f"stale rule {rule_id}: expected at least {rule['minimum_occurrence_lines']} line(s), found {rule_lines[rule_id]}"
            )
        if len(rule_files[rule_id]) < rule["minimum_files"]:
            errors.append(
                f"stale rule {rule_id}: expected at least {rule['minimum_files']} file(s), found {len(rule_files[rule_id])}"
            )

    counts = {
        str(rule["id"]): (rule_lines[str(rule["id"])], len(rule_files[str(rule["id"])]))
        for rule in rules
    }
    return errors, counts, policy["_identity_registry_summary"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to scan")
    parser.add_argument(
        "--policy",
        default=DEFAULT_POLICY,
        help="Repository-relative retired identity policy path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors, counts, identity_summary = validate(args.root, args.policy)
    except PolicyError as exc:
        print(f"Repository identity validation failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("Repository identity validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    total_lines = sum(lines for lines, _ in counts.values())
    total_files = sum(files for _, files in counts.values())
    print(
        "Product identity registry validation passed: "
        f"{identity_summary['records']} canonical identity record(s), "
        f"{identity_summary['aliases']} alias record(s), "
        f"{identity_summary['bindings']} binding(s), "
        f"{identity_summary['future_namespaces']} reserved namespace rule(s), "
        f"{identity_summary['consumers']} consumer contract(s)."
    )
    print(
        "Repository identity validation passed: "
        f"{total_lines} retired-name line(s), {total_files} classified file assignment(s), "
        f"{len(counts)} active rule(s)."
    )
    for rule_id, (lines, files) in counts.items():
        print(f"- {rule_id}: {lines} line(s), {files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
