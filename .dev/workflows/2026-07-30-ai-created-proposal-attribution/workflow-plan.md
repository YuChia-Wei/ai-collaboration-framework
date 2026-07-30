# AI-Created Proposal Attribution

## Workflow Metadata

- `workflow_id`: `2026-07-30-ai-created-proposal-attribution`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-30-ai-created-proposal-attribution`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-07-30-ai-created-proposal-attribution`
- `created_at`: `2026-07-30T23:33:42+08:00`
- `updated_at`: `2026-07-30T23:36:20+08:00`

## Objective And Scope

- Require every AI-created GitHub Issue, including a Proposal, to receive the `created-by:codex` label in its creation request.
- Keep human-submitted Proposal forms attribution-neutral so GitHub user authorship is not mislabeled.
- Preserve the existing detailed hidden marker requirement for projected formal Story and Enabler Issues without extending that marker to Proposals.
- Record Proposal #69 as the live correction that prompted this source-contract update.
- Exclude changes to Proposal acceptance, formal backlog promotion, implementation scope, and external development-rule deliberation.

## Authorization Record

- On 2026-07-30, the repository owner stated that all AI-created Issues must receive the Codex creation label.
- The owner explicitly identified Proposal #69 as AI-created and requested the missing label.
- The label was added to #69 and read back before this durable policy correction.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `GHATTR-004` | Define and validate source-aware Proposal creation attribution. | `in_progress` |

## Provider Boundary

- Attribution is determined by the creation source, not by the Issue kind.
- AI-created Proposals receive `created-by:codex` in the creation request.
- Human-submitted Proposals do not receive the label from the public form.
- GitHub cannot independently infer that an Issue was created through an AI execution; the creating AI/runtime must apply the configured label.
- The label records initial content creation only and does not grant approval, ownership, assignment, or implementation authority.

## Resume Checkpoint

- Last completed action: corrected Proposal #69 online and validated the source-aware provider contract.
- Current task: integrate the validated contract through pull-request-only `main`.
- Exact next action: commit, push, and open the pull request.
- Validation already completed: #69 label read-back, 18 focused provider tests, migration dry-run, workflow contracts, AI-context validation, and Git diff checks.
- Git state: dedicated branch from merged `main@6886c92`.
- Blockers or unresolved decisions: none.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-30-ai-created-proposal-attribution` | `main@6886c92` | active remediation | pending | local | `2026-07-30T23:33:42+08:00` | Persist the owner-approved attribution rule. | Validate, commit, push, and open a PR. |
