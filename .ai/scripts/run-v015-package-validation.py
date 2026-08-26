#!/usr/bin/env python3
"""Run one independent v0.15 package validation lane or aggregate terminals."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/run-v015-package-validation.py")

import argparse
import json
import subprocess

from ai_context_v015_validation import (
    ValidationError,
    aggregate_terminals,
    execute_lane,
)


def add_lane_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--prior-terminal", type=Path)
    parser.add_argument("--material-state-change")
    parser.add_argument("--authorization-ref")
    parser.add_argument("--trusted-reference", action="store_true")


def validate_aggregate_output(root: Path, output: Path) -> Path:
    resolved = output.resolve()
    allowed = (root / ".dev/ai-context/local/validation").resolve()
    if not resolved.is_relative_to(allowed):
        raise ValidationError("aggregate-output-outside-ignored-validation-root")
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", str(resolved)],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if ignored.returncode != 0:
        raise ValidationError("aggregate-output-not-ignored")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Source repository root; defaults to the owning checkout.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    for lane in ("fast", "medium", "long"):
        add_lane_arguments(subcommands.add_parser(lane))
    aggregate = subcommands.add_parser("aggregate")
    aggregate.add_argument("--terminal", action="append", required=True, type=Path)
    aggregate.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    try:
        if args.command == "aggregate":
            output = validate_aggregate_output(root, args.output)
            return_code, record = aggregate_terminals(args.terminal, output)
        else:
            return_code, record = execute_lane(
                root=root,
                lane=args.command,
                expected_commit=args.expected_commit,
                output_dir=args.output_dir,
                attempt=args.attempt,
                prior_terminal=args.prior_terminal,
                material_state_change=args.material_state_change,
                authorization_ref=args.authorization_ref,
                trusted_reference=args.trusted_reference,
            )
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as error:
        reason = error.reason_code if isinstance(error, ValidationError) else "validation-preflight-failed"
        print(f"v0.15 package validation failed before terminal admission: {reason}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "schema_version": record["schema_version"],
                "outcome": record["outcome"],
                **({"lane": record["lane"]} if "lane" in record else {}),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
