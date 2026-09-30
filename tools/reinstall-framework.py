#!/usr/bin/env python3
"""Opt-in Git-backed breaking reinstall; one closed JSON stdin request/result."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types


def pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ValueError("duplicate request key")
        result[key] = value
    return result


def invalid(value):
    raise ValueError("invalid request scalar")


def main():
    if not sys.flags.isolated or not sys.flags.dont_write_bytecode:
        raise ValueError("Use python -I -B")
    raw = sys.stdin.buffer.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError("request budget")
    request = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                         parse_constant=invalid, parse_float=invalid)
    root = Path(__file__).absolute().parents[1]
    pin = request["installation"]["engine"]
    if Path(request["installation"]["engine_root"]) != root:
        raise ValueError("executing engine root")
    name = "src/tools/maintain_framework.py"
    rows = [r for r in pin["files"] if r["path"] == name]
    if len(rows) != 1:
        raise ValueError("bootstrap pin")
    launch = root / name
    for item in (launch, *launch.parents):
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("linked bootstrap")
    before = launch.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > 16 * 1024 * 1024:
        raise ValueError("bootstrap file")
    with launch.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        content = stream.read(16 * 1024 * 1024 + 1)
        after = os.fstat(stream.fileno())
    final = launch.lstat()
    signature = lambda i: (i.st_dev, i.st_ino, i.st_size, i.st_mtime_ns, i.st_mode, i.st_nlink)
    if not signature(before) == signature(opened) == signature(after) == signature(final) or hashlib.sha256(content).hexdigest() != rows[0]["sha256"]:
        raise ValueError("bootstrap drift")
    module = types.ModuleType("aicf_reinstall_bootstrap")
    module.__file__ = str(launch)
    exec(compile(content, str(launch), "exec", dont_inherit=True), module.__dict__)
    with module.verified_engine(str(root), pin):
        from distribution.reinstallation import execute
        result = execute(request)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["outcome"] in {"planned", "reinstalled"} else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, ImportError) as exc:
        print(json.dumps({"outcome": "blocked", "changed": False, "diagnostics": [{
            "code": "reinstall-bootstrap", "reason": "Pinned request or isolated bootstrap was rejected."}]}))
        raise SystemExit(1)
