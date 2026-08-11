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
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-r2-review-routing`
- `created_at`: `2026-08-11T20:20:48+08:00`
- `updated_at`: `2026-08-11T20:54:00+08:00`
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
- Verification assessment: `.dev/assessments/ASM-20260811-004/assessment.yaml`.
- Tasks: `.dev/workflows/2026-08-11-std-001-r2-review-routing/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#CRL-001` | HIGH | `ai-context-governance` / `code-reviewer` | remediate | `STD191-001` | declared-load inventory, missing/unrelated route fixtures, package projection |
| `ASM-20260811-003#CRL-002` | HIGH | canonical engineering-rule and review-contract owners | remediate | `STD191-001` | rule-ID/owner equivalence, target-selection fixtures, independent assessment |

## Stages And Checkpoints

1. Baseline audit and evidence freeze. `completed`
2. Finding triage and remediation authorization. `completed`
3. Bounded remediation and validation. `completed`
4. Independent post-remediation audit. `completed`
5. Finding reconciliation, commit verification, and closure. `completed`

## Resume Checkpoint

- Last completed action: Finalized `ASM-20260811-004`, which independently reconciles CRL-001/002 as addressed at fixed subject `8b5b402` with no new blocking finding.
- Current task: `STD191-001`.
- Exact next action: commit local #191 workflow closeout, then return to the #61 coordination branch and start #192 from its authorized parent checkpoint.
- Validation already completed: focused routing/package contract 8/8, role execution 6/6, adapter 31/31, wrapper 16/16, language/parity 10/10, profile/document/effective-rule contracts, shell registry, and `validate-ai-context.py` passed. The full packaging matrix timed out at 244 seconds and remains recorded as failed.
- Git state: implementation `aea7a44`, package guard `a5cece2`, phase-lazy correction `8b5b402`, and verification assessment `0f200cf`; nothing from #191 is pushed or merged.
- Branch history and checkpoint handoffs: local stacked branch from the unpushed #61 coordination checkpoint.
- Blockers or unresolved decisions: none for local implementation; transport and integration remain unauthorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-r2-review-routing` | `codex/2026-08-11-std-001-standards-simplification@73b12c6` | implementation checkpoint | `aea7a44` | local | `2026-08-11T20:44:00+08:00` | Execute #191 as an independent rollback unit | Commit focused package guard, then independently audit fixed snapshot |
| 1 | `codex/2026-08-11-std-001-r2-review-routing` | `aea7a44` | verification checkpoint | `8b5b402`, `0f200cf` | local | `2026-08-11T20:53:00+08:00` | Finish phase-lazy correction and independent verification | Close local workflow; transport/integration remain separate |
