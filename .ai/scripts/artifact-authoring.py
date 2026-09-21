#!/usr/bin/env python3
"""Preview, apply or recover restricted workflow/assessment authoring requests."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/artifact-authoring.py")

from artifact_authoring import AuthoringError, apply, catalog, parse, plan, recover


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog")
    for name in ("preview", "apply"):
        sub = commands.add_parser(name)
        sub.add_argument("--request", type=Path, required=True)
        if name == "apply": sub.add_argument("--expect", required=True, help="digest from the unchanged preview")
    recovery = commands.add_parser("recover")
    recovery.add_argument("--journal", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            print(json.dumps(catalog(args.root), indent=2))
        elif args.command == "recover":
            recover(args.root, args.journal)
            print("Pending bundle rolled back; prior observations remain in the ignored recovery journal.")
        else:
            request = parse(args.request.read_text(encoding="utf-8"), "request")
            if args.command == "preview":
                result = plan(args.root, request)
                print(result.diff(), end="")
                print(f"Preview digest: {result.digest}")
                print("No files written. Apply requires the same request and --expect digest.")
            else:
                journal = apply(args.root, request, args.expect)
                print(f"Bundle applied and validated before writes. Journal: {journal.relative_to(args.root.resolve()).as_posix()}")
        return 0
    except (AuthoringError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
