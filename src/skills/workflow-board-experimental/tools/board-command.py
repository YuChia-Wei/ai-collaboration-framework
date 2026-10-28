#!/usr/bin/env python3
"""Prepare, accept or reconcile Board V2 commands without sending them."""
import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def unavailable():
    return {"contract_version": "workflow-records/board-command/1", "operation": None,
            "status": "unavailable", "bridge_effect": "none", "command_outcome": "unknown",
            "error": {"code": "runtime_unavailable", "message": "Requires Python 3.11+, jsonschema >=4.26,<5, its dependencies and all declared local runtime/schema members; nothing was installed."},
            "next_action": "retain_original_prepared_command_if_dispatch_may_have_occurred"}


def runtime():
    if not (3, 11) <= sys.version_info[:2] < (4, 0):
        raise ImportError("Python prerequisite")
    version = tuple(int(item) for item in importlib.metadata.version("jsonschema").split(".")[:2])
    if not (4, 26) <= version < (5, 0):
        raise ImportError("jsonschema prerequisite")
    member = Path(__file__).resolve().parent / "workflow_records/board_command.py"
    if not member.is_file() or member.is_symlink():
        raise ImportError("Declared command runtime missing")
    spec = importlib.util.spec_from_file_location("board_command_runtime", member)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, help="Strict UTF-8 JSON file, or '-' for stdin")
    parser.add_argument("--activate", action="store_true", help="Explicitly activate this experimental bridge for this invocation")
    args = parser.parse_args(argv)
    if not args.activate:
        print(json.dumps({"contract_version": "workflow-records/board-command/1", "operation": None,
                          "status": "unavailable", "bridge_effect": "none", "command_outcome": "unknown",
                          "error": {"code": "experimental_not_activated", "message": "Installation does not activate the experimental Board bridge; select --activate explicitly."}}))
        return 1
    try:
        api = runtime()
    except (ImportError, OSError, ValueError):
        print(json.dumps(unavailable()))
        return 1
    try:
        if args.request == "-":
            raw = sys.stdin.buffer.read(api.MAX_BYTES + 1)
        else:
            with Path(args.request).open("rb") as stream:
                raw = stream.read(api.MAX_BYTES + 1)
        result = api.execute(api.decode(raw))
    except api.CommandError as exc:
        result = api.failure(None, exc)
    except OSError:
        result = api.failure(None, api.CommandError("io_error", "Cannot read selected request; retain any already dispatched command."))
    sys.stdout.buffer.write(api.encode(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
