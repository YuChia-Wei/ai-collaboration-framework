#!/usr/bin/env python3
"""Run the deterministic, model-free AI behavior evaluation corpus."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-behavior-evaluation.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / ".ai/evaluation/corpus-manifest.yaml"
BASELINE_PATH = ROOT / ".ai/evaluation/baselines/v1.yaml"
DEVWF_RUNNER = (
    ROOT
    / ".ai/assets/skills/software-development-orchestrator/scripts/"
    "validate-software-development-orchestrator-acceptance.py"
)
DEVWF_PROFILE = (
    ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
)
REQUIRED_FAMILIES = {
    "empty",
    "existing",
    "copied-template",
    "software-development",
    "customization-upgrade",
    "identifier-compatibility",
}
SUCCESS_STATUSES = {"passed", "not-applicable"}


class EvaluationError(ValueError):
    """Raised when a corpus or behavior contract fails closed."""


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EvaluationError(f"{path}: expected a YAML mapping")
    return data


def safe_repo_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationError(f"{label}: expected a non-empty repository path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise EvaluationError(f"{label}: unsafe repository-relative path {value!r}")
    resolved = (ROOT / candidate).resolve()
    if ROOT.resolve() not in (resolved, *resolved.parents):
        raise EvaluationError(f"{label}: path escapes repository root")
    return resolved


def string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise EvaluationError(f"{label}: expected a string list")
    return list(value)


def evaluate_repository(
    case_id: str, family: str, facts: dict[str, Any]
) -> dict[str, Any]:
    if facts.get("requested_capability") != "initialize-ai-context":
        raise EvaluationError(f"{case_id}: initialization route is missing")
    state = facts.get("repository_state")
    if state != family:
        raise EvaluationError(f"{case_id}: repository state must match family")
    target_owned = sorted(string_list(facts.get("target_owned_files"), "target_owned_files"))
    copied_truth = sorted(string_list(facts.get("copied_source_truth"), "copied_source_truth"))
    if state == "empty":
        if target_owned or copied_truth:
            raise EvaluationError(f"{case_id}: empty repository contains classified files")
        decision = "initialize"
    elif state == "existing":
        if not target_owned or copied_truth:
            raise EvaluationError(
                f"{case_id}: existing repository must preserve target truth only"
            )
        decision = "adapt-and-preserve"
    elif state == "copied-template":
        if not target_owned or not copied_truth:
            raise EvaluationError(
                f"{case_id}: copied-template case requires target and source truth"
            )
        if facts.get("source_truth_disposition") != "reject":
            raise EvaluationError(
                f"{case_id}: copied source truth must be rejected, never preserved"
            )
        decision = "adapt-and-remove-source-truth"
    else:
        raise EvaluationError(f"{case_id}: unsupported repository state {state!r}")
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "family": family,
        "route": "ai-context-init",
        "decision": decision,
        "details": {
            "preserve_target_owned": target_owned,
            "reject_source_truth": copied_truth,
        },
    }


def load_python_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise EvaluationError(f"Unable to load behavior oracle: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_software_development(
    case_id: str, family: str, facts: dict[str, Any]
) -> dict[str, Any]:
    fixture_path = safe_repo_path(facts.get("activation_fixture"), "activation_fixture")
    if not fixture_path.is_file():
        raise EvaluationError(f"{case_id}: activation fixture is missing")
    devwf = load_python_module("eval_dev_workflow_oracle", DEVWF_RUNNER)
    routed, errors = devwf.route_classified_envelope(
        load_yaml_mapping(fixture_path),
        load_yaml_mapping(DEVWF_PROFILE),
    )
    if errors:
        raise EvaluationError(f"{case_id}: DEVWF oracle failed: {'; '.join(errors)}")
    activation = routed.get("activation", {})
    stages = routed.get("stages", [])
    pause = routed.get("approval_pause", {})
    if (
        not isinstance(activation, dict)
        or not isinstance(stages, list)
        or not isinstance(pause, dict)
    ):
        raise EvaluationError(f"{case_id}: DEVWF oracle returned malformed output")

    test_execution = facts.get("test_execution")
    if not isinstance(test_execution, dict):
        raise EvaluationError(f"{case_id}: test_execution must be a mapping")
    selected = string_list(
        test_execution.get("selected_levels"), "test_execution.selected_levels"
    )
    required = string_list(
        test_execution.get("required_for_closeout"),
        "test_execution.required_for_closeout",
    )
    outcomes = test_execution.get("outcomes")
    if not isinstance(outcomes, dict):
        raise EvaluationError(f"{case_id}: test outcomes must be a mapping")
    if not set(required).issubset(selected):
        raise EvaluationError(f"{case_id}: closeout levels must be selected")
    blocked: list[str] = []
    for level in required:
        outcome = outcomes.get(level)
        if not isinstance(outcome, dict):
            raise EvaluationError(f"{case_id}: missing required outcome {level!r}")
        status = outcome.get("status")
        evidence = outcome.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise EvaluationError(f"{case_id}: {level} outcome requires evidence")
        if status not in SUCCESS_STATUSES:
            blocked.append(level)

    stage_capabilities: list[str] = []
    implementation_state = ""
    for stage in stages:
        if not isinstance(stage, dict):
            raise EvaluationError(f"{case_id}: malformed DEVWF stage")
        capability = stage.get("capability_slot")
        if not isinstance(capability, str):
            raise EvaluationError(f"{case_id}: stage is missing capability")
        stage_capabilities.append(capability)
        if capability == "implementation":
            implementation_state = str(stage.get("state", ""))
    if pause.get("paused") is not True or implementation_state != "blocked-awaiting-approval":
        raise EvaluationError(f"{case_id}: implementation crossed the approval gate")

    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "family": family,
        "route": "software-development-orchestrator",
        "decision": "pause-before-implementation",
        "details": {
            "activated_without_named_skill": (
                routed.get("activated") is True
                and activation.get("named_skill_dependency") is False
            ),
            "stage_capabilities": stage_capabilities,
            "implementation_state": implementation_state,
            "test_closeout_ready": not blocked,
            "blocked_required_levels": sorted(blocked),
        },
    }


def evaluate_customization(
    case_id: str, family: str, facts: dict[str, Any]
) -> dict[str, Any]:
    if facts.get("requested_capability") != "upgrade-ai-context":
        raise EvaluationError(f"{case_id}: upgrade route is missing")
    provenance = string_list(facts.get("provenance_records"), "provenance_records")
    if provenance != [".dev/ai-context/provenance.yaml"]:
        raise EvaluationError(f"{case_id}: exactly one canonical provenance is required")
    customizations = facts.get("customizations")
    if not isinstance(customizations, list) or not customizations:
        raise EvaluationError(f"{case_id}: semantic customizations are required")
    ids: list[str] = []
    for index, item in enumerate(customizations):
        if not isinstance(item, dict):
            raise EvaluationError(f"{case_id}: customization {index} is malformed")
        for field in (
            "customization_id",
            "identity_kind",
            "subject",
            "reason",
            "owner",
            "evidence",
            "audit_status",
        ):
            if item.get(field) in (None, "", []):
                raise EvaluationError(
                    f"{case_id}: customization {index} is missing {field}"
                )
        if item.get("identity_kind") not in {"capability", "rule", "contract"}:
            raise EvaluationError(f"{case_id}: unsupported customization identity")
        if item.get("audit_status") != "verified":
            raise EvaluationError(f"{case_id}: customization must be verified")
        ids.append(str(item["customization_id"]))
    if len(ids) != len(set(ids)):
        raise EvaluationError(f"{case_id}: duplicate customization identifier")
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "family": family,
        "route": "ai-context-upgrader",
        "decision": "semantic-reconciliation-required",
        "details": {
            "provenance": provenance[0],
            "customization_ids": sorted(ids),
            "preservation_mode": "target-owned-semantic-customization",
        },
    }


def evaluate_compatibility(
    case_id: str, family: str, facts: dict[str, Any]
) -> dict[str, Any]:
    if facts.get("requested_capability") != "resolve-skill-identifiers":
        raise EvaluationError(f"{case_id}: skill-registry route is missing")
    active = sorted(string_list(facts.get("active_identifiers"), "active_identifiers"))
    expected_active = ["ai-context-init", "software-development-orchestrator"]
    if active != expected_active:
        raise EvaluationError(f"{case_id}: active identifiers are incomplete")
    aliases = facts.get("compatibility_entries")
    expected_aliases = {
        "dev-workflow": "software-development-orchestrator",
        "repo-structure-sync": "ai-context-init",
    }
    if aliases != expected_aliases:
        raise EvaluationError(f"{case_id}: deprecated compatibility entries drifted")
    historical = sorted(
        string_list(facts.get("historical_identifiers"), "historical_identifiers")
    )
    if historical != ["dev-workflow", "repo-structure-sync"]:
        raise EvaluationError(f"{case_id}: historical identifiers were removed")
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "family": family,
        "route": "skill-registry",
        "decision": "activate-with-deprecated-aliases",
        "details": {
            "active_identifiers": active,
            "compatibility_entries": aliases,
            "preserve_historical_identifiers": historical,
        },
    }


EVALUATORS: dict[str, Callable[[str, str, dict[str, Any]], dict[str, Any]]] = {
    "empty": evaluate_repository,
    "existing": evaluate_repository,
    "copied-template": evaluate_repository,
    "software-development": evaluate_software_development,
    "customization-upgrade": evaluate_customization,
    "identifier-compatibility": evaluate_compatibility,
}


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != "1.0":
        raise EvaluationError("manifest.schema_version must be 1.0")
    boundaries = manifest.get("boundaries")
    if not isinstance(boundaries, dict) or boundaries.get("model_calls") != "out-of-scope":
        raise EvaluationError("manifest must prohibit model calls")
    families = set(string_list(manifest.get("families"), "manifest.families"))
    if families != REQUIRED_FAMILIES:
        raise EvaluationError("manifest family coverage is incomplete")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != len(REQUIRED_FAMILIES):
        raise EvaluationError("manifest must contain exactly one case per family")
    ids: set[str] = set()
    case_families: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise EvaluationError(f"manifest case {index} must be a mapping")
        case_id = case.get("case_id")
        family = case.get("family")
        if not isinstance(case_id, str) or case_id in ids:
            raise EvaluationError(f"manifest case {index} has duplicate/invalid id")
        if not isinstance(family, str) or family not in REQUIRED_FAMILIES:
            raise EvaluationError(f"manifest case {case_id} has invalid family")
        ids.add(case_id)
        case_families.add(family)
        safe_repo_path(case.get("input"), f"{case_id}.input")
        safe_repo_path(case.get("expected"), f"{case_id}.expected")
    if case_families != REQUIRED_FAMILIES:
        raise EvaluationError("manifest does not cover every family")
    return cases


def run_corpus(
    manifest_path: Path = MANIFEST_PATH,
    *,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    manifest = load_yaml_mapping(manifest_path)
    cases = validate_manifest(manifest)
    results: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case["case_id"])
        family = str(case["family"])
        input_path = safe_repo_path(case["input"], f"{case_id}.input")
        expected_path = safe_repo_path(case["expected"], f"{case_id}.expected")
        facts = (
            overrides[case_id]
            if overrides is not None and case_id in overrides
            else load_yaml_mapping(input_path)
        )
        actual = EVALUATORS[family](case_id, family, facts)
        expected = load_yaml_mapping(expected_path)
        if actual != expected:
            raise EvaluationError(
                f"{case_id}: deterministic oracle drift\n"
                f"expected={json.dumps(expected, sort_keys=True)}\n"
                f"actual={json.dumps(actual, sort_keys=True)}"
            )
        results.append(actual)
    normalized = {
        "schema_version": "1.0",
        "corpus_id": manifest["corpus_id"],
        "corpus_version": manifest["corpus_version"],
        "normalization": "exact-yaml-mappings-sorted-by-case-id",
        "results": sorted(results, key=lambda item: str(item["case_id"])),
    }
    payload = json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    normalized["sha256"] = hashlib.sha256(payload).hexdigest()
    return normalized


def compare_results(baseline: dict[str, Any], candidate: dict[str, Any]) -> None:
    if baseline != candidate:
        raise EvaluationError("candidate result differs from deterministic baseline")


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--output", type=Path, required=True)
    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--baseline", type=Path, default=BASELINE_PATH)
    compare_parser.add_argument("--candidate", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            result = run_corpus()
            compare_results(load_yaml_mapping(BASELINE_PATH), result)
            print(
                "AI behavior deterministic evaluation passed "
                f"({len(result['results'])} cases, model calls: 0)."
            )
        elif args.command == "run":
            result = run_corpus()
            write_yaml(args.output, result)
            print(f"Wrote deterministic evaluation result: {args.output}")
        else:
            compare_results(
                load_yaml_mapping(args.baseline),
                load_yaml_mapping(args.candidate),
            )
            print("Deterministic baseline and candidate are equivalent.")
    except (EvaluationError, OSError, yaml.YAMLError) as exc:
        print(f"AI behavior deterministic evaluation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
