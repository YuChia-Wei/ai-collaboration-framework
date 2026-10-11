"""Bounded complete logical backups; input data is never executed as SQL or paths."""
from __future__ import annotations

import base64
import json
import os
import sqlite3
import uuid

from .contracts import (MAX_FILE, RecordError, decode_json, digest, encoded,
                        identifier, require, timestamp, unique_object, validate_unicode)
from .common import relative_path, validate_checkpoint
from .sqlite_store import (DDL, MAX_BLOBS_BYTES, MAX_REVISIONS, MAX_WORKFLOWS,
                           MAX_WORKFLOW_OPERATIONS, MAX_ADMIN_OPERATIONS,
                           SCHEMA, SQLiteStore, absolute_file)

FORMAT = "workflow-backup/1"
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_DATA_BYTES = 60 * 1024 * 1024
MAX_ADMIN_ROW_BYTES = 2048
TABLES = {"workflows": (2, ()), "revisions": (4, (3,)),
          "blobs": (2, (1,)), "operations": (5, (3, 4))}


def payload(connection, meta):
    tables = {}
    for table, (_, byte_columns) in TABLES.items():
        order = "hash" if table == "blobs" else "id" if table == "workflows" else "workflow_id,revision" if table == "revisions" else "workflow_id,id"
        rows = connection.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()
        require(len(rows) <= 8192, "limit_exceeded", "Backup row capacity exceeded.")
        tables[table] = [[base64.b64encode(bytes(value)).decode("ascii") if index in byte_columns else value
                          for index, value in enumerate(row)] for row in rows]
    return {"schema_version": SCHEMA,
            "identity": {key: meta[key] for key in ("provider_id", "store_id", "repository_id", "instance_id")},
            "tables": tables}


def snapshot_digest(connection, meta):
    return digest(encoded(payload(connection, meta)))


def check_capacity(connection, reserve=0):
    meta = decode_json(bytes(connection.execute("SELECT value FROM store_meta WHERE id=1").fetchone()[0]))
    value = payload(connection, meta)
    check_payload_capacity(value, reserve)


def check_payload_capacity(value, reserve=0):
    admin = [row for row in value["tables"]["operations"] if row[0] == ""]
    require(len(admin) + reserve <= MAX_ADMIN_OPERATIONS,
            "limit_exceeded", "Administrative history lacks capacity for another complete transfer; retain the active store.")
    require(all(len(encoded(row)) + 1 <= MAX_ADMIN_ROW_BYTES for row in admin),
            "limit_exceeded", "Administrative receipt exceeds its reserved bound.")
    normal = {**value, "tables": {**value["tables"], "operations": [row for row in value["tables"]["operations"] if row[0] != ""]}}
    require(len(encoded(normal)) <= MAX_DATA_BYTES,
            "limit_exceeded", "Complete backup capacity reached; no history was removed.")


def validate_payload(value):
    require(isinstance(value, dict) and set(value) == {"schema_version", "identity", "tables"},
            "malformed_record", "Invalid backup payload.")
    require(value["schema_version"] == SCHEMA, "unsupported_version", "Unsupported backup database schema.")
    identity = value["identity"]
    require(isinstance(identity, dict) and set(identity) == {"provider_id", "store_id", "repository_id", "instance_id"},
            "malformed_record", "Invalid backup identity.")
    for item in identity.values():
        identifier(item)
    require(isinstance(value["tables"], dict) and set(value["tables"]) == set(TABLES),
            "malformed_record", "Backup tables are incomplete or unknown.")
    decoded = {}
    for table, (width, byte_columns) in TABLES.items():
        rows = value["tables"][table]
        require(isinstance(rows, list) and len(rows) <= 8192, "limit_exceeded", "Invalid backup row count.")
        result = []
        for row in rows:
            require(isinstance(row, list) and len(row) == width, "malformed_record", "Invalid backup row width.")
            converted = list(row)
            for column in byte_columns:
                require(isinstance(row[column], str) and len(row[column]) <= (MAX_FILE + 2) * 4 // 3 + 4,
                        "limit_exceeded", "Encoded member exceeds its limit.")
                try:
                    converted[column] = base64.b64decode(row[column], validate=True)
                except ValueError as exc:
                    raise RecordError("malformed_record", "Invalid backup member encoding.") from exc
                require(len(converted[column]) <= MAX_FILE, "limit_exceeded", "Backup member exceeds its limit.")
            result.append(converted)
        decoded[table] = result

    blobs = {}
    total_bytes = 0
    for key, raw in decoded["blobs"]:
        require(isinstance(key, str) and key == digest(raw) and key not in blobs,
                "malformed_record", "Duplicate or corrupt backup blob.")
        blobs[key] = raw
        total_bytes += len(raw)
    require(total_bytes <= MAX_BLOBS_BYTES, "limit_exceeded", "Backup blob capacity exceeded.")
    workflows = {}
    for workflow_id, revision in decoded["workflows"]:
        identifier(workflow_id)
        require(isinstance(revision, str) and workflow_id not in workflows,
                "malformed_record", "Duplicate or invalid workflow identity.")
        workflows[workflow_id] = revision
    require(len(workflows) <= MAX_WORKFLOWS, "limit_exceeded", "Too many workflows.")
    revisions, counts, referenced_blobs, event_ops = {}, {}, set(), set()
    for workflow_id, revision, parent, raw in decoded["revisions"]:
        require(isinstance(workflow_id, str) and workflow_id in workflows and isinstance(revision, str) and revision == digest(raw)
                and (workflow_id, revision) not in revisions, "malformed_record", "Invalid revision identity or digest.")
        state = decode_json(raw)
        require(isinstance(state, dict) and set(state) == {"metadata", "tasks", "entrypoint", "documents", "attachments", "checkpoint", "event"},
                "malformed_record", "Invalid revision state.")
        for kind in ("documents", "attachments"):
            require(isinstance(state[kind], dict), "malformed_record", "Invalid document references.")
            for name, blob_hash in state[kind].items():
                relative_path(name)
                require(isinstance(blob_hash, str) and blob_hash in blobs, "malformed_record", "Document references a missing blob.")
                referenced_blobs.add(blob_hash)
        # Reuse the creation contract without importing or executing the stored data.
        record = {key: state[key] for key in ("metadata", "tasks", "entrypoint")}
        record["documents"] = {}
        for name, key in state["documents"].items():
            try:
                record["documents"][name] = blobs[key].decode("utf-8")
            except UnicodeError as exc:
                raise RecordError("malformed_record", "Text document is not UTF-8.") from exc
            require("\x00" not in record["documents"][name], "malformed_record", "Text document contains binary data.")
        record["attachments"] = {name: base64.b64encode(blobs[key]).decode("ascii") for name, key in state["attachments"].items()}
        SQLiteStore.validate_record(record)
        checkpoint = state["checkpoint"]
        if checkpoint is not None:
            require(isinstance(checkpoint, dict) and set(checkpoint) == {"operation_id", "recorded_at", "value"}, "malformed_record", "Invalid retained checkpoint.")
            identifier(checkpoint["operation_id"])
            timestamp(checkpoint["recorded_at"])
            validate_checkpoint(checkpoint["value"])
        event = state["event"]
        require(isinstance(event, dict) and set(event) == {"operation_id", "operation", "recorded_at", "parent"}
                and event["parent"] == parent and event["operation"] in ("create", "checkpoint", "write-document"),
                "malformed_record", "Invalid revision event.")
        identifier(event["operation_id"])
        timestamp(event["recorded_at"])
        require((workflow_id, event["operation_id"]) not in event_ops, "malformed_record", "Duplicate revision operation.")
        event_ops.add((workflow_id, event["operation_id"]))
        revisions[(workflow_id, revision)] = (parent, state)
        counts[workflow_id] = counts.get(workflow_id, 0) + 1
        require(counts[workflow_id] <= MAX_REVISIONS, "limit_exceeded", "Workflow revision capacity exceeded.")
    for workflow_id, current in workflows.items():
        seen, cursor = set(), current
        while cursor is not None:
            require(isinstance(cursor, str) and (workflow_id, cursor) in revisions and cursor not in seen,
                    "malformed_record", "Revision chain is incomplete or cyclic.")
            seen.add(cursor)
            cursor = revisions[(workflow_id, cursor)][0]
        require(len(seen) == counts.get(workflow_id, 0), "malformed_record", "Backup includes an orphan revision.")
    for (workflow_id, _), (parent, state) in revisions.items():
        operation = state["event"]["operation"]
        checkpoint = state["checkpoint"]
        if operation == "create":
            require(parent is None and checkpoint is None, "malformed_record", "Creation cannot inherit a checkpoint or parent.")
            continue
        require(isinstance(parent, str) and (workflow_id, parent) in revisions,
                "malformed_record", "A mutation requires its retained parent.")
        prior = revisions[(workflow_id, parent)][1]
        require(all(state[key] == prior[key] for key in ("metadata", "tasks", "entrypoint", "attachments")),
                "malformed_record", "Mutation changed fields outside its supported contract.")
        if operation == "checkpoint":
            require(checkpoint is not None and checkpoint["operation_id"] == state["event"]["operation_id"]
                    and state["documents"] == prior["documents"],
                    "malformed_record", "Checkpoint state does not match its revision operation.")
        else:
            require(checkpoint == prior["checkpoint"] and set(state["documents"]) == set(prior["documents"])
                    and sum(state["documents"][key] != prior["documents"][key] for key in state["documents"]) <= 1,
                    "malformed_record", "Document revision altered checkpoint history or document identity.")
    require(referenced_blobs == set(blobs), "malformed_record", "Backup includes an orphan blob.")
    operations = {}
    admin_count = sum(row[0] == "" for row in decoded["operations"])
    require(admin_count <= MAX_ADMIN_OPERATIONS and len(decoded["operations"]) - admin_count <= MAX_WORKFLOW_OPERATIONS,
            "limit_exceeded", "Operation capacity exceeded.")
    check_payload_capacity(value)
    for workflow_id, op, request_hash, receipt_raw, event_raw in decoded["operations"]:
        require(isinstance(workflow_id, str) and (workflow_id == "" or workflow_id in workflows), "malformed_record", "Operation scope is missing.")
        identifier(op)
        require(isinstance(request_hash, str) and len(request_hash) == 71 and request_hash.startswith("sha256:")
                and all(c in "0123456789abcdef" for c in request_hash[7:]), "malformed_record", "Invalid operation request digest.")
        require((workflow_id, op) not in operations, "malformed_record", "Duplicate operation identity.")
        receipt, event = decode_json(receipt_raw), decode_json(event_raw)
        require(isinstance(receipt, dict) and receipt.get("operation_id") == op and receipt.get("state") == "applied"
                and receipt.get("replayed") is False and isinstance(event, dict) and event.get("operation_id") == op
                and set(event) == {"operation_id", "operation", "recorded_at"},
                "malformed_record", "Invalid retained operation result.")
        timestamp(event["recorded_at"])
        if workflow_id:
            ref = {"provider_id": identity["provider_id"], "store_id": identity["store_id"], "workflow_id": workflow_id}
            require(receipt.get("workflow_ref") == ref and (workflow_id, receipt.get("revision")) in revisions,
                    "malformed_record", "Receipt references a missing workflow revision.")
            state = revisions[(workflow_id, receipt["revision"])][1]
            require(state["event"]["operation_id"] == op and state["event"]["operation"] == event.get("operation"),
                    "malformed_record", "Receipt and revision event disagree.")
        else:
            shapes = {"init": {"instance_id", "store_state"}, "restore": {"instance_id", "store_state", "snapshot_digest"},
                      "deactivate": {"store_state", "retirement_seal", "snapshot_digest"}, "activate": {"instance_id", "store_state"}}
            kind = event.get("operation")
            require(isinstance(kind, str) and kind in shapes and set(receipt) == shapes[kind] |
                    {"state", "operation_id", "replayed"}, "malformed_record", "Invalid administrative receipt shape.")
            require(receipt["store_state"] == {"init": "active", "restore": "inactive", "deactivate": "retired", "activate": "active"}[kind],
                    "malformed_record", "Administrative receipt state disagrees with its operation.")
            for key in ("instance_id", "retirement_seal"):
                if key in receipt:
                    identifier(receipt[key])
            if "snapshot_digest" in receipt:
                value_digest = receipt["snapshot_digest"]
                require(isinstance(value_digest, str) and len(value_digest) == 71 and value_digest.startswith("sha256:")
                        and all(c in "0123456789abcdef" for c in value_digest[7:]), "malformed_record", "Invalid retained snapshot digest.")
        operations[(workflow_id, op)] = receipt
    require(event_ops == {key for key in operations if key[0]}, "malformed_record", "Revision and operation history differ.")
    return decoded


def preflight(path, expected_digest):
    source = absolute_file(path)
    require(isinstance(expected_digest, str) and expected_digest.startswith("sha256:"), "invalid_input", "Supply the observed backup digest.")
    require(source.is_file(), "not_found", "Backup is missing.")
    with source.open("rb") as stream:
        raw = stream.read(MAX_ARCHIVE + 1)
    require(len(raw) <= MAX_ARCHIVE, "limit_exceeded", "Backup exceeds the archive limit.")
    require(digest(raw) == expected_digest, "integrity_error", "Backup bytes differ from the expected digest.")
    try:
        def reject_constant(_):
            raise ValueError("Non-finite number")
        archive = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)
        validate_unicode(archive)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise RecordError("malformed_record", "Invalid backup JSON.") from exc
    require(isinstance(archive, dict) and set(archive) == {"format", "snapshot_digest", "payload"}, "malformed_record", "Invalid backup envelope.")
    require(archive["format"] == FORMAT, "unsupported_version", "Unsupported backup format.")
    require(archive["snapshot_digest"] == digest(encoded(archive["payload"])), "integrity_error", "Backup snapshot digest mismatch.")
    decoded = validate_payload(archive["payload"])
    return archive, decoded


def export_store(store, request):
    destination = absolute_file(request.get("destination"))
    require(not destination.exists() and destination.parent.is_dir(), "already_exists", "Select a new backup file in an existing directory.")
    with store.transaction() as (connection, meta):
        value = payload(connection, meta)
    validate_payload(value)
    snapshot = digest(encoded(value))
    raw = encoded({"format": FORMAT, "snapshot_digest": snapshot, "payload": value})
    require(len(raw) <= MAX_ARCHIVE, "limit_exceeded", "Backup exceeds the archive limit.")
    created = False
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        raise
    return {"state": "exported", "archive_digest": digest(raw), "snapshot_digest": snapshot,
            "counts": {key: len(rows) for key, rows in value["tables"].items()}}


def restore_store(store, request):
    archive, tables = preflight(request.get("archive"), request.get("archive_digest"))
    identity = archive["payload"]["identity"]
    require((identity["provider_id"], identity["store_id"], identity["repository_id"]) ==
            (store.provider_id, store.store_id, store.repository_id), "binding_mismatch", "Restore logical identity must match the explicit target binding.")
    op = identifier(request.get("operation_id"))
    if store.database.exists():
        with store.transaction() as (connection, _):
            prior = store.replay(connection, "", op, request)
            require(prior is not None, "already_exists", "Restore never overwrites an existing store.")
            return prior
    check_payload_capacity(archive["payload"], reserve=2)
    require(store.database.parent.is_dir(), "not_found", "Select an existing persistent parent directory.")
    try:
        fd = os.open(store.database, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise RecordError("writer_busy", "Another restore reserved the target.") from exc
    os.close(fd)
    connection = None
    try:
        connection = sqlite3.connect(store.database, isolation_level=None)
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        for statement in DDL:
            connection.execute(statement)
        meta = {"schema_version": SCHEMA, "provider_id": store.provider_id, "store_id": store.store_id,
                "repository_id": store.repository_id, "repository_binding": store.binding,
                "instance_id": str(uuid.uuid4()), "state": "inactive", "retirement": None,
                "origin": {"instance_id": identity["instance_id"], "snapshot_digest": archive["snapshot_digest"]}}
        connection.execute("INSERT INTO store_meta VALUES(1,?)", (encoded(meta),))
        for table, (width, _) in TABLES.items():
            connection.executemany(f"INSERT INTO {table} VALUES({','.join('?' for _ in range(width))})", tables[table])
        receipt = {"state": "applied", "operation_id": op, "instance_id": meta["instance_id"], "store_state": "inactive",
                   "snapshot_digest": archive["snapshot_digest"], "replayed": False}
        # A new restore identity cannot shadow any retained administrative operation.
        require(connection.execute("SELECT 1 FROM operations WHERE workflow_id='' AND id=?", (op,)).fetchone() is None,
                "operation_id_conflict", "Restore ID conflicts with a retained operation.")
        store.save_operation(connection, "", request, receipt)
        connection.commit()
        return receipt
    except BaseException:
        if connection is not None:
            connection.close()
            connection = None
        store.database.unlink(missing_ok=True)
        raise
    finally:
        if connection is not None:
            connection.close()


def deactivate(store, request):
    op = identifier(request.get("operation_id"))
    with store.transaction(write=True) as (connection, meta):
        prior = store.replay(connection, "", op, request)
        if prior is not None:
            return prior
        require(meta["state"] == "active", "store_inactive", "Only the active original store can retire.")
        # Same requirement as restore: fail before retirement if the archived
        # history cannot accommodate the next target's restore and activation.
        check_capacity(connection, reserve=2)
        snapshot = snapshot_digest(connection, meta)
        require(request.get("snapshot_digest") == snapshot, "revision_conflict", "Export snapshot is stale; export again before retirement.")
        seal = str(uuid.uuid4())
        meta["state"] = "retired"
        meta["retirement"] = {"seal": seal, "snapshot_digest": snapshot, "successor_instance_id": None}
        store.save_meta(connection, meta)
        receipt = {"state": "applied", "operation_id": op, "store_state": "retired", "retirement_seal": seal,
                   "snapshot_digest": snapshot, "replayed": False}
        store.save_operation(connection, "", request, receipt)
        return receipt


def activate(store, request):
    op = identifier(request.get("operation_id"))
    with store.transaction() as (connection, meta):
        prior = store.replay(connection, "", op, request)
        if prior is not None:
            return prior
        require(meta["state"] == "inactive" and meta["origin"] is not None, "store_inactive", "Only an inactive restored store can activate.")
        check_capacity(connection, reserve=1)
    old_path = absolute_file(request.get("retired_database"))
    require(old_path != store.database, "binding_mismatch", "Activation requires the original retired database.")
    require(old_path.is_file(), "unsupported_capability", "Disaster activation without the original store requires a separately selected recovery procedure.")
    original = SQLiteStore(store.root, store.provider_id, {"store_id": store.store_id, "repository_id": store.repository_id,
                                                         "database": str(old_path), "busy_timeout_ms": store.timeout})
    # Phase one is durable. A failed phase two is recoverable only for this same instance.
    with original.transaction(write=True) as (connection, old):
        retirement = old.get("retirement")
        require(old["state"] == "retired" and isinstance(retirement, dict) and
                old["instance_id"] == meta["origin"]["instance_id"] and
                retirement["snapshot_digest"] == meta["origin"]["snapshot_digest"] and
                request.get("retirement_seal") == retirement["seal"],
                "binding_mismatch", "Original retirement proof does not match this restored snapshot.")
        require(retirement["successor_instance_id"] in (None, meta["instance_id"]),
                "binding_mismatch", "The original store already names another successor.")
        retirement["successor_instance_id"] = meta["instance_id"]
        original.save_meta(connection, old)
    try:
        with store.transaction(write=True) as (connection, current):
            prior = store.replay(connection, "", op, request)
            if prior is not None:
                return prior
            require(current["instance_id"] == meta["instance_id"] and current["state"] == "inactive"
                    and current["origin"] == meta["origin"],
                    "binding_mismatch", "Restored instance changed during activation.")
            current["state"] = "active"
            store.save_meta(connection, current)
            receipt = {"state": "applied", "operation_id": op, "store_state": "active", "instance_id": current["instance_id"], "replayed": False}
            store.save_operation(connection, "", request, receipt)
            return receipt
    except (RecordError, OSError, sqlite3.Error) as exc:
        error = RecordError("activation_pending", "The original store reserved this successor; preserve both stores and reconcile/retry this same target.")
        error.mutation_state = "unknown"
        raise error from exc
