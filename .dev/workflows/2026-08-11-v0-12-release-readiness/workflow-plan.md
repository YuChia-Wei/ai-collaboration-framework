# v0.12 Source Disposition And Terminal Release Readiness

## Workflow Metadata

- `workflow_id`: `2026-08-11-v0-12-release-readiness`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-v0-12-release-candidate`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-11-v0-12-release-readiness`
- `created_at`: `2026-08-11T00:43:10+08:00`
- `updated_at`: `2026-08-11T01:48:35+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: v0.12 has no terminal candidate, the release lifecycle still requires a post-tag source closeout, and the current 32 `.dev/**` source omissions (30 at the #184 assessment baseline plus two later governed lesson files) lack an exhaustive machine-readable disposition.
- Authorized remediation scope: implement Issues #184 and #167, correct their release contracts and validation, prepare the exact v0.12 candidate, reconcile online work-management state, and integrate a pre-tag terminal state whose only remaining owner action is creating and pushing an annotated tag.
- Exclusions: creating or moving a tag, publishing v0.12, mutating v0.11 tag/assets/history, implementing v0.13 #61 rounds, storing credentials in the repository, or changing unrelated package identity decisions.
- Source workflow completion criteria: source-disposition coverage fails closed; candidate/tag publication paths use v0.12 online Issue authority; tag-triggered CI publishes and performs provider-only reconciliation without a source PR; the exact source candidate passes local and hosted review.
- External handoff criteria: the accepted candidate is integrated without changing its tree, merged `main` passes the pre-tag gate, and the final frozen Luna task passes. These are read-only provider/handoff gates and are intentionally not written back into the source snapshot they verify.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260810-003/assessment.yaml`
- Authorization and release decisions: GitHub Issues #167, #169, and #184.
- Remediation report: `.dev/workflows/2026-08-11-v0-12-release-readiness/reports/remediation-report.md`
- Independent verification: final frozen read-only Codex task using `gpt-5.6-luna` at `high`; the parent performs no mutations while it runs, and its result is retained as external handoff evidence rather than a post-verification source commit.
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
5. Run hosted candidate gates, integrate the accepted candidate to `main`, and complete online pre-tag reconciliation.
6. Run the exact merged-main pre-tag gates, then freeze all source and provider state.
7. Start the final external Luna validation only after that freeze, perform no concurrent mutation, and hand the user only the annotated-tag creation/push action after its read-back passes.

## Resume Checkpoint

- Last completed action: candidate PR #189 at `cef52c2aac01213c2eda7f1881cfaad9784413f5` passed all five hosted checks after exact local candidate-state, provider preflight, source-disposition, and deterministic archive validation had passed.
- Current task: source-side workflow is complete; the terminal record commit must pass its superseding hosted checks before the exact candidate tree is merged and frozen.
- Exact next action: commit and push the terminal source record, wait for the superseding PR #189 checks, merge the accepted tree, run merged-main pre-tag read-only gates, and only then start the external Luna task.
- Validation already completed: release registry 15/15, workflow registry 72/72, release-state 33/33, version-governance 21/21, provider 7/7, release-notes 9/9, AI-context structural validation, exact candidate state, live provider preflight, source dispositions, prior-asset verification, deterministic archive build/parity, and `git diff --check` passed.
- Git state: branch `codex/2026-08-11-v0-12-release-candidate` from exact `origin/main@d1823a0c0cbf75ea13a33820443f5416c1dee86e`.
- Branch history and checkpoint handoffs: implementation segment merged through PR #188; candidate continuation resumed from the fetched merge commit.
- Blockers or unresolved decisions: repository Actions secret `RELEASE_PROVIDER_TOKEN` does not yet exist and must be provisioned before the tag can publish; pull-request workflows intentionally never receive it. Exact live Project preflight will run before tag handoff and again inside the protected tag publication job.

## Terminal Snapshot Rule

This workflow closes its source-owned work in the candidate PR. The final PR merge, merged-main pre-tag read-back, and frozen Luna verification observe that exact accepted tree externally. A passing result must not trigger a source evidence commit, because that would create a different unverified release snapshot and recreate the post-tag closeout pattern removed by #167.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-v0-12-release-readiness` | `main@bd1bd2530bfe76b56bd38023c4e3f9c167291120` | merge-commit integration | `cead16fd415bde663233f899ba0c16b28e2d270c` | PR #188 → `main@d1823a0c0cbf75ea13a33820443f5416c1dee86e` | `2026-08-11T01:38:38+08:00` | #184 and #167 implementation passed all hosted checks and closed as completed | resume the same delivery on a new branch from updated main |
| 2 | `codex/2026-08-11-v0-12-release-candidate` | `main@d1823a0c0cbf75ea13a33820443f5416c1dee86e` | hosted candidate validation | `cef52c2aac01213c2eda7f1881cfaad9784413f5` | PR #189, five checks passed | `2026-08-11T01:48:35+08:00` | exact source candidate passed local and hosted gates; terminal record is the final source-only delta | rerun hosted checks, merge, and perform external frozen handoff gates without source writes |
