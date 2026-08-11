# Workflow Gate Policy

This policy defines when an agent should create workflow artifacts proactively instead of using direct mode.

## Default Modes

| Mode | Use |
| --- | --- |
| Direct mode | Conversation, exploration, or small single-pass work that does not need a durable repository execution record. |
| Assessment mode | Read-only analysis that needs a durable report but does not authorize remediation or execution tracking. |
| Workflow mode | Authorized execution that changes source-of-truth, crosses skill boundaries, or needs durable execution-task tracking. |

Mode is determined by intent, mutation, and execution tracking, not by the number of analysis steps alone. A transient read-only analysis may use multiple passes or sub-agents in direct mode when it does not write a repository report, mutate repository files, or perform remediation. A user request for a "report" means a durable repository artifact only when the user asks to save, persist, land, or otherwise retain it in the repository. Persistence by itself selects assessment mode, not workflow mode.

## Independent Delivery Decisions

Do not collapse these decisions into one another:

| Decision | Question | Typical values |
| --- | --- | --- |
| Execution record | What durable repository execution state is needed? | `direct`, `assessment`, `workflow` |
| Delivery grouping | Which approved outcomes must move, validate, review, and roll back together? | one outcome per delivery, or several work items in one cohesive delivery |
| Integration gate | What review or automation must pass before the target branch changes? | direct push where target policy permits, or pull request |
| Git topology | Does a grouped branch boundary carry information that must remain visible? | linear integration or merge commit |

Workflow mode does not imply one workflow per Issue, a pull request does not
imply a merge commit, and a single commit does not imply low risk. Decide each
axis from its own evidence and target policy.

## Work-Management Lifecycle

Keep work-management state distinct from repository execution state. A planning
word, a detailed breakdown, or a multi-step conversation does not by itself
authorize repository work or create a workflow.

| State | Durable home | Repository execution consequence |
| --- | --- | --- |
| Conversation and exploration | The conversation only. | No branch, workflow locator, commit, or pull request. |
| Candidate work and unapproved plan | For this source repository, a GitHub Issue; GitHub Projects provide the priority and status views. | The tracker item records possible work but does not authorize execution merely by existing or changing provider state. No repository branch or pull request is created merely to record it. |
| Authorized execution | An online GitHub Issue that records the material scope plus explicit owner authorization, and a skill-owned workflow when the workflow gate applies. | Create the dedicated branch before the locator or material repository edits. Bind the workflow and pull request to the Issue; never fabricate a tracker identifier or infer authorization from provider state. |
| Integrated repository fact | `main`, after the required pull request is merged. | Do not describe branch-only or tracker-only work as integrated repository truth. |

GitHub Issues and Projects are this repository's selected work-management
authority, not a framework-wide requirement for target repositories. The
framework stays provider-neutral. This repository does not define a separate
repository proposal artifact class: a retained but unapproved plan belongs in
a GitHub Issue. Every new material implementation or release scope needs its
online Issue before execution; if the provider is unavailable, stop before
material work rather than inventing a repository-local substitute or
overloading an `in_progress` workflow.

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
`disabled`. This source repository selects `required` for both material
work-item binding and the merge gate in `.dev/backlog/providers/github.yaml`.
An owner authorization remains necessary, but it never removes the requirement
to create and bind an online Issue before material work begins.

For software-development work, activation is intent-based. A high-level request
that spans planning, requirements, design, implementation, testing, review, or
closeout may activate the repository's development orchestration without the
user naming `software-development-orchestrator` or any downstream skill. Determine stages from the
requested outcome, current artifacts, repository policy, and approval state,
not from skill names alone.

## Delivery Cohesion For Multiple Work Items

Before creating workflow artifacts for multiple approved Issues or other work
items, decide the delivery unit. Group the items into one workflow, branch,
validation path, and pull request when they share all material delivery
boundaries:

- one coherent user or maintainer outcome;
- the same base and work branch;
- substantially the same required validation and environment;
- the same reviewer, approval, security, and ownership boundary;
- the same release gate or deployment horizon; and
- atomic integration and rollback are acceptable.

Split the delivery when an item can and should be reviewed, released, reverted,
or resumed independently; when approval, security, ownership, environment, or
release boundaries differ; or when the owner explicitly selects independent
delivery. Ask the owner only when these boundaries are materially ambiguous.

A workflow and pull request may bind multiple approved work-item identifiers.
Record all applicable identifiers in workflow and commit metadata, but do not
create one workflow, task, branch, or pull request merely because there is more
than one Issue. Issue count is traceability input, not delivery cardinality.

## Must Create a Workflow

Create a durable workflow and its discovery locator only when execution is
authorized, or the owner requires durable cross-session execution tracking,
**and both of these tests pass**:

1. The workflow will preserve unique approval, coordination, execution,
   handoff, external-lifecycle, or recovery state that is not adequately owned
   by an Issue, ADR, assessment, commit, pull request, release record, or the
   conversation.
2. At least one material execution condition applies:
   - independently meaningful stages need status or approval checkpoints;
   - cross-skill, cross-owner, sub-agent, host, runtime, or session handoff is
     required;
   - canonical rules or future agent behavior need staged remediation plus
     independent verification;
   - `.ai/`, `.dev/`, `.agents/`, `.claude/`, or wrapper routing crosses
     ownership or compatibility boundaries;
   - release, publication, migration, deployment, or another external
     lifecycle must be resumed or reconciled safely;
   - failure, rollback, or partial completion requires durable task state; or
   - the owner explicitly requests workflow tracking for the authorized work.

Candidate tracker management, discussion, plan drafting, and task breakdown are
not workflow triggers unless they also meet the authorization condition above.

File count, commit count, Issue count, skill-invocation count, and the number of
analysis steps are signals only. They must not independently select workflow
mode.

### Low-Task Proportionality Review

One task, or fewer than three substantive tasks, is a review signal rather than
a prohibition. Before retaining such a workflow, record which unique state from
the first test above justifies it. Release publication, an external-host
checkpoint, an approval boundary, or an independently resumable migration can
justify a one-task workflow.

Do not invent tasks to satisfy a count. Generic validation, evidence formatting,
provider read-back, commit creation, pull-request creation, and workflow
closeout are lifecycle steps unless they produce independently owned outcomes.
If the only proposed task is the change itself and no unique workflow state can
be named, return to direct mode.

## Direct Mode Is Enough

Direct mode is acceptable when all of these are true:

- the change is one coherent, bounded execution unit;
- only one skill is needed;
- an Issue, ADR, assessment, commit, pull request, release record, or the
  conversation adequately owns any required decision trail;
- no independently resumable task state, approval transition, or external
  lifecycle must be preserved;
- validation can be completed in the same turn.

Direct mode may touch several files when the change is mechanical and remains
within one ownership and validation boundary. Conversely, a one-file change may
need workflow mode when it carries an external lifecycle or durable approval
checkpoint.

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

Branch naming, checkpoint integration, continuation branch, push, and positive
linear-versus-merge-commit selection are defined by
`.dev/TEAM-GIT-FLOW-RULES.MD`.

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

## Long-Running Validation Delegation Gate

This gate applies in direct and workflow mode. It changes the execution surface,
not the selected validation, severity, or pass/fail contract.

A command is long-running when any condition is true:

- its selected profile is `release` or `nightly-full`;
- it selects a full package, compatibility, or history matrix;
- repository evidence predicts at least 120 seconds of wall time; or
- a prior comparable execution observed at least 120 seconds of wall time.

Before dispatch, the owning conversation must finish tracked mutations, run the
narrow focused checks, obtain a clean worktree, and bind the exact command to a
full immutable commit SHA. Pending design decisions, mutable source state, and
unbounded credentials are dispatch blockers.

Run the command in a separate external runtime task using the least expensive
execution profile that can faithfully execute and report the bounded command.
Its scope is read-only except for ignored validation logs or artifacts. It must
not repair, commit, push, mutate Issues or Projects, or broaden the command.

The owning conversation may read back dispatch once, then must yield. It must
not issue repeated waits, status probes, or progress narration. The external
task returns one completion report containing:

- immutable commit SHA and clean-state preflight;
- exact command and working directory;
- start, completion, and wall-time evidence;
- selected, executed, reused, failed, blocked, warning, deferred, and
  not-applicable counts when the runner exposes them;
- exit code plus log, evidence, or bounded output references; and
- final tracked worktree state.

Timeout, interruption, missing completion evidence, and blocked execution are
non-passing. The owning workflow remains open until it receives and accepts an
allowed final outcome. When the runtime cannot provide an independent task that
reports completion without polling, record `blocked-by-environment` or create a
fresh-session handoff; never substitute synchronous polling in the owning
conversation.

Keep canonical aggregate runners because they own profile selection,
dependency ordering, unified evidence, and fail-closed classification. A future
parallel runner is allowed only after independent contract coverage proves its
dependency DAG, artifact and temporary-state isolation, bounded concurrency,
deterministic evidence ordering, timeout propagation, and fail-closed
cancellation. Until then, reduce interaction cost through external execution,
not unverified parallelism or removal of the aggregate gate.

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
- delivery grouping was evaluated before separate workflows were created for multiple work items;
- a workflow with fewer than three substantive tasks records the unique state that justified workflow mode without padding the task list;
- integration gate and Git topology were selected independently under `.dev/TEAM-GIT-FLOW-RULES.MD`.

## Representative Decisions

| Scenario | Execution record | Delivery grouping | Integration gate | Topology |
| --- | --- | --- | --- | --- |
| Correct historical README wording with no normative, generated, release, security, or migration truth change | direct | one bounded change | pull request in this source repository | linear |
| Remove one stale index entry and validate it in the same turn | direct | one bounded change | pull request in this source repository | linear |
| Retain a read-only repository audit without remediation | assessment | one assessment | pull request in this source repository | normally linear |
| Implement several Issues on one branch with shared validation, reviewers, release gate, and rollback | direct or one workflow according to unique execution state | one cohesive multi-Issue delivery | one pull request | select from boundary value, not Issue count |
| Publish or reconcile a release across hosted and local state | workflow | one release lifecycle | pull request plus owner-controlled publication gates | merge commit when the grouped lifecycle boundary must remain visible |
| Change canonical behavior across portable policy, routing, validators, and independent verification | workflow | one policy outcome | pull request | linear or merge commit according to whether the branch boundary adds durable information |
