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
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-07-25-work-management-policy`
- `created_at`: `2026-07-25T08:02:06+08:00`
- `updated_at`: `2026-07-25T08:02:06+08:00`
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
That authorization permits evidence capture and a decision-ready policy proposal;
it does not approve the source-of-truth choices below.

| Decision | Owner decision required before policy edits | Proposed default |
| --- | --- | --- |
| `WMP-DEC-001` | When does a workflow begin? | Only when execution is authorized or durable cross-session execution tracking is required; discussion and unapproved planning do not create a workflow locator. |
| `WMP-DEC-002` | Where do candidate work and unapproved plan details live? | An optional tracker such as GitHub Issues is the preferred durable candidate surface; without a selected provider, discussion remains conversational until the owner approves repository persistence. |
| `WMP-DEC-003` | What is the repository-only alternative for a plan that must be retained but is not executable? | Decide whether to add a separate proposal artifact class or require an explicitly approved planning branch; do not overload an `in_progress` execution workflow. |
| `WMP-DEC-004` | What Git transport is required at each lifecycle boundary? | Branches are required for repository workflow or policy edits; a draft PR is optional review transport before an intended merge; `main` changes require the repository merge policy; a push-only checkpoint does not imply completion. |

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
| `WMP-002` | Obtain owner approval for the proposed lifecycle and transport decisions. | `in_progress` |
| `WMP-003` | Apply the approved policy and navigation changes. | `pending` |
| `WMP-004` | Validate, obtain independent verification, commit, and close. | `pending` |

## Resume Checkpoint

- Last completed action: created the dedicated workflow branch and recorded
  `ASM-20260725-001` as the baseline assessment.
- Current task: `WMP-002`.
- Exact next action: receive the owner's decisions for `WMP-DEC-001` through
  `WMP-DEC-004`; do not edit canonical policy before that approval.
- Validation already completed: repository state was clean before branch
  creation; baseline evidence was read from the active governance policies,
  backlog provider direction, and workflow task contract.
- Git state: branch `codex/2026-07-25-work-management-policy` starts from
  `main@672344b5d1d3ca8edce77244e29568c53403ccab`.
- Branch history and checkpoint handoffs: none; bootstrap is not yet committed.
- Blockers or unresolved decisions: all four `WMP-DEC-*` entries above require
  explicit owner approval before remediation.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-25-work-management-policy` | `main@672344b5d1d3ca8edce77244e29568c53403ccab` | active bootstrap | none | local | `2026-07-25T08:02:06+08:00` | Establish a decision-ready policy workflow without changing canonical policy. | Obtain `WMP-DEC-001` through `WMP-DEC-004`. |
