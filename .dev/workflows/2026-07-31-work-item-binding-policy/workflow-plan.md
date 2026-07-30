# Work-Item Binding And Merge-Gate Selection

## Workflow Metadata

- `workflow_id`: `2026-07-31-work-item-binding-policy`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-31-work-item-binding-policy`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-07-31-work-item-binding-policy`
- `created_at`: `2026-07-31T00:06:18+08:00`
- `updated_at`: `2026-07-31T00:22:24+08:00`

## Objective And Scope

- Define a valid work-item binding as both traceability and execution-authorization evidence.
- Keep raw Issue existence, provider state, and Project automation from authorizing work without explicit owner approval.
- Let each target team select work-item binding and PR merge-gate modes independently as `required`, `optional`, or `disabled`.
- Select `optional` for both modes in this source repository.
- Leave downstream template selections unresolved until the target team explicitly decides them.
- Exclude online Issue creation, backlog promotion, release allocation, and automatic hosted merge-gate implementation.

## Authorization Record

- On 2026-07-31, the owner selected traceability plus work authorization as the two work-item binding purposes.
- The owner requested a controllable PR merge gate, selected optional behavior for this repository, and delegated downstream selection to each installing team.
- The owner explicitly authorized implementation and direct merge to `main` without a source Issue; this is valid under the source repository's selected optional mode.
- The owner will reconcile overlapping development-rule work in another conversation.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `WIBIND-001` | Define, validate, integrate, and read back the work-item binding selection contract. | `in_progress` |

## Boundary Decisions

- Binding validity requires explicit owner approval; provider state alone remains non-authoritative.
- Work-item binding controls execution entry, while merge-gate selection independently controls integration enforcement.
- `optional` permits an explicitly recorded no-Issue authorization; it does not make authorization optional.
- The source GitHub provider selection is source-only and must not become a downstream default.
- Downstream selections are target-owned truth under `.dev/project-config.yaml` and survive framework upgrades through customization reconciliation.

## Resume Checkpoint

- Last completed action: validated the policy, provider, target template, schema, wrapper registration, workflow, packaging, repository configuration, and .NET child tests.
- Current task: integrate the validated contract through pull-request-only `main`.
- Exact next action: commit, push, open the pull request, and verify hosted checks.
- Validation already completed: focused Python contracts, AI-context and workflow validators, the 45-check quick gate with three Bash-PATH environment failures, and the same three .NET child commands passing directly on Windows.
- Git state: dedicated branch from `main@618ceb0`.
- Blockers or unresolved decisions: overlapping work in another session is owner-managed and does not block this branch.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-31-work-item-binding-policy` | `main@618ceb0` | active remediation | pending | local | `2026-07-31T00:06:18+08:00` | Implement the owner-approved provider-neutral binding contract. | Validate, commit, push, open PR, and merge after hosted checks. |
