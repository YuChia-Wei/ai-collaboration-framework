# Unified SQLite source store and explicit Board replica delivery

`workflow-records/source-store/1` is an additive profile. SQLite owns local reads,
native acceptance, immutable source snapshots and delivery intent. Board receives
source copies, without manufactured collaboration lifecycle events. No production
database is selected or created by installation. Use an explicitly selected local
database outside the repository, with the existing `/1` configuration format.

Run `python -I -B <package>/tools/source-store.py --root <Git-repository>
--config <configuration.json> --request <request.json-or->`. Prerequisites are
Python 3.11+, PyYAML 6 and jsonschema 4.26+ with the complete declared source
package. No dependency, network schema or credential is fetched. Shared package
members are declared once; the CLI uses existing provider and command-transport
modules plus its source-store modules.

## Requests and local results

Every request has `contract_version: workflow-records/source-store/1`, `operation`
and complete `store_ref: {provider_id, store_id}`. Unknown fields fail. Optional
`max_output_bytes` bounds the whole response (2048–2097152, default 1048576).
Input is bounded at 2 MiB, strict UTF-8 JSON with safe integer numbers. No content
is clipped. If a response is lost or exceeds budget after a commit, retain the
original operation ID and query its receipt; an error is not proof of rollback.

| Operation | Required additional fields | Result |
| --- | --- | --- |
| `source-init` | `operation_id`, `schema_version: workflow-sqlite/2` | Explicit fresh schema-2 initialization |
| `source-import-git` | `operation_id`, `kind`, `workflow_id`, `source_commit`, `source_root` | Atomic per-unit archive snapshot and fixed-target intents |
| `source-list` | Optional `offset=0`, `limit=20` (1–100) | Latest native/archive/root-index units with original IDs and sync status |
| `source-read` | `snapshot_id` | Complete exact-version manifest and separate sync status |
| `source-chunk` | `snapshot_id`, `path`, `index` | Exact chunk base64, raw hash and identity |
| `source-operation` | `operation_id` | Local mutation receipt or unknown |
| `replica-bind` | `operation_id`, `binding`, `new_source_namespace: true` | Initial-only binding and baseline under one write lock |
| `replica-prepare` | `intent_id`, optional `mode: command` or `lookup` | One exact already-persisted command or original lookup |
| `replica-observe` | `operation_id`, `intent_id`, `step_index`, `channel: direct` or `lookup`, `mcp_result` | Retained transport/evaluation and monotonic sync status |

Mutations use stable local operation IDs. Exact replay returns the stored receipt
without repeating import or enqueue; changed payload under the same ID conflicts.
`source-init` uses the existing administrative receipt scope; other source
mutations have a separate retained operation scope. New source operations refuse
v1 databases with `explicit_upgrade_required`; no implicit upgrade exists.
Existing `/1` native writers retain their request meanings on both schemas.

Successful responses have `status: ok`, `local_result: accepted`, and `result`.
Local mutation result contains `state: applied`, `operation_id`, `replayed` and
the operation's result. Synchronization is independent: `not_configured`, or
`complete`/`incomplete` with per-binding intent IDs and pending/conflict/complete.
Local reads remain local even when Board is unavailable. Root-index archives are
explicitly distinguished from original workflow units, never counted as another
original workflow by their kind.

```json
{"contract_version":"workflow-records/source-store/1","operation":"source-init","store_ref":{"provider_id":"local","store_id":"local-records"},"operation_id":"initialize-source-2","schema_version":"workflow-sqlite/2"}
```

```json
{"contract_version":"workflow-records/source-store/1","operation":"replica-bind","store_ref":{"provider_id":"local","store_id":"local-records"},"operation_id":"initial-board-binding","new_source_namespace":true,"binding":{"binding_id":"board-initial","binding_revision":1,"project_ref":{"store_id":"workflow-records-private-collaboration","namespace":"personal","project_id":"ai-collaboration-framework"},"source_id":"explicitly-new-source-namespace"}}
```

```json
{"contract_version":"workflow-records/source-store/1","operation":"source-import-git","store_ref":{"provider_id":"local","store_id":"local-records"},"operation_id":"archive-one-unit","kind":"archive-workflow","workflow_id":"original-workflow-folder","source_commit":"f701105059bfc180dc5c212122e2fed939fdf664","source_root":".dev/workflows/original-workflow-folder"}
```

## Exact source preservation and atomicity

Git import reads blob objects from the explicit 40-hex commit, not checkout
bytes. One request selects one directory and publishes it atomically; no partial
version is visible. `archive-workflow` includes all descendants.
`archive-root-index` includes only direct files in the selected source directory.
Gitlinks are refused; symlink blob bytes and six-digit mode are retained as data,
never followed. Binary, empty, CRLF and files larger than the native `/1` limit
remain exact. Every file is reconstructed and size/hash-verified before local
acceptance. Whole Git commit history is outside this snapshot import.

Derived title/status come only from parseable `workflow.yaml`, `workflow.yml` or
`workflow.json` string fields, with file/selector provenance. Missing/unparseable
or oversized projected values are `unknown`; all original files and unknown
metadata remain raw source bytes. No locator, native task, authority or entrypoint
is invented. Kind and original workflow ID are prominent local read fields.

Mapping version `source-store-mapping/1` retains kind and original ID explicitly.
Remote workflow ID is `unit-` plus SHA-256 of UTF-8 `(kind + NUL + original ID)`;
both original and remote IDs are in the manifest. Archive revision is its immutable
`snapshot-<manifest-digest-hex>` ID; native revision is `native-<original-digest-hex>`
and the full original `sha256:` revision is retained in provenance. Native state,
receipt and event bytes are copied, not rewritten. Document/attachment blobs are
included separately. Old native hashes and original limits remain unchanged.

Schema-2 native create/create-task/checkpoint/write-document/revise-workflow capture runs after
the native receipt/event insert and before capacity checking in the same SQLite
transaction. State, snapshot and every configured pending intent commit together.
Omitting caller binding data cannot bypass saved bindings. Replays do not enqueue.
Remote observations/backup operations do not create native revisions or delivery.

## Initial binding, fixed requests and explicit host steps

Binding is initial-only and requires an explicitly **new** remote source namespace
at head zero. Existing binding IDs or project/source targets cannot be replaced,
reset or automatically adopted. Baseline includes every retained source snapshot
under the same write lock that saves the binding; there is no scan/writer gap.
All later snapshots retain that fixed target and mapping revision.

Each intent persists its complete begin/chunk-batch/activate commands, immutable
operation IDs and expected remote head before any host dispatch. Up to four full
49152-byte chunks fit a bounded request; smaller chunks can batch up to 32. Each
target workflow's next version waits for all preceding steps and accepted remote
activation. Rejected CAS stops delivery; expected revisions are never auto-bumped.

`source-read`/`source-list` expose `synchronization.targets[].intent_id`.
Pass one to replica-prepare. `result` gives `intent_id`, `step_index`, fixed
`binding`, original `command`, `local_command_fingerprint`, `recovery_query`,
symbolic `tool_name` and exact dispatch `request` for the selected mode.

```javascript
const prepared = prepareResponse.result;
const transport = await selectedHostTool(prepared.request); // no AI rewriting
const observeRequest = {
  contract_version: "workflow-records/source-store/1",
  operation: "replica-observe", store_ref: selectedStoreRef,
  operation_id: stableLocalObservationId,
  intent_id: prepared.intent_id, step_index: prepared.step_index,
  channel: "direct", mcp_result: transport
};
```

The profile accepts MCP CallToolResult, including the specifically observed
INVALID_ARGUMENT error annotation normalized by the command bridge. A host using
another explicit transport must first verify its transport status and scope, retain
its actual raw result, then wrap the unchanged native data as structuredContent.
No credential enters bindings, intents, observations or backups.

Receipt schema, target, source/workflow/revision, operation, command, original
expected revision and activation increment are verified. Board's owner-bound
request digest is not recomputed. Direct host correlation establishes a receipt;
lookup without an already confirmed digest remains observed-only and requires
the exact original command replay. Null, malformed, mismatched and native fault
responses remain unknown with raw observation retained. A delayed unknown cannot
erase accepted evidence. Rejected steps remain conflicts; no background retry,
fallback, pruning or identity switch exists. Inactive/retired stores refuse
dispatch preparation and new observations; restoration itself emits no network IO.

## Complete backup and bounds

Existing `/1` export/preflight/restore/deactivate/activate operate on schema 2
through `workflow-backup/2`, preserving native plus all snapshot chunks, bindings,
intents, exact commands, observation history and source receipts. Referential,
hash, native-revision, target, command and observation classification closure is
validated before restore. Restore is inactive and retains pending delivery bytes;
the original retirement/single-successor activation protocol still applies.
V1 archives retain their original format and validation; no v1 data is upgraded.

This increment supplies initial immutable bindings, SQLite-only read authority
and manual host dispatch. Dynamic target changes, read-source switching, full
local task/status editing, formal source-policy adoption and the remaining
multi-carrier/migration behavior are separate feature gaps. It does not complete
those larger delivery scopes.

Limits refuse instead of dropping data: 1000 files, 16 MiB/file, 32 MiB/unit,
240000 canonical manifest bytes, 49152 raw bytes/chunk, 64 MiB retained source raw
chunks, 128 MiB retained prepared command bytes, 65536 rows per new table,
240 MiB complete portable data and 256 MiB backup. Native `/1` byte/task/history
and administrative limits remain unchanged. Headroom covers the observed
19.4 MiB source snapshot plus base64 delivery and backup encodings; it is not a
promise of unlimited future history. Capacity is checked after new rows, while
the local transaction can roll back. No automatic cleanup is selected.

Frozen `SourceReplicaV1/schema.json` comes from reviewed Board commit
`5bf075abb64b797f039e7484aa96485f814835e2`, observed checkout SHA256
`c3cfd0ddc6f639209ae50f0edc90c1106f24e584c4eb0fafbc7f8453d8970879`.
Only CRLF→LF normalization was applied; packaged SHA256 is
`02ac880c1969e43c0094e88bd5817e2e205fb8552cbaf7b8f30ae2e45f331ab9`.
Runtime verifies the packaged hash and uses jsonschema with only local references.
These source/fixture checks do not establish production provisioning, migration,
hosted quota acceptance, physical durability, installation or source-policy cutover.
