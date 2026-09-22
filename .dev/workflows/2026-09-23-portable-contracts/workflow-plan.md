# Portable Contracts Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-23-portable-contracts`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-23-portable-contracts`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-23-portable-contracts`
- `created_at`: `2026-09-23T01:09:27+08:00`
- `updated_at`: `2026-09-23T01:21:23+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

Deliver [Issue #325](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/325), P1-A of #322: the smallest implementable portable skill package, project configuration and filesystem artifact contracts, illustrated by one standalone Lesson skill. Source: assessment A1-A3/A6 and its execution-plan.md U001. The task delegation authorizes this design and local commits; it reserves first push, PR, merge and Issue closure to the coordinator.

Write only `.dev/design/framework-next/portable-contracts/` and this workflow. No product relocation, root/shared edits, universal package manager, provider sync, full migration engine, release or adoption. #326 owns source/consumer layout; report interface choices through the coordinator.

Completion criteria are Issue acceptance 1-5: declared closure, clear owners/configurable paths, schema/tool/operation dispositions without fabricated execution, one skill/store/schema family, concrete design plus this workflow and a concise zh-TW explanation.

## Artifact Contract

- Baseline: `.dev/assessments/ASM-20260923-00-6oq/assessment.yaml` (read-only).
- Authority: `.dev/assessments/ASM-20260923-00-6oq/execution-plan.md`, U001.
- Input handoff: `.dev/workflows/2026-09-23-framework-redesign-control/handoffs/issue-325.yaml`.
- Design: `.dev/design/framework-next/portable-contracts/README.md` and linked contracts/examples.
- Task: `tasks/T001-portable-contracts.json`.
- Report: `reports/remediation-report.md` (content review and U001 dispositions).
- Verification assessment: deferred-by-owner until P7 under U001; not invented.
- Shared workflow index: coordinator-owned; supply a row in the delivery handoff.

## Finding Triage

| Source | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- |
| Issue #325 acceptance 1-5; assessment A1-A3/A6 | ai-context-governance | Bounded design | T001-portable-contracts | Direct readability/content review only |

This is an authorized design task, not a claim that all assessment findings have been remediated. One substantive task is sufficient: workflow mode preserves the explicit U001 exception, cross-Issue ownership and first-push handoff. Extra tasks would repeat the same delivery boundary.

## Stages And Checkpoints

1. Confirm Issue scope, starting commit and dedicated worktree; create this workflow.
2. Author one coherent contract/example set.
3. Inspect contents, parse JSON/YAML, check whitespace and exact planned commit message.
4. Record local completion and hand off to coordinator; stop before first push.

U001 supersedes template audit/critical/legacy validation stages. Legacy validators, check-all/critical gates, test suites, package/upgrade/migration trials, independent validation-only audits and CI remain **deferred-by-owner** until P7. Direct JSON/YAML parsing, file read-back, Git checks and existing commit-message format checking are allowed. No CI observation here is a passing CI result.

## Resume Checkpoint

- Last completed action: design/example authored and read back; direct JSON/YAML parsing, scoped diff and exact commit-message format checks passed.
- Current task: none; T001-portable-contracts completed for design scope.
- Exact next action: coordinator reads handoff.yaml, reviews #325/#326 interfaces and arranges first push/PR; no implementation work remains in this issue-owned workflow.
- Validation already completed: direct UTF-8 reads/JSON-YAML parsing, manual content and scope review, git diff --cached --check and exact planned commit-message validation. Runtime/legacy checks remain deferred-by-owner until P7.
- Git state: starting `53c9c8e58615e87e36f7b74ea8851fe845312daa`, assigned worktree `F:/framework-next/325`.
- Blockers: none; no runtime implementation or behavioral validation is claimed.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | codex/2026-09-23-portable-contracts | main at 53c9c8e58615e87e36f7b74ea8851fe845312daa | local design | containing commit of handoff.yaml | none | 2026-09-23T01:09:27+08:00 | Independent P1-A | Coordinator review before first push |

The coordinator selects final commit organization and integration topology. A local commit does not mean merged, released, adopted or Issue closed.

## Delivery And Coordination

- Stable package `lesson`, metadata `skill-package.yaml`, schema `lesson.record@1.0.0` at `schemas/lesson-record.schema.json`, default template `templates/lesson.md`, planned tool `lesson.fs`.
- Added package-owned `references/configuration.md` alongside `references/operations.md`; #326 should include both by reference without copying their semantics.
- #326 physical source/install/projection design is compatible; this task does not edit its subtree or shared indexes.
- Completed means the bounded design is delivered. Runtime implementation belongs to P2, lifecycle to P3-A and validation to P7. Push/PR/merge/Issue closure remain coordinator actions.
