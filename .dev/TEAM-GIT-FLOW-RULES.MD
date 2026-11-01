# Repository Branch And Merge Policy

The [source development policy](standards/SOURCE-DEVELOPMENT-POLICY.md) owns
validation and conditional review. This document owns Git branch and transport
decisions; Git operations do not create additional local test requirements.

This document is the canonical owner of repository branch naming, workflow
branch lifecycle, checkpoint handoff, push continuation, and merge strategy.

The repository uses a single-trunk, short-lived-branch model. It is
GitHub-Flow-like because work branches start from and return to `main`, but it
adds repository-specific workflow artifacts, checkpoint continuation, and a
positive merge-topology decision. It is not classic Git Flow: there is no persistent
`develop`, release, or hotfix integration hierarchy. It is also not strict
trunk-based development because workflow-mode changes do not occur directly on
`main`.

## Core Rule

`main` is the only long-lived trunk.

All feature, workflow, documentation, and agent work branches start from `main`.
Every change entering `main` must have a pull request; do not push unreviewed
work directly to `main`. A local fast-forward is allowed only after the pull
request's required checks and review gates pass, as defined below. An explicitly
requested earlier integration is a checkpoint and does not close the workflow.

## Branch Model

### Long-Lived Branches

| Branch | Role |
| --- | --- |
| `main` | Single trunk and integration branch. Must stay coherent and reviewable. |

Do not create persistent `develop`, `baseline`, `release`, or agent-specific long-lived branches for normal work.

### Short-Lived Branches

Use short-lived branches for bounded work. When workflow mode applies, a
dedicated workflow branch is mandatory. Direct mode remains governed by
`.dev/standards/WORKFLOW-GATE-POLICY.md` and does not create workflow artifacts.

| Prefix | Use |
| --- | --- |
| `codex/` | Codex-owned workflow or task branch. |
| `claude/` | Claude-owned workflow or task branch. |
| `docs/` | Human-authored documentation branch when no agent prefix is appropriate. |
| `fix/` | Small human-authored fix branch when no agent prefix is appropriate. |

Use the agent prefix when an agent performs the work.

## Worktree Location And Failed Setup

When worktree creation, client registration or access fails, establish separately
whether the checkout exists, Git registers it, the client registers it, and the
current execution surface can read/write it. Preserve actual errors and unknown
results. Registration failure or access denied alone does not establish a path
length, filesystem or client defect.

For an existing checkout, inspect its current Git identity and the client's
actually available attach or repair capability before creating another checkout.
Do not bypass access controls or silently create a replacement inside the main
checkout's ignored temporary tree. Missing client capabilities remain unavailable;
Git registration alone does not prove client attachment or usable access.

Select a location from the explicitly configured worktree root when usable, with
a short, visible path appropriate to the selected checkout and intermediate
operations. Check its current accessibility, filesystem and destination occupancy.
An unavailable configured root needs an explicit alternative within task authority;
never assume a drive letter, RAM disk or client tool is always available. Keep
durable work out of disposable cleanup scope. A short path is risk reduction,
not evidence that a particular failure was caused by length.

Before an authorized move or deletion of a worktree, verify the resolved absolute
source/destination, intended containment, Git worktree registration and HEAD,
dirty tracked changes, untracked and ignored data, destination occupancy, and
the required recovery or preservation of work. An occupied destination or unknown
state stops that action until reconciled. Preserve user-owned data; neither an
ignored path nor a failed registration grants deletion, relocation or prune
authority. Use the supported Git/client operation only after those facts and
permissions are established, then read back its actual result.

These rules apply to worktree setup/recovery and cleanup that may contain a
worktree. They add no universal gate or record requirement to ordinary temporary
file cleanup. The historical
[candidate observation](lessons/records/lesson-2a0d6ef0b36e48f09278e272108b4a47.lesson.json)
is supporting experience, not proof of a reproduced client or disk defect.

## Normal Flow

1. Start from a clean `main`.
2. Create or switch to a short-lived branch before workflow artifacts or material edits:

   ```text
   <prefix>/<topic>
   ```

3. Make focused commits following `.dev/standards/GIT-COMMIT-POLICY.md`.
4. Decide whether the actual change needs tests under source policy; run only the selected checks.
5. Push the branch and open a pull request to `main` when transport is
   authorized. A draft pull request is optional before review or handoff.
6. Select linear integration or a merge commit from the rules below after the
   pull request's required validation and review. Do not push unreviewed work
   directly to `main`.
7. Confirm `main` is clean after the pull-request merge.

## Workflow Branches

When work selects workflow mode, regardless of execution-record storage, use:

```text
codex/<workflow-id>
claude/<workflow-id>
```

Examples:

```text
codex/2026-07-11-ai-context-skill-and-doc-cleanup
claude/2026-07-11-payment-refactor-stage-1
```

Create the branch before creating or materially changing the selected workflow
record. Record branch and base branch in native metadata under the
[workflow store policy](standards/WORKFLOW-STORE-POLICY.md). Historical Git
locators retain their original branch provenance.

## Assessment Branches

Standalone durable assessments use a dedicated short-lived branch without a
workflow locator:

```text
codex/assessment/<lowercase-assessment-id>
claude/assessment/<lowercase-assessment-id>
```

Create the branch before `.dev/assessments/<assessment-id>/assessment.yaml` or
the report. Keep assessed surfaces read-only and commit only assessment-owned
artifacts plus required assessment index updates. If an assessment is produced
inside an existing authorized workflow, use the workflow branch instead of
creating a competing assessment branch.

Assessment branches follow the normal pull-request and topology-selection rule.

## Integration Gate And Merge Topology

Every change entering `main` requires a pull request. The pull-request gate and
the Git topology are separate decisions: workflow mode does not require a merge
commit, and direct mode does not bypass review.

Repository integration is the reviewed Git event that enters the configured
integration branch. It is not workflow completion, assessment finality,
release-source validation, hosted publication, or publication finalization.

For each delivered Issue, declare final or deferred intent under the
[Issue closure policy](standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md).
Immediately before integration, read the actual PR head/base, effective review
state and required checks. Require current-head Source change gate success
when the native src/** or tools/** PR filters apply. Respect actual provider
protection and the source policy's independent-review conditions. Missing
required facts block integration; do not invent a pass or alter protection.

No custom admission validator, declaration record, packet or v3 receipt is
required for ordinary source PRs. A changed reviewed subject needs affected
review; identity-only changes require a comparison, not repeated review or
local tests. Record the actual integration commit separately from the PR head.
Issue and Project closure need their own authorized action and live read-back;
they do not require a source repair or evidence-sync commit.

### Linear Integration

Choose linear integration when the branch boundary adds no durable information
beyond the commits and pull request, especially when these conditions hold:

- the delivery is one coherent outcome and has no independently resumable
  checkpoint, approval, or handoff boundary;
- commits are already reviewable in order, or the branch is a single coherent
  commit;
- release, migration, publication, security, or external-host lifecycle state
  does not need to remain grouped by a merge node; and
- rollback does not require treating the branch as one retained topology unit.

Linear integration is a normal path for direct-mode fixes, standalone
assessments, documentation changes that do not alter normative or release
truth, and workflow deliveries whose branch boundary carries no additional
meaning. A historical README-only update normally uses direct mode, a pull
request, and linear integration unless it changes normative, generated,
release, security, or migration truth.

Use either:

- GitHub **Rebase and merge**; or
- after the pull request exists and all required hosted checks and review gates
  pass, a maintainer-selected local `git merge --ff-only <branch>` followed by
  an immediate push of `main` and pull-request/main read-back.

The local fast-forward path is not permission to push unreviewed work directly
to `main`. It must not bypass branch protection, required checks, approvals, or
the repository's pull-request evidence.

### Merge-Commit Integration

Choose a merge commit (`--no-ff` or the GitHub merge-commit equivalent) when the
branch boundary itself is durable evidence, including one or more of these:

- multiple meaningful commits form a review or rollback unit that should
  remain visibly grouped;
- the branch contains an approval, checkpoint, cross-runtime, cross-host, or
  handoff boundary;
- release, publication, migration, deployment, security, or other external
  lifecycle reconciliation must remain visible as one integration event; or
- repository or owner policy explicitly requires a merge node for this
  delivery.

Commit count, Issue count, file count, and workflow mode are signals only. None
of them selects topology by itself. Record the selected topology and reason in
the pull request or workflow when workflow mode applies.

## Checkpoint Handoff And Cross-Machine Continuation

An `in_progress` status does not by itself block push, pull-request creation,
or integration. Such a workflow may be integrated when separately authorized
and all repository integration gates pass. Integration does not imply workflow
completion; preserve the required checkpoint and continuation state.

When work must move to another machine or session before all workflow tasks are complete:

1. Save a native handoff with complete reference, revision, source/branch and next
   action; keep unfinished workflow state active. For separately authorized,
   coherent tracked changes, commit a validated checkpoint. A session changing
   only native records requires no record-only Git commit.
2. Prefer pushing the workflow branch when tracked-change transport is authorized
   and integration into `main` is not required. Native database access/backup and
   explicit replica delivery follow the store policy; Git push does not transport
   that database or make another machine's store available.
3. For a push-only handoff, fetch the remote branch on the next machine and resume that branch, or create a continuation branch from that remote branch. Do not restart from `main`, because it does not contain the unmerged checkpoint.
4. If integration is explicitly requested, push the branch and integrate its
   pull request using the selected topology. A checkpoint or handoff normally
   retains a merge commit because the branch boundary carries resume evidence;
   do not bypass the pull-request gate.
5. After a checkpoint merge, start from the updated target branch and create a new continuation branch such as `<prefix>/<workflow-id>-cont-02`; do not continue material work on the target branch.
6. Record any actual checkpoint type (`push` or `merge`), commit, remote or target,
   timestamp, reason, last completed task and exact resume branch/action in the
   native entrypoint. A record-only handoff states that no Git transport occurred.
7. Update native `branch`, `base_branch`, `updated_at` and branch history only when
   the active branch segment changes; preserve historical locator bytes.

A checkpoint push or merge is a transport and handoff boundary. Neither is a
workflow completion signal.

## Commit Rule

Commit formatting and commit timing are defined in:

```text
.dev/standards/GIT-COMMIT-POLICY.md
```

Do not duplicate detailed commit message rules here.

## Workflow Gate

When deciding whether a task needs a workflow branch and workflow artifacts, follow:

```text
.dev/standards/WORKFLOW-GATE-POLICY.md
```

## Cleanup Before Merge

Before merging a short-lived branch back to `main`:

- confirm workflow task statuses are accurate;
- confirm validation was run or skipped with a documented reason;
- remove accidental temporary files;
- keep intentional workflow artifacts when they are part of the decision trail;
- run `git status --short` and confirm only intended changes were committed.

## Outdated Branch Models

The following branch models are not used for current work:

- `develop` as a second long-lived integration line;
- agent-specific long-lived branches.

Reintroduce any of these only after updating this document and the related workflow policy.
