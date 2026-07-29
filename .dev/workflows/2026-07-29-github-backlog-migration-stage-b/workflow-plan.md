# GitHub Backlog Migration Stage B

## Workflow Metadata

- `workflow_id`: `2026-07-29-github-backlog-migration-stage-b`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-29-github-backlog-migration-stage-b`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `issue-batch-2`
- `artifact_root`: `.dev/workflows/2026-07-29-github-backlog-migration-stage-b`
- `created_at`: `2026-07-29T22:58:40+08:00`
- `updated_at`: `2026-07-29T23:04:30+08:00`

## Objective And Scope

- Create the 37 formal GitHub Issues that remain after the four verified canaries.
- Apply the canonical lifecycle: keep unfinished items open; add the historical closing comment and close resolved or declined items with the exact reason.
- Read back every Issue after creation and record provider identities immediately.
- Create the public `AI Collaboration Framework — Backlog & Roadmap` Project, configure the approved minimal fields, add all 41 formal Issues, and project canonical values.
- Configure the approved `Active Backlog`, `Roadmap`, `Owner Review`, and `History by Release` views plus only the two low-risk automation outcomes when the provider supports them.
- Preserve `.dev/backlog/` and `.dev/workflows/` as canonical authorities; GitHub remains a visibility, feedback, and owner-review provider.

## Authorization Record

- The owner approved the Issue/Project provider design and the four-canary pilot in the preceding discussions.
- Issues #21-#24 were read back successfully after the attribution policy was integrated.
- On 2026-07-29 the owner explicitly authorized continuation with `OK 可繼續`.
- This authorization covers the remaining 37 formal Issues, the public Project, approved fields/views, the two-item automation allowlist, provider receipts, and PR-only repository closeout.
- It does not authorize Project state to trigger repository workflow execution or reverse-write canonical backlog truth.

## Immutable Apply Plan

- Source snapshot: `e83b759c8cf1deeb11af5ae748359f6a4c63b200`.
- Plan evidence: `.dev/workflows/2026-07-29-github-issue-creation-attribution/evidence/github-backlog-dry-run.yaml`.
- Plan SHA-256: `702a9155084d04de892b6eac79579cce18c44dcd0dc84d5df93efc9a92a7a8e8`.
- Total projection: 41 items, 5 open, 36 closed, 0 blocked, 11 Story, 30 Enabler.
- Existing verified canaries: `DEVWF-001`, `AIC-007`, `R042-005`, `UPG-001`.
- Remaining batches:
  1. `CAP-001`, `CFG-001`, `CI-001`, `CI-002`, `CTX-001`, `CTX-002`, `CTX-003`, `CUST-001`, `DEVWF-002`, `DIST-001`
  2. `ENF-001`, `EVAL-001`, `GOV-001`, `GOV-002`, `GOV-003`, `HANDOFF-001`, `INIT-001`, `LANG-001`, `OBS-001`, `PKG-001`
  3. `PKG-002`, `PKG-003`, `PKG-004`, `R042-001`, `R042-002`, `R042-003`, `R042-004`, `REL-001`, `REL-002`, `REL-003`
  4. `REL-004`, `SAG-001`, `SIMPL-001`, `SKILL-001`, `STD-001`, `TOOL-001`, `VAL-001`

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `GHBM-001` | Verify immutable plan, existing canaries, label contract, and absence of a Project. | `completed` |
| `GHBM-002` | Apply and read back remaining batch 1. | `completed` |
| `GHBM-003` | Apply and read back remaining batch 2. | `in_progress` |
| `GHBM-004` | Apply and read back remaining batch 3. | `pending` |
| `GHBM-005` | Apply and read back remaining batch 4. | `pending` |
| `GHBM-006` | Verify all 41 mappings, create the Project, fields, and item values. | `pending` |
| `GHBM-007` | Configure supported views and automation, perform complete provider read-back, and close the workflow. | `pending` |

## Stop And Recovery Rules

- Before creation, fail if any planned backlog ID already exists outside the recorded mapping.
- After each Issue, verify number, title, exact body, all hidden markers, exact labels, empty assignees, state, close reason, and closing comment.
- Stop the current batch on any mismatch; retain successful mappings and correct in place. Never delete migrated Issues as rollback.
- Record each successful Issue mapping in `.dev/backlog/provider-mappings/github-issues.yaml` immediately.
- Do not start Project creation until all 41 Issue mappings pass read-back.
- If a provider capability is unavailable, record it as `deferred/unavailable`; do not invent provider state and do not block repository workflows.

## Resume Checkpoint

- Last completed action: created and exactly read back batch 1 as Issues #27-#36; all ten are closed as completed with one immutable historical comment each.
- Current task: `GHBM-003`.
- Exact next action: create and read back remaining batch 2, recording each successful provider mapping immediately.
- Blockers: none; Project views and automation remain capability-checked rather than assumed.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-29-github-backlog-migration-stage-b` | `main@4b4a663` | active Stage B apply | pending | local | `2026-07-29T22:58:40+08:00` | Apply the owner-approved remaining migration with durable batch receipts. | Complete preflight, then apply batches sequentially. |
