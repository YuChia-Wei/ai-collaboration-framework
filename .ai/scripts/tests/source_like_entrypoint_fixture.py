#!/usr/bin/env python3
"""Small disposable source-like fixtures for direct-entrypoint contract tests."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path


_SHARED_PATHS = (
    ".ai/scripts/python_prerequisites.py",
    ".ai/scripts/python-entrypoints.json",
)


def copy_source_like_entrypoints(
    source_root: Path,
    fixture_root: Path,
    entrypoints: Iterable[str],
    *,
    support_files: Iterable[str] = (),
) -> None:
    """Copy only the exact direct-entrypoint inputs needed before target imports."""
    for relative_path in (*_SHARED_PATHS, *entrypoints, *support_files):
        source_path = source_root / relative_path
        fixture_path = fixture_root / relative_path
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        contents = source_path.read_bytes()
        fixture_path.write_bytes(contents)
        if fixture_path.read_bytes() != contents:
            raise AssertionError(f"fixture copy did not preserve {relative_path}")


def fixture_tree_snapshot(root: Path) -> dict[str, str]:
    """Record the bounded disposable tree, including empty directories and files."""
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[f"{relative_path}/"] = "<directory>"
        elif path.is_file():
            snapshot[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot
