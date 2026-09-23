# Work management design and implementation

- Workflow: `2026-09-23-work-management`; owner: `ai-context-governance`.
- Branch/worktree: `codex/2026-09-23-work-management`, `F:/framework-next/335`.
- Base: main; starting commit `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`.
- State: **in_progress**, remediation-planning; Issue [#335](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/335) is OPEN in the last live read.
- Created/updated: 2026-09-23T08:18:00+08:00.
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version 1.2.0, adapted under U001.

## Objective and ownership

Design and later implement independent PR and local-backlog skills with one GitHub provider boundary. This first checkpoint writes only `.dev/design/framework-next/work-management/` and this workflow. Product source, shared configuration/parser/manifest/schema ownership, runtime entries, coordinator workflow/index and historical backlog remain protected.

This two-task workflow retains unique cross-session state: an early contract commit, coordinator-owned interface reconciliation, later source ownership and source delivery, plus assigned P7 verification deferral. It is not padded with audit-only tasks. Governance templates are used proportionally; no legacy validator compliance is claimed.

## Tasks and completion

| Task | State | Bounded completion |
| --- | --- | --- |
| [WM-001](tasks/WM-001.json) | completed | Reviewable contract, two record schema proposals, operations/members/config needs, lifecycle/authority tables and synthetic examples. |
| [WM-002](tasks/WM-002.json) | in_progress | Receive coordinator reconciliation and explicit source ownership; implement actual source/tools/docs in this same task. No product source started at checkpoint. |

Contract delivery does not satisfy the Issue's final implementation outcome. Behavioral/schema/package/provider acceptance and CI are deferred-by-owner under U001 to program #322 coordinator / P7. Source implementation may later complete its bounded code-delivery scope without claiming those checks passed.

## Decisions and next action

[Integration proposal](../../design/framework-next/work-management/integration-proposal.json) contains:
WM-C1 multi-namespace config semantics/version and existing-consumer changes;
WM-C2 exact 10 PR / 8 backlog members plus package-owned pr.github tool;
WM-C3 coordinated single-writer provider update versus explicitly unsupported atomic concurrency.

Coordinator owns selections, shared files, first push and online integration. Resume this same task after those choices and source ownership are explicit. No new user approval checkpoint is being introduced. No push/PR/merge/Issue/Project mutation, credential change, runtime activation or release is authorized for this executor.

## Evidence and branch checkpoint

[Report](reports/contract-checkpoint.md) and [receiving checkpoint](handoff.yaml) preserve observed facts, limitations and continuation. The containing commit identifies the local design checkpoint without a self-referential SHA. Original dispatch and P2 handoff remain unchanged. The local commit lands in the existing persistent common Git database; F: source files remain volatile.

The same branch continues after coordinator reconciliation unless the coordinator explicitly assigns another existing branch/worktree. No executor-created task/worktree or sub-agent is permitted.