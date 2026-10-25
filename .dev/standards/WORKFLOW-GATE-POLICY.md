# Workflow Gate Policy

The [source development policy](SOURCE-DEVELOPMENT-POLICY.md) owns current
validation, review and PR requirements. This document owns execution-record
selection and continuation; selecting a workflow does not select more tests.

This policy defines when an agent should create workflow artifacts proactively instead of using direct mode.

## Default Modes

| Mode | Use |
| --- | --- |
| Direct mode | Conversation, exploration, or small single-pass work that does not need a durable source-project execution record. |
| Assessment mode | Read-only analysis that needs a durable report but does not authorize remediation or execution tracking. |
| Workflow mode | Authorized execution that changes source-of-truth, crosses skill boundaries, or needs durable execution-task tracking. |

Mode is determined by intent, mutation, and execution tracking, not by the number of analysis steps alone. A transient read-only analysis may use multiple passes or sub-agents in direct mode when it does not write a repository report, mutate repository files, or perform remediation. A user request for a "report" means a durable repository artifact only when the user asks to save, persist, land, or otherwise retain it in the repository. Persistence by itself selects assessment mode, not workflow mode.

## Independent Delivery Decisions

Do not collapse these decisions into one another:

| Decision | Question | Typical values |
| --- | --- | --- |
| Execution record | What durable source-project execution state is needed? | `direct`, `assessment`, `workflow` |
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
| Conversation and exploration | The conversation only. | No branch, execution record, commit, or pull request. |
| Candidate work and unapproved plan | For this source repository, a GitHub Issue; GitHub Projects provide the priority and status views. | The tracker item records possible work but does not authorize execution merely by existing or changing provider state. No repository branch or pull request is created merely to record it. |
| Authorized execution | An online GitHub Issue recording material requirement scope, with authorization and handoff recorded through the workflow mechanism. | Create the dedicated branch before the selected execution record or material repository edits. Bind the workflow and pull request to the Issue; never fabricate a tracker identifier or infer authorization from provider state. |
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
owner's explicit approval is captured in the workflow mechanism and bound to
the requirement. A conversation may supply the decision, but the Issue system
MUST NOT store authorization or handoff, including in comments. Follow the
[public requirement content policy](PUBLIC-REQUIREMENT-CONTENT-POLICY.md). The workflow remains execution truth and `main` remains
integrated repository truth.

Targets select a provider-neutral binding mode:

- `required`: an approved work item must be bound before execution;
- `optional`: a binding is preferred but explicit owner authorization may be
  recorded through the workflow without an Issue binding; or
- `disabled`: no work-item binding is used and authorization is recorded
  through the workflow mechanism, outside the Issue system.

Targets separately select whether pull-request integration enforces the
binding as `required`, treats it as `optional`, or leaves the merge gate
`disabled`. This source repository selects `required` for both material
work-item binding and the merge gate in
`.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml`.
An owner authorization remains necessary, but it never removes the requirement
to create and bind an online Issue before material work begins.

For software-development work, activation is intent-based. A high-level request
that spans planning, requirements, design, implementation, testing, review, or
closeout may activate the repository's development orchestration without the
user naming an orchestration skill. The restored `software-development-orchestrator`
coordinates stage selection and specialist handoffs. This source project owns
workflow records, source policy and Issue authority; the skill supplies no record
store or replacement source policy. Determine stages from the
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

Create a durable workflow in the selected store only when execution is
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
create a workflow execution record solely because the report is durable. Commits contain
only assessment-owned artifacts and required assessment index updates.

If remediation is authorized later, create a new workflow and reference the
assessment and selected finding IDs. If assessment and remediation are requested
together, use workflow mode for execution while keeping the assessment report
under `.dev/assessments/`.

## Workflow Artifacts

When workflow mode is used:

1. Start from the intended base branch, normally `main`.
2. Create or switch to a dedicated workflow branch before creating workflow artifacts or making material task changes.
3. Then create or explicitly continue the native workflow record and its skill-owned logical documents under [workflow storage](WORKFLOW-STORE-POLICY.md).

Branch naming, checkpoint integration, continuation branch, push, and positive
linear-versus-merge-commit selection are defined by
`.dev/TEAM-GIT-FLOW-RULES.MD`.

- Follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` for complete native identity,
  full-date IDs, timestamps, logical documents and minimum task metadata.
- Use the workflow-owning source templates for plans, tasks, reports and layout;
  the selected store holds daily execution state without requiring a Git YAML tree.
- Keep formal artifacts in their Git-owned paths and historical locators as provenance.
- Do not assume every workflow has `review-report.md` or the same report structure.
- Do not create a workflow directly on `main`. Historical workflows created before
  this rule retain their history and need a dedicated continuation branch before
  resuming material work through the selected native record.

## Task Status Rule

Each task record should move through:

```text
pending -> in_progress -> completed
```

Use `deferred` only when the task is intentionally postponed and the workflow plan or task results explain why.

## Commit Rule

Workflow stages should follow `.dev/standards/GIT-COMMIT-POLICY.md`. Commit one
validated coherent unit of tracked source, policy or formal artifacts when
Git delivery is authorized. Native progress alone does not require a commit.
Small tasks completed and validated together may share a commit.
History compression is limited to unshared, unpushed commits under the active
repository policy and must preserve approval, review, evidence, checkpoint,
handoff, and shared-history boundaries.

Merging or pushing an incomplete workflow is a checkpoint handoff, not workflow
completion. This classification is not an integration prohibition: an
`in_progress` workflow may be pushed, reviewed, or merged when those actions
are separately authorized, the checkpoint is valid, and the repository
integration gates pass. Keep the workflow and unfinished tasks active. Resume
a push-only handoff from the pushed branch; after a checkpoint merge, create
the next continuation branch from the updated target as defined by
`.dev/TEAM-GIT-FLOW-RULES.MD`.

When continuation also crosses a model, runtime, host, machine, or fresh
session, follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` using the existing
entrypoint or bounded assignment; no additional machine checkpoint is required.

## Approval and validation

Resolve pending owner decisions before dependent implementation; carry accepted
inputs forward without repeating authoring stages. Record actual authority in
the existing work record. Neither a workflow nor a plan grants provider writes,
credentials, installation or publication permission.

Before any test, apply the necessity and high-cost trigger rules in
[source development policy](SOURCE-DEVELOPMENT-POLICY.md#decide-before-running-a-test).
There is no default unit-plus-integration obligation for every edit and no
test-execution skill or legacy target profile to load for ordinary source work.
Use actual project commands and existing evidence. Required acceptance cannot
be replaced by a cheaper claim; absent infrastructure remains a limitation.

## Selected long-running work

Choose an execution surface only after establishing why the test is needed.
Keep relevant inputs stable, isolate writers and set a bounded command/timeout.
Use direct execution or a bounded delegate within authorization; duration does
not create another gate, packet, lease, external platform or report schema.
Independent review still runs against an immutable commit under source policy.
For delegated long-running work, use the available completion callback/event
rather than repeated polling. Retain the command, source, outcome, limitations
and available duration in the existing record. Interrupted, timed-out, drifted
or incomplete execution is not passed. Investigate before any affected rerun.

## Closeout

Review the completed diff and already available results against accepted scope.
Record remaining work, failures and explicit deferrals; do not trigger another
product run merely to close the workflow. Preserve each Issue's acceptance
outcome in the existing record rather than a second machine/human ledger pair.

Mark local completion only when workflow-owned work and applicable verification
are complete. Follow the commit policy for a coherent local delivery. PR checks,
integration, Issue/Project closure and publication remain separate operations.
Provider-only follow-up does not require an evidence-sync commit or reopening
completed local work. An unfinished checkpoint retains its next action/owner.

## Historical context — NOT AN EXECUTION TRIGGER

The [earlier workflow gate](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/standards/WORKFLOW-GATE-POLICY.md)
describes retired critical/full gates, universal preflight, packet/lease and
ledger workflows. Do not execute those instructions for ordinary source work.
Only an explicitly selected legacy/release obligation selects its compatible
revision and verified tools. Existing support duties and U001/P7 deferrals
remain with their owners; unavailable tooling is not restored by this note.

## Representative Decisions

| Scenario | Execution record | Delivery grouping | Integration gate | Topology |
| --- | --- | --- | --- | --- |
| Correct historical README wording with no normative, generated, release, security, or migration truth change | direct | one bounded change | pull request in this source repository | linear |
| Remove one stale index entry and validate it in the same turn | direct | one bounded change | pull request in this source repository | linear |
| Retain a read-only repository audit without remediation | assessment | one assessment | pull request in this source repository | normally linear |
| Implement several Issues on one branch with shared validation, reviewers, release gate, and rollback | direct or one workflow according to unique execution state | one cohesive multi-Issue delivery | one pull request | select from boundary value, not Issue count |
| Publish or reconcile a release across hosted and local state | workflow | one release lifecycle | pull request plus owner-controlled publication gates | merge commit when the grouped lifecycle boundary must remain visible |
| Change canonical behavior across portable policy, routing, validators, and independent verification | workflow | one policy outcome | pull request | linear or merge commit according to whether the branch boundary adds durable information |
