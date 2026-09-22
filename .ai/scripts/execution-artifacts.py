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
    AUTHORITY_REFS, StrictLoader, authority_manifest, digest, encoded, load_mapping, load_module, models_errors,
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


def validate_prepare_request(request: dict, loaded: tuple | None = None) -> tuple[dict, dict | None]:
    """Validate explicit input facts without creating a packet or dispatch."""
    guard, external, guard_schema, schema = loaded or validators()
    require(structure_errors(request, schema, "prepare_request"))
    require(models_errors(guard_schema) + external.validate_schema_definition(schema))
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
    return observed, review


INPUT_KINDS = ("review-input", "prepare-request", "dependency-request", "evidence-ledger")


def input_fields(value: Any, required: set[str], optional: set[str] | None = None) -> None:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - (optional or set()):
        raise ContractError("input fields do not match the selected authoring operation")


def input_file(ref: str, watched: dict[str, str], external: Any) -> bytes:
    """Observe exact local bytes without accepting aliases or linked ancestors."""
    if not isinstance(ref, str) or external.canonical_repository_ref(ref) != ref:
        raise ContractError("input reference must be canonical and repository-relative")
    path = ROOT / ref
    chain = (path, *path.parents)
    if path.resolve() != path or any(p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()) for p in chain):
        raise ContractError("linked input paths are unsupported")
    data = path.read_bytes()
    watched[ref] = sha256(data)
    return data


def input_authority_bytes(ref: str, external: Any) -> bytes:
    # A fixed package-envelope key is available only to the runtime, never to
    # caller-selected input paths. Match the existing prerequisite boundary.
    if ref == "package-envelope:requirements.txt":
        path = ROOT.parent / "requirements.txt"
        if (ROOT / "requirements.txt").exists() or path.resolve() != path or any(
            part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()) for part in (path, *path.parents)
        ):
            raise ContractError("package-envelope requirements authority changed or is linked")
        return path.read_bytes()
    return input_file(ref, {}, external)


def build_review_subject(repository: str, base_sha: str, head_sha: str, guard: Any) -> dict:
    """Produce the canonical content subject; it grants no review or admission."""
    import re
    if not isinstance(repository, str) or not repository.strip():
        raise ContractError("repository identity must be supplied explicitly")
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value) for value in (base_sha, head_sha)):
        raise ContractError("review base and expected head must be full commit identities")
    for value in (base_sha, head_sha):
        result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-t", value], capture_output=True, text=True, check=False, timeout=30)
        if result.returncode or result.stdout.strip() != "commit":
            raise ContractError("review identities must name commits, not trees or other Git objects")
    trees = [guard.git_tree_identity(value) for value in (base_sha, head_sha)]
    if not all(trees):
        raise ContractError("review commits must resolve to existing trees")
    return {"schema_version": "independent-review-subject/v1", "repository_id": repository,
            "base_tree": trees[0], "head_tree": trees[1]}


def build_review_input(request: dict, watched: dict[str, str], loaded: tuple) -> dict:
    guard, external, guard_schema, _ = loaded
    input_fields(request, {"version", "expected_head", "repository", "base_sha", "classification", "criteria", "authority_paths"})
    if not isinstance(request["authority_paths"], list) or not request["authority_paths"]:
        raise ContractError("authority_paths must be a non-empty explicit list")
    content = build_review_subject(request["repository"], request["base_sha"], request["expected_head"], guard)
    record = {"schema_version": "1.0", "record_type": "independent-review-input",
              "classification": copy.deepcopy(request["classification"]),
              "subject": {"repository": request["repository"], "base_sha": request["base_sha"], "head_sha": request["expected_head"],
                          "base_tree": content["base_tree"], "head_tree": content["head_tree"], "subject_digest": digest(content)},
              "criteria": copy.deepcopy(request["criteria"]),
              "authority": [{"path": ref, "sha256": sha256(input_file(ref, watched, external))} for ref in request["authority_paths"]]}
    guard.validate_review_input(record, guard_schema)
    return record


def build_prepare_request(request: dict, watched: dict[str, str], loaded: tuple) -> dict:
    _, external, _, schema = loaded
    fields = set(record_model(schema, "prepare_request", "1.0")["required"]) - {"schema_version", "record_type"}
    fields.remove("expected_commit_sha")
    input_fields(request, fields | {"version", "expected_head"}, {"review_input"})
    record = {key: copy.deepcopy(value) for key, value in request.items() if key not in {"version", "expected_head"}}
    record.update(schema_version="1.0", record_type="execution-prepare-request", expected_commit_sha=request["expected_head"])
    validate_prepare_request(record, loaded)
    for ref in (record["role"].get("path"), f".ai/assets/skills/{record['owning_skill']}/skill.yaml", record.get("review_input")):
        if ref:
            input_file(ref, watched, external)
    return record


def build_dependency_request(request: dict, watched: dict[str, str], loaded: tuple) -> dict:
    _, external, _, _ = loaded
    input_fields(request, {"version", "expected_head", "validator_id", "harness", "entrypoint", "callable", "argv", "declared_dependencies"})
    for ref in (".ai/scripts/observe-validation-dependencies.py", ".ai/assets/shared/validation-dependency-observation.schema.yaml"):
        input_file(ref, watched, external)
    observer = load_module(ROOT / ".ai/scripts/observe-validation-dependencies.py", "artifact_input_observer")
    record = {key: copy.deepcopy(value) for key, value in request.items() if key not in {"version", "expected_head"}}
    record.update(schema_version=observer.REQUEST_SCHEMA, subject=request["expected_head"])
    record = observer.validate_request(record, ROOT)
    if record["harness"] != observer.SUPPORTED_HARNESS:
        raise ContractError("input authoring supports only the current observation harness")
    for ref in (record["entrypoint"], *record["declared_dependencies"]["file"]):
        input_file(ref, watched, external)
    return record


def build_evidence_ledger(request: dict, watched: dict[str, str], loaded: tuple) -> dict:
    guard, external, guard_schema, _ = loaded
    input_fields(request, {"version", "expected_head", "entries"})
    if not isinstance(request["entries"], list) or not request["entries"]:
        raise ContractError("ledger entries must be non-empty")
    entries = []
    for supplied in request["entries"]:
        input_fields(supplied, {"acceptance_id", "issue", "requires_actual_execution", "evidence_kind", "command", "profile", "outcome", "evidence_ref"}, {"execution_receipt_ref"})
        if type(supplied["issue"]) is not int or supplied["issue"] <= 0:
            raise ContractError("ledger issue must be a positive integer, not a boolean")
        ref = supplied["evidence_ref"]
        if not isinstance(ref, str) or ":" not in ref:
            raise ContractError("evidence must be an explicit typed local reference")
        prefix, local_ref = ref.split(":", 1)
        if prefix not in {"ignored", "run", "job", "tracked", "workflow", "fixture"}:
            raise ContractError("ledger authoring requires file-backed evidence")
        if prefix == "ignored" and (not external.git_ignores_reference(local_ref) or external.git_tracks_reference(local_ref)):
            raise ContractError("ignored evidence must be ignored and untracked")
        if prefix == "tracked" and not external.git_tracks_reference(local_ref):
            raise ContractError("tracked evidence must be tracked")
        entry = {key: copy.deepcopy(supplied[key]) for key in ("acceptance_id", "issue", "requires_actual_execution", "evidence_kind", "command", "profile", "outcome")}
        entry.update(subject_sha=request["expected_head"], evidence_refs=[ref], evidence_sha256=sha256(input_file(local_ref, watched, external)),
                     execution_receipt_ref=None, execution_receipt_file_sha256=None, execution_receipt=None)
        receipt_ref = supplied.get("execution_receipt_ref")
        if receipt_ref is not None:
            if not isinstance(receipt_ref, str) or ":" not in receipt_ref:
                raise ContractError("execution receipt requires a typed local reference")
            receipt_path = receipt_ref.split(":", 1)[1]
            if not receipt_ref.startswith("ignored:") or not external.git_ignores_reference(receipt_path) or external.git_tracks_reference(receipt_path):
                raise ContractError("execution receipts must be ignored and untracked")
            receipt_bytes = input_file(receipt_path, watched, external)
            entry.update(execution_receipt_ref=receipt_ref, execution_receipt_file_sha256=sha256(receipt_bytes),
                         execution_receipt=yaml.load(receipt_bytes, Loader=StrictLoader))
        entries.append(entry)
    projected = [{key: entry[key] for key in ("acceptance_id", "outcome", "evidence_sha256")} for entry in entries]
    record = {"schema_version": "1.0", "record_type": "acceptance-evidence-ledger", "subject_sha": request["expected_head"],
              "entries": entries, "human_report": {"entries": projected, "report_sha256": digest(projected)}}
    record["ledger_sha256"] = digest(record)
    guard.validate_evidence(record, guard_schema)
    return record


def author_input(kind: str, request: dict, output_ref: str | None = None, expected: str | None = None) -> dict:
    """Preview or create one new input; never execute, admit, acquire or release."""
    if kind not in INPUT_KINDS or not isinstance(request, dict) or request.get("version") != "1.0":
        raise ContractError("unsupported input kind or request version")
    loaded = validators()
    _, external, _, _ = loaded
    observed = observed_git()
    if observed["head"] != request.get("expected_head") or observed["tracked_status"]:
        raise ContractError("input authoring requires the expected clean tracked HEAD")
    watched: dict[str, str] = {}
    for ref in (*AUTHORITY_REFS, ".gitignore"):
        if ref == "requirements.txt" and not (ROOT / ref).is_file():
            ref = "package-envelope:requirements.txt"
        watched[ref] = sha256(input_authority_bytes(ref, external))
    builders = {"review-input": build_review_input, "prepare-request": build_prepare_request,
                "dependency-request": build_dependency_request, "evidence-ledger": build_evidence_ledger}
    record = builders[kind](request, watched, loaded)
    # Canonicalization also refuses non-finite numbers and unsupported YAML values.
    binding = digest({"kind": kind, "request": request, "record": record, "git": observed, "inputs": watched})
    for ref, value in list(watched.items()):
        if sha256(input_authority_bytes(ref, external)) != value:
            raise ContractError("input bytes drifted during preparation")
    if observed_git() != observed:
        raise ContractError("Git state drifted during input preparation")
    if output_ref is None:
        if expected is not None:
            raise ContractError("--expect requires --output")
        return {"operation": "input", "kind": kind, "state": "preview", "preview_digest": binding,
                "record": record, "execution_run_by_tool": False, "admission_granted": False}
    if expected != binding:
        raise ContractError("input preview changed; inspect a fresh preview before writing")
    output = safe_output(output_ref, external)
    if output.exists() or not output.parent.is_dir():
        raise ContractError("input requires a new file under an existing ignored parent")
    owned: list[tuple[Path, str]] = []
    try:
        exclusive_file(output, encoded(record), owned)
        for ref, value in watched.items():
            if sha256(input_authority_bytes(ref, external)) != value:
                raise ContractError("input bytes drifted during publication")
        if observed_git() != observed:
            raise ContractError("Git state drifted during input publication")
    except BaseException:
        rollback(owned)
        raise
    return {"operation": "input", "kind": kind, "state": "authored", "output_ref": output_ref,
            "preview_digest": binding, "execution_run_by_tool": False, "admission_granted": False}


def prepare(request: dict, output_ref: str) -> dict:
    loaded = validators()
    guard, external, guard_schema, schema = loaded
    require(structure_errors(request, schema, "prepare_request"))
    require(models_errors(guard_schema) + external.validate_schema_definition(schema))
    output = safe_output(output_ref, external)
    if output.exists() or not output.parent.is_dir():
        raise ContractError("prepare requires a new output directory under an existing ignored parent")
    observed, review = validate_prepare_request(request, loaded)
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
    p = modes.add_parser("input", help="preview or author current input records; no execution or admission")
    p.add_argument("--kind", choices=INPUT_KINDS, required=True); p.add_argument("--request", type=Path, required=True)
    p.add_argument("--output"); p.add_argument("--expect", help="digest from the unchanged input preview")
    args = parser.parse_args()
    try:
        if args.mode == "prepare": result = prepare(load_mapping(args.request), args.output)
        elif args.mode == "finalize": result = finalize(load_mapping(args.observations), args.dispatch)
        elif args.mode == "migrate":
            if args.dry_run and args.output: raise ContractError("--dry-run and --output are mutually exclusive")
            if not args.dry_run and not args.output: raise ContractError("select --dry-run or a new --output explicitly")
            result = migrate(args.source, args.to_version, args.output, args.dispatch)
        elif args.mode == "check": result = check(args.record, args.dispatch, args.historical)
        elif args.mode == "input": result = author_input(args.kind, load_mapping(args.request), args.output, args.expect)
        else: result = templates(args.check)
        print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (ValueError, OSError, yaml.YAMLError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"state": "preparation-failed", "errors": str(exc).splitlines(), "behavioral_outcome": "not-executed-by-this-tool"}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
