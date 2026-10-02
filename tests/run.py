#!/usr/bin/env python3
"""Explicit local test suites; no installation, candidate build or provider calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT), str(ROOT / "framework_next")]

SUITES = {
    "schemas": "schemas",
    "tools": "tools",
    "distribution": (
        "framework_next.test_contracts", "framework_next.test_adapters",
        "framework_next.test_distribution_contracts", "framework_next.test_maintenance_contracts",
        "framework_next.test_skill_naming", "framework_next.test_distribution_versions",
    ),
    "release": "release",
    "source": ("source.test_source_gates", "test_runner"),
    "loader": ("framework_next.test_engine_source",),
    "platform": ("framework_next.test_protected_paths", "framework_next.test_windows_paths"),
}
DEFAULT_SUITES = ("schemas", "tools", "distribution", "release", "source")


def load_suite(name):
    loader = unittest.TestLoader()
    modules = SUITES[name]
    if isinstance(modules, str):
        return loader.discover(str(ROOT / modules), pattern="test_*.py", top_level_dir=str(ROOT))
    return loader.loadTestsFromNames(modules)


def execute(names):
    started = time.monotonic()
    suite = unittest.TestSuite()
    for name in names:
        selected = load_suite(name)
        if selected.countTestCases() == 0:
            raise ValueError("selected suite contains no tests: " + name)
        suite.addTests(selected)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    passed = result.wasSuccessful() and result.testsRun > 0 and not result.skipped
    return {"interface": "framework-tests/1", "suites": names,
            "outcome": "passed" if passed else "failed", "tests": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors),
            "skipped": len(result.skipped), "duration_seconds": round(time.monotonic() - started, 6)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", action="append", choices=tuple(SUITES),
                        help="repeat to combine suites; default: schemas tools distribution release source")
    args = parser.parse_args(argv)
    names = list(dict.fromkeys(args.suite or DEFAULT_SUITES))
    try:
        report = execute(names)
    except (ImportError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        report = {"interface": "framework-tests/1", "suites": names, "outcome": "failed",
                  "tests": 0, "failures": 0, "errors": 1, "skipped": 0, "duration_seconds": 0.0}
    print(json.dumps({"framework_tests": report}, ensure_ascii=False, sort_keys=True))
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
