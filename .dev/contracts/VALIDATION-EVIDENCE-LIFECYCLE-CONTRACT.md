# Validation Evidence Lifecycle Contract

This source-project contract explains how to retain and interpret validation
results. The [source development policy](../standards/SOURCE-DEVELOPMENT-POLICY.md)
owns test selection, independent review and the PR gate. It does not require a
receipt platform or a separate evidence store for ordinary source work.

## Decide whether an earlier result still applies

Inspect the actual diff and the check's inputs and direct dependencies. Consider
environment or provider changes only where the conclusion depends on them.
Record the original result and a short reason when relying on it; do not claim
that an unexecuted check ran on the new revision.

| Relevant change | Treatment |
| --- | --- |
| No change to the behavior or inputs that the check establishes | Keep the original result; no repeat execution is needed |
| Behavior, relevant input, assertion or dependency changed | Run the affected checks if needed to establish the changed claim |
| Environment changed and the result depends on it | Reassess that environmental claim; do not invalidate unrelated results |
| PR head, required checks, effective reviews or Issue/Project state | Read current provider facts at the operation that needs them |
| Commit identity changed without a relevant content change | Confirm the relevant diff remains equal; a new SHA alone is not a test trigger |

Unknown impact calls for bounded investigation of the relevant dependency. Do
not declare unknown coverage passed or automatically run an entire matrix.
Ordinary decisions can be explained in the existing conversation, task or PR;
they need no new hash inventory, dependency resolver, receipt or paired reports.

## Independent review and concurrent work

Review one immutable diff with identified criteria and governing rules. Keep the
reviewer read-only and separate from the writer. A relevant content, criteria or
authority change requires affected review again. For identity-only changes,
compare the reviewed diff and applicable rules with the current subject and
retain the original reviewer/result; no new review is implied by the SHA.

Keep a selected test's input stable while it runs. Stop or qualify its result
if a concurrent change affects that input. An unrelated report update does not
invalidate product evidence. Only actual independent review or a specifically
selected immutable execution requires a fixed commit; ordinary focused local
checks may run against identified working-tree changes.

## Record the actual outcome

Use the existing work record for the command or review scope, source, result,
relevant environment, limitations and next action. Retain failures and their
repair disposition; later success does not erase them. Failed, blocked,
interrupted, skipped, not-run and unknown results are not passed.

Unit, fixture, installation, actor and hosted results establish different claims.
A hash establishes content identity, not that an agent read or followed it.
Selected runtime settings are not observed runtime identity or provider usage.
Do not infer actual cost, general model reliability or a saving percentage from
missing or incomparable measurements. No cost dataset is required.

Required current-head hosted checks remain fresh under source policy. Local
results never replace the PR gate. Provider read-back and record-only closeout
do not themselves require another product test run or evidence-sync commit.

## Historical context — NOT AN EXECUTION TRIGGER

The previous manifest/rebind/closure-resolver platform and receipt schemas are
retained evidence formats, not an ordinary source route. Their earlier meaning
is available in the [pre-simplification contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/contracts/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md).
Do not follow its commands because this note or a historical record mentions
them. Only an explicitly selected legacy/release obligation may use its own
compatible revision and verified tools. Missing tools remain unavailable;
existing support/recovery duties and their original evidence are not waived.
