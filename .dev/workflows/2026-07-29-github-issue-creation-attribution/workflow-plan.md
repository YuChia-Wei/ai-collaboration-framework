# GitHub Issue Creation Attribution

## Workflow Metadata

- `workflow_id`: `2026-07-29-github-issue-creation-attribution`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-29-github-issue-creation-attribution`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `provider-contract-pr-integration`
- `artifact_root`: `.dev/workflows/2026-07-29-github-issue-creation-attribution`
- `created_at`: `2026-07-29T22:21:37+08:00`
- `updated_at`: `2026-07-29T22:30:00+08:00`

## Objective And Scope

- Add `created-by:codex` to every formal GitHub Story or Enabler Issue projected by this source repository.
- Preserve detailed execution provenance in the hidden marker `<!-- created-by: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com> -->` immediately before the canonical identity markers.
- Do not add a visible creation-attribution section to Issue bodies.
- Keep public Proposal intake user-authored and do not inject the trailer into the Proposal form.
- After the provider contract is merged through PR-only `main`, update and read back only the four existing canary Issues.
- Keep the remaining 37 backlog Issues and the GitHub Project paused until the owner reviews the updated canaries.

## Authorization Record

- The owner requested Codex creation attribution comparable to Git commit attribution on 2026-07-29.
- After reviewing the visible trailer approach, the owner approved a `created-by:codex` label plus a hidden detailed marker instead.
- Authorization includes the provider contract change, its PR-only integration, and in-place update of the four already-created canary Issues.
- This does not authorize creation of the remaining 37 Issues or the GitHub Project.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `GHATTR-001` | Add and validate the formal Issue creation-attribution contract. | `completed` |
| `GHATTR-002` | Merge the contract through PR-only `main`. | `in_progress` |
| `GHATTR-003` | Update four canary Issue bodies and persist read-back evidence. | `pending` |

## Provider Boundary

- The label records that Codex initially created or projected the formal Issue content; it does not change backlog authorship, ownership, approval, priority, or workflow authorization.
- `.dev/backlog/items/*.yaml` remains canonical outcome truth, and `.dev/workflows/` remains execution and verification truth.
- GitHub account metadata remains provider-native metadata; the label supplies visible attribution while the hidden marker preserves detailed execution provenance.
- The configured runtime, model, and reasoning effort bind to the active creation execution and must be refreshed before a later batch if that provenance changes.
- Proposal Issues remain attributable to the submitting GitHub user and receive no automatic Codex trailer.

## Resume Checkpoint

- Last completed action: received owner approval to replace the visible trailer with a label and hidden detailed marker before push.
- Current task: `GHATTR-002`.
- Exact next action: commit, push, open the contract PR, and merge it through PR-only `main`.
- Blockers: none for the contract; online canary updates wait for the contract PR to merge.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-29-github-issue-creation-attribution` | `main@27bc777` | validated implementation | pending | local | `2026-07-29T22:30:00+08:00` | Add the owner-approved label and hidden marker contract before mutating live canaries. | Amend the unpushed checkpoint, push, open PR, and merge. |
