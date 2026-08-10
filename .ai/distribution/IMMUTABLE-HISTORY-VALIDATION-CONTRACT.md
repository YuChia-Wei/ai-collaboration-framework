# Immutable-History Validation Contract

## Scope

This is a source-repository-only contract. It protects the retained evidence
under `.dev/workflows`, `.dev/assessments`, and `.dev/releases`; it does not
convert that history into a downstream requirement or payload.

The machine-readable authority is
`.ai/distribution/validation/immutable-history-validation.yaml`. It declares
the exact history roots and index files, validator and schema fingerprint
paths, full-validator commands, receipt path, and routine/full profile sets.

Downstream repositories have no immutable-source-history receipt. Their
applicable boundary is target-local AI-context validation through
`validate-ai-context-target.py`.

## Full refresh

Run a refresh only from a clean worktree whose source revision is committed:

```text
python .ai/scripts/validate-immutable-history.py refresh \
  --repo . \
  --contract .ai/distribution/validation/immutable-history-validation.yaml \
  --receipt .ai/distribution/validation/immutable-history-receipt.yaml \
  --head HEAD
```

`refresh` executes these native full validators in the declared order and
writes no receipt unless all return zero:

1. `workflow-artifacts`
2. `assessment-artifacts`
3. `source-ai-context-version`

The resulting deterministic YAML receipt contains no timestamp or TTL. It
binds the exact full source revision and root tree OID plus SHA-256 digests of
the immutable-history root tree objects, validator fingerprint blobs, schema
fingerprint blobs, and history-index blobs. A Git tree object is
content-addressed over every descendant; calculating the recorded digest from
the fixed root object IDs does not enumerate historical blobs during routine
verification.

The validator fingerprint includes the three native validator entrypoints and
their transitive runtime inputs: `python_prerequisites.py`,
`ai_context_target_provenance.py`, `ai_context_effective_rules.py`,
`python-entrypoints.json`, and `requirements.txt`. Any change to one of these
inputs is deny-first protected and requires full validation.

The full receipt also binds each published (and legacy non-planned) release's
declared `tag` and `commit` to the tag's currently resolved commit and records
a deterministic `release_ref_digest`. Planned and validated releases with
`tag`/`commit: null` remain native-validator concerns and are still protected
by the release-root tree binding. Routine verification enumerates only the
release declarations at the bound source revision, requires their canonical
record set to exactly match the receipt, and re-resolves those tags. This
bounded release-only parse prevents a hand-edited receipt from omitting a
published tag without rewalking workflow or assessment history. A missing,
moved, omitted, or declaration-mismatched tag is `full-required`, even when the
source commit/tree and path diff are unchanged.

Commit the resulting receipt in the immediate next commit, with that commit
changing only the receipt path. The receipt records that commit's first parent
as `source.revision`; this two-commit shape avoids a self-reference and makes a
working-tree or self-selected-current-HEAD receipt unusable.

## Routine verification

For `fast` and `pr`, run:

```text
python .ai/scripts/validate-immutable-history.py verify \
  --repo . \
  --contract .ai/distribution/validation/immutable-history-validation.yaml \
  --receipt .ai/distribution/validation/immutable-history-receipt.yaml \
  --head HEAD \
  --output-format tsv
```

Routine verification is read-only and fail-closed. It requires a clean
worktree, a committed receipt, the receipt containing commit on `HEAD`'s
first-parent chain, a one-parent receipt commit that changes only the receipt,
and `source.revision` equal to that commit's first parent. It validates the
source commit/tree and receipt digest bindings through fixed Git objects, then
uses `git diff --name-status <source>..HEAD` with the contract's closed,
deny-first allowlist.

Immutable-history roots, their indexes, every validator/schema/runtime
fingerprint path, and the receipt provenance shape are protected before an
allowlist match is considered. Those changes always produce `full-required`.
The source-validator inputs `.dev/backlog/**`, `.dev/ai-context/**`, and
`.dev/AI-CONTEXT-SOURCE.yaml` are protected by the same deny-first rule.
Subsequent ordinary changes can reuse the three immutable-history checks only
when every changed path matches the explicit contract allowlist (for example,
`tools/**`, `src/**`, `tests/**`, `.dev/guides/**`, and selected agent-facing
documents). A broad `.ai/**` allowance is intentionally forbidden; only
`.ai/assets/**`, validator-independent script documentation, and script tests
are listed. An unknown path, missing-source, provenance mismatch,
malformed-receipt, or dirty-worktree produces `full-required`; it never
produces a reusable result.

Allowlisted additions and modifications may reuse the proof; deletions always
require full validation. Continuation merge commits also require full
validation because a first-parent final-state diff cannot prove that a side
branch did not delete and recreate a path. This closes rename-as-delete-plus-add
and side-branch delete/recreate gaps and avoids silently accepting a removed
workflow/assessment reference, template, or guide that a native validator
requires.

`--head` accepts `HEAD` or its exact 40-character SHA, but source verification
and refresh require it to resolve to the checked-out `HEAD`. The receipt is
read from the worktree, so accepting a different historical object would mix
unrelated bytes and is rejected as an invalid invocation.

`--contract` is accepted only when it resolves to the canonical source path
`.ai/distribution/validation/immutable-history-validation.yaml`; symlinks and
lookalike YAML files are rejected. This prevents refresh from executing a
different command list while recording a canonical-looking fingerprint.

The declared native command token `python` is executed as the already-approved
`sys.executable`, rather than resolving `PATH` a second time. This keeps the
full refresh on the same interpreter selected by the prerequisite gate.

Routine verification does not walk or hash workflow or assessment history. It
does parse the comparatively small release-declaration set to prove tag-list
completeness. The full refresh performs the native full validation; routine
verification proves that the content-addressed source objects have not been
superseded by a disallowed first-parent change.

`release` and `nightly-full` always report `full-required`. The explicit gates
`release-candidate`, `scheduled-governance`, `validator-schema-change`, and
`immutable-history-change` also require a full refresh/validation path.

## Stable command result

`verify` defaults to a one-line JSON object. Its required fields are:

- `outcome`: `routine-reusable` or `full-required`;
- `reason`: stable reason code;
- `source_revision` and `source_tree`: the bound values when a receipt can be
  parsed, otherwise `null`;
- `receipt_commit`: the containing receipt commit when resolved, otherwise
  `null`;
- `reusable_check_ids`: the three reusable check IDs only for a reusable
  outcome.

`--output-format tsv` emits exactly one tab-separated line:

```text
outcome<TAB>reason<TAB>source_revision<TAB>source_tree<TAB>receipt_commit<TAB>comma-separated-reusable-check-ids
```

Exit status is `0` only for `routine-reusable` (and a successful `refresh`),
`10` for `full-required`, and `2` for an invalid invocation, malformed
contract/configuration, or a failed refresh validator. A malformed, absent, or
stale receipt is a safe `full-required` escalation rather than an execution
pass. `refresh` never overwrites or creates a receipt after a failed validator.

`verify --mode downstream` reports the explicit source-history boundary as
`downstream-target-local`; `refresh --mode downstream` is invalid.
