#!/usr/bin/env python3
"""Opt-in source checkout workflow-record CLI. Does not install or mutate Git."""
from pathlib import Path
import argparse
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from workflow_records import WorkflowRecords
from workflow_records.contracts import MAX_FILE, RecordError, decode_json, encoded
from workflow_records.service import failure


def load(path):
    with path.open("rb") as stream:
        return decode_json(stream.read(MAX_FILE + 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--config", type=Path, help="Explicit config JSON; never saved implicitly")
    parser.add_argument("--request", type=Path, required=True, help="UTF-8 JSON request")
    args = parser.parse_args(argv)
    try:
        request = load(args.request)
        config = load(args.config) if args.config else None
        result = WorkflowRecords(args.root, config).execute(request)
    except RecordError as exc:
        result = failure(None, exc)
    except OSError:
        result = failure(None, RecordError("io_error", "Cannot read selected request/configuration."))
    sys.stdout.buffer.write(encoded(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
