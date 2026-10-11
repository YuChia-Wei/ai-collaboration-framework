"""Source-only import compatibility; canonical modules belong to the optional skill."""
from pathlib import Path
__path__ = [str(Path(__file__).resolve().parents[1] / "skills/workflow-records/tools/workflow_records")]
from .service import WorkflowRecords
__all__ = ["WorkflowRecords"]
