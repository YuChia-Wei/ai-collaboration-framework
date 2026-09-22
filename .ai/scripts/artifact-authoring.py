#!/usr/bin/env python3
"""Route, preview, apply or recover bounded artifact authoring requests."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/artifact-authoring.py")

from artifact_authoring import AuthoringError, apply, catalog, fields, parse, plan, recover


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog")
    routing = commands.add_parser("routes", help="inspect checked lifecycle owner routes, including explicit gaps")
    routing.add_argument("--kind", help="select one lifecycle kind")
    for name in ("preview", "apply"):
        sub = commands.add_parser(name)
        if name == "preview":
            sub.add_argument("--request", type=Path, required=True)
            sub.add_argument("--json", action="store_true", help="emit resolved request, captured timestamp, digest and diff to stdout")
        else:
            source = sub.add_mutually_exclusive_group(required=True)
            source.add_argument("--request", type=Path, help="legacy request with explicit timestamp")
            source.add_argument("--preview", type=Path, help="unchanged JSON output from preview --json")
            sub.add_argument("--expect", required=True, help="digest from the unchanged preview")
    recovery = commands.add_parser("recover")
    recovery.add_argument("--journal", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            print(json.dumps(catalog(args.root), indent=2))
        elif args.command == "routes":
            from artifact_lifecycle import routes
            print(json.dumps(routes(args.root, args.kind), indent=2))
        elif args.command == "recover":
            recover(args.root, args.journal)
            print("Pending bundle rolled back; prior observations remain in the ignored recovery journal.")
        else:
            if args.command == "apply" and args.preview:
                preview = parse(args.preview.read_text(encoding="utf-8-sig"), "preview")
                fields(preview, {"format", "request", "digest", "diff"}, set(), "preview")
                if preview["format"] != "artifact-authoring-preview/v1" or preview["digest"] != args.expect:
                    raise AuthoringError("preview format or expected digest mismatch")
                request = preview["request"]
            else:
                request = parse(args.request.read_text(encoding="utf-8-sig"), "request")
            if args.command == "preview":
                result = plan(args.root, request)
                if args.json:
                    print(json.dumps({"format": "artifact-authoring-preview/v1", "request": result.request,
                                      "digest": result.digest, "diff": result.diff()}, ensure_ascii=False, indent=2))
                else:
                    print(result.diff(), end="")
                    print(f"Preview digest: {result.digest}")
                    print("No files written. For automatic timestamps, retain preview --json output and apply --preview with --expect.")
            else:
                journal = apply(args.root, request, args.expect)
                print(f"Bundle applied and validated before writes. Journal: {journal.relative_to(args.root.resolve()).as_posix()}")
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
