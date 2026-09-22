# Source Layout Design Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-23-source-layout`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-23-source-layout`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-23-source-layout`
- `created_at`: `2026-09-23T01:08:23+08:00`
- `updated_at`: `2026-09-23T01:20:56+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

Deliver [Issue #326](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/326), P1-B under #322: source-versus-consumer design, mapping inventory, concrete manifest/layout/recovery examples and a Traditional Chinese explanation. Own only `.dev/design/framework-next/source-layout/` and this workflow. Work only in `F:/framework-next/326`, starting at `53c9c8e58615e87e36f7b74ea8851fe845312daa`; do not change the main checkout.

No full relocation, schema duplication, implementation, package build, migration trial, downstream adoption, provider mutation, release or tag. No sub-agents or child-created tasks. Local coherent commits are authorized; stop before first push/PR/merge/Issue closure. The coordinator owns `.dev/workflows/INDEX.MD` and cross-Issue integration.

## Authority And U001 Exception

[U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md) overrides conflicting legacy gates. [Architecture A2/A7/A9](../../assessments/ASM-20260923-00-6oq/architecture.md) supplies the selected design direction. The [incoming handoff](../2026-09-23-framework-redesign-control/handoffs/issue-326.yaml) pins an earlier coordinator subject; actual starting HEAD above was verified clean on the designated branch.

Legacy validators, critical/check-all, test suites, package/upgrade/migration trials, validation-only audit packets and CI are **deferred-by-owner to P7**, never passed. No old gate or validator redesign is part of this task. Allowed checks are file readability, direct JSON/YAML syntax, reference/content inspection, Git diff/status and commit-message format. The normal independent post-audit/handoff-validator stages are deferred under this same explicit exception, not silently satisfied.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260923-00-6oq/` (read-only authority; this workflow does not close its findings).
- Design entry: [Traditional Chinese explanation](../../design/framework-next/source-layout/README.md).
- Design: [source/consumer design](../../design/framework-next/source-layout/design.md).
- Inventory: [mapping and staged transition](../../design/framework-next/source-layout/mapping-inventory.md).
- Examples: `.dev/design/framework-next/source-layout/examples/`.
- Report: `reports/remediation-report.md`.
- Task: [SL326-001](tasks/SL326-001.json), the single coherent design task.
- Coordinator handoff: `handoff.yaml`, an adapted U001 record, not native handoff-validator compliance.
- Verification assessment: `deferred-by-owner` under U001; no fake assessment instance.

## Acceptance Mapping

| Issue acceptance | Deliverable | Evidence boundary |
| --- | --- | --- |
| AC1: source-output mapping excludes history/custom | Design ownership/output tables, exact five-member manifest, inventory | Content inspection only; package behavior unexecuted |
| AC2: edit one skill and reach dev install | Design stable/development sequence; installed layout | Future path described; no implemented CLI claim |
| AC3: replacement versus delta; paired recovery | Design I/O table/recovery sequence; installation example | No rollback or data-conversion execution claim |
| AC4: bounded first move and later inventory | Inventory P2 list and P3-P7 dispositions | No whole-repository copy or old upgrade promise |
| AC5: design/examples/workflow/zh-TW and deferrals | Six design files and issue workflow | Readability/syntax/diff only, legacy checks deferred |

## P1-A Coordination

The coordinator supplied #325 exact names: skill `lesson`, `skill-package.yaml`, `SKILL.md`, family `lesson.record` / `1.0.0`, `schemas/lesson-record.schema.json`, `templates/lesson.md`, `references/operations.md`, tool `lesson.fs` with planned implementation and null entrypoint, required/optional lists empty. Its specimen root is `.dev/design/framework-next/portable-contracts/lesson/`; it owns config/schema/operation semantics. This task maps those references without copying schemas. Final combined-content cross-review remains coordinator work.

Concrete P1-B defaults: physical core/custom/lock under `.ai`; copied generated Codex entry `framework-lesson`; one exact manifest; stable generated installation tracked together; development candidate explicitly selected from a commit. These are proposals for implementation, not changes to current active root policy.

## Stages And Checkpoints

1. Verify Issue, U001, existing worktree and owning governance/templates.
2. Draft one coherent design/inventory/examples set and align public names through coordinator.
3. Read changed content; check syntax, links, diff and planned commit message.
4. Record completed design scope and deferred execution; create coherent local commit.
5. Send self-contained handoff to coordinator and stop before online integration.

## Resume Checkpoint

- Last completed action: six design artifacts authored and inspected; names aligned with P1-A; allowed checks and planned message format succeeded.
- Current task: `SL326-001`, completed for design delivery; implementation and runtime validation remain outside this workflow.
- Exact next action: coordinator reads this workflow's containing commit, cross-reviews #325/#326, organizes local commits and selects first push/PR integration.
- Validation: see `reports/remediation-report.md`; no legacy gate/test/package/CI success is claimed.
- Git state: dedicated local branch; resolve final delivery SHA from the containing commit; no push/PR/merge/Issue closure by this task.
- Blockers: none for design delivery. Coordinator reviews tracked-stable dogfood and first Codex entry choices before P2; P7 owns validation/CI.
- Index: suggested row in `handoff.yaml`; shared index is intentionally unchanged because coordinator owns it.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Reason | Resume Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-23-source-layout` | `main` at `53c9c8e58615e87e36f7b74ea8851fe845312daa` | Local design delivery | Resolve containing commit after local commit | No push; coordinator owns PR integration | U001 P1-B | Cross-review #325/#326 and organize commits before first push |
