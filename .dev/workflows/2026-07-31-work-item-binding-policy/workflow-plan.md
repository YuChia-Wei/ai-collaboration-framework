# Work-Item Binding And Merge-Gate Selection

## Workflow Metadata

- `workflow_id`: `2026-07-31-work-item-binding-policy`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-31-work-item-binding-policy-closeout`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-07-31-work-item-binding-policy`
- `created_at`: `2026-07-31T00:06:18+08:00`
- `updated_at`: `2026-07-31T00:29:59+08:00`

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
| `WIBIND-001` | Define, validate, integrate, and read back the work-item binding selection contract. | `completed` |

## Boundary Decisions

- Binding validity requires explicit owner approval; provider state alone remains non-authoritative.
- Work-item binding controls execution entry, while merge-gate selection independently controls integration enforcement.
- `optional` permits an explicitly recorded no-Issue authorization; it does not make authorization optional.
- The source GitHub provider selection is source-only and must not become a downstream default.
- Downstream selections are target-owned truth under `.dev/project-config.yaml` and survive framework upgrades through customization reconciliation.

## Resume Checkpoint

- Last completed action: read back merge commit `d4d9220d328068043b990494f9171ea13078b4e7` from `main` after PR #73 and all required hosted checks passed.
- Current task: completed; this continuation branch records closeout evidence only.
- Exact next action: merge the closeout-only pull request into `main`.
- Validation already completed: focused Python contracts, AI-context and workflow validators, direct .NET child tests, commit-range validation, and all three hosted checks for PR #73.
- Git state: closeout continuation branch from merged `main@d4d9220`.
- Blockers or unresolved decisions: overlapping work in another session is owner-managed and does not block this branch.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-31-work-item-binding-policy` | `main@618ceb0` | integration | `12e513d977cfc4aa095b9038ca2150df65086d7b` | PR #73 / `main@d4d9220` | `2026-07-31T00:28:47+08:00` | Implement and validate the owner-approved provider-neutral binding contract. | Start a continuation branch from merged main and record closeout evidence. |
| 2 | `codex/2026-07-31-work-item-binding-policy-closeout` | `main@d4d9220` | closeout | pending | closeout PR / `main` | `2026-07-31T00:29:59+08:00` | Persist merge read-back and completed workflow state. | Merge the closeout-only PR; no implementation work remains. |
