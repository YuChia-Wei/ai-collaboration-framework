# Work Management Lifecycle And Git Governance Policy

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-25-work-management-policy`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-25-work-management-policy`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-07-25-work-management-policy`
- `created_at`: `2026-07-25T08:02:06+08:00`
- `updated_at`: `2026-07-26T00:55:38+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the current workflow gate correctly protects durable,
  executable repository work, but its broad planning and multi-stage triggers
  make exploratory discussion, candidate backlog intake, and active execution
  too easy to conflate. The repository also permits optional backlog providers
  without a defined promotion boundary from an online item to a repository
  workflow.
- Authorized remediation scope: define an explicit lifecycle for transient
  discussion, candidate work in an optional external tracker, owner-approved
  planning, and authorized execution; then update the affected governance
  policies and navigation only after the owner approves the decision register.
- Exclusions: do not create or migrate GitHub Issues or Projects; do not install
  Multica or another tracker; do not alter product source or tests; do not alter
  release records, tags, or publication state; do not claim an external tracker
  is mandatory for all target repositories.
- Completion criteria: policies distinguish conversation, provider-owned
  candidate work, durable proposal, and execution workflow; a workflow is not
  created solely because a discussion contains planning words; external issue
  linkage remains optional and never fabricates identifiers; branch, draft PR,
  merge, and completion semantics are explicit; governed validation passes; an
  independent post-remediation assessment reconciles every baseline finding.

## Decision Authority

Opening this workflow was authorized by the repository owner on 2026-07-25.
The owner approved the following source-of-truth and transport decisions on
2026-07-26; they authorize `WMP-003` to make the bounded policy edits.

| Decision | Owner-approved policy decision | Evidence |
| --- | --- | --- |
| `WMP-DEC-001` | A workflow begins only when execution is authorized or durable cross-session execution tracking is required. Discussion and unapproved planning do not create a workflow locator. | Owner response: `1 同意`. |
| `WMP-DEC-002` | For this repository, GitHub Issues and GitHub Projects are the candidate-work provider. The framework remains provider-neutral for target repositories. | Owner response: `2 選 GitHub`. |
| `WMP-DEC-003` | This repository does not add a repository proposal artifact class. A retained but unapproved plan belongs in a GitHub Issue; without an available provider, it remains conversational until the owner explicitly authorizes another persistence route. An execution workflow must not be overloaded for this purpose. | Owner response: `3 同意`. |
| `WMP-DEC-004` | Repository workflow and policy edits stay branch-first. Draft PRs are optional before review or handoff, but every change entering `main` must use a pull request. Workflow completion and PR integration remain separate facts. | Owner response: `4 要求 PR 合併 main`. |

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260725-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-07-25-work-management-policy/reports/remediation-report.md`
- Verification assessment: not allocated until policy edits are approved
- Tasks: `.dev/workflows/2026-07-25-work-management-policy/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260725-001#AIC-001` | MEDIUM | governance | revise only after `WMP-DEC-001` | `WMP-003` | policy path and semantic review |
| `ASM-20260725-001#AIC-002` | MEDIUM | governance / owner | select provider and proposal boundary | `WMP-002` | cross-policy consistency |
| `ASM-20260725-001#AIC-003` | LOW | governance | clarify branch, draft PR, and merge semantics | `WMP-003` | policy wording and reference checks |

## Stages And Checkpoints

1. Freeze the independent baseline and current policy evidence.
2. Obtain owner decisions for candidate, proposal, workflow, and PR boundaries.
3. Apply the smallest approved policy and navigation changes.
4. Run structural and semantic validation, then request independent verification.
5. Reconcile findings, publish the remediation report, commit, and close.

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `WMP-001` | Record the baseline assessment and map current policy boundaries. | `completed` |
| `WMP-002` | Obtain owner approval for the proposed lifecycle and transport decisions. | `completed` |
| `WMP-003` | Apply the approved policy and navigation changes. | `completed` |
| `WMP-004` | Validate, obtain independent verification, commit, and close. | `in_progress` |

## Resume Checkpoint

- Last completed action: applied and locally validated the approved lifecycle,
  GitHub candidate-provider, and pull-request integration policies.
- Current task: `WMP-004`.
- Exact next action: obtain an independent post-remediation assessment,
  reconcile the baseline findings, validate the full workflow range, and create
  the final local checkpoint.
- Validation already completed: repository state was clean before branch
  creation; baseline evidence was read from the active governance policies,
  backlog provider direction, and workflow task contract.
- Git state: branch `codex/2026-07-25-work-management-policy` starts from
  `main@672344b5d1d3ca8edce77244e29568c53403ccab` and contains the validated
  bootstrap commit `6e62a4fe71cf4a034584e73865ef412ccd9fe8a3`.
- Branch history and checkpoint handoffs: the bootstrap and owner-decision
  checkpoints are local; neither has been pushed or merged.
- Blockers or unresolved decisions: none. The approved decisions bound the
  remediation; no external tracker item creation or GitHub transport is
  authorized by this policy work alone.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-25-work-management-policy` | `main@672344b5d1d3ca8edce77244e29568c53403ccab` | local bootstrap checkpoint | `6e62a4fe71cf4a034584e73865ef412ccd9fe8a3` | local | `2026-07-25T08:07:48+08:00` | Establish a decision-ready policy workflow without changing canonical policy. | Apply approved lifecycle and PR policy changes. |
| 1 | `codex/2026-07-25-work-management-policy` | `main@672344b5d1d3ca8edce77244e29568c53403ccab` | local owner-decision checkpoint | `f59288f` | local | `2026-07-26T00:51:56+08:00` | Preserve the owner's four approved lifecycle and transport decisions before policy remediation. | Complete independent verification and close the workflow. |
