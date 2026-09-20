#!/usr/bin/env python3
"""Validate external-task candidates and issue exact-byte custody receipts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
from execution_artifact_contract import (structure_errors, models_errors, authority_manifest, manifest_errors, ContractError)

SCHEMA_PATH = ROOT / ".ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml"
BEGIN_MARKER = "BEGIN_EXTERNAL_TASK_DELEGATION"
END_MARKER = "END_EXTERNAL_TASK_DELEGATION"
COMPLETION_BEGIN_MARKER = "BEGIN_EXTERNAL_TASK_COMPLETION"
COMPLETION_END_MARKER = "END_EXTERNAL_TASK_COMPLETION"
RECEIPT_BEGIN_MARKER = "BEGIN_EXTERNAL_TASK_VALIDATION_RECEIPT"
RECEIPT_END_MARKER = "END_EXTERNAL_TASK_VALIDATION_RECEIPT"
SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
AGENT_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-agent-execution-guardrails.py"
AGENT_SCHEMA_PATH = ROOT / ".ai/assets/shared/agent-execution-guardrails.schema.yaml"
CANONICAL_AGENT_VALIDATOR_REF = ".ai/scripts/validate-agent-execution-guardrails.py"
CANONICAL_VALIDATOR_REF = ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py"


class StrictSafeLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader: StrictSafeLoader, node: Any, deep: bool = False) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            if key in mapping:
                raise yaml.YAMLError(f"duplicate mapping key: {key!r}")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        except TypeError as exc:
            raise yaml.YAMLError("mapping keys must be hashable") from exc
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


def strict_yaml_load(text: str) -> Any:
    return yaml.load(text, Loader=StrictSafeLoader)


def load_mapping(path: Path) -> dict[str, Any]:
    data = strict_yaml_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def exact_yaml_value_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if len(left) != len(right):
            return False
        unmatched = list(right.items())
        for left_key, left_value in left.items():
            for index, (right_key, right_value) in enumerate(unmatched):
                if exact_yaml_value_equal(left_key, right_key) and exact_yaml_value_equal(left_value, right_value):
                    del unmatched[index]
                    break
            else:
                return False
        return not unmatched
    if isinstance(left, list):
        return len(left) == len(right) and all(
            exact_yaml_value_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def validate_exact_mapping_bytes(record: dict[str, Any], raw_bytes: bytes, label: str) -> list[str]:
    try:
        parsed = strict_yaml_load(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError):
        return [f"receipt {label} bytes must deserialize to a YAML mapping equal to the supplied {label}"]
    try:
        matches_record = exact_yaml_value_equal(parsed, record)
    except RecursionError:
        matches_record = False
    if not isinstance(parsed, dict) or not matches_record:
        return [f"receipt {label} bytes must deserialize to a YAML mapping equal to the supplied {label}"]
    return []


def missing_fields(value: object, required: list[str], label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    return [f"{label}.{field} is required" for field in required if field not in value]


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_exact_integer(value: object, expected: int) -> bool:
    return is_integer(value) and value == expected


def string_list(value: object, *, allow_empty: bool = True) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(non_empty_string(item) for item in value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def iso_with_offset(value: object) -> bool:
    if not non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def contained_path(value: object) -> Path | None:
    if not non_empty_string(value):
        return None
    raw_path = str(value)
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts or any(":" in component for component in raw_path.replace("\\", "/").split("/")):
        return None
    resolved = (ROOT / candidate).resolve()
    return resolved if resolved == ROOT or ROOT in resolved.parents else None


def canonical_repository_ref(value: object, *, accept_platform_separators: bool = False) -> str | None:
    """Return a canonical, contained repository-relative reference or None."""
    path = contained_path(value)
    if path is None or path == ROOT or not isinstance(value, str):
        return None
    reference = path.relative_to(ROOT).as_posix()
    supplied = value.replace("\\", "/") if accept_platform_separators else value
    return reference if supplied == reference else None


def git_ignores_reference(reference: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "--quiet", "--no-index", "--", reference],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return False
    return result.returncode == 0


def git_tracks_reference(reference: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", reference],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return True
    return result.returncode == 0


def is_beneath(path: Path, root: Path) -> bool:
    return path != root and root in path.parents


def canonical_receipt_writer_argv(candidate_ref: str, dispatch_ref: str, receipt_ref: str) -> list[str]:
    return [
        "python", CANONICAL_VALIDATOR_REF,
        "--candidate", candidate_ref,
        "--dispatch", dispatch_ref,
        "--write-receipt", receipt_ref,
    ]


def canonical_agent_validator_argv(packet_ref: str) -> list[str]:
    return ["python", CANONICAL_AGENT_VALIDATOR_REF, "--packet", packet_ref]


def validate_pre_send_artifacts(pre_send: dict[str, Any], packet_contract: dict[str, Any]) -> list[str]:
    """Require custody artifacts to be declared, isolated ignored files."""
    errors: list[str] = []
    packet_path = contained_path(packet_contract.get("packet_ref"))
    if packet_path is None or not packet_path.is_file():
        return ["dispatch pre-send artifact validation requires a readable bound execution packet"]
    try:
        packet = load_mapping(packet_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [f"dispatch pre-send artifact validation cannot load the bound execution packet: {exc}"]
    raw_roots = packet.get("ignored_artifact_roots")
    if not string_list(raw_roots, allow_empty=False):
        return ["bound execution packet must declare ignored artifact roots for pre-send custody artifacts"]
    roots: list[Path] = []
    for raw_root in raw_roots:
        root_ref = canonical_repository_ref(raw_root)
        root_path = contained_path(raw_root)
        if root_ref is None or root_path is None:
            errors.append("bound execution packet ignored artifact roots must be canonical contained repository-relative paths")
        elif not git_ignores_reference(root_ref) or git_tracks_reference(root_ref):
            errors.append("bound execution packet ignored artifact roots must be actually ignored and untracked")
        else:
            roots.append(root_path)
    references: dict[str, str] = {}
    for field in ("dispatch_ref", "candidate_ref", "receipt_ref"):
        reference = canonical_repository_ref(pre_send.get(field))
        path = contained_path(pre_send.get(field))
        if reference is None or path is None:
            errors.append(f"dispatch.completion_delivery.pre_send_validation.{field} must be a canonical contained repository-relative path")
            continue
        references[field] = reference
        if not git_ignores_reference(reference) or git_tracks_reference(reference):
            errors.append(f"dispatch.completion_delivery.pre_send_validation.{field} must be actually ignored and untracked")
        if not roots or not any(is_beneath(path, root) for root in roots):
            errors.append(f"dispatch.completion_delivery.pre_send_validation.{field} must be beneath a declared ignored artifact root")
    if len(references) == 3 and len(set(references.values())) != 3:
        errors.append("dispatch.completion_delivery.pre_send_validation custody artifact refs must be distinct")
    if len(references) == 3 and pre_send.get("receipt_writer_argv") != canonical_receipt_writer_argv(
        references["candidate_ref"], references["dispatch_ref"], references["receipt_ref"],
    ):
        errors.append("dispatch.completion_delivery.pre_send_validation.receipt_writer_argv must exactly bind the declared candidate_ref, dispatch_ref, and receipt_ref")
    return errors


def unexpected_fields(value: object, allowed: set[str], label: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    extras = sorted(set(value) - allowed)
    return [f"{label} contains unsupported fields: {', '.join(extras)}"] if extras else []


def validate_bound_packet(packet_contract: dict[str, Any], dispatch: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    packet_path = contained_path(packet_contract.get("packet_ref"))
    if packet_path is None:
        return ["dispatch.execution_packet.packet_ref must be a contained repository-relative path"]
    if not packet_path.is_file():
        return ["dispatch.execution_packet.packet_ref does not exist"]
    if packet_contract.get("packet_sha256") != sha256_bytes(packet_path.read_bytes()):
        errors.append("dispatch.execution_packet.packet_sha256 does not match packet file bytes")
    try:
        spec = importlib.util.spec_from_file_location("agent_execution_guardrails_for_dispatch", AGENT_VALIDATOR_PATH)
        if spec is None or spec.loader is None:
            raise ValueError("canonical agent execution validator cannot be loaded")
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        packet_record = load_mapping(packet_path)
        validator.validate_packet(packet_record, load_mapping(AGENT_SCHEMA_PATH))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return errors + [f"dispatch.execution_packet canonical validation failed: {exc}"]
    if packet_record.get("execution_kind") != "external":
        errors.append("dispatch.execution_packet execution_kind must be external")
    if packet_record.get("subject", {}).get("exact_sha") != dispatch.get("subject", {}).get("commit_sha"):
        errors.append("dispatch.execution_packet content subject must match dispatch subject")
    if packet_record.get("invocation", {}).get("argv") != dispatch.get("execution", {}).get("argv") or packet_record.get("invocation", {}).get("cwd") != dispatch.get("execution", {}).get("working_directory"):
        errors.append("dispatch.execution_packet invocation must match dispatch execution")
    if packet_record.get("integration_owner") != dispatch.get("source", {}).get("final_integration_owner"):
        errors.append("dispatch.execution_packet integration_owner must match dispatch source")
    return errors


def validate_schema_definition(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = models_errors(schema)
    if schema.get("schema_version") != "1.3":
        errors.append("schema.schema_version must be 1.3")
    if schema.get("contract_id") != "external-task-delegation":
        errors.append("schema.contract_id must be external-task-delegation")
    if schema.get("record_types") != {"dispatch": "external-task-dispatch", "completion": "external-task-completion", "validation_receipt": "external-task-validation-receipt"}:
        errors.append("schema.record_types must declare dispatch, completion, and validation receipt records")
    for key, begin, end, count in (("prompt_transport", BEGIN_MARKER, END_MARKER, "dispatch_records_per_prompt"), ("completion_transport", COMPLETION_BEGIN_MARKER, COMPLETION_END_MARKER, "completion_records_per_message"), ("receipt_transport", RECEIPT_BEGIN_MARKER, RECEIPT_END_MARKER, "receipt_records_per_message")):
        transport = schema.get(key)
        errors.extend(missing_fields(transport, ["begin_marker", "end_marker", count], f"schema.{key}"))
        if isinstance(transport, dict) and (transport.get("begin_marker") != begin or transport.get("end_marker") != end or not is_exact_integer(transport.get(count), 1)):
            errors.append(f"schema.{key} markers or record count are invalid")
    delivery = schema.get("dispatch", {}).get("completion_delivery", {})
    if delivery.get("primary_modes") != ["source-task-callback", "parent-event-wait"] or delivery.get("fallback_modes") != ["parent-event-wait", "single-terminal-readback", "none"]:
        errors.append("schema dispatch delivery modes are invalid")
    semantics = schema.get("transport_semantics", {})
    expected = {
        "parent_wait_timeout": "pending-awaiting-completion",
        "callback_failure_with_retrievable_terminal_report": "recoverable-by-one-terminal-readback",
        "terminal_task_without_valid_completion_report": "non-passing",
        "repeated_status_polling": "prohibited",
        "source_task_progress_delivery": "terminal-only",
        "runtime_local_progress": "runtime-policy-owned-and-not-source-delivery",
        "pre_send_completion_validation": "required",
        "post_validation_record_mutation": "prohibited",
        "callback_payload": "exact-candidate-bytes-with-independent-receipt",
        "custody_release": "a receipt matching the exact candidate and dispatch bytes is required before one terminal delivery for every terminal outcome",
    }
    for key, value in expected.items():
        if semantics.get(key) != value:
            errors.append(f"schema transport semantic {key} is invalid")
    return errors


def validate_dispatch(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = structure_errors(record, schema, "dispatch")
    if errors:
        return errors
    if record.get("schema_version") not in {"1.2", "1.3"}: errors.append("dispatch.schema_version must be 1.2 or 1.3")
    if record.get("record_type") != "external-task-dispatch": errors.append("dispatch.record_type must be external-task-dispatch")
    if not non_empty_string(record.get("delegation_id")) or not ID_RE.fullmatch(str(record.get("delegation_id", ""))): errors.append("dispatch.delegation_id must be a stable bounded identifier")
    if not non_empty_string(record.get("task_kind")): errors.append("dispatch.task_kind must be a non-empty string")
    source = record.get("source")

    if isinstance(source, dict):
        if source.get("task_id_source") not in schema["dispatch"]["source"]["task_id_sources"]: errors.append("dispatch.source.task_id_source is invalid")
        if source.get("task_id_source") == "explicit" and not non_empty_string(source.get("task_id")): errors.append("dispatch.source.task_id is required when task_id_source is explicit")
        if not non_empty_string(source.get("final_integration_owner")): errors.append("dispatch.source.final_integration_owner must be non-empty")
    objective = record.get("objective")

    if isinstance(objective, dict) and (not non_empty_string(objective.get("goal")) or not string_list(objective.get("non_goals"))): errors.append("dispatch.objective must contain a goal and string non_goals")
    subject = record.get("subject")

    if isinstance(subject, dict) and (not non_empty_string(subject.get("repository_root")) or not SHA_RE.fullmatch(str(subject.get("commit_sha", ""))) or subject.get("clean_worktree_required") is not True): errors.append("dispatch.subject is invalid")
    execution = record.get("execution")

    if isinstance(execution, dict) and (not non_empty_string(execution.get("working_directory")) or not string_list(execution.get("argv"), allow_empty=False) or not is_integer(execution.get("timeout_seconds")) or execution.get("timeout_seconds", 0) <= 0): errors.append("dispatch.execution is invalid")
    packet = record.get("execution_packet")

    if isinstance(packet, dict):
        if packet.get("schema_ref") != ".ai/assets/shared/agent-execution-guardrails.schema.yaml" or not SHA256_RE.fullmatch(str(packet.get("packet_sha256", ""))) or packet.get("validation_outcome") != "passed": errors.append("dispatch.execution_packet is invalid")
        if packet.get("subject_sha") != (subject or {}).get("commit_sha"): errors.append("dispatch.execution_packet.subject_sha must match dispatch subject")
        argv = packet.get("validator_argv")
        packet_ref = packet.get("packet_ref")
        if not non_empty_string(packet_ref) or argv != canonical_agent_validator_argv(packet_ref): errors.append("dispatch.execution_packet.validator_argv must exactly bind the canonical agent validator and packet_ref")
        errors.extend(validate_bound_packet(packet, record))
    permissions = record.get("permissions")

    if isinstance(permissions, dict) and (not string_list(permissions.get("read_scope"), allow_empty=False) or not string_list(permissions.get("write_scope")) or not set(permissions.get("write_scope", [])) <= {"ignored-validation-artifacts"} or permissions.get("repair_allowed") is not False or permissions.get("external_mutations") != [] or permissions.get("secret_values") != "prohibited"): errors.append("dispatch.permissions is invalid")
    delivery = record.get("completion_delivery")

    if isinstance(delivery, dict):
        contract = schema["dispatch"]["completion_delivery"]
        if delivery.get("primary") not in contract["primary_modes"] or delivery.get("fallback") not in contract["fallback_modes"] or delivery.get("destination") != "source-task" or delivery.get("progress_updates") != "terminal-only" or not is_exact_integer(delivery.get("max_terminal_reports"), 1) or delivery.get("report_schema") != "same-contract#completion": errors.append("dispatch.completion_delivery is invalid")
        pre_send = delivery.get("pre_send_validation")

        if isinstance(pre_send, dict):
            argv = pre_send.get("receipt_writer_argv")
            if pre_send.get("required") is not True or not string_list(argv, allow_empty=False): errors.append("dispatch.completion_delivery.pre_send_validation receipt writer is invalid")
            for field in ("dispatch_ref", "candidate_ref", "receipt_ref"):
                if not non_empty_string(pre_send.get(field)): errors.append(f"dispatch.completion_delivery.pre_send_validation.{field} must be non-empty")
            if pre_send.get("failure_action") != "do-not-deliver-terminal-report" or pre_send.get("payload_binding") != "exact-candidate-bytes-with-independent-receipt": errors.append("dispatch.completion_delivery.pre_send_validation custody binding is invalid")
            if isinstance(packet, dict):
                errors.extend(validate_pre_send_artifacts(pre_send, packet))
    if not string_list(record.get("stop_conditions"), allow_empty=False): errors.append("dispatch.stop_conditions must be a non-empty string list")
    if record.get("schema_version") == "1.3":
        try:
            packet_record = load_mapping(contained_path(record["execution_packet"]["packet_ref"]))
            errors.extend(manifest_errors(record["authority_manifest"], authority_manifest(ROOT, packet_record)))
            review_selected = record["task_kind"] in {"review", "fixed-head-audit", "independent-review"} or packet_record["role"]["path"].endswith("/fixed-head-independent-auditor/sub-agent.yaml")
            if review_selected and (packet_record.get("schema_version") != "1.1" or not packet_record.get("review_input")):
                errors.append("current review dispatch requires packet 1.1 with bound review_input; prose cannot substitute")
        except (OSError, ValueError, TypeError, AttributeError, yaml.YAMLError) as exc:
            errors.append(f"dispatch authority or review binding cannot be established: {type(exc).__name__}")
    return errors


def validate_completion(record: dict[str, Any], schema: dict[str, Any], dispatch: dict[str, Any] | None = None) -> list[str]:
    errors = structure_errors(record, schema, "completion")
    if errors:
        return errors
    if record.get("schema_version") not in {"1.2", "1.3"}: errors.append("completion.schema_version must be 1.2 or 1.3")
    if record.get("record_type") != "external-task-completion": errors.append("completion.record_type must be external-task-completion")
    for field in ("delegation_id", "source_task_id", "delegated_task_id"):
        if not non_empty_string(record.get(field)): errors.append(f"completion.{field} must be non-empty")
    subject, preflight, execution, result, final_state = (record.get(key) for key in ("subject", "preflight", "execution", "result", "final_state"))

    if isinstance(subject, dict) and (not SHA_RE.fullmatch(str(subject.get("expected_commit_sha", ""))) or not SHA_RE.fullmatch(str(subject.get("observed_commit_sha", "")))): errors.append("completion subject SHAs must be full Git SHAs")

    if isinstance(preflight, dict) and (not isinstance(preflight.get("commit_matches"), bool) or not isinstance(preflight.get("clean_worktree"), bool)): errors.append("completion.preflight is invalid")

    if isinstance(execution, dict) and (not non_empty_string(execution.get("working_directory")) or not string_list(execution.get("argv"), allow_empty=False)): errors.append("completion.execution is invalid")
    timing = record.get("timing")

    if isinstance(timing, dict) and (not iso_with_offset(timing.get("started_at")) or not iso_with_offset(timing.get("completed_at")) or not isinstance(timing.get("duration_seconds"), (int, float)) or isinstance(timing.get("duration_seconds"), bool) or timing.get("duration_seconds", -1) < 0): errors.append("completion.timing is invalid")

    outcome = result.get("outcome") if isinstance(result, dict) else None
    if isinstance(result, dict) and (outcome not in schema["completion"]["result"]["outcomes"] or (result.get("exit_code") is not None and not is_integer(result.get("exit_code")))): errors.append("completion.result is invalid")
    counts = result.get("counts") if isinstance(result, dict) else None
    if counts is not None and (not isinstance(counts, dict) or any(not non_empty_string(key) or not is_integer(value) or value < 0 for key, value in counts.items())): errors.append("completion.result.counts must be null or a mapping of non-negative integers")
    evidence = record.get("evidence")

    if isinstance(evidence, dict) and not isinstance(evidence.get("bounded_output"), str): errors.append("completion.evidence.bounded_output must be a string")
    if isinstance(evidence, dict) and (not string_list(evidence.get("refs")) or (not evidence.get("refs") and not non_empty_string(evidence.get("bounded_output")))): errors.append("completion.evidence requires a ref or bounded_output")

    if isinstance(final_state, dict) and (not isinstance(final_state.get("clean_worktree"), bool) or not string_list(final_state.get("tracked_changes"))): errors.append("completion.final_state is invalid")
    delivery = record.get("delivery")

    if isinstance(delivery, dict) and (delivery.get("mode") not in schema["completion"]["delivery"]["modes"] or delivery.get("destination") != "source-task" or not is_exact_integer(delivery.get("terminal_report_number"), 1)): errors.append("completion.delivery is invalid")
    if outcome == "passed":
        if not isinstance(subject, dict) or subject.get("expected_commit_sha") != subject.get("observed_commit_sha"): errors.append("passed completion requires matching expected and observed commit SHAs")
        if not isinstance(preflight, dict) or preflight.get("commit_matches") is not True or preflight.get("clean_worktree") is not True: errors.append("passed completion requires a matching clean preflight")
        if not isinstance(result, dict) or not is_exact_integer(result.get("exit_code"), 0): errors.append("passed completion requires exit_code zero")
        if not isinstance(final_state, dict) or final_state.get("clean_worktree") is not True or final_state.get("tracked_changes") != []: errors.append("passed completion requires a clean final worktree with no tracked changes")
    if dispatch is not None:
        if record.get("schema_version") != dispatch.get("schema_version"): errors.append("completion.schema_version must match dispatch")
        if record.get("delegation_id") != dispatch.get("delegation_id"): errors.append("completion.delegation_id must match dispatch")
        if isinstance(subject, dict) and subject.get("expected_commit_sha") != dispatch.get("subject", {}).get("commit_sha"): errors.append("completion expected commit must match dispatch")
        if isinstance(execution, dict) and (execution.get("working_directory") != dispatch.get("execution", {}).get("working_directory") or execution.get("argv") != dispatch.get("execution", {}).get("argv")): errors.append("completion.execution must match dispatch")
        if dispatch.get("source", {}).get("task_id_source") == "explicit" and record.get("source_task_id") != dispatch.get("source", {}).get("task_id"): errors.append("completion.source_task_id must match explicit dispatch source")
        dispatch_delivery = dispatch.get("completion_delivery")
        if isinstance(delivery, dict) and isinstance(dispatch_delivery, dict):
            allowed_modes = {dispatch_delivery.get("primary")}
            if dispatch_delivery.get("fallback") != "none":
                allowed_modes.add(dispatch_delivery.get("fallback"))
            if delivery.get("mode") not in allowed_modes:
                errors.append("completion.delivery.mode must match dispatch primary or non-none fallback")
    return errors


def build_validation_receipt(candidate: dict[str, Any], dispatch: dict[str, Any], candidate_ref: str, candidate_bytes: bytes, dispatch_ref: str, dispatch_bytes: bytes, receipt_ref: str) -> dict[str, Any]:
    if candidate.get("schema_version") != "1.3" or dispatch.get("schema_version") != "1.3":
        raise ValueError("current receipt writer requires explicit 1.3 dispatch and candidate; historical receipts are never upgraded")
    packet_record = load_mapping(contained_path(dispatch["execution_packet"]["packet_ref"]))
    expected_authority = authority_manifest(ROOT, packet_record)
    if manifest_errors(dispatch.get("authority_manifest"), expected_authority):
        raise ValueError("receipt writer current authority differs from dispatch")
    receipt = {"schema_version": "1.3", "record_type": "external-task-validation-receipt", "delegation_id": candidate["delegation_id"], "receipt_ref": receipt_ref, "candidate": {"ref": candidate_ref, "sha256": sha256_bytes(candidate_bytes)}, "dispatch": {"ref": dispatch_ref, "sha256": sha256_bytes(dispatch_bytes)}, "validator": {"script_sha256": sha256_bytes(Path(__file__).read_bytes()), "argv": canonical_receipt_writer_argv(candidate_ref, dispatch_ref, receipt_ref), "exit_code": 0}, "custody": {"state": "released", "release_scope": "one matching terminal candidate delivery"}}

    receipt["authority_manifest"] = expected_authority
    return receipt


def validate_receipt(receipt: dict[str, Any], schema: dict[str, Any], candidate: dict[str, Any], candidate_bytes: bytes, dispatch: dict[str, Any], dispatch_bytes: bytes) -> list[str]:
    errors = structure_errors(receipt, schema, "receipt")
    if errors:
        return errors
    errors.extend(validate_exact_mapping_bytes(candidate, candidate_bytes, "candidate"))
    errors.extend(validate_exact_mapping_bytes(dispatch, dispatch_bytes, "dispatch"))
    if receipt.get("schema_version") != "1.3" or receipt.get("record_type") != "external-task-validation-receipt": errors.append("receipt schema_version or record_type is invalid")
    if receipt.get("schema_version") != "1.3" or candidate.get("schema_version") != "1.3" or dispatch.get("schema_version") != "1.3":
        return errors + ["historical 1.2 receipt is readable only with its original immutable validator authority; current admission requires explicit 1.3 preparation, not receipt migration"]
    try:
        packet_record = load_mapping(contained_path(dispatch["execution_packet"]["packet_ref"]))
        errors.extend(manifest_errors(receipt.get("authority_manifest"), authority_manifest(ROOT, packet_record)))
        if receipt.get("authority_manifest") != dispatch.get("authority_manifest"):
            errors.append("receipt.authority_manifest must match dispatch current validation authority")
    except (OSError, ValueError, TypeError, AttributeError, yaml.YAMLError):
        errors.append("receipt current validation authority cannot be established")
    if receipt.get("delegation_id") != candidate.get("delegation_id") or receipt.get("delegation_id") != dispatch.get("delegation_id"): errors.append("receipt.delegation_id must match candidate and dispatch")
    for key, bytes_value in (("candidate", candidate_bytes), ("dispatch", dispatch_bytes)):
        binding = receipt.get(key)

        if isinstance(binding, dict) and binding.get("sha256") != sha256_bytes(bytes_value): errors.append(f"receipt.{key}.sha256 does not match exact {key} bytes")
    pre_send = dispatch.get("completion_delivery", {}).get("pre_send_validation", {})
    candidate_binding = receipt.get("candidate", {})
    dispatch_binding = receipt.get("dispatch", {})
    if candidate_binding.get("ref") != pre_send.get("candidate_ref"):
        errors.append("receipt.candidate.ref must match dispatch pre-send candidate_ref")
    if dispatch_binding.get("ref") != pre_send.get("dispatch_ref"):
        errors.append("receipt.dispatch.ref must match dispatch pre-send dispatch_ref")
    if receipt.get("receipt_ref") != pre_send.get("receipt_ref"):
        errors.append("receipt.receipt_ref must match dispatch pre-send receipt_ref")
    validator = receipt.get("validator")

    if isinstance(validator, dict) and (validator.get("script_sha256") != sha256_bytes(Path(__file__).read_bytes()) or not string_list(validator.get("argv"), allow_empty=False) or not is_exact_integer(validator.get("exit_code"), 0)): errors.append("receipt.validator is invalid")
    if isinstance(validator, dict) and validator.get("argv") != pre_send.get("receipt_writer_argv"):
        errors.append("receipt.validator.argv must match dispatch pre-send receipt_writer_argv")
    custody = receipt.get("custody")

    if isinstance(custody, dict) and (custody.get("state") != "released" or custody.get("release_scope") != "one matching terminal candidate delivery"): errors.append("receipt.custody is invalid")
    errors.extend(validate_dispatch(dispatch, schema))
    errors.extend(validate_completion(candidate, schema, dispatch))
    return errors


def extract_record_from_envelope(text: str, begin_marker: str, end_marker: str, label: str) -> dict[str, Any]:
    if text.count(begin_marker) != 1 or text.count(end_marker) != 1: raise ValueError(f"{label} must contain exactly one external-task envelope")
    _, remainder = text.split(begin_marker, 1)
    payload, after = remainder.split(end_marker, 1)
    if begin_marker in after: raise ValueError(f"{label} envelope markers are out of order")
    data = strict_yaml_load(payload.strip())
    if not isinstance(data, dict): raise ValueError(f"{label} envelope must contain one YAML mapping")
    return data


def extract_exact_envelope_bytes(text: str, begin_marker: str, end_marker: str, label: str) -> bytes:
    if text.count(begin_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError(f"{label} must contain exactly one external-task envelope")
    _, remainder = text.split(begin_marker, 1)
    payload, after = remainder.split(end_marker, 1)
    if begin_marker in after:
        raise ValueError(f"{label} envelope markers are out of order")
    if payload.startswith("\r\n"):
        payload = payload[2:]
    elif payload.startswith("\n"):
        payload = payload[1:]
    return payload.encode("utf-8")


def validate_terminal_delivery_message(text: str, schema: dict[str, Any], dispatch: dict[str, Any], dispatch_bytes: bytes) -> list[str]:
    errors: list[str] = []
    try:
        candidate_bytes = extract_exact_envelope_bytes(text, COMPLETION_BEGIN_MARKER, COMPLETION_END_MARKER, "terminal delivery")
        candidate = strict_yaml_load(candidate_bytes.decode("utf-8"))
        receipt = extract_receipt_from_message(text)
        if not isinstance(candidate, dict):
            errors.append("terminal delivery candidate must be a YAML mapping")
        else:
            errors.extend(validate_receipt(receipt, schema, candidate, candidate_bytes, dispatch, dispatch_bytes))
    except (ValueError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    return errors


def validate_receipt_custody_paths(candidate_path: Path, dispatch_path: Path, receipt_path: Path, dispatch: dict[str, Any], *, action: str, receipt_option: str) -> list[str]:
    """Bind every CLI custody artifact path to the dispatch's declared refs."""
    errors: list[str] = []
    pre_send = dispatch.get("completion_delivery", {}).get("pre_send_validation", {})
    for option, path, declared_ref in (
        ("--candidate", candidate_path, pre_send.get("candidate_ref")),
        ("--dispatch", dispatch_path, pre_send.get("dispatch_ref")),
        (receipt_option, receipt_path, pre_send.get("receipt_ref")),
    ):
        actual_ref = canonical_repository_ref(str(path), accept_platform_separators=True)
        if (
            not isinstance(declared_ref, str)
            or canonical_repository_ref(declared_ref) != declared_ref
            or actual_ref != declared_ref
        ):
            errors.append(f"receipt {action} {option} path must exactly match its declared safe pre-send ref")
    return errors


def validate_receipt_verification_request(candidate_path: Path, dispatch_path: Path, receipt_path: Path, dispatch: dict[str, Any]) -> list[str]:
    """Require receipt verification to read the dispatch-bound custody files."""
    return validate_receipt_custody_paths(
        candidate_path, dispatch_path, receipt_path, dispatch,
        action="verification", receipt_option="--receipt",
    )


def validate_receipt_write_request(candidate_path: Path, dispatch_path: Path, receipt_path: Path, dispatch: dict[str, Any]) -> list[str]:
    """Bind receipt-writing file arguments to the already-validated custody refs."""
    errors = validate_receipt_custody_paths(
        candidate_path, dispatch_path, receipt_path, dispatch,
        action="writing", receipt_option="--write-receipt",
    )
    if dispatch.get("schema_version") != "1.3":
        errors.append("current receipt writer requires explicit 1.3 dispatch and candidate; historical receipts are never upgraded")
    if not errors and receipt_path.exists():
        errors.append("receipt writing refuses to overwrite a pre-existing output")
    return errors


def write_receipt_exclusively(receipt_path: Path, receipt: dict[str, Any]) -> list[str]:
    try:
        with receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
            yaml.safe_dump(receipt, stream, sort_keys=False)
    except FileExistsError:
        return ["receipt writing refuses to overwrite a pre-existing output"]
    except OSError as exc:
        return [f"receipt writing could not create the declared output: {exc.strerror or type(exc).__name__}"]
    return []


def extract_dispatch_from_prompt(text: str) -> dict[str, Any]: return extract_record_from_envelope(text, BEGIN_MARKER, END_MARKER, "prompt")
def extract_completion_from_message(text: str) -> dict[str, Any]: return extract_record_from_envelope(text, COMPLETION_BEGIN_MARKER, COMPLETION_END_MARKER, "completion message")
def extract_receipt_from_message(text: str) -> dict[str, Any]: return extract_record_from_envelope(text, RECEIPT_BEGIN_MARKER, RECEIPT_END_MARKER, "receipt message")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path, help="Dispatch or completion candidate YAML record")
    parser.add_argument("--candidate", type=Path, help="Terminal candidate YAML record")
    parser.add_argument("--dispatch", type=Path, help="Dispatch YAML record used to cross-check a candidate")
    parser.add_argument("--receipt", type=Path, help="Independent validation receipt to verify")
    parser.add_argument("--write-receipt", type=Path, help="Write a receipt only after candidate validation succeeds")
    parser.add_argument("--prompt", type=Path, help="Prompt text containing one marked dispatch envelope")
    parser.add_argument("--completion-message", type=Path, help="Message text containing one marked completion envelope")
    parser.add_argument("--terminal-message", type=Path, help="Message containing one completion candidate and one receipt envelope")
    parser.add_argument("--schema-only", action="store_true", help="Validate only the canonical schema definition")
    return parser.parse_args()


def input_supplied(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, bytes, list, tuple, set, dict)):
        return bool(value)
    return True


def validate_input_modes(args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    candidate_modes = [
        name for name, value in (
            ("record", args.record),
            ("--candidate", args.candidate),
            ("--completion-message", args.completion_message),
            ("--terminal-message", args.terminal_message),
        ) if input_supplied(value)
    ]
    if len(candidate_modes) > 1:
        errors.append("candidate input modes are mutually exclusive: " + ", ".join(candidate_modes))
    dispatch_modes = [
        name for name, value in (("--dispatch", args.dispatch), ("--prompt", args.prompt))
        if input_supplied(value)
    ]
    if len(dispatch_modes) > 1:
        errors.append("dispatch input modes are mutually exclusive: " + ", ".join(dispatch_modes))
    if args.write_receipt is not None:
        conflicts = any(input_supplied(value) for value in (
            args.record, args.prompt, args.completion_message, args.terminal_message, args.receipt,
        )) or args.schema_only
        if not input_supplied(args.candidate) or not input_supplied(args.dispatch) or conflicts:
            errors.append("--write-receipt requires exactly --candidate and --dispatch, with no record, prompt, message, receipt, or schema-only mode")
    if args.receipt is not None:
        conflicts = any(input_supplied(value) for value in (
            args.record, args.prompt, args.completion_message, args.terminal_message, args.write_receipt,
        )) or args.schema_only
        if not input_supplied(args.candidate) or not input_supplied(args.dispatch) or conflicts:
            errors.append("--receipt requires exactly --candidate and --dispatch, with no record, prompt, message, write-receipt, or schema-only mode")
    return errors


def main() -> int:
    args = parse_args(); schema = load_mapping(SCHEMA_PATH); errors = validate_schema_definition(schema)
    input_mode_errors = validate_input_modes(args)
    if input_mode_errors:
        errors.extend(input_mode_errors)
        print("External-task delegation validation failed:"); [print(f"- {error}") for error in errors]; return 1
    candidate_path = args.candidate; candidate: dict[str, Any] | None = None; candidate_bytes: bytes | None = None
    dispatch_path = args.dispatch; dispatch: dict[str, Any] | None = None; dispatch_bytes: bytes | None = None
    try:
        if args.prompt: dispatch = extract_dispatch_from_prompt(args.prompt.read_text(encoding="utf-8")); dispatch_bytes = args.prompt.read_bytes()
        elif dispatch_path: dispatch = load_mapping(dispatch_path); dispatch_bytes = dispatch_path.read_bytes()
        if args.terminal_message:
            terminal_text = args.terminal_message.read_text(encoding="utf-8")
            candidate_bytes = extract_exact_envelope_bytes(terminal_text, COMPLETION_BEGIN_MARKER, COMPLETION_END_MARKER, "terminal delivery")
            candidate = strict_yaml_load(candidate_bytes.decode("utf-8"))
        elif args.completion_message: candidate = extract_completion_from_message(args.completion_message.read_text(encoding="utf-8")); candidate_bytes = args.completion_message.read_bytes()
        elif candidate_path: candidate = load_mapping(candidate_path); candidate_bytes = candidate_path.read_bytes()
        elif args.record:
            record = load_mapping(args.record)
            if record.get("record_type") == "external-task-dispatch": dispatch, dispatch_bytes = record, args.record.read_bytes()
            else: candidate, candidate_bytes, candidate_path = record, args.record.read_bytes(), args.record
    except (OSError, ValueError, yaml.YAMLError) as exc: errors.append(str(exc))
    if dispatch is not None: errors.extend(validate_dispatch(dispatch, schema))
    if candidate is not None:
        if dispatch is None: errors.append("completion candidate requires --dispatch for cross-record validation")
        else: errors.extend(validate_completion(candidate, schema, dispatch))
    if args.terminal_message is not None:
        if dispatch is None or dispatch_bytes is None:
            errors.append("terminal delivery verification requires --dispatch")
        else:
            try:
                errors.extend(validate_terminal_delivery_message(terminal_text, schema, dispatch, dispatch_bytes))
            except (OSError, ValueError, yaml.YAMLError) as exc:
                errors.append(str(exc))
    if args.receipt is not None:
        if candidate is None or dispatch is None or candidate_bytes is None or dispatch_bytes is None or candidate_path is None or dispatch_path is None: errors.append("receipt verification requires --candidate and --dispatch")
        else:
            path_errors = validate_receipt_verification_request(candidate_path, dispatch_path, args.receipt, dispatch)
            errors.extend(path_errors)
            if not path_errors:
                try: errors.extend(validate_receipt(load_mapping(args.receipt), schema, candidate, candidate_bytes, dispatch, dispatch_bytes))
                except (OSError, ValueError, yaml.YAMLError) as exc: errors.append(str(exc))
    if args.write_receipt is not None:
        if candidate is None or dispatch is None or candidate_bytes is None or dispatch_bytes is None or candidate_path is None or dispatch_path is None: errors.append("receipt writing requires --candidate and --dispatch files")
        else:
            errors.extend(validate_receipt_write_request(candidate_path, dispatch_path, args.write_receipt, dispatch))
            if not errors:
                pre_send = dispatch["completion_delivery"]["pre_send_validation"]
                receipt = build_validation_receipt(
                    candidate, dispatch,
                    pre_send["candidate_ref"], candidate_bytes,
                    pre_send["dispatch_ref"], dispatch_bytes,
                    pre_send["receipt_ref"],
                )
                errors.extend(write_receipt_exclusively(args.write_receipt, receipt))
    if not args.schema_only and dispatch is None and candidate is None and not errors: errors.append("provide a record, --candidate, --prompt, --completion-message, or --schema-only")
    if errors:
        print("External-task delegation validation failed:"); [print(f"- {error}") for error in errors]; return 1
    print("External-task custody receipt issued." if args.write_receipt else "External-task candidate validation passed; custody remains held unless a matching receipt was verified.")
    return 0


if __name__ == "__main__": raise SystemExit(main())
