#!/usr/bin/env python3
"""Prepare Board V2 queries or accept a supplied MCP result; performs no transport."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def runtime():
    # Loading this exact declared member avoids the unrelated provider package
    # initializer and ambient modules. No source-checkout or dependency fallback.
    member = Path(__file__).resolve().parent / "workflow_records" / "board_query.py"
    if not (3, 11) <= sys.version_info[:2] < (4, 0) or not member.is_file() or member.is_symlink():
        raise ImportError("Missing local runtime")
    spec = importlib.util.spec_from_file_location("board_query_runtime", member)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="UTF-8 JSON file, or '-' for stdin")
    parser.add_argument("--activate", action="store_true", help="Explicitly activate this experimental bridge for this invocation")
    args = parser.parse_args(argv)
    if not args.activate:
        print(json.dumps({"contract_version": "workflow-records/board-query/1", "operation": None,
                          "status": "unavailable", "mutation_state": "none",
                          "error": {"code": "experimental_not_activated", "message": "Installation does not activate the experimental Board bridge; select --activate explicitly."}}))
        return 1
    try:
        api = runtime()
    except (ImportError, OSError):
        print(json.dumps({"contract_version": "workflow-records/board-query/1", "operation": None,
                          "status": "unavailable", "mutation_state": "none",
                          "error": {"code": "runtime_unavailable", "message": "Requires Python 3.11+ and the declared local board_query.py runtime."}}))
        return 1
    try:
        if args.request == "-":
            raw = sys.stdin.buffer.read(api.MAX_BYTES + 1)
        else:
            with Path(args.request).open("rb") as stream:
                raw = stream.read(api.MAX_BYTES + 1)
        result = api.execute(api.decode(raw))
    except api.QueryError as exc:
        result = api.failure(None, exc)
    except OSError:
        result = api.failure(None, api.QueryError("io_error", "Cannot read selected request."))
    sys.stdout.buffer.write(api.encode(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
