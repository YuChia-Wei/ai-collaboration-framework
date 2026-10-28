"""Schema-2 immutable local snapshots and persisted single-carrier delivery steps."""
from __future__ import annotations
import base64
import copy
import hashlib
import re
import sqlite3
import subprocess

from . import source_contract as c
from .contracts import RecordError, StoreRef, WorkflowRef, decode_json, encoded, require
from .sqlite_store import SQLiteStore, now, request_digest

KINDS = ("native-workflow", "archive-workflow", "archive-root-index")
MAX_RAW = 64 * 1024 * 1024
MAX_PREPARED = 128 * 1024 * 1024
MAX_ROWS = 65536
DDL = (
    "CREATE TABLE source_snapshots (sequence INTEGER PRIMARY KEY, id TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, workflow_id TEXT NOT NULL, revision TEXT NOT NULL, manifest BLOB NOT NULL, UNIQUE(kind,workflow_id,revision))",
    "CREATE TABLE source_blobs (hash TEXT PRIMARY KEY, data BLOB NOT NULL)",
    "CREATE TABLE source_chunks (snapshot_id TEXT NOT NULL REFERENCES source_snapshots(id), path TEXT NOT NULL, chunk_index INTEGER NOT NULL, hash TEXT NOT NULL REFERENCES source_blobs(hash), PRIMARY KEY(snapshot_id,path,chunk_index))",
    "CREATE TABLE source_bindings (id TEXT PRIMARY KEY, target_key TEXT NOT NULL UNIQUE, value BLOB NOT NULL)",
    "CREATE TABLE replica_intents (sequence INTEGER PRIMARY KEY, id TEXT NOT NULL UNIQUE, snapshot_id TEXT NOT NULL REFERENCES source_snapshots(id), binding_id TEXT NOT NULL REFERENCES source_bindings(id), expected_revision INTEGER NOT NULL, target BLOB NOT NULL, UNIQUE(snapshot_id,binding_id))",
    "CREATE TABLE replica_steps (intent_id TEXT NOT NULL REFERENCES replica_intents(id), step_index INTEGER NOT NULL, operation_id TEXT NOT NULL UNIQUE, command BLOB NOT NULL, PRIMARY KEY(intent_id,step_index))",
    "CREATE TABLE replica_observations (sequence INTEGER PRIMARY KEY, intent_id TEXT NOT NULL, step_index INTEGER NOT NULL, value BLOB NOT NULL, FOREIGN KEY(intent_id,step_index) REFERENCES replica_steps(intent_id,step_index))",
    "CREATE TABLE source_operations (id TEXT PRIMARY KEY, request_digest TEXT NOT NULL, receipt BLOB NOT NULL)",
)
TABLES = {"source_snapshots": (6, (5,)), "source_blobs": (2, (1,)), "source_chunks": (4, ()),
          "source_bindings": (3, (2,)), "replica_intents": (6, (5,)), "replica_steps": (4, (3,)),
          "replica_observations": (4, (3,)), "source_operations": (3, (2,))}


def schema2(meta):
    require(meta["schema_version"] in (c.SCHEMA, c.SCHEMA21, c.SCHEMA3), "explicit_upgrade_required",
            "This operation requires an explicitly initialized workflow-sqlite/2 database; v1 was not upgraded.")


def replay(connection, request):
    c.native_id(request.get("operation_id"))
    row = connection.execute("SELECT request_digest,receipt FROM source_operations WHERE id=?", (request["operation_id"],)).fetchone()
    if row:
        require(row[0] == request_digest(request), "operation_id_conflict", "Source operation ID names different content.")
        result = c.parse(bytes(row[1]))
        result["replayed"] = True
        return result


def receipt(connection, request, result):
    value = {"state": "applied", "operation_id": request["operation_id"], "replayed": False, **result}
    require(len(encoded(value)) <= c.MAX_INPUT, "limit_exceeded", "Source operation receipt exceeds retention cell bound.")
    connection.execute("INSERT INTO source_operations VALUES(?,?,?)", (request["operation_id"], request_digest(request), encoded(value)))
    from .backup import check_capacity
    check_capacity(connection)
    return value


def disabled_bindings(connection):
    """Read immutable disable receipts; never rewrite a binding or historical intent."""
    disabled = {}
    maximum = connection.execute("SELECT coalesce(max(sequence),0) FROM source_snapshots").fetchone()[0]
    for operation_id, fingerprint, raw in connection.execute("SELECT id,request_digest,receipt FROM source_operations"):
        value = c.parse(bytes(raw))
        require(isinstance(value, dict), "malformed_record", "Source operation receipt must be an object.")
        if value.get("operation") != "binding-disable":
            require(not ({"cutoff_sequence", "binding_digest"} & set(value)), "malformed_record", "Unrecognized binding control receipt.")
            continue
        c.fields(value, {"state", "operation_id", "replayed", "operation", "request", "binding_id", "binding_digest", "cutoff_sequence"})
        request = value["request"]
        c.fields(request, {"contract_version", "operation", "store_ref", "operation_id", "binding_id", "expected_binding_digest", "expected_snapshot_sequence"}, {"max_output_bytes"})
        ref = StoreRef.parse(request["store_ref"])
        c.native_id(operation_id)
        c.native_id(value["binding_id"])
        if "max_output_bytes" in request:
            c.integer(request["max_output_bytes"], 2048, c.MAX_INPUT)
        cutoff = c.integer(value["cutoff_sequence"], 0, maximum)
        c.integer(request["expected_snapshot_sequence"], 0, maximum)
        require(cutoff == 0 or connection.execute("SELECT 1 FROM source_snapshots WHERE sequence=?", (cutoff,)).fetchone(), "malformed_record", "Control cutoff snapshot is absent.")
        target = connection.execute("SELECT value FROM source_bindings WHERE id=?", (value["binding_id"],)).fetchone()
        require(target is not None, "malformed_record", "Control binding is absent.")
        target_digest = c.digest(c.canonical(c.parse(bytes(target[0]))))
        require(value["state"] == "applied" and value["replayed"] is False and
                request["contract_version"] == c.PROFILE and request["operation"] == "binding-disable" and
                request["operation_id"] == value["operation_id"] == operation_id and
                request["binding_id"] == value["binding_id"] and
                request["expected_binding_digest"] == value["binding_digest"] == target_digest and
                request["expected_snapshot_sequence"] == cutoff and fingerprint == request_digest(request) and
                value["binding_id"] not in disabled,
                "malformed_record", "Disable control identity, digest, cutoff or uniqueness changed.")
        disabled[value["binding_id"]] = value
    return disabled


def binding_status(connection, binding_id):
    c.native_id(binding_id)
    target = connection.execute("SELECT value FROM source_bindings WHERE id=?", (binding_id,)).fetchone()
    require(target is not None, "not_found", "Source binding is absent.")
    control = disabled_bindings(connection).get(binding_id)
    return {"binding_id": binding_id, "binding_digest": c.digest(c.canonical(c.parse(bytes(target[0])))),
            "snapshot_sequence": connection.execute("SELECT coalesce(max(sequence),0) FROM source_snapshots").fetchone()[0],
            "state": "disabled" if control else "active", "disable_receipt": control}


def snapshot(connection, snapshot_id, verify=True):
    row = connection.execute("SELECT sequence,id,kind,workflow_id,revision,manifest FROM source_snapshots WHERE id=?", (snapshot_id,)).fetchone()
    require(row is not None, "not_found", "Selected source snapshot is absent.")
    manifest = c.parse(bytes(row[5]))
    require(row[1] == "snapshot-" + c.digest(c.canonical(manifest))[7:], "integrity_error", "Source manifest digest changed.")
    if verify:
        verify_files(connection, row[1], manifest)
    return row, manifest


def verify_files(connection, snapshot_id, manifest):
    c.fields(manifest, {"source", "workflow", "files"})
    require(isinstance(manifest["files"], list) and len(manifest["files"]) <= 1000, "limit_exceeded", "Source unit has too many files.")
    paths, total, count = set(), 0, 0
    for file in manifest["files"]:
        c.fields(file, {"path", "mode", "size", "sha256"})
        c.path(file["path"])
        require(file["path"] not in paths and isinstance(file["mode"], str) and re.fullmatch("[0-7]{6}", file["mode"]) is not None,
                "malformed_record", "Duplicate path or invalid original mode.")
        paths.add(file["path"])
        c.integer(file["size"], 0, c.MAX_FILE)
        chunks = connection.execute("SELECT chunk_index,hash FROM source_chunks WHERE snapshot_id=? AND path=? ORDER BY chunk_index", (snapshot_id, file["path"])).fetchall()
        require(len(chunks) == (file["size"] + c.CHUNK - 1) // c.CHUNK, "integrity_error", "Source file chunks are missing or extra.")
        hasher, size = hashlib.sha256(), 0
        for index, (selected_index, key) in enumerate(chunks):
            require(selected_index == index, "integrity_error", "Source chunk indices are not contiguous.")
            found = connection.execute("SELECT data FROM source_blobs WHERE hash=?", (key,)).fetchone()
            require(found is not None, "integrity_error", "Source chunk data is missing.")
            raw = bytes(found[0])
            require(c.digest(raw) == key and len(raw) == min(c.CHUNK, file["size"] - size), "integrity_error", "Source chunk hash or size is invalid.")
            hasher.update(raw)
            size += len(raw)
        require(size == file["size"] and "sha256:" + hasher.hexdigest() == file["sha256"], "integrity_error", "Reconstructed source file hash or size differs.")
        total += size
        count += len(chunks)
    require(total <= c.MAX_UNIT and len(c.canonical(manifest)) <= 240000, "limit_exceeded", "Source unit/manifest exceeds replica bounds.")
    require(connection.execute("SELECT count(*) FROM source_chunks WHERE snapshot_id=?", (snapshot_id,)).fetchone()[0] == count,
            "integrity_error", "Source snapshot contains undeclared chunks.")


def publish(connection, kind, workflow_id, source, workflow, files, revision=None):
    require(kind in KINDS, "invalid_input", "Unknown source unit kind.")
    c.native_id(workflow_id)
    records = [{"path": path, "mode": mode, "size": len(raw), "sha256": c.digest(raw)} for path, mode, raw in files]
    manifest = {"source": {**source, "kind": kind, "original_workflow_id": workflow_id, "mapping_version": c.MAPPING},
                "workflow": {**workflow, "id": c.unit_id(kind, workflow_id), "original_id": workflow_id, "kind": kind}, "files": records}
    key = "snapshot-" + c.digest(c.canonical(manifest))[7:]
    revision = revision or key
    c.native_id(revision)
    existing = connection.execute("SELECT id FROM source_snapshots WHERE kind=? AND workflow_id=? AND revision=?", (kind, workflow_id, revision)).fetchone()
    if existing:
        require(existing[0] == key, "revision_conflict", "Source revision already names another immutable manifest.")
        snapshot(connection, key)
        return key
    require(sum(len(raw) for _, _, raw in files) <= c.MAX_UNIT, "limit_exceeded", "Source unit exceeds raw byte limit.")
    connection.execute("INSERT INTO source_snapshots(id,kind,workflow_id,revision,manifest) VALUES(?,?,?,?,?)", (key, kind, workflow_id, revision, c.canonical(manifest)))
    for path, _, raw in files:
        for index, offset in enumerate(range(0, len(raw), c.CHUNK)):
            chunk = raw[offset:offset + c.CHUNK]
            hash_value = c.digest(chunk)
            connection.execute("INSERT OR IGNORE INTO source_blobs VALUES(?,?)", (hash_value, chunk))
            connection.execute("INSERT INTO source_chunks VALUES(?,?,?,?)", (key, path, index, hash_value))
    snapshot(connection, key)
    selected_schema = decode_json(bytes(connection.execute("SELECT value FROM store_meta WHERE id=1").fetchone()[0]))["schema_version"]
    if selected_schema == c.SCHEMA3:
        from .source_config import capture_membership
        capture_membership(connection, key, kind, workflow_id)
    else:
        disabled = disabled_bindings(connection)
        for (binding_id, value) in connection.execute("SELECT id,value FROM source_bindings ORDER BY id").fetchall():
            if binding_id not in disabled:
                enqueue(connection, key, binding_id, c.parse(bytes(value)))
    return key


def native_projection(revision, raw, state, operation, read_blob):
    """Pure deterministic projection shared by capture and backup equivalence."""
    files = [("_native/state.json", "100644", raw), ("_native/receipt.json", "100644", bytes(operation[1])),
             ("_native/event.json", "100644", bytes(operation[2])), ("_native/request-digest.txt", "100644", operation[0].encode("ascii"))]
    for kind in ("documents", "attachments"):
        for name, key in state[kind].items():
            files.append((kind + "/" + name, "100644", read_blob(key)))
    source = {"type": "sqlite-native", "native_revision": revision, "native_operation_id": state["event"]["operation_id"]}
    workflow = {"title": state["metadata"]["title"], "status": state["metadata"]["status"],
                "view_provenance": {"file": "_native/state.json", "selector": "metadata"}}
    return source, workflow, files


def capture_native(connection, workflow_id, revision):
    row = connection.execute("SELECT state FROM revisions WHERE workflow_id=? AND revision=?", (workflow_id, revision)).fetchone()
    require(row is not None, "integrity_error", "Native snapshot revision is missing.")
    raw = bytes(row[0])
    state = decode_json(raw)
    op = state["event"]["operation_id"]
    operation = connection.execute("SELECT request_digest,receipt,event FROM operations WHERE workflow_id=? AND id=?", (workflow_id, op)).fetchone()
    require(operation is not None, "integrity_error", "Native receipt must exist before source capture.")
    source, workflow, files = native_projection(revision, raw, state, operation, lambda key: SQLiteStore.blob(connection, key))
    publish(connection, "native-workflow", workflow_id, source, workflow, files, "native-" + revision[7:])


def commands(connection, snapshot_id, target, expected, intent_id):
    row, manifest = snapshot(connection, snapshot_id)
    common = {"service_contract_version": c.NATIVE_PROFILE, "schema_version": "1.0", "project_ref": target["project_ref"], "expected_revision": expected}
    payload = {"source_id": target["source_id"], "workflow_id": manifest["workflow"]["id"], "source_revision": row[4]}
    output = []
    def add(name, values):
        operation_id = "delivery-" + hashlib.sha256((intent_id + ":" + str(len(output))).encode()).hexdigest()
        value = {**common, "operation_id": operation_id, "command": name, "payload": {**payload, **values}}
        require(len(c.canonical(value)) <= 300000, "limit_exceeded", "Prepared replica command exceeds native request limit.")
        output.append(value)
    add("replica.begin", {"manifest_hash": c.digest(c.canonical(manifest)), "manifest": manifest})
    batch = []
    for file in manifest["files"]:
        for index, key, data in connection.execute("SELECT c.chunk_index,c.hash,b.data FROM source_chunks c JOIN source_blobs b ON b.hash=c.hash WHERE c.snapshot_id=? AND c.path=? ORDER BY c.chunk_index", (snapshot_id, file["path"])):
            chunk = {"path": file["path"], "index": index, "content_base64": base64.b64encode(bytes(data)).decode("ascii"), "chunk_hash": key}
            trial = {**common, "operation_id": "delivery-" + "0" * 64, "command": "replica.chunk.put", "payload": {**payload, "chunks": batch + [chunk]}}
            if batch and (len(batch) == 32 or len(c.canonical(trial)) > 300000):
                add("replica.chunk.put", {"chunks": batch})
                batch = []
            batch.append(chunk)
    if batch:
        add("replica.chunk.put", {"chunks": batch})
    add("replica.activate", {"manifest_hash": c.digest(c.canonical(manifest))})
    return output


def enqueue(connection, snapshot_id, binding_id, target):
    row, manifest = snapshot(connection, snapshot_id)
    prior = connection.execute("SELECT i.snapshot_id FROM replica_intents i WHERE i.binding_id=? ORDER BY i.sequence", (binding_id,)).fetchall()
    expected = sum(snapshot(connection, item[0], verify=False)[1]["workflow"]["id"] == manifest["workflow"]["id"] for item in prior)
    key = "intent-" + hashlib.sha256((binding_id + ":" + snapshot_id).encode()).hexdigest()
    connection.execute("INSERT INTO replica_intents(id,snapshot_id,binding_id,expected_revision,target) VALUES(?,?,?,?,?)", (key, snapshot_id, binding_id, expected, c.canonical(target)))
    for index, command in enumerate(commands(connection, snapshot_id, target, expected, key)):
        connection.execute("INSERT INTO replica_steps VALUES(?,?,?,?)", (key, index, command["operation_id"], c.canonical(command)))


def confirmed(connection, intent_id, step_index):
    for (raw,) in connection.execute("SELECT value FROM replica_observations WHERE intent_id=? AND step_index=? ORDER BY sequence", (intent_id, step_index)):
        value = c.parse(bytes(raw))["evaluation"]
        if value["outcome"] in ("accepted", "rejected"):
            return value
    return None


def synchronization(connection, snapshot_id):
    items = []
    for key, binding_id in connection.execute("SELECT id,binding_id FROM replica_intents WHERE snapshot_id=? ORDER BY sequence", (snapshot_id,)):
        outcomes = [confirmed(connection, key, index) for (index,) in connection.execute("SELECT step_index FROM replica_steps WHERE intent_id=? ORDER BY step_index", (key,))]
        state = "complete" if all(value and value["outcome"] == "accepted" for value in outcomes) else "conflict" if any(value and value["outcome"] == "rejected" for value in outcomes) else "pending"
        items.append({"intent_id": key, "binding_id": binding_id, "state": state})
    return {"state": "not_configured" if not items else "complete" if all(item["state"] == "complete" for item in items) else "incomplete", "targets": items}


def evaluate(connection, intent_id, index, command, channel, transport):
    prior = confirmed(connection, intent_id, index)
    if transport is None:
        return {"outcome": "unknown", "reason": "response_missing"}
    try:
        native = c.mcp_value(transport)
        if channel == "lookup":
            c.validate("result_replica_operation_get", native)
            require(native["project_ref"] == command["project_ref"] and native["operation_id"] == command["operation_id"],
                    "receipt_mismatch", "Lookup envelope has another project or operation.")
            if native["outcome"] == "unknown":
                require(native["project_ref"] == command["project_ref"] and native["operation_id"] == command["operation_id"], "receipt_mismatch", "Unknown lookup has another scope.")
                return {"outcome": "unknown", "native_result": native}
            result = native["receipt"]
            require(result["accepted"] == (native["outcome"] == "accepted"), "receipt_mismatch", "Lookup outcome contradicts its receipt.")
        else:
            result = native
        c.validate("receipt", result)
        require(not transport.get("isError", False) or result["accepted"] is False, "receipt_mismatch", "Error flag contradicts an accepted receipt.")
        for key in ("project_ref", "operation_id", "command", "expected_revision"):
            require(result[key] == command[key], "receipt_mismatch", "Receipt does not name the persisted original command.")
        for key in ("source_id", "workflow_id", "source_revision"):
            require(result[key] == command["payload"][key], "receipt_mismatch", "Receipt source identity changed.")
        if result["accepted"]:
            require(result["revision"] == command["expected_revision"] + (command["command"] == "replica.activate"), "receipt_mismatch", "Receipt changed the expected remote head.")
        if prior:
            require(result["request_digest"] == prior["native_result"]["request_digest"] and result["accepted"] == prior["native_result"]["accepted"], "receipt_mismatch", "Receipt contradicts already confirmed evidence.")
        if channel == "lookup" and not prior:
            return {"outcome": "observed_accepted" if result["accepted"] else "observed_rejected", "native_result": result, "requires_original_replay": True}
        return {"outcome": "accepted" if result["accepted"] else "rejected", "native_result": result, "server_digest_verification": "host_correlated_not_recomputed"}
    except (RecordError, ImportError, KeyError, TypeError, ValueError) as exc:
        return {"outcome": "unknown", "reason": getattr(exc, "code", "invalid_transport"), "native_transport_retained": True}


def import_git(store, request):
    commit, root = request["source_commit"], request["source_root"]
    require(isinstance(commit, str) and re.fullmatch("[0-9a-f]{40}", commit) is not None, "invalid_input", "Select an exact Git commit.")
    c.path(root)
    require(request["kind"] in ("archive-workflow", "archive-root-index"), "invalid_input", "Git imports require an explicit archive kind.")
    def git(*args):
        result = subprocess.run(["git", "-C", str(store.root), *args], capture_output=True, timeout=30)
        require(result.returncode == 0, "source_unavailable", "Selected Git objects are unavailable.")
        return result.stdout
    require(git("cat-file", "-t", commit).strip() == b"commit", "invalid_input", "Source must be a commit object.")
    rows = git("ls-tree", "-r", "-l", "-z", commit, "--", root).split(b"\0")
    selected, total = [], 0
    for raw in rows:
        if not raw:
            continue
        header, filename = raw.split(b"\t", 1)
        mode, kind, oid, size = header.split()
        name = filename.decode("utf-8")
        require(name.startswith(root + "/"), "invalid_input", "Select one source directory, not a single file.")
        relative = name[len(root) + 1:]
        if request["kind"] == "archive-root-index" and "/" in relative:
            continue
        require(kind == b"blob", "unsupported_capability", "Gitlinks require a separately selected archive mapping.")
        c.path(relative)
        count = int(size)
        require(count <= c.MAX_FILE, "limit_exceeded", "Source file exceeds replica size bound.")
        total += count
        selected.append((relative, mode.decode("ascii"), oid.decode("ascii"), count))
    require(selected and len(selected) <= 1000 and total <= c.MAX_UNIT, "limit_exceeded", "Selected source unit is absent or exceeds bounds.")
    files = []
    for name, mode, oid, count in selected:
        data = git("cat-file", "blob", oid)
        require(len(data) == count, "integrity_error", "Git blob size changed.")
        files.append((name, mode, data))
    view = {"title": "unknown", "status": "unknown", "view_provenance": {"title": "unknown", "status": "unknown"}}
    for name, _, raw in files:
        if name in ("workflow.yaml", "workflow.yml", "workflow.json"):
            if len(raw) > 262144:
                break  # Raw metadata remains archived; its view is unknown.
            try:
                from .common import mapping
                data = mapping(raw, ".json" if name.endswith(".json") else ".yaml")
                for field in ("title", "status"):
                    if isinstance(data.get(field), str) and 0 < len(data[field]) <= 4096:
                        view[field] = data[field]
                        view["view_provenance"][field] = {"file": name, "selector": field}
            except RecordError:
                pass
            break
    return files, view, {"type": "git-snapshot", "source_commit": commit, "source_root": root, "repository_id": store.repository_id}


class SourceStore:
    def __init__(self, root, config):
        from .service import WorkflowRecords
        self.service = WorkflowRecords(root, config)

    def execute(self, request):
        if isinstance(request, dict) and request.get("contract_version") == c.PROFILE2:
            from .source_config import execute
            return execute(self, request)
        operation = request.get("operation") if isinstance(request, dict) else None
        if not isinstance(operation, str) or len(operation) > 64 or not operation.isascii():
            operation = None
        try:
            require(isinstance(request, dict) and request.get("contract_version") == c.PROFILE, "unsupported_version", "Unsupported source-store profile.")
            common = {"contract_version", "operation", "store_ref"}
            inputs = {"source-init": {"operation_id", "schema_version"}, "source-import-git": {"operation_id", "kind", "workflow_id", "source_commit", "source_root"},
                      "replica-bind": {"operation_id", "binding", "new_source_namespace"},
                      "binding-status": {"binding_id"},
                      "binding-disable": {"operation_id", "binding_id", "expected_binding_digest", "expected_snapshot_sequence"}, "source-list": set(), "source-read": {"snapshot_id"},
                      "source-chunk": {"snapshot_id", "path", "index"}, "replica-prepare": {"intent_id"},
                      "replica-observe": {"operation_id", "intent_id", "step_index", "channel", "mcp_result"}, "source-operation": {"operation_id"}}
            require(operation in inputs, "unsupported_capability", "Unknown source-store operation.")
            optional = {"max_output_bytes"} | ({"offset", "limit"} if operation == "source-list" else {"mode"} if operation == "replica-prepare" else set())
            c.fields(request, common | inputs[operation], optional)
            require(len(c.canonical(request)) <= c.MAX_INPUT, "limit_exceeded", "Source-store request exceeds input bound.")
            maximum = c.integer(request.get("max_output_bytes", 1048576), 2048, c.MAX_INPUT)
            ref = StoreRef.parse(request["store_ref"])
            store = self.service.provider(ref)
            require(isinstance(store, SQLiteStore), "unsupported_capability", "Source-store requires the explicit SQLite provider.")
            if operation == "source-init":
                require(request["schema_version"] == c.SCHEMA, "invalid_input", "Fresh schema-2 initialization must be explicit.")
                if store.database.exists():
                    with store.transaction() as (_, meta):
                        schema2(meta)
                result = store.initialize(request, schema=c.SCHEMA)
            else:
                if operation == "source-import-git":
                    # Git reads are outside the write lock; exact committed objects
                    # are immutable. Publication and fixed-target enqueue are atomic.
                    with store.transaction() as (connection, meta):
                        schema2(meta)
                        import_prior = replay(connection, request)
                    if import_prior is None:
                        files, view, source = import_git(store, request)
                write = operation in ("source-import-git", "replica-bind", "replica-observe", "binding-disable")
                with store.transaction(write=write) as (connection, meta):
                    schema2(meta)
                    prior = replay(connection, request) if write else None
                    if prior is not None:
                        result = prior
                    else:
                        if write or operation == "replica-prepare":
                            require(meta["state"] == "active", "store_inactive", "Inactive or retired source stores cannot mutate or prepare dispatch.")
                        if operation == "source-import-git":
                            key = publish(connection, request["kind"], request["workflow_id"], source, view, files)
                            result = receipt(connection, request, {"snapshot_id": key, "synchronization": synchronization(connection, key)})
                        elif operation == "replica-bind":
                            require(meta["schema_version"] in (c.SCHEMA, c.SCHEMA21), "unsupported_capability", "Schema 3 uses workflow-scoped /2 carrier configuration.")
                            target = request["binding"]
                            c.binding(target)
                            require(request["new_source_namespace"] is True, "invalid_input", "Binding requires an explicitly new remote source namespace at head zero.")
                            target_key = c.digest(c.canonical({"project_ref": target["project_ref"], "source_id": target["source_id"]}))
                            require(connection.execute("SELECT 1 FROM source_bindings WHERE id=? OR target_key=?", (target["binding_id"], target_key)).fetchone() is None,
                                    "already_exists", "Bindings are initial-only; replacing a binding or used target namespace is refused.")
                            connection.execute("INSERT INTO source_bindings VALUES(?,?,?)", (target["binding_id"], target_key, c.canonical(target)))
                            for (key,) in connection.execute("SELECT id FROM source_snapshots ORDER BY sequence").fetchall():
                                enqueue(connection, key, target["binding_id"], target)
                            result = receipt(connection, request, {"binding_id": target["binding_id"]})
                        elif operation == "binding-status":
                            result = binding_status(connection, request["binding_id"])
                        elif operation == "binding-disable":
                            require(meta["schema_version"] in (c.SCHEMA, c.SCHEMA21), "unsupported_capability", "Schema 3 retains its explicit configuration owner.")
                            status = binding_status(connection, request["binding_id"])
                            require(status["state"] == "active", "binding_disabled", "The binding is already disabled; replay its original operation.")
                            c.integer(request["expected_snapshot_sequence"], 0)
                            require(request["expected_binding_digest"] == status["binding_digest"] and
                                    request["expected_snapshot_sequence"] == status["snapshot_sequence"],
                                    "revision_conflict", "Binding or atomic snapshot cutoff changed; read binding-status before retry.")
                            meta["schema_version"] = c.SCHEMA21
                            store.save_meta(connection, meta)
                            result = receipt(connection, request, {"operation": "binding-disable", "request": copy.deepcopy(request),
                                "binding_id": request["binding_id"], "binding_digest": status["binding_digest"],
                                "cutoff_sequence": status["snapshot_sequence"]})
                        elif operation == "source-list":
                            offset, limit = c.integer(request.get("offset", 0), 0, MAX_ROWS), c.integer(request.get("limit", 20), 1, 100)
                            rows = connection.execute("SELECT id FROM source_snapshots s WHERE sequence=(SELECT max(sequence) FROM source_snapshots p WHERE p.kind=s.kind AND p.workflow_id=s.workflow_id) ORDER BY sequence LIMIT ? OFFSET ?", (limit + 1, offset)).fetchall()
                            items = [self.read(connection, row[0], False) for row in rows[:limit]]
                            result = {"items": items, "next_offset": offset + limit if len(rows) > limit else None}
                        elif operation == "source-read":
                            result = self.read(connection, request["snapshot_id"], True)
                        elif operation == "source-chunk":
                            row, manifest = snapshot(connection, request["snapshot_id"])
                            c.path(request["path"])
                            index = c.integer(request["index"], 0)
                            found = connection.execute("SELECT b.hash,b.data FROM source_chunks c JOIN source_blobs b ON b.hash=c.hash WHERE c.snapshot_id=? AND c.path=? AND c.chunk_index=?", (row[1], request["path"], index)).fetchone()
                            require(found is not None, "not_found", "Selected exact source chunk is absent (empty files have zero chunks).")
                            result = {"snapshot_id": row[1], "path": request["path"], "index": index, "chunk_hash": found[0], "content_base64": base64.b64encode(bytes(found[1])).decode("ascii")}
                        elif operation == "source-operation":
                            found = connection.execute("SELECT receipt FROM source_operations WHERE id=?", (request["operation_id"],)).fetchone()
                            result = c.parse(bytes(found[0])) if found else {"state": "unknown", "operation_id": request["operation_id"]}
                        elif operation == "replica-prepare":
                            result = self.prepare(connection, request)
                        elif operation == "replica-observe":
                            intent = connection.execute("SELECT snapshot_id FROM replica_intents WHERE id=?", (request["intent_id"],)).fetchone()
                            found = connection.execute("SELECT command FROM replica_steps WHERE intent_id=? AND step_index=?", (request["intent_id"], c.integer(request["step_index"], 0))).fetchone()
                            require(intent is not None and found is not None, "not_found", "Selected persisted replica step is absent.")
                            require(request["channel"] in ("direct", "lookup"), "invalid_input", "Observation channel must be direct or lookup.")
                            evaluation = evaluate(connection, request["intent_id"], request["step_index"], c.parse(bytes(found[0])), request["channel"], request["mcp_result"])
                            value = {"channel": request["channel"], "transport": request["mcp_result"], "evaluation": evaluation}
                            require(len(c.canonical(value)) <= c.MAX_INPUT, "limit_exceeded", "Observation exceeds its retention cell bound.")
                            cursor = connection.execute("INSERT INTO replica_observations(intent_id,step_index,value) VALUES(?,?,?)", (request["intent_id"], request["step_index"], c.canonical(value)))
                            result = receipt(connection, request, {"observation_sequence": cursor.lastrowid, "evaluation": evaluation, "synchronization": synchronization(connection, intent[0])})
            response = {"contract_version": c.PROFILE, "operation": operation, "status": "ok", "local_result": "accepted", "result": result,
                        "limitations": ["host dispatch is explicit; remote digest is not recomputed", "local acceptance and replica completion are distinct"]}
            require(len(encoded(response)) <= maximum, "limit_exceeded", "Whole source-store response exceeds budget; reconcile operation receipt before retry.")
            return response
        except RecordError as exc:
            return {"contract_version": c.PROFILE, "operation": operation, "status": "error", "local_result": "unknown" if exc.code in ("io_error", "storage_error", "limit_exceeded") else "not_applied",
                    "error": {"code": exc.code, "message": exc.message}}
        except (OSError, sqlite3.Error, ValueError, KeyError, TypeError, RecursionError, ImportError):
            return {"contract_version": c.PROFILE, "operation": operation, "status": "error", "local_result": "unknown",
                    "error": {"code": "storage_error", "message": "Source-store operation unavailable; retain original operation and query its receipt."}}

    @staticmethod
    def read(connection, key, include_manifest):
        row, manifest = snapshot(connection, key)
        result = {"snapshot_id": row[1], "kind": row[2], "workflow_id": row[3], "source_revision": row[4],
                  "title": manifest["workflow"]["title"], "original_status": manifest["workflow"]["status"],
                  "remote_workflow_id": manifest["workflow"]["id"], "synchronization": synchronization(connection, key)}
        if include_manifest:
            result["manifest"] = manifest
        return result

    @staticmethod
    def prepare(connection, request):
        intent_id = request["intent_id"]
        intent = connection.execute("SELECT sequence,snapshot_id,binding_id,target FROM replica_intents WHERE id=?", (intent_id,)).fetchone()
        require(intent is not None, "not_found", "Replica intent is absent.")
        mode = request.get("mode", "command")
        require(mode in ("command", "lookup"), "invalid_input", "Dispatch mode must be explicit command or lookup.")
        require(mode == "lookup" or intent[2] not in disabled_bindings(connection),
                "binding_disabled", "Disabled bindings cannot prepare commands; retained lookup and observation remain available.")
        row, manifest = snapshot(connection, intent[1])
        for prior_id, prior_snapshot in connection.execute("SELECT id,snapshot_id FROM replica_intents WHERE binding_id=? AND sequence<? ORDER BY sequence", (intent[2], intent[0])):
            if mode == "command" and snapshot(connection, prior_snapshot, False)[1]["workflow"]["id"] == manifest["workflow"]["id"]:
                require(synchronization(connection, prior_snapshot)["targets"] and all(item["state"] == "complete" for item in synchronization(connection, prior_snapshot)["targets"] if item["binding_id"] == intent[2]),
                        "predecessor_pending", "Prior remote activation for this workflow must be accepted before dispatch.")
        for index, raw in connection.execute("SELECT step_index,command FROM replica_steps WHERE intent_id=? ORDER BY step_index", (intent_id,)):
            known = confirmed(connection, intent_id, index)
            if known and known["outcome"] == "accepted":
                continue
            require(known is None, "replica_conflict", "A durable rejected step blocks delivery; its expected revision was not changed.")
            command = c.parse(bytes(raw))
            c.validate("command", command)
            query = {"service_contract_version": c.NATIVE_PROFILE, "schema_version": "1.0", "project_ref": command["project_ref"], "query": "replica.operation.get", "payload": {"operation_id": command["operation_id"]}}
            mode = request.get("mode", "command")
            require(mode in ("command", "lookup"), "invalid_input", "Dispatch mode must be explicit command or lookup.")
            return {"intent_id": intent_id, "step_index": index, "binding": c.parse(bytes(intent[3])), "command": command,
                    "local_command_fingerprint": c.digest(bytes(raw)), "recovery_query": query,
                    "tool_name": "source_v1_" + (command["command"] if mode == "command" else query["query"]).replace(".", "_"),
                    "request": command if mode == "command" else query, "synchronization": synchronization(connection, intent[1])}
        return {"intent_id": intent_id, "state": "complete", "synchronization": synchronization(connection, intent[1])}
