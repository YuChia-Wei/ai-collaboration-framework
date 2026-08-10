# v0.12 Source Disposition And Terminal Release Readiness

## Workflow Metadata

- `workflow_id`: `2026-08-11-v0-12-release-readiness`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-v0-12-release-readiness`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `validation`
- `artifact_root`: `.dev/workflows/2026-08-11-v0-12-release-readiness`
- `created_at`: `2026-08-11T00:43:10+08:00`
- `updated_at`: `2026-08-11T01:27:57+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: v0.12 has no terminal candidate, the release lifecycle still requires a post-tag source closeout, and the current 32 `.dev/**` source omissions (30 at the #184 assessment baseline plus two later governed lesson files) lack an exhaustive machine-readable disposition.
- Authorized remediation scope: implement Issues #184 and #167, correct their release contracts and validation, prepare the exact v0.12 candidate, reconcile online work-management state, and integrate a pre-tag terminal state whose only remaining owner action is creating and pushing an annotated tag.
- Exclusions: creating or moving a tag, publishing v0.12, mutating v0.11 tag/assets/history, implementing v0.13 #61 rounds, storing credentials in the repository, or changing unrelated package identity decisions.
- Completion criteria: source-disposition coverage fails closed; candidate/tag publication paths use v0.12 online Issue authority; tag-triggered CI publishes and performs provider-only reconciliation without a source PR; the exact candidate passes local, hosted, and frozen independent validation; merged `main` passes the pre-tag gate.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260810-003/assessment.yaml`
- Authorization and release decisions: GitHub Issues #167, #169, and #184.
- Remediation report: `.dev/workflows/2026-08-11-v0-12-release-readiness/reports/remediation-report.md`
- Independent verification: final frozen read-only Codex task using `gpt-5.6-luna` at `high`; the parent performs no mutations while it runs.
- Tasks: `.dev/workflows/2026-08-11-v0-12-release-readiness/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260810-003#PKG-001` | HIGH | `ai-context-governance` | remediate in v0.12 | `PKG010-001` | focused contract tests, package inventory, governance and critical gates |
| GitHub Issue #167 | HIGH | `ai-context-governance` | remediate before v0.12 tag | `REL006-001` | release-state, workflow-contract, renderer, candidate and failure fixtures |
| GitHub Issue #169 | HIGH | release coordination | keep open until hosted publication reconciliation | `REL012-001` | exact candidate CI, merged-main pre-tag gate, provider preflight |

## Stages And Checkpoints

1. Freeze live Issue/Project/repository baseline and release acceptance contract.
2. Implement and validate #184 source-disposition coverage.
3. Implement and validate #167 terminal pre-tag and provider-only post-tag automation.
4. Close integrated implementation Issues and create the exact v0.12 candidate artifacts.
5. Run hosted candidate gates and freeze all source/provider state.
6. Start the final external Luna validation only after freeze; do not mutate concurrently.
7. Integrate to `main`, rerun the exact pre-tag gate, and hand the user only the annotated-tag creation/push action.

## Resume Checkpoint

- Last completed action: PR #188 candidate and Ubuntu prerequisite checks passed on `abeef30`; three checks exposed one shared stale 29-entry dependency-validator count. The validator now expects 31 total / 29 PyYAML entries, and its 19 tests, the four Windows launcher tests, four entrypoint-contract tests, and direct validation pass locally.
- Current task: integrate `PKG010-001` and `REL006-001` through a reviewed implementation pull request.
- Exact next action: commit and push the focused CI correction, then wait for the superseding PR #188 checks before Issue closeout or release-candidate authoring.
- Validation already completed: source disposition derives `1052 = 117 packaged + 903 explicit exclusions + 32 dispositions` with zero implicit omissions; release-state 33/33, provider 7/7, workflow 8/8, governance-workflow 7/7, and file-disposition 31/31 tests passed; source governance, AI context, and `git diff --check` passed.
- Git state: branch `codex/2026-08-11-v0-12-release-readiness` from the exact baseline.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: repository Actions secret `RELEASE_PROVIDER_TOKEN` must exist before the tag can publish; pull-request workflows intentionally never receive it. Exact live Project preflight will run before tag handoff and again inside the protected tag publication job.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-v0-12-release-readiness` | `main@bd1bd2530bfe76b56bd38023c4e3f9c167291120` | implementation validation | pending | pending | `2026-08-11T01:19:03+08:00` | #184 and #167 implementation is locally focused-green; hosted review remains | commit, push, and open implementation PR |
