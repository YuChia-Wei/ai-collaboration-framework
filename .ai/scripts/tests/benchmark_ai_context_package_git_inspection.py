#!/usr/bin/env python3
"""Benchmark legacy and snapshot package-apply Git inspection on one host."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import subprocess
import sys
import time
import types
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
TEST_PATH = ROOT / ".ai/scripts/tests/test_ai_context_package_apply.py"
MODULE_PATH = ROOT / ".ai/scripts/ai_context_package_apply.py"


def load_fixture_module():
    spec = importlib.util.spec_from_file_location(
        "perf002_package_apply_fixtures", TEST_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load package apply fixtures: {TEST_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_legacy_module(ref: str):
    result = subprocess.run(
        ["git", "show", f"{ref}:.ai/scripts/ai_context_package_apply.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"cannot load legacy package apply module: {detail}")
    name = "perf002_legacy_ai_context_package_apply"
    module = types.ModuleType(name)
    module.__file__ = str(MODULE_PATH)
    sys.modules[name] = module
    exec(compile(result.stdout, str(MODULE_PATH), "exec"), module.__dict__)
    return module, hashlib.sha256(result.stdout).hexdigest()


@contextmanager
def count_git_processes():
    original_run = subprocess.run
    counter = {"count": 0}

    def counted_run(*args, **kwargs):
        argv = args[0] if args else kwargs.get("args")
        if isinstance(argv, (list, tuple)) and argv and argv[0] == "git":
            counter["count"] += 1
        return original_run(*args, **kwargs)

    with mock.patch.object(subprocess, "run", side_effect=counted_run):
        yield counter


def make_fixture(fixtures, payload_count: int):
    fixture = fixtures.PackageApplyFixture()
    previous = {
        f".ai/perf002/item-{index:04d}.txt": (
            f"payload-{index}\n".encode("utf-8"),
            "framework-managed",
            "0644",
        )
        for index in range(max(0, payload_count - 1))
    }
    incoming = dict(previous)
    added_path = f".ai/perf002/item-{payload_count - 1:04d}.txt"
    incoming[added_path] = (
        f"payload-{payload_count - 1}\n".encode("utf-8"),
        "framework-managed",
        "0644",
    )
    for path, (content, _ownership, _mode) in previous.items():
        destination = fixture.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    if previous:
        fixtures.git(fixture.target, "add", ".ai/perf002")
        fixture.commit_target("retained v0.14-scale baseline")
    operations = [
        fixtures.operation(
            "0000-add",
            "add",
            added_path,
        )
    ]
    fixture.make_package(incoming, operations, previous)
    return fixture


def invoke_plan(module, fixture, *, instrumented: bool):
    events: list[dict] = []
    started = time.perf_counter_ns()
    with count_git_processes() as processes:
        if instrumented:
            plan = module.build_plan(
                fixture.package,
                fixture.target,
                fixture.previous_path,
                "0.9.0",
                git_inspection_hook=events.append,
            )
        else:
            plan = module.build_plan(
                fixture.package,
                fixture.target,
                fixture.previous_path,
                "0.9.0",
            )
    return plan, {
        "duration_ns": time.perf_counter_ns() - started,
        "git_process_count": processes["count"],
        "instrumentation": events,
    }


def invoke_apply(module, plan, *, instrumented: bool):
    events: list[dict] = []
    packet = module.build_upgrade_remediation_packet(plan)
    proposal = packet["automatic_proposal"]
    decision = {
        "schema_version": "upgrade-remediation-decision/v1",
        "packet_sha256": packet["canonical_digest"],
        "plan_sha256": plan["plan_sha256"],
        "transaction_id": plan["plan_sha256"],
        "status": "approved",
        "owner": "perf002-benchmark",
        "decided_at": "2026-08-25T12:00:00+08:00",
        "evidence": "local exact-head benchmark fixture",
        "reason": "exercise the retained v0.14-scale apply path",
        "accepted_operation_ids": proposal["apply_operation_ids"],
        "reconciliation_ids": proposal["reconciliation_ids"],
        "policy_adoptions": None,
        "candidate_authority": {
            "provenance_sha256": "a" * 64,
            "customizations_sha256": "b" * 64,
        },
    }
    started = time.perf_counter_ns()
    with count_git_processes() as processes:
        if instrumented:
            receipt = module.apply_plan(
                plan,
                remediation_decision=decision,
                git_inspection_hook=events.append,
            )
        else:
            receipt = module.apply_plan(plan, remediation_decision=decision)
    if len(receipt["applied_operation_ids"]) != len(
        proposal["apply_operation_ids"]
    ):
        raise RuntimeError("benchmark apply did not complete every operation")
    return {
        "duration_ns": time.perf_counter_ns() - started,
        "git_process_count": processes["count"],
        "instrumentation": events,
    }


def run_sample(fixtures, module, payload_count: int, *, instrumented: bool):
    fixture = make_fixture(fixtures, payload_count)
    try:
        plan, plan_result = invoke_plan(
            module, fixture, instrumented=instrumented
        )
        apply_result = invoke_apply(module, plan, instrumented=instrumented)
        return {"plan": plan_result, "apply": apply_result}
    finally:
        fixture.close()


def summarize(samples: list[dict]) -> dict:
    cold = samples[0]
    warm = samples[1:]
    result = {
        "cold_first_fresh_fixture": cold,
        "warm_fresh_fixture_runs": warm,
        "warm_run_count": len(warm),
        "warm_median": {},
    }
    for phase in ("plan", "apply"):
        result["warm_median"][phase] = {
            "duration_ns": int(
                statistics.median(item[phase]["duration_ns"] for item in warm)
            ),
            "git_process_count": int(
                statistics.median(
                    item[phase]["git_process_count"] for item in warm
                )
            ),
        }
    return result


def run_profile(
    fixtures,
    module,
    payload_count: int,
    warm_runs: int,
    *,
    instrumented: bool,
) -> dict:
    samples = [
        run_sample(
            fixtures,
            module,
            payload_count,
            instrumented=instrumented,
        )
        for _ in range(warm_runs + 1)
    ]
    return {
        "payload_count": payload_count,
        "profile": "native-windows-real-filesystem-default-temp",
        "cache_condition": (
            "first sample is cold-first without OS cache reset; following samples "
            "are warm host-cache runs on fresh disposable fixture repositories"
        ),
        **summarize(samples),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--calibration-count", type=int, default=8)
    parser.add_argument("--scale-count", type=int, default=631)
    parser.add_argument("--warm-runs", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.calibration_count < 1 or args.scale_count < 1 or args.warm_runs < 3:
        parser.error("counts must be positive and --warm-runs must be at least 3")

    fixtures = load_fixture_module()
    legacy, legacy_sha256 = load_legacy_module(args.base_ref)
    current = fixtures.APPLY
    subject = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tracked_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    committed_module = subprocess.run(
        ["git", "show", f"{subject}:.ai/scripts/ai_context_package_apply.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if tracked_status or committed_module != MODULE_PATH.read_bytes():
        raise RuntimeError(
            "benchmark subject must be a clean exact HEAD containing the current module bytes"
        )
    document = {
        "schema_version": "package-apply-git-benchmark/v1",
        "subject_commit": subject,
        "base_ref": args.base_ref,
        "legacy_module_sha256": legacy_sha256,
        "current_module_sha256": hashlib.sha256(MODULE_PATH.read_bytes()).hexdigest(),
        "warm_runs": args.warm_runs,
        "legacy_calibration": run_profile(
            fixtures,
            legacy,
            args.calibration_count,
            args.warm_runs,
            instrumented=False,
        ),
        "snapshot_calibration": run_profile(
            fixtures,
            current,
            args.calibration_count,
            args.warm_runs,
            instrumented=True,
        ),
        "legacy_scale": run_profile(
            fixtures,
            legacy,
            args.scale_count,
            args.warm_runs,
            instrumented=False,
        ),
        "snapshot_scale": run_profile(
            fixtures,
            current,
            args.scale_count,
            args.warm_runs,
            instrumented=True,
        ),
    }
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"))
    document["content_sha256"] = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    rendered = json.dumps(document, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
