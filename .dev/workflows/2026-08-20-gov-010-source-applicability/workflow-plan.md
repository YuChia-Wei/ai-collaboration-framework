# GOV-010 Source-Repository Effective-Rule Applicability

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-gov-010-source-applicability`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-20-gov-010-source-applicability`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `implementation-validated`
- `artifact_root`: `.dev/workflows/2026-08-20-gov-010-source-applicability`
- `created_at`: `2026-08-20T08:17:32+08:00`
- `updated_at`: `2026-08-20T08:46:07+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #219 demonstrates that action-skill effective-rule consumption cannot distinguish this framework source repository from an initialized downstream target without requiring fabricated downstream provenance.
- Authorized remediation scope: Define and validate explicit `framework-source` and `initialized-target` applicability, deterministic source execution evidence, consistent action-skill declarations, diagnostics, packaging exclusion, fixtures, and thin-wrapper parity.
- Exclusions: No downstream provenance fabrication, historical evidence rewrite, local roadmap/backlog mutation, tag or Release mutation, asset/package publication, nightly activation, or unrelated Issue implementation.
- Completion criteria: Issue #219 acceptance criteria pass at one exact clean head; a fresh independent read-only audit finds no release-blocking defect; hosted checks pass; the admitted PR terminal-closes #219; post-merge Issue and provider state are read back.

## Authority And Evidence

- Work-item authority: live GitHub Issue #219 and explicit repository-owner authorization.
- Execution evidence owner: this workflow only; it is not a second Issue tracker or Project roadmap.
- Source baseline: clean `main` and `origin/main` at `094670feab495137e3d5e30a62291e572a164028`.
- Current Project field recovery is owned by a separate user-owned thread and is not claimed complete here.

## Artifact Contract

- Baseline assessment: `not-applicable` (Issue #219 is the accepted defect contract).
- Remediation report: `.dev/workflows/2026-08-20-gov-010-source-applicability/reports/remediation-report.md`
- Verification assessment: to be created by a fresh independent exact-head auditor after implementation freezes.
- Tasks: `.dev/workflows/2026-08-20-gov-010-source-applicability/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `#219#GOV-010` | release-blocking | `ai-context-governance` | remediate | `GOV-010` | focused resolver, schema, declaration, package, wrapper, and repository governance checks |

## Stages And Checkpoints

1. Freeze live Issue, Git, canonical policy, resolver, schema, declaration, fixture, and package-boundary evidence.
2. Implement one explicit applicability contract and deterministic source execution packet without weakening initialized-target fail-closed behavior.
3. Run focused validation and update workflow evidence.
4. Commit one coherent bounded stage and obtain a fresh independent read-only exact-head audit.
5. Push, open one terminal-close PR, pass hosted and merge-admission gates, merge the admitted head, and read back #219.

## Resume Checkpoint

- Last completed action: Explicit source/target applicability, resolver evidence, action-skill contracts, diagnostics, source-only package exclusions, and focused fixtures were implemented and validated.
- Current task: `GOV-010`
- Exact next action: Commit and push the implementation checkpoint, create the terminal-close PR, add its declaration record, then freeze the final exact head for source execution evidence and independent audit.
- Validation already completed: 27 resolver tests passed with 2 existing skips; action-skill contract, focused package isolation, wrapper metadata, AI-context, source-governance, source-disposition, workflow-artifact, YAML parse, and diff checks passed. The broader package test-file attempt timed out after 124.025 seconds and is retained as failed non-gating evidence; its new single focused fixture subsequently passed in 1.383 seconds and no run-owned process or `.tmp/p` residue remained.
- Git state: branch `codex/2026-08-20-gov-010-source-applicability`; base `094670feab495137e3d5e30a62291e572a164028`; implementation checkpoint remains uncommitted.
- Branch history and checkpoint handoffs: Segment 1 created directly from clean `main`; no handoff or checkpoint integration.
- Blockers or unresolved decisions: None for source implementation. Project Target release restoration is independently owned and must be read back before final v0.14 release readiness.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-gov-010-source-applicability` | `main@094670feab495137e3d5e30a62291e572a164028` | active | pending | local | `2026-08-20T08:17:32+08:00` | Terminal-close #219 delivery | Commit the validated implementation checkpoint and create the PR before final exact-head closeout. |
