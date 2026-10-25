#!/usr/bin/env python3
"""Explicit schema-2 local source snapshots and replica host bridge; no dispatch."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
runtime_root = Path(__file__).resolve().parent
sys.path.insert(0, str(runtime_root))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args(argv)
    try:
        # Fail before import rather than resolving a namespace/ambient package
        # when a declared local initializer or shared runtime member is absent.
        for member in ("__init__", "contracts", "common", "git_store", "sqlite_store", "backup", "service",
                       "source_contract", "source_store", "source_backup", "board_query", "board_command"):
            local = runtime_root / "workflow_records" / (member + ".py")
            if not local.is_file() or local.is_symlink():
                raise ImportError("Declared local source-store runtime is incomplete")
        for member in ("source-replica-v1.schema.json", "board-collaboration-v2.schema.json"):
            local = runtime_root.parent / "schemas" / member
            if not local.is_file() or local.is_symlink():
                raise ImportError("Declared local schema is missing")
        import yaml
        import jsonschema
        version = tuple(int(part) for part in importlib.metadata.version("jsonschema").split(".")[:2])
        if not (3, 11) <= sys.version_info[:2] < (4, 0) or yaml.__version__.split(".")[0] != "6" or not (4, 26) <= version < (5, 0):
            raise ImportError("Selected source-store runtime version is unavailable")
        from workflow_records import source_contract as c
        from workflow_records.source_store import SourceStore
        from workflow_records.contracts import RecordError, encoded
    except (ImportError, ValueError):
        print(json.dumps({"contract_version": "workflow-records/source-store/1", "status": "unavailable", "local_result": "unknown",
                          "error": {"code": "provider_unavailable", "message": "Requires Python 3.11+, PyYAML 6, jsonschema 4.26+ and the complete declared package; nothing was installed."}}))
        return 1
    try:
        with Path(args.config).open("rb") as stream:
            config = c.parse(stream.read(c.MAX_INPUT + 1))
        if args.request == "-":
            raw = sys.stdin.buffer.read(c.MAX_INPUT + 1)
        else:
            with Path(args.request).open("rb") as stream:
                raw = stream.read(c.MAX_INPUT + 1)
        if len(raw) > c.MAX_INPUT:
            raise RecordError("limit_exceeded", "Source-store input exceeds whole-object limit.")
        result = SourceStore(args.root, config).execute(c.parse(raw))
    except (RecordError, OSError) as exc:
        result = {"contract_version": c.PROFILE, "status": "error", "local_result": "unknown",
                  "error": {"code": getattr(exc, "code", "io_error"), "message": getattr(exc, "message", "Cannot read selected source-store inputs.")}}
    sys.stdout.buffer.write(encoded(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
