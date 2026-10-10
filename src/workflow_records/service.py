"""Bounded common entry, provider selection and actual resume consumer."""
from __future__ import annotations

from pathlib import Path

from .contracts import (VERSION, MAX_OUTPUT, RecordError, WorkflowRef, encoded,
                        identifier, integer, require)
from .git_store import GitStore, relative_path

DEFAULT_CONFIG = {
    "contract_version": VERSION, "default_provider": "git",
    "stores": {"git": {"kind": "git", "store_id": "project-workflows", "root": ".dev/workflows"}},
}
LIMITATIONS = ["source-checkout delivery; not an installed skill",
              "single Git working directory; cooperating writers only",
              "no automatic commit, migration, failover or cross-clone transaction"]


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
        require(item["kind"] == "git", "provider_unavailable", "Selected provider is not implemented; no fallback was attempted.")
        return GitStore(self.root, ref.provider_id, ref.store_id, item["root"])

    def capabilities(self):
        return {"contract_version": VERSION, "providers": {
            key: {"kind": item["kind"], "store_id": item["store_id"], "available": item["kind"] == "git",
                  "operations": ["find", "context", "read", "checkpoint", "resume", "validate", "operation"]
                  if item["kind"] == "git" else [], "create": False,
                  "portability": "explicit document reads; export/import/migration are not implemented"}
            for key, item in self.config["stores"].items()}}

    def execute(self, request):
        operation = request.get("operation") if isinstance(request, dict) else None
        try:
            require(isinstance(request, dict), "invalid_input", "Request must be an object.")
            require(request.get("contract_version") == VERSION, "unsupported_version", "Unsupported request contract.")
            require(isinstance(operation, str) and len(operation) <= 32,
                    "invalid_input", "Operation must be a bounded string.")
            require(operation in {"capabilities", "find", "context", "read", "checkpoint", "resume", "validate", "operation"},
                    "unsupported_capability", "Operation is not implemented in this slice.")
            fields = {"contract_version", "operation", "max_output_bytes"}
            fields |= {"capabilities": set(), "find": {"provider_id", "offset", "limit"},
                       "context": {"workflow_ref", "task_limit"}, "read": {"workflow_ref", "document", "revision", "offset", "limit"},
                       "checkpoint": {"workflow_ref", "checkpoint", "operation_id", "expected_revision", "expected_source_head"},
                       "resume": {"workflow_ref", "task_limit", "limit"}, "validate": {"workflow_ref"},
                       "operation": {"workflow_ref", "operation_id"}}[operation]
            require(set(request) <= fields, "invalid_input", "Request contains unknown fields.")
            maximum = integer(request.get("max_output_bytes", MAX_OUTPUT), 2048, MAX_OUTPUT)
            if operation == "capabilities":
                result = self.capabilities()
            elif operation == "find":
                provider_id = request.get("provider_id", self.config["default_provider"])
                ref = WorkflowRef.parse(self.reference("discovery", provider_id))
                result = self.provider(ref).find(integer(request.get("offset", 0), 0, 1000000),
                                                 integer(request.get("limit", 10), 1, 100))
            else:
                ref = WorkflowRef.parse(request.get("workflow_ref"))
                provider = self.provider(ref)
                if operation in ("context", "resume", "validate"):
                    result = provider.context(ref, integer(request.get("task_limit", 16), 1, 128))
                    if operation == "resume":
                        entrypoint = result["entrypoint"]
                        result["plan"] = provider.read(ref, entrypoint["document"], entrypoint["revision"],
                                                       0, integer(request.get("limit", 4096), 1, 32768))
                        # Avoid combining task/context state from two different reads.
                        require(provider.snapshot(ref).revision == result["revision"],
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
                else:
                    result = provider.operation(ref, identifier(request.get("operation_id")))
            response = {"contract_version": VERSION, "operation": operation, "status": "ok", "result": result,
                        "mutation_state": "applied" if operation == "checkpoint" else "none", "limitations": LIMITATIONS}
            # A mutation receipt is small and bounded before any write; query overflow is explicit.
            require(len(encoded(response)) <= maximum, "limit_exceeded", "Result exceeds output limit; request a smaller page.")
            return response
        except RecordError as exc:
            return failure(operation, exc)
        except (OSError, ValueError, TypeError, RecursionError):
            # An IO failure may follow replacement (for example lock release).
            return failure(operation, RecordError("io_error", "Storage operation failed; reconcile operation receipt before retry."),
                           mutation="unknown" if operation == "checkpoint" else "none")


def failure(operation, error, mutation="none"):
    if not isinstance(operation, str) or len(operation) > 32:
        operation = None
    return {"contract_version": VERSION, "operation": operation, "status": "unavailable"
            if error.code == "provider_unavailable" else "error", "mutation_state": mutation,
            "error": {"code": error.code, "message": error.message}}
