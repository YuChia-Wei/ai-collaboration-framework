# Portable Environment Execution Routing

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-14-environment-execution-routing`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-14-environment-execution-routing`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `audit`
- `artifact_root`: `.dev/workflows/2026-08-14-environment-execution-routing`
- `created_at`: `2026-08-14T21:40:34+08:00`
- `updated_at`: `2026-08-14T21:40:34+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #210 identifies the missing boundary between portable environment readiness and deterministic execution routing. Repeated host, sandbox, WSL, CLI, and connector failures cannot be safely prevented while concrete routes exist only in conversation memory or tracked repository guidance.
- Authorized remediation scope: Implement the owner-approved Issue #210 contract: Git tracks only the portable contract/schema, non-personal enforcement, and the ignore rule; personal route values remain in a conventional Git-ignored local file; after bounded diagnosis succeeds, the agent must ask before persisting the reusable route.
- Exclusions: Do not write a personal local binding without a separate post-recovery consent decision. Do not store credentials, tokens, sessions, private endpoints, usernames, or source-host defaults in tracked files. Do not push, open a pull request, merge, release, or publish.
- Completion criteria: A portable contract and schema define route, readiness, evidence, retry, fallback, consent, and storage semantics; the conventional local path is proven Git-ignored; deterministic validation rejects tracked, sensitive, ambiguous, or unauthorized bindings; downstream packaging exposes the portable contract but excludes personal values; focused Windows and Ubuntu-24.04 validation passes; independent verification is recorded after the owner reviews the result shape.

## Authorization And Delivery

- Work item: GitHub Issue `#210`, `[TOOL-005] Define Portable Environment Execution Routing Standard`.
- Authorization: Owner message on 2026-08-14: `OK，進行實作，我要看成果的樣態再跟你說怎麼調整`.
- Delivery cohesion: Contract, local-binding boundary, validation, package projection, and agent behavior form one atomic portable capability and share one review, rollback, and compatibility boundary.
- Workflow justification: This changes canonical portable rules and future agent behavior across `.ai`, `.dev`, runtime discovery, packaging, and validation. The workflow preserves the owner review checkpoint before independent verification and closure.
- Planned topology: Linear integration is the initial recommendation because this is one coherent capability; integration remains owner-controlled and may be reconsidered if later review creates a durable approval or handoff boundary.

## Artifact Contract

- Baseline assessment: `not-applicable`; Issue #210 plus completed readiness Issue #147 are the approved design baseline.
- Remediation report: `.dev/workflows/2026-08-14-environment-execution-routing/reports/remediation-report.md`
- Verification assessment: `pending owner review`; independent post-remediation verification will receive a new assessment ID if the reviewed implementation proceeds to closure.
- Tasks: `.dev/workflows/2026-08-14-environment-execution-routing/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `Issue-210-contract` | high | `ai-context-governance` | implement | `ENVROUTE-001-contract-schema` | schema and contract tests |
| `Issue-210-local-persistence` | high | `ai-context-governance` | implement | `ENVROUTE-002-local-binding` | ignore, consent, and sensitive-field negative tests |
| `Issue-210-downstream` | high | `ai-context-governance` | implement | `ENVROUTE-003-downstream-integration` | package, init/upgrade, Windows, and WSL checks |
| `Issue-210-verification` | high | `ai-context-auditor` | pending owner review | `VERIFY-001-independent-audit` | independent read-only assessment |

## Stages And Checkpoints

1. Freeze Issue #210 authorization and inventory existing readiness, package, init, upgrade, and validation boundaries. `in_progress`
2. Implement the provider-neutral contract and schema. `pending`
3. Implement Git-ignored local-binding validation and post-recovery consent behavior. `pending`
4. Integrate downstream packaging and compatibility checks. `pending`
5. Run focused Windows and explicit `Ubuntu-24.04` WSL validation outside the sandbox. `pending`
6. Present the implementation shape for owner review and adjustment. `pending`
7. After owner review, obtain independent verification and reconcile the workflow. `pending`

## Resume Checkpoint

- Last completed action: Created the dedicated workflow branch from clean `main` aligned with `origin/main`.
- Current task: `ENVROUTE-001-contract-schema`.
- Exact next action: Inventory the readiness schema, distribution allowlist, target validator, init/upgrader boundaries, indexes, and related tests before selecting exact artifact paths.
- Validation already completed: Branch preflight only; implementation validation has not started.
- Git state: Clean branch `codex/2026-08-14-environment-execution-routing` based on current `main`; no push, pull request, or merge.
- Branch history and checkpoint handoffs: None.
- Blockers or unresolved decisions: Exact schema and local settings paths remain to be selected from repository conventions. The owner review checkpoint intentionally precedes independent verification and workflow closure.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-14-environment-execution-routing` | `main` | local-active | pending | local | `2026-08-14T21:40:34+08:00` | Authorized Issue #210 implementation with an owner review checkpoint | Continue `ENVROUTE-001-contract-schema` on the same branch |
