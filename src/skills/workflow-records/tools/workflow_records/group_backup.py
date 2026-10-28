"""Complete group transfer, inactive restore and single-successor activation."""
from __future__ import annotations

import copy
from pathlib import Path
import uuid

from . import source_contract as c
from .contracts import require
from . import group_model as m
from .group_storage import atomic_json, bounded, group_lock, load_member, local_path, read_json

FORMAT = "workflow-local-group-backup/1"


def validate_group(control, members, identity):
    from .group_providers import intents
    m.validate_control(control, identity)
    require(set(control["members"]) == set(members), "integrity_error", "Backup member closure differs.")
    source_events = members[control["authority"]]["events"]
    for envelope in members.values():
        m.validate(envelope, identity)
        require(envelope["events"] == source_events[:len(envelope["events"])], "integrity_error", "Backup contains a divergent local member.")
        used = set(envelope["aux_operations"]) | {event["body"]["operation_id"] for event in envelope["events"]}
        require(not used.intersection(control["operations"]), "integrity_error", "Operation identity crosses administrative/data scopes.")
        for event in envelope["events"]:
            require(event["body"]["configuration_revision"] <= control["configuration_revision"] and event["body"]["authority_epoch"] <= control["authority_epoch"],
                    "integrity_error", "Event configuration/authority exceeds retained control.")
        for row in intents(envelope):
            target = row["target"]
            if target["kind"] == "local":
                require(target["member_id"] in control["members"] and control["members"][target["member_id"]]["generation"] == target["generation"],
                        "integrity_error", "Fixed local target generation is absent from control.")
    return members


def snapshot(group, control, envelope):
    m.validate_control(control, group.identity, str(group.root))
    members = {}
    for key, member in control["members"].items():
        members[key] = m.validate(load_member(member), group.identity)
    require(members[control["authority"]] == envelope, "revision_conflict", "Authority changed during export.")
    validate_group(control, members, group.identity)
    payload = {"control_directory": str(group.directory), "control": control, "members": members}
    return payload, c.digest(bounded(payload))


def export(group, control, envelope, request):
    payload, digest = snapshot(group, control, envelope)
    archive = {"format": FORMAT, "snapshot_digest": digest, "payload": payload}
    destination = local_path(request["destination"])
    require(not destination.exists() and not destination.is_relative_to(group.directory) and
            all(str(destination).casefold() != member["path"].casefold() for member in control["members"].values()),
            "unsafe_path", "Export requires a fresh path outside live storage.")
    atomic_json(destination, archive, fresh=True)
    return {"state": "exported", "snapshot_digest": digest, "archive_digest": c.digest(bounded(archive)), "destination": str(destination)}


def preflight(path, digest, identity):
    archive = read_json(local_path(path))
    c.fields(archive, {"format", "snapshot_digest", "payload"})
    require(archive["format"] == FORMAT and c.digest(bounded(archive)) == digest, "integrity_error", "Backup format/digest differs.")
    payload = archive["payload"]
    c.fields(payload, {"control_directory", "control", "members"})
    require(c.digest(bounded(payload)) == archive["snapshot_digest"], "integrity_error", "Complete backup payload hash differs.")
    control = m.validate_control(payload["control"], identity)
    require(control["group_ref"] == identity and control["authority"] in control["members"] and
            set(control["members"]) == set(payload["members"]), "binding_mismatch", "Backup group/member closure differs.")
    validate_group(control, payload["members"], identity)
    return archive


def restore(group, archive, request):
    if group.control_path.exists():
        prior = group.admin_replay(group.control(), request)
        require(prior is not None, "already_exists", "Restore cannot replace a group.")
        return prior
    payload = archive["payload"]
    previous = payload["control"]
    require(set(request["member_paths"]) == set(previous["members"]), "invalid_input", "Restore must explicitly relocate every retained member.")
    after = copy.deepcopy(previous)
    after["instance_id"] = str(uuid.uuid4())
    after["repository_binding"] = str(group.root)
    after["state"] = "inactive"
    after["origin"] = {"instance_id": previous["instance_id"], "snapshot_digest": archive["snapshot_digest"], "control_directory": payload["control_directory"]}
    after["retirement"] = None
    writes, paths = [], []
    for key, member in after["members"].items():
        path = local_path(request["member_paths"][key])
        group.check_path(path, paths, require_parent=True)
        require(not path.exists(), "already_exists", "Restore requires fresh member paths.")
        member["path"] = str(path)
        paths.append(member)
        writes.append({"member": member, "before": None, "envelope": payload["members"][key]})
    require(after["members"]["file"]["path"] == str(group.file_path), "binding_mismatch", "Restored file member differs from the selected locator.")
    result = {"state": "applied", "operation_id": request["operation_id"], "store_state": "inactive", "instance_id": after["instance_id"],
              "snapshot_digest": archive["snapshot_digest"], "replayed": False}
    require(request["operation_id"] not in after["operations"] and m.replay(payload["members"][previous["authority"]], request) is None,
            "operation_id_conflict", "Restore operation identity was already used.")
    after["operations"][request["operation_id"]] = {"request": copy.deepcopy(request), "request_digest": m.fingerprint(request), "receipt": result}
    m.validate_control(after, group.identity, str(group.root))
    group.transition(None, after, writes)
    return result


def activate(group, control, envelope, request):
    from .group_service import LocalGroup, CONFIG
    origin = control["origin"]
    require(origin is not None, "binding_mismatch", "Restored origin is missing.")
    directory = local_path(request["original_control_directory"])
    require(str(directory) == origin["control_directory"] and directory != group.directory,
            "binding_mismatch", "Activation requires the original group control directory.")
    old_value = read_json(directory / "control.json")
    config = {"contract_version": CONFIG, "group_ref": group.identity, "control_directory": str(directory), "file_path": old_value["members"]["file"]["path"]}
    original = LocalGroup(old_value["repository_binding"], config)
    with group_lock(directory):
        original.recover()
        retired = original.control()
        retirement = retired["retirement"]
        require(retired["state"] == "retired" and retired["instance_id"] == origin["instance_id"] and retirement is not None and
                retirement["snapshot_digest"] == origin["snapshot_digest"] and retirement["seal"] == request["retirement_seal"],
                "binding_mismatch", "Original retirement proof differs from this restored snapshot.")
        require(retirement["successor_instance_id"] in (None, control["instance_id"]), "successor_conflict", "Another restored instance already claimed activation.")
        claimed = copy.deepcopy(retired)
        claimed["retirement"]["successor_instance_id"] = control["instance_id"]
        # Claim first. A crash leaves only this same instance eligible to retry activation.
        atomic_json(original.control_path, claimed)
        after = copy.deepcopy(control)
        after["state"] = "active"
        after["configuration_revision"] += 1
        after["authority_epoch"] += 1
        result = {"state": "applied", "operation_id": request["operation_id"], "store_state": "active", "instance_id": after["instance_id"], "replayed": False}
        after["operations"][request["operation_id"]] = {"request": copy.deepcopy(request), "request_digest": m.fingerprint(request), "receipt": result}
        group.transition(control, after)
        return result
