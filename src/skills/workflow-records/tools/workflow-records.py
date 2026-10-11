#!/usr/bin/env python3
"""Optional installed workflow-record CLI. Uses only its declared local runtime."""
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
runtime_root = Path(__file__).resolve().parent
sys.path.insert(0, str(runtime_root))
try:
    if not (3, 11) <= sys.version_info[:2] < (4, 0):
        raise ImportError("Python prerequisite")
    for member in ("__init__", "contracts", "common", "git_store", "sqlite_store", "backup", "service"):
        source = runtime_root / "workflow_records" / (member + ".py")
        if not source.is_file() or source.is_symlink():
            raise ImportError("Required local member")
    import yaml
    if int(yaml.__version__.split(".")[0]) != 6:
        raise ImportError("PyYAML prerequisite")
    from workflow_records import WorkflowRecords
    from workflow_records.contracts import MAX_FILE, RecordError, decode_json, encoded
    from workflow_records.service import failure
except (ImportError, ValueError):
    print(json.dumps({"contract_version": "workflow-records/1", "operation": None, "status": "unavailable",
                      "mutation_state": "none", "error": {"code": "provider_unavailable",
                      "message": "Requires Python 3.11+ in the 3.x series, PyYAML 6.x and the complete local workflow runtime; nothing was installed automatically."}}))
    raise SystemExit(1)


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
