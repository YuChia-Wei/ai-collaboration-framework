#!/usr/bin/env python3
"""Fail-closed, read-only evaluator for Architecture Kit readiness records."""

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
RECORD_TYPE = "architecture-kit-readiness-record"
CRITERIA = (
    "immutable_package_identity",
    "diagnostic_constraint_crosswalk",
    "behavior_parity",
    "consumer_guidance",
    "compatible_profile_range",
    "real_target_proof",
    "migration_rollback_proof",
    "owner_cutover_approval",
)
CRITERION_STATES = {"verified", "unavailable", "stale", "incompatible", "unresolved", "source-only"}
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PLACEHOLDER = re.compile(r"<[^>]+>")


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.YAMLError(f"duplicate mapping key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def load_yaml_file(path: Path) -> tuple[dict[str, Any] | None, bytes | None, list[str]]:
    try:
        raw = path.read_bytes()
        value = yaml.load(raw.decode("utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return None, None, [f"{path}: cannot read YAML: {exc}"]
    if not isinstance(value, dict):
        return None, raw, [f"{path}: top-level YAML value must be a mapping"]
    return value, raw, []


def parse_yaml_bytes(raw: bytes, location: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=UniqueKeyLoader)
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{location}: cannot parse YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{location}: top-level YAML value must be a mapping")
        return None
    return value


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{location}: must be a mapping")
    return {}


def closed_mapping(value: Any, location: str, allowed: set[str], errors: list[str]) -> dict[str, Any]:
    result = mapping(value, location, errors)
    unknown = set(result) - allowed
    if unknown:
        errors.append(f"{location}: unexpected keys {sorted(unknown)}")
    return result


def non_empty_string(value: Any, location: str, errors: list[str]) -> str:
    if isinstance(value, str) and value.strip():
        return value
    errors.append(f"{location}: must be a non-empty string")
    return ""


def sha256(value: Any, location: str, errors: list[str]) -> str:
    value = non_empty_string(value, location, errors)
    if value and not SHA256.fullmatch(value):
        errors.append(f"{location}: must be a lowercase SHA-256 digest")
    return value


def safe_relative_path(value: Any, location: str, errors: list[str]) -> tuple[str, ...] | None:
    value = non_empty_string(value, location, errors)
    if not value:
        return None
    if value.startswith(("/", "\\")) or "\\" in value:
        errors.append(f"{location}: must be a safe repository-relative slash-separated path")
        return None
    parts = tuple(value.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        errors.append(f"{location}: must not contain empty, '.' or '..' path segments")
        return None
    return parts


def safe_directory(repository_root: Path, value: Any, location: str, errors: list[str]) -> Path | None:
    parts = safe_relative_path(value, location, errors)
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
        root = repository_root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        errors.append(f"{location}: cannot resolve evidence root: {exc}")
        return None
    if not resolved.is_relative_to(root):
        errors.append(f"{location}: evidence root escapes repository root")
        return None
    return resolved


def safe_regular_file(root: Path, value: Any, location: str, errors: list[str]) -> Path | None:
    parts = safe_relative_path(value, location, errors)
    if parts is None:
        return None
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"{location}: must not traverse symlink {current}")
            return None
    if candidate.is_symlink() or not candidate.is_file():
        errors.append(f"{location}: must resolve to a regular non-symlink file")
        return None
    try:
        if not candidate.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
            errors.append(f"{location}: regular file escapes its required root")
            return None
    except OSError as exc:
        errors.append(f"{location}: cannot resolve evidence file: {exc}")
        return None
    return candidate


def canonical_provider_root(repository_root: Path, provider_root: Path, errors: list[str]) -> Path | None:
    try:
        root = repository_root.resolve(strict=True)
    except OSError as exc:
        errors.append(f"repository_root: cannot resolve repository root: {exc}")
        return None
    expected = root.joinpath(*CANONICAL_ROOT.rstrip("/").split("/"))
    current = root
    for part in CANONICAL_ROOT.rstrip("/").split("/"):
        current = current / part
        if current.is_symlink():
            errors.append(f"canonical provider root: must not traverse symlink {current}")
            return None
    if provider_root.is_symlink() or not expected.is_dir():
        errors.append("provider_root: must be the regular canonical provider root")
        return None
    try:
        if provider_root.resolve(strict=True) != expected.resolve(strict=True):
            errors.append("provider_root: must resolve to the canonical provider root under repository_root")
            return None
    except OSError as exc:
        errors.append(f"provider_root: cannot resolve provider root: {exc}")
        return None
    return expected


def canonical_manifest(manifest: dict[str, Any], manifest_bytes: bytes | None, repository_root: Path | None, provider_root: Path | None, errors: list[str]) -> tuple[dict[str, Any], bytes | None]:
    if manifest_bytes is None or repository_root is None or provider_root is None:
        errors.append("provider_binding: requires raw canonical provider-manifest bytes, repository_root, and provider_root")
        return {}, None
    root = canonical_provider_root(repository_root, provider_root, errors)
    if root is None:
        return {}, None
    path = safe_regular_file(root, "provider-manifest.yaml", "canonical provider manifest", errors)
    if path is None:
        return {}, None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"canonical provider manifest: cannot read manifest: {exc}")
        return {}, None
    if raw != manifest_bytes:
        errors.append("provider-manifest: supplied raw bytes differ from the physical canonical manifest")
    parsed = parse_yaml_bytes(raw, "canonical provider manifest", errors)
    if parsed is None:
        return {}, raw
    if manifest != parsed:
        errors.append("provider-manifest: supplied mapping differs from the raw canonical manifest")
    return parsed, raw


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    top = closed_mapping(manifest, "provider-manifest", {"schema_version", "provider", "capabilities", "activation_contract", "precutover_availability", "architecture_kit_readiness_contract"}, errors)
    if top.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"provider-manifest.schema_version: must be {SCHEMA_VERSION!r}")
    provider = closed_mapping(top.get("provider"), "provider-manifest.provider", {"id", "canonical_root", "owner_component", "delivery_state", "default_activation_state", "source_delivery", "supported_activation_modes", "unsupported_activation_modes"}, errors)
    if provider.get("id") != PROVIDER_ID:
        errors.append(f"provider-manifest.provider.id: must be {PROVIDER_ID!r}")
    if provider.get("canonical_root") != CANONICAL_ROOT:
        errors.append(f"provider-manifest.provider.canonical_root: must be {CANONICAL_ROOT!r}")
    precutover = closed_mapping(top.get("precutover_availability"), "provider-manifest.precutover_availability", {"architecture_kit"}, errors)
    kit = closed_mapping(precutover.get("architecture_kit"), "provider-manifest.precutover_availability.architecture_kit", {"availability", "lifecycle", "selectable", "reason"}, errors)
    if (kit.get("availability"), kit.get("lifecycle"), kit.get("selectable")) != ("unavailable", "pre-cutover", False):
        errors.append("provider-manifest.precutover_availability.architecture_kit: must remain unavailable, pre-cutover, and non-selectable")
    contract = closed_mapping(top.get("architecture_kit_readiness_contract"), "provider-manifest.architecture_kit_readiness_contract", {"record_schema", "record_template", "current_fixture", "evaluator", "required_criteria", "criterion_states", "current_package_version_status", "source_presence_is_provider_availability", "planned_package_is_provider_availability", "repository_project_is_provider_availability", "preview_or_dual_run_is_cutover_proof", "evaluation", "future_cutover"}, errors)
    expected_paths = {"record_schema": "schemas/architecture-kit-readiness-record.schema.yaml", "record_template": "templates/architecture-kit-readiness-record.yaml", "current_fixture": "fixtures/architecture-kit-unavailable/readiness-record.yaml", "evaluator": "scripts/evaluate-architecture-kit-readiness.py"}
    for key, expected in expected_paths.items():
        if contract.get(key) != expected:
            errors.append(f"provider-manifest.architecture_kit_readiness_contract.{key}: must be {expected!r}")
    if contract.get("required_criteria") != list(CRITERIA):
        errors.append("provider-manifest.architecture_kit_readiness_contract.required_criteria: must be the exact canonical ordered criteria")
    if contract.get("criterion_states") != ["verified", "unavailable", "stale", "incompatible", "unresolved", "source-only"]:
        errors.append("provider-manifest.architecture_kit_readiness_contract.criterion_states: must be the exact canonical states")
    for key in ("source_presence_is_provider_availability", "planned_package_is_provider_availability", "repository_project_is_provider_availability", "preview_or_dual_run_is_cutover_proof"):
        if contract.get(key) is not False:
            errors.append(f"provider-manifest.architecture_kit_readiness_contract.{key}: must be false")
    if contract.get("current_package_version_status") != "unavailable":
        errors.append("provider-manifest.architecture_kit_readiness_contract.current_package_version_status: must be 'unavailable'")
    evaluation = closed_mapping(contract.get("evaluation"), "provider-manifest.architecture_kit_readiness_contract.evaluation", {"any_non_verified_criterion", "all_verified_criteria", "all_verified_selection", "grants_cutover_authorization", "evaluator_side_effects"}, errors)
    if evaluation != {"any_non_verified_criterion": "unsupported", "all_verified_criteria": "evidence-complete", "all_verified_selection": "not-selected", "grants_cutover_authorization": False, "evaluator_side_effects": "none"}:
        errors.append("provider-manifest.architecture_kit_readiness_contract.evaluation: must keep the closed non-authorizing semantics")
    future = closed_mapping(contract.get("future_cutover"), "provider-manifest.architecture_kit_readiness_contract.future_cutover", {"breaking", "preview_or_dual_run", "remove_bundled_source", "legacy_provider", "requires_explicit_owner_authorization"}, errors)
    if future != {"breaking": True, "preview_or_dual_run": False, "remove_bundled_source": True, "legacy_provider": False, "requires_explicit_owner_authorization": True}:
        errors.append("provider-manifest.architecture_kit_readiness_contract.future_cutover: must keep the closed breaking topology")


def validate_binding(record: dict[str, Any], raw_manifest: bytes | None, errors: list[str]) -> dict[str, Any]:
    binding = closed_mapping(record.get("provider_binding"), "provider_binding", {"provider_id", "canonical_root", "framework_version", "framework_commit", "provider_manifest_sha256"}, errors)
    if binding.get("provider_id") != PROVIDER_ID:
        errors.append(f"provider_binding.provider_id: must be {PROVIDER_ID!r}")
    if binding.get("canonical_root") != CANONICAL_ROOT:
        errors.append(f"provider_binding.canonical_root: must be {CANONICAL_ROOT!r}")
    framework_version = non_empty_string(binding.get("framework_version"), "provider_binding.framework_version", errors)
    if framework_version and (PLACEHOLDER.search(framework_version) or framework_version == "unavailable"):
        errors.append("provider_binding.framework_version: must be an exact concrete framework version")
    commit = non_empty_string(binding.get("framework_commit"), "provider_binding.framework_commit", errors)
    if commit and not SHA40.fullmatch(commit):
        errors.append("provider_binding.framework_commit: must be a lowercase 40-character Git SHA")
    digest = sha256(binding.get("provider_manifest_sha256"), "provider_binding.provider_manifest_sha256", errors)
    if raw_manifest is not None and digest and digest != digest_bytes(raw_manifest):
        errors.append("provider_binding.provider_manifest_sha256: must match raw provider-manifest.yaml bytes")
    return binding


def evidence_index(record: dict[str, Any], errors: list[str]) -> tuple[str, dict[str, dict[str, Any]]]:
    evidence = closed_mapping(record.get("evidence"), "evidence", {"root", "records"}, errors)
    root = non_empty_string(evidence.get("root"), "evidence.root", errors)
    if root:
        safe_relative_path(root, "evidence.root", errors)
    entries = evidence.get("records")
    if not isinstance(entries, list):
        errors.append("evidence.records: must be a list")
        return root, {}
    indexed: dict[str, dict[str, Any]] = {}
    for number, value in enumerate(entries, start=1):
        location = f"evidence.records[{number}]"
        entry = closed_mapping(value, location, {"id", "path", "sha256"}, errors)
        identifier = non_empty_string(entry.get("id"), f"{location}.id", errors)
        safe_relative_path(entry.get("path"), f"{location}.path", errors)
        sha256(entry.get("sha256"), f"{location}.sha256", errors)
        if identifier:
            if identifier in indexed:
                errors.append(f"{location}.id: duplicate evidence ID {identifier!r}")
            else:
                indexed[identifier] = entry
    return root, indexed


def validate_criteria(record: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    values = record.get("criteria")
    if not isinstance(values, list):
        errors.append("criteria: must be a list")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for number, value in enumerate(values, start=1):
        location = f"criteria[{number}]"
        criterion = closed_mapping(value, location, {"id", "state", "evidence_ids"}, errors)
        identifier = non_empty_string(criterion.get("id"), f"{location}.id", errors)
        if identifier and identifier not in CRITERIA:
            errors.append(f"{location}.id: unknown criterion {identifier!r}")
        if identifier in indexed:
            errors.append(f"{location}.id: duplicate criterion {identifier!r}")
        elif identifier in CRITERIA:
            indexed[identifier] = criterion
        state = criterion.get("state")
        if state not in CRITERION_STATES:
            errors.append(f"{location}.state: must be one of {sorted(CRITERION_STATES)}")
        evidence_ids = criterion.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not all(isinstance(item, str) and item for item in evidence_ids):
            errors.append(f"{location}.evidence_ids: must be a list of non-empty evidence IDs")
        elif len(set(evidence_ids)) != len(evidence_ids):
            errors.append(f"{location}.evidence_ids: must not contain duplicates")
        elif state == "verified" and not evidence_ids:
            errors.append(f"{location}.evidence_ids: verified criterion requires file-backed evidence")
        elif state != "verified" and evidence_ids:
            errors.append(f"{location}.evidence_ids: non-verified criterion must expose its gap without evidence fallback")
    missing = sorted(set(CRITERIA) - set(indexed))
    if missing:
        errors.append(f"criteria: missing required criteria {missing}")
    return indexed


def validate_payload(criterion: str, payload: Any, record: dict[str, Any], location: str, errors: list[str]) -> None:
    package = mapping(record.get("architecture_kit"), "architecture_kit", errors)
    if criterion == "immutable_package_identity":
        value = closed_mapping(payload, location, {"package_id", "package_version", "package_digest", "publication_reference"}, errors)
        if package.get("package_version_status") != "available":
            errors.append(f"{location}: immutable package identity requires package_version_status 'available'")
        if value.get("package_id") != package.get("package_id") or value.get("package_version") != package.get("package_version"):
            errors.append(f"{location}: package ID and version must exactly match architecture_kit")
        if any(
            not isinstance(value.get(key), str)
            or value.get(key) == "unavailable"
            or PLACEHOLDER.search(value.get(key))
            for key in ("package_id", "package_version")
        ):
            errors.append(f"{location}: package ID and version must be concrete")
        sha256(value.get("package_digest"), f"{location}.package_digest", errors)
        non_empty_string(value.get("publication_reference"), f"{location}.publication_reference", errors)
    elif criterion == "diagnostic_constraint_crosswalk":
        value = closed_mapping(payload, location, {"bindings", "unmapped_diagnostics"}, errors)
        bindings = value.get("bindings")
        if not isinstance(bindings, list) or not bindings:
            errors.append(f"{location}.bindings: must be a non-empty list")
        else:
            for number, binding in enumerate(bindings, start=1):
                binding = closed_mapping(binding, f"{location}.bindings[{number}]", {"diagnostic_id", "constraint_id"}, errors)
                non_empty_string(binding.get("diagnostic_id"), f"{location}.bindings[{number}].diagnostic_id", errors)
                non_empty_string(binding.get("constraint_id"), f"{location}.bindings[{number}].constraint_id", errors)
        if value.get("unmapped_diagnostics") != []:
            errors.append(f"{location}.unmapped_diagnostics: must be an empty list")
    elif criterion == "behavior_parity":
        value = closed_mapping(payload, location, {"scenarios", "failed_scenarios", "mismatched_scenarios", "equivalence"}, errors)
        scenarios = value.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            errors.append(f"{location}.scenarios: must be a non-empty list")
        else:
            for number, scenario in enumerate(scenarios, start=1):
                scenario = closed_mapping(scenario, f"{location}.scenarios[{number}]", {"scenario_id", "result"}, errors)
                non_empty_string(scenario.get("scenario_id"), f"{location}.scenarios[{number}].scenario_id", errors)
                if scenario.get("result") != "passed":
                    errors.append(f"{location}.scenarios[{number}].result: must be 'passed'")
        if value.get("failed_scenarios") != [] or value.get("mismatched_scenarios") != [] or value.get("equivalence") != "equivalent":
            errors.append(f"{location}: requires empty failed/mismatched scenarios and equivalence 'equivalent'")
    elif criterion == "consumer_guidance":
        value = closed_mapping(payload, location, {"guidance_reference", "guidance_digest"}, errors)
        non_empty_string(value.get("guidance_reference"), f"{location}.guidance_reference", errors)
        sha256(value.get("guidance_digest"), f"{location}.guidance_digest", errors)
    elif criterion == "compatible_profile_range":
        value = closed_mapping(payload, location, {"profile", "compatibility_range"}, errors)
        if value.get("profile") != "dotnet-backend":
            errors.append(f"{location}.profile: must be 'dotnet-backend'")
        non_empty_string(value.get("compatibility_range"), f"{location}.compatibility_range", errors)
    elif criterion == "real_target_proof":
        value = closed_mapping(payload, location, {"target_identity", "target_commit", "invocation", "result"}, errors)
        non_empty_string(value.get("target_identity"), f"{location}.target_identity", errors)
        commit = non_empty_string(value.get("target_commit"), f"{location}.target_commit", errors)
        if commit and not SHA40.fullmatch(commit):
            errors.append(f"{location}.target_commit: must be a lowercase 40-character Git SHA")
        non_empty_string(value.get("invocation"), f"{location}.invocation", errors)
        if value.get("result") != "passed":
            errors.append(f"{location}.result: must be 'passed'")
    elif criterion == "migration_rollback_proof":
        value = closed_mapping(payload, location, {"migration", "rollback"}, errors)
        for key in ("migration", "rollback"):
            result = closed_mapping(value.get(key), f"{location}.{key}", {"plan_reference", "result"}, errors)
            non_empty_string(result.get("plan_reference"), f"{location}.{key}.plan_reference", errors)
            if result.get("result") != "passed":
                errors.append(f"{location}.{key}.result: must be 'passed'")
    elif criterion == "owner_cutover_approval":
        value = closed_mapping(payload, location, {"decision_reference", "decision_digest", "scope", "execution_authorization"}, errors)
        non_empty_string(value.get("decision_reference"), f"{location}.decision_reference", errors)
        sha256(value.get("decision_digest"), f"{location}.decision_digest", errors)
        if value.get("scope") != "readiness-gate":
            errors.append(f"{location}.scope: must be 'readiness-gate'")
        if value.get("execution_authorization") is not False:
            errors.append(f"{location}.execution_authorization: must be false")


def verify_referenced_evidence(record: dict[str, Any], criteria: dict[str, dict[str, Any]], repository_root: Path | None, errors: list[str]) -> None:
    root_value, entries = evidence_index(record, errors)
    referenced = [identifier for criterion in CRITERIA if criterion in criteria for identifier in criteria[criterion].get("evidence_ids", [])]
    if len(set(referenced)) != len(referenced):
        errors.append("evidence.records: evidence IDs must not be reused across criteria")
    missing = sorted(set(referenced) - set(entries))
    if missing:
        errors.append(f"evidence.records: referenced evidence IDs are not declared {missing}")
    unreferenced = sorted(set(entries) - set(referenced))
    if unreferenced:
        errors.append(f"evidence.records: unreferenced evidence IDs {unreferenced}")
    if repository_root is None:
        if referenced:
            errors.append("evidence: verified criteria require an explicit repository_root")
        return
    if not entries:
        return
    root = safe_directory(repository_root, root_value, "evidence.root", errors)
    if root is None:
        return
    binding = mapping(record.get("provider_binding"), "provider_binding", errors)
    owners = {identifier: criterion for criterion in CRITERIA if criterion in criteria for identifier in criteria[criterion].get("evidence_ids", [])}
    for identifier, entry in entries.items():
        criterion = owners.get(identifier)
        if criterion is None:
            continue
        path = safe_regular_file(root, entry.get("path"), f"evidence[{identifier}].path", errors)
        if path is None:
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"evidence[{identifier}]: cannot read evidence: {exc}")
            continue
        if entry.get("sha256") != digest_bytes(raw):
            errors.append(f"evidence[{identifier}]: recorded sha256 does not match raw file bytes")
            continue
        metadata = parse_yaml_bytes(raw, f"evidence[{identifier}]", errors)
        if metadata is None:
            continue
        metadata = closed_mapping(metadata, f"evidence[{identifier}]", {"schema_version", "evidence_id", "provider_id", "framework_version", "framework_commit", "provider_manifest_sha256", "criterion", "status", "payload"}, errors)
        expected = {"schema_version": SCHEMA_VERSION, "evidence_id": identifier, "provider_id": PROVIDER_ID, "framework_version": binding.get("framework_version"), "framework_commit": binding.get("framework_commit"), "provider_manifest_sha256": binding.get("provider_manifest_sha256"), "criterion": criterion, "status": "verified"}
        for key, expected_value in expected.items():
            if metadata.get(key) != expected_value:
                errors.append(f"evidence[{identifier}].{key}: must match the readiness record")
        validate_payload(criterion, metadata.get("payload"), record, f"evidence[{identifier}].payload", errors)


def output_binding(record: dict[str, Any]) -> dict[str, Any]:
    binding = record.get("provider_binding") if isinstance(record.get("provider_binding"), dict) else {}
    package = record.get("architecture_kit") if isinstance(record.get("architecture_kit"), dict) else {}
    return {"provider_id": binding.get("provider_id"), "framework_version": binding.get("framework_version"), "framework_commit": binding.get("framework_commit"), "provider_manifest_sha256": binding.get("provider_manifest_sha256"), "architecture_kit_package_id": package.get("package_id"), "architecture_kit_package_version": package.get("package_version"), "architecture_kit_package_version_status": package.get("package_version_status")}


def evaluate(record: dict[str, Any], manifest: dict[str, Any], *, provider_manifest_bytes: bytes | None = None, repository_root: Path | None = None, provider_root: Path | None = None) -> dict[str, Any]:
    """Evaluate declared local evidence only; never select, execute, or authorize cutover."""
    errors: list[str] = []
    canonical, raw_manifest = canonical_manifest(manifest, provider_manifest_bytes, repository_root, provider_root, errors)
    if canonical:
        validate_manifest(canonical, errors)
    record = closed_mapping(record, "readiness-record", {"schema_version", "record_type", "record_id", "provider_binding", "architecture_kit", "current_state", "deferred_targets", "evidence", "criteria", "future_cutover"}, errors)
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: must be {SCHEMA_VERSION!r}")
    if record.get("record_type") != RECORD_TYPE:
        errors.append(f"record_type: must be {RECORD_TYPE!r}")
    non_empty_string(record.get("record_id"), "record_id", errors)
    validate_binding(record, raw_manifest, errors)
    package = closed_mapping(record.get("architecture_kit"), "architecture_kit", {"package_id", "package_version", "package_version_status"}, errors)
    package_id = non_empty_string(package.get("package_id"), "architecture_kit.package_id", errors)
    package_version = non_empty_string(package.get("package_version"), "architecture_kit.package_version", errors)
    status = package.get("package_version_status")
    if status not in {"unavailable", "unresolved", "available"}:
        errors.append("architecture_kit.package_version_status: must be unavailable, unresolved, or available")
    if status == "unavailable" and (package_id != "unavailable" or package_version != "unavailable"):
        errors.append("architecture_kit: unavailable package status must not fabricate a package identity or version")
    if status == "available" and (PLACEHOLDER.search(package_id) or PLACEHOLDER.search(package_version) or package_id == "unavailable" or package_version == "unavailable"):
        errors.append("architecture_kit: available package status requires concrete immutable package identity and version")
    current = closed_mapping(record.get("current_state"), "current_state", {"availability", "lifecycle", "selectable", "source_presence_is_availability", "planned_package_is_availability", "repo_project_is_availability", "preview_or_dual_run_is_cutover_proof"}, errors)
    expected_current = {"availability": "unavailable", "lifecycle": "pre-cutover", "selectable": False, "source_presence_is_availability": False, "planned_package_is_availability": False, "repo_project_is_availability": False, "preview_or_dual_run_is_cutover_proof": False}
    for key, expected in expected_current.items():
        if current.get(key) != expected:
            errors.append(f"current_state.{key}: must be {expected!r}")
    targets = record.get("deferred_targets")
    if not isinstance(targets, list) or not targets:
        errors.append("deferred_targets: must be a non-empty list")
    else:
        for number, target in enumerate(targets, start=1):
            target = closed_mapping(target, f"deferred_targets[{number}]", {"target", "gap", "required_action"}, errors)
            for key in ("target", "gap", "required_action"):
                non_empty_string(target.get(key), f"deferred_targets[{number}].{key}", errors)
    criteria = validate_criteria(record, errors)
    future = closed_mapping(record.get("future_cutover"), "future_cutover", {"breaking", "preview_or_dual_run", "remove_bundled_source", "legacy_provider", "requires_explicit_owner_authorization", "evaluator_may_execute", "evaluator_may_authorize"}, errors)
    expected_future = {"breaking": True, "preview_or_dual_run": False, "remove_bundled_source": True, "legacy_provider": False, "requires_explicit_owner_authorization": True, "evaluator_may_execute": False, "evaluator_may_authorize": False}
    if future != expected_future:
        errors.append("future_cutover: must keep the closed breaking and non-authorizing topology")
    verified = {criterion for criterion in CRITERIA if criterion in criteria and criteria[criterion].get("state") == "verified"}
    if verified:
        verify_referenced_evidence(record, criteria, repository_root, errors)
    else:
        root, entries = evidence_index(record, errors)
        if entries:
            errors.append("evidence.records: non-verified readiness records must not declare evidence entries")
    all_verified = len(verified) == len(CRITERIA)
    if all_verified and status != "available":
        errors.append("architecture_kit.package_version_status: all verified criteria require an available package version")
    valid = not errors
    readiness = "evidence-complete" if valid and all_verified else "unsupported" if valid else "invalid"
    return {"valid": valid, "readiness": readiness, "availability": "unavailable", "selectable": False, "selection": "not-selected" if readiness == "evidence-complete" else "not-selectable", "cutover_authorization": "not-granted", "side_effects": "none", "binding": output_binding(record), "errors": errors}


def exit_code(result: dict[str, Any]) -> int:
    """Only complete evidence returns success; it remains non-selecting and non-authorizing."""
    return 0 if result.get("valid") is True and result.get("readiness") == "evidence-complete" else 1


def invalid_result(errors: list[str]) -> dict[str, Any]:
    return {"valid": False, "readiness": "invalid", "availability": "unavailable", "selectable": False, "selection": "not-selectable", "cutover_authorization": "not-granted", "side_effects": "none", "binding": output_binding({}), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an Architecture Kit readiness record without side effects.")
    parser.add_argument("--record", type=Path, required=True, help="Readiness-record YAML path.")
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[7], help="Repository root used only for safe evidence reads.")
    parser.add_argument("--format", choices=("json",), default="json", help="Structured output format.")
    arguments = parser.parse_args()
    provider_root = Path(__file__).resolve().parents[1]
    record, _, record_errors = load_yaml_file(arguments.record)
    manifest, manifest_bytes, manifest_errors = load_yaml_file(provider_root / "provider-manifest.yaml")
    result = invalid_result(record_errors + manifest_errors) if record is None or manifest is None else evaluate(record, manifest, provider_manifest_bytes=manifest_bytes, repository_root=arguments.repository_root, provider_root=provider_root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
