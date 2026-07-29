# GitHub Issue Creation Attribution

## Workflow Metadata

- `workflow_id`: `2026-07-29-github-issue-creation-attribution`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-29-github-issue-creation-attribution-continuation`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-07-29-github-issue-creation-attribution`
- `created_at`: `2026-07-29T22:21:37+08:00`
- `updated_at`: `2026-07-29T22:40:09+08:00`

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
| `GHATTR-002` | Merge the contract through PR-only `main`. | `completed` |
| `GHATTR-003` | Update four canary Issue bodies and persist read-back evidence. | `completed` |

## Provider Boundary

- The label records that Codex initially created or projected the formal Issue content; it does not change backlog authorship, ownership, approval, priority, or workflow authorization.
- `.dev/backlog/items/*.yaml` remains canonical outcome truth, and `.dev/workflows/` remains execution and verification truth.
- GitHub account metadata remains provider-native metadata; the label supplies visible attribution while the hidden marker preserves detailed execution provenance.
- The configured runtime, model, and reasoning effort bind to the active creation execution and must be refreshed before a later batch if that provenance changes.
- Proposal Issues remain attributable to the submitting GitHub user and receive no automatic Codex trailer.

## Resume Checkpoint

- Last completed action: updated and exactly read back Issues #21-#24 with the new label and hidden marker while preserving state, close reason, assignees, and original closing comments.
- Current task: none; `GHATTR-001` through `GHATTR-003` are completed.
- Exact next action: commit and integrate this continuation receipt through PR-only `main`, then wait for owner approval before creating the remaining 37 Issues or Project.
- Blockers: none for attribution; the remaining migration is deliberately owner-gated.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-29-github-issue-creation-attribution` | `main@27bc777` | checkpoint merge | `2968aad35b611006fcadc222ac4b2d31f499e46f` | PR #25 / `main@e83b759` | `2026-07-29T22:34:49+08:00` | Integrate the provider contract before mutating live canaries. | Resume on a continuation branch from merged main. |
| 2 | `codex/2026-07-29-github-issue-creation-attribution-continuation` | `main@e83b759` | validated closure checkpoint | pending | local | `2026-07-29T22:40:09+08:00` | Update only the four existing canaries and persist exact evidence. | Commit, push, open the continuation receipt PR, and merge. |
