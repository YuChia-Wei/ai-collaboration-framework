"""Current locator/task format, with additive single-file checkpoints.

No Git mutation, cross-clone transaction, legacy migration or automatic recovery.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile

import yaml

from .contracts import (VERSION, MAX_FILE, MAX_OPERATIONS, MAX_TASKS, RecordError,
                        WorkflowRef, decode_json, digest, encoded, identifier,
                        require, timestamp, validate_unicode)


from .common import (RecordLoader, mapping, relative_path, contained, read_bytes,
                     text, required_strings, clipped, validate_checkpoint, source_head)


@dataclass
class Snapshot:
    ref: WorkflowRef
    locator: dict
    artifact: Path
    tasks: list
    journal: dict
    files: dict
    revision: str


class GitStore:
    def __init__(self, root, provider_id, store_id, locator_root):
        self.root = Path(root).resolve()
        self.provider_id = provider_id
        self.store_id = store_id
        self.locator_root = str(relative_path(locator_root))
        self.directory = contained(self.root, self.locator_root)

    def source_head(self):
        return source_head(self.root)

    def current_revision(self, ref):
        return self.snapshot(ref).revision

    def snapshot(self, ref):
        require(ref.provider_id == self.provider_id and ref.store_id == self.store_id,
                "binding_mismatch", "Reference differs from selected store.")
        files = {}

        def load(path):
            relative = path.relative_to(self.root).as_posix()
            raw = read_bytes(contained(self.root, relative))
            files[relative] = raw
            return raw

        locator_path = contained(self.root, f"{self.locator_root}/{ref.workflow_id}/workflow.yaml")
        locator = mapping(load(locator_path), ".yaml")
        require(locator.get("schema_version") == "1.0", "unsupported_version",
                "Only workflow locator schema 1.0 is supported.")
        require(locator.get("lifecycle_contract", "1.0") == "1.0", "unsupported_version",
                "Unknown lifecycle contract.")
        required_strings(locator, ("workflow_id", "workflow_kind", "title", "owner_skill", "status",
                                   "artifact_root", "entrypoint", "created_at", "updated_at",
                                   "template_source", "template_version", "branch", "base_branch"))
        require(locator["workflow_id"] == ref.workflow_id, "malformed_record", "Locator identity mismatch.")
        timestamp(locator["created_at"])
        timestamp(locator["updated_at"])
        artifact = contained(self.root, locator["artifact_root"])
        require(artifact.is_dir(), "not_found", "Artifact root is missing.")
        text(load(contained(artifact, locator["entrypoint"])))
        task_dir = contained(artifact, "tasks")
        paths = list(task_dir.iterdir()) if task_dir.is_dir() else []
        # The selected format uses direct tasks/*.json|yaml|yml, not a history scan.
        paths = sorted(p for p in paths if p.suffix in (".json", ".yaml", ".yml"))
        require(len(paths) <= MAX_TASKS, "limit_exceeded", "Too many tasks for this slice.")
        tasks, task_ids = [], set()
        for path in paths:
            task = mapping(load(path), path.suffix)
            required_strings(task, ("task_id", "workflow_id", "owner_skill", "status", "created_at",
                                    "updated_at", "template_source", "template_version"))
            identifier(task["task_id"])
            require(task["workflow_id"] == ref.workflow_id and task["task_id"] not in task_ids,
                    "malformed_record", "Task relationship is invalid or duplicated.")
            timestamp(task["created_at"])
            timestamp(task["updated_at"])
            task_ids.add(task["task_id"])
            tasks.append((path.relative_to(artifact).as_posix(), task))
        journal = {"contract_version": VERSION, "workflow_ref": ref.as_dict(),
                   "locator_root": self.locator_root, "operations": []}
        checkpoint_path = contained(artifact, ".workflow-records/checkpoint.json")
        if checkpoint_path.exists():
            journal = mapping(load(checkpoint_path), ".json")
            require(journal.get("contract_version") == VERSION, "unsupported_version", "Unknown checkpoint version.")
            require(journal.get("workflow_ref") == ref.as_dict() and
                    journal.get("locator_root") == self.locator_root, "binding_mismatch",
                    "Stored checkpoint binding differs from selected store.")
            operations = journal.get("operations")
            require(isinstance(operations, list) and 0 < len(operations) <= MAX_OPERATIONS,
                    "malformed_record", "Invalid operation journal.")
            operation_ids = set()
            for entry in operations:
                require(isinstance(entry, dict), "malformed_record", "Invalid operation entry.")
                required_strings(entry, ("operation_id", "request_digest", "previous_revision", "source_head", "recorded_at"))
                identifier(entry["operation_id"])
                require(entry["operation_id"] not in operation_ids, "malformed_record", "Duplicate operation identity.")
                operation_ids.add(entry["operation_id"])
                timestamp(entry["recorded_at"])
                self.validate_checkpoint(entry.get("checkpoint"))
        revision = digest(encoded({key: digest(value) for key, value in sorted(files.items())}))
        return Snapshot(ref, locator, artifact, tasks, journal, files, revision)

    def find(self, offset, limit):
        self.source_head()
        if not self.directory.exists():
            raise RecordError("not_found", "Selected locator root does not exist.")
        folders = sorted(p.name for p in self.directory.iterdir() if p.is_dir())
        rows = []
        for name in folders[offset:offset + limit]:
            try:
                ref = WorkflowRef(self.provider_id, self.store_id, identifier(name))
                snapshot = self.snapshot(ref)
                rows.append({"workflow_ref": ref.as_dict(), "title": clipped(snapshot.locator["title"], 256),
                             "status": snapshot.locator["status"], "revision": snapshot.revision})
            except RecordError as exc:
                rows.append({"workflow_id": name, "error": {"code": exc.code, "message": exc.message}})
        return {"items": rows, "complete": not any("error" in row for row in rows),
                "next_offset": offset + limit if offset + limit < len(folders) else None}

    def context(self, ref, task_limit):
        snapshot = self.snapshot(ref)
        locator = snapshot.locator
        tasks = [{"task_id": task["task_id"], "status": task["status"],
                  "title": clipped(task.get("title", task["task_id"]), 256), "document": path}
                 for path, task in snapshot.tasks[:task_limit]]
        entrypoint = locator["entrypoint"]
        raw = snapshot.files[(snapshot.artifact / entrypoint).relative_to(self.root).as_posix()]
        last = snapshot.journal["operations"][-1] if snapshot.journal["operations"] else None
        checkpoint = None if last is None else {
            "operation_id": last["operation_id"], "recorded_at": last["recorded_at"],
            "summary": clipped(last["checkpoint"]["summary"], 1024),
            "next_action": clipped(last["checkpoint"]["next_action"], 1024),
            "document": ".workflow-records/checkpoint.json", "details_loaded": False}
        return {"workflow_ref": ref.as_dict(), "revision": snapshot.revision, "source_head": self.source_head(),
                "title": clipped(locator["title"], 512), "status": locator["status"],
                "owner_skill": locator["owner_skill"], "authority": clipped(locator.get("authority", ""), 1024),
                "tasks": tasks, "tasks_truncated": len(tasks) < len(snapshot.tasks),
                "missing": ["tasks"] if not snapshot.tasks else [],
                "entrypoint": {"document": entrypoint, "revision": digest(raw)},
                "checkpoint": checkpoint, "documents_loaded": False,
                "validation_scope": "locator, entrypoint, direct tasks and optional checkpoint; no lifecycle acceptance"}

    def read(self, ref, document, revision, offset, limit):
        snapshot = self.snapshot(ref)
        raw = read_bytes(contained(snapshot.artifact, document))
        actual = digest(raw)
        require(revision is None or revision == actual, "revision_conflict", "Document revision changed.")
        content = text(raw)
        return {"workflow_ref": ref.as_dict(), "document": document, "revision": actual,
                "encoding": "utf-8", "content": content[offset:offset + limit],
                "total_characters": len(content), "offset": offset,
                "truncated": offset > 0 or offset + limit < len(content),
                "next_offset": offset + limit if offset + limit < len(content) else None}

    validate_checkpoint = staticmethod(validate_checkpoint)

    @contextmanager
    def writer(self, artifact):
        directory = contained(artifact, ".workflow-records")
        directory.mkdir(exist_ok=True)
        lock = contained(directory, "writer.lock")
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise RecordError("writer_busy", "Writer lock exists; reconcile its owner before manual recovery.") from exc
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded({"pid": os.getpid()}))
            yield
        finally:
            lock.unlink()

    def checkpoint(self, ref, request):
        self.validate_checkpoint(request.get("checkpoint"))
        operation_id = identifier(request.get("operation_id"))
        expected = request.get("expected_revision")
        expected_source = request.get("expected_source_head")
        require(isinstance(expected, str) and expected.startswith("sha256:") and
                isinstance(expected_source, str) and expected_source,
                "invalid_input", "Checkpoint requires expected_revision and expected_source_head.")
        request_digest = digest(encoded({key: request[key] for key in
            ("checkpoint", "operation_id", "expected_revision", "expected_source_head")}))
        original = self.snapshot(ref)
        temporary = None
        with self.writer(original.artifact):
            snapshot = self.snapshot(ref)
            for entry in snapshot.journal["operations"]:
                if entry["operation_id"] == operation_id:
                    require(entry["request_digest"] == request_digest, "operation_id_conflict", "Operation ID already names a different request.")
                    return self.receipt(entry, replayed=True)
            require(snapshot.revision == expected, "revision_conflict", "Workflow inputs changed; read context again.")
            require(self.source_head() == expected_source, "source_conflict", "Git HEAD changed; reconcile the source first.")
            require(snapshot.tasks, "not_found", "Selected task format is missing; checkpoint is refused.")
            require(len(snapshot.journal["operations"]) < MAX_OPERATIONS, "limit_exceeded", "Operation retention is full; no history was removed.")
            entry = {"operation_id": operation_id, "request_digest": request_digest,
                     "previous_revision": expected, "source_head": expected_source,
                     "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "checkpoint": request["checkpoint"]}
            snapshot.journal["operations"].append(entry)
            raw = encoded(snapshot.journal)
            require(len(raw) <= MAX_FILE, "limit_exceeded", "Checkpoint history is full; no history was removed.")
            destination = contained(snapshot.artifact, ".workflow-records/checkpoint.json")
            try:
                fd, name = tempfile.mkstemp(prefix="checkpoint-", suffix=".tmp", dir=destination.parent)
                temporary = Path(name)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
                require(self.snapshot(ref).revision == expected and self.source_head() == expected_source,
                        "revision_conflict", "Inputs changed before replacement.")
                os.replace(temporary, destination)
                temporary = None
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            return self.receipt(entry, replayed=False)

    @staticmethod
    def receipt(entry, replayed=False):
        return {"state": "applied", "operation_id": entry["operation_id"],
                "checkpoint_revision": digest(encoded(entry)), "source_head": entry["source_head"],
                "replayed": replayed}

    def operation(self, ref, operation_id):
        snapshot = self.snapshot(ref)
        for entry in snapshot.journal["operations"]:
            if entry["operation_id"] == operation_id:
                return self.receipt(entry)
        return {"state": "unknown", "operation_id": operation_id,
                "reason": "No retained receipt; absence does not prove that a write failed."}
