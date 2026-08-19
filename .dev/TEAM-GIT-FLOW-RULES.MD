# Repository Branch And Merge Policy

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

## Normal Flow

1. Start from a clean `main`.
2. Create or switch to a short-lived branch before workflow artifacts or material edits:

   ```text
   <prefix>/<topic>
   ```

3. Make focused commits following `.dev/standards/GIT-COMMIT-POLICY.md`.
4. Run the narrowest meaningful validation.
5. Push the branch and open a pull request to `main` when transport is
   authorized. A draft pull request is optional before review or handoff.
6. Select linear integration or a merge commit from the rules below after the
   pull request's required validation and review. Do not push unreviewed work
   directly to `main`.
7. Confirm `main` is clean after the pull-request merge.

## Workflow Branches

When work uses `.dev/workflows/<workflow-id>/`, use:

```text
codex/<workflow-id>
claude/<workflow-id>
```

Examples:

```text
codex/2026-07-11-ai-context-skill-and-doc-cleanup
claude/2026-07-11-payment-refactor-stage-1
```

Create the branch before creating `.dev/workflows/<workflow-id>/workflow.yaml`. Record the branch and base branch in the locator.

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

For this source repository, repository integration and GitHub Issue closure
also remain separate facts. Every named Issue in a material pull request must
declare exactly one `terminal-close` or `deferred` disposition under
`.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`. A terminal disposition
requires a matching approved closing keyword and post-merge Issue/Project
read-back; a deferred disposition uses `Refs`, records its reason and next gate
or owner, and must remain open. A closing keyword never authorizes work.

The required pull-request check validates only the tracked declaration against
the live PR event and checkout head. Immediately before integration, obtain a
fresh provider read-back and run
`.ai/scripts/validate-terminal-issue-closure.py` with the current event snapshot
and `--capture-admission-evidence`. The validator emits the verified snapshot
to stdout and writes no repository path; trusted orchestration may retain it
under ignored validation artifacts. A replay instead uses the untracked
`--admission-evidence` snapshot plus `--verify-provider-live`. The
provider configuration owns the required-check
set, and the live GitHub response must exactly match the snapshot's provider
review/check-run identities and timestamps. That merge-admission run must bind
the approved review and the complete successful required-check set to the same
immutable head. Do not commit the volatile snapshot; any head drift
invalidates it and requires a fresh independent audit, hosted read-back, and
admission run.

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

When work must move to another machine or session before all workflow tasks are complete:

1. Commit a coherent validated checkpoint and keep the workflow `active`.
2. Prefer pushing the workflow branch when integration into `main` is not required.
3. For a push-only handoff, fetch the remote branch on the next machine and resume that branch, or create a continuation branch from that remote branch. Do not restart from `main`, because it does not contain the unmerged checkpoint.
4. If integration is explicitly requested, push the branch and integrate its
   pull request using the selected topology. A checkpoint or handoff normally
   retains a merge commit because the branch boundary carries resume evidence;
   do not bypass the pull-request gate.
5. After a checkpoint merge, start from the updated target branch and create a new continuation branch such as `<prefix>/<workflow-id>-cont-02`; do not continue material work on the target branch.
6. Record the checkpoint type (`push` or `merge`), commit, remote or target, timestamp, reason, last completed task, and exact resume branch/action in the workflow plan.
7. Update locator `branch`, `base_branch`, `updated_at`, and branch history only when the active branch segment changes.

A checkpoint push or merge is a transport and handoff boundary. Neither is a workflow completion signal.

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
