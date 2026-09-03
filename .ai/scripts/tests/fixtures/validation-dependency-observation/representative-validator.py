"""Representative bounded validator used by VAL-012 contract tests."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
FIXTURE_ROOT = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    from decimal import Decimal

    arguments = [] if argv is None else list(argv)
    value = (FIXTURE_ROOT / "declared.txt").read_text(encoding="utf-8").strip()
    os.getenv("VAL012_MODE", "representative")
    python_result = subprocess.run(
        [sys.executable, "-B", "-c", "pass"],
        check=False,
        capture_output=True,
    )
    git_result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if "--take-branch" in arguments:
        (FIXTURE_ROOT / "untaken.txt").read_text(encoding="utf-8")
    return 0 if Decimal(value) == 12 and python_result.returncode == 0 and git_result.returncode == 0 else 1
