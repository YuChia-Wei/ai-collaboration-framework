#!/usr/bin/env python3
"""Generate the frozen 2026-07 GitHub backlog migration compatibility preview."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/plan-github-backlog-migration.py")

from github_backlog_provider import (
    ProviderContractError,
    build_plan,
    dump_plan_yaml,
    render_plan_markdown,
)


DEFAULT_CONFIG = Path(".dev/backlog/providers/github-legacy-migration.yaml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--revision", default="HEAD", help="Canonical Git commit/ref")
    parser.add_argument("--output-yaml", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when existing outputs differ; do not rewrite them",
    )
    return parser.parse_args()


def compare_or_write(path: Path, content: str, check: bool) -> None:
    if check:
        existing = path.read_text(encoding="utf-8") if path.is_file() else None
        if existing != content:
            raise ProviderContractError(f"generated output differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    repo = args.repo.resolve()
    config_path = args.config if args.config.is_absolute() else repo / args.config
    try:
        plan = build_plan(repo, config_path, args.revision)
        yaml_text = dump_plan_yaml(plan)
        markdown_text = render_plan_markdown(plan)
        if args.output_yaml:
            compare_or_write(args.output_yaml, yaml_text, args.check)
        if args.output_markdown:
            compare_or_write(args.output_markdown, markdown_text, args.check)
    except (OSError, ProviderContractError) as exc:
        print(f"GitHub backlog migration plan failed: {exc}", file=sys.stderr)
        return 1
    counts = plan["counts"]
    print(
        "GitHub backlog migration dry-run passed: "
        f"{counts['total']} items, {counts['open']} open, {counts['closed']} closed, "
        f"{counts['blocked']} blocked; online writes: false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
