# Workflow Gate Policy

This policy defines when an agent should create workflow artifacts proactively instead of using direct mode.

## Default Modes

| Mode | Use |
| --- | --- |
| Direct mode | Conversation, exploration, or small single-pass work that does not need a durable repository execution record. |
| Assessment mode | Read-only analysis that needs a durable report but does not authorize remediation or execution tracking. |
| Workflow mode | Authorized execution that changes source-of-truth, crosses skill boundaries, or needs durable execution-task tracking. |

Mode is determined by intent, mutation, and execution tracking, not by the number of analysis steps alone. A transient read-only analysis may use multiple passes or sub-agents in direct mode when it does not write a repository report, mutate repository files, or perform remediation. A user request for a "report" means a durable repository artifact only when the user asks to save, persist, land, or otherwise retain it in the repository. Persistence by itself selects assessment mode, not workflow mode.

## Work-Management Lifecycle

Keep work-management state distinct from repository execution state. A planning
word, a detailed breakdown, or a multi-step conversation does not by itself
authorize repository work or create a workflow.

| State | Durable home | Repository execution consequence |
| --- | --- | --- |
| Conversation and exploration | The conversation only. | No branch, workflow locator, commit, or pull request. |
| Candidate work and unapproved plan | For this source repository, a GitHub Issue; GitHub Projects provide the priority and status views. | The tracker item records possible work but does not authorize execution merely by existing or changing provider state. No repository branch or pull request is created merely to record it. |
| Authorized execution | Explicit owner authorization, optionally bound to an approved work item according to the selected work-item binding mode, plus a skill-owned workflow when the workflow gate applies. | Create the dedicated branch before the locator or material repository edits. Record the work-item binding or the explicit no-binding authorization; never fabricate a tracker identifier. |
| Integrated repository fact | `main`, after the required pull request is merged. | Do not describe branch-only or tracker-only work as integrated repository truth. |

GitHub Issues and Projects are this repository's selected candidate-work
provider, not a framework-wide requirement for target repositories. The
framework stays provider-neutral. This repository does not define a separate
repository proposal artifact class: a retained but unapproved plan belongs in
a GitHub Issue. If no selected provider is available, retain it in the
conversation until the owner explicitly authorizes another persistence route;
do not overload an `in_progress` execution workflow.

## Work-Item Binding Contract

A valid work-item binding serves two purposes together:

1. trace the execution and pull request to the approved work outcome; and
2. preserve evidence that the owner authorized that outcome for execution.

An Issue, Project field, provider event, or provider state never authorizes
execution by itself. The binding becomes authorization evidence only when the
owner's explicit approval is recorded in the work item, workflow, pull request,
or conversation. The workflow remains execution truth and `main` remains
integrated repository truth.

Targets select a provider-neutral binding mode:

- `required`: an approved work item must be bound before execution;
- `optional`: a binding is preferred but explicit owner authorization may be
  recorded without one; or
- `disabled`: no work-item binding is used and authorization is recorded
  outside a tracker.

Targets separately select whether pull-request integration enforces the
binding as `required`, treats it as `optional`, or leaves the merge gate
`disabled`. This source repository selects `optional` for both work-item
binding and the merge gate in `.dev/backlog/providers/github.yaml`. A missing
Issue therefore does not block an owner-approved change here, but the workflow
or pull request must preserve the explicit authorization source.

For software-development work, activation is intent-based. A high-level request
that spans planning, requirements, design, implementation, testing, review, or
closeout may activate the repository's development orchestration without the
user naming `software-development-orchestrator` or any downstream skill. Determine stages from the
requested outcome, current artifacts, repository policy, and approval state,
not from skill names alone.

## Must Create a Workflow

Create a durable workflow and its discovery locator only when execution is
authorized, or the owner requires durable cross-session execution tracking, and
one or more of these are true:

- the authorized task needs two or more execution stages;
- the task needs cross-skill or sub-agent handoff;
- the task changes canonical source-of-truth rules;
- the task reorganizes `.ai/`, `.dev/`, `.agents/`, `.claude/`, or wrapper routing;
- the task affects future agent behavior;
- the task needs execution plan, review, or task status artifacts;
- the task involves document governance, source-of-truth cleanup, or context boundary changes;
- the task will likely touch five or more files;
- the owner explicitly requests a workflow for the authorized execution.

Candidate tracker management, discussion, plan drafting, and task breakdown are
not workflow triggers unless they also meet the authorization condition above.

## Direct Mode Is Enough

Direct mode is acceptable when all of these are true:

- the change is small and local;
- only one skill is needed;
- no durable decision trail is required;
- no canonical rule or source-of-truth boundary changes;
- no task status needs to be preserved;
- validation can be completed in the same turn.

Transient read-only analysis is also direct mode even when it is multi-stage or uses sub-agents, provided that all of these are true:

- the result is returned only in the conversation;
- no durable report or workflow artifact is written to the repository;
- no repository file is mutated;
- no finding is remediated.

Creating or refining a selected external tracker item does not by itself change
the repository mode. It must remain within the owner's authorization for that
provider. Only a binding with explicit owner approval may serve as execution
authorization evidence; an unapproved plan never does.

## Assessment Mode

Use assessment mode when all of these are true:

- the requested result is a durable audit, large code review, architecture assessment, or similar observation;
- the assessed surfaces remain read-only;
- remediation or implementation is not authorized;
- task-level execution tracking is not required beyond the assessment locator's draft resume checkpoint.

Follow `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`. Create a dedicated
assessment branch before writing `.dev/assessments/<assessment-id>/`, but do not
create a workflow locator solely because the report is durable. Commits contain
only assessment-owned artifacts and required assessment index updates.

If remediation is authorized later, create a new workflow and reference the
assessment and selected finding IDs. If assessment and remediation are requested
together, use workflow mode for execution while keeping the assessment report
under `.dev/assessments/`.

## Workflow Artifacts

When workflow mode is used:

1. Start from the intended base branch, normally `main`.
2. Create or switch to a dedicated workflow branch before creating workflow artifacts or making material task changes.
3. Then create the workflow locator and skill-owned artifacts.

Branch naming, checkpoint merge, continuation branch, push, and `--no-ff` details are defined by `.dev/TEAM-GIT-FLOW-RULES.MD`.

```text
.dev/workflows/<workflow-id>/
  workflow.yaml
```

- Follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` for discovery, full-date IDs, timestamps, artifact roots, and minimum task metadata.
- Use the workflow-owning skill's templates for its plan, tasks, reports, and domain-specific layout.
- Default the artifact root to `.dev/workflows/<workflow-id>/`; a skill may declare another repository-relative root while retaining the locator above.
- Do not assume every workflow has `review-report.md` or the same task/report structure.
- Do not create a workflow directly on `main`. Historical workflows created before this rule are not retroactively rewritten, but must use a dedicated continuation branch before resuming material work.

## Task Status Rule

Each task JSON should move through:

```text
pending -> in_progress -> completed
```

Use `deferred` only when the task is intentionally postponed and the workflow plan or task results explain why.

## Commit Rule

Workflow stages should follow `.dev/standards/GIT-COMMIT-POLICY.md`. Commit one
validated durable stage or coherent bounded task batch, not each skill
invocation. Small tasks completed and validated together may share a commit.
History compression is limited to unshared, unpushed commits under the active
repository policy and must preserve approval, review, evidence, checkpoint,
handoff, and shared-history boundaries.

Merging or pushing an incomplete workflow is a checkpoint handoff, not workflow completion. Keep the workflow and unfinished tasks active. Resume a push-only handoff from the pushed branch; after a checkpoint merge, create the next continuation branch from the updated target as defined by `.dev/TEAM-GIT-FLOW-RULES.MD`.

When continuation also crosses a model, runtime, host, machine, or fresh
session, follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` and create its
machine-readable receiving checkpoint before transfer.

## Software-Development Approval And Validation Gate

For a software-development workflow:

- pause before creating or executing implementation work while a requirement,
  design, or specification discussion is awaiting approval;
- record the authorization source before the implementation transition;
- resolve optional `test-execution` through target-profile commands, a
  separately evaluated external skill, or the fallback contract, in that order;
- use target-owned test commands, working directory, prerequisites, environment
  boundary, credential requirements, and policy without storing secret values,
  inventing credentials, bypassing controls, or escalating privileges
  implicitly;
- select unit and integration tests by default; select E2E, browser, Playwright,
  and environment-dependent tests only when target policy, requirements, an
  approved plan, or an owner decision requires them;
- record each selected test level as `passed`, `failed`,
  `blocked-by-environment`, `not-applicable`, or `deferred-with-owner`;
  `blocked-by-environment` is blocked and never passed;
- treat spec compliance as unselected and `not-applicable` by default. When a
  target profile, problem-frame workflow, requirement, or owner decision
  selects it, incomplete configuration or coverage below 100% fails closed.

A mandatory selected specialized test keeps closeout open until its outcome is
acceptable under target policy. `deferred-with-owner` requires the responsible
owner and follow-up condition; it is not implicit success.

## Workflow Closing Checklist

Before sending a final response in workflow mode, the agent must verify all of the following:

- workflow plan and task artifacts reflect the completed or deferred state;
- approval sources for requirement/design/specification transitions are
  recorded before implementation;
- required validation has passed, or skipped validation is explicitly recorded with a reason;
- each required test level has its exact target-owned command context, outcome,
  and evidence; blocked tests are not counted as passed;
- unselected spec compliance is recorded as `not-applicable`, while selected
  spec compliance has complete configuration and direct evidence of 100%
  coverage;
- approved requirements and specs, implementation completion, required tests,
  selected compliance, review disposition, validation evidence, task state,
  commit evidence, and branch/handoff state were checked separately;
- `.dev/standards/GIT-COMMIT-POLICY.md` has been checked for commit requirements;
- when the commit policy requires a commit, the commit has been created before claiming completion;
- when no commit is created, the final response cites the exact policy exception that applies.
- the workflow was not marked complete merely because its branch was merged or pushed as a checkpoint;
- workflow completion and pull-request integration were reported as separate facts; do not claim a `main` change until the pull request required by `.dev/TEAM-GIT-FLOW-RULES.MD` is merged;
- any requested merge used `--no-ff` unless the user explicitly selected another strategy.
