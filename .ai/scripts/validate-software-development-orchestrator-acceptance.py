#!/usr/bin/env python3
"""Compatibility entrypoint for the skill-owned acceptance validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[1]
    / "assets/skills/software-development-orchestrator/scripts/"
    "validate-software-development-orchestrator-acceptance.py"
)
SPEC = importlib.util.spec_from_file_location(
    "software_development_orchestrator_acceptance", TARGET
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load canonical validator: {TARGET}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

for name in dir(MODULE):
    if not name.startswith("__"):
        globals()[name] = getattr(MODULE, name)


if __name__ == "__main__":
    raise SystemExit(MODULE.main())
