"""Project-owned adapter descriptors and host-correlated handoffs; no execution."""
from __future__ import annotations

import copy

from . import source_contract as c
from .common import contained, relative_path
from .contracts import require
from . import group_model as m
from .group_storage import read_json


def descriptor(root, value):
    c.fields(value, {"provider_id", "implementation_ref", "implementation_version", "protocol_version", "project_id", "scope", "capabilities", "settings_non_secret"}, {"settings", "settings_file"})
    m.identifier(value["provider_id"])
    m.identifier(value["project_id"])
    m.identifier(value["scope"])
    require(value["protocol_version"] == m.HANDOFF and value["settings_non_secret"] is True, "invalid_input", "Only the explicit non-secret host-mediated protocol is supported.")
    require(isinstance(value["implementation_version"], str) and 0 < len(value["implementation_version"]) <= 160, "invalid_input", "Implementation version is required.")
    relative_path(value["implementation_ref"])
    # A reference is retained, never imported or launched. Managed copies are not project extension owners.
    for name in ("implementation_ref", "settings_file"):
        if name in value:
            relative_path(value[name])
            require(not value[name].casefold().startswith((".ai/", ".agents/", ".claude/", ".codex/")), "unsafe_path", "Provider resources must be project-owned outside managed runtime directories.")
            contained(root, value[name])
    capabilities = value["capabilities"]
    require(isinstance(capabilities, list) and capabilities == ["replicate"], "unsupported_capability", "This profile supports only replica handoffs; remote command authority is unavailable.")
    require(("settings" in value) != ("settings_file" in value), "invalid_input", "Select inline settings or an explicit settings file.")
    settings = copy.deepcopy(value["settings"]) if "settings" in value else read_json(contained(root, value["settings_file"]))
    require(isinstance(settings, dict) and len(c.canonical(settings)) <= 65536, "limit_exceeded", "Non-secret settings must be a bounded JSON object (64 KiB).")
    result = copy.deepcopy(value)
    result.pop("settings", None)
    result["settings_snapshot"] = settings
    result["settings_digest"] = c.digest(c.canonical(settings))
    return result


def revise(root, providers, request, project_id):
    value = copy.deepcopy(providers)
    operation = request["operation"]
    if operation in ("provider-register", "provider-update"):
        item = descriptor(root, request["registration"])
        require(item["project_id"] == project_id, "binding_mismatch", "Registration project differs from the group.")
        key = item["provider_id"]
        require((key in value) == (operation == "provider-update"), "already_exists" if operation == "provider-register" else "not_found", "Provider must be fresh for register and existing for update.")
        if key in value:
            require(request["expected_generation"] == value[key]["current_generation"], "configuration_conflict", "Provider generation changed.")
        generation = "generation-" + c.digest(c.canonical({"registration": item, "operation_id": request["operation_id"]}))[7:]
        history = value.setdefault(key, {"current_generation": generation, "generations": {}})
        history["current_generation"] = generation
        history["generations"][generation] = {"descriptor": item, "enabled": False}
        require(len(history["generations"]) <= 32 and len(value) <= 16, "limit_exceeded", "Provider generation capacity exceeded.")
    else:
        key = m.identifier(request["provider_id"])
        require(key in value, "not_found", "Provider is not registered.")
        generation = request["expected_generation"]
        require(generation == value[key]["current_generation"], "configuration_conflict", "Provider generation changed.")
        value[key]["generations"][generation]["enabled"] = operation == "provider-enable"
    return value


def remote_targets(envelope, providers):
    targets = []
    for key, registration in providers.items():
        generation = registration["current_generation"]
        item = registration["generations"][generation]
        if not item["enabled"]:
            continue
        predecessor = None
        for event in envelope["events"]:
            for target in event["body"]["targets"]:
                if target.get("provider_id") == key and target.get("generation") == generation:
                    predecessor = intent_id(event["cut"], target)
        targets.append({"kind": "remote", "provider_id": key, "generation": generation, "predecessor_intent_id": predecessor,
                        "descriptor": copy.deepcopy(item["descriptor"])})
    return targets


def intent_id(cut, target):
    return "intent-" + c.digest(c.canonical({"cut": cut, "target": target}))[7:]


def intents(envelope):
    rows = [{"intent_id": key, **baseline} for key, baseline in envelope["baselines"].items()]
    for event in envelope["events"]:
        for target in event["body"]["targets"]:
            rows.append({"intent_id": intent_id(event["cut"], target), "cut": event["cut"], "target": target})
    return rows


def prepare(envelope, identity, request):
    selected = next((row for row in intents(envelope) if row["intent_id"] == request["intent_id"]), None)
    require(selected and selected["target"]["kind"] == "remote", "not_found", "Remote intent is absent.")
    target = selected["target"]
    mode = request["mode"]
    require(mode in ("command", "lookup"), "invalid_input", "Select command or lookup.")
    # Disable affects new command dispatch, but never prevents original-identity lookup.
    providers = m.current(envelope)["providers"]
    registered = providers.get(target["provider_id"], {})
    generation = registered.get("generations", {}).get(target["generation"])
    require(generation is not None, "integrity_error", "Retained target generation is missing.")
    prior = envelope["deliveries"].get(selected["intent_id"], {})
    if mode == "command":
        require((generation["enabled"] and registered["current_generation"] == target["generation"]) or prior.get("dispatch_authorized") is True,
                "provider_disabled", "Generation is disabled/retired; lookup or explicit original-intent resume is available.")
    for row in intents(envelope):
        if row["intent_id"] == selected["intent_id"]:
            break
        if row["target"]["kind"] == "remote" and (row["target"]["provider_id"], row["target"]["generation"]) == (target["provider_id"], target["generation"]):
            require(envelope["deliveries"].get(row["intent_id"], {}).get("state") == "accepted", "predecessor_pending", "Previous provider intent is not accepted.")
    if mode == "command":
        require(prior.get("attempts", 0) < prior.get("attempt_limit", 32), "limit_exceeded", "Dispatch bound reached; lookup and explicit original-intent resume remain available.")
    event = next(event for event in envelope["events"] if event["cut"] == selected["cut"])
    saved = next((item["command"] for item in envelope["handoffs"].values() if item["intent_id"] == selected["intent_id"]), None)
    predecessor = target["predecessor_intent_id"]
    expected = envelope["deliveries"][predecessor]["provider_revision"] if predecessor else None
    command = saved or {"contract_version": m.HANDOFF, "group_ref": identity, "provider_id": target["provider_id"], "generation": target["generation"],
               "capability": "replicate", "operation_id": selected["intent_id"], "logical_revision": selected["cut"],
               "expected_provider_revision": expected, "registration": target["descriptor"],
               "payload": event["body"]["state"]}
    if saved is None:
        command["request_digest"] = c.digest(c.canonical(command))
    handoff_id = "handoff-" + command["request_digest"][7:]
    envelope["handoffs"][handoff_id] = {"intent_id": selected["intent_id"], "command": command}
    envelope["deliveries"][selected["intent_id"]] = {**prior, "state": prior.get("state", "pending"), "attempts": prior.get("attempts", 0) + (mode == "command")}
    return {"state": "prepared", "operation_id": request["operation_id"], "handoff_id": handoff_id,
            "mode": mode, "request": command if mode == "command" else {key: command[key] for key in ("contract_version", "group_ref", "provider_id", "generation", "operation_id", "request_digest", "logical_revision")},
            "backend_verification": "unavailable", "replayed": False}


def observe(envelope, request):
    saved = envelope["handoffs"].get(request["handoff_id"])
    require(saved is not None, "not_found", "Pinned handoff is absent.")
    command = saved["command"]
    observed = request["observation"]
    m.validate_observation(command, observed)
    status = envelope["deliveries"][saved["intent_id"]]
    if status["state"] == "accepted" and observed["outcome"] == "accepted":
        require(status["provider_revision"] == observed["provider_revision"], "revision_conflict", "Accepted opaque provider revision changed.")
    observations = status.setdefault("observations", [])
    require(len(observations) < status.get("observation_limit", 64), "limit_exceeded", "Observation history is full; explicitly resume the original intent.")
    observations.append(copy.deepcopy(observed))
    if status["state"] != "accepted":
        status["state"] = observed["outcome"]
        if observed["outcome"] == "accepted":
            status["provider_revision"] = observed["provider_revision"]
            status["logical_revision"] = observed["logical_revision"]
    return {"state": "observed", "operation_id": request["operation_id"], "intent_id": saved["intent_id"], "outcome": status["state"],
            "evidence_kind": "host-correlated-assertion", "backend_verification": "unavailable", "replayed": False}
