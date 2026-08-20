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
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-20-gov-010-source-applicability`
- `created_at`: `2026-08-20T08:17:32+08:00`
- `updated_at`: `2026-08-20T08:49:21+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #219 demonstrates that action-skill effective-rule consumption cannot distinguish this framework source repository from an initialized downstream target without requiring fabricated downstream provenance.
- Authorized remediation scope: Define and validate explicit `framework-source` and `initialized-target` applicability, deterministic source execution evidence, consistent action-skill declarations, diagnostics, packaging exclusion, fixtures, and thin-wrapper parity.
- Exclusions: No downstream provenance fabrication, historical evidence rewrite, local roadmap/backlog mutation, tag or Release mutation, asset/package publication, nightly activation, or unrelated Issue implementation.
- Technical workflow completion criteria: The #219 source change, task, focused verification, remediation report, and terminal-close declaration are complete on the PR branch. Fresh exact-head audit, hosted checks, merge admission, integration, and post-merge Issue/Project read-back remain separate provider gates and are recorded online without a post-audit source mutation.

## Authority And Evidence

- Work-item authority: live GitHub Issue #219 and explicit repository-owner authorization.
- Execution evidence owner: this workflow only; it is not a second Issue tracker or Project roadmap.
- Source baseline: clean `main` and `origin/main` at `094670feab495137e3d5e30a62291e572a164028`.
- Current Project field recovery is owned by a separate user-owned thread and is not claimed complete here.

## Artifact Contract

- Baseline assessment: `not-applicable` (Issue #219 is the accepted defect contract).
- Remediation report: `.dev/workflows/2026-08-20-gov-010-source-applicability/reports/remediation-report.md`
- Verification assessment: a fresh read-only exact-head auditor returns transient findings and the passing online `github-terminal-issue-closure-audit/v1` receipt; no post-audit tracked mutation is permitted.
- Tasks: `.dev/workflows/2026-08-20-gov-010-source-applicability/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `#219#GOV-010` | release-blocking | `ai-context-governance` | remediate | `GOV-010` | focused resolver, schema, declaration, package, wrapper, and repository governance checks |

## Stages And Checkpoints

1. Freeze live Issue, Git, canonical policy, resolver, schema, declaration, fixture, and package-boundary evidence.
2. Implement one explicit applicability contract and deterministic source execution packet without weakening initialized-target fail-closed behavior.
3. Run focused validation and update workflow evidence.
4. Commit the coherent implementation stage, open one terminal-close PR, and close the technical workflow with its declaration and remediation report.
5. Freeze the final source head, obtain a fresh independent read-only audit, pass hosted and merge-admission gates, merge the admitted head, and record #219 read-back online without mutating the audited source head.

## Resume Checkpoint

- Last completed action: Implementation checkpoint `19d2c952014c2a135bd9a34824cf9e5610932ec8` was committed, validated through actual clean framework-source execution, pushed, and opened as PR #223.
- Current task: `GOV-010`
- Exact next action: Commit and push the PR #223 terminal-close declaration and remediation report, then perform the separate provider gates against that immutable source head.
- Validation already completed: 27 resolver tests passed with 2 existing skips; action-skill contract, focused package isolation, wrapper metadata, AI-context, source-governance, source-disposition, workflow-artifact, YAML parse, and diff checks passed. The broader package test-file attempt timed out after 124.025 seconds and is retained as failed non-gating evidence; its new single focused fixture subsequently passed in 1.383 seconds and no run-owned process or `.tmp/p` residue remained.
- Git state: branch `codex/2026-08-20-gov-010-source-applicability`; base `094670feab495137e3d5e30a62291e572a164028`; implementation checkpoint `19d2c952014c2a135bd9a34824cf9e5610932ec8` is pushed and PR #223 is open.
- Branch history and checkpoint handoffs: Segment 1 created directly from clean `main`; no handoff or checkpoint integration.
- Blockers or unresolved decisions: None for source implementation. Project Target release restoration is independently owned and must be read back before final v0.14 release readiness.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-gov-010-source-applicability` | `main@094670feab495137e3d5e30a62291e572a164028` | technical-completion | `19d2c952014c2a135bd9a34824cf9e5610932ec8` | `origin` / PR #223 | `2026-08-20T08:49:21+08:00` | Terminal-close #219 delivery | Commit the declaration/report and freeze the resulting source head for provider admission. |
