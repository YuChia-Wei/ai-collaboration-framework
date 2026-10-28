"""Versioned group values and immutable event/cut validation; no IO."""
from __future__ import annotations

import base64
import copy
from pathlib import Path
import re

from . import source_contract as c
from .common import relative_path
from .contracts import require
from .group_storage import FORMAT, bounded

PROFILE = "workflow-records/local-group/1"
PROVIDERS = "workflow-records/provider-control/1"
HANDOFF = "workflow-records/provider-handoff/1"
MAX_EVENTS = 256


def identifier(value):
    c.native_id(value)
    return value


def fingerprint(request):
    return c.digest(c.canonical({key: value for key, value in request.items() if key != "max_output_bytes"}))


def blob(value):
    c.fields(value, {"encoding", "content"})
    require(value["encoding"] in ("utf-8", "base64") and isinstance(value["content"], str), "invalid_input", "Use utf-8 or base64 content.")
    try:
        raw = value["content"].encode("utf-8") if value["encoding"] == "utf-8" else base64.b64decode(value["content"], validate=True)
    except (ValueError, UnicodeError):
        require(False, "invalid_input", "Invalid document bytes.")
    require(len(raw) <= 1024 * 1024, "limit_exceeded", "A group document is bounded to 1 MiB.")
    return {"encoding": "base64", "content": base64.b64encode(raw).decode("ascii"), "hash": c.digest(raw), "size": len(raw)}


def check_blob(value):
    c.fields(value, {"encoding", "content", "hash", "size"})
    require(value["encoding"] == "base64", "integrity_error", "Stored bytes require canonical base64.")
    normalized = blob({key: value[key] for key in ("encoding", "content")})
    require(normalized == value, "integrity_error", "Stored document hash or encoding differs.")


def check_state(state):
    if state is None:
        return
    c.fields(state, {"metadata", "tasks", "entrypoint", "documents", "attachments", "checkpoint"})
    require(isinstance(state["metadata"], dict) and isinstance(state["tasks"], list), "invalid_input", "Metadata/tasks have invalid types.")
    require(isinstance(state["metadata"].get("title"), str) and isinstance(state["metadata"].get("status"), str), "invalid_input", "Metadata requires title and status.")
    require(len(state["tasks"]) <= 128, "limit_exceeded", "Task capacity exceeded.")
    names = []
    for task in state["tasks"]:
        require(isinstance(task, dict), "invalid_input", "Tasks must be objects.")
        names.append(identifier(task.get("task_id")))
    require(len(set(names)) == len(names), "invalid_input", "Duplicate tasks.")
    for key in ("documents", "attachments"):
        require(isinstance(state[key], dict) and len(state[key]) <= 128, "limit_exceeded", "Invalid or excessive document collection.")
        folded = set()
        for path, value in state[key].items():
            relative_path(path)
            require(path.casefold() not in folded, "unsafe_path", "Case-aliased document paths are unsupported.")
            folded.add(path.casefold())
            check_blob(value)
    require(state["entrypoint"] in state["documents"], "invalid_input", "Entrypoint must name a document.")


def reduce_state(state, request):
    operation = request["operation"]
    if operation == "group-create":
        require(state is None, "already_exists", "Workflow already exists.")
        record = copy.deepcopy(request["record"])
        c.fields(record, {"metadata", "tasks", "entrypoint", "documents", "attachments"})
        for key in ("documents", "attachments"):
            require(isinstance(record[key], dict), "invalid_input", "Documents and attachments must be objects.")
            record[key] = {name: blob(value) for name, value in record[key].items()}
        record["checkpoint"] = None
    else:
        require(state is not None, "not_found", "Workflow has not been created.")
        record = copy.deepcopy(state)
        if operation == "group-create-task":
            record["tasks"].append(copy.deepcopy(request["task"]))
        elif operation == "group-checkpoint":
            from .common import validate_checkpoint
            validate_checkpoint(request["checkpoint"])
            record["checkpoint"] = copy.deepcopy(request["checkpoint"])
        elif operation == "group-write-document":
            relative_path(request["document"])
            record["documents"][request["document"]] = blob(request["content"])
        else:
            require(isinstance(request["metadata_patch"], dict), "invalid_input", "Metadata patch must be an object.")
            record["metadata"].update(copy.deepcopy(request["metadata_patch"]))
            patches = request["task_patches"]
            require(isinstance(patches, dict), "invalid_input", "Task patches must be an object.")
            tasks = {task["task_id"]: task for task in record["tasks"]}
            for name, patch in patches.items():
                require(name in tasks and isinstance(patch, dict) and "task_id" not in patch, "invalid_input", "Patch an existing task without changing its identity.")
                tasks[name].update(copy.deepcopy(patch))
            for key in ("documents", "attachments"):
                require(isinstance(request[key], dict), "invalid_input", "Document patches must be objects.")
                for path, value in request[key].items():
                    relative_path(path)
                    record[key][path] = blob(value)
    check_state(record)
    return record


def empty_envelope(identity):
    return seal({"format": FORMAT, "identity": identity, "events": [], "baselines": {},
                 "deliveries": {}, "aux_operations": {}, "handoffs": {}})


def seal(value):
    value.pop("checksum", None)
    value["checksum"] = c.digest(bounded(value))
    bounded(value)
    return value


def head(envelope):
    return envelope["events"][-1]["cut"] if envelope["events"] else None


def current(envelope):
    return envelope["events"][-1]["body"] if envelope["events"] else {"state": None, "providers": {}}


def validate_control(value, identity, repository_binding=None):
    c.fields(value, {"format", "group_ref", "repository_binding", "instance_id", "state", "configuration_revision", "authority_epoch", "authority", "members", "operations", "origin", "retirement"})
    require(value["format"] == "workflow-local-group-control/1" and value["group_ref"] == identity, "binding_mismatch", "Control identity/version differs.")
    require(isinstance(value["repository_binding"], str) and Path(value["repository_binding"]).is_absolute(), "integrity_error", "Invalid repository binding.")
    if repository_binding is not None:
        require(value["repository_binding"] == repository_binding, "binding_mismatch", "Control project root differs.")
    identifier(value["instance_id"])
    c.integer(value["configuration_revision"])
    c.integer(value["authority_epoch"], 1)
    require(value["state"] in ("active", "inactive", "retired") and isinstance(value["members"], dict) and 0 < len(value["members"]) <= 8,
            "integrity_error", "Invalid group state/member count.")
    require(isinstance(value["authority"], str) and value["authority"] in value["members"] and "file" in value["members"], "integrity_error", "Missing authority/default file member.")
    paths, generations = set(), set()
    for key, member in value["members"].items():
        identifier(key)
        c.fields(member, {"kind", "path", "generation", "active"})
        identifier(member["generation"])
        require(member["kind"] in ("file", "sqlite") and type(member["active"]) is bool and isinstance(member["path"], str) and Path(member["path"]).is_absolute(),
                "integrity_error", "Invalid member descriptor.")
        require(member["generation"] not in generations and member["path"].casefold() not in paths, "integrity_error", "Duplicate member location/generation.")
        paths.add(member["path"].casefold())
        generations.add(member["generation"])
    require(value["members"]["file"]["kind"] == "file" and value["members"][value["authority"]]["active"], "integrity_error", "Default/selected member is invalid.")
    require(isinstance(value["operations"], dict) and 0 < len(value["operations"]) <= 4096, "integrity_error", "Invalid administrative history.")
    for key, operation in value["operations"].items():
        identifier(key)
        c.fields(operation, {"request", "request_digest", "receipt"})
        request, result = operation["request"], operation["receipt"]
        require(isinstance(request, dict), "integrity_error", "Administrative request must be an object.")
        require(request.get("operation_id") == key and request.get("group_ref") == identity and request.get("contract_version") == PROFILE and
                request.get("operation") in ("group-init", "member-add", "member-remove", "select-authority", "group-deactivate", "group-restore", "group-activate") and
                operation["request_digest"] == fingerprint(request), "integrity_error", "Administrative request closure differs.")
        require(isinstance(result, dict) and result.get("operation_id") == key and result.get("state") == "applied" and result.get("replayed") is False,
                "integrity_error", "Administrative receipt closure differs.")
        if "configuration_revision" in result:
            c.integer(result["configuration_revision"], 0, value["configuration_revision"])
        if "authority_epoch" in result:
            c.integer(result["authority_epoch"], 1, value["authority_epoch"])
    if value["origin"] is not None:
        c.fields(value["origin"], {"instance_id", "snapshot_digest", "control_directory"})
        identifier(value["origin"]["instance_id"])
        require(isinstance(value["origin"]["control_directory"], str) and Path(value["origin"]["control_directory"]).is_absolute(), "integrity_error", "Invalid original control location.")
        require(re.fullmatch(r"sha256:[0-9a-f]{64}", value["origin"]["snapshot_digest"]) is not None, "integrity_error", "Invalid origin snapshot digest.")
    if value["state"] == "inactive":
        require(value["origin"] is not None and value["retirement"] is None, "integrity_error", "Inactive restore has invalid origin/retirement.")
    if value["state"] == "retired":
        retirement = value["retirement"]
        c.fields(retirement, {"seal", "snapshot_digest", "successor_instance_id"})
        identifier(retirement["seal"])
        require(re.fullmatch(r"sha256:[0-9a-f]{64}", retirement["snapshot_digest"]) is not None, "integrity_error", "Invalid retirement snapshot digest.")
        if retirement["successor_instance_id"] is not None:
            identifier(retirement["successor_instance_id"])
    else:
        require(value["retirement"] is None, "integrity_error", "An unretired group carries retirement state.")
    bounded(value)
    return value


def validate_observation(command, observed, *, persisted=False):
    """Apply the same pinned-command admission rules live and during recovery."""
    c.fields(observed, {"contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision", "outcome", "provider_revision"})
    binding_error = "integrity_error" if persisted else "binding_mismatch"
    input_error = "integrity_error" if persisted else "invalid_input"
    require(all(observed[key] == command[key] for key in
                ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")),
            binding_error, "Observation does not match the original handoff scope/digest/logical cut.")
    require(observed["outcome"] in ("accepted", "rejected", "conflict", "unknown"), input_error, "Unknown observation classification.")
    if observed["outcome"] == "accepted":
        require(isinstance(observed["provider_revision"], str) and 0 < len(observed["provider_revision"]) <= 1024,
                input_error, "Accepted provider revision must be bounded opaque text.")
    else:
        require(observed["provider_revision"] is None or isinstance(observed["provider_revision"], str),
                input_error, "Provider revision must be text or null.")
    return observed


def validate(envelope, identity):
    c.fields(envelope, {"format", "identity", "events", "baselines", "deliveries", "aux_operations", "handoffs", "checksum"})
    require(envelope["format"] == FORMAT and envelope["identity"] == identity, "binding_mismatch", "Carrier identity differs from the complete group reference.")
    require(envelope["checksum"] == c.digest(bounded({key: value for key, value in envelope.items() if key != "checksum"})), "integrity_error", "Complete envelope checksum differs.")
    require(isinstance(envelope["events"], list) and len(envelope["events"]) <= MAX_EVENTS, "limit_exceeded", "Retained event capacity exceeded.")
    from .group_providers import intents, intent_id
    previous, ids = None, set()
    predecessors = {}
    for index, event in enumerate(envelope["events"]):
        c.fields(event, {"cut", "body"})
        body = event["body"]
        c.fields(body, {"sequence", "parent", "operation_id", "request_digest", "request", "state", "providers", "targets", "configuration_revision", "authority_epoch"})
        require(body["sequence"] == index + 1 and body["parent"] == previous and event["cut"] == c.digest(c.canonical(body)), "integrity_error", "Immutable event chain differs.")
        require(identifier(body["operation_id"]) not in ids and fingerprint(body["request"]) == body["request_digest"], "integrity_error", "Operation identity/digest closure differs.")
        require(body["request"].get("operation_id") == body["operation_id"] and body["request"].get("group_ref") == identity,
                "binding_mismatch", "Event request identity differs.")
        ids.add(body["operation_id"])
        check_state(body["state"])
        require(isinstance(body["providers"], dict) and isinstance(body["targets"], list), "integrity_error", "Invalid event provider/target closure.")
        for provider_id, registered in body["providers"].items():
            identifier(provider_id)
            require(registered["current_generation"] in registered["generations"], "integrity_error", "Provider current generation is absent.")
            for generation, entry in registered["generations"].items():
                identifier(generation)
                desc = entry["descriptor"]
                require(type(entry["enabled"]) is bool and desc["provider_id"] == provider_id and desc["project_id"] == identity["project_id"] and
                        desc["protocol_version"] == HANDOFF and desc["settings_digest"] == c.digest(c.canonical(desc["settings_snapshot"])),
                        "integrity_error", "Pinned provider generation/settings differ.")
        for target in body["targets"]:
            require(target.get("kind") in ("local", "remote"), "integrity_error", "Unknown retained target.")
            identifier(target["generation"])
            if target["kind"] == "local":
                identifier(target["member_id"])
                require(target["expected_parent"] == body["parent"], "integrity_error", "Local target parent differs.")
            else:
                registration = body["providers"][target["provider_id"]]["generations"][target["generation"]]
                require(target["descriptor"] == registration["descriptor"] and registration["enabled"], "integrity_error", "Remote target lost its accepted generation.")
                scope = (target["provider_id"], target["generation"])
                require(target.get("predecessor_intent_id") == predecessors.get(scope), "integrity_error", "Remote target predecessor differs from its retained event order.")
                predecessors[scope] = intent_id(event["cut"], target)
        previous = event["cut"]
    for key in ("baselines", "deliveries", "aux_operations", "handoffs"):
        require(isinstance(envelope[key], dict) and len(envelope[key]) <= 4096, "limit_exceeded", "Invalid or excessive retained auxiliary records.")
    cuts = {event["cut"] for event in envelope["events"]}
    for baseline in envelope["baselines"].values():
        require(baseline["cut"] is None or baseline["cut"] in cuts, "integrity_error", "Baseline cut is not retained.")
        require(baseline["target"]["kind"] == "local" and baseline["target"]["expected_parent"] is None, "integrity_error", "Invalid baseline target.")
    targets = {row["intent_id"]: row for row in intents(envelope)}
    pinned_commands = {}
    for key, handoff in envelope["handoffs"].items():
        command = handoff["command"]
        c.fields(handoff, {"intent_id", "command"})
        c.fields(command, {"contract_version", "group_ref", "provider_id", "generation", "capability", "operation_id", "logical_revision", "expected_provider_revision", "registration", "payload", "request_digest"})
        require(command["contract_version"] == HANDOFF and command["capability"] == "replicate", "integrity_error", "Invalid handoff contract/capability.")
        require(command["request_digest"] == c.digest(c.canonical({name: value for name, value in command.items() if name != "request_digest"})) and
                key == "handoff-" + command["request_digest"][7:] and command["group_ref"] == identity and command["operation_id"] == handoff["intent_id"],
                "integrity_error", "Pinned handoff identity/hash differs.")
        event = next((item for item in envelope["events"] if item["cut"] == command["logical_revision"]), None)
        require(event is not None and command["payload"] == event["body"]["state"], "integrity_error", "Pinned handoff payload differs from its cut.")
        require(any(target["kind"] == "remote" and target["provider_id"] == command["provider_id"] and target["generation"] == command["generation"] and
                    target["descriptor"] == command["registration"] for target in event["body"]["targets"]), "integrity_error", "Handoff lost its fixed target.")
        intent = handoff["intent_id"]
        require(intent in targets and intent not in pinned_commands, "integrity_error", "Handoff requires one exact retained intent/command.")
        fixed = targets[intent]
        target = fixed["target"]
        require(target["kind"] == "remote" and fixed["cut"] == command["logical_revision"] and
                target["provider_id"] == command["provider_id"] and target["generation"] == command["generation"] and
                target["descriptor"] == command["registration"], "integrity_error", "Pinned command differs from its original fixed intent.")
        pinned_commands[intent] = command
    for key, value in envelope["aux_operations"].items():
        c.fields(value, {"request", "request_digest", "receipt"})
        require(value["request"]["operation_id"] == key and value["request"]["group_ref"] == identity and fingerprint(value["request"]) == value["request_digest"],
                "integrity_error", "Auxiliary operation closure differs.")
        require(value["receipt"]["operation_id"] == key and value["receipt"]["replayed"] is False and key not in ids, "integrity_error", "Auxiliary receipt identity differs.")
        if value["request"].get("operation") == "provider-prepare":
            request, result = value["request"], value["receipt"]
            c.fields(result, {"state", "operation_id", "handoff_id", "mode", "request", "backend_verification", "replayed"})
            intent = request.get("intent_id")
            require(intent in pinned_commands and request.get("mode") in ("command", "lookup"), "integrity_error", "Prepare receipt lost its original intent/mode.")
            command = pinned_commands[intent]
            expected = command if request["mode"] == "command" else {name: command[name] for name in
                       ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")}
            require(result["state"] == "prepared" and result["mode"] == request["mode"] and
                    result["handoff_id"] == "handoff-" + command["request_digest"][7:] and result["request"] == expected and
                    result["backend_verification"] == "unavailable", "integrity_error", "Prepare receipt differs from its original pinned command.")
    for key, status in envelope["deliveries"].items():
        require(key in targets and status.get("state") in ("pending", "accepted", "rejected", "conflict", "unknown"), "integrity_error", "Delivery lost its fixed intent/state.")
        c.integer(status.get("attempt_limit", 32), 32, 1024)
        c.integer(status["attempts"], 0, status.get("attempt_limit", 32))
        c.integer(status.get("observation_limit", 64), 64, 4096)
        require(type(status.get("dispatch_authorized", False)) is bool and isinstance(status.get("observations", []), list) and len(status.get("observations", [])) <= status.get("observation_limit", 64),
                "integrity_error", "Invalid delivery resume/observation history.")
        if targets[key]["target"]["kind"] == "remote":
            observations = status.get("observations", [])
            if observations or status["state"] == "accepted":
                require(key in pinned_commands, "integrity_error", "Remote observations/acceptance require the original retained handoff.")
                for observed in observations:
                    validate_observation(pinned_commands[key], observed, persisted=True)
        if targets[key]["target"]["kind"] == "remote" and status["state"] == "accepted":
            require(status["logical_revision"] == targets[key]["cut"] and isinstance(status["provider_revision"], str) and bool(status["provider_revision"]),
                    "integrity_error", "Accepted logical/provider revision closure differs.")
            require(any(observed.get("outcome") == "accepted" and observed.get("provider_revision") == status["provider_revision"] and observed.get("logical_revision") == status["logical_revision"]
                        for observed in status.get("observations", [])), "integrity_error", "Accepted remote delivery lacks its retained host assertion.")
    for intent, command in pinned_commands.items():
        predecessor = targets[intent]["target"]["predecessor_intent_id"]
        expected = None
        if predecessor is not None:
            status = envelope["deliveries"].get(predecessor, {})
            require(status.get("state") == "accepted", "integrity_error", "Prepared successor lacks accepted predecessor evidence.")
            expected = status["provider_revision"]
        require(command["expected_provider_revision"] == expected, "integrity_error", "Pinned provider revision differs from its accepted predecessor.")
    bounded(envelope)
    return envelope


def receipt(event, replayed=False):
    return {"state": "applied", "operation_id": event["body"]["operation_id"], "revision": event["cut"], "replayed": replayed}


def replay(envelope, request):
    for event in envelope["events"]:
        if event["body"]["operation_id"] == request["operation_id"]:
            require(event["body"]["request_digest"] == fingerprint(request), "operation_id_conflict", "Operation ID names a different request.")
            return receipt(event, True)
    prior = envelope["aux_operations"].get(request["operation_id"])
    if prior:
        require(prior["request_digest"] == fingerprint(request), "operation_id_conflict", "Operation ID names a different request.")
        return {**prior["receipt"], "replayed": True}
    return None


def save_aux(envelope, request, result):
    envelope["aux_operations"][request["operation_id"]] = {"request": copy.deepcopy(request), "request_digest": fingerprint(request), "receipt": copy.deepcopy(result)}
    return result
