"""Explicit repository-bound local store; cooperating writers use short transactions."""
from __future__ import annotations

import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import uuid

from .contracts import (MAX_FILE, MAX_TASKS, RecordError, WorkflowRef, decode_json,
                        digest, encoded, identifier, integer, require)
from .common import (clipped, relative_path, required_strings, source_head, text,
                     validate_checkpoint)

SCHEMA = "workflow-sqlite/1"
MAX_BLOBS_BYTES = 32 * 1024 * 1024
MAX_REVISIONS = 256
MAX_WORKFLOWS = 256
MAX_WORKFLOW_OPERATIONS = 4096
MAX_ADMIN_OPERATIONS = 128
DDL = (
    "CREATE TABLE store_meta (id INTEGER PRIMARY KEY CHECK(id=1), value BLOB NOT NULL)",
    "CREATE TABLE workflows (id TEXT PRIMARY KEY, revision TEXT NOT NULL)",
    "CREATE TABLE revisions (workflow_id TEXT NOT NULL REFERENCES workflows(id), revision TEXT NOT NULL, parent TEXT, state BLOB NOT NULL, PRIMARY KEY(workflow_id, revision))",
    "CREATE TABLE blobs (hash TEXT PRIMARY KEY, data BLOB NOT NULL)",
    "CREATE TABLE operations (workflow_id TEXT NOT NULL, id TEXT NOT NULL, request_digest TEXT NOT NULL, receipt BLOB NOT NULL, event BLOB NOT NULL, PRIMARY KEY(workflow_id,id))",
)


def absolute_file(value):
    require(isinstance(value, str) and value and Path(value).is_absolute(),
            "unsafe_path", "Database/archive requires an explicit absolute local path.")
    raw = Path(value)
    require(not str(raw).startswith(("\\\\", "//")), "unsupported_topology", "Network paths are unsupported.")
    for candidate in [*reversed(raw.parents), raw]:
        if candidate.exists() or candidate.is_symlink():
            info = candidate.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "unsafe_path", "Symlinks and reparse points are unsupported.")
    if os.name == "nt":
        import ctypes
        require(ctypes.windll.kernel32.GetDriveTypeW(str(raw.anchor)) != 4,
                "unsupported_topology", "Mapped network drives are unsupported.")
    return raw.resolve()


def repository_binding(root):
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RecordError("provider_unavailable", "Repository identity is unavailable.") from exc
    require(result.returncode == 0, "provider_unavailable", "A Git repository is required for source binding.")
    common = Path(result.stdout.decode("utf-8").strip()).resolve()
    require(common.is_dir(), "provider_unavailable", "Repository identity is unavailable.")
    return str(common)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def request_digest(request):
    # Transport paging/output bounds do not change the operation identity.
    return digest(encoded({key: value for key, value in request.items() if key != "max_output_bytes"}))


class SQLiteStore:
    def __init__(self, root, provider_id, descriptor):
        self.root = Path(root).resolve()
        self.provider_id = provider_id
        self.store_id = identifier(descriptor["store_id"])
        self.repository_id = identifier(descriptor["repository_id"])
        self.database = absolute_file(descriptor["database"])
        self.timeout = integer(descriptor.get("busy_timeout_ms", 1000), 0, 10000)
        self.binding = repository_binding(self.root)
        require(not self.database.is_relative_to(self.root) and
                not self.database.is_relative_to(Path(self.binding).parent),
                "unsafe_path", "The active database must be outside the repository and its worktrees.")

    def _open(self):
        absolute_file(str(self.database))
        require(self.database.is_file(), "provider_unavailable", "Local store is not initialized; no fallback was attempted.")
        connection = sqlite3.connect(self.database.as_uri() + "?mode=rw", uri=True,
                                     timeout=self.timeout / 1000, isolation_level=None)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA trusted_schema=OFF")
            connection.execute("PRAGMA synchronous=FULL")
            require(connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete",
                    "unsupported_topology", "Only rollback DELETE journal is supported.")
        except BaseException:
            connection.close()
            raise
        return connection

    @contextmanager
    def transaction(self, write=False, active=False):
        connection = None
        try:
            connection = self._open()
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            meta = self.meta(connection)
            if active:
                require(meta["state"] == "active", "store_inactive", "Writes require the sole active store.")
            yield connection, meta
            connection.commit()
        except sqlite3.Error as exc:
            if connection is not None:
                connection.rollback()
            code = getattr(exc, "sqlite_errorcode", 0) & 0xff
            if code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                raise RecordError("writer_busy", "Local store is busy; retry with the same operation identity.") from exc
            raise RecordError("storage_error", "Local database failed integrity or IO checks; reconcile operation results.") from exc
        finally:
            if connection is not None:
                connection.close()

    def meta(self, connection):
        row = connection.execute("SELECT value FROM store_meta WHERE id=1").fetchone()
        require(row is not None, "malformed_record", "Store identity is missing.")
        value = decode_json(bytes(row[0]))
        require(value.get("schema_version") == SCHEMA, "unsupported_version", "Unsupported local schema.")
        require((value.get("provider_id"), value.get("store_id"), value.get("repository_id"), value.get("repository_binding")) ==
                (self.provider_id, self.store_id, self.repository_id, self.binding),
                "binding_mismatch", "Local store belongs to a different repository or provider.")
        require(value.get("state") in ("active", "inactive", "retired"), "malformed_record", "Unknown store state.")
        return value

    @staticmethod
    def save_meta(connection, meta):
        connection.execute("UPDATE store_meta SET value=? WHERE id=1", (encoded(meta),))

    def initialize(self, request):
        op = identifier(request.get("operation_id"))
        if self.database.exists():
            with self.transaction() as (connection, _):
                prior = self.replay(connection, "", op, request)
                require(prior is not None, "already_exists", "Initialization never replaces an existing store.")
                return prior
        require(self.database.parent.is_dir(), "not_found", "Select an existing persistent parent directory.")
        # Exclusive creation reserves only this exact new target, never another file.
        try:
            fd = os.open(self.database, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise RecordError("writer_busy", "Another initializer reserved the database.") from exc
        os.close(fd)
        connection = None
        try:
            connection = sqlite3.connect(self.database, isolation_level=None)
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE")
            for statement in DDL:
                connection.execute(statement)
            meta = {"schema_version": SCHEMA, "provider_id": self.provider_id, "store_id": self.store_id,
                    "repository_id": self.repository_id, "repository_binding": self.binding,
                    "instance_id": str(uuid.uuid4()), "state": "active", "origin": None, "retirement": None}
            connection.execute("INSERT INTO store_meta VALUES(1,?)", (encoded(meta),))
            receipt = {"state": "applied", "operation_id": op, "instance_id": meta["instance_id"], "store_state": "active", "replayed": False}
            self.save_operation(connection, "", request, receipt)
            connection.commit()
            return receipt
        except BaseException:
            if connection is not None:
                connection.close()
                connection = None
            self.database.unlink(missing_ok=True)
            raise
        finally:
            if connection is not None:
                connection.close()

    def check_ref(self, ref):
        require(ref.provider_id == self.provider_id and ref.store_id == self.store_id,
                "binding_mismatch", "Reference differs from selected local store.")

    @staticmethod
    def replay(connection, scope, op, request):
        row = connection.execute("SELECT request_digest,receipt FROM operations WHERE workflow_id=? AND id=?", (scope, op)).fetchone()
        if row is None:
            return None
        require(row[0] == request_digest(request), "operation_id_conflict", "Operation ID already names different content.")
        receipt = decode_json(bytes(row[1]))
        receipt["replayed"] = True
        return receipt

    @staticmethod
    def save_operation(connection, scope, request, receipt):
        count = connection.execute("SELECT count(*) FROM operations WHERE (workflow_id='')=?", (not bool(scope),)).fetchone()[0]
        require(count < (MAX_WORKFLOW_OPERATIONS if scope else MAX_ADMIN_OPERATIONS),
                "limit_exceeded", "Operation retention is full; no history was removed.")
        event = {"operation": request["operation"], "operation_id": request["operation_id"], "recorded_at": now()}
        connection.execute("INSERT INTO operations VALUES(?,?,?,?,?)",
                           (scope, request["operation_id"], request_digest(request), encoded(receipt), encoded(event)))
        # Check the actual portable representation while the write can still
        # roll back. Normal history cannot consume lifecycle transfer headroom.
        from .backup import check_capacity
        check_capacity(connection)

    def _state(self, connection, ref, revision=None):
        self.check_ref(ref)
        current = connection.execute("SELECT revision FROM workflows WHERE id=?", (ref.workflow_id,)).fetchone()
        require(current is not None, "not_found", "Workflow is absent from the selected store.")
        selected = current[0] if revision is None else revision
        row = connection.execute("SELECT state FROM revisions WHERE workflow_id=? AND revision=?", (ref.workflow_id, selected)).fetchone()
        require(row is not None, "not_found", "Workflow revision is not retained.")
        raw = bytes(row[0])
        require(digest(raw) == selected, "malformed_record", "Revision digest mismatch.")
        return decode_json(raw), selected

    def current_revision(self, ref):
        with self.transaction() as (connection, _):
            return self._state(connection, ref)[1]

    @staticmethod
    def blob(connection, hash_value):
        row = connection.execute("SELECT data FROM blobs WHERE hash=?", (hash_value,)).fetchone()
        require(row is not None, "malformed_record", "A retained blob is missing.")
        raw = bytes(row[0])
        require(len(raw) <= MAX_FILE and digest(raw) == hash_value, "malformed_record", "Blob digest or size mismatch.")
        return raw

    @staticmethod
    def put_blob(connection, raw):
        require(len(raw) <= MAX_FILE, "limit_exceeded", "A document or attachment exceeds the byte limit.")
        key = digest(raw)
        if connection.execute("SELECT 1 FROM blobs WHERE hash=?", (key,)).fetchone() is None:
            size = connection.execute("SELECT coalesce(sum(length(data)),0) FROM blobs").fetchone()[0]
            require(size + len(raw) <= MAX_BLOBS_BYTES, "limit_exceeded", "Blob retention is full; no history was removed.")
            connection.execute("INSERT INTO blobs VALUES(?,?)", (key, raw))
        return key

    @staticmethod
    def validate_record(record):
        require(isinstance(record, dict) and set(record) == {"metadata", "tasks", "entrypoint", "documents", "attachments"},
                "invalid_input", "Local record requires metadata, tasks, entrypoint, documents and attachments.")
        metadata = record["metadata"]
        require(isinstance(metadata, dict), "invalid_input", "Workflow metadata must be an object.")
        required_strings(metadata, ("title", "status", "owner_skill", "authority"))
        tasks = record["tasks"]
        require(isinstance(tasks, list) and 0 < len(tasks) <= MAX_TASKS, "invalid_input", "A bounded nonempty task list is required.")
        ids = set()
        for task in tasks:
            require(isinstance(task, dict), "invalid_input", "Task must be an object.")
            task_id = identifier(task.get("task_id"))
            required_strings(task, ("status", "title"))
            require(task_id not in ids, "invalid_input", "Task identity is duplicated.")
            ids.add(task_id)
        paths = set()
        for kind in ("documents", "attachments"):
            values = record[kind]
            require(isinstance(values, dict) and len(values) <= 128, "limit_exceeded", "Expected a bounded document map.")
            for name, value in values.items():
                relative_path(name)
                require(not name.casefold().startswith(".workflow-records/"), "invalid_input", "Internal checkpoint document names are reserved.")
                require(name.casefold() not in paths and isinstance(value, str), "invalid_input", "Document identity is duplicate or content is invalid.")
                paths.add(name.casefold())
        require(record["entrypoint"] in record["documents"], "invalid_input", "Entrypoint must name a supplied text document.")

    def create(self, ref, request):
        self.check_ref(ref)
        self.validate_record(request.get("record"))
        op = identifier(request.get("operation_id"))
        with self.transaction(write=True) as (connection, meta):
            prior = self.replay(connection, ref.workflow_id, op, request)
            if prior is not None:
                return prior
            require(meta["state"] == "active", "store_inactive", "Create requires the active store.")
            require(connection.execute("SELECT 1 FROM workflows WHERE id=?", (ref.workflow_id,)).fetchone() is None,
                    "already_exists", "Workflow already exists.")
            require(connection.execute("SELECT count(*) FROM workflows").fetchone()[0] < MAX_WORKFLOWS,
                    "limit_exceeded", "Workflow capacity reached.")
            record = request["record"]
            state = {"metadata": record["metadata"], "tasks": record["tasks"], "entrypoint": record["entrypoint"],
                     "documents": {}, "attachments": {}, "checkpoint": None}
            for kind in ("documents", "attachments"):
                for name, value in record[kind].items():
                    try:
                        raw = value.encode("utf-8") if kind == "documents" else base64.b64decode(value, validate=True)
                    except ValueError as exc:
                        raise RecordError("invalid_input", "Attachment must be strict base64.") from exc
                    if kind == "documents":
                        text(raw)
                    state[kind][name] = self.put_blob(connection, raw)
            revision = self.save_revision(connection, ref, state, None, request)
            receipt = {"state": "applied", "operation_id": op, "workflow_ref": ref.as_dict(), "revision": revision, "replayed": False}
            self.save_operation(connection, ref.workflow_id, request, receipt)
            return receipt

    @staticmethod
    def save_revision(connection, ref, state, previous, request):
        count = connection.execute("SELECT count(*) FROM revisions WHERE workflow_id=?", (ref.workflow_id,)).fetchone()[0]
        require(count < MAX_REVISIONS, "limit_exceeded", "Revision retention is full; no history was removed.")
        state["event"] = {"operation_id": request["operation_id"], "operation": request["operation"], "recorded_at": now(), "parent": previous}
        raw = encoded(state)
        require(len(raw) <= MAX_FILE, "limit_exceeded", "Workflow state exceeds the byte limit.")
        revision = digest(raw)
        connection.execute("INSERT INTO workflows VALUES(?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision", (ref.workflow_id, revision))
        connection.execute("INSERT INTO revisions VALUES(?,?,?,?)", (ref.workflow_id, revision, previous, raw))
        return revision

    def checkpoint(self, ref, request):
        validate_checkpoint(request.get("checkpoint"))
        return self.update(ref, request)

    def update(self, ref, request):
        op = identifier(request.get("operation_id"))
        with self.transaction(write=True) as (connection, meta):
            prior = self.replay(connection, ref.workflow_id, op, request)
            if prior is not None:
                return prior
            require(meta["state"] == "active", "store_inactive", "Updates require the active store.")
            state, previous = self._state(connection, ref)
            require(request.get("expected_revision") == previous, "revision_conflict", "Workflow inputs changed; read context again.")
            head = source_head(self.root)
            require(request.get("expected_source_head") == head, "source_conflict", "Git HEAD changed; reconcile the source first.")
            if request["operation"] == "checkpoint":
                state["checkpoint"] = {"operation_id": op, "recorded_at": now(), "value": request["checkpoint"]}
            else:
                name = str(relative_path(request.get("document")))
                content = request.get("content")
                require(name in state["documents"] and isinstance(content, str), "invalid_input", "Select an existing text document and replacement text.")
                raw = content.encode("utf-8")
                text(raw)
                state["documents"][name] = self.put_blob(connection, raw)
            revision = self.save_revision(connection, ref, state, previous, request)
            receipt = {"state": "applied", "operation_id": op, "workflow_ref": ref.as_dict(), "revision": revision,
                       "checkpoint_revision": revision, "source_head": head, "replayed": False}
            self.save_operation(connection, ref.workflow_id, request, receipt)
            require(source_head(self.root) == head, "source_conflict", "Git HEAD changed before the local commit.")
            return receipt

    def find(self, offset, limit):
        with self.transaction() as (connection, _):
            rows = connection.execute("SELECT id FROM workflows ORDER BY id LIMIT ? OFFSET ?", (limit + 1, offset)).fetchall()
            result = []
            for (workflow_id,) in rows[:limit]:
                ref = WorkflowRef(self.provider_id, self.store_id, workflow_id)
                state, revision = self._state(connection, ref)
                result.append({"workflow_ref": ref.as_dict(), "title": clipped(state["metadata"]["title"], 256),
                               "status": state["metadata"]["status"], "revision": revision})
            return {"items": result, "complete": True, "next_offset": offset + limit if len(rows) > limit else None}

    def context(self, ref, task_limit):
        with self.transaction() as (connection, meta):
            return self._context(connection, meta, ref, task_limit)

    def _context(self, connection, meta, ref, task_limit):
        state, revision = self._state(connection, ref)
        self.blob(connection, state["documents"][state["entrypoint"]])
        metadata = state["metadata"]
        last = state["checkpoint"]
        checkpoint = None if last is None else {"operation_id": last["operation_id"], "recorded_at": last["recorded_at"],
                "summary": clipped(last["value"]["summary"], 1024), "next_action": clipped(last["value"]["next_action"], 1024),
                "document": ".workflow-records/checkpoint.json", "details_loaded": False}
        return {"workflow_ref": ref.as_dict(), "revision": revision, "source_head": source_head(self.root),
                "title": clipped(metadata["title"], 512), "status": metadata["status"], "owner_skill": metadata["owner_skill"],
                "authority": clipped(metadata["authority"], 1024),
                "tasks": [{"task_id": task["task_id"], "status": task["status"], "title": clipped(task["title"], 256)}
                          for task in state["tasks"][:task_limit]],
                "tasks_truncated": len(state["tasks"]) > task_limit, "missing": [], "store_state": meta["state"],
                "entrypoint": {"document": state["entrypoint"], "revision": state["documents"][state["entrypoint"]]},
                "checkpoint": checkpoint, "documents_loaded": False,
                "validation_scope": "local identity, immutable state and selected document; no lifecycle acceptance"}

    def read(self, ref, document, revision, offset, limit):
        with self.transaction() as (connection, _):
            return self._read(connection, ref, document, revision, offset, limit)

    def _read(self, connection, ref, document, revision, offset, limit):
        relative_path(document)
        state, _ = self._state(connection, ref)
        if document == ".workflow-records/checkpoint.json":
            require(state["checkpoint"] is not None, "not_found", "No checkpoint is retained.")
            raw = encoded(state["checkpoint"])
            require(revision is None or revision == digest(raw), "revision_conflict", "Checkpoint document changed.")
        else:
            key = state["documents"].get(document)
            if revision is not None and revision != key:
                # Only versions linked to this exact workflow/document are addressable.
                historical = connection.execute("SELECT state FROM revisions WHERE workflow_id=?", (ref.workflow_id,))
                require(any(decode_json(bytes(row[0]))["documents"].get(document) == revision for row in historical),
                        "revision_conflict", "Document revision is not retained for this workflow.")
                key = revision
            require(key is not None, "not_found", "Text document is absent.")
            raw = self.blob(connection, key)
        content = text(raw)
        return {"workflow_ref": ref.as_dict(), "document": document, "revision": digest(raw), "encoding": "utf-8",
                "content": content[offset:offset + limit], "total_characters": len(content), "offset": offset,
                "truncated": offset > 0 or offset + limit < len(content), "next_offset": offset + limit if offset + limit < len(content) else None}

    def resume(self, ref, task_limit, limit):
        with self.transaction() as (connection, meta):
            context = self._context(connection, meta, ref, task_limit)
            entry = context["entrypoint"]
            context["plan"] = self._read(connection, ref, entry["document"], entry["revision"], 0, limit)
            return context

    def operation(self, ref, operation_id):
        scope = "" if ref is None else ref.workflow_id
        if ref is not None:
            self.check_ref(ref)
        with self.transaction() as (connection, _):
            row = connection.execute("SELECT receipt FROM operations WHERE workflow_id=? AND id=?", (scope, operation_id)).fetchone()
            if row is not None:
                return decode_json(bytes(row[0]))
        return {"state": "unknown", "operation_id": operation_id, "reason": "No retained receipt; absence does not prove that a write failed."}
