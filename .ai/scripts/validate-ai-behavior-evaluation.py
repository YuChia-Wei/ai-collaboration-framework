#!/usr/bin/env python3
"""Run the deterministic, model-free AI behavior evaluation corpus."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
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
FAULT_MANIFEST_PATH = ROOT / ".ai/evaluation/incident-mutants.yaml"
FAULT_OUTPUT_ROOT = ROOT / ".dev/ai-context/local/validation"
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
CRITICAL_INCIDENTS = {"CTX-010", "REL-016", "UPG-005"}
CRITICAL_MUTANT_CATEGORIES = {
    "coordinated-weakening",
    "evidence-omission",
    "identity-substitution",
    "semantic-bypass",
    "validation-chain-break",
}
MUTANT_CRITICALITIES = {"critical", "exploratory"}
MUTANT_OUTCOMES = {"detected", "detected-by-unexpected-detector", "survived"}
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{0,95}$")
INCIDENT_REFERENCE = re.compile(r"^[A-Z][A-Z0-9-]{1,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class EvaluationError(ValueError):
    """Raised when a corpus or behavior contract fails closed."""

    def __init__(
        self, message: str, *, detector_id: str = "evaluation-contract"
    ) -> None:
        super().__init__(message)
        self.detector_id = detector_id


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
                f"{case_id}: copied source truth must be rejected, never preserved",
                detector_id="copied-source-truth-rejection",
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
            raise EvaluationError(
                f"{case_id}: {level} outcome requires evidence",
                detector_id="required-test-evidence",
            )
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
            raise EvaluationError(
                f"{case_id}: customization must be verified",
                detector_id="semantic-customization-verification",
            )
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
        raise EvaluationError(
            f"{case_id}: active identifiers are incomplete",
            detector_id="identifier-compatibility-exactness",
        )
    aliases = facts.get("compatibility_entries")
    expected_aliases = {
        "dev-workflow": "software-development-orchestrator",
        "repo-structure-sync": "ai-context-init",
    }
    if aliases != expected_aliases:
        raise EvaluationError(
            f"{case_id}: deprecated compatibility entries drifted",
            detector_id="identifier-compatibility-exactness",
        )
    historical = sorted(
        string_list(facts.get("historical_identifiers"), "historical_identifiers")
    )
    if historical != ["dev-workflow", "repo-structure-sync"]:
        raise EvaluationError(
            f"{case_id}: historical identifiers were removed",
            detector_id="identifier-compatibility-exactness",
        )
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
                f"actual={json.dumps(actual, sort_keys=True)}",
                detector_id="deterministic-expected-output-comparison",
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
        raise EvaluationError(
            "candidate result differs from deterministic baseline",
            detector_id="deterministic-baseline-comparison",
        )


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_text(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise EvaluationError(
            "incident fault injection could not resolve repository identity",
            detector_id="incident-execution-environment",
        )
    return completed.stdout


def tracked_status_digest() -> str:
    status = git_text("status", "--porcelain=v1", "--untracked-files=no")
    return hashlib.sha256(status.encode("utf-8")).hexdigest()


def subject_commit() -> str:
    commit = git_text("rev-parse", "HEAD").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise EvaluationError(
            "incident fault injection resolved an invalid repository HEAD",
            detector_id="incident-execution-environment",
        )
    return commit


ADAPTER_INPUTS = {
    "ctx010-coordinated-capability-id": (
        "ai-behavior-validator",
        "ctx010-contract",
        "ctx010-schema",
        "ctx010-template",
        "ctx010-validator",
        "fault-manifest-schema",
        "fault-result-schema",
        "python-entrypoints",
        "python-prerequisites",
    ),
    "rel016-semantic-publication-bypass": (
        "ai-behavior-validator",
        "ai-context-package-identity",
        "fault-manifest-schema",
        "fault-result-schema",
        "python-entrypoints",
        "python-prerequisites",
        "rel016-mutant",
        "rel016-renderer",
    ),
    "upg005-incoming-validator-failure": (
        "ai-behavior-validator",
        "fault-manifest-schema",
        "fault-result-schema",
        "python-entrypoints",
        "python-prerequisites",
        "upg005-matrix",
        "upg005-output",
        "upg005-receipt",
        "upg005-validator",
    ),
    "identifier-compatibility-substitution": (
        "ai-behavior-validator",
        "fault-manifest-schema",
        "fault-result-schema",
        "identifier-expected",
        "identifier-fixture",
        "python-entrypoints",
        "python-prerequisites",
    ),
    "required-test-evidence-omission": (
        "ai-behavior-validator",
        "devwf-activation-fixture",
        "devwf-profile",
        "devwf-runner",
        "evidence-expected",
        "evidence-fixture",
        "fault-manifest-schema",
        "fault-result-schema",
        "python-entrypoints",
        "python-prerequisites",
    ),
    "unknown-structured-field": (
        "ai-behavior-validator",
        "empty-expected",
        "empty-fixture",
        "fault-manifest-schema",
        "fault-result-schema",
        "python-entrypoints",
        "python-prerequisites",
    ),
}
ADAPTER_EXPECTED_DETECTORS = {
    "ctx010-coordinated-capability-id": "ctx010-immutable-owner-baseline",
    "rel016-semantic-publication-bypass": "rel016-publication-content-contract",
    "upg005-incoming-validator-failure": "edge-validation-report-invalid-shape",
    "identifier-compatibility-substitution": "identifier-compatibility-exactness",
    "required-test-evidence-omission": "required-test-evidence",
    "unknown-structured-field": "none-known",
}


def _validate_candidate_inputs(
    value: object,
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise EvaluationError("candidate_inputs must be a non-empty list")
    input_ids = [item.get("input_id") for item in value if isinstance(item, dict)]
    if len(input_ids) != len(value) or input_ids != sorted(set(input_ids)):
        raise EvaluationError("candidate input identifiers must be sorted and unique")
    inputs: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict) or set(item) != {"input_id", "path", "sha256"}:
            raise EvaluationError(f"candidate input {index} has an invalid shape")
        input_id = item["input_id"]
        path_text = item["path"]
        expected_digest = item["sha256"]
        if not isinstance(input_id, str) or not IDENTIFIER.fullmatch(input_id):
            raise EvaluationError(f"candidate input {index} has an invalid identifier")
        path = safe_repo_path(path_text, f"candidate_inputs[{index}].path")
        if not path.is_file() or path.relative_to(ROOT).as_posix() != path_text:
            raise EvaluationError(f"candidate input {input_id} is not one exact file")
        if not isinstance(expected_digest, str) or not SHA256.fullmatch(expected_digest):
            raise EvaluationError(f"candidate input {input_id} has an invalid SHA-256")
        observed_digest = file_sha256(path)
        if observed_digest != expected_digest:
            raise EvaluationError(
                f"candidate input {input_id} differs from its declared SHA-256",
                detector_id="candidate-input-identity",
            )
        inputs[input_id] = {
            "input_id": input_id,
            "path": path_text,
            "sha256": observed_digest,
            "resolved_path": path,
        }
    return inputs


def validate_fault_manifest(
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    required_fields = {
        "schema_version",
        "corpus_id",
        "corpus_version",
        "manifest_schema",
        "result_schema",
        "boundaries",
        "required_incidents",
        "required_critical_categories",
        "candidate_inputs",
        "mutants",
    }
    if set(manifest) != required_fields or manifest.get("schema_version") != "1.0":
        raise EvaluationError("incident mutant manifest has an invalid root shape")
    if manifest.get("corpus_id") != "incident-derived-validator-effectiveness":
        raise EvaluationError("incident mutant corpus identity is invalid")
    schema_ids = {
        "manifest_schema": "incident-mutant-manifest",
        "result_schema": "incident-fault-injection-result",
    }
    for field, schema_id in schema_ids.items():
        path = safe_repo_path(manifest.get(field), field)
        if not path.is_file():
            raise EvaluationError(f"{field} does not resolve to one file")
        if load_yaml_mapping(path).get("schema_id") != schema_id:
            raise EvaluationError(f"{field} has an invalid schema identity")
    boundaries = manifest.get("boundaries")
    if boundaries != {
        "critical_survivor": "fail-gate",
        "exploratory_survivor": "follow-up-required",
        "model_calls": "out-of-scope",
        "tracked_file_mutation": "forbidden",
    }:
        raise EvaluationError("incident mutant boundaries are incomplete")
    required_incidents = string_list(
        manifest.get("required_incidents"), "required_incidents"
    )
    if required_incidents != sorted(CRITICAL_INCIDENTS):
        raise EvaluationError("required incident coverage is incomplete")
    required_categories = string_list(
        manifest.get("required_critical_categories"),
        "required_critical_categories",
    )
    if required_categories != sorted(CRITICAL_MUTANT_CATEGORIES):
        raise EvaluationError("required critical mutant categories are incomplete")

    inputs = _validate_candidate_inputs(manifest.get("candidate_inputs"))
    mutants = manifest.get("mutants")
    if not isinstance(mutants, list) or not mutants:
        raise EvaluationError("mutants must be a non-empty list")
    mutant_ids = [item.get("mutant_id") for item in mutants if isinstance(item, dict)]
    if len(mutant_ids) != len(mutants) or mutant_ids != sorted(set(mutant_ids)):
        raise EvaluationError("mutant identifiers must be sorted and unique")
    expected_mutant_fields = {
        "mutant_id",
        "incident_reference",
        "category",
        "criticality",
        "adapter",
        "expected_detector",
        "input_refs",
        "follow_up",
    }
    seen_adapters: set[str] = set()
    referenced_inputs: set[str] = set()
    critical_categories: set[str] = set()
    critical_incidents: set[str] = set()
    for index, mutant in enumerate(mutants):
        if not isinstance(mutant, dict) or set(mutant) != expected_mutant_fields:
            raise EvaluationError(f"mutant {index} has an invalid shape")
        mutant_id = mutant["mutant_id"]
        adapter = mutant["adapter"]
        criticality = mutant["criticality"]
        category = mutant["category"]
        incident_reference = mutant["incident_reference"]
        expected_detector = mutant["expected_detector"]
        if not isinstance(mutant_id, str) or not IDENTIFIER.fullmatch(mutant_id):
            raise EvaluationError(f"mutant {index} has an invalid identifier")
        if not isinstance(adapter, str) or adapter not in ADAPTER_INPUTS:
            raise EvaluationError(f"mutant {mutant_id} names an unknown adapter")
        if adapter in seen_adapters:
            raise EvaluationError(f"mutant adapter {adapter} is duplicated")
        seen_adapters.add(adapter)
        if criticality not in MUTANT_CRITICALITIES:
            raise EvaluationError(f"mutant {mutant_id} has invalid criticality")
        if not isinstance(category, str) or not IDENTIFIER.fullmatch(category):
            raise EvaluationError(f"mutant {mutant_id} has an invalid category")
        if (
            not isinstance(incident_reference, str)
            or not INCIDENT_REFERENCE.fullmatch(incident_reference)
        ):
            raise EvaluationError(f"mutant {mutant_id} has an invalid incident reference")
        if expected_detector != ADAPTER_EXPECTED_DETECTORS[adapter]:
            raise EvaluationError(f"mutant {mutant_id} expected detector drifted")
        input_refs = string_list(mutant.get("input_refs"), f"{mutant_id}.input_refs")
        if input_refs != sorted(set(input_refs)) or tuple(input_refs) != ADAPTER_INPUTS[adapter]:
            raise EvaluationError(f"mutant {mutant_id} input closure is incomplete")
        if any(input_ref not in inputs for input_ref in input_refs):
            raise EvaluationError(f"mutant {mutant_id} references an unknown input")
        referenced_inputs.update(input_refs)
        if criticality == "critical":
            if mutant.get("follow_up") is not None:
                raise EvaluationError(f"critical mutant {mutant_id} cannot be advisory")
            critical_categories.add(category)
            if incident_reference in CRITICAL_INCIDENTS:
                critical_incidents.add(incident_reference)
        elif not isinstance(mutant.get("follow_up"), str) or not mutant["follow_up"]:
            raise EvaluationError(f"exploratory mutant {mutant_id} needs follow-up text")
    if seen_adapters != set(ADAPTER_INPUTS):
        raise EvaluationError("incident mutant adapter coverage is incomplete")
    if referenced_inputs != set(inputs):
        raise EvaluationError("candidate input inventory contains unused files")
    if critical_categories != CRITICAL_MUTANT_CATEGORIES:
        raise EvaluationError("critical mutant category coverage is incomplete")
    if critical_incidents != CRITICAL_INCIDENTS:
        raise EvaluationError("known incident mutant coverage is incomplete")
    return mutants, inputs


def _input_path(inputs: dict[str, dict[str, Any]], input_id: str) -> Path:
    return inputs[input_id]["resolved_path"]


def _detect_ctx010(inputs: dict[str, dict[str, Any]]) -> str | None:
    detector = load_python_module(
        "incident_ctx010_detector", _input_path(inputs, "ctx010-validator")
    )
    schema = detector.load_yaml(_input_path(inputs, "ctx010-schema"))
    contract = detector.load_yaml(_input_path(inputs, "ctx010-contract"))
    template = detector.load_yaml(_input_path(inputs, "ctx010-template"))
    detector.mutate_coordinated_capability_id(schema, contract, template)
    detector.rewrite_mutable_authority_digests_for_attack(schema, contract, template)
    errors = detector.contract_errors(contract, schema, template)
    immutable_error = "schema canonical SHA-256 must equal Issue #205 accepted baseline"
    if any(immutable_error in error for error in errors):
        return "ctx010-immutable-owner-baseline"
    return "ctx010-contract-validator" if errors else None


def _detect_rel016(inputs: dict[str, dict[str, Any]]) -> str | None:
    detector = load_python_module(
        "incident_rel016_detector", _input_path(inputs, "rel016-renderer")
    )
    try:
        detector.assert_phase_neutral_publication_claims(
            {"version": "v0.14.0"},
            _input_path(inputs, "rel016-mutant"),
            "incident mutant",
        )
    except detector.ReleaseNotesError:
        return "rel016-publication-content-contract"
    return None


def _detect_upg005(inputs: dict[str, dict[str, Any]]) -> str | None:
    detector = load_python_module(
        "incident_upg005_detector", _input_path(inputs, "upg005-validator")
    )
    raw_matrix, _ = detector.load_route_matrix(_input_path(inputs, "upg005-matrix"))
    matrix = detector.validate_matrix(raw_matrix)
    route = matrix["routes"][0]
    edge = route["edges"][0]
    receipt = json.loads(_input_path(inputs, "upg005-receipt").read_text(encoding="utf-8"))
    receipt["portable_validation"]["execution"]["outcome"] = "failed"
    receipt["portable_validation"]["execution"]["exit_code"] = 1
    report = detector.canonical_json(receipt).encode("utf-8")
    diagnostic = detector._edge_validation_receipt_diagnostic(
        edge,
        report,
        _input_path(inputs, "upg005-output").read_bytes(),
        {"route_id": route["route_id"], "edge_id": edge["edge_id"]},
        matrix["target"]["package_identity"],
    )
    if isinstance(diagnostic, dict) and isinstance(diagnostic.get("code"), str):
        return diagnostic["code"]
    return None


def _detect_identifier_substitution(
    inputs: dict[str, dict[str, Any]],
) -> str | None:
    facts = load_yaml_mapping(_input_path(inputs, "identifier-fixture"))
    facts["compatibility_entries"]["dev-workflow"] = "ai-context-init"
    try:
        actual = evaluate_compatibility(
            "identifier-compatibility", "identifier-compatibility", facts
        )
    except EvaluationError as exc:
        return exc.detector_id
    expected = load_yaml_mapping(_input_path(inputs, "identifier-expected"))
    return "deterministic-expected-output-comparison" if actual != expected else None


def _detect_evidence_omission(inputs: dict[str, dict[str, Any]]) -> str | None:
    facts = load_yaml_mapping(_input_path(inputs, "evidence-fixture"))
    del facts["test_execution"]["outcomes"]["integration"]["evidence"]
    try:
        actual = evaluate_software_development(
            "software-development", "software-development", facts
        )
    except EvaluationError as exc:
        return exc.detector_id
    expected = load_yaml_mapping(_input_path(inputs, "evidence-expected"))
    return "deterministic-expected-output-comparison" if actual != expected else None


def _detect_unknown_field(inputs: dict[str, dict[str, Any]]) -> str | None:
    facts = load_yaml_mapping(_input_path(inputs, "empty-fixture"))
    facts["exploratory_annotation"] = {"status": "unknown"}
    try:
        actual = evaluate_repository("empty-repository", "empty", facts)
    except EvaluationError as exc:
        return exc.detector_id
    expected = load_yaml_mapping(_input_path(inputs, "empty-expected"))
    return "deterministic-expected-output-comparison" if actual != expected else None


FAULT_ADAPTERS: dict[str, Callable[[dict[str, dict[str, Any]]], str | None]] = {
    "ctx010-coordinated-capability-id": _detect_ctx010,
    "rel016-semantic-publication-bypass": _detect_rel016,
    "upg005-incoming-validator-failure": _detect_upg005,
    "identifier-compatibility-substitution": _detect_identifier_substitution,
    "required-test-evidence-omission": _detect_evidence_omission,
    "unknown-structured-field": _detect_unknown_field,
}


def run_incident_fault_injection(
    manifest_path: Path = FAULT_MANIFEST_PATH,
    *,
    disabled_detectors: set[str] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    if ROOT.resolve() not in (manifest_path, *manifest_path.parents):
        raise EvaluationError("incident mutant manifest escapes the repository root")
    manifest = load_yaml_mapping(manifest_path)
    mutants, inputs = validate_fault_manifest(manifest)
    disabled = set() if disabled_detectors is None else set(disabled_detectors)
    if any(not isinstance(item, str) or not IDENTIFIER.fullmatch(item) for item in disabled):
        raise EvaluationError("disabled detector test controls are invalid")
    before_status = tracked_status_digest()
    results: list[dict[str, Any]] = []
    for mutant in mutants:
        try:
            actual_detector = FAULT_ADAPTERS[mutant["adapter"]](inputs)
        except Exception as exc:
            raise EvaluationError(
                f"mutant {mutant['mutant_id']} adapter was blocked by "
                f"{type(exc).__name__}",
                detector_id="incident-adapter-execution",
            ) from None
        if actual_detector in disabled:
            actual_detector = None
        if actual_detector is None:
            outcome = "survived"
        elif actual_detector == mutant["expected_detector"]:
            outcome = "detected"
        else:
            outcome = "detected-by-unexpected-detector"
        if outcome not in MUTANT_OUTCOMES:
            raise EvaluationError("incident mutant produced an unsupported outcome")
        result = {
            "mutant_id": mutant["mutant_id"],
            "incident_reference": mutant["incident_reference"],
            "category": mutant["category"],
            "criticality": mutant["criticality"],
            "expected_detector": mutant["expected_detector"],
            "actual_detector": actual_detector,
            "outcome": outcome,
            "input_refs": list(mutant["input_refs"]),
            "follow_up": mutant["follow_up"] if outcome == "survived" else None,
        }
        result["diagnostic_fingerprint"] = canonical_json_sha256(
            {
                "adapter": mutant["adapter"],
                "actual_detector": actual_detector,
                "outcome": outcome,
            }
        )
        results.append(result)
    after_status = tracked_status_digest()
    tracked_state_unchanged = before_status == after_status
    critical = [item for item in results if item["criticality"] == "critical"]
    exploratory = [item for item in results if item["criticality"] == "exploratory"]
    critical_survivors = [
        item["mutant_id"] for item in critical if item["outcome"] != "detected"
    ]
    exploratory_survivors = [
        item["mutant_id"] for item in exploratory if item["outcome"] == "survived"
    ]
    if critical_survivors or not tracked_state_unchanged:
        decision = "failed"
    elif exploratory_survivors:
        decision = "passed-with-exploratory-survivors"
    else:
        decision = "passed"
    report: dict[str, Any] = {
        "schema_version": "incident-fault-injection-result/v1",
        "corpus_id": manifest["corpus_id"],
        "corpus_version": manifest["corpus_version"],
        "subject": {"commit": subject_commit()},
        "manifest_digest": canonical_json_sha256(manifest),
        "candidate_inputs": [
            {
                "input_id": item["input_id"],
                "path": item["path"],
                "sha256": item["sha256"],
            }
            for item in inputs.values()
        ],
        "results": results,
        "effectiveness": {
            "critical_detected": len(critical) - len(critical_survivors),
            "critical_total": len(critical),
            "critical_detection_percent": (
                100 * (len(critical) - len(critical_survivors)) // len(critical)
            ),
            "critical_survivors": critical_survivors,
            "exploratory_total": len(exploratory),
            "exploratory_survivors": exploratory_survivors,
            "follow_up_candidates": [
                {
                    "mutant_id": item["mutant_id"],
                    "summary": item["follow_up"],
                }
                for item in exploratory
                if item["outcome"] == "survived"
            ],
        },
        "worktree": {
            "before_tracked_status_digest": before_status,
            "after_tracked_status_digest": after_status,
            "tracked_state_unchanged": tracked_state_unchanged,
        },
        "test_controls": {"disabled_detectors": sorted(disabled)},
        "decision": {
            "outcome": decision,
            "critical_gate": "failed" if critical_survivors else "passed",
            "exploratory_disposition": (
                "follow-up-required" if exploratory_survivors else "no-survivors"
            ),
        },
    }
    report["report_digest"] = canonical_json_sha256(report)
    return report


def safe_fault_output(value: Path) -> Path:
    output = safe_repo_path(value.as_posix(), "fault-injection output")
    allowed = FAULT_OUTPUT_ROOT.resolve()
    if allowed not in (output, *output.parents) or output == allowed:
        raise EvaluationError(
            "fault-injection output must be beneath .dev/ai-context/local/validation"
        )
    if output.exists():
        raise EvaluationError("fault-injection output is create-only")
    relative = output.relative_to(ROOT).as_posix()
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", relative],
        cwd=ROOT,
        check=False,
    )
    if ignored.returncode != 0:
        raise EvaluationError("fault-injection output must be ignored by Git")
    return output


def write_yaml_create_only(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            yaml.safe_dump(data, stream, sort_keys=False, allow_unicode=True)
    except OSError as exc:
        raise EvaluationError("fault-injection output could not be created") from exc


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
    fault_parser = subparsers.add_parser("fault-injection")
    fault_parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(".ai/evaluation/incident-mutants.yaml"),
    )
    fault_parser.add_argument("--output", type=Path)
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
        elif args.command == "compare":
            compare_results(
                load_yaml_mapping(args.baseline),
                load_yaml_mapping(args.candidate),
            )
            print("Deterministic baseline and candidate are equivalent.")
        else:
            manifest_path = safe_repo_path(
                args.manifest.as_posix(), "fault-injection manifest"
            )
            result = run_incident_fault_injection(manifest_path)
            if args.output is not None:
                output = safe_fault_output(args.output)
                write_yaml_create_only(output, result)
            print(
                "Incident fault injection "
                f"{result['decision']['outcome']} "
                f"({result['effectiveness']['critical_detected']}/"
                f"{result['effectiveness']['critical_total']} critical detected; "
                f"{len(result['effectiveness']['exploratory_survivors'])} "
                "exploratory survivor(s))."
            )
            if result["decision"]["outcome"] == "failed":
                return 1
    except (EvaluationError, OSError, yaml.YAMLError) as exc:
        print(f"AI behavior deterministic evaluation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
