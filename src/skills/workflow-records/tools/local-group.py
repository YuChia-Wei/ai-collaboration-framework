#!/usr/bin/env python3
"""Explicit local workflow authority and project-owned provider handoffs; no dispatch."""
import argparse
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
        for name in ("__init__", "contracts", "common", "source_contract", "group_storage", "group_model", "group_providers", "group_service", "group_backup"):
            path = runtime_root / "workflow_records" / (name + ".py")
            if not path.is_file() or path.is_symlink():
                raise ImportError("Incomplete local-group closure")
        from workflow_records import source_contract as c
        from workflow_records.group_service import LocalGroup
        from workflow_records.contracts import RecordError
    except ImportError:
        print('{"status":"unavailable","error":{"code":"provider_unavailable","message":"Complete local-group runtime is required; nothing was installed."}}')
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
            raise RecordError("limit_exceeded", "Request exceeds 2 MiB.")
        result = LocalGroup(args.root, config).execute(c.parse(raw))
    except (RecordError, OSError) as exc:
        result = {"status": "error", "local_result": "unknown", "error": {"code": getattr(exc, "code", "io_error"), "message": getattr(exc, "message", "Selected inputs are unavailable.")}}
    sys.stdout.buffer.write(c.canonical(result) + b"\n")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
