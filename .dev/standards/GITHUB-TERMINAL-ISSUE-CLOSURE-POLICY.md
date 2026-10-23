# GitHub Terminal Issue Closure Policy

This source-only policy governs final versus partial delivery of GitHub Issues.
The [source development policy](SOURCE-DEVELOPMENT-POLICY.md) owns review and
the PR gate; [GitHub work management](GITHUB-WORK-MANAGEMENT-POLICY.yaml) owns
provider configuration. Closing keywords and provider state never authorize work.

## Per-Issue delivery intent

For each Issue delivered by a PR, state one disposition in its existing body:

- `terminal-close`: final accepted delivery, with an owner-authorized matching
  `Closes`, `Fixes` or `Resolves` keyword.
- `deferred`: Issue closure is not selected, using `Refs #<number>` with the
  actual product delivery status and any remaining functional limitation or
  dependency; no closing keyword for that Issue. Completed implementation may
  still be reference-only; do not invent a functional gap to explain its lifecycle.

The public body contains product delivery facts under
[the public content boundary](PUBLIC-REQUIREMENT-CONTENT-POLICY.md).
Record closure authority, execution checkpoints and next actions in the workflow,
not in the Issue or PR body, comments or review discussions.

Do not mix dispositions for one Issue or put closing keywords in commits to
bypass the selected PR intent. Reference-only background Issues do not become
delivered work. No separate declaration record or machine receipt is needed.

## Before integration

Obtain fresh PR head/base, effective review state and required checks. Apply
source policy's conditional independent review and maintainer acceptance.
Require actual current-head `Source change gate` success for PRs selected by
the native `src/**` or `tools/**` filters. Outside those paths it is not
applicable, not a fabricated pass. Respect any additional actual provider
protection; discrepancies need their owner's reconciliation, not implicit
settings changes or invented checks.

Confirm the selected Issue scope and applicable verification are complete for
final delivery. Failed, blocked, cancelled, timed-out, missing or unknown
required results do not satisfy that claim. Pending implementation keeps a
delivery deferred. A relevant change after independent review needs affected
review again; a new SHA alone does not require another review or local test run.

Use live provider read-back at the integration decision. Do not introduce a
second custom admission gate, packet, v3 receipt or snapshot-validation loop.
Local results cannot replace hosted checks, and an author's inspection cannot
replace required independent review.

## After integration or administrative closure

Read the actual integration commit, each delivered Issue state and its relevant
Project fields separately. A successful merge does not prove Issue closure or
Project completion. A deferred Issue remains open and must not be represented
as Done. Perform provider mutations only under actual owner authorization.

An already integrated, accepted delivery may be closed administratively with
explicit owner approval; do not invent a historical closing keyword. Record
the actual Issue/Project outcomes and disclose missing or mismatched read-back.
Do not report provider closeout complete while required state is unconfirmed.

Workflow completion, integration and Issue/Project closure are separate facts.
Later provider-only read-back need not reopen completed local implementation or
produce a tracked evidence-sync commit. It does not trigger another product run.
Release, installation and downstream adoption retain their own authorization.

## Historical context — NOT AN EXECUTION TRIGGER

The [earlier closure contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md)
documents retired declaration/admission/reconciliation receipt formats. Retained
validators and schemas interpret selected compatible records; their existence
does not activate them for new source PRs. Do not follow historical commands
from this note. Explicit legacy/release work keeps its selected revision,
evidence and verified-tool prerequisites; no support or recovery duty is waived.
