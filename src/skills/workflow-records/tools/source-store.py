#!/usr/bin/env python3
"""Explicit local source snapshots and retained replica data; no dispatch."""
import argparse
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
                       "source_contract", "source_store", "source_backup", "source_config", "source_proof"):
            local = runtime_root / "workflow_records" / (member + ".py")
            if not local.is_file() or local.is_symlink():
                raise ImportError("Declared local source-store runtime is incomplete")
        import yaml
        if not (3, 11) <= sys.version_info[:2] < (4, 0) or yaml.__version__.split(".")[0] != "6":
            raise ImportError("Selected source-store runtime version is unavailable")
        from workflow_records import source_contract as c
        from workflow_records.source_store import SourceStore
        from workflow_records.contracts import RecordError, encoded
    except (ImportError, ValueError):
        print(json.dumps({"contract_version": "workflow-records/source-store/1", "status": "unavailable", "local_result": "unknown",
                          "error": {"code": "provider_unavailable", "message": "Requires Python 3.11+, PyYAML 6 and the complete local source-store runtime; nothing was installed."}}))
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
        request = c.parse(raw)
        if isinstance(request, dict) and str(request.get("operation", "")).startswith("board-"):
            raise RecordError("provider_unavailable", "Board bridges require explicitly selected and activated workflow-board-experimental; core never loads an adapter implicitly.")
        result = SourceStore(args.root, config).execute(request)
    except (RecordError, OSError) as exc:
        result = {"contract_version": c.PROFILE, "status": "error", "local_result": "unknown",
                  "error": {"code": getattr(exc, "code", "io_error"), "message": getattr(exc, "message", "Cannot read selected source-store inputs.")}}
    sys.stdout.buffer.write(encoded(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
