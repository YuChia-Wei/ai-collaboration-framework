# Agent Execution Guardrails Contract

## Purpose

This contract binds delegated, external, and fixed-head agent work to an exact
subject, explicit authority, exclusive tracked-writer ownership, and evidence
that cannot be upgraded from a synthetic substitute. It complements, rather
than replaces, `ROLE-EXECUTION-CONTRACT.md` and the external-task terminal
transport contract.

## Proportionate execution

Classify the actual operation before constructing evidence. Review preflight
uses `validate-agent-execution-guardrails.py --classify <input.yaml>` or the
same classifier through `--review-input`. Its versioned
`agent-execution-classification` input is defined in
`agent-execution-guardrails.schema.yaml`. The owner supplies observed execution
boundary, duration, change domains, snapshot isolation and permissions; unknown
facts select the full tier. A terminal label alone does not select the full tier.
Ordinary same-runtime analysis and local edits may classify inline using these
same criteria; do not create a classification artifact solely for routine work.
Ordinary same-runtime work may use the bounded envelope below. This includes
short independent read-only review of an isolated immutable ordinary change.
It must not mutate providers, access credentials, change publication or target
adoption state, or change authority, evidence custody or security contracts.

- Name the owning skill, goal, allowed reads/writes, non-goals, input sources,
  expected output, stop conditions, retry budget and parent integration owner.
- Select and load an applicable canonical role when one exists. A runtime
  execution profile is not a role; an owning skill may delegate a bounded unit
  without inventing a role when no canonical binding applies.
- Read-only workers may run together. For local edits, name exactly one tracked
  writer for the worktree and keep the parent and other workers read-only until
  it returns. Disjoint filenames do not authorize concurrent tracked writers.
- Record the actual invocation and returned result in the conversation or owning
  task. Do not create a sealed packet, lease, full role record or acceptance
  ledger solely for ordinary analysis or a local edit.
- Recheck the relevant input and diff on return. An implementation result is
  supporting evidence, never independent review. A bounded independent review
  may satisfy an ordinary review gate when its subject, criteria, authority and
  independence match; neither tier grants release admission or invents an
  actual-execution receipt.

Use the full contract below for authority, evidence-custody, security, release
or adoption changes; external or long-running validation; privileged operations;
or a shared mutable review checkout or shared frozen snapshot. Unknown risk,
boundary, duration or snapshot selects the full contract. Reviewing changes to
this custody contract itself remains a full independent review.
These are agent-dispatch requirements. Direct owner execution still follows its
adoption or publication evidence contract; it does not fabricate a delegated
role or invocation solely to perform an authorized local operation.
The distinction changes evidence overhead, not authorization, semantics, runtime
permissions, truthful reporting or required validation. Retry after a failure
still requires a material state change; attempt three needs new authorization.

## Review input preflight

Before either tier dispatches behavioral review, validate one
`independent-review-input/v1.0` with `--review-input <input.yaml>`. It contains the
classification, repository and base/head commit and tree identities, canonical
`independent-review-subject/v1` digest, nonempty review criteria, and tracked
authority paths with exact byte digests. The validator checks the clean fixed
execution checkout, Git content identities and authority bytes and returns
input, criteria and authority digests. The owning task binds and supplies that
exact input; dispatch prose is not a replacement for missing machine input.
Full packet v1.0 remains compatible but does not by itself encode these review
inputs. Validate and bind the review input separately under the dispatch
contract. Bounded review needs neither a full packet nor a snapshot lease.

Preflight reports preparation readiness only. Missing or malformed inputs are a
`preparation-failure`, not a behavioral finding or an executed review. Preserve
existing failed attempts and their counts. Record a new behavioral attempt only
when behavior was actually reviewed; this does not reset an existing retry
budget or bypass its authorization. Keep `behavior-defect`, `environment-failure`
and `provider-reconciliation` distinct. Repair and rerun only affected checks;
unchanged content, criteria and authority may reuse eligible review through the
existing content-addressed proof. Provider gates remain fresh. Failed, blocked,
interrupted and unexecuted outcomes never become passed through formatting.

## Pre-dispatch packet

Every execution selected for the full contract must validate one
`agent-execution-packet` before dispatch. The packet identifies the owning
skill, canonical role path and applicability, exact repository SHA, complete
argv and working directory, permissions, ignored artifact roots, terminal
schema and one-shot callback/event-wait transport, integration owner, stop
conditions, retry budget, and current attempt authorization.

The exact repository SHA pins a stable execution checkout and records where the
work ran. It is a locator and provenance fact, not by itself the validity key
for the resulting evidence. After history-only identity changes, eligible
evidence or independent review may be rebound only through the content-addressed
proof defined by `VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md`.

The validator resolves the owning skill's tracked canonical `skill.yaml`,
requires the named role to be an active tracked canonical role asset, and
requires that exact role path to appear in the skill's `role_bindings`.
External dispatch additionally loads the contained packet, validates its
internal canonical seal, binds the exact packet file-byte digest, and compares
subject, argv, cwd, and integration owner. A path-shaped assertion is not a
packet binding.

Static role availability is not invocation evidence. Fixed-head auditors and
external validators are read-only. Attempt three or later requires a new owner
or workflow authorization reference that was not consumed by an earlier
attempt.

## Worktree snapshot lease

A machine-readable lease binds one worktree snapshot and packet holder. An
active tracked-writer lease rejects any other observed tracked writer. Read-only
agents may coexist, and validation may write only beneath declared ignored
artifact roots. A terminal lease is `released` only after ignored output is
sealed or released and no tracked drift exists; otherwise it is `invalidated`.
The snapshot digest is derived from the observed HEAD and tracked status and is
checked against live Git state. An active holder uses a digest-bound ignored
lock whose canonical validator acquisition uses create-new semantics; an
existing lock fails before execution.

## Acceptance and report parity

An acceptance ledger maps each Issue acceptance identifier independently to
its evidence kind, exact command/profile/subject, outcome, evidence references,
and digest. The human report projection must contain the same identifiers,
outcomes, and digests. An acceptance marked `requires_actual_execution` may be
satisfied only by `actual-execution`; mock, fixture, synthetic, or unit evidence
remains supporting evidence and cannot be relabeled.
Every `actual-execution` entry carries a separately sealed terminal command
receipt with matching subject, command, profile, timing, outcome, exit code,
and evidence digest. It must state `executed: true` and `synthetic: false`;
fixture-only references are rejected as actual execution.
The entry must also name contained ignored receipt and output files. The
validator loads both files, verifies their exact byte digests, compares the
persisted receipt with the ledger copy, and rejects a missing or path-shaped
reference. A self-sealed mapping without those repository artifacts is not
actual execution evidence.

## Retry and failure identity

Failure fingerprints contain only stable metadata: failure class, command
digest, subject SHA, environment class, and bounded diagnostic codes. A retry
requires a material state-change digest. Attempt three or later additionally
requires fresh owner or workflow authorization. Repeating an unchanged failure
is a stopped attempt, not new validation.
Fresh authorizations are individually sealed and bind the exact attempt,
intended retry subject, prior failure, and authorize-retry decision; their
digests must differ from prior authorization. A retry record may carry an
optional `retry_subject_sha` when a new immutable execution subject differs
from the historical failure subject. It must be a full Git SHA and requires a
material state-change digest. Without that field, the failure subject remains
the intended retry subject for legacy records.
Attempt-three packets and retry records load the referenced workflow-local
authorization, validate its canonical seal, and require its attempt, subject,
prior failure, and single consuming packet identity to match. A prefix or an
unresolved reference is not authorization.

## Code graph freshness

Graph discovery records the indexed and current commit SHAs as provenance plus
coverage. Freshness is content-addressed: a complete index remains applicable
after a history-only commit change when Git proves that the indexed and current
commits have the same full tree. Commit-SHA inequality by itself does not make
the graph stale.

A content-stale, missing, partial, or unknown graph must be reindexed or
replaced by a tracked-file fallback over explicit paths. Search absence is
evidence only from a complete index for the current content tree or such a
tracked fallback; graph search alone is never proof of absence. If either
commit tree cannot be resolved, content equivalence is unknown and fails
closed to reindex or fallback.
Fallback paths must be contained repository-relative paths with tracked content;
an absolute or untracked search root is rejected.

## PowerShell safety

Scripts and generated snippets must not assign to PowerShell automatic or
reserved variables, case-insensitively. Use purpose-specific names such as
`$taskHost`, never `$Host`, `$PID`, `$HOME`, `$Error`, or `$Matches`.
