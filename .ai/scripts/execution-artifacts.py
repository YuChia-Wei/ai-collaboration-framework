#!/usr/bin/env python3
"""Prepare, check, finalize, or explicitly migrate bounded execution artifacts."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/execution-artifacts.py")

import yaml
from execution_artifact_contract import (
    ContractError, EXTERNAL_SCHEMA, EXTERNAL_VALIDATOR, GUARD_SCHEMA, GUARD_VALIDATOR,
    authority_manifest, digest, encoded, load_mapping, load_module, models_errors,
    record_model, sha256, structure_errors, template_value,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = {
    "dispatch": ".ai/assets/skills/software-development-orchestrator/templates/external-task-dispatch.template.yaml",
    "completion": ".ai/assets/skills/software-development-orchestrator/templates/external-task-completion.template.yaml",
    "prepare_request": ".ai/assets/skills/software-development-orchestrator/templates/execution-prepare-request.template.yaml",
    "observations": ".ai/assets/skills/software-development-orchestrator/templates/execution-observations.template.yaml",
}


def validators() -> tuple[Any, Any, dict, dict]:
    guard = load_module(ROOT / GUARD_VALIDATOR, "artifact_guardrails")
    external = load_module(ROOT / EXTERNAL_VALIDATOR, "artifact_delegation")
    # ROOT is explicit so isolated test repositories exercise actual filesystem/Git.
    guard.ROOT = external.ROOT = ROOT
    guard.SCHEMA_PATH = external.AGENT_SCHEMA_PATH = ROOT / GUARD_SCHEMA
    external.AGENT_VALIDATOR_PATH = ROOT / GUARD_VALIDATOR
    external.SCHEMA_PATH = ROOT / EXTERNAL_SCHEMA
    return guard, external, load_mapping(ROOT / GUARD_SCHEMA), load_mapping(ROOT / EXTERNAL_SCHEMA)


def require(errors: list[str]) -> None:
    if errors:
        raise ContractError("\n".join(errors))


def safe_output(ref: str, external: Any) -> Path:
    if external.canonical_repository_ref(ref) != ref or not external.git_ignores_reference(ref) or external.git_tracks_reference(ref):
        raise ContractError("output must be a canonical contained ignored untracked repository reference")
    path = ROOT / ref
    # Reject aliases, symlinks and Windows junctions even when they resolve inside ROOT.
    if path.resolve() != path or any(parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()) for parent in (path, *path.parents) if parent != ROOT and ROOT in parent.parents):
        raise ContractError("output aliases and linked directories are not supported")
    return path


def observed_git() -> dict:
    def git(*argv: str) -> str:
        result = subprocess.run(["git", "-C", str(ROOT), *argv], capture_output=True, text=True, encoding="utf-8", check=False, timeout=30)
        if result.returncode:
            raise ContractError("cannot observe repository Git identity")
        return result.stdout.strip()
    return {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"), "tracked_status": git("status", "--porcelain=v1", "--untracked-files=no")}


def exclusive_file(path: Path, value: bytes, owned: list[tuple[Path, str]]) -> None:
    with path.open("xb") as stream:
        owned.append((path, sha256(value)))
        stream.write(value)


def rollback(owned: list[tuple[Path, str]], directory: Path | None = None) -> None:
    # Only exact files exclusively created by this operation; never recursive delete.
    errors = []
    for path, expected_sha in reversed(owned):
        if path.resolve() != path or ROOT not in path.parents or (path.exists() and sha256(path.read_bytes()) != expected_sha):
            errors.append("cleanup refused an output whose identity or bytes changed")
        else:
            path.unlink(missing_ok=True)
    if directory is not None:
        try:
            directory.rmdir()
        except OSError:
            errors.append("cleanup preserved a non-empty output directory")
    require(errors)


def prepare(request: dict, output_ref: str) -> dict:
    guard, external, guard_schema, schema = validators()
    require(structure_errors(request, schema, "prepare_request"))
    require(models_errors(guard_schema) + external.validate_schema_definition(schema))
    output = safe_output(output_ref, external)
    if output.exists() or not output.parent.is_dir():
        raise ContractError("prepare requires a new output directory under an existing ignored parent")
    observed = observed_git()
    errors = []
    if observed["head"] != request["expected_commit_sha"]:
        errors.append("prepare expected_commit_sha does not match observed HEAD")
    if observed["tracked_status"]:
        errors.append("prepare requires a clean tracked worktree")
    cwd = Path(request["execution"]["working_directory"])
    cwd = (ROOT / cwd).resolve() if not cwd.is_absolute() else cwd.resolve()
    if not cwd.is_dir() or (cwd != ROOT and ROOT not in cwd.parents):
        errors.append("prepare working directory must exist inside this repository")
    review_ref = request.get("review_input")
    review_selected = request["task_kind"] in {"review", "fixed-head-audit", "independent-review"} or request["role"]["path"].endswith("/fixed-head-independent-auditor/sub-agent.yaml")
    review = None
    if review_selected and not review_ref:
        errors.append("selected review requires explicit review_input; objective prose cannot supply criteria")
    if review_ref:
        try:
            if external.canonical_repository_ref(review_ref) != review_ref:
                raise ContractError("review_input must be a canonical contained reference")
            review = load_mapping(ROOT / review_ref)
            guard.validate_review_input(review, guard_schema)
            if review["subject"]["head_sha"] != observed["head"]:
                errors.append("review_input subject differs from observed HEAD")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
    require(errors)
    refs = {name: f"{output_ref}/{name}.yaml" for name in ("packet", "dispatch", "candidate", "receipt", "review-input")}
    packet = {
        "schema_version": "1.1", "record_type": "agent-execution-packet", "packet_id": request["delegation_id"],
        "execution_kind": "external", "owning_skill": request["owning_skill"], "role": copy.deepcopy(request["role"]),
        "subject": {"repository": ROOT.name, "exact_sha": observed["head"]},
        "invocation": {"argv": request["execution"]["argv"], "cwd": request["execution"]["working_directory"]},
        "permissions": {"network": request["network"], "tracked_write": "deny", "provider_mutation": "deny"},
        "ignored_artifact_roots": [output_ref],
        "terminal": {"schema_ref": EXTERNAL_SCHEMA, "mode": "callback" if request["delivery"]["primary"] == "source-task-callback" else "event-wait", "destination": "source-task", "max_terminal_messages": 1},
        "integration_owner": request["source"]["final_integration_owner"], "stop_conditions": request["stop_conditions"], "retry": request["retry"],
        "review_input": {"ref": refs["review-input"], "sha256": sha256(encoded(review))} if review else None,
    }
    packet["packet_sha256"] = digest(packet)
    packet_bytes = encoded(packet)
    dispatch = {
        "schema_version": "1.3", "record_type": "external-task-dispatch", "delegation_id": request["delegation_id"], "task_kind": request["task_kind"],
        "source": request["source"], "objective": request["objective"],
        "subject": {"repository_root": ROOT.as_posix(), "commit_sha": observed["head"], "clean_worktree_required": True},
        "execution": request["execution"],
        "execution_packet": {"schema_ref": GUARD_SCHEMA, "packet_ref": refs["packet"], "packet_sha256": sha256(packet_bytes), "subject_sha": observed["head"], "validator_argv": external.canonical_agent_validator_argv(refs["packet"]), "validation_outcome": "passed"},
        "permissions": {"read_scope": ["repository"], "write_scope": ["ignored-validation-artifacts"], "repair_allowed": False, "external_mutations": [], "secret_values": "prohibited"},
        "completion_delivery": {**request["delivery"], "destination": "source-task", "progress_updates": "terminal-only", "max_terminal_reports": 1, "report_schema": "same-contract#completion", "pre_send_validation": {"required": True, "receipt_writer_argv": external.canonical_receipt_writer_argv(refs["candidate"], refs["dispatch"], refs["receipt"]), "dispatch_ref": refs["dispatch"], "candidate_ref": refs["candidate"], "receipt_ref": refs["receipt"], "failure_action": "do-not-deliver-terminal-report", "payload_binding": "exact-candidate-bytes-with-independent-receipt"}},
        "stop_conditions": request["stop_conditions"], "authority_manifest": authority_manifest(ROOT, packet),
    }
    require(structure_errors(packet, guard_schema, "packet") + structure_errors(dispatch, schema, "dispatch"))
    owned: list[tuple[Path, str]] = []
    output.mkdir()  # exclusive reservation; collision never reuses another task's bundle
    try:
        if review:
            exclusive_file(ROOT / refs["review-input"], encoded(review), owned)
        exclusive_file(ROOT / refs["packet"], packet_bytes, owned)
        guard.validate_packet(packet, guard_schema)
        require(external.validate_dispatch(dispatch, schema))
        # validation_outcome above describes this validator execution only.
        if observed_git() != observed:
            raise ContractError("prepare observed Git state drifted during preparation")
        dispatch_bytes = encoded(dispatch)
        exclusive_file(ROOT / refs["dispatch"], dispatch_bytes, owned)
        transport = schema["prompt_transport"]
        message = (transport["begin_marker"] + "\n").encode() + dispatch_bytes + (transport["end_marker"] + "\n").encode()
        parsed_dispatch = external.extract_dispatch_from_prompt(message.decode("utf-8"))
        require(external.validate_exact_mapping_bytes(parsed_dispatch, dispatch_bytes, "dispatch"))
        require(external.validate_dispatch(parsed_dispatch, schema))
        exclusive_file(output / "dispatch-message.txt", message, owned)
    except BaseException:
        rollback(owned, output)
        raise
    return {"operation": "prepare", "state": "ready", "dispatch_ref": refs["dispatch"], "dispatch_message_ref": f"{output_ref}/dispatch-message.txt", "packet_ref": refs["packet"], "execution_observed": False}


def finalize(observations: dict, dispatch_ref: str) -> dict:
    _, external, _, schema = validators()
    require(structure_errors(observations, schema, "observations"))
    dispatch_path = safe_output(dispatch_ref, external)
    dispatch_bytes = dispatch_path.read_bytes()
    dispatch = load_mapping(dispatch_path)
    require(external.validate_dispatch(dispatch, schema))
    if dispatch["schema_version"] != "1.3":
        raise ContractError("finalize requires explicit current 1.3 preparation")
    pre_send = dispatch["completion_delivery"]["pre_send_validation"]
    if pre_send["dispatch_ref"] != dispatch_ref:
        raise ContractError("finalize dispatch path differs from its declared ref")
    candidate_path = safe_output(pre_send["candidate_ref"], external)
    receipt_path = safe_output(pre_send["receipt_ref"], external)
    terminal_ref = str(Path(pre_send["candidate_ref"]).parent / "terminal-message.txt").replace("\\", "/")
    terminal_path = safe_output(terminal_ref, external)
    if candidate_path.exists() or receipt_path.exists() or terminal_path.exists():
        raise ContractError("finalize refuses an existing candidate or receipt or terminal message")
    candidate = {
        "schema_version": "1.3", "record_type": "external-task-completion", "delegation_id": dispatch["delegation_id"],
        "source_task_id": observations["source_task_id"], "delegated_task_id": observations["delegated_task_id"],
        "subject": {"expected_commit_sha": dispatch["subject"]["commit_sha"], "observed_commit_sha": observations["observed_commit_sha"]},
        **{key: copy.deepcopy(observations[key]) for key in ("preflight", "execution", "timing", "result", "evidence", "final_state")},
        "delivery": {"mode": observations["delivery_mode"], "destination": "source-task", "terminal_report_number": 1},
    }
    require(external.validate_completion(candidate, schema, dispatch))
    candidate_bytes = encoded(candidate)
    owned: list[tuple[Path, str]] = []
    try:
        exclusive_file(candidate_path, candidate_bytes, owned)
        require(external.validate_receipt_write_request(Path(pre_send["candidate_ref"]), Path(dispatch_ref), Path(pre_send["receipt_ref"]), dispatch))
        if dispatch_path.read_bytes() != dispatch_bytes:
            raise ContractError("dispatch changed during finalize")
        receipt = external.build_validation_receipt(candidate, dispatch, pre_send["candidate_ref"], candidate_bytes, dispatch_ref, dispatch_bytes, pre_send["receipt_ref"])
        require(external.validate_receipt(receipt, schema, candidate, candidate_bytes, dispatch, dispatch_bytes))
        require(external.write_receipt_exclusively(receipt_path, receipt))
        receipt_bytes = yaml.safe_dump(receipt, sort_keys=False).encode("utf-8")
        owned.append((receipt_path, sha256(receipt_bytes)))
        if receipt_path.read_bytes() != receipt_bytes or candidate_path.read_bytes() != candidate_bytes or dispatch_path.read_bytes() != dispatch_bytes:
            raise ContractError("custody bytes changed during finalize")
        terminal_bytes = (
            (external.COMPLETION_BEGIN_MARKER + "\n").encode() + candidate_bytes
            + (external.COMPLETION_END_MARKER + "\n" + external.RECEIPT_BEGIN_MARKER + "\n").encode()
            + receipt_bytes + (external.RECEIPT_END_MARKER + "\n").encode()
        )
        require(external.validate_terminal_delivery_message(terminal_bytes.decode("utf-8"), schema, dispatch, dispatch_bytes))
        exclusive_file(terminal_path, terminal_bytes, owned)
    except BaseException:
        rollback(owned)
        raise
    return {"operation": "finalize", "candidate_ref": pre_send["candidate_ref"], "receipt_ref": pre_send["receipt_ref"], "terminal_message_ref": terminal_ref, "execution_outcome": candidate["result"]["outcome"], "observations_source": "caller-supplied actual observations", "validator_outcome": "passed", "execution_run_by_tool": False}


def migrate(source_ref: str, target_version: str, output_ref: str | None, dispatch_ref: str | None = None) -> dict:
    _, external, _, schema = validators()
    if external.canonical_repository_ref(source_ref) != source_ref:
        raise ContractError("migration source must be a canonical contained reference")
    source = ROOT / source_ref
    source_bytes = source.read_bytes()
    record = load_mapping(source)
    family = {"external-task-dispatch": "dispatch", "external-task-completion": "completion"}.get(record.get("record_type"))
    if family is None or record.get("schema_version") != "1.2" or target_version != "1.3":
        raise ContractError("unsupported migration; only dispatch/completion 1.2 -> 1.3 is supported; receipts are never migrated")
    require(structure_errors(record, schema, family))
    migrated = copy.deepcopy(record)
    migrated["schema_version"] = "1.3"
    if family == "dispatch":
        require(external.validate_dispatch(record, schema))
        packet = load_mapping(ROOT / record["execution_packet"]["packet_ref"])
        migrated["authority_manifest"] = authority_manifest(ROOT, packet)
        if output_ref:
            refs = {key: f"{output_ref}/{key}.yaml" for key in ("dispatch", "candidate", "receipt")}
            pre_send = migrated["completion_delivery"]["pre_send_validation"]
            pre_send.update({f"{key}_ref": ref for key, ref in refs.items()})
            pre_send["receipt_writer_argv"] = external.canonical_receipt_writer_argv(refs["candidate"], refs["dispatch"], refs["receipt"])
            # The original packet's declared ignored root must cover the new bundle.
        require(external.validate_dispatch(migrated, schema))
    else:
        if not dispatch_ref or external.canonical_repository_ref(dispatch_ref) != dispatch_ref:
            raise ContractError("completion migration requires an explicit current 1.3 --dispatch")
        dispatch = load_mapping(ROOT / dispatch_ref)
        if dispatch.get("schema_version") != "1.3":
            raise ContractError("completion migration requires a current 1.3 dispatch")
        require(external.validate_dispatch(dispatch, schema))
        require(external.validate_completion(migrated, schema, dispatch))
    changes = ["schema_version: 1.2 -> 1.3"]
    if family == "dispatch":
        changes.append("bind current validation authority (not historical execution authority)")
        if output_ref:
            changes.append("bind new candidate/dispatch/receipt paths")
    report = {"operation": "migrate", "source_ref": source_ref, "source_sha256": sha256(source_bytes), "target_version": target_version, "changes": changes, "execution_facts_changed": False, "receipt_created": False, "preview": migrated}
    if output_ref:
        output = safe_output(output_ref, external)
        if output.exists() or not output.parent.is_dir():
            raise ContractError("migration requires a new output directory under an existing ignored parent")
        owned: list[tuple[Path, str]] = []
        output.mkdir()
        try:
            exclusive_file(output / f"{family}.yaml", encoded(migrated), owned)
            exclusive_file(output / "migration.yaml", encoded({key: value for key, value in report.items() if key != "preview"}), owned)
            if source.read_bytes() != source_bytes:
                raise ContractError("migration source changed during conversion")
        except BaseException:
            rollback(owned, output)
            raise
        report["output_ref"] = f"{output_ref}/{family}.yaml"
    return report


def check(ref: str, dispatch_ref: str | None, historical: bool = False) -> dict:
    guard, external, guard_schema, schema = validators()
    if external.canonical_repository_ref(ref) != ref:
        raise ContractError("check input must be a canonical contained reference")
    record = load_mapping(ROOT / ref)
    kind = record.get("record_type")
    families = {"agent-execution-packet": "packet", "external-task-dispatch": "dispatch", "external-task-completion": "completion", "external-task-validation-receipt": "receipt"}
    family = families.get(kind)
    if family is None:
        raise ContractError("check supports packet, dispatch, completion and receipt records")
    if historical:
        require(structure_errors(record, guard_schema if family == "packet" else schema, family))
        return {"state": "historical-structure-readable", "admission": False, "behavioral_execution_verified": False}
    if family == "packet":
        guard.validate_packet(record, guard_schema)
    elif family == "dispatch":
        require(external.validate_dispatch(record, schema))
    else:
        if not dispatch_ref or external.canonical_repository_ref(dispatch_ref) != dispatch_ref:
            raise ContractError("completion and receipt check require --dispatch")
        dispatch_path = ROOT / dispatch_ref
        dispatch = load_mapping(dispatch_path)
        require(external.validate_dispatch(dispatch, schema))
        if family == "completion":
            require(external.validate_completion(record, schema, dispatch))
        else:
            pre_send = dispatch["completion_delivery"]["pre_send_validation"]
            require(external.validate_receipt_verification_request(Path(pre_send["candidate_ref"]), Path(dispatch_ref), Path(ref), dispatch))
            candidate_path = ROOT / pre_send["candidate_ref"]
            require(external.validate_receipt(record, schema, load_mapping(candidate_path), candidate_path.read_bytes(), dispatch, dispatch_path.read_bytes()))
    return {"state": "validated", "record_type": kind, "execution_run_by_tool": False}


def templates(check_only: bool) -> dict:
    schema = load_mapping(ROOT / EXTERNAL_SCHEMA)
    require(models_errors(schema))
    errors = []
    for family, ref in TEMPLATES.items():
        version = "1.0" if family in {"prepare_request", "observations"} else "1.3"
        content = b"# Generated by execution-artifacts.py templates; placeholders are not execution facts.\n" + encoded(template_value(record_model(schema, family, version)))
        path = ROOT / ref
        if check_only:
            if not path.is_file() or path.read_bytes() != content:
                errors.append(f"generated template drift: {ref}")
        else:
            path.write_bytes(content)
    require(errors)
    return {"operation": "templates", "state": "current"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    p = modes.add_parser("prepare"); p.add_argument("--request", required=True, type=Path); p.add_argument("--output", required=True)
    p = modes.add_parser("finalize"); p.add_argument("--observations", required=True, type=Path); p.add_argument("--dispatch", required=True)
    p = modes.add_parser("migrate"); p.add_argument("--source", required=True); p.add_argument("--to-version", required=True); p.add_argument("--output"); p.add_argument("--dispatch"); p.add_argument("--dry-run", action="store_true")
    p = modes.add_parser("check"); p.add_argument("record"); p.add_argument("--dispatch"); p.add_argument("--historical", action="store_true")
    p = modes.add_parser("templates"); p.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.mode == "prepare": result = prepare(load_mapping(args.request), args.output)
        elif args.mode == "finalize": result = finalize(load_mapping(args.observations), args.dispatch)
        elif args.mode == "migrate":
            if args.dry_run and args.output: raise ContractError("--dry-run and --output are mutually exclusive")
            if not args.dry_run and not args.output: raise ContractError("select --dry-run or a new --output explicitly")
            result = migrate(args.source, args.to_version, args.output, args.dispatch)
        elif args.mode == "check": result = check(args.record, args.dispatch, args.historical)
        else: result = templates(args.check)
        print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (ValueError, OSError, yaml.YAMLError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "preparation-failed", "errors": str(exc).splitlines(), "behavioral_outcome": "not-executed-by-this-tool"}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
