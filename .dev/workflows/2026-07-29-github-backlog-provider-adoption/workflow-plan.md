# GitHub Backlog Provider Adoption

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-29-github-backlog-provider-adoption`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-29-github-backlog-provider-adoption`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `closure`
- `artifact_root`: `.dev/workflows/2026-07-29-github-backlog-provider-adoption`
- `created_at`: `2026-07-29T21:27:05+08:00`
- `updated_at`: `2026-07-29T21:48:26+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the source repository has 41 durable backlog items and an owner-approved GitHub Issues and Projects collaboration design, but no source-only provider contract, deterministic projection, mapping receipt, or safe migration preview exists.
- Authorized remediation scope: implement the Stage A repository contract, including provider-neutral boundaries, a source-only GitHub projection configuration, Proposal intake form, mapping receipt schema, deterministic 41-item dry-run generator, validation, and a PR-ready handoff.
- Exclusions: do not create or mutate online GitHub Issues, labels, Projects, views, fields, workflows, or automation; do not merge the Stage A PR; do not change any of the 41 portable backlog items; do not treat Project state as workflow authorization.
- Completion criteria: the adapter produces exactly one deterministic preview for each of the 41 formal backlog items, all configured classifications and lifecycle projections validate fail closed, source-only files are excluded from package payloads, repository gates pass, and Stage B remains blocked on merge plus a fresh-main owner-approved dry-run.

## Authorization Record

- The owner approved the full Issue and Project design interactively and authorized Stage A on 2026-07-29.
- Stage A authorizes repository changes, a dedicated branch, commits, push, and a pull request only.
- Stage B online provider mutation requires the Stage A PR to merge and a new explicit owner approval of a dry-run generated from fresh `main`.

## Artifact Contract

- Baseline assessment: not applicable; the approved design and current 41-item backlog are the bounded baseline.
- Provider contract: `.dev/backlog/providers/github.yaml`
- Mapping receipt: `.dev/backlog/provider-mappings/github-issues.yaml`
- Dry-run evidence: `.dev/workflows/2026-07-29-github-backlog-provider-adoption/evidence/`
- Remediation report: `.dev/workflows/2026-07-29-github-backlog-provider-adoption/reports/remediation-report.md`
- Verification assessment: not applicable; deterministic adapter tests and repository validators cover Stage A without making provider claims.
- Tasks: `.dev/workflows/2026-07-29-github-backlog-provider-adoption/tasks/`

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `GHBP-001` | Define source-of-truth boundaries, provider configuration, Proposal intake, and receipt schema. | `completed` |
| `GHBP-002` | Implement the read-only GitHub backlog projection adapter and focused tests. | `completed` |
| `GHBP-003` | Generate and review the complete 41-item dry-run and canary/batch plan. | `completed` |
| `GHBP-004` | Run aggregate validation, close Stage A locally, and prepare PR handoff. | `in_progress` |

## Provider Boundary

- `.dev/backlog/items/*.yaml` remains portable durable backlog truth.
- `.dev/backlog/ROADMAP.md` remains the canonical release horizon and gate record.
- `.dev/workflows/` remains the only owner of authorized execution tasks and validation evidence.
- GitHub Issues are concise outcome and feedback projections; GitHub Project is a visibility projection.
- Provider identifiers and read-back receipts are source-repository-only and never become a workflow dependency.

## Stage B Handoff

1. Merge this Stage A PR through the PR-only `main` policy.
2. Generate a fresh 41-item dry-run from the resulting immutable `main` commit.
3. Obtain explicit owner approval for that exact preview.
4. Create labels, four canary Issues, and read them back before owner confirmation.
5. Create the remaining Issues in `10 + 10 + 10 + 7` batches, recording each successful mapping immediately.
6. Create and configure the Public Project, add all 41 Issues, and perform full read-back.
7. Commit provider receipts on a continuation branch and open a separate PR.

## Resume Checkpoint

- Last completed action: generated and reviewed the deterministic 41-item preview; all focused, workflow, AI-context, source-governance, repository-config, and package regression gates pass after using repository-local Temp for Windows fixtures.
- Current task: `GHBP-004`.
- Exact next action: create the validated implementation checkpoint, finalize workflow closure evidence, push the branch, and open the Stage A PR.
- Validation already completed: provider contract 15/15; package regression 27 tests with one expected skip; repository configuration 13/13; workflow and governance suites; dry-run regeneration check; source governance; AI-context aggregate; Python compile; `git diff --check`.
- Git state: `codex/2026-07-29-github-backlog-provider-adoption` from `main@08b9fd9`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: none for Stage A; Stage B remains deliberately blocked on merge, fresh-main dry-run, and explicit owner approval.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-29-github-backlog-provider-adoption` | `main@08b9fd9` | active Stage A | — | local | `2026-07-29T21:27:05+08:00` | Implement the approved repository contract without online provider mutation. | Complete GHBP-001 through GHBP-004, then push and open the Stage A PR. |
