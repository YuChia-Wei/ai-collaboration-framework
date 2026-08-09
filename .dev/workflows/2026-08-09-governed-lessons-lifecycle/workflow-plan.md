# Governed Lessons Knowledge Lifecycle

## Workflow Metadata

- `workflow_id`: `2026-08-09-governed-lessons-lifecycle`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-09-governed-lessons-lifecycle`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-08-09-governed-lessons-lifecycle`
- `created_at`: `2026-08-09T13:40:15+08:00`
- `updated_at`: `2026-08-09T13:55:47+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Authorization And Work-Item Binding

- Work item: [GitHub Issue #163](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/163)
- Authorization: Issue #163 records the repository owner's explicit authorization to define and implement the governed lesson knowledge lifecycle and its first WSL environment lesson.
- Subject baseline: `main` and `origin/main` were both read back at `29134dcc5eb18945ca901be5a049b36956197142` before branch creation.
- Pull-request gate: required; no direct mutation of `main`.

## Objective And Scope

- Problem statement: the repository once advertised a lessons area but never tracked a lesson directory or lesson document; define the previously missing contract without claiming that a complete prior system existed.
- Authorized scope: create the non-normative lesson knowledge class, identity and lifecycle contract, template, environment category, first evidence-backed WSL lesson, owned navigation, and the narrowest lesson-specific structure/reference validation.
- Exclusions: runtime/profile/environment classification, `missing-dotnet-sdk`, environment-readiness policy or schema, mandatory release-runbook preflight, release profiles, package bytes, tags, Releases, release allocation, v0.11 history, runtime installation, and Issues #149, #150, and #153.
- Completion criteria: the lesson contract and first lesson satisfy #163, deterministic repository validation passes, compliant workflow commits exist, and the delivery is submitted through and read back from the required pull-request gate.

## Delivery Cohesion And Proportionality

- One substantive task is retained because the canonical knowledge-class contract, first exemplar, navigation, and validator form one review and rollback unit.
- Workflow mode preserves unique owner authorization, future-agent-behavior change, and pull-request integration state. Validation, commit creation, provider read-back, and closeout remain lifecycle steps rather than padded tasks.
- Linear integration is selected provisionally because this is one coherent outcome with no independently resumable checkpoint or external release boundary. The final PR gate decides integration availability.

## Artifact Contract

- Baseline assessment: `not-applicable`; this is owner-authorized policy creation, not remediation of a persisted assessment finding.
- Remediation report: `not-applicable`; no assessment finding lifecycle is being claimed.
- Verification assessment: `not-applicable`; deterministic lesson, AI-context, workflow, commit, and hosted PR checks own verification for this delivery.
- Tasks: `.dev/workflows/2026-08-09-governed-lessons-lifecycle/tasks/`

## Stages And Checkpoints

1. Freeze Issue, Git, historical, and v0.11 evidence boundaries.
2. Implement the bounded lesson contract, first lesson, navigation, and validator.
3. Run deterministic validation and create compliant workflow commits.
4. Push the branch, open the #163 pull request, and read back checks, review, and integration state.
5. Reconcile workflow and Issue state only after accepted integration; an open branch or pull request is not terminal completion.

## Boundary Decisions

- `.dev/lessons/` is a source-repository knowledge class. The current distribution profile does not select it, and #163 makes no package-profile change.
- Lesson records are evidence-backed and reusable but have `Normative Authority: none`; they cannot override standards, policy, guides, runbooks, assessments, workflows, release evidence, or machine-local state.
- `environment` is the first category because the incident concerns shell startup, process environment, and host/runtime availability rather than .NET architecture.
- The observed `~/.bash_profile` is retained only as a sanitized remediation example. No personal profile bytes or current machine-readiness state are repository truth.
- `missing-dotnet-sdk`, environment-readiness policy/schema, runner behavior, release profiles, package bytes, tags, Releases, allocation, and v0.11 evidence remain unchanged.
- Future guide, runbook, policy, or validator promotion remains separately authorized work; no such follow-up is implied by this delivery.

## Validation Selection

- Lesson contract tests: selected; six pass/fail lifecycle and structure cases.
- AI-context, source-governance, workflow-artifact, and Git-diff validation: selected.
- Spec compliance: `not-applicable`; no problem frame, requirement, or owner decision selected it.
- Unit/integration product tests: `not-applicable`; this delivery changes documentation and a source-governance validator, not product code.
- WSL/.NET environment execution: `not-applicable`; #163 consumes pinned v0.11 evidence and does not authorize runtime installation or new release-profile execution.

## Resume Checkpoint

- Last completed action: implemented the lesson contract, environment exemplar, navigation, and source-only validator; focused and repository validators passed.
- Current task: `AICG-163-001`
- Exact next action: review the complete diff, create the implementation commit, then push and open the #163 pull request.
- Validation already completed: lesson tests 6/6 outside the Codex temp-directory sandbox boundary; AI-context validation with one governed lesson; source-governance validation; workflow-artifact validation; `git diff --check`.
- Git state: bootstrap commit `26ed9c1abddf734002e9082db6e72b5f2695c517`; implementation changes are uncommitted on the dedicated branch.
- Branch history and checkpoint handoffs: segment 1 started from `main`; no handoff checkpoint.
- Blockers or unresolved decisions: hosted pull-request checks and integration state have not yet been observed.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-09-governed-lessons-lifecycle` | `main@29134dcc5eb18945ca901be5a049b36956197142` | `none` | `pending` | `local` | `2026-08-09T13:40:15+08:00` | Initial authorized delivery segment. | Continue `AICG-163-001` on this branch. |
