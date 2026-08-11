# v0.13 SDK-Free Framework Baseline

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-11-ctx-009-sdk-free-baseline`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-ctx-009-sdk-free-baseline`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `audit`
- `artifact_root`: `.dev/workflows/2026-08-11-ctx-009-sdk-free-baseline`
- `created_at`: `2026-08-11T08:21:27+08:00`
- `updated_at`: `2026-08-11T08:21:27+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Framework-owned source and release validation currently selects compilable .NET analyzer, runtime-validation, and BuildingBlocks test surfaces. This makes the framework release baseline depend directly on the .NET SDK even though downstream adoption is intended to remain portable and provider-selectable.
- Authorized remediation scope: Implement GitHub Issue #187 for the v0.13.0 delivery. Remove required framework-owned .NET build/test gates and distributable compilable provider implementation, convert the analyzer path to target-selected on-demand project creation guidance, retain canonical engineering semantics and bounded reference material, and obtain independent before/after AI-context evidence.
- Exclusions: Do not implement or publish `EngineeringGuardrails.Contracts.*` from #179; do not create a replacement framework-owned NuGet analyzer, `dotnet tool`, or precompiled CLI; do not rewrite existing tags, releases, final assessments, or completed workflows; do not push, open a pull request, merge, close Issues, tag, or publish without separate authorization.
- Completion criteria: Every #187 acceptance criterion is directly evidenced; framework-owned required checks pass with `dotnet` unavailable from `PATH`; active registries, runners, distribution contracts, indexes, provider manifests, activation contracts, examples, validators, and release guidance agree on the SDK-free boundary; an independent post-remediation audit has no unaddressed active finding.

## Authorization And Delivery

- Work item: [GitHub Issue #187](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/187), live-read as `OPEN` on 2026-08-11.
- Project read-back: Project #3 records `Status=Inbox`, `Target release=v0.13.0`, `Owner review=Approved`, `Published in=Not yet published`, and no Priority value.
- Implementation authorization: Owner message on 2026-08-11: `開始處理 0.13 的作業`. This authorizes local implementation of #187 and its required workflow/audit records; transport, integration, Issue closure, tag, and publication remain separate decisions.
- Delivery cohesion: #187 is one coherent SDK-free baseline delivery with shared source, distribution, validation, audit, review, and rollback boundaries. #179 remains an independent Contracts-adoption lifecycle and is not bound to this workflow.
- Workflow-value decision: Workflow mode preserves unique baseline inventory, canonical/provider remediation, no-`dotnet` acceptance evidence, and independent verification state across several ownership boundaries.
- Planned integration gate: Pull request to `main`, only after separate owner authorization for push and pull-request creation.
- Planned topology: Merge commit, because the baseline audit, multi-surface remediation, and independent verification form a durable review and rollback unit. Final selection remains subject to the pull-request gate and owner decision.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-11-ctx-009-sdk-free-baseline/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260811-002/assessment.yaml`
- Tasks: `.dev/workflows/2026-08-11-ctx-009-sdk-free-baseline/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `#187` framework-owned SDK gates | high | `ai-context-governance` | inventory and remediate | `CTX009-001`, `CTX009-002` | baseline assessment, registry/runner checks, controlled no-`dotnet` validation |
| `#187` bundled provider boundary | high | `ai-context-governance` | replace implementation contract with target-selected guidance | `CTX009-002` | distribution projection, provider/index/reference validation |
| `#187` retained example evidence | medium | `ai-context-governance` | classify and validate | `CTX009-002` | example manifest and direct file evidence |
| `#187` independent verification | high | `ai-context-auditor` | verify after remediation | `CTX009-003` | `ASM-20260811-002` and finding reconciliation |

## Stages And Checkpoints

1. Freeze the remote `main` and #187/Project authorization baseline, then create the dedicated workflow branch and artifacts. `completed`
2. Produce `ASM-20260811-001` as a read-only inventory of every active framework-owned .NET SDK dependency and affected contract surface. `in_progress`
3. Remove or reclassify framework-owned compilable .NET implementation and required release gates while preserving canonical engineering semantics and target-owned on-demand guidance. `pending`
4. Run repository-native validation, including controlled execution with `dotnet` unavailable from `PATH`, and record exact outcomes. `pending`
5. Produce independent verification `ASM-20260811-002`, reconcile every finding, and close the local workflow only when commit and validation policy are satisfied. `pending`

## Resume Checkpoint

- Last completed action: Confirmed clean `main` and remote SHA `a4fd14f0f08ad53859df1c860db0eb9643cdb2de`, live-read #187 and Project #3, selected workflow mode, and created the dedicated branch and workflow bootstrap.
- Current task: `CTX009-001`.
- Exact next action: Use `ai-context-auditor` to create the read-only baseline assessment `ASM-20260811-001`, inventorying every active SDK gate and provider/distribution/reference dependency before material context remediation.
- Validation already completed: Git worktree/branch and remote SHA read-back; #187 and Project #3 live read-back; workflow gate, artifact policy, branch policy, commit policy, AI-context boundary, and language policy intake.
- Git state: Dedicated branch `codex/2026-08-11-ctx-009-sdk-free-baseline` from clean `main` at `a4fd14f0f08ad53859df1c860db0eb9643cdb2de`; workflow bootstrap is uncommitted.
- Branch history and checkpoint handoffs: Segment 1 is local only; no push, pull request, merge, tag, or publication exists.
- Blockers or unresolved decisions: None for local #187 execution. Push, pull request, merge, Issue closure, tag, and v0.13.0 publication remain unrequested.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-ctx-009-sdk-free-baseline` | `main@a4fd14f0` | local-active | pending | local | `2026-08-11T08:21:27+08:00` | Authorized #187 SDK-free baseline delivery | Complete `CTX009-001` baseline audit before remediation |
