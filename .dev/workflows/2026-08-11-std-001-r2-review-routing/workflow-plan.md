# Code Review File-Type And Finding-Scoped References

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-11-std-001-r2-review-routing`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-std-001-r2-review-routing`
- `base_branch`: `codex/2026-08-11-std-001-standards-simplification`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-r2-review-routing`
- `created_at`: `2026-08-11T20:20:48+08:00`
- `updated_at`: `2026-08-11T20:20:48+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #191 owns `ASM-20260811-003#CRL-001` and `CRL-002`: Code Reviewer entry and role references load broad duplicated material, omit consistent file-type routes, and contain semantic drift from canonical target-selection rules.
- Authorized remediation scope: implement entry/file-type/finding routing, reduce unconditional reference loading, designate canonical rule owners, retain compatibility entry paths, and add deterministic load/equivalence/package validation.
- Exclusions: governance terminology changes belong to #192; package navigation and component-closure changes belong to #193; product .NET source review, Project allocation, push, PR, merge, Issue closure, tag, Release, and publication are not authorized.
- Completion criteria: supported review file types have explicit bounded routes; general and specialist roles no longer load the same monolithic shared set unconditionally; checklist, severity, output, role applicability, and engineering semantics are equivalent; focused and aggregate validation pass; an independent verification assessment reconciles both findings.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-003/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-11-std-001-r2-review-routing/reports/remediation-report.md`
- Verification assessment: allocate after remediation validation.
- Tasks: `.dev/workflows/2026-08-11-std-001-r2-review-routing/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#CRL-001` | HIGH | `ai-context-governance` / `code-reviewer` | remediate | `STD191-001` | declared-load inventory, missing/unrelated route fixtures, package projection |
| `ASM-20260811-003#CRL-002` | HIGH | canonical engineering-rule and review-contract owners | remediate | `STD191-001` | rule-ID/owner equivalence, target-selection fixtures, independent assessment |

## Stages And Checkpoints

1. Baseline audit and evidence freeze. `completed`
2. Finding triage and remediation authorization. `completed`
3. Bounded remediation and validation. `in_progress`
4. Independent post-remediation audit. `pending`
5. Finding reconciliation, commit verification, and closure. `pending`

## Resume Checkpoint

- Last completed action: Created Issue #191, recorded owner implementation authorization, and branched from parent checkpoint `73b12c6`.
- Current task: `STD191-001`.
- Exact next action: inventory current Code Reviewer entry, role, reference, standard, validator, and package routes; then implement the smallest bounded routing contract.
- Validation already completed: parent baseline assessment `ASM-20260811-003` and workflow validators passed before branch creation.
- Git state: clean dedicated branch before workflow bootstrap; nothing from #191 is pushed or merged.
- Branch history and checkpoint handoffs: local stacked branch from the unpushed #61 coordination checkpoint.
- Blockers or unresolved decisions: none for local implementation; transport and integration remain unauthorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-r2-review-routing` | `codex/2026-08-11-std-001-standards-simplification@73b12c6` | local implementation start | pending | local | `2026-08-11T20:20:48+08:00` | Execute #191 as an independent rollback unit | Inventory and remediate Code Reviewer routing |
