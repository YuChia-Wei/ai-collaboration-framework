#!/usr/bin/env python3
"""Source-maintainer invocation; all selection and assembly behavior lives in src."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a development candidate from one exact committed selection; never install it.")
    parser.add_argument("--repository", type=Path, required=True, help="Absolute source worktree root matching this implementation")
    parser.add_argument("--commit", required=True, help="Full lowercase immutable commit object ID")
    parser.add_argument("--profile", required=True, help="Explicit profile ID, initially lesson-minimal")
    parser.add_argument("--output-root", type=Path, required=True, help="Existing absolute output parent outside the worktree")
    parser.add_argument("--scratch-root", type=Path, required=True, help="Existing absolute scratch parent outside the worktree; may equal output-root")
    args = parser.parse_args()
    if sys.version_info < (3, 11) or sys.version_info >= (4, 0):
        parser.error("Python >=3.11,<4 is required")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from distribution.assembly import assemble
    from distribution.data import DistributionError
    try:
        result = assemble(args.repository, args.commit, args.profile, args.output_root, args.scratch_root)
    except (DistributionError, OSError, UnicodeError, TypeError, RecursionError) as exc:
        print(json.dumps({"outcome": "failed", "diagnostic": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
