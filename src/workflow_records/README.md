# Workflow records source compatibility

The canonical optional product package is [workflow-records](../skills/workflow-records/SKILL.md).
Read its [operations](../skills/workflow-records/references/operations.md) and
[Git record format](../skills/workflow-records/references/git-format.md).
This source-only namespace preserves existing source consumers; downstream
execution uses the complete installed package and never this shim or root tools.
