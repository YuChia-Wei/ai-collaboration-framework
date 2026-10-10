# Workflow records contract 1 and Git slice

This optional source capability provides a common application entry and a Git
working-directory adapter. `tools/workflow-records.py` is its executable checkout
entry. It is not in the installed skill catalog or release manifest. The
orchestrator remains an instruction package that works without a store.

The contract belongs to the framework; a future board adapter maps it to the
board's independently versioned API. Workflow runs/tasks are execution records,
not automatic GitHub/Azure DevOps work-item creation or state transitions.

## Responsibilities

- `contracts.py`: provider-neutral reference, version, port and errors.
- `service.py`: explicit store selection, bounded requests/results, capabilities
  and the actual resume consumer.
- `git_store.py`: current record parser, document reads, content revision and
  conditional single-file checkpoint replacement.
- CLI: input/output transport only. No network, Git mutation or implicit config.

Python 3.11+ and PyYAML 6 are required. The source test environment pins its
dependencies separately. No database, distribution engine or retired workflow-v2
code is imported. This slice intentionally avoids a DI container or universal
cross-product domain model.

## Explicit configuration and binding

`--root` selects the project Git working directory. `--config` optionally selects
a UTF-8 JSON file; omission selects the following checkout default. Neither
operation writes configuration or changes a project's policy.

```json
{
  "contract_version": "workflow-records/1",
  "default_provider": "git",
  "stores": {
    "git": {"kind": "git", "store_id": "project-workflows", "root": ".dev/workflows"}
  }
}
```

All record operations require the full reference returned by discovery:

```json
{"provider_id":"git","store_id":"project-workflows","workflow_id":"2026-10-10-example"}
```

The store identity is a stable caller-owned label, not an absolute clone path.
Root mappings are caller-owned and must remain stable for an existing binding.
Overlapping Git locator roots in one config are refused. A first checkpoint
persists its full reference and locator root and refuses reinterpretation under
another binding. Legacy records need no rewrite: discovery assigns an explicit
Git reference; all subsequent calls carry it. There is no write operation that
migrates or rebinds a workflow.

The default selects only unqualified discovery and the future create operation;
it is never consulted for an existing explicit reference. Changing it does not
move records. The assessment consumer explicitly uses the `git` provider for its
legacy workflow IDs regardless of the default. A missing provider, changed store
identity or unavailable remote never causes another store to be tried.

Local/remote descriptors currently contain only `kind` and `store_id`. Credentials,
URLs and database engine settings are deliberately not accepted before those
adapters exist. Capability inspection reports them as unavailable.

## Common ports and minimum provider contract

| Port | Required semantics | This Git slice |
| --- | --- | --- |
| Query | discover, bounded context, specified document revision, operation result | implemented as `find`, `context`, `read`, `operation` |
| Command | stable operation ID, explicit binding, conditional input revision, observable mutation result | additive `checkpoint` only |
| Portability | enumerate/export documents at explicit revisions; preserve identity, versions and unknown data; validate import before authority transfer | revision-bound `read` implemented; complete export/import/create/migration unsupported |
| Consumer | use the same query/parser rather than a second filesystem interpretation | actual `resume`, `validate` and opt-in assessment workflow references |

No provider may report success for a missing or malformed required record. No
automatic write failover is part of the contract. Future providers must expose
their capabilities before execution and reject unsupported operations explicitly.

## Three-mode capability matrix

Git is implemented locally; local and remote columns are design requirements,
not passed provider acceptance. The mandatory baseline for a full provider is
query/context/document revisions, conditional checkpoint, explicit binding and
operation outcome. Create and portability require separately advertised support.

| Concern | Git working directory | Local database (future) | Remote adapter (future) |
| --- | --- | --- | --- |
| Writable authority | one configured working directory/ref; cooperating tool writers | one selected database/ref | one selected service tenant/store/ref |
| Read revision | core file-content digest; document byte digest | transactional revision/snapshot | documented server revision/ETag |
| Write concurrency | lock + content check + single-file replace | database transaction and revision condition | server-side conditional command |
| Multiple clones/branches | independent copies; reconciliation is explicit | no promise without selected engine/deployment | only guarantees advertised by server contract |
| Unknown outcome | query retained operation journal; absent means unknown | query committed operation/result row | query operation; pending if not terminal |
| Unavailable | no alternate store writes | unavailable; no Git fallback | unavailable/pending; no Git/local fallback |
| Portability | original files retained; document reads available | future export/import contract required | future export/import adapter mapping required |
| Current execution | checkout CLI, local tests | not implemented | not implemented; board version independent |

The same full-provider scenario maps as follows: create resolves the selected
default once and returns a complete ref; handoff reads bounded context; change
supplies that ref, expected revision and operation ID; document read specifies
its returned revision; outcome lookup uses the same ref and operation ID. For
Git today, creation stays with the existing project writer and the first selected
tool action is discovery. Calling `create` here returns `unsupported_capability`.
This is an explicit first-slice limit, not a stub returning a fabricated record.

## Wire operations

Every request contains `contract_version: "workflow-records/1"` and `operation`.
Unknown fields and versions are rejected. Every response contains that version,
operation, `status`, `mutation_state`, and either `result` or a stable `error`.
Success means the requested operation completed within its declared scope; it
does not mean workflow approval, lifecycle completion or provider integration.

| Operation | Additional request fields | Result |
| --- | --- | --- |
| `capabilities` | none | configured kinds, availability, operations, unsupported create/portability |
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

The only persistent write is an append to the operation history in
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

## Compatibility and next slices

Non-users retain existing paths and behavior. The assessment validator's optional
`--workflow-store-config` selects stricter common-format validation for its
workflow references; omission retains existence-only behavior. Legacy commit,
handoff, terminal and artifact gates are not silently redirected or restored.

Future slices: optional package distribution/runtime declaration; create through
the common entry; additional historical task layouts; multi-document updates;
local provider/backup; board adapter; full export/import and explicit authority
transfer. Migration requires an owner-selected frozen source, complete export,
verified import, retirement of the old writable authority and explicit activation
of the new binding with recoverable interruption states. No current command
performs those steps. Git/local delivery remains valid without board integration.
