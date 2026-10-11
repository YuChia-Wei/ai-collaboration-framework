#!/usr/bin/env python3
"""Source-project convenience entry; downstream implementation belongs to src."""
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/skills/workflow-records/tools/workflow-records.py"), run_name="__main__")
