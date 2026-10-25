# Workflow record operations

## Runtime and invocation

Use Python 3.11 or later in the 3.x series, PyYAML 6.x, Git, and Python's
`sqlite3` module for local SQLite stores. Select a Python environment that
already provides these prerequisites. `-I` excludes user-site packages and
ambient Python paths; install or select prerequisites only with applicable
permission. This package does not download runtimes or start a server.

The installed CLI is relative to the selected project root:

```text
python -I -B <project>/.ai/core/skills/workflow-records/tools/workflow-records.py --root <project> --request <request.json> --config <configuration.json>
```

`--request` and `--config` read UTF-8 JSON files. Configuration is optional and
never saved implicitly. The CLI returns one bounded JSON response and a nonzero
exit status for an unsuccessful result. Inspect `status`, `mutation_state` and
diagnostics instead of treating process exit alone as durable success.

A bounded initial request is:

```json
{"contract_version":"workflow-records/1","operation":"capabilities"}
```

Use the returned capabilities and the selected operation's runtime validation
for exact accepted fields. Unknown fields or versions fail closed. A missing
provider does not authorize fallback to another provider.

## Selection and identity

A workflow reference contains `provider_id`, `store_id` and `workflow_id`.
A store reference contains `provider_id` and `store_id`. Retain each complete
reference; a display name or current default is not a stable substitute.
Previously selected Git records keep their explicit references when the default
provider for new records changes.

The configuration contract uses `contract_version`, `default_provider` and
named `stores`. A Git descriptor supplies `kind: git`, `store_id` and a selected
relative `root`. A local descriptor supplies `kind: local`, `store_id`,
`repository_id`, an absolute local `database` path, and optionally
`busy_timeout_ms` between 0 and 10000 (default 1000). Use an explicitly selected
local path. Initialization, activation and restoration are separate operations;
configuration presence alone does not prove that a database is ready or active.

Package metadata has `configuration: null` because installation does not
provision project configuration, records or templates. This does not mean the
runtime has no configuration or persistent data. The selected project owns its
workflow records and database lifecycle.

## Public operations

| Operation | Selected purpose |
| --- | --- |
| `capabilities` | Report configured providers and their available operations. |
| `find` | Discover bounded workflow summaries in the selected provider. |
| `context` | Read bounded workflow and task context. |
| `read` | Read a selected document or bounded range. |
| `checkpoint` | Persist an authorized checkpoint with the required concurrency inputs. |
| `resume` | Read bounded continuation context without claiming work completion. |
| `validate` | Assess the selected record's supported structural checks. |
| `operation` | Read an operation receipt using exactly one workflow or store reference. |
| `init` | Initialize the explicitly selected local store. |
| `create` | Create a workflow in the explicitly selected local store. |
| `write-document` | Write a selected local workflow document. |
| `export` | Export the selected local store to an authorized destination. |
| `preflight` | Check the selected local export and recovery inputs. |
| `restore` | Restore from the explicitly selected local recovery inputs. |
| `deactivate` | Deactivate the selected local store under its runtime contract. |
| `activate` | Activate the selected local store under its runtime contract. |

`init`, `export`, `preflight`, `restore`, `deactivate` and `activate` use a complete
store reference. `create` and `write-document` are also local-only. Follow the
runtime's exact request validation and returned diagnostics; this table does
not add accepted fields or guarantees. Remote storage is unavailable unless a
future implemented provider is explicitly selected. No operation automatically
commits, pushes, migrates Git history or updates an external work tracker.

Preserve operation identifiers, revisions and receipts across interruption or
an uncertain response. A stale revision requires reconciliation with the actual
record. Recovery evidence and an export file are not proof that a restore was
performed or that another machine can use the restored store.

## Package and reader compatibility

This optional package is `workflow-records@0.1.0`; its runtime contract remains
`workflow-records/1`. Distribution release versions have a separate lifecycle.
Metadata 5 declares the CLI's supporting modules in `resources.tools[].support_files`
so code is included as executable support, not represented as documentation.
Readers that only support metadata 1 through 4 reject this package. Select an
engine that supports metadata 5; do not downgrade the declaration or remove
module checks to force an older reader to accept it.

All bundled product inputs originate in `src/skills/workflow-records/` and its
explicit package members. Installed execution resolves its local modules inside
the installed package; it must not import the framework source checkout or root
`tools/` compatibility wrapper. The wrapper remains source-development tooling
and is not a downstream runtime dependency. Installation does not select this
skill through existing presets or change the source project's own installation.

## Exact requests

The additive [source-store profile](source-store.md) provides explicit schema-2
source snapshots and persisted replica delivery while preserving the requests below.

Board V2 uses the additive [board-query profile](board-query.md) and separate
`tools/board-query.py` CLI for `board-query-prepare` / `board-query-accept`.
The `workflow-records/1` requests below keep their existing provider semantics.
Authorized Board writes use the separate [board-command profile](board-command.md)
and `tools/board-command.py`; query preparation does not grant write authority.

Every request includes `contract_version: "workflow-records/1"` and `operation`.
All accept optional `max_output_bytes` from 2048 to 65536. Unknown fields fail.
References and operation IDs use nonempty bounded ASCII identifiers; preserve
returned IDs and digests exactly rather than deriving them from display titles.

| Operation | Additional fields (optional fields in parentheses) |
| --- | --- |
| `capabilities` | none |
| `find` | (`provider_id`, `offset=0`, `limit=10`, maximum 100) |
| `context` | `workflow_ref`, (`task_limit=16`, maximum 128) |
| `read` | `workflow_ref`, `document`, (`revision`, `offset=0`, `limit=4096`, maximum 32768 characters) |
| `checkpoint` | `workflow_ref`, `operation_id`, `expected_revision`, `expected_source_head`, `checkpoint` |
| `resume` | `workflow_ref`, (`task_limit=16`, `limit=4096`) |
| `validate` | `workflow_ref` |
| `operation` | exactly one of `workflow_ref` or `store_ref`, plus `operation_id` |
| `init` | `store_ref`, `operation_id` |
| `create` | `workflow_ref`, `operation_id`, `record` |
| `create-task` | `workflow_ref`, `operation_id`, `expected_revision`, `expected_source_head`, `task` |
| `write-document` | `workflow_ref`, `operation_id`, `expected_revision`, `expected_source_head`, `document`, `content` |
| `export` | `store_ref`, absolute local `destination` (must not exist) |
| `preflight` | `store_ref`, absolute local `archive`, `archive_digest` |
| `restore` | `store_ref`, `operation_id`, absolute local `archive`, `archive_digest` |
| `deactivate` | `store_ref`, `operation_id`, `snapshot_digest` |
| `activate` | `store_ref`, `operation_id`, absolute local `retired_database`, `retirement_seal` |

`read` addresses text documents. Binary attachments are retained and checked in
complete exports; this version has no separate binary-read or attachment-update
operation. `write-document` replaces one existing text document. Existing task/metadata
editing, Git-to-SQLite migration and multi-document commands are not advertised.
The Git format and existing checkpoint behavior are in [git-format.md](git-format.md).

`create-task` is available only on SQLite. It appends one task to the selected
workflow using the same task contract as `create`: a path-safe `task_id` and
nonempty `status` and `title` strings, within the state byte limit. Unknown task extensions, including
optional `owner_skill`, are preserved. The task ID must be unique within that
workflow (`already_exists` otherwise); the 128-task limit remains in force.
Copy `revision` and `source_head` from `context` into the required expected fields.
Missing or unknown envelope fields are rejected. The operation preserves all
existing tasks, metadata, documents, attachments and checkpoint history, and
commits the new revision and receipt in one transaction. Replay precedes current
revision/source and active-store checks. No local-backlog, local item or tracker
write is required. Task transitions and completion policy are outside this operation.

## SQLite setup and operation chain

Select an existing persistent local parent outside the project working directory
and its Git common directory. UNC paths, mapped network drives, symlinks and
reparse components are refused. Do not use a RAM disk for durable records. For
example, select the following caller-owned configuration after choosing a real
path and stable logical repository identity:

```json
{
  "contract_version": "workflow-records/1",
  "default_provider": "local",
  "stores": {
    "git": {"kind":"git","store_id":"project-workflows","root":".dev/workflows"},
    "local": {"kind":"local","store_id":"team-workflows","repository_id":"my-project","database":"C:/WorkflowData/my-project.sqlite","busy_timeout_ms":1000}
  }
}
```

`init` explicitly creates the absent database. Reads never create one. Both
providers require an existing Git repository for source identity. SQLite records
the resolved Git common-directory binding as well as `repository_id`: explicitly
configured linked worktrees may share a store; an independent clone cannot use
that same store just by repeating the logical ID. Existing Git references still
select Git when `default_provider` changes. `create` always requires the complete
chosen reference, so a retry cannot drift to a different default.

```json
{"contract_version":"workflow-records/1","operation":"init","store_ref":{"provider_id":"local","store_id":"team-workflows"},"operation_id":"initialize-1"}
```

```json
{
  "contract_version":"workflow-records/1","operation":"create",
  "workflow_ref":{"provider_id":"local","store_id":"team-workflows","workflow_id":"example"},
  "operation_id":"create-example",
  "record":{
    "metadata":{"title":"Example","status":"in_progress","owner_skill":"software-development-orchestrator","authority":"caller-selected task"},
    "tasks":[{"task_id":"T1","title":"Implement the selected change","status":"pending"}],
    "entrypoint":"plan.md","documents":{"plan.md":"# Example\n"},
    "attachments":{"evidence.bin":"AAEC"}
  }
}
```

Metadata and task extension fields are preserved in every retained revision and
export, including fields not projected into bounded context. Names must be safe
relative paths, unique without case distinctions across documents/attachments;
`.workflow-records/` is reserved. Text is UTF-8; attachment content is strict base64.

Call `context` with the returned reference. Copy its `revision` and `source_head`
into a new checkpoint request. The checkpoint has exactly `summary`, `authority`,
`completed`, `pending`, `blockers`, `evidence`, `next_action`; completed/pending/
blockers/evidence are bounded string lists, other fields are bounded strings.
These observations do not grant approval or prove lifecycle completion.

Retain the entire original mutation request and its `operation_id`. Same ID and
same request returns the original receipt with `replayed: true`, even after
revision advancement or inactive restore. A changed request under that ID yields
`operation_id_conflict`; a new operation with stale inputs yields
`revision_conflict` or `source_conflict`. Lookup absence means `unknown`, never
proof that the write failed. `max_output_bytes` is excluded from replay identity.

SQLite uses short `BEGIN IMMEDIATE` write transactions, rollback DELETE journal
and synchronous FULL. State, revision, blobs, event and receipt commit together.
The bounded lock timeout yields `writer_busy` without another-store fallback.
`resume` reads context and the selected entrypoint in one read transaction.
Filesystem/device power-loss guarantees are not established by process tests.

## Complete backup and controlled authority transfer

1. Export to a new local file. The result returns `archive_digest` for the exact
   archive bytes and `snapshot_digest` for the complete logical snapshot. Keep
   both with the artifact. Export includes every retained workflow, revision,
   document/attachment blob, event and operation receipt in one read transaction.
2. Run `preflight` against that exact archive and digest. It validates version,
   identity, hashes, relationships, unique IDs, limits and the complete retained
   history. It writes nothing and does not activate a store.
3. Point the same logical store configuration at a fresh absent database, then
   `restore` with a new administrative operation ID. Restore preflights first,
   refuses replacement, preserves logical IDs/history/receipts and creates a new
   physical instance in `inactive` state. Query, old document read and safe replay
   are available; new workflow mutations are refused.
4. With cooperating writers quiescent, `deactivate` the original using the export's
   `snapshot_digest`. Any intervening committed change makes the export stale and
   retirement fails. Successful retirement is permanent and yields a
   `retirement_seal`; preserve the original database.
5. `activate` the restored target with the original `retired_database` and seal.
   The original durably records one successor instance before the target becomes
   writable. A second restored copy cannot claim the same original authority.

These two databases cannot commit atomically. An interruption between activation
phases leaves the original retired and the target inactive; `activation_pending`
with `mutation_state: unknown` means preserve both, query the original operation
ID and retry the same target/request. Never initialize a replacement, erase the
claim or activate another restored copy. If the original database is missing,
activation is `unsupported_capability`; disaster promotion requires a separately
selected recovery procedure. A restored archive can still be inspected offline.

The API assumes cooperating writers. Raw database copies/edits can bypass its
authority model. No automatic backup schedule, cross-machine synchronization,
disaster promotion, remote service or Dolt provider is supplied.

Limits are fail-closed without eviction: 256 workflows per store, 256 retained
revisions per workflow, 128 tasks, 128 documents and 128 attachments per initial
record, 256 KiB per blob/state/request, 32 MiB aggregate blob bytes, 4096 operation
workflow operation receipts, 128 administrative receipts, and 64 MiB backup bytes.
Normal portable data is capped at 60 MiB in the actual JSON/base64 representation;
each administrative row is capped at 2 KiB. Writes check this before commit.
Restore and retirement require two free administrative slots; activation checks
one before reserving the successor. At the finite transfer-history limit, the
next transfer is refused while the original stays active. History is never
evicted to make space; this version does not provide unlimited generations.
Errors contain stable codes and omit host paths.
Successful export/restore is scoped to the selected bytes and bindings; it does
not prove availability of another machine, disaster readiness or publication.
