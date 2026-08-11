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
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-11-ctx-009-sdk-free-baseline`
- `created_at`: `2026-08-11T08:21:27+08:00`
- `updated_at`: `2026-08-11T10:16:43+08:00`
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
| `ASM-20260811-001#SDKGATE-001` | high | `ai-context-governance` | remove required framework SDK selection | `CTX009-002` | registry/runner checks, controlled no-`dotnet` validation |
| `ASM-20260811-001#SDKPAYLOAD-001` | high | `ai-context-governance` | remove compilable payload and SDK seed | `CTX009-002` | distribution and package projection validation |
| `ASM-20260811-001#SDKEVID-001` | high | `ai-context-governance` | reclassify source-include evidence | `CTX009-002` | evidence manifest and Python structural contract |
| `ASM-20260811-001#SDKPROV-001` | high | `ai-context-governance` | replace implementation activation with target-selected recipe | `CTX009-002` | recipe, index, mapping, and reference validation |
| `ASM-20260811-001#SDKDOC-001` | medium | `ai-context-governance` | reconcile active guidance and tests | `CTX009-002` | link, context, registry, and focused contract validation |
| `#187` independent verification | high | `ai-context-auditor` | verify after remediation | `CTX009-003` | `ASM-20260811-002` and finding reconciliation |

## Stages And Checkpoints

1. Freeze the remote `main` and #187/Project authorization baseline, then create the dedicated workflow branch and artifacts. `completed`
2. Produce `ASM-20260811-001` as a read-only inventory of every active framework-owned .NET SDK dependency and affected contract surface. `completed`
3. Remove or reclassify framework-owned compilable .NET implementation and required release gates while preserving canonical engineering semantics and target-owned on-demand guidance. `completed`
4. Run repository-native validation, including controlled execution with `dotnet` unavailable from `PATH`, and record exact outcomes. `completed`
5. Produce independent verification `ASM-20260811-002`, reconcile every finding, and close the local workflow only when commit and validation policy are satisfied. `completed`

## Resume Checkpoint

- Last completed action: Finalized independent verification `ASM-20260811-002`, which addressed all five baseline findings and found no new blocking issue.
- Current task: none; `CTX009-001`, `CTX009-002`, and `CTX009-003` are completed.
- Exact next action: Wait for separate owner authorization before any push or pull-request creation.
- Validation already completed: SDK-free 5/5; fail-closed 38/38; dependency 17/17 plus live zero-managed-project result; final package matrix 36 passed and 1 external-downstream skip; controlled no-`dotnet` PR receipt 37 selected checks passed with 15 executed and 22 fingerprint-reused, 18 unselected entries not-applicable, 0 failed, and 0 blocked; assessment, workflow, source-governance, AI-context, and focused package contracts passed.
- Git state: Dedicated local branch `codex/2026-08-11-ctx-009-sdk-free-baseline`; implementation is committed through `889493a`; `ASM-20260811-002` and these terminal records are carried by the containing closeout commit.
- Branch history and checkpoint handoffs: Segment 1 is locally complete; no push, pull request, merge, Issue closure, tag, or publication exists.
- Blockers or unresolved decisions: None for local #187 completion. Hosted integration, external downstream validation, Issue closure, and v0.13.0 publication remain separate owner decisions.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-ctx-009-sdk-free-baseline` | `main@a4fd14f0` | local verification checkpoint | `7652e5f1`, `2e40c69e`, `4abb7f1`, `3fdd7a1`, `889493a`, plus containing closeout commit | local | `2026-08-11T10:16:43+08:00` | Complete the authorized #187 SDK-free baseline, preserve failed/interim receipts, and obtain independent verification | Await separate owner authorization for push and pull-request creation |
