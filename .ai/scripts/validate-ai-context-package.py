#!/usr/bin/env python3
"""Validate AI context archives, sidecars, and ZIP/tar payload parity."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context-package.py")

import argparse
from ai_context_package import PackageError, validate_archive, validate_sidecar


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        results = []
        for archive in args.archives:
            validate_sidecar(archive)
            results.append((archive, validate_archive(archive)))
        if len(results) > 1:
            baseline_path, baseline = results[0]
            for candidate_path, candidate in results[1:]:
                if baseline != candidate:
                    raise PackageError(
                        f"archive member bytes or modes differ: {baseline_path} vs {candidate_path}"
                    )
    except (OSError, PackageError, ValueError) as exc:
        print(f"AI context package validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"AI context package validation passed for {len(results)} archive(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
