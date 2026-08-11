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
- `status`: `in_progress`
- `current_phase`: `bounded-remediation`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-r3-governance-terms`
- `created_at`: `2026-08-11T20:58:53+08:00`
- `updated_at`: `2026-08-11T20:58:53+08:00`
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
3. Bounded remediation and validation. `in_progress`
4. Independent post-remediation audit. `pending`
5. Finding reconciliation and local closure. `pending`

## Resume Checkpoint

- Last completed action: Read back the open Issue #192 scope and owner authorization comment, then created this dedicated branch from the updated #61 coordination checkpoint `088fee7`.
- Current task: `STD192-001`.
- Exact next action: inventory the active owners, machine literals, portable projections, schemas, validators, and source-release consumers; then implement the smallest qualified routing and doctrine split.
- Validation already completed: #61 baseline assessment `ASM-20260811-003` and R3 terminology matrix are final; live Issue authorization was read back.
- Git state: local branch `codex/2026-08-11-std-001-r3-governance-terms` at parent `088fee7`; nothing from #192 is pushed or merged.
- Branch history and checkpoint handoffs: #191 remains isolated at `f62f110`; this branch contains no #191 implementation commits.
- Blockers or unresolved decisions: none for local implementation; transport and integration remain unauthorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | workflow bootstrap | pending | local | `2026-08-11T20:58:53+08:00` | Execute #192 as an independent rollback unit | Inventory active term owners and portable/source release projections |
