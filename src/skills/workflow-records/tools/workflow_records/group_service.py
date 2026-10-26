"""One workflow, one selected local authority, exact ordered replica delivery."""
from __future__ import annotations

import copy
from pathlib import Path
import uuid

from . import source_contract as c
from .contracts import RecordError, require
from . import group_model as m
from . import group_providers as p
from .group_storage import (MAX_BYTES, atomic_json, bounded, envelope_digest, group_lock,
                            load_member, local_path, read_json, save_member)

CONFIG = "workflow-records/local-group-config/1"
CONTROL = "workflow-local-group-control/1"
READS = {"group-configuration", "group-context", "group-resume", "group-read", "group-operation", "group-sync-status", "provider-list", "provider-inspect"}
WORKFLOW = {"group-create", "group-create-task", "group-checkpoint", "group-write-document", "group-revise-workflow"}
PROVIDER_MUTATIONS = {"provider-register", "provider-update", "provider-enable", "provider-disable", "provider-prepare", "provider-observe"}
ADMIN = {"member-add", "member-remove", "select-authority", "group-deactivate", "group-activate"}
EXTRAS = {
    "group-init": set(), "group-configuration": set(), "group-context": set(), "group-resume": set(),
    "group-read": {"document", "collection"}, "group-operation": {"lookup_operation_id"}, "group-sync-status": set(),
    "group-create": {"record"}, "group-create-task": {"task"}, "group-checkpoint": {"checkpoint"},
    "group-write-document": {"document", "content"},
    "group-revise-workflow": {"metadata_patch", "task_patches", "documents", "attachments"},
    "member-add": {"member_id", "kind", "path"}, "member-remove": {"member_id", "expected_generation"},
    "select-authority": {"member_id", "expected_generation"}, "group-sync": {"intent_id"}, "group-resume-intent": {"intent_id", "additional_attempts"},
    "provider-list": set(), "provider-inspect": {"provider_id"},
    "provider-register": {"registration"}, "provider-update": {"registration", "expected_generation"},
    "provider-enable": {"provider_id", "expected_generation"}, "provider-disable": {"provider_id", "expected_generation"},
    "provider-prepare": {"intent_id", "mode"}, "provider-observe": {"handoff_id", "observation"},
    "group-export": {"destination"}, "group-preflight": {"archive", "archive_digest"},
    "group-restore": {"archive", "archive_digest", "member_paths"},
    "group-deactivate": {"snapshot_digest"}, "group-activate": {"original_control_directory", "retirement_seal"},
}


class LocalGroup:
    def __init__(self, root, config):
        self.root = Path(root).resolve()
        require(self.root.is_dir(), "not_found", "Explicit project root is missing.")
        c.fields(config, {"contract_version", "group_ref", "control_directory", "file_path"})
        require(config["contract_version"] == CONFIG, "unsupported_version", "Unsupported group configuration.")
        c.fields(config["group_ref"], {"group_id", "project_id", "workflow_id"})
        for value in config["group_ref"].values():
            m.identifier(value)
        self.identity = copy.deepcopy(config["group_ref"])
        self.directory = local_path(config["control_directory"])
        self.file_path = local_path(config["file_path"])
        self.check_path(self.file_path)
        self.control_path = self.directory / "control.json"
        self.transition_path = self.directory / "transition.json"

    def check_path(self, path, members=(), *, require_parent=False):
        require(path != self.directory and not path.is_relative_to(self.directory) and not self.directory.is_relative_to(path),
                "unsafe_path", "Carrier and control roots must not overlap.")
        if require_parent:
            require(path.parent.is_dir(), "not_found", "Explicit persistent storage parent is missing.")
        require(all(str(path).casefold() != item["path"].casefold() for item in members), "binding_mismatch", "Carrier paths must be distinct.")

    def control(self):
        value = m.validate_control(read_json(self.control_path), self.identity, str(self.root))
        c.fields(value, {"format", "group_ref", "repository_binding", "instance_id", "state", "configuration_revision", "authority_epoch", "authority", "members", "operations", "origin", "retirement"})
        require(value["format"] == CONTROL and value["group_ref"] == self.identity and value["repository_binding"] == str(self.root),
                "binding_mismatch", "Control belongs to another group/project root.")
        require(value["state"] in ("active", "inactive", "retired") and value["authority"] in value["members"], "integrity_error", "Missing/conflicting authority selection.")
        paths = []
        for key, member in value["members"].items():
            m.identifier(key)
            c.fields(member, {"kind", "path", "generation", "active"})
            require(member["kind"] in ("file", "sqlite") and type(member["active"]) is bool, "integrity_error", "Invalid local member descriptor.")
            self.check_path(local_path(member["path"]), paths)
            paths.append(member)
        require(value["members"][value["authority"]]["active"], "integrity_error", "Selected authority is inactive.")
        require(value["members"].get("file", {}).get("path") == str(self.file_path), "binding_mismatch", "Configured file carrier identity changed.")
        return value

    def recover(self):
        if not self.transition_path.exists():
            return
        transition = read_json(self.transition_path)
        c.fields(transition, {"format", "before", "after", "writes"})
        require(transition["format"] == "workflow-local-group-transition/1" and transition["after"]["group_ref"] == self.identity,
                "binding_mismatch", "Transition identity differs.")
        m.validate_control(transition["after"], self.identity, str(self.root))
        current = read_json(self.control_path) if self.control_path.exists() else None
        actual = c.digest(bounded(current)) if current is not None else None
        next_digest = c.digest(bounded(transition["after"]))
        require(actual in (transition["before"], next_digest), "configuration_conflict", "Control drifted during an unfinished transition.")
        for write in transition["writes"]:
            c.fields(write, {"member", "before", "envelope"})
            require(write["member"] in transition["after"]["members"].values(), "binding_mismatch", "Transition write is outside its selected members.")
            self.check_path(local_path(write["member"]["path"]))
            m.validate(write["envelope"], self.identity)
        for write in transition["writes"]:
            member, target = write["member"], write["envelope"]
            m.validate(target, self.identity)
            # Only exact before/after bytes are eligible for deterministic recovery.
            if Path(member["path"]).exists():
                present = load_member(member)
                actual_member = envelope_digest(present)
                if actual_member == envelope_digest(target):
                    continue
                require(actual_member == write["before"], "replica_conflict", "Carrier diverged during an unfinished transition.")
                save_member(member, target, actual_member)
            else:
                require(write["before"] is None, "provider_unavailable", "An existing transition carrier is unavailable.")
                save_member(member, target, fresh=True)
        if actual != next_digest:
            atomic_json(self.control_path, transition["after"])
        self.transition_path.unlink()

    def transition(self, before, after, writes=()):
        value = {"format": "workflow-local-group-transition/1", "before": c.digest(bounded(before)) if before is not None else None,
                 "after": after, "writes": list(writes)}
        atomic_json(self.transition_path, value, fresh=True)
        self.recover()

    def envelope(self, control):
        return m.validate(load_member(control["members"][control["authority"]]), self.identity)

    def commit(self, control, before, after):
        m.seal(after)
        m.validate(after, self.identity)
        self.capacity(control, after)
        save_member(control["members"][control["authority"]], after, envelope_digest(before))

    def capacity(self, control, envelope):
        require(len(control["operations"]) <= 4096 and len(bounded(envelope)) * (len(control["members"]) + 2) + len(bounded(control)) < MAX_BYTES,
                "limit_exceeded", "Retained state lacks complete-group backup headroom; nothing was pruned.")

    def cas(self, control, envelope, request):
        require(control["state"] == "active", "store_inactive", "The group is not active.")
        require(request["expected_configuration_revision"] == control["configuration_revision"], "configuration_conflict", "Local membership/authority configuration changed.")
        require(request["expected_authority_epoch"] == control["authority_epoch"], "authority_conflict", "Selected authority epoch changed.")
        require(request["expected_revision"] == m.head(envelope), "revision_conflict", "Workflow cut changed.")

    def admin_replay(self, control, request):
        prior = control["operations"].get(request["operation_id"])
        if prior:
            require(prior["request_digest"] == m.fingerprint(request), "operation_id_conflict", "Operation ID names a different administrative request.")
            return {**prior["receipt"], "replayed": True}
        return None

    def init(self, request):
        if self.control_path.exists():
            control = self.control()
            prior = self.admin_replay(control, request)
            require(prior is not None, "already_exists", "Initialization requires fresh storage.")
            return prior
        self.check_path(self.file_path, require_parent=True)
        member = {"kind": "file", "path": str(self.file_path), "generation": "generation-" + str(uuid.uuid4()), "active": True}
        result = {"state": "applied", "operation_id": request["operation_id"], "authority": "file", "configuration_revision": 0, "authority_epoch": 1, "revision": None, "replayed": False}
        control = {"format": CONTROL, "group_ref": self.identity, "repository_binding": str(self.root), "instance_id": str(uuid.uuid4()), "state": "active",
                   "configuration_revision": 0, "authority_epoch": 1, "authority": "file", "members": {"file": member},
                   "operations": {request["operation_id"]: {"request": copy.deepcopy(request), "request_digest": m.fingerprint(request), "receipt": result}}, "origin": None, "retirement": None}
        require(not self.file_path.exists(), "already_exists", "File initialization cannot overwrite existing storage.")
        self.transition(None, control, [{"member": member, "before": None, "envelope": m.empty_envelope(self.identity)}])
        return result

    def query(self, control, envelope, request):
        operation = request["operation"]
        body = m.current(envelope)
        if operation == "group-configuration":
            return {"group_ref": self.identity, "instance_id": control["instance_id"], "state": control["state"],
                    "configuration_revision": control["configuration_revision"], "authority_epoch": control["authority_epoch"],
                    "authority": control["authority"], "members": control["members"], "revision": m.head(envelope),
                    "provider_configuration_revision": sum(event["body"]["request"]["operation"] in ("provider-register", "provider-update", "provider-enable", "provider-disable") for event in envelope["events"])}
        if operation in ("group-context", "group-resume"):
            require(body["state"] is not None, "not_found", "Workflow is absent.")
            return {"group_ref": self.identity, "revision": m.head(envelope), "authority": control["authority"], "authority_epoch": control["authority_epoch"],
                    "configuration_revision": control["configuration_revision"], "record": body["state"]}
        if operation == "group-read":
            require(body["state"] is not None and request["collection"] in ("documents", "attachments"), "not_found", "Select an existing document collection.")
            document = body["state"][request["collection"]].get(request["document"])
            require(document is not None, "not_found", "Document is absent.")
            return {"revision": m.head(envelope), "document": request["document"], **document}
        if operation == "group-operation":
            key = m.identifier(request["lookup_operation_id"])
            for event in envelope["events"]:
                if event["body"]["operation_id"] == key:
                    return m.receipt(event)
            prior = control["operations"].get(key) or envelope["aux_operations"].get(key)
            return prior["receipt"] if prior else {"state": "unknown", "operation_id": key}
        if operation == "group-sync-status":
            return {"revision": m.head(envelope), "targets": [{**row, "delivery": envelope["deliveries"].get(row["intent_id"], {"state": "pending", "attempts": 0})} for row in p.intents(envelope)]}
        providers = body["providers"]
        if operation == "provider-inspect":
            require(request["provider_id"] in providers, "not_found", "Provider is not registered.")
            providers = {request["provider_id"]: providers[request["provider_id"]]}
        return {"providers": providers, "backend_verification": "unavailable", "evidence_kind": "registration-only"}

    def append(self, control, envelope, request):
        body = m.current(envelope)
        state, providers = body["state"], body["providers"]
        operation = request["operation"]
        if operation in WORKFLOW:
            state = m.reduce_state(state, request)
        else:
            expected = sum(event["body"]["request"]["operation"] in ("provider-register", "provider-update", "provider-enable", "provider-disable") for event in envelope["events"])
            require(request["expected_provider_configuration_revision"] == expected, "configuration_conflict", "Provider configuration revision changed.")
            providers = p.revise(self.root, providers, request, self.identity["project_id"])
        targets = [{"kind": "local", "member_id": key, "generation": member["generation"], "expected_parent": m.head(envelope)}
                   for key, member in control["members"].items() if member["active"] and key != control["authority"]]
        if operation in WORKFLOW:
            targets += p.remote_targets(envelope, providers)
        event_body = {"sequence": len(envelope["events"]) + 1, "parent": m.head(envelope), "operation_id": request["operation_id"],
                      "request_digest": m.fingerprint(request), "request": copy.deepcopy(request), "state": state, "providers": providers, "targets": targets,
                      "configuration_revision": control["configuration_revision"], "authority_epoch": control["authority_epoch"]}
        event = {"cut": c.digest(c.canonical(event_body)), "body": event_body}
        envelope["events"].append(event)
        return m.receipt(event)

    def synchronize(self, control, envelope, request):
        rows = p.intents(envelope)
        row = next((item for item in rows if item["intent_id"] == request["intent_id"]), None)
        require(row and row["target"]["kind"] == "local", "not_found", "Selected local intent is absent.")
        target = row["target"]
        member = control["members"].get(target["member_id"])
        require(member and member["generation"] == target["generation"], "binding_mismatch", "Original member generation is unavailable.")
        require(target["member_id"] != control["authority"], "authority_conflict", "Replica apply cannot target selected authority.")
        prior = envelope["deliveries"].get(row["intent_id"], {})
        require(prior.get("attempts", 0) < prior.get("attempt_limit", 32), "limit_exceeded", "Synchronization dispatch bound reached; explicitly resume the original intent.")
        replica = m.validate(load_member(member), self.identity)
        require(replica["events"] == envelope["events"][:len(replica["events"])], "replica_conflict", "Replica immutable history diverged.")
        expected = target["expected_parent"]
        prefix = []
        for event in envelope["events"]:
            prefix.append(event)
            if event["cut"] == row["cut"]:
                break
        if row["cut"] is None:
            prefix = []
        already = len(replica["events"]) >= len(prefix) and replica["events"][:len(prefix)] == prefix
        if not already:
            require(m.head(replica) == expected, "replica_conflict", "Replica parent changed; no overwrite or revision bump was attempted.")
            require(replica["events"] == prefix[:len(replica["events"])], "replica_conflict", "Replica immutable history diverged.")
        if not already or len(replica["events"]) == len(prefix):
            copied = copy.deepcopy(envelope)
            copied["events"] = copy.deepcopy(prefix)
            cuts = {item["cut"] for item in prefix}
            copied["baselines"] = {key: value for key, value in copied["baselines"].items() if value["cut"] is None or value["cut"] in cuts}
            # Transport observations are transferred only for intents present at this cut.
            known = {item["intent_id"] for item in p.intents(copied)}
            copied["deliveries"] = {key: value for key, value in copied["deliveries"].items() if key in known}
            copied["handoffs"] = {key: value for key, value in copied["handoffs"].items() if value["intent_id"] in known}
            m.seal(copied)
            save_member(member, copied, envelope_digest(replica))
        envelope["deliveries"][row["intent_id"]] = {**prior, "state": "accepted", "attempts": prior.get("attempts", 0) + 1}
        return {"state": "applied", "operation_id": request["operation_id"], "intent_id": row["intent_id"], "revision": row["cut"], "replayed": False}

    def administration(self, control, envelope, request):
        operation = request["operation"]
        after = copy.deepcopy(control)
        changed = copy.deepcopy(envelope)
        writes = []
        if operation == "member-add":
            key = m.identifier(request["member_id"])
            require(key not in control["members"] and request["kind"] in ("file", "sqlite"), "already_exists", "Member ID must be fresh and carrier kind supported.")
            require(len(control["members"]) < 8, "limit_exceeded", "Local member capacity exceeded.")
            path = local_path(request["path"])
            self.check_path(path, control["members"].values(), require_parent=True)
            require(not path.exists(), "already_exists", "Only a fresh member path can be registered.")
            member = {"kind": request["kind"], "path": str(path), "generation": "generation-" + str(uuid.uuid4()), "active": True}
            after["members"][key] = member
            baseline = {"cut": m.head(envelope), "target": {"kind": "local", "member_id": key, "generation": member["generation"], "expected_parent": None}}
            changed["baselines"]["baseline-" + str(uuid.uuid4())] = baseline
            writes.append({"member": member, "before": None, "envelope": m.empty_envelope(self.identity)})
        elif operation in ("member-remove", "select-authority"):
            key = m.identifier(request["member_id"])
            member = control["members"].get(key)
            require(member and member["generation"] == request["expected_generation"] and member["active"], "configuration_conflict", "Member generation changed or is inactive.")
            require(key != control["authority"], "authority_conflict", "Select another authority before changing this member.")
            if operation == "member-remove":
                after["members"][key]["active"] = False
            else:
                replica = m.validate(load_member(member), self.identity)
                require(replica["events"] == envelope["events"] and replica["baselines"] == envelope["baselines"], "source_cut_conflict", "Authority transfer requires the complete current cut and operation closure.")
                # Every local target through this cut must have been acknowledged first.
                require(all(envelope["deliveries"].get(row["intent_id"], {}).get("state") == "accepted" for row in p.intents(envelope) if row["target"]["kind"] == "local"),
                        "predecessor_pending", "Pending local deliveries prevent authority transfer.")
                after["authority"] = key
                after["authority_epoch"] += 1
                writes.append({"member": member, "before": envelope_digest(replica), "envelope": changed})
        elif operation == "group-deactivate":
            from .group_backup import snapshot
            _, digest = snapshot(self, control, envelope)
            require(request["snapshot_digest"] == digest, "revision_conflict", "Complete-group export is stale.")
            after["state"] = "retired"
            after["retirement"] = {"seal": str(uuid.uuid4()), "snapshot_digest": digest, "successor_instance_id": None}
        else:
            from .group_backup import activate
            return activate(self, control, envelope, request)
        after["configuration_revision"] += 1
        result = {"state": "applied", "operation_id": request["operation_id"], "configuration_revision": after["configuration_revision"],
                  "authority_epoch": after["authority_epoch"], "authority": after["authority"], "revision": m.head(envelope), "replayed": False}
        if after["retirement"] is not None:
            result["retirement_seal"] = after["retirement"]["seal"]
        after["operations"][request["operation_id"]] = {"request": copy.deepcopy(request), "request_digest": m.fingerprint(request), "receipt": result}
        if changed != envelope:
            m.seal(changed)
            writes.append({"member": control["members"][control["authority"]], "before": envelope_digest(envelope), "envelope": changed})
        # Switch copies current auxiliary recovery state as well as the proven immutable cut.
        for write in writes:
            m.seal(write["envelope"])
        self.capacity(after, changed)
        self.transition(control, after, writes)
        return result

    def execute(self, request):
        operation = request.get("operation") if isinstance(request, dict) else None
        version = request.get("contract_version") if isinstance(request, dict) else m.PROFILE
        try:
            require(isinstance(request, dict) and operation in EXTRAS, "unsupported_capability", "Unknown local-group operation.")
            require(version == (m.PROVIDERS if operation.startswith("provider-") else m.PROFILE), "unsupported_version", "Select the operation's exact versioned contract.")
            required = {"contract_version", "group_ref", "operation"} | EXTRAS[operation]
            mutation = operation not in READS | {"group-export", "group-preflight"}
            if mutation:
                required |= {"operation_id"}
                m.identifier(request.get("operation_id"))
            if mutation and operation not in ("group-init", "group-restore"):
                required |= {"expected_configuration_revision", "expected_authority_epoch", "expected_revision"}
            if operation in ("provider-register", "provider-update", "provider-enable", "provider-disable"):
                required |= {"expected_provider_configuration_revision"}
            c.fields(request, required, {"max_output_bytes"})
            if "expected_configuration_revision" in required:
                c.integer(request["expected_configuration_revision"])
                c.integer(request["expected_authority_epoch"], 1)
                require(request["expected_revision"] is None or isinstance(request["expected_revision"], str), "invalid_input", "Expected revision must be a cut or null.")
            if "expected_provider_configuration_revision" in required:
                c.integer(request["expected_provider_configuration_revision"])
            require(request["group_ref"] == self.identity, "binding_mismatch", "Request group identity differs from selected configuration.")
            require(len(c.canonical(request)) <= c.MAX_INPUT, "limit_exceeded", "Request exceeds 2 MiB.")
            maximum = c.integer(request.get("max_output_bytes", c.MAX_INPUT), 2048, c.MAX_INPUT)
            with group_lock(self.directory):
                self.recover()
                if operation == "group-init":
                    result = self.init(request)
                elif operation in ("group-preflight", "group-restore"):
                    from .group_backup import preflight, restore
                    archive = preflight(request["archive"], request["archive_digest"], self.identity)
                    result = {"state": "valid", "snapshot_digest": archive["snapshot_digest"]} if operation == "group-preflight" else restore(self, archive, request)
                else:
                    control = self.control()
                    envelope = self.envelope(control)
                    if operation in READS:
                        result = self.query(control, envelope, request)
                    elif operation == "group-export":
                        from .group_backup import export
                        result = export(self, control, envelope, request)
                    else:
                        prior = self.admin_replay(control, request) or m.replay(envelope, request)
                        if prior is not None:
                            result = prior
                        else:
                            if operation != "group-activate":
                                self.cas(control, envelope, request)
                            else:
                                require(control["state"] == "inactive", "store_inactive", "Activation requires an inactive restored group.")
                                require(request["expected_configuration_revision"] == control["configuration_revision"] and request["expected_authority_epoch"] == control["authority_epoch"] and request["expected_revision"] == m.head(envelope), "configuration_conflict", "Restored group changed before activation.")
                            if operation in ADMIN:
                                result = self.administration(control, envelope, request)
                            else:
                                updated = copy.deepcopy(envelope)
                                if operation in WORKFLOW or operation in ("provider-register", "provider-update", "provider-enable", "provider-disable"):
                                    result = self.append(control, updated, request)
                                else:
                                    if operation == "group-resume-intent":
                                        require(any(item["intent_id"] == request["intent_id"] for item in p.intents(updated)), "not_found", "Original intent is absent.")
                                        additional = c.integer(request["additional_attempts"], 1, 32)
                                        prior_delivery = updated["deliveries"].get(request["intent_id"], {"state": "pending", "attempts": 0})
                                        limit = prior_delivery.get("attempt_limit", 32) + additional
                                        require(limit <= 1024, "limit_exceeded", "Retained intent dispatch budget cannot exceed 1024.")
                                        observation_limit = prior_delivery.get("observation_limit", 64) + additional * 2
                                        require(observation_limit <= 4096, "limit_exceeded", "Retained observation budget cannot exceed 4096.")
                                        updated["deliveries"][request["intent_id"]] = {**prior_delivery, "attempt_limit": limit, "observation_limit": observation_limit, "dispatch_authorized": True}
                                        result = {"state": "resumed", "operation_id": request["operation_id"], "intent_id": request["intent_id"], "attempt_limit": limit, "replayed": False}
                                    elif operation == "group-sync":
                                        try:
                                            result = self.synchronize(control, updated, request)
                                        except (RecordError, OSError) as exc:
                                            row = next((item for item in p.intents(updated) if item["intent_id"] == request["intent_id"]), None)
                                            if row is None or row["target"]["kind"] != "local":
                                                raise
                                            previous = updated["deliveries"].get(row["intent_id"], {})
                                            code = getattr(exc, "code", "storage_error")
                                            outcome = "conflict" if code in ("replica_conflict", "binding_mismatch", "integrity_error") else "unknown"
                                            updated["deliveries"][row["intent_id"]] = {**previous, "state": previous.get("state") if previous.get("state") == "accepted" else outcome,
                                                                                   "attempts": min(previous.get("attempts", 0) + (code != "limit_exceeded"), previous.get("attempt_limit", 32)), "last_error": code}
                                            result = {"state": outcome, "operation_id": request["operation_id"], "intent_id": row["intent_id"], "error": {"code": code}, "replayed": False}
                                    elif operation == "provider-prepare":
                                        result = p.prepare(updated, self.identity, request)
                                    else:
                                        result = p.observe(updated, request)
                                    m.save_aux(updated, request, result)
                                self.commit(control, envelope, updated)
                response = {"contract_version": version, "operation": operation, "status": "ok", "local_result": "accepted", "result": result,
                            "limitations": ["cooperating local APIs only", "host observations are assertions, not backend attestation", "physical power-loss durability is unverified"]}
                require(len(c.canonical(response)) <= maximum, "limit_exceeded", "Whole response exceeds the output budget; reconcile the original operation ID.")
                return response
        except RecordError as exc:
            return {"contract_version": version, "operation": operation, "status": "error", "local_result": "unknown" if exc.code in ("storage_error", "io_error", "limit_exceeded") else "not_applied", "error": {"code": exc.code, "message": exc.message}}
        except (OSError, ValueError, KeyError, TypeError, RecursionError):
            return {"contract_version": version, "operation": operation, "status": "error", "local_result": "unknown", "error": {"code": "storage_error", "message": "Storage operation failed; reconcile the original operation ID."}}
