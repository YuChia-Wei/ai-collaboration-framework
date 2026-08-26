#!/usr/bin/env python3
"""Resolve one exact public archive base from the governed version boundary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from ai_context_package_identity import PackageIdentityError, expected_package_id
from python_prerequisites import guard_direct_entrypoint


guard_direct_entrypoint(".ai/scripts/resolve-ai-context-package-identity.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        package_id = expected_package_id(args.version)
    except PackageIdentityError as exc:
        print(f"Package identity resolution failed: {exc}", file=sys.stderr)
        return 1
    print(package_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
