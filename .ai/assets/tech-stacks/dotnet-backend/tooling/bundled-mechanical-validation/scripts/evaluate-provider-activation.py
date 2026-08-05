#!/usr/bin/env python3
"""Fail-closed evaluator for bundled mechanical-validation activation records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


PROVIDER_ID = "ai-context-dotnet-bundled-mechanical-validation"
CANONICAL_ROOT = ".ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation/"
SCHEMA_VERSION = "1.0"
OUTCOMES = {
    "source-available",
    "active-reference-in-place",
    "active-materialized",
    "stale",
    "unresolved",
}
FRESHNESS = {"fresh", "stale", "unresolved"}
CAPABILITIES = {"analyzers", "runtime-validation"}
CAPABILITY_PROJECTS = {
    "analyzers": "analyzers/DotnetBackendAnalyzers.csproj",
    "runtime-validation": "runtime-validation/DotnetBackendValidation.csproj",
}
CAPABILITY_SOURCE_ROOTS = {
    "analyzers": "analyzers/",
    "runtime-validation": "runtime-validation/",
}
EVIDENCE_KINDS = ("wiring", "configuration", "invocation")
APPLIED_STATUSES = {"verified-existing", "applied-by-target-owner"}
DEFAULT_EVIDENCE_ROOT = (
    ".dev/ai-context/provider-evidence/ai-context-dotnet-bundled-mechanical-validation"
)
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PLACEHOLDER = re.compile(r"<[^>]+>")


def load_yaml_file(path: Path) -> tuple[dict[str, Any] | None, bytes | None, list[str]]:
    try:
        raw = path.read_bytes()
        value = yaml.safe_load(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return None, None, [f"{path}: cannot read YAML: {exc}"]
    if not isinstance(value, dict):
        return None, raw, [f"{path}: top-level YAML value must be a mapping"]
    return value, raw, []


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_value(value: Any) -> str:
    return digest_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{location}: must be a mapping")
    return {}


def closed_mapping(
    value: Any,
    location: str,
    allowed_keys: set[str],
    errors: list[str],
) -> dict[str, Any]:
    result = mapping(value, location, errors)
    unexpected = set(result) - allowed_keys
    if unexpected:
        errors.append(f"{location}: unexpected keys {sorted(unexpected)}")
    return result


def non_empty_string(value: Any, location: str, errors: list[str]) -> str:
    if isinstance(value, str) and value.strip():
        return value
    errors.append(f"{location}: must be a non-empty string")
    return ""


def concrete_string(value: Any, location: str, errors: list[str]) -> str:
    result = non_empty_string(value, location, errors)
    if result and PLACEHOLDER.search(result):
        errors.append(f"{location}: placeholders cannot support an active outcome")
    return result


def non_empty_mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any]:
    result = mapping(value, location, errors)
    if not result:
        errors.append(f"{location}: must not be empty")
    return result


def safe_relative_path(value: Any, location: str, errors: list[str]) -> tuple[str, ...] | None:
    path = non_empty_string(value, location, errors)
    if not path:
        return None
    if path.startswith(("/", "\\")) or "\\" in path:
        errors.append(f"{location}: must be a safe repository-relative slash-separated path")
        return None
    parts = tuple(path.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        errors.append(f"{location}: must not contain empty, '.' or '..' path segments")
        return None
    return parts


def safe_directory(
    repository_root: Path,
    relative_path: Any,
    location: str,
    errors: list[str],
) -> Path | None:
    parts = safe_relative_path(relative_path, location, errors)
    if parts is None:
        return None
    candidate = repository_root.joinpath(*parts)
    current = repository_root
    for part in parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"{location}: must not traverse symlink {current}")
            return None
    if not candidate.is_dir():
        errors.append(f"{location}: evidence root directory does not exist: {candidate}")
        return None
    try:
        resolved_root = repository_root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
    except OSError as exc:
        errors.append(f"{location}: cannot resolve evidence root: {exc}")
        return None
    if not resolved_candidate.is_relative_to(resolved_root):
        errors.append(f"{location}: evidence root escapes repository root")
        return None
    return resolved_candidate


def safe_regular_file(
    root: Path,
    relative_path: Any,
    location: str,
    errors: list[str],
) -> Path | None:
    parts = safe_relative_path(relative_path, location, errors)
    if parts is None:
        return None
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"{location}: must not traverse symlink {current}")
            return None
    if not candidate.is_file() or candidate.is_symlink():
        errors.append(f"{location}: must resolve to a regular non-symlink file")
        return None
    try:
        resolved_root = root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
    except OSError as exc:
        errors.append(f"{location}: cannot resolve evidence file: {exc}")
        return None
    if not resolved_candidate.is_relative_to(resolved_root):
        errors.append(f"{location}: regular file escapes its required root")
        return None
    return resolved_candidate


def canonical_provider_root(
    repository_root: Path,
    provider_root: Path,
    errors: list[str],
) -> Path | None:
    """Resolve only the physical canonical provider root; reject symlink traversal."""
    try:
        resolved_repository_root = repository_root.resolve(strict=True)
    except OSError as exc:
        errors.append(f"repository_root: cannot resolve repository root: {exc}")
        return None
    if not resolved_repository_root.is_dir():
        errors.append("repository_root: must resolve to a directory")
        return None

    expected = resolved_repository_root.joinpath(*CANONICAL_ROOT.rstrip("/").split("/"))
    current = resolved_repository_root
    for part in CANONICAL_ROOT.rstrip("/").split("/"):
        current = current / part
        if current.is_symlink():
            errors.append(f"canonical provider root: must not traverse symlink {current}")
            return None
    if not expected.is_dir():
        errors.append(f"canonical provider root: directory does not exist: {expected}")
        return None
    try:
        resolved_expected = expected.resolve(strict=True)
        resolved_provider_root = provider_root.resolve(strict=True)
    except OSError as exc:
        errors.append(f"provider_root: cannot resolve provider root: {exc}")
        return None
    if provider_root.is_symlink():
        errors.append("provider_root: must not be a symlink")
        return None
    if not resolved_provider_root.is_dir():
        errors.append("provider_root: must resolve to a directory")
        return None
    if resolved_provider_root != resolved_expected:
        errors.append(
            "provider_root: must resolve to the canonical provider root under repository_root"
        )
        return None
    return resolved_expected


def verify_canonical_provider_files(
    provider_root: Path,
    provider_manifest_bytes: bytes,
    errors: list[str],
) -> None:
    manifest_path = safe_regular_file(
        provider_root,
        "provider-manifest.yaml",
        "canonical provider manifest",
        errors,
    )
    if manifest_path is not None:
        try:
            if manifest_path.read_bytes() != provider_manifest_bytes:
                errors.append(
                    "provider manifest bytes: must be loaded from the canonical provider root"
                )
        except OSError as exc:
            errors.append(f"canonical provider manifest: cannot read manifest: {exc}")
    for capability in sorted(CAPABILITIES):
        safe_regular_file(
            provider_root,
            CAPABILITY_PROJECTS[capability],
            f"canonical provider {capability} project",
            errors,
        )


def manifest_capabilities(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"provider-manifest.schema_version: must be {SCHEMA_VERSION!r}")
    provider = mapping(manifest.get("provider"), "provider-manifest.provider", errors)
    required_provider = {
        "id": PROVIDER_ID,
        "canonical_root": CANONICAL_ROOT,
        "owner_component": "dotnet-backend",
        "delivery_state": "source-available",
        "default_activation_state": "source-available",
        "source_delivery": "source-only",
    }
    for key, expected in required_provider.items():
        if provider.get(key) != expected:
            errors.append(f"provider-manifest.provider.{key}: must be {expected!r}")
    if provider.get("supported_activation_modes") != ["reference-in-place"]:
        errors.append(
            "provider-manifest.provider.supported_activation_modes: must be ['reference-in-place']"
        )
    if provider.get("unsupported_activation_modes") != ["materialize-to-tools"]:
        errors.append(
            "provider-manifest.provider.unsupported_activation_modes: must be ['materialize-to-tools']"
        )

    capabilities = mapping(manifest.get("capabilities"), "provider-manifest.capabilities", errors)
    if set(capabilities) != CAPABILITIES:
        errors.append("provider-manifest.capabilities: must contain exactly analyzers and runtime-validation")
    for name in sorted(CAPABILITIES):
        capability = mapping(capabilities.get(name), f"provider-manifest.capabilities.{name}", errors)
        if capability.get("source_root") != CAPABILITY_SOURCE_ROOTS[name]:
            errors.append(
                f"provider-manifest.capabilities.{name}.source_root: "
                f"must be {CAPABILITY_SOURCE_ROOTS[name]!r}"
            )
        if capability.get("project") != CAPABILITY_PROJECTS[name]:
            errors.append(
                f"provider-manifest.capabilities.{name}.project: "
                f"must be {CAPABILITY_PROJECTS[name]!r}"
            )

    activation = mapping(manifest.get("activation_contract"), "provider-manifest.activation_contract", errors)
    if set(activation.get("state_values", [])) != OUTCOMES:
        errors.append("provider-manifest.activation_contract.state_values: must contain every activation state")
    materialization = mapping(
        activation.get("materialization"),
        "provider-manifest.activation_contract.materialization",
        errors,
    )
    if materialization.get("implementation_status") != "unavailable":
        errors.append(
            "provider-manifest.activation_contract.materialization.implementation_status: "
            "must be 'unavailable'"
        )
    if materialization.get("evaluator_outcome") != "fail-closed":
        errors.append(
            "provider-manifest.activation_contract.materialization.evaluator_outcome: "
            "must be 'fail-closed'"
        )
    if materialization.get("required_target_limitation_evidence") is not True:
        errors.append(
            "provider-manifest.activation_contract.materialization."
            "required_target_limitation_evidence: must be true"
        )
    if materialization.get("required_separate_authorization") is not True:
        errors.append(
            "provider-manifest.activation_contract.materialization."
            "required_separate_authorization: must be true"
        )
    target_ownership = mapping(
        activation.get("target_ownership"),
        "provider-manifest.activation_contract.target_ownership",
        errors,
    )
    if target_ownership.get("provider_evaluator_automation_mutation") != "not-performed":
        errors.append(
            "provider-manifest.activation_contract.target_ownership."
            "provider_evaluator_automation_mutation: must be 'not-performed'"
        )
    if set(target_ownership.get("accepted_applied_statuses", [])) != APPLIED_STATUSES:
        errors.append(
            "provider-manifest.activation_contract.target_ownership."
            "accepted_applied_statuses: must contain verified-existing and applied-by-target-owner"
        )
    precutover = mapping(
        manifest.get("precutover_availability"),
        "provider-manifest.precutover_availability",
        errors,
    )
    architecture_kit = mapping(
        precutover.get("architecture_kit"),
        "provider-manifest.precutover_availability.architecture_kit",
        errors,
    )
    if architecture_kit.get("availability") != "unavailable":
        errors.append(
            "provider-manifest.precutover_availability.architecture_kit.availability: "
            "must be 'unavailable'"
        )
    if architecture_kit.get("lifecycle") != "pre-cutover":
        errors.append(
            "provider-manifest.precutover_availability.architecture_kit.lifecycle: "
            "must be 'pre-cutover'"
        )
    if architecture_kit.get("selectable") is not False:
        errors.append(
            "provider-manifest.precutover_availability.architecture_kit.selectable: must be false"
        )


def validate_capability_shape(capability: str, value: Any, errors: list[str]) -> dict[str, Any]:
    location = f"capabilities.{capability}"
    record = closed_mapping(
        value,
        location,
        {"state", "selection", "wiring", "configuration", "invocation", "evidence_ids"},
        errors,
    )
    if "selection" in record:
        closed_mapping(record["selection"], f"{location}.selection", {"source"}, errors)
    if "wiring" in record:
        closed_mapping(
            record["wiring"],
            f"{location}.wiring",
            {"strategy", "source_path", "target_reference"},
            errors,
        )
    if "configuration" in record:
        closed_mapping(
            record["configuration"],
            f"{location}.configuration",
            {"ownership", "target_reference"},
            errors,
        )
    if "invocation" in record:
        closed_mapping(
            record["invocation"],
            f"{location}.invocation",
            {"command", "evidence_scope"},
            errors,
        )
    if "evidence_ids" in record:
        closed_mapping(record["evidence_ids"], f"{location}.evidence_ids", set(EVIDENCE_KINDS), errors)
    return record


def evidence_index(record: dict[str, Any], errors: list[str]) -> tuple[str, dict[str, dict[str, Any]]]:
    evidence = closed_mapping(record.get("evidence"), "evidence", {"root", "records"}, errors)
    root = evidence.get("root", DEFAULT_EVIDENCE_ROOT)
    if not isinstance(root, str) or not root.strip():
        errors.append("evidence.root: must be a non-empty repository-relative path")
        root = DEFAULT_EVIDENCE_ROOT
    entries = evidence.get("records")
    if not isinstance(entries, list):
        errors.append("evidence.records: must be a list")
        return root, {}
    indexed: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(entries, start=1):
        location = f"evidence.records[{index}]"
        entry = closed_mapping(value, location, {"id", "path", "sha256"}, errors)
        identifier = non_empty_string(entry.get("id"), f"{location}.id", errors)
        non_empty_string(entry.get("path"), f"{location}.path", errors)
        recorded_digest = non_empty_string(entry.get("sha256"), f"{location}.sha256", errors)
        if recorded_digest and not SHA256.fullmatch(recorded_digest):
            errors.append(f"{location}.sha256: must be a lowercase SHA-256 digest")
        if identifier:
            if identifier in indexed:
                errors.append(f"{location}.id: duplicate evidence ID {identifier!r}")
            else:
                indexed[identifier] = entry
    return root, indexed


def verify_evidence(
    identifier: str,
    capability: str,
    kind: str,
    expected_statuses: set[str],
    index: dict[str, dict[str, Any]],
    evidence_root: Path,
    record: dict[str, Any],
    errors: list[str],
) -> None:
    location = f"capabilities.{capability}.evidence_ids.{kind}"
    entry = index.get(identifier)
    if entry is None:
        errors.append(f"{location}: evidence ID {identifier!r} is not declared")
        return
    path = safe_regular_file(evidence_root, entry.get("path"), f"evidence[{identifier}].path", errors)
    if path is None:
        return
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"evidence[{identifier}]: cannot read evidence file: {exc}")
        return
    if entry.get("sha256") != digest_bytes(raw):
        errors.append(f"evidence[{identifier}]: recorded sha256 does not match raw file bytes")
        return
    try:
        metadata = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"evidence[{identifier}]: invalid YAML metadata: {exc}")
        return
    metadata = closed_mapping(
        metadata,
        f"evidence[{identifier}]",
        {
            "schema_version",
            "evidence_id",
            "provider_id",
            "framework_commit",
            "capability",
            "kind",
            "status",
            "target_plan_sha256",
        },
        errors,
    )
    framework = record.get("framework")
    framework_commit = framework.get("commit") if isinstance(framework, dict) else None
    expected_values = {
        "schema_version": SCHEMA_VERSION,
        "evidence_id": identifier,
        "provider_id": PROVIDER_ID,
        "framework_commit": framework_commit,
        "capability": capability,
        "kind": kind,
        "target_plan_sha256": record.get("target_plan_sha256"),
    }
    for key, expected in expected_values.items():
        if metadata.get(key) != expected:
            errors.append(f"evidence[{identifier}].{key}: must match the activation record")
    if metadata.get("status") not in expected_statuses:
        errors.append(
            f"evidence[{identifier}].status: must be one of {sorted(expected_statuses)} for {kind}"
        )


def verify_active_evidence(
    record: dict[str, Any],
    capabilities: dict[str, dict[str, Any]],
    provider_manifest_bytes: bytes | None,
    repository_root: Path | None,
    provider_root: Path | None,
    errors: list[str],
) -> None:
    if provider_manifest_bytes is None or repository_root is None or provider_root is None:
        errors.append(
            "active-reference-in-place: verified evidence context requires repository_root, "
            "provider_root, and raw provider manifest bytes"
        )
        return
    resolved_provider_root = canonical_provider_root(repository_root, provider_root, errors)
    if resolved_provider_root is None:
        return
    verify_canonical_provider_files(resolved_provider_root, provider_manifest_bytes, errors)
    if record.get("provider_manifest_sha256") != digest_bytes(provider_manifest_bytes):
        errors.append("provider_manifest_sha256: must match raw provider-manifest.yaml bytes")
    if record.get("target_plan_sha256") != digest_value(record.get("target_plan")):
        errors.append("target_plan_sha256: must match the deterministic target_plan digest")
    evidence_root_path, index = evidence_index(record, errors)
    root = safe_directory(repository_root, evidence_root_path, "evidence.root", errors)
    if root is None:
        return
    used_ids: set[str] = set()
    for capability in sorted(capabilities):
        evidence_ids = mapping(
            capabilities[capability].get("evidence_ids"),
            f"capabilities.{capability}.evidence_ids",
            errors,
        )
        for kind, statuses in (
            ("wiring", APPLIED_STATUSES),
            ("configuration", APPLIED_STATUSES),
            ("invocation", {"passed"}),
        ):
            identifier = concrete_string(
                evidence_ids.get(kind),
                f"capabilities.{capability}.evidence_ids.{kind}",
                errors,
            )
            if not identifier:
                continue
            if identifier in used_ids:
                errors.append(f"evidence ID {identifier!r}: must not prove more than one capability/kind")
                continue
            used_ids.add(identifier)
            verify_evidence(identifier, capability, kind, statuses, index, root, record, errors)


def validate_active_capability(
    capability: str,
    record: dict[str, Any],
    errors: list[str],
) -> None:
    location = f"capabilities.{capability}"
    if record.get("state") != "active-reference-in-place":
        errors.append(f"{location}.state: must match active-reference-in-place")
    selection = non_empty_mapping(record.get("selection"), f"{location}.selection", errors)
    concrete_string(selection.get("source"), f"{location}.selection.source", errors)
    wiring = non_empty_mapping(record.get("wiring"), f"{location}.wiring", errors)
    concrete_string(wiring.get("strategy"), f"{location}.wiring.strategy", errors)
    source_path = concrete_string(wiring.get("source_path"), f"{location}.wiring.source_path", errors)
    if source_path != CANONICAL_ROOT + CAPABILITY_PROJECTS[capability]:
        errors.append(
            f"{location}.wiring.source_path: must be "
            f"{CANONICAL_ROOT + CAPABILITY_PROJECTS[capability]!r}"
        )
    concrete_string(wiring.get("target_reference"), f"{location}.wiring.target_reference", errors)
    configuration = non_empty_mapping(record.get("configuration"), f"{location}.configuration", errors)
    if configuration.get("ownership") != "target-owned":
        errors.append(f"{location}.configuration.ownership: must be 'target-owned'")
    concrete_string(configuration.get("target_reference"), f"{location}.configuration.target_reference", errors)
    invocation = non_empty_mapping(record.get("invocation"), f"{location}.invocation", errors)
    concrete_string(invocation.get("command"), f"{location}.invocation.command", errors)
    concrete_string(invocation.get("evidence_scope"), f"{location}.invocation.evidence_scope", errors)


def evaluate(
    record: dict[str, Any],
    manifest: dict[str, Any],
    *,
    provider_manifest_bytes: bytes | None = None,
    repository_root: Path | None = None,
    provider_root: Path | None = None,
) -> list[str]:
    """Return contract violations; active proof reads only explicit evidence files."""
    errors: list[str] = []
    manifest_capabilities(manifest, errors)
    record = closed_mapping(
        record,
        "activation-record",
        {
            "schema_version",
            "record_id",
            "provider",
            "framework",
            "canonical_root",
            "provider_manifest_sha256",
            "outcome",
            "freshness",
            "selected_capabilities",
            "target_plan",
            "target_plan_sha256",
            "evidence",
            "capabilities",
        },
        errors,
    )
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: must be {SCHEMA_VERSION!r}")
    non_empty_string(record.get("record_id"), "record_id", errors)
    provider = closed_mapping(record.get("provider"), "provider", {"id"}, errors)
    if provider.get("id") != PROVIDER_ID:
        errors.append(f"provider.id: must be {PROVIDER_ID!r}")
    framework = closed_mapping(record.get("framework"), "framework", {"version", "commit"}, errors)
    non_empty_string(framework.get("version"), "framework.version", errors)
    commit = non_empty_string(framework.get("commit"), "framework.commit", errors)
    if commit and not SHA40.fullmatch(commit):
        errors.append("framework.commit: must be a lowercase 40-character Git SHA")
    if record.get("canonical_root") != CANONICAL_ROOT:
        errors.append(f"canonical_root: must be {CANONICAL_ROOT!r}")

    outcome = record.get("outcome")
    if outcome not in OUTCOMES:
        errors.append(f"outcome: must be one of {sorted(OUTCOMES)}")
        outcome = ""
    freshness = record.get("freshness")
    if freshness not in FRESHNESS:
        errors.append(f"freshness: must be one of {sorted(FRESHNESS)}")
    elif outcome == "active-reference-in-place" and freshness != "fresh":
        errors.append("freshness: active-reference-in-place requires declared freshness 'fresh'")
    elif outcome == "stale" and freshness != "stale":
        errors.append("freshness: stale outcome requires declared freshness 'stale'")
    elif outcome == "unresolved" and freshness != "unresolved":
        errors.append("freshness: unresolved outcome requires declared freshness 'unresolved'")

    selected = record.get("selected_capabilities")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        errors.append("selected_capabilities: must be a list of capability IDs")
        selected = []
    if len(set(selected)) != len(selected):
        errors.append("selected_capabilities: must not contain duplicates")
    unknown = set(selected) - CAPABILITIES
    if unknown:
        errors.append(f"selected_capabilities: unknown capability IDs {sorted(unknown)}")
    selected_set = set(selected) & CAPABILITIES

    target_plan = closed_mapping(
        record.get("target_plan"),
        "target_plan",
        {
            "plan_id",
            "activation_mode",
            "target_repository",
            "provider_evaluator_automation_mutation",
            "source_copy",
            "target_limitation_evidence",
            "separate_authorization",
        },
        errors,
    )
    non_empty_string(target_plan.get("plan_id"), "target_plan.plan_id", errors)
    non_empty_string(target_plan.get("target_repository"), "target_plan.target_repository", errors)
    if target_plan.get("activation_mode") not in {"none", "reference-in-place", "materialize-to-tools"}:
        errors.append("target_plan.activation_mode: must be none, reference-in-place, or materialize-to-tools")
    if target_plan.get("provider_evaluator_automation_mutation") != "not-performed":
        errors.append("target_plan.provider_evaluator_automation_mutation: must be 'not-performed'")
    if target_plan.get("source_copy") is not False:
        errors.append("target_plan.source_copy: must be false; production provider source must stay in place")

    capabilities = mapping(record.get("capabilities"), "capabilities", errors)
    configured = set(capabilities)
    unexpected = configured - CAPABILITIES
    if unexpected:
        errors.append(f"capabilities: unknown capability records {sorted(unexpected)}")
    if configured & CAPABILITIES != selected_set:
        errors.append("capabilities: must contain exactly the selected capability records")
    capability_records = {
        capability: validate_capability_shape(capability, capabilities.get(capability), errors)
        for capability in sorted(configured & CAPABILITIES)
    }

    if outcome == "source-available":
        if selected_set:
            errors.append("source-available: must not select a capability")
        if target_plan.get("activation_mode") != "none":
            errors.append("source-available: target_plan.activation_mode must be 'none'")
    elif outcome == "active-reference-in-place":
        if not selected_set:
            errors.append("active-reference-in-place: at least one capability must be selected")
        if target_plan.get("activation_mode") != "reference-in-place":
            errors.append("active-reference-in-place: target_plan.activation_mode must be 'reference-in-place'")
        for capability in sorted(selected_set):
            validate_active_capability(capability, capability_records.get(capability, {}), errors)
        verify_active_evidence(
            record,
            {capability: capability_records.get(capability, {}) for capability in selected_set},
            provider_manifest_bytes,
            repository_root,
            provider_root,
            errors,
        )
    elif outcome in {"stale", "unresolved"}:
        if not selected_set:
            errors.append(f"{outcome}: must name the partial or contradictory selected capability")
        for capability in sorted(selected_set):
            state = capability_records.get(capability, {}).get("state")
            if state not in {"stale", "unresolved"}:
                errors.append(f"capabilities.{capability}.state: partial setup must be stale or unresolved")
    elif outcome == "active-materialized":
        errors.append("active-materialized: unsupported because materialization implementation is unavailable")

    if target_plan.get("activation_mode") == "materialize-to-tools":
        if not isinstance(target_plan.get("target_limitation_evidence"), list) or not target_plan["target_limitation_evidence"]:
            errors.append("materialize-to-tools: target_limitation_evidence is required")
        if not isinstance(target_plan.get("separate_authorization"), str) or not target_plan["separate_authorization"].strip():
            errors.append("materialize-to-tools: separate_authorization is required")
        errors.append("materialize-to-tools: unsupported because implementation is unavailable")
    elif outcome == "active-materialized":
        errors.append("active-materialized: target_plan.activation_mode must be materialize-to-tools")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a bundled-provider activation record.")
    parser.add_argument("--record", type=Path, required=True, help="Activation-record YAML path.")
    parser.add_argument(
        "--provider-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Provider root containing provider-manifest.yaml.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Explicit repository root required to verify an active record's evidence files.",
    )
    arguments = parser.parse_args()
    record, _, record_errors = load_yaml_file(arguments.record)
    manifest, manifest_bytes, manifest_errors = load_yaml_file(arguments.provider_root / "provider-manifest.yaml")
    errors = record_errors + manifest_errors
    if record is not None and manifest is not None:
        errors.extend(
            evaluate(
                record,
                manifest,
                provider_manifest_bytes=manifest_bytes,
                repository_root=arguments.repository_root,
                provider_root=arguments.provider_root,
            )
        )
    if errors:
        print("Bundled provider activation evaluation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Bundled provider activation evaluation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
