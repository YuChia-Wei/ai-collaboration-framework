# Git workflow record format and behavior

Read [the shared operations contract](operations.md) for invocation, configuration,
request fields and SQLite behavior. This reference defines the existing Git
provider only. The installed CLI supports both Git and SQLite through explicit
references; remote providers remain unavailable.

## Wire operations

Every request contains `contract_version: "workflow-records/1"` and `operation`.
Unknown fields and versions are rejected. Every response contains that version,
operation, `status`, `mutation_state`, and either `result` or a stable `error`.
Success means the requested operation completed within its declared scope; it
does not mean workflow approval, lifecycle completion or provider integration.

| Operation | Additional request fields | Result |
| --- | --- | --- |
| `capabilities` | none | configured kinds, availability, operations, provider capabilities |
| `find` | optional provider_id, offset (0), limit (10, maximum 100) | refs and summaries, errors per invalid candidate, complete flag and next_offset |
| `context` | workflow_ref, optional task_limit (16, maximum 128) | revision, source_head, essential identity/status/authority, task summaries, entrypoint ref, latest checkpoint summary, missing/truncation markers |
| `read` | workflow_ref, document relative to artifact_root; optional revision, offset (0), limit (4096, maximum 32768 characters) | raw-byte digest, UTF-8 text page, total size and explicit truncation |
| `checkpoint` | workflow_ref, operation_id, expected_revision, expected_source_head, checkpoint | applied receipt and stable checkpoint_revision |
| `operation` | workflow_ref, operation_id | retained applied receipt or unknown; absence never means not_applied |
| `resume` | workflow_ref, optional task_limit and limit | common context plus entrypoint at its specified revision; refuses core drift during composition |
| `validate` | workflow_ref | same parser/core relationships, selected scope and revision; no restored aggregate gate |

`max_output_bytes` optionally bounds each response from 2048 to 65536 bytes.
Required identity/error data is not silently truncated. Oversize queries fail
with `limit_exceeded`; select smaller pages. Text summaries carry their own
truncated flag. Context never claims that referenced documents were read in full.
No token reduction percentage is promised.

The selected locator is `root/<workflow_id>/workflow.yaml`, schema `1.0`, with
the current identity, artifact_root, entrypoint, timestamps, template and branch
fields. Tasks are direct `tasks/*.json|yaml|yml` with the current minimum identity
and relationship fields. Extension fields are allowed and never rewritten. This
is not all historical layouts: root-level task files, YAML aliases, unknown
schema/lifecycle versions and non-UTF-8 documents are outside this slice. Missing
tasks are marked in context; validate/checkpoint refuse them. Lifecycle acceptance
and project-specific extra rules remain with their owner.

Core `revision` covers the raw locator, entrypoint, selected task file paths/bytes
and checkpoint journal. It deliberately excludes unrelated evidence documents;
each requested document has its own raw-byte revision. `source_head` is separate
because Git HEAD alone does not identify uncommitted record content. At most 128
tasks and 256 KiB per record/document are read. No history tree is recursively
scanned. Relative paths reject escapes, absolute/drive/UNC/ADS paths, reserved
names and symlink/reparse components. Hostile simultaneous external filesystem
mutation is not a supported writer model.

## Checkpoint and failure semantics

The checkpoint payload contains exactly `summary`, `authority`, `completed`,
`pending`, `blockers`, `evidence`, `next_action`. Text and list sizes are bounded.
These are caller-supplied observations, not authenticated approvals or proof that
listed commands ran. Source identity is recorded by the adapter.

For the Git provider, the only persistent write is an append to the operation history in
`artifact_root/.workflow-records/checkpoint.json`, using a same-directory temporary
file and atomic replace. The same file contains binding, operation ID, request
digest, previous core revision, source identity, timestamp and checkpoint content.
Old locator, plan, task and evidence bytes are unchanged; workflow/task status is
not automatically updated by checkpoint. The original project writer remains the
owner of those changes. A journal is part of the same Git store, not a fallback
provider or an independent lifecycle authority.

The adapter creates an exclusive `writer.lock`, validates revision and source,
then rechecks immediately before replace. Only cooperating writers are serialized.
A manual editor can race outside this lock; this is not a universal CAS or a
multi-file transaction. Two branches/clones have no shared lock. No commit, stage,
fetch, checkout or push is performed.

- Failure before replacement keeps the previous checkpoint.
- An I/O failure may occur after replacement; `mutation_state: unknown` requires
  querying the same operation ID before retrying.
- Same ID plus same original request returns its retained receipt, even if the
  current revision has advanced. A different request under that ID is rejected.
- Receipts preserve a checkpoint-entry digest; this is not a claim that the
  current workflow revision still equals the post-write revision.
- History is bounded by 128 operations and the 256 KiB file limit. At capacity,
  refuse new writes; do not compact history or evict idempotency information.
- An absent receipt means unknown. Recovery must not infer failure from absence.
- Operation lookup and replay require a valid current locator/task/plan snapshot.
  If that snapshot is damaged, preserve the journal and repair the selected
  records under project authority before retrying; a failed lookup is not proof
  that the checkpoint was not applied.
- A crash may retain the lock or a temporary file. No stale lock is stolen.
  Stop writers, inspect the journal/operation and the lock owner's liveness, then
  let the project owner remove only the confirmed stale lock/temp file. Preserve
  the journal. Re-read context before a new command.
- File fsync and replace do not establish power-loss durability on every storage
  device, network filesystem or RAM disk. Only local observed behavior is tested.

Stable errors include `invalid_input`, `not_found`, `malformed_record`,
`unsupported_version`, `unsupported_format`, `unsupported_capability`,
`unsafe_path`, `binding_mismatch`, `revision_conflict`, `source_conflict`,
`writer_busy`, `operation_id_conflict`, `limit_exceeded`, `provider_unavailable`,
`io_error`. Errors omit absolute paths and raw filesystem exception text. JSON
and YAML reject escaped lone surrogates, including nested values and keys, before
mutation; valid Unicode scalar values remain supported.

Remote unavailability example: an explicit remote ref yields
`status: unavailable`, `mutation_state: none`, error `provider_unavailable` and
no Git write. A future accepted remote command whose terminal result is not yet
known must expose pending/unknown through its operation query; it cannot report
completed merely because transport accepted the request.
