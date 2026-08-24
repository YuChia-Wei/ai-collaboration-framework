#!/usr/bin/env python3
"""Run or benchmark the tracked ephemeral fixture profile without leaking roots."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/run-test-fixture-profile.py")

from test_fixture_runtime import (
    DIAGNOSTICS_VARIABLE,
    ENVIRONMENT_VARIABLE,
    SUMMARY_PREFIX,
    FixtureRootError,
    load_classification_manifest,
    platform_family,
    resolve_fixture_root,
)


ROOT = Path(__file__).resolve().parents[2]
STORAGE_KINDS = {
    "unspecified-explicit",
    "generic-fast-storage",
    "ram-backed",
    "tmpfs",
    "wsl-native",
}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("action", choices=("run", "benchmark"))
    value.add_argument("--mode", choices=("default", "accelerated"), required=True)
    value.add_argument("--fixture-root")
    value.add_argument("--storage-kind", choices=sorted(STORAGE_KINDS), default="unspecified-explicit")
    value.add_argument("--condition", choices=("cold", "warm"), required=True)
    value.add_argument("--runs", type=int, default=None)
    value.add_argument("--output", type=Path)
    return value


def _parse_summary(output: str) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for line in output.splitlines():
        if line.startswith(SUMMARY_PREFIX):
            value = json.loads(line[len(SUMMARY_PREFIX) :])
            if isinstance(value, dict):
                summaries.append(value)
    return summaries


def _sanitized_preflight(args: argparse.Namespace) -> tuple[dict[str, object], dict[str, str]]:
    child_environment = dict(os.environ)
    child_environment[DIAGNOSTICS_VARIABLE] = "1"
    if args.mode == "default":
        if args.fixture_root:
            raise FixtureRootError("default mode must not receive --fixture-root")
        child_environment.pop(ENVIRONMENT_VARIABLE, None)
        resolution = resolve_fixture_root(environ={})
    else:
        resolution = resolve_fixture_root(args.fixture_root)
        if resolution.route != "accelerated":
            raise FixtureRootError(
                "accelerated mode requires --fixture-root or AI_CONTEXT_TEST_TMP_ROOT"
            )
        assert resolution.preflight is not None
        child_environment[ENVIRONMENT_VARIABLE] = str(resolution.preflight.root)
    diagnostic = resolution.diagnostic(workspace=ROOT)
    diagnostic["source"] = resolution.source
    if resolution.preflight:
        diagnostic.update(
            {
                "filesystem_type": resolution.preflight.filesystem_type,
                "capacity_bytes": resolution.preflight.capacity_bytes,
                "free_bytes": resolution.preflight.free_bytes,
                "writable": True,
                "containment_preflight": "passed",
            }
        )
    else:
        diagnostic.update(
            {
                "filesystem_type": "os-default",
                "capacity_bytes": "not-applicable",
                "free_bytes": "not-applicable",
                "writable": "not-applicable",
                "containment_preflight": "not-applicable",
            }
        )
    return diagnostic, child_environment


def run(args: argparse.Namespace) -> int:
    runs = args.runs if args.runs is not None else (3 if args.action == "benchmark" else 1)
    if runs < 1:
        raise FixtureRootError("runs must be at least 1")
    if args.action == "benchmark" and runs < 3:
        raise FixtureRootError("benchmark requires at least three runs for a median")

    manifest = load_classification_manifest(ROOT)
    tests = [entry["path"] for entry in manifest["tests"]]
    diagnostic, child_environment = _sanitized_preflight(args)
    subject = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    result_runs: list[dict[str, object]] = []
    final_exit = 0
    for run_number in range(1, runs + 1):
        started = time.perf_counter()
        fixture_count = 0
        fixture_seconds = 0.0
        outcomes: list[dict[str, object]] = []
        for relative in tests:
            completed = subprocess.run(
                [sys.executable, relative, "-v"],
                cwd=ROOT,
                env=child_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            combined = completed.stdout + completed.stderr
            sys.stdout.write(combined)
            summaries = _parse_summary(combined)
            fixture_count += sum(int(item.get("fixture_count", 0)) for item in summaries)
            fixture_seconds += sum(float(item.get("fixture_creation_seconds", 0.0)) for item in summaries)
            outcomes.append({"test": relative, "exit_code": completed.returncode})
            if completed.returncode != 0:
                final_exit = completed.returncode
                break
        result_runs.append(
            {
                "run": run_number,
                "wall_duration_seconds": round(time.perf_counter() - started, 6),
                "fixture_creation_seconds": round(fixture_seconds, 6),
                "fixture_count": fixture_count,
                "subprocess_phase_seconds": "unavailable",
                "nested_subprocess_count": "unavailable",
                "outcomes": outcomes,
            }
        )
        if final_exit:
            break

    complete_durations = [float(item["wall_duration_seconds"]) for item in result_runs]
    evidence = {
        "schema_version": "1.0",
        "profile": manifest["profile"],
        "fixture_classification": "ephemeral-fixture-io",
        "mode": args.mode,
        "storage_kind": args.storage_kind if args.mode == "accelerated" else "os-default",
        "condition": args.condition,
        "platform": platform_family(),
        "commit": subject,
        "test_count": len(tests),
        "tests": tests,
        "preflight": diagnostic,
        "runs": result_runs,
        "median_wall_duration_seconds": round(statistics.median(complete_durations), 6),
        "outcome": "passed" if final_exit == 0 and len(result_runs) == runs else "failed",
    }
    rendered = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return final_exit


def main() -> int:
    args = parser().parse_args()
    try:
        return run(args)
    except (FixtureRootError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"Fixture profile failed before material fixtures: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
