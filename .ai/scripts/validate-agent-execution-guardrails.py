#!/usr/bin/env python3
"""Fail-closed validation for agent packets, leases, evidence, retries, and graph freshness."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-agent-execution-guardrails.py")

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / ".ai/assets/shared/agent-execution-guardrails.schema.yaml"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_REF = re.compile(r"^(?:ignored|workflow|issue|commit|run|job|fixture|tracked):[^\s]+$")


class GuardrailError(ValueError):
    pass


def mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GuardrailError(f"{name} must be a mapping")
    return value


def exact_keys(value: dict[str, Any], required: set[str], name: str) -> None:
    if set(value) != required:
        raise GuardrailError(f"{name} keys must be exactly {sorted(required)}")


def string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GuardrailError(f"{name} must be a non-empty string")
    return value


def strings(value: Any, name: str, *, empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not empty and not value) or any(not isinstance(item, str) or not item for item in value):
        raise GuardrailError(f"{name} must be a list of non-empty strings")
    return value


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sealed(record: dict[str, Any], field: str) -> None:
    claimed = record.get(field)
    if not isinstance(claimed, str) or not SHA256.fullmatch(claimed):
        raise GuardrailError(f"{field} must be lowercase SHA-256")
    if claimed != digest({key: value for key, value in record.items() if key != field}):
        raise GuardrailError(f"{field} does not match canonical content")


def reject_private(value: Any, schema: dict[str, Any], path: str = "record") -> None:
    if isinstance(value, dict):
        forbidden = set(schema["privacy_forbidden_keys"])
        for key, nested in value.items():
            if str(key).lower() in forbidden:
                raise GuardrailError(f"{path}.{key} is privacy-forbidden")
            reject_private(nested, schema, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_private(nested, schema, f"{path}[{index}]")


def validate_packet(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "packet_id", "execution_kind", "owning_skill", "role", "subject", "invocation", "permissions", "ignored_artifact_roots", "terminal", "integration_owner", "stop_conditions", "retry", "packet_sha256"}, "packet")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["packet"]:
        raise GuardrailError("packet schema identity is invalid")
    string(record["packet_id"], "packet_id")
    string(record["owning_skill"], "owning_skill")
    if record["execution_kind"] not in schema["execution_kinds"]:
        raise GuardrailError("execution_kind is invalid")
    role = mapping(record["role"], "role")
    exact_keys(role, {"path", "applicability", "reason"}, "role")
    if not string(role["path"], "role.path").startswith(".ai/assets/sub-agent-role-prompts/"):
        raise GuardrailError("role.path must be canonical")
    if role["applicability"] not in schema["role_applicability"]:
        raise GuardrailError("role.applicability is invalid")
    string(role["reason"], "role.reason")
    subject = mapping(record["subject"], "subject")
    exact_keys(subject, {"repository", "exact_sha"}, "subject")
    string(subject["repository"], "subject.repository")
    if not isinstance(subject["exact_sha"], str) or not SHA40.fullmatch(subject["exact_sha"]):
        raise GuardrailError("subject.exact_sha must be a lowercase 40-character SHA")
    invocation = mapping(record["invocation"], "invocation")
    exact_keys(invocation, {"argv", "cwd"}, "invocation")
    strings(invocation["argv"], "invocation.argv")
    string(invocation["cwd"], "invocation.cwd")
    permissions = mapping(record["permissions"], "permissions")
    exact_keys(permissions, {"network", "tracked_write", "provider_mutation"}, "permissions")
    if any(value not in schema["permission_modes"] for value in permissions.values()):
        raise GuardrailError("permissions must use allow or deny")
    ignored = strings(record["ignored_artifact_roots"], "ignored_artifact_roots", empty=True)
    if any(Path(item).is_absolute() or ".." in Path(item).parts for item in ignored):
        raise GuardrailError("ignored artifact roots must be contained repository-relative paths")
    terminal = mapping(record["terminal"], "terminal")
    exact_keys(terminal, {"schema_ref", "mode", "destination", "max_terminal_messages"}, "terminal")
    string(terminal["schema_ref"], "terminal.schema_ref")
    if terminal["mode"] not in schema["terminal_modes"] or terminal["max_terminal_messages"] != 1:
        raise GuardrailError("terminal transport must be one callback or event wait")
    string(terminal["destination"], "terminal.destination")
    string(record["integration_owner"], "integration_owner")
    strings(record["stop_conditions"], "stop_conditions")
    retry = mapping(record["retry"], "retry")
    exact_keys(retry, {"attempt", "budget", "authorization_refs"}, "retry")
    if not isinstance(retry["attempt"], int) or retry["attempt"] < 1 or not isinstance(retry["budget"], int) or retry["budget"] < retry["attempt"]:
        raise GuardrailError("retry attempt and budget are invalid")
    authorizations = strings(retry["authorization_refs"], "retry.authorization_refs", empty=True)
    if retry["attempt"] >= 3 and not authorizations:
        raise GuardrailError("attempt 3+ requires new owner or workflow authorization")
    if record["execution_kind"] in {"external", "fixed-head-audit"} and (permissions["tracked_write"] != "deny" or permissions["provider_mutation"] != "deny"):
        raise GuardrailError("external and fixed-head execution must be read-only")
    reject_private(record, schema)
    sealed(record, "packet_sha256")


def validate_lease(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "lease_id", "worktree", "subject_sha", "snapshot_sha256", "state", "holder", "observed_other_tracked_writers", "ignored_artifacts", "tracked_mutations", "terminal_release", "lease_sha256"}, "lease")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["lease"]:
        raise GuardrailError("lease schema identity is invalid")
    string(record["lease_id"], "lease_id")
    string(record["worktree"], "worktree")
    if not isinstance(record["subject_sha"], str) or not SHA40.fullmatch(record["subject_sha"]):
        raise GuardrailError("lease subject_sha is invalid")
    if not isinstance(record["snapshot_sha256"], str) or not SHA256.fullmatch(record["snapshot_sha256"]):
        raise GuardrailError("snapshot_sha256 is invalid")
    if record["state"] not in schema["lease_states"]:
        raise GuardrailError("lease state is invalid")
    holder = mapping(record["holder"], "holder")
    exact_keys(holder, {"packet_id", "access"}, "holder")
    string(holder["packet_id"], "holder.packet_id")
    if holder["access"] not in schema["lease_access"]:
        raise GuardrailError("holder access is invalid")
    other_writers = strings(record["observed_other_tracked_writers"], "observed_other_tracked_writers", empty=True)
    mutations = strings(record["tracked_mutations"], "tracked_mutations", empty=True)
    artifacts = record["ignored_artifacts"]
    if not isinstance(artifacts, list):
        raise GuardrailError("ignored_artifacts must be a list")
    for item in artifacts:
        item = mapping(item, "ignored_artifact")
        exact_keys(item, {"path", "state", "sha256"}, "ignored_artifact")
        string(item["path"], "ignored_artifact.path")
        if item["state"] not in schema["artifact_states"]:
            raise GuardrailError("ignored artifact state is invalid")
        if item["sha256"] is not None and (not isinstance(item["sha256"], str) or not SHA256.fullmatch(item["sha256"])):
            raise GuardrailError("ignored artifact digest is invalid")
    terminal_release = mapping(record["terminal_release"], "terminal_release")
    exact_keys(terminal_release, {"released", "reason"}, "terminal_release")
    if not isinstance(terminal_release["released"], bool):
        raise GuardrailError("terminal_release.released must be boolean")
    string(terminal_release["reason"], "terminal_release.reason")
    if record["state"] == "active" and holder["access"] == "tracked-writer" and other_writers:
        raise GuardrailError("active lease rejects another tracked writer")
    if record["state"] == "active" and mutations:
        raise GuardrailError("active lease snapshot drifted")
    if record["state"] == "released" and (mutations or not terminal_release["released"] or any(item["state"] == "open" for item in artifacts)):
        raise GuardrailError("released lease requires clean tracked state and terminal artifact release")
    if record["state"] == "invalidated" and terminal_release["released"]:
        raise GuardrailError("invalidated lease cannot claim terminal release")
    reject_private(record, schema)
    sealed(record, "lease_sha256")


def validate_evidence(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "subject_sha", "entries", "human_report", "ledger_sha256"}, "evidence ledger")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["evidence"]:
        raise GuardrailError("evidence schema identity is invalid")
    if not isinstance(record["subject_sha"], str) or not SHA40.fullmatch(record["subject_sha"]):
        raise GuardrailError("evidence subject_sha is invalid")
    entries = record["entries"]
    if not isinstance(entries, list) or not entries:
        raise GuardrailError("entries must be non-empty")
    expected: dict[str, tuple[str, str]] = {}
    for entry in entries:
        entry = mapping(entry, "entry")
        exact_keys(entry, {"acceptance_id", "issue", "requires_actual_execution", "evidence_kind", "command", "profile", "subject_sha", "outcome", "evidence_refs", "evidence_sha256"}, "entry")
        acceptance = string(entry["acceptance_id"], "acceptance_id")
        if acceptance in expected:
            raise GuardrailError("acceptance identifiers must be unique")
        if not isinstance(entry["issue"], int) or entry["issue"] <= 0 or not isinstance(entry["requires_actual_execution"], bool):
            raise GuardrailError("entry issue or actual-execution flag is invalid")
        if entry["evidence_kind"] not in schema["evidence_kinds"] or entry["outcome"] not in schema["outcomes"]:
            raise GuardrailError("entry evidence kind or outcome is invalid")
        string(entry["command"], "entry.command")
        string(entry["profile"], "entry.profile")
        if entry["subject_sha"] != record["subject_sha"]:
            raise GuardrailError("entry subject SHA must match ledger subject")
        refs = strings(entry["evidence_refs"], "entry.evidence_refs")
        if any(not SAFE_REF.fullmatch(ref) for ref in refs):
            raise GuardrailError("evidence references must use privacy-safe typed references")
        if not isinstance(entry["evidence_sha256"], str) or not SHA256.fullmatch(entry["evidence_sha256"]):
            raise GuardrailError("entry evidence_sha256 is invalid")
        if entry["requires_actual_execution"] and entry["evidence_kind"] != "actual-execution":
            raise GuardrailError("synthetic, mock, unit, or document evidence cannot satisfy actual execution")
        expected[acceptance] = (entry["outcome"], entry["evidence_sha256"])
    report = mapping(record["human_report"], "human_report")
    exact_keys(report, {"entries", "report_sha256"}, "human_report")
    projected: dict[str, tuple[str, str]] = {}
    if not isinstance(report["entries"], list):
        raise GuardrailError("human_report.entries must be a list")
    for item in report["entries"]:
        item = mapping(item, "human_report entry")
        exact_keys(item, {"acceptance_id", "outcome", "evidence_sha256"}, "human_report entry")
        projected[string(item["acceptance_id"], "human acceptance_id")] = (item["outcome"], item["evidence_sha256"])
    if projected != expected:
        raise GuardrailError("human report does not match acceptance evidence ledger")
    if report["report_sha256"] != digest(report["entries"]):
        raise GuardrailError("human report digest is invalid")
    reject_private(record, schema)
    sealed(record, "ledger_sha256")


def validate_retry(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "attempt", "failure", "prior_failure_sha256", "material_state_change_sha256", "new_authorization_refs", "decision", "retry_sha256"}, "retry")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["retry"]:
        raise GuardrailError("retry schema identity is invalid")
    if not isinstance(record["attempt"], int) or record["attempt"] < 1 or record["decision"] not in schema["retry_decisions"]:
        raise GuardrailError("retry attempt or decision is invalid")
    failure = mapping(record["failure"], "failure")
    exact_keys(failure, {"failure_class", "command_sha256", "subject_sha", "environment_class", "diagnostic_codes"}, "failure")
    string(failure["failure_class"], "failure_class")
    string(failure["environment_class"], "environment_class")
    strings(failure["diagnostic_codes"], "diagnostic_codes", empty=True)
    if not isinstance(failure["command_sha256"], str) or not SHA256.fullmatch(failure["command_sha256"]) or not isinstance(failure["subject_sha"], str) or not SHA40.fullmatch(failure["subject_sha"]):
        raise GuardrailError("failure identity is invalid")
    for field in ("prior_failure_sha256", "material_state_change_sha256"):
        if record[field] is not None and (not isinstance(record[field], str) or not SHA256.fullmatch(record[field])):
            raise GuardrailError(f"{field} is invalid")
    authorizations = strings(record["new_authorization_refs"], "new_authorization_refs", empty=True)
    if record["decision"] == "retry" and record["attempt"] >= 2 and record["material_state_change_sha256"] is None:
        raise GuardrailError("retry without material state change is forbidden")
    if record["decision"] == "retry" and record["attempt"] >= 3 and not authorizations:
        raise GuardrailError("attempt 3+ retry requires new owner or workflow authorization")
    reject_private(record, schema)
    sealed(record, "retry_sha256")


def validate_graph(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "project", "head_sha", "indexed_sha", "index_state", "coverage", "reindex_attempted", "fallback", "fallback_paths", "absence_claim", "freshness_sha256"}, "graph freshness")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["graph"]:
        raise GuardrailError("graph schema identity is invalid")
    string(record["project"], "project")
    if not isinstance(record["head_sha"], str) or not SHA40.fullmatch(record["head_sha"]):
        raise GuardrailError("graph head_sha is invalid")
    if record["indexed_sha"] is not None and (not isinstance(record["indexed_sha"], str) or not SHA40.fullmatch(record["indexed_sha"])):
        raise GuardrailError("graph indexed_sha is invalid")
    if record["index_state"] not in schema["graph_states"] or record["coverage"] not in schema["graph_coverage"] or record["fallback"] not in schema["graph_fallbacks"]:
        raise GuardrailError("graph freshness state is invalid")
    if not isinstance(record["reindex_attempted"], bool) or not isinstance(record["absence_claim"], bool):
        raise GuardrailError("graph booleans are invalid")
    paths = strings(record["fallback_paths"], "fallback_paths", empty=True)
    exact_complete = record["index_state"] == "fresh" and record["coverage"] == "complete" and record["indexed_sha"] == record["head_sha"]
    tracked_fallback = record["fallback"] == "tracked-search" and bool(paths)
    if record["index_state"] in {"stale", "missing"} and not record["reindex_attempted"] and not tracked_fallback:
        raise GuardrailError("stale or missing graph requires reindex or tracked fallback")
    if record["absence_claim"] and not (exact_complete or tracked_fallback):
        raise GuardrailError("search absence is not proof without exact complete index or tracked fallback")
    reject_private(record, schema)
    sealed(record, "freshness_sha256")


def validate_powershell_source(source: str, schema: dict[str, Any]) -> None:
    reserved = set(schema["reserved_powershell_variables"])
    assignment = re.compile(r"(?im)^\s*\$(?:global:|script:|local:)?([a-z_][a-z0-9_]*)\s*(?:=|\+=|-=|\+\+|--)")
    violations = sorted({match.group(1) for match in assignment.finditer(source) if match.group(1).lower() in reserved}, key=str.lower)
    if violations:
        raise GuardrailError(f"PowerShell reserved automatic variable assignment: {', '.join(violations)}")


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return mapping(value, str(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--packet", type=Path)
    group.add_argument("--lease", type=Path)
    group.add_argument("--evidence-ledger", type=Path)
    group.add_argument("--retry", type=Path)
    group.add_argument("--graph-freshness", type=Path)
    group.add_argument("--powershell-source", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema = load(SCHEMA_PATH)
    try:
        if args.packet:
            validate_packet(load(args.packet), schema)
        elif args.lease:
            validate_lease(load(args.lease), schema)
        elif args.evidence_ledger:
            validate_evidence(load(args.evidence_ledger), schema)
        elif args.retry:
            validate_retry(load(args.retry), schema)
        elif args.graph_freshness:
            validate_graph(load(args.graph_freshness), schema)
        elif args.powershell_source:
            validate_powershell_source(args.powershell_source.read_text(encoding="utf-8"), schema)
        else:
            required = {"schema_version", "contract_id", "record_types", "execution_kinds", "role_applicability", "permission_modes", "lease_states", "lease_access", "artifact_states", "evidence_kinds", "outcomes", "retry_decisions", "graph_states", "graph_coverage", "graph_fallbacks", "terminal_modes", "reserved_powershell_variables", "privacy_forbidden_keys"}
            exact_keys(schema, required, "schema")
        print("Agent execution guardrails passed.")
        return 0
    except (GuardrailError, OSError, yaml.YAMLError) as exc:
        print(f"Agent execution guardrails failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
