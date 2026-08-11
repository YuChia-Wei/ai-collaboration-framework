# Qualified Governance Terms And Source Release Doctrine Separation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-11-std-001-r3-governance-terms`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-std-001-r3-governance-terms`
- `base_branch`: `codex/2026-08-11-std-001-standards-simplification`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-r3-governance-terms`
- `created_at`: `2026-08-11T20:58:53+08:00`
- `updated_at`: `2026-08-11T21:37:32+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #192 owns `ASM-20260811-003#GTM-001`: active governance guidance reuses bare lifecycle, candidate, integration, publication, closeout, finalization, and validated terms across different authorities, while portable target guidance can expose source-release-only doctrine.
- Authorized remediation scope: extend the existing AI-context ownership registry with compact qualified term routing; keep definitions with their existing domain owners; distinguish source release, package candidate, repository integration, workflow completion, assessment finality, hosted publication, and publication finalization; separate source-only release procedure from portable target version/provenance/upgrade guidance; add bounded validators and compatibility dispositions.
- Exclusions: Code Reviewer routing belongs to #191; broken payload navigation and component closure belong to #193; historical workflow/assessment/release evidence is immutable; Project allocation, push, PR, merge, Issue closure, tag, Release, and publication are not authorized.
- Completion criteria: active terms have a machine-readable namespace/owner route and contextual shorthand policy; bare terms cannot imply cross-owner authority; portable target instructions exclude source-release procedure; existing machine literals remain compatible; focused and aggregate validation pass; an independent verification assessment reconciles `GTM-001`.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-003/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-11-std-001-r3-governance-terms/reports/remediation-report.md`
- Planned verification assessment: `.dev/assessments/ASM-20260811-005/assessment.yaml`.
- Tasks: `.dev/workflows/2026-08-11-std-001-r3-governance-terms/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#GTM-001` | HIGH | `ai-context-governance` plus existing domain owners | remediate | `STD192-001` | term-route inventory, forbidden ambiguity fixtures, source/portable projection, independent assessment |

## Stages And Checkpoints

1. Baseline audit and evidence freeze. `completed`
2. Finding triage and remediation authorization. `completed`
3. Bounded remediation and validation. `completed`
4. Independent post-remediation audit. `completed`
5. Finding reconciliation and local closure. `completed`

## Resume Checkpoint

- Last completed action: Finalized independent verification `ASM-20260811-005`, which reconciled `GTM-001` as addressed at fixed subject `fe85095` with no new blocking finding.
- Current task: none; `STD192-001` is completed.
- Exact next action: record #192 local completion on the parent #61 workflow, then execute #193 against a deliberately combined local package view without inferring remote integration authority.
- Validation already completed: governance routing 8/8; AI-context validator passed with 15 qualified terms; final fast profile selected 32 required checks with 12 executed, 20 evidence-reused, 0 failed, and 0 blocked; package smoke 1/1 outside the filesystem sandbox; 625 selected paths and 369 packaged Markdown documents contained no source-release command or source-policy link; assessment and workflow artifact validators passed.
- Git state: dedicated local branch `codex/2026-08-11-std-001-r3-governance-terms`; implementation fixed at `fe85095`, assessment at `5299db5`, and terminal records are carried by the containing closeout commit; nothing is pushed or merged.
- Branch history and checkpoint handoffs: #191 remains isolated at `f62f110`; this branch contains no #191 implementation commits. Two earlier `3c85863` aggregate source-governance timeouts remain failed receipts even though later exact-environment and final-subject runs passed.
- Blockers or unresolved decisions: none for local #192 completion. Project allocation, transport, integration, Issue closure, tag, Release, and publication remain unauthorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | workflow bootstrap | `10581e8` | local | `2026-08-11T20:58:53+08:00` | Execute #192 as an independent rollback unit | Implement the qualified term registry and source/portable policy split |
| 1 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | implementation checkpoint | `3c85863`, `fe85095` | local | `2026-08-11T21:30:58+08:00` | Qualify 15 terms, separate source release procedure, project the portable target policy, and correct release-phase machine binding | Run independent fixed-subject verification |
| 1 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | independent verification checkpoint | `5299db5`, plus containing closeout commit | local | `2026-08-11T21:37:32+08:00` | Reconcile `GTM-001` as addressed and preserve time-specific failure/advisory evidence | Update parent #61 coordination; keep all remote actions separate |
