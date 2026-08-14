#!/usr/bin/env python3
"""Plan, apply, resume, or roll back an extracted AI context package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The planner is executed from inside the checksum-governed extracted envelope.
# Prevent the local module import from creating an ungoverned __pycache__ member
# before the envelope checksum set is verified.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/plan-ai-context-package-apply.py")

import yaml

from ai_context_package_apply import (
    ApplyError,
    apply_plan,
    atomic_write_bytes,
    build_plan,
    recover_transaction,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--previous-files", type=Path)
    parser.add_argument(
        "--previous-version",
        help=(
            "Exact source version for schema 2 upgrades; must be supplied with "
            "--previous-files"
        ),
    )
    parser.add_argument("--acknowledge", action="append", default=[])
    parser.add_argument(
        "--enable-provider",
        action="append",
        default=[],
        choices=["repo-backlog"],
        help="Enable an optional provider for a clean installation.",
    )
    lifecycle = parser.add_mutually_exclusive_group()
    lifecycle.add_argument("--apply", action="store_true")
    lifecycle.add_argument("--resume", metavar="TRANSACTION_ID")
    lifecycle.add_argument("--rollback", metavar="TRANSACTION_ID")
    parser.add_argument("--plan-output", type=Path)
    args = parser.parse_args()
    try:
        if args.resume or args.rollback:
            if args.plan_output or args.previous_files or args.previous_version or args.acknowledge or args.enable_provider:
                raise ApplyError(
                    "recovery cannot change the sealed plan, selection, or acknowledgements"
                )
            if args.resume and args.package_root is None:
                raise ApplyError("--resume requires --package-root")
            result = recover_transaction(
                args.target_root,
                args.resume or args.rollback,
                "resume" if args.resume else "rollback",
                args.package_root,
            )
            label = "apply_receipt" if args.resume else "rollback_journal"
            print(yaml.safe_dump({label: result}, sort_keys=False), end="")
            return 0
        if args.package_root is None:
            raise ApplyError("planning and --apply require --package-root")
        if args.plan_output:
            output = args.plan_output.resolve()
            for forbidden_root, label in (
                (args.package_root.resolve(), "extracted package"),
                (args.target_root.resolve(), "target repository"),
            ):
                if output == forbidden_root or output.is_relative_to(forbidden_root):
                    raise ApplyError(f"--plan-output must be outside the {label}")
        plan = build_plan(
            args.package_root,
            args.target_root,
            args.previous_files,
            args.previous_version,
            args.enable_provider,
        )
        content = yaml.safe_dump(plan, sort_keys=False, allow_unicode=True)
        if args.plan_output:
            atomic_write_bytes(args.plan_output, content.encode("utf-8"))
        print(content, end="")
        if not args.apply:
            print("Dry run only. Re-run with --apply after reviewing the plan.")
            return 0
        receipt = apply_plan(plan, set(args.acknowledge))
        print(yaml.safe_dump({"apply_receipt": receipt}, sort_keys=False), end="")
        return 0
    except (OSError, ApplyError, ValueError) as exc:
        print(f"AI context package apply failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
