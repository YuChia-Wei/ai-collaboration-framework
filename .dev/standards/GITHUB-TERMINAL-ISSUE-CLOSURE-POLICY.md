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
records deterministically. The aggregate source governance profile runs that
validator and its GWT tests. This policy, its validator and tests, provider
configuration, dated evidence, and the source PR template are excluded from
downstream packages; historical records are not rewritten.
