#!/usr/bin/env python3
"""Run the exact-head PERF-002 long validation profile sequentially."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def run_step(name: str, argv: list[str], output_dir: Path) -> dict:
    started_at = now()
    started = time.perf_counter()
    result = subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    duration = time.perf_counter() - started
    stdout_path = output_dir / f"{name}.stdout.log"
    stderr_path = output_dir / f"{name}.stderr.log"
    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    combined = (result.stdout + b"\n" + result.stderr).decode(
        "utf-8", errors="replace"
    )
    ran = re.findall(r"Ran (\d+) tests?", combined)
    skipped = re.findall(r"skipped=(\d+)", combined)
    return {
        "name": name,
        "argv": argv,
        "started_at": started_at,
        "completed_at": now(),
        "duration_seconds": round(duration, 6),
        "exit_code": result.returncode,
        "counts": {
            "tests": int(ran[-1]) if ran else 0,
            "skipped": int(skipped[-1]) if skipped else 0,
        },
        "stdout": {
            "path": stdout_path.relative_to(ROOT).as_posix(),
            "sha256": digest(result.stdout),
            "bytes": len(result.stdout),
        },
        "stderr": {
            "path": stderr_path.relative_to(ROOT).as_posix(),
            "sha256": digest(result.stderr),
            "bytes": len(result.stderr),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--scale-count", type=int, default=631)
    parser.add_argument("--warm-runs", type=int, default=3)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40,64}", args.expected_commit):
        parser.error("--expected-commit must be a full lowercase Git object ID")
    if args.scale_count < 1 or args.warm_runs < 3:
        parser.error("--scale-count must be positive and --warm-runs at least 3")
    output_dir = args.output_dir.resolve()
    try:
        output_dir.relative_to(ROOT)
    except ValueError:
        parser.error("--output-dir must be contained by the repository")
    output_dir.mkdir(parents=True, exist_ok=True)

    observed = git("rev-parse", "HEAD").stdout.strip()
    tracked_status = git("status", "--porcelain", "--untracked-files=no").stdout
    if observed != args.expected_commit or tracked_status:
        summary = {
            "schema_version": "perf002-long-validation/v1",
            "outcome": "blocked-by-environment",
            "expected_commit": args.expected_commit,
            "observed_commit": observed,
            "clean_tracked_worktree": not bool(tracked_status),
            "steps": [],
        }
        (output_dir / "summary.json").write_text(
            json.dumps(summary, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 2

    commands = [
        (
            "package-apply",
            [
                sys.executable,
                str(ROOT / ".ai/scripts/tests/test_ai_context_package_apply.py"),
                "-v",
            ],
        ),
        (
            "multi-hop",
            [
                sys.executable,
                str(ROOT / ".ai/scripts/tests/test_ai_context_multi_hop_upgrade.py"),
                "-v",
            ],
        ),
        (
            "git-benchmark",
            [
                sys.executable,
                str(
                    ROOT
                    / ".ai/scripts/tests/benchmark_ai_context_package_git_inspection.py"
                ),
                "--base-ref",
                args.base_ref,
                "--calibration-count",
                "8",
                "--scale-count",
                str(args.scale_count),
                "--warm-runs",
                str(args.warm_runs),
                "--output",
                str(output_dir / "benchmark.json"),
            ],
        ),
    ]
    started_at = now()
    started = time.perf_counter()
    steps: list[dict] = []
    for name, argv in commands:
        step = run_step(name, argv, output_dir)
        steps.append(step)
        if step["exit_code"] != 0:
            break
    final_head = git("rev-parse", "HEAD").stdout.strip()
    final_status = git("status", "--porcelain", "--untracked-files=no").stdout
    passed = (
        len(steps) == len(commands)
        and all(item["exit_code"] == 0 for item in steps)
        and final_head == args.expected_commit
        and not final_status
    )
    summary = {
        "schema_version": "perf002-long-validation/v1",
        "outcome": "passed" if passed else "failed",
        "expected_commit": args.expected_commit,
        "observed_commit": final_head,
        "clean_tracked_worktree": not bool(final_status),
        "started_at": started_at,
        "completed_at": now(),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "steps": steps,
    }
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    summary["content_sha256"] = digest(encoded)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
