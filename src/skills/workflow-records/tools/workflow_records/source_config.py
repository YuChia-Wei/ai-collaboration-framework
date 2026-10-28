"""Workflow-scoped schema-3 configuration; SQLite remains the command owner."""
from __future__ import annotations

import copy
import hashlib
import sqlite3

from . import source_contract as c
from .contracts import RecordError, StoreRef, encoded, require
from .sqlite_store import SQLiteStore, request_digest

DDL = (
    "CREATE TABLE source_configurations (workflow_id TEXT NOT NULL, revision INTEGER NOT NULL, value BLOB NOT NULL, PRIMARY KEY(workflow_id,revision))",
    "CREATE TABLE source_snapshot_configurations (snapshot_id TEXT PRIMARY KEY REFERENCES source_snapshots(id), workflow_id TEXT NOT NULL, configuration_revision INTEGER NOT NULL)",
    "CREATE TABLE source_read_proofs (id TEXT PRIMARY KEY, value BLOB NOT NULL)",
    "CREATE TABLE source_read_evidence (proof_id TEXT NOT NULL REFERENCES source_read_proofs(id), step_index INTEGER NOT NULL, value BLOB NOT NULL, PRIMARY KEY(proof_id,step_index))",
)
TABLES = {"source_configurations": (3, (2,)), "source_snapshot_configurations": (3, ()),
          "source_read_proofs": (2, (1,)), "source_read_evidence": (3, (2,))}


def current(connection, workflow_id):
    c.native_id(workflow_id)
    require(connection.execute("SELECT 1 FROM workflows WHERE id=?", (workflow_id,)).fetchone(), "not_found", "Native workflow is absent.")
    row = connection.execute("SELECT value FROM source_configurations WHERE workflow_id=? ORDER BY revision DESC LIMIT 1", (workflow_id,)).fetchone()
    return c.parse(bytes(row[0])) if row else {"workflow_id": workflow_id, "configuration_revision": 0,
                                             "bindings": {}, "read_source": {"kind": "sqlite"}}


def latest(connection, workflow_id):
    row = connection.execute("SELECT id FROM source_snapshots WHERE kind='native-workflow' AND workflow_id=? ORDER BY sequence DESC LIMIT 1", (workflow_id,)).fetchone()
    require(row, "not_found", "Native source snapshot is absent.")
    return row[0]


def capture_membership(connection, snapshot_id, kind, workflow_id):
    if kind != "native-workflow":
        return
    from .source_store import enqueue
    config = current(connection, workflow_id)
    connection.execute("INSERT INTO source_snapshot_configurations VALUES(?,?,?)", (snapshot_id, workflow_id, config["configuration_revision"]))
    for binding in config["bindings"].values():
        enqueue(connection, snapshot_id, binding["generation_id"], binding["target"])


def baseline(connection, workflow_id, binding):
    from .source_store import enqueue
    for (key,) in connection.execute("SELECT id FROM source_snapshots WHERE kind='native-workflow' AND workflow_id=? ORDER BY sequence", (workflow_id,)).fetchall():
        enqueue(connection, key, binding["generation_id"], binding["target"])


def add_generation(connection, workflow_id, request, revision):
    binding = request["binding"]
    c.fields(binding, {"binding_id", "project_ref", "source_id"})
    logical_id = binding["binding_id"]
    c.native_id(logical_id)
    require(request["new_source_namespace"] is True, "invalid_input", "A fresh remote namespace at head zero must be explicitly selected.")
    generation = "generation-" + hashlib.sha256((workflow_id + "\0" + logical_id + "\0" + str(revision)).encode()).hexdigest()
    target = {**binding, "binding_id": generation, "binding_revision": revision}
    c.binding(target)
    target_key = c.digest(c.canonical({"project_ref": target["project_ref"], "source_id": target["source_id"]}))
    require(connection.execute("SELECT 1 FROM source_bindings WHERE target_key=?", (target_key,)).fetchone() is None,
            "already_exists", "Used namespaces cannot be adopted, reset or reused by another generation.")
    connection.execute("INSERT INTO source_bindings VALUES(?,?,?)", (generation, target_key, c.canonical(target)))
    return logical_id, {"generation_id": generation, "target": target}


def mutate(connection, request):
    from .source_store import receipt
    config = current(connection, request["workflow_id"])
    require(c.integer(request["expected_configuration_revision"]) == config["configuration_revision"],
            "configuration_conflict", "Workflow configuration changed; retain the original request.")
    value = copy.deepcopy(config)
    value.setdefault("selection_proof_id", None)
    revision = config["configuration_revision"] + 1
    operation = request["operation"]
    if operation in ("replica-add", "replica-update"):
        logical_id = request["binding"]["binding_id"] if isinstance(request["binding"], dict) else None
        c.native_id(logical_id)
        exists = logical_id in config["bindings"]
        require(exists == (operation == "replica-update"), "not_found" if operation == "replica-update" else "already_exists", "Binding must exist for update and be absent for add.")
        if exists:
            require(request["expected_binding_generation"] == config["bindings"][logical_id]["generation_id"], "configuration_conflict", "Binding generation changed.")
            require(config["read_source"] != {"kind": "replica", "binding_id": logical_id,
                                             "generation_id": config["bindings"][logical_id]["generation_id"]},
                    "read_source_in_use", "Select another read source before replacing its binding.")
        logical_id, binding = add_generation(connection, request["workflow_id"], request, revision)
        value["bindings"][logical_id] = binding
        require(len(value["bindings"]) <= 100, "limit_exceeded", "Workflow has too many selected carriers.")
        baseline(connection, request["workflow_id"], binding)
    elif operation == "replica-remove":
        logical_id = request["binding_id"]
        c.native_id(logical_id)
        require(logical_id in config["bindings"], "not_found", "Binding is absent.")
        require(request["expected_binding_generation"] == config["bindings"][logical_id]["generation_id"], "configuration_conflict", "Binding generation changed.")
        require(config["read_source"].get("binding_id") != logical_id, "read_source_in_use", "Select another source before removing its binding.")
        del value["bindings"][logical_id]
    else:
        selected = request["read_source"]
        require(isinstance(selected, dict), "invalid_input", "Select a complete read source.")
        if selected.get("kind") == "sqlite":
            c.fields(selected, {"kind"})
            require("proof_id" not in request, "invalid_input", "SQLite selection has no remote proof.")
            value["selection_proof_id"] = None
        else:
            c.fields(selected, {"kind", "binding_id", "generation_id"})
            require(selected["kind"] == "replica" and selected["binding_id"] in config["bindings"], "invalid_input", "Select an active binding.")
            require(selected["generation_id"] == config["bindings"][selected["binding_id"]]["generation_id"], "configuration_conflict", "Selected generation changed.")
            from .source_proof import proven
            proof = proven(connection, request.get("proof_id"))
            require(proof["purpose"] == "selection" and proof["workflow_id"] == request["workflow_id"]
                    and proof["configuration_revision"] == config["configuration_revision"]
                    and proof["binding_id"] == selected["binding_id"] and proof["generation_id"] == selected["generation_id"]
                    and proof["snapshot_id"] == latest(connection, request["workflow_id"]),
                    "source_cut_conflict", "Selection requires a complete proof of this workflow's current local cut and binding.")
            value["selection_proof_id"] = proof["proof_id"]
        value["read_source"] = copy.deepcopy(selected)
    value.update(configuration_revision=revision, operation_id=request["operation_id"],
                 source_cut=latest(connection, request["workflow_id"]), request=copy.deepcopy(request))
    connection.execute("INSERT INTO source_configurations VALUES(?,?,?)", (request["workflow_id"], revision, c.canonical(value)))
    return receipt(connection, request, {"workflow_id": request["workflow_id"], "configuration_revision": revision, "configuration": value})


def validate_backup(connection, decoded):
    """Derive exact intent closure from configuration history, including baselines."""
    from .source_store import snapshot
    workflows = {row[0] for row in decoded["workflows"]}
    snapshots = {row[1]: row for row in decoded["source_snapshots"]}
    histories, generations, expected = {}, set(), set()
    source_receipts = {row[0]: c.parse(bytes(row[2])) for row in decoded["source_operations"]}
    source_digests = {row[0]: row[1] for row in decoded["source_operations"]}
    for workflow_id, revision, raw in sorted(decoded["source_configurations"]):
        c.integer(revision, 1)
        require(workflow_id in workflows, "malformed_record", "Configuration workflow is absent.")
        config = c.parse(bytes(raw))
        c.fields(config, {"workflow_id", "configuration_revision", "bindings", "read_source", "operation_id", "source_cut", "selection_proof_id", "request"})
        history = histories.setdefault(workflow_id, [])
        prior = history[-1] if history else {"configuration_revision": 0, "bindings": {}, "read_source": {"kind": "sqlite"}}
        require(config["workflow_id"] == workflow_id and config["configuration_revision"] == revision == prior["configuration_revision"] + 1
                and isinstance(config["bindings"], dict) and len(config["bindings"]) <= 100,
                "malformed_record", "Configuration revisions are incomplete or inconsistent.")
        cut = snapshots.get(config["source_cut"])
        require(cut and cut[2] == "native-workflow" and cut[3] == workflow_id,
                "malformed_record", "Configuration source cut belongs to another workflow.")
        require(not history or cut[0] >= snapshots[prior["source_cut"]][0], "malformed_record", "Configuration source cut moved backwards.")
        accepted = source_receipts.get(config["operation_id"])
        require(isinstance(accepted, dict) and accepted.get("configuration") == config and accepted.get("configuration_revision") == revision
                and accepted.get("workflow_id") == workflow_id, "malformed_record", "Configuration lacks its accepted source receipt.")
        original = config["request"]
        require(isinstance(original, dict) and original.get("contract_version") == c.PROFILE2
                and original.get("workflow_id") == workflow_id and original.get("operation_id") == config["operation_id"]
                and original.get("expected_configuration_revision") == revision - 1
                and request_digest(original) == source_digests[config["operation_id"]],
                "malformed_record", "Configuration request lost its original identity, expected revision or digest.")
        operation = original.get("operation")
        require(operation in ("replica-add", "replica-update", "replica-remove", "select-read-source"),
                "malformed_record", "Configuration request is not a configuration mutation.")
        changed = {key for key in set(prior["bindings"]) | set(config["bindings"])
                   if prior["bindings"].get(key) != config["bindings"].get(key)}
        if operation in ("replica-add", "replica-update"):
            logical_id = original["binding"]["binding_id"]
            require(changed == {logical_id} and logical_id in config["bindings"]
                    and (logical_id in prior["bindings"]) == (operation == "replica-update")
                    and config["read_source"] == prior["read_source"] and original["new_source_namespace"] is True,
                    "malformed_record", "Carrier generation changed outside its original command.")
            if operation == "replica-update":
                require(original["expected_binding_generation"] == prior["bindings"][logical_id]["generation_id"]
                        and prior["read_source"].get("binding_id") != logical_id,
                        "malformed_record", "Update replaced a selected or unexpected generation.")
            target = config["bindings"][logical_id]["target"]
            require(original["binding"] == {"binding_id": logical_id, "project_ref": target["project_ref"], "source_id": target["source_id"]},
                    "malformed_record", "Carrier target differs from the original command.")
        elif operation == "replica-remove":
            logical_id = original["binding_id"]
            require(changed == {logical_id} and logical_id in prior["bindings"] and logical_id not in config["bindings"]
                    and original["expected_binding_generation"] == prior["bindings"][logical_id]["generation_id"]
                    and config["read_source"] == prior["read_source"] and prior["read_source"].get("binding_id") != logical_id,
                    "malformed_record", "Carrier removal differs from its original command.")
        else:
            require(not changed and original["read_source"] == config["read_source"],
                    "malformed_record", "Read selection changed carrier membership or its original selector.")
        added = set()
        for logical_id, binding in config["bindings"].items():
            c.native_id(logical_id)
            c.fields(binding, {"generation_id", "target"})
            target = binding["target"]
            c.binding(target)
            generation = binding["generation_id"]
            require(target["binding_id"] == generation, "malformed_record", "Binding generation differs from its immutable target.")
            stored = connection.execute("SELECT value FROM source_bindings WHERE id=?", (generation,)).fetchone()
            require(stored and c.parse(bytes(stored[0])) == target, "malformed_record", "Configuration target differs from retained binding.")
            if logical_id not in prior["bindings"] or prior["bindings"][logical_id] != binding:
                expected_generation = "generation-" + hashlib.sha256((workflow_id + "\0" + logical_id + "\0" + str(revision)).encode()).hexdigest()
                require(generation == expected_generation and target["binding_revision"] == revision and generation not in generations,
                        "malformed_record", "Binding generation was reused or rewritten.")
                generations.add(generation)
                added.add(generation)
                for key, selected in snapshots.items():
                    if selected[2] == "native-workflow" and selected[3] == workflow_id and selected[0] <= cut[0]:
                        expected.add((key, generation))
        selected = config["read_source"]
        require(isinstance(selected, dict), "malformed_record", "Invalid read selector.")
        if selected.get("kind") == "sqlite":
            c.fields(selected, {"kind"})
            require(config["selection_proof_id"] is None, "malformed_record", "Local selection contains a remote proof.")
        else:
            c.fields(selected, {"kind", "binding_id", "generation_id"})
            require(selected["kind"] == "replica" and selected["binding_id"] in config["bindings"]
                    and selected["generation_id"] == config["bindings"][selected["binding_id"]]["generation_id"],
                    "malformed_record", "Read selector does not name an active immutable generation.")
            if operation == "select-read-source":
                from .source_proof import load, plan
                proof = load(connection, config["selection_proof_id"], check_configuration=False)
                require(proof["purpose"] == "selection" and proof["workflow_id"] == workflow_id
                        and proof["configuration_revision"] == revision - 1 and proof["generation_id"] == selected["generation_id"]
                        and proof["binding_id"] == selected["binding_id"] and proof["snapshot_id"] == config["source_cut"]
                        and connection.execute("SELECT count(*) FROM source_read_evidence WHERE proof_id=?", (proof["proof_id"],)).fetchone()[0] == len(plan(connection, proof)),
                        "malformed_record", "Selected source lacks a complete proof of its configuration cut.")
                require(original.get("proof_id") == proof["proof_id"], "malformed_record", "Selection proof differs from its original command.")
            else:
                require(config["selection_proof_id"] == prior["selection_proof_id"], "malformed_record", "Unchanged selection rewrote its proof.")
        require(len(added) <= 1, "malformed_record", "A configuration introduced multiple generations.")
        history.append(config)
    require(generations == {row[0] for row in decoded["source_bindings"]}, "malformed_record", "Orphan binding generation.")
    native_keys = {key for key, row in snapshots.items() if row[2] == "native-workflow"}
    require({row[0] for row in decoded["source_snapshot_configurations"]} == native_keys,
            "malformed_record", "Native snapshot configuration closure is incomplete.")
    for key, workflow_id, revision in decoded["source_snapshot_configurations"]:
        c.integer(revision)
        selected = snapshots[key]
        require(selected[3] == workflow_id, "malformed_record", "Snapshot configuration scope changed.")
        eligible = [config for config in histories.get(workflow_id, []) if snapshots[config["source_cut"]][0] < selected[0]]
        config = eligible[-1] if eligible else {"configuration_revision": 0, "bindings": {}}
        require(revision == config["configuration_revision"], "malformed_record", "Snapshot was captured under a different configuration.")
        expected.update((key, binding["generation_id"]) for binding in config["bindings"].values())
    require(expected == {(row[2], row[3]) for row in decoded["replica_intents"]},
            "malformed_record", "Historical configuration target membership is incomplete or contains extra deliveries.")
    from . import source_proof
    for proof_id, raw in decoded["source_read_proofs"]:
        proof = c.parse(bytes(raw))
        c.fields(proof, {"proof_id", "workflow_id", "configuration_revision", "purpose", "binding_id", "generation_id", "target", "snapshot_id", "source_revision", "manifest_hash", "authority_cut"})
        c.native_id(proof_id)
        require(proof["proof_id"] == proof_id and proof["workflow_id"] in workflows, "malformed_record", "Read proof identity changed.")
        revision = c.integer(proof["configuration_revision"])
        history = histories.get(proof["workflow_id"], [])
        require(revision <= len(history), "malformed_record", "Read proof configuration is absent.")
        config = history[revision - 1] if revision else {"bindings": {}, "read_source": {"kind": "sqlite"}}
        row, manifest = snapshot(connection, proof["snapshot_id"])
        cut = snapshots.get(proof["authority_cut"])
        require(row[2] == "native-workflow" and row[3] == proof["workflow_id"] and cut and cut[3] == proof["workflow_id"]
                and row[0] <= cut[0] and proof["source_revision"] == row[4] and proof["manifest_hash"] == c.digest(c.canonical(manifest))
                and proof["purpose"] in ("read", "selection"), "malformed_record", "Read proof source cut or version changed.")
        if proof["target"] is None:
            require(proof["purpose"] == "read" and proof["binding_id"] is None and proof["generation_id"] is None
                    and config["read_source"] == {"kind": "sqlite"} and proof["snapshot_id"] == proof["authority_cut"],
                    "malformed_record", "Local read proof selected another source.")
        else:
            binding = config["bindings"].get(proof["binding_id"])
            require(binding and binding == {"generation_id": proof["generation_id"], "target": proof["target"]},
                    "malformed_record", "Read proof target changed.")
            require(proof["purpose"] == "selection" and proof["snapshot_id"] == proof["authority_cut"]
                    or proof["purpose"] == "read" and config["read_source"] == {"kind": "replica", "binding_id": proof["binding_id"], "generation_id": proof["generation_id"]},
                    "malformed_record", "Read proof does not follow its selected source.")
        provider_revision = None
        for expected_index, (index, native_raw) in enumerate(connection.execute("SELECT step_index,value FROM source_read_evidence WHERE proof_id=? ORDER BY step_index", (proof_id,))):
            require(index == expected_index, "malformed_record", "Read evidence steps are incomplete.")
            provider_revision = source_proof.verify_evidence(connection, proof, index, c.parse(bytes(native_raw)), provider_revision)


def execute(owner, request):
    from .source_store import replay, receipt, SourceStore
    operation = request.get("operation")
    try:
        common = {"contract_version", "operation", "store_ref"}
        changes = {"operation_id", "workflow_id", "expected_configuration_revision"}
        inputs = {"source-init": {"operation_id", "schema_version"}, "source-operation": {"operation_id"},
                  "source-configuration": {"workflow_id"}, "replica-add": changes | {"binding", "new_source_namespace"},
                  "replica-update": changes | {"binding", "new_source_namespace", "expected_binding_generation"},
                  "replica-remove": changes | {"binding_id", "expected_binding_generation"},
                  "select-read-source": changes | {"read_source"},
                  "read-prepare": {"operation_id", "workflow_id", "expected_configuration_revision"},
                  "read-accept": {"operation_id", "proof_id", "step_index", "mcp_result"},
                  "read-result": {"proof_id"}, "read-chunk": {"proof_id", "path", "index"}}
        require(isinstance(operation, str) and operation in inputs, "unsupported_capability", "Unknown /2 source operation.")
        optional = {"max_output_bytes"} | ({"proof_id"} if operation == "select-read-source" else
                   {"binding_id"} if operation == "read-prepare" else set())
        c.fields(request, common | inputs[operation], optional)
        require(len(c.canonical(request)) <= c.MAX_INPUT, "limit_exceeded", "Source request exceeds whole-object bound.")
        maximum = c.integer(request.get("max_output_bytes", 1048576), 2048, c.MAX_INPUT)
        store = owner.service.provider(StoreRef.parse(request["store_ref"]))
        require(isinstance(store, SQLiteStore), "unsupported_capability", "The command authority must be SQLite.")
        if operation == "source-init":
            require(request["schema_version"] == c.SCHEMA3, "invalid_input", "/2 initializes an explicit fresh schema 3.")
            if store.database.exists():
                with store.transaction() as (_, meta):
                    require(meta["schema_version"] == c.SCHEMA3, "explicit_upgrade_required", "Existing schemas are never upgraded implicitly.")
            result = store.initialize(request, schema=c.SCHEMA3)
        else:
            write = operation in ("replica-add", "replica-update", "replica-remove", "select-read-source", "read-prepare", "read-accept")
            with store.transaction(write=write) as (connection, meta):
                require(meta["schema_version"] == c.SCHEMA3, "explicit_upgrade_required", "Workflow /2 configuration requires fresh schema 3; existing store remains unchanged.")
                prior = replay(connection, request) if write else None
                if prior is not None:
                    result = prior
                else:
                    if write:
                        require(meta["state"] == "active", "store_inactive", "Inactive stores cannot accept configuration or transport observations.")
                    if operation == "source-configuration":
                        result = current(connection, request["workflow_id"])
                    elif operation in ("replica-add", "replica-update", "replica-remove", "select-read-source"):
                        result = mutate(connection, request)
                    elif operation == "source-operation":
                        row = connection.execute("SELECT receipt FROM source_operations WHERE id=?", (request["operation_id"],)).fetchone()
                        result = c.parse(bytes(row[0])) if row else {"state": "unknown", "operation_id": request["operation_id"]}
                    else:
                        from . import source_proof
                        if operation == "read-prepare":
                            result = receipt(connection, request, source_proof.prepare(connection, request))
                        elif operation == "read-accept":
                            result = receipt(connection, request, source_proof.accept(connection, request))
                        else:
                            result = source_proof.result(connection, request)
        response = {"contract_version": c.PROFILE2, "operation": operation, "status": "ok", "local_result": "accepted", "result": result,
                    "limitations": ["SQLite is the sole command authority", "transport is explicit; replica proof is host-correlated, not identity attestation"]}
        require(len(encoded(response)) <= maximum, "limit_exceeded", "Whole response exceeds budget; reconcile the original operation receipt.")
        return response
    except RecordError as exc:
        return {"contract_version": c.PROFILE2, "operation": operation, "status": "error", "local_result": "unknown" if exc.code in ("io_error", "storage_error", "limit_exceeded") else "not_applied", "error": {"code": exc.code, "message": exc.message}}
    except (OSError, sqlite3.Error, ValueError, KeyError, TypeError, RecursionError, ImportError):
        return {"contract_version": c.PROFILE2, "operation": operation, "status": "error", "local_result": "unknown", "error": {"code": "storage_error", "message": "Source operation unavailable; reconcile its original receipt."}}
