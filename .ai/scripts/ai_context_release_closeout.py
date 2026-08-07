#!/usr/bin/env python3
"""Plan or verify source-only, post-tag AI-context release closeout."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import discover_candidates, guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/ai_context_release_closeout.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
STATE_VALIDATOR = ROOT / ".ai/scripts/validate-ai-context-release-state.py"
FORBIDDEN_ARGUMENTS = {"tag", "push", "delete", "reset", "checkout", "switch", "merge"}


class BlockedByEnvironment(RuntimeError):
    """A required local runtime is unavailable before a repository write."""


def run_read_only(command: list[str]) -> None:
    if not command or any(token in FORBIDDEN_ARGUMENTS for token in command):
        raise ValueError("closeout accepts read-only post-publication commands only")
    result = subprocess.run(command, cwd=ROOT, check=False, text=True)
    if result.returncode:
        raise RuntimeError(f"closeout check failed ({result.returncode}): {' '.join(command)}")


def runtime_preflight() -> str:
    """Inspect Python and the optional offline uv route without writing repository state."""
    candidates = discover_candidates()
    if not candidates:
        raise BlockedByEnvironment(
            "blocked-by-environment: no sanctioned Python or offline uv runtime is available"
        )
    return candidates[0].source


def read_tagged_at(version: str) -> str:
    result = subprocess.run(
        ["git", "for-each-ref", f"refs/tags/{version}", "--format=%(taggerdate:iso-strict)"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode or not result.stdout.strip():
        raise RuntimeError(f"unable to read annotated tag timestamp for {version}")
    return result.stdout.strip().splitlines()[0]


def update_release_record(
    worktree: Path,
    arguments: argparse.Namespace,
    tagged_at: str,
) -> Path:
    path = worktree / ".dev" / "releases" / arguments.version / "release.yaml"
    try:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load release registry from isolated worktree: {exc}") from exc
    if not isinstance(record, dict) or record.get("status") != "validated":
        raise RuntimeError("isolated closeout patch requires a validated release registry")

    tagged_commit = subprocess.run(
        ["git", "rev-parse", f"{arguments.version}^{{}}"],
        cwd=worktree,
        check=False,
        capture_output=True,
        text=True,
    )
    if tagged_commit.returncode or not tagged_commit.stdout.strip():
        raise RuntimeError(f"unable to peel immutable tag {arguments.version}")

    recorded_at = arguments.recorded_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    record.update(
        {
            "status": "published",
            "tag": arguments.version,
            "commit": tagged_commit.stdout.strip(),
            "tagged_at": tagged_at,
            "recorded_at": recorded_at,
            "updated_at": recorded_at,
        }
    )
    validation = record.setdefault("validation", {})
    if not isinstance(validation, dict):
        raise RuntimeError("release validation field must be a mapping")
    validation["published_run"] = arguments.workflow_run_id
    validation["public_release_url"] = (
        f"https://github.com/{arguments.repository}/releases/tag/{arguments.version}"
    )
    path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8", newline="\n")
    return path


def plan_patch(arguments: argparse.Namespace) -> None:
    """Generate a records-only patch in an isolated worktree after hosted read-back."""
    if (ROOT / arguments.output).resolve().is_relative_to(ROOT):
        raise ValueError("--output must stay outside the primary worktree")
    output = Path(arguments.output).resolve()
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing patch: {output}")
    runtime_preflight()
    base = [sys.executable, str(STATE_VALIDATOR), "--version", arguments.version, "--hosted"]
    shared = ["--repository", arguments.repository, "--workflow-run-id", arguments.workflow_run_id]
    if arguments.rendered_body:
        shared.extend(["--rendered-body", arguments.rendered_body])
    run_read_only([*base, "--phase", "publication", *shared])
    with tempfile.TemporaryDirectory(prefix="ai-context-release-closeout-") as temporary:
        worktree = Path(temporary) / "worktree"
        added = False
        try:
            subprocess.run(["git", "worktree", "add", "--detach", str(worktree), "HEAD"], cwd=ROOT, check=True)
            added = True
            update_release_record(worktree, arguments, read_tagged_at(arguments.version))
            command = [sys.executable, str(STATE_VALIDATOR), "--root", str(worktree), "--phase", "finalization", "--version", arguments.version, "--hosted", "--repository", arguments.repository, "--workflow-run-id", arguments.workflow_run_id]
            if arguments.rendered_body:
                command.extend(["--rendered-body", arguments.rendered_body])
            run_read_only(command)
            checked = subprocess.run(["git", "diff", "--check"], cwd=worktree, check=False)
            if checked.returncode:
                raise RuntimeError("isolated closeout registry patch fails git diff --check")
            patch = subprocess.run(["git", "diff", "--binary", "--", ".dev/releases"], cwd=worktree, check=True, capture_output=True).stdout
            if not patch:
                raise RuntimeError("isolated closeout registry patch is empty")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(patch)
        finally:
            if added:
                subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, check=False)
    print(f"Source-only closeout patch planned at {output}.")


def verify(arguments: argparse.Namespace) -> None:
    runtime_preflight()
    base = [sys.executable, str(STATE_VALIDATOR), "--version", arguments.version, "--hosted"]
    shared = ["--repository", arguments.repository]
    if arguments.rendered_body:
        shared.extend(["--rendered-body", arguments.rendered_body])
    if arguments.workflow_run_id:
        shared.extend(["--workflow-run-id", arguments.workflow_run_id])
    run_read_only([*base, "--phase", "finalization", *shared])
    print(f"Source-only release closeout passed for {arguments.version}.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    verify_parser = commands.add_parser("verify", help="read back a published release and its records")
    verify_parser.add_argument("--version", required=True)
    verify_parser.add_argument("--repository", required=True)
    verify_parser.add_argument("--workflow-run-id")
    verify_parser.add_argument("--rendered-body")
    verify_parser.set_defaults(handler=verify)
    patch_parser = commands.add_parser("plan-patch", help="create only an isolated records-only patch")
    patch_parser.add_argument("--version", required=True)
    patch_parser.add_argument("--repository", required=True)
    patch_parser.add_argument("--workflow-run-id", required=True)
    patch_parser.add_argument("--rendered-body")
    patch_parser.add_argument("--recorded-at")
    patch_parser.add_argument("--output", required=True)
    patch_parser.set_defaults(handler=plan_patch)
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        arguments.handler(arguments)
    except BlockedByEnvironment as exc:
        print(f"Source-only release closeout blocked: {exc}", file=sys.stderr)
        return 3
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Source-only release closeout failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
