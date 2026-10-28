"""Optional workflow-record provider API."""
__all__ = ["WorkflowRecords"]


def __getattr__(name):
    # File-only local groups do not load native SQLite adapters implicitly.
    if name == "WorkflowRecords":
        from .service import WorkflowRecords
        globals()[name] = WorkflowRecords
        return WorkflowRecords
    raise AttributeError(name)
