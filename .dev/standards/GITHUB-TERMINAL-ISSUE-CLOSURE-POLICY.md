# GitHub Terminal Issue Closure Policy

This source-repository-only policy governs how a pull request references and
closes named GitHub Issues. It is not portable target guidance, and a closing
keyword never authorizes work.

## Per-Issue Delivery Disposition

Every Issue named by a pull request has exactly one disposition:

- `terminal-close`: the pull request is the final accepted delivery for that
  Issue and uses one approved closing keyword for that Issue.
- `deferred`: the pull request is a checkpoint or partial delivery, uses
  `Refs #<issue-number>`, contains no closing keyword for that Issue, and
  records both `closure_deferred_reason` and the next terminal gate or owner.

A pull request may mix the two modes for different Issues. A single Issue may
not use both modes or both reference forms.
The complete set of `Refs`, `Closes`, `Fixes`, and `Resolves` targets in the PR
body must equal the record's Issue set. Qualified targets must name this
repository; foreign-repository references fail. Commit messages in the
base-to-head range may not contain closing keywords, so a deferred or omitted
Issue cannot bypass the PR-body disposition gate when the commit reaches the
default branch.

## Terminal-Close Gate

`terminal-close` is valid only after all of the following are observed for the
named Issue:

- the online Issue binding and explicit owner authorization already exist;
- the delivery is final and accepted for that Issue;
- workflow scope, tasks, and every applicable verification are complete;
- review is approved and every hosted check succeeded;
- the pull request merged at the exact expected head;
- the pull-request body contains the matching approved closing keyword; and
- post-merge read-back proves the same merged head, the Issue is closed as
  completed, and its Project status is `Done`.

A failed, cancelled, or timed-out hosted check, review block, head drift,
missing read-back, or mismatched Issue or Project state is nonterminal.

## Deferred Gate

`deferred` requires `Refs #<issue-number>`, forbids `Closes`, `Fixes`, and
`Resolves` for that Issue, and requires a non-empty deferred reason plus an
exact next terminal gate or owner. If the pull request has merged, read-back
must prove the deferred Issue remains open and is not projected as `Done`.

## Enforcement And Distribution

`.dev/backlog/providers/github.yaml` owns the selected provider configuration.
`.ai/scripts/validate-terminal-issue-closure.py` validates durable disposition
records deterministically through three fail-closed validation stages without
adding another closure mode:

- `declaration` validates the per-Issue PR intent and reference syntax;
- `merge-admission` binds the current PR number and head, approved review,
  exact required-check context set, and every successful required check to the
  same head; and
- `reconciliation` additionally binds the expected/merged head and post-merge
  Issue/Project read-back.

On a GitHub pull-request event, including a PR-body `edited` activity, the
required validator check selects exactly one
`declaration` record bound to that current PR number and validates the live
event body, event head, and checked-out head. A missing, duplicate,
historical-only, non-declaration, or mismatched record fails. That required
check proves declaration only; it must not be represented as merge admission.

Before merge, the integrator must use `--capture-admission-evidence` with a
fresh event snapshot to generate, validate, and emit the provider read-back
without writing a repository path. Trusted orchestration may retain that
stdout under ignored validation artifacts. Replaying such a snapshot requires the current event snapshot,
`--admission-evidence <path>`, and `--verify-provider-live`. The admission snapshot uses contract
`github-terminal-issue-closure-admission` and supplies the exact PR number,
repository, base, head, body, approved review, required-check context set, and successful
hosted checks.
The provider configuration, not the snapshot, owns the complete required-check
context set. Live verification re-reads GitHub with `GITHUB_TOKEN` and requires
the snapshot's provider review/check-run identifiers, timestamps, conclusions,
heads, PR body, repository, and base to match that fresh response exactly. The
live PR metadata must also match the current event before its base-to-head commit range
is accepted. A replayed snapshot without
live verification is rejected. The validator itself never writes the capture,
eliminating repository symlink/reparse and overwrite races. It overlays those verified volatile facts
only onto a tracked declaration in memory and requires every fact to match the
same event and checkout head. A later lifecycle stage cannot be downgraded by
an admission overlay. The snapshot must remain untracked, must not be reused after head drift, and must
not be committed to the candidate it validates. Missing admission evidence is
a merge blocker, even when the declaration check passes. This live-verified non-mutating
overlay avoids a self-referential commit whose evidence changes its own head.

Without an event the validator is only a static contract check. The aggregate
source governance profile runs the declaration validator and its GWT tests.
This policy, its validator and tests, provider
configuration, dated evidence, and the source PR template are excluded from
downstream packages; historical records are not rewritten.
