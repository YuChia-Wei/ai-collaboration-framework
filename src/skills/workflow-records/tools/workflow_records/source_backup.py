"""Complete schema-2 backup closure, retaining the original v1 native validator."""
import base64
from contextlib import closing
import hashlib
import sqlite3

from . import source_contract as c
from .contracts import StoreRef, decode_json, encoded, require
from .source_store import DDL, TABLES, MAX_ROWS, MAX_RAW, MAX_PREPARED

MAX_DATA_BYTES = 240 * 1024 * 1024


def native_payload(value):
    from . import backup
    return {**value, "schema_version": "workflow-sqlite/1", "tables": {key: value["tables"][key] for key in backup.TABLES}}


def payload(connection, meta):
    from . import backup
    value = backup.payload(connection, {**meta, "schema_version": "workflow-sqlite/1"})
    value["schema_version"] = meta["schema_version"]
    selected_tables = TABLES
    if meta["schema_version"] == c.SCHEMA3:
        from .source_config import TABLES as config_tables
        selected_tables = {**TABLES, **config_tables}
    for table, (_, columns) in selected_tables.items():
        rows = connection.execute("SELECT * FROM " + table + " ORDER BY 1,2").fetchall()
        require(len(rows) <= MAX_ROWS, "limit_exceeded", "Source backup row capacity exceeded.")
        value["tables"][table] = [[base64.b64encode(bytes(item)).decode("ascii") if index in columns else item for index, item in enumerate(row)] for row in rows]
    return value


def check_capacity(value, reserve=0):
    from . import backup
    backup.check_payload_capacity(native_payload(value), reserve)
    require(len(encoded(value)) + reserve * backup.MAX_ADMIN_ROW_BYTES <= MAX_DATA_BYTES, "limit_exceeded", "Complete schema-2 backup capacity exceeded; no history was removed.")
    raw = sum(len(base64.b64decode(row[1], validate=True)) for row in value["tables"]["source_blobs"])
    prepared = sum(len(base64.b64decode(row[3], validate=True)) for row in value["tables"]["replica_steps"])
    require(raw <= MAX_RAW and prepared <= MAX_PREPARED, "limit_exceeded", "Source raw/prepared retention is full.")
    require(all(isinstance(rows, list) and len(rows) <= MAX_ROWS for rows in value["tables"].values()), "limit_exceeded", "Schema-2 row retention is full.")


def validate_payload(value):
    from . import backup
    from . import source_store as s
    selected_ddl, selected_tables = DDL, TABLES
    schema3 = isinstance(value, dict) and value.get("schema_version") == c.SCHEMA3
    if schema3:
        from .source_config import DDL as config_ddl, TABLES as config_tables
        selected_ddl, selected_tables = DDL + config_ddl, {**TABLES, **config_tables}
    require(isinstance(value, dict) and set(value) == {"schema_version", "identity", "tables"}
            and value["schema_version"] in (c.SCHEMA, c.SCHEMA21, c.SCHEMA3) and isinstance(value["tables"], dict)
            and set(value["tables"]) == set(backup.TABLES) | set(selected_tables), "malformed_record", "Source backup table closure is incomplete.")
    decoded = backup.validate_payload(native_payload(value), schema2_native=True)
    check_capacity(value)
    for table, (width, columns) in selected_tables.items():
        output = []
        for row in value["tables"][table]:
            require(isinstance(row, list) and len(row) == width, "malformed_record", "Invalid source backup row width.")
            result = list(row)
            for index in columns:
                require(isinstance(row[index], str) and len(row[index]) <= (c.MAX_INPUT + 2) * 4 // 3 + 4, "limit_exceeded", "Encoded source member is too large.")
                raw = base64.b64decode(row[index], validate=True)
                require(base64.b64encode(raw).decode("ascii") == row[index] and len(raw) <= c.MAX_INPUT,
                        "malformed_record", "Noncanonical source backup encoding.")
                result[index] = raw
            for index, item in enumerate(result):
                if index not in columns:
                    require(type(item) in (str, int), "malformed_record", "Invalid source backup scalar.")
            output.append(result)
        decoded[table] = output
    try:
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            for statement in selected_ddl:
                connection.execute(statement)
            for table, (width, _) in selected_tables.items():
                connection.executemany("INSERT INTO " + table + " VALUES(" + ",".join("?" for _ in range(width)) + ")", decoded[table])
            used = set()
            native = {(row[0], row[1]): bytes(row[3]) for row in decoded["revisions"]}
            native_blobs = {row[0]: bytes(row[1]) for row in decoded["blobs"]}
            native_operations = {(row[0], row[1]): (row[2], row[3], row[4]) for row in decoded["operations"]}
            captured = set()
            for sequence, key, kind, workflow_id, revision, _ in decoded["source_snapshots"]:
                c.integer(sequence, 1)
                require(kind in s.KINDS, "malformed_record", "Unknown backup source kind.")
                c.native_id(workflow_id)
                c.native_id(revision)
                row, manifest = s.snapshot(connection, key)
                require(manifest["source"]["mapping_version"] == c.MAPPING and manifest["source"]["kind"] == kind
                        and manifest["source"]["original_workflow_id"] == workflow_id and manifest["workflow"]["original_id"] == workflow_id
                        and manifest["workflow"]["kind"] == kind and manifest["workflow"]["id"] == c.unit_id(kind, workflow_id),
                        "malformed_record", "Source mapping is not reversible or changed.")
                if decoded["source_bindings"]:
                    c.validate("command", {"service_contract_version": c.NATIVE_PROFILE, "schema_version": "1.0",
                                      "project_ref": {"store_id": "validation", "namespace": "personal", "project_id": "validation"},
                                      "operation_id": "validation", "expected_revision": 0, "command": "replica.begin",
                                      "payload": {"source_id": "validation", "workflow_id": manifest["workflow"]["id"], "source_revision": revision,
                                                  "manifest_hash": c.digest(c.canonical(manifest)), "manifest": manifest}})
                if kind == "native-workflow":
                    original = manifest["source"]["native_revision"]
                    require(revision == "native-" + original[7:] and (workflow_id, original) in native, "malformed_record", "Native source snapshot lost its revision.")
                    state = decode_json(native[(workflow_id, original)])
                    operation = native_operations[(workflow_id, state["event"]["operation_id"])]
                    source, workflow, files = s.native_projection(original, native[(workflow_id, original)], state, operation, native_blobs.__getitem__)
                    expected_source = {**source, "kind": kind, "original_workflow_id": workflow_id, "mapping_version": c.MAPPING}
                    expected_workflow = {**workflow, "id": c.unit_id(kind, workflow_id), "original_id": workflow_id, "kind": kind}
                    expected_files = [{"path": name, "mode": mode, "size": len(raw), "sha256": c.digest(raw)} for name, mode, raw in files]
                    require(manifest["source"] == expected_source and manifest["workflow"] == expected_workflow and manifest["files"] == expected_files,
                            "integrity_error", "Native source projection differs from its complete retained state/header/file mapping.")
                    for name, _, expected in files:
                        chunks = connection.execute("SELECT b.data FROM source_chunks c JOIN source_blobs b ON b.hash=c.hash WHERE snapshot_id=? AND path=? ORDER BY chunk_index", (key, name)).fetchall()
                        require(b"".join(bytes(row[0]) for row in chunks) == expected, "integrity_error", "Native snapshot file lost exact retained bytes.")
                    captured.add((workflow_id, original))
            require(captured == set(native), "malformed_record", "Schema-2 native revisions lack source snapshots.")
            for key, raw in decoded["source_blobs"]:
                require(len(raw) <= c.CHUNK and c.digest(raw) == key, "integrity_error", "Corrupt source backup chunk.")
            used = {row[3] for row in decoded["source_chunks"]}
            require(used == {row[0] for row in decoded["source_blobs"]}, "malformed_record", "Orphan source blob.")
            bindings = {}
            for key, target_key, raw in decoded["source_bindings"]:
                target = c.parse(raw)
                c.binding(target)
                require(target["binding_id"] == key and target_key == c.digest(c.canonical({"project_ref": target["project_ref"], "source_id": target["source_id"]})),
                        "malformed_record", "Source binding identity changed.")
                bindings[key] = target
            controls = s.disabled_bindings(connection)
            require(not controls or value["schema_version"] == c.SCHEMA21, "malformed_record", "Disable controls require the explicit schema-2.1 marker.")
            require(value["schema_version"] != c.SCHEMA21 or controls, "malformed_record", "Schema-2.1 lost its disable controls.")
            for control in controls.values():
                selected_ref = StoreRef.parse(control["request"]["store_ref"])
                require((selected_ref.provider_id, selected_ref.store_id) == (value["identity"]["provider_id"], value["identity"]["store_id"]),
                        "malformed_record", "Disable request belongs to another store.")
            heads = {}
            expected_steps = set()
            for sequence, key, snapshot_id, binding_id, expected, raw in sorted(decoded["replica_intents"]):
                c.integer(sequence, 1)
                c.integer(expected)
                target = c.parse(raw)
                c.binding(target)
                require(binding_id in bindings and target == bindings[binding_id]
                        and key == "intent-" + hashlib.sha256((binding_id + ":" + snapshot_id).encode()).hexdigest(),
                        "malformed_record", "Immutable replica target or intent identity changed.")
                manifest = s.snapshot(connection, snapshot_id, False)[1]
                scope = (binding_id, manifest["workflow"]["id"])
                require(expected == heads.get(scope, 0), "malformed_record", "Replica remote revisions are not ordered.")
                heads[scope] = expected + 1
                commands = s.commands(connection, snapshot_id, target, expected, key)
                retained = connection.execute("SELECT step_index,operation_id,command FROM replica_steps WHERE intent_id=? ORDER BY step_index", (key,)).fetchall()
                require(len(retained) == len(commands), "malformed_record", "Prepared replica steps are incomplete.")
                for index, ((selected, operation_id, prepared), command) in enumerate(zip(retained, commands)):
                    require(type(selected) is int and selected == index and operation_id == command["operation_id"] and bytes(prepared) == c.canonical(command),
                            "integrity_error", "Persisted original replica command changed.")
                    c.validate("command", command)
                    expected_steps.add((key, index))
            require(expected_steps == {(row[0], row[1]) for row in decoded["replica_steps"]}, "malformed_record", "Orphan replica step.")
            if schema3:
                from .source_config import validate_backup
                validate_backup(connection, decoded)
            else:
                require({(row[2], row[3]) for row in decoded["replica_intents"]} == {(row[1], binding_id) for row in decoded["source_snapshots"] for binding_id in bindings
                        if binding_id not in controls or row[0] <= controls[binding_id]["cutoff_sequence"]},
                        "malformed_record", "A fixed target delivery intent is missing.")
            # Replay observation interpretation in order without trusting stored
            # outcome flags. Earlier accepted evidence cannot be overwritten.
            observations = sorted(decoded["replica_observations"])
            connection.execute("DELETE FROM replica_observations")
            for sequence, intent_id, index, raw in observations:
                c.integer(sequence, 1)
                c.integer(index)
                observation = c.parse(raw)
                c.fields(observation, {"channel", "transport", "evaluation"})
                require(observation["channel"] in ("direct", "lookup"), "malformed_record", "Invalid observation channel.")
                command = c.parse(bytes(connection.execute("SELECT command FROM replica_steps WHERE intent_id=? AND step_index=?", (intent_id, index)).fetchone()[0]))
                evaluation = s.evaluate(connection, intent_id, index, command, observation["channel"], observation["transport"])
                require(evaluation == observation["evaluation"], "integrity_error", "Stored receipt classification was forged.")
                connection.execute("INSERT INTO replica_observations VALUES(?,?,?,?)", (sequence, intent_id, index, raw))
            for operation_id, request_hash, raw in decoded["source_operations"]:
                c.native_id(operation_id)
                require(re_full_hash(request_hash), "malformed_record", "Invalid source operation request digest.")
                result = c.parse(raw)
                require(isinstance(result, dict) and {"operation_id", "state", "replayed"} <= set(result),
                        "malformed_record", "Source operation receipt must be an object with required identity/state fields.")
                require(result["operation_id"] == operation_id and result["state"] == "applied" and result["replayed"] is False,
                        "malformed_record", "Invalid source operation receipt.")
                if "snapshot_id" in result:
                    require(connection.execute("SELECT 1 FROM source_snapshots WHERE id=?", (result["snapshot_id"],)).fetchone(), "malformed_record", "Source receipt snapshot is absent.")
    except sqlite3.Error as exc:
        raise c.RecordError("malformed_record", "Schema-2 backup has invalid references or duplicate keys.") from exc
    return decoded


def re_full_hash(value):
    import re
    return isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None
