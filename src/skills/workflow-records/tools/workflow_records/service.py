"""Bounded common entry, provider selection and actual resume consumer."""
from __future__ import annotations

from pathlib import Path
import sqlite3

from .contracts import (VERSION, MAX_OUTPUT, RecordError, WorkflowRef, StoreRef, encoded,
                        identifier, integer, require, validate_unicode)
from .git_store import GitStore, relative_path
from .sqlite_store import SQLiteStore
from . import backup

DEFAULT_CONFIG = {
    "contract_version": VERSION, "default_provider": "git",
    "stores": {"git": {"kind": "git", "store_id": "project-workflows", "root": ".dev/workflows"}},
}
GIT_OPERATIONS = ["find", "context", "read", "checkpoint", "resume", "validate", "operation"]
LOCAL_OPERATIONS = GIT_OPERATIONS + ["init", "create", "write-document", "export", "preflight", "restore", "deactivate", "activate"]
STORE_OPERATIONS = {"init", "export", "preflight", "restore", "deactivate", "activate"}
MUTATIONS = {"checkpoint", "init", "create", "write-document", "export", "restore", "deactivate", "activate"}
LIMITATIONS = ["cooperating API writers only; no protection against direct storage edits",
              "no automatic commit, migration, failover or cross-clone synchronization"]


class WorkflowRecords:
    def __init__(self, project_root, config=None):
        self.root = Path(project_root).resolve()
        require(self.root.is_dir(), "invalid_input", "Project root is missing.")
        self.config = DEFAULT_CONFIG if config is None else config
        require(isinstance(self.config, dict) and set(self.config) ==
                {"contract_version", "default_provider", "stores"},
                "invalid_input", "Configuration fields are incomplete or unknown.")
        require(self.config["contract_version"] == VERSION, "unsupported_version", "Unsupported configuration contract.")
        stores = self.config["stores"]
        require(isinstance(stores, dict) and 0 < len(stores) <= 16,
                "invalid_input", "Configuration requires bounded named stores.")
        roots = set()
        for provider_id, item in stores.items():
            identifier(provider_id)
            require(isinstance(item, dict) and item.get("kind") in ("git", "local", "remote"),
                    "invalid_input", "Unknown store kind.")
            identifier(item.get("store_id"))
            fields = {"kind", "store_id", "root"} if item["kind"] == "git" else {"kind", "store_id"}
            if item["kind"] == "local" and "database" in item:
                fields |= {"database", "repository_id"}
                require(set(item) in (fields, fields | {"busy_timeout_ms"}), "invalid_input", "Local store fields are incomplete or unknown.")
                identifier(item["repository_id"])
                require(isinstance(item["database"], str), "invalid_input", "Local database path must be text.")
                integer(item.get("busy_timeout_ms", 1000), 0, 10000)
            else:
                require(set(item) == fields, "invalid_input", "Store fields are incomplete or unknown.")
            if item["kind"] == "git":
                relative = str(relative_path(item["root"]))
                # Case-insensitive overlap is conservatively rejected on every host.
                normalized = relative.casefold()
                require(not any(normalized == known or normalized.startswith(known + "/")
                                or known.startswith(normalized + "/") for known in roots),
                        "binding_mismatch", "Git store roots must not overlap.")
                roots.add(normalized)
        identifier(self.config["default_provider"])
        require(self.config["default_provider"] in stores, "invalid_input", "Default provider is not configured.")

    def reference(self, workflow_id, provider_id="git"):
        """Legacy selected Git refs are explicit and never follow the new-record default."""
        identifier(provider_id)
        require(provider_id in self.config["stores"], "provider_unavailable", "Referenced provider is not configured.")
        item = self.config["stores"][provider_id]
        return WorkflowRef(provider_id, item["store_id"], identifier(workflow_id)).as_dict()

    def provider(self, ref):
        item = self.config["stores"].get(ref.provider_id)
        require(item is not None, "provider_unavailable", "Referenced provider is not configured.")
        require(item["store_id"] == ref.store_id, "binding_mismatch", "Store identity changed.")
        if item["kind"] == "git":
            return GitStore(self.root, ref.provider_id, ref.store_id, item["root"])
        if item["kind"] == "local" and "database" in item:
            return SQLiteStore(self.root, ref.provider_id, item)
        raise RecordError("provider_unavailable", "Selected provider is unavailable; no fallback was attempted.")

    def capabilities(self):
        return {"contract_version": VERSION, "providers": {
            key: {"kind": item["kind"], "store_id": item["store_id"], "available": item["kind"] == "git" or (item["kind"] == "local" and "database" in item),
                  "operations": GIT_OPERATIONS if item["kind"] == "git" else LOCAL_OPERATIONS if item["kind"] == "local" and "database" in item else [],
                  "create": item["kind"] == "local" and "database" in item,
                  "portability": "complete bounded export and inactive restore" if item["kind"] == "local" and "database" in item else "explicit document reads; export/import/migration are not implemented",
                  "availability_scope": "implemented adapter/configuration; operation execution checks runtime and store",
                  "concurrency": "serialized local transactions; DELETE journal" if item["kind"] == "local" else "cooperating writers in one working directory"}
            for key, item in self.config["stores"].items()}}

    def execute(self, request):
        operation = request.get("operation") if isinstance(request, dict) else None
        try:
            require(isinstance(request, dict), "invalid_input", "Request must be an object.")
            validate_unicode(request, "invalid_input")
            require(request.get("contract_version") == VERSION, "unsupported_version", "Unsupported request contract.")
            require(isinstance(operation, str) and len(operation) <= 32,
                    "invalid_input", "Operation must be a bounded string.")
            require(operation in set(LOCAL_OPERATIONS) | {"capabilities"},
                    "unsupported_capability", "Operation is not implemented in this slice.")
            fields = {"contract_version", "operation", "max_output_bytes"}
            fields |= {"capabilities": set(), "find": {"provider_id", "offset", "limit"},
                       "context": {"workflow_ref", "task_limit"}, "read": {"workflow_ref", "document", "revision", "offset", "limit"},
                       "checkpoint": {"workflow_ref", "checkpoint", "operation_id", "expected_revision", "expected_source_head"},
                       "resume": {"workflow_ref", "task_limit", "limit"}, "validate": {"workflow_ref"},
                       "operation": {"workflow_ref", "store_ref", "operation_id"},
                       "init": {"store_ref", "operation_id"},
                       "create": {"workflow_ref", "record", "operation_id"},
                       "write-document": {"workflow_ref", "document", "content", "operation_id", "expected_revision", "expected_source_head"},
                       "export": {"store_ref", "destination"},
                       "preflight": {"store_ref", "archive", "archive_digest"},
                       "restore": {"store_ref", "archive", "archive_digest", "operation_id"},
                       "deactivate": {"store_ref", "snapshot_digest", "operation_id"},
                       "activate": {"store_ref", "retired_database", "retirement_seal", "operation_id"}}[operation]
            require(set(request) <= fields, "invalid_input", "Request contains unknown fields.")
            maximum = integer(request.get("max_output_bytes", MAX_OUTPUT), 2048, MAX_OUTPUT)
            if operation == "capabilities":
                result = self.capabilities()
            elif operation == "find":
                provider_id = request.get("provider_id", self.config["default_provider"])
                ref = WorkflowRef.parse(self.reference("discovery", provider_id))
                result = self.provider(ref).find(integer(request.get("offset", 0), 0, 1000000),
                                                 integer(request.get("limit", 10), 1, 100))
            elif operation in STORE_OPERATIONS or (operation == "operation" and "store_ref" in request):
                require("workflow_ref" not in request, "invalid_input", "Select exactly one reference scope.")
                ref = StoreRef.parse(request.get("store_ref"))
                provider = self.provider(ref)
                require(isinstance(provider, SQLiteStore), "unsupported_capability", "This operation requires the local SQLite provider.")
                if operation == "init":
                    result = provider.initialize(request)
                elif operation == "export":
                    result = backup.export_store(provider, request)
                elif operation == "preflight":
                    archive, tables = backup.preflight(request.get("archive"), request.get("archive_digest"))
                    identity = archive["payload"]["identity"]
                    require((identity["provider_id"], identity["store_id"], identity["repository_id"]) ==
                            (provider.provider_id, provider.store_id, provider.repository_id),
                            "binding_mismatch", "Backup identity differs from the selected store.")
                    result = {"valid": True, "snapshot_digest": archive["snapshot_digest"], "counts": {key: len(rows) for key, rows in tables.items()}}
                elif operation == "restore":
                    result = backup.restore_store(provider, request)
                elif operation == "deactivate":
                    result = backup.deactivate(provider, request)
                elif operation == "activate":
                    result = backup.activate(provider, request)
                else:
                    result = provider.operation(None, identifier(request.get("operation_id")))
            else:
                ref = WorkflowRef.parse(request.get("workflow_ref"))
                provider = self.provider(ref)
                if operation in ("context", "resume", "validate"):
                    result = provider.context(ref, integer(request.get("task_limit", 16), 1, 128))
                    if operation == "resume":
                        limit = integer(request.get("limit", 4096), 1, 32768)
                        if isinstance(provider, SQLiteStore):
                            result = provider.resume(ref, integer(request.get("task_limit", 16), 1, 128), limit)
                        else:
                            entrypoint = result["entrypoint"]
                            result["plan"] = provider.read(ref, entrypoint["document"], entrypoint["revision"], 0, limit)
                            require(provider.current_revision(ref) == result["revision"],
                                    "revision_conflict", "Workflow changed while preparing resume context.")
                    elif operation == "validate":
                        require(not result["missing"], "not_found", "Required selected task records are missing.")
                        result = {"valid": True, "workflow_ref": ref.as_dict(), "revision": result["revision"],
                                  "scope": result["validation_scope"]}
                elif operation == "read":
                    result = provider.read(ref, request.get("document"), request.get("revision"),
                                           integer(request.get("offset", 0), 0, 1000000),
                                           integer(request.get("limit", 4096), 1, 32768))
                elif operation == "checkpoint":
                    result = provider.checkpoint(ref, request)
                elif operation in ("create", "write-document"):
                    require(isinstance(provider, SQLiteStore), "unsupported_capability", "This operation requires the local SQLite provider.")
                    result = provider.create(ref, request) if operation == "create" else provider.update(ref, request)
                else:
                    result = provider.operation(ref, identifier(request.get("operation_id")))
            response = {"contract_version": VERSION, "operation": operation, "status": "ok", "result": result,
                        "mutation_state": "applied" if operation in MUTATIONS else "none", "limitations": LIMITATIONS}
            # A mutation receipt is small and bounded before any write; query overflow is explicit.
            require(len(encoded(response)) <= maximum, "limit_exceeded", "Result exceeds output limit; request a smaller page.")
            return response
        except RecordError as exc:
            return failure(operation, exc, mutation=getattr(exc, "mutation_state", None) or
                           ("unknown" if isinstance(operation, str) and operation in MUTATIONS and exc.code == "storage_error" else "none"))
        except (OSError, ValueError, TypeError, RecursionError, sqlite3.Error):
            # An IO failure may follow replacement (for example lock release).
            return failure(operation, RecordError("io_error", "Storage operation failed; reconcile operation receipt before retry."),
                           mutation="unknown" if isinstance(operation, str) and operation in MUTATIONS else "none")


def failure(operation, error, mutation="none"):
    if not isinstance(operation, str) or len(operation) > 32 or not operation.isascii():
        operation = None
    return {"contract_version": VERSION, "operation": operation, "status": "unavailable"
            if error.code == "provider_unavailable" else "error", "mutation_state": mutation,
            "error": {"code": error.code, "message": error.message}}
