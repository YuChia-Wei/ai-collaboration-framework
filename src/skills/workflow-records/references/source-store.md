# Unified SQLite source store and explicit Board replica delivery

`workflow-records/source-store/1` is an additive profile. SQLite owns local reads,
native acceptance, immutable source snapshots and delivery intent. Board receives
source copies, without manufactured collaboration lifecycle events. No production
database is selected or created by installation. Use an explicitly selected local
database outside the repository, with the existing `/1` configuration format.

Run `python -I -B <package>/tools/source-store.py --root <Git-repository>
--config <configuration.json> --request <request.json-or->`. Prerequisites are
Python 3.11+ and PyYAML 6 with the complete declared core package.
`jsonschema` 4.26+ is loaded only for selected replica DTO/proof validation or
backup data containing replicas; ordinary local-only operation needs no Board
module, Board V2 schema or jsonschema runtime. No dependency, network schema or credential is fetched. Shared package members are declared once; the CLI uses only its local provider
and source-store modules. The inert SourceReplica schema preserves existing
replica data; it does not activate an online integration.

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
| `binding-status` | `binding_id` | Current target digest, global snapshot sequence and retained disable receipt |
| `binding-disable` | `operation_id`, `binding_id`, `expected_binding_digest`, `expected_snapshot_sequence` | Atomic irreversible cutoff and immutable original-request receipt |
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

The `/1` profile retains initial immutable bindings, explicit SQLite reads and
manual host dispatch. Workflow-scoped configuration and selected reads use the
separate `/2` profile below. Formal source-policy adoption, migration and real
cross-client/hosted acceptance remain separate from controlled fixture evidence.

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

## Workflow-scoped configuration and selected reads: `/2`

`workflow-records/source-store/2` requires an explicitly initialized fresh
`workflow-sqlite/3` database. Its default read source is SQLite and its only
command authority is SQLite. It uses the same explicit root, store configuration,
CLI, strict request fields and whole-object limits. No operation upgrades an
existing database. Schema-1/2 stores keep their existing capabilities; `/2`
operations return `explicit_upgrade_required` there. Production provisioning,
configuration changes and migration are never selected by installation.

Each logical workflow has its own configuration revision, initially zero, and
exactly one read source. Configuring one workflow cannot change another workflow.
The native workflow must already exist. Archive units retain `/1` physical reads;
they do not acquire a native workflow identity or workflow configuration.

| Operation | Required additional fields |
| --- | --- |
| `source-init` | `operation_id`, `schema_version: workflow-sqlite/3` |
| `source-configuration` | `workflow_id` |
| `source-operation` | `operation_id` |
| `replica-add` | `operation_id`, `workflow_id`, `expected_configuration_revision`, `binding`, `new_source_namespace: true` |
| `replica-update` | Same as add plus `expected_binding_generation` |
| `replica-remove` | `operation_id`, `workflow_id`, `expected_configuration_revision`, `binding_id`, `expected_binding_generation` |
| `select-read-source` | `operation_id`, `workflow_id`, `expected_configuration_revision`, `read_source`; `proof_id` required for replica selection |
| `read-prepare` | `operation_id`, `workflow_id`, `expected_configuration_revision`; optional `binding_id` prepares a candidate selection proof |
| `read-accept` | `operation_id`, `proof_id`, `step_index`, `mcp_result` |
| `read-result` | `proof_id` |
| `read-chunk` | `proof_id`, `path`, `index` |

Every request also carries `contract_version`, `operation` and the complete
`store_ref`. `max_output_bytes` is optional. Configuration mutations replay an
already accepted identical operation before checking the expected configuration
revision; changed content under that ID conflicts. CAS, configuration history,
baseline intents and receipt share one `BEGIN IMMEDIATE` transaction. A stale CAS
leaves no new binding, baseline, receipt or configuration revision.

```json
{"contract_version":"workflow-records/source-store/2","operation":"source-init","store_ref":{"provider_id":"local","store_id":"records"},"operation_id":"initialize-three","schema_version":"workflow-sqlite/3"}
```

```json
{"contract_version":"workflow-records/source-store/2","operation":"replica-add","store_ref":{"provider_id":"local","store_id":"records"},"operation_id":"add-selected-carrier","workflow_id":"example","expected_configuration_revision":0,"new_source_namespace":true,"binding":{"binding_id":"board","project_ref":{"store_id":"board","namespace":"personal","project_id":"example-project"},"source_id":"explicit-fresh-namespace"}}
```

The `binding` input has exactly `binding_id`, `project_ref` and `source_id`.
The accepted configuration returns its immutable `generation_id` and full
`target`, including the generated physical binding identity and revision. Update
requires a fresh namespace; existing/retired targets cannot be adopted or reset.
Baseline includes every retained native snapshot of this workflow. Later native
mutations capture exactly the active generations under the same SQLite lock.
Updating/removing a carrier changes future membership only. Original pending
intents, payloads, target IDs, expected remote heads and receipts remain intact
and retain their original `/1` preparation/observation route. A selected read
binding must first be explicitly switched away before removal/replacement.

### Complete read proof and explicit switching

For the default SQLite source, `read-prepare` immediately returns a complete
persisted read token. `read-result` returns its pinned native state, manifest and
revision mapping; `read-chunk` returns its exact source bytes. No remote schema or
transport is required for an unbound offline workflow.

For an explicitly chosen experimental replica, prepare a candidate proof:

```json
{"contract_version":"workflow-records/source-store/2","operation":"read-prepare","store_ref":{"provider_id":"local","store_id":"records"},"operation_id":"prove-current-cut","workflow_id":"example","expected_configuration_revision":1,"binding_id":"board"}
```

Preparation persists the workflow/configuration/generation/source/version/hash
token and returns one exact SourceReplica/1 query. The explicit host dispatches
that unchanged request and supplies its raw MCP result to `read-accept`, retaining
the original operation ID for response-loss replay. Accept returns the next exact
query until `read_state: complete`. No network call runs inside a local transaction.
The plan covers the exact-version `replica.read` header, every 50-file manifest
page and every file chunk. Project/source/workflow/version/hash, provider revision,
page totals/order and all raw chunk/file bytes must agree with the immutable
local cut. Empty files have no chunks. Conflicting text/structured MCP results,
missing pages, altered bytes and wrong scope fail without advancing proof state.
This proof correlates host-returned data; it does not attest remote actor identity.

```json
{"contract_version":"workflow-records/source-store/2","operation":"select-read-source","store_ref":{"provider_id":"local","store_id":"records"},"operation_id":"select-proven-replica","workflow_id":"example","expected_configuration_revision":1,"read_source":{"kind":"replica","binding_id":"board","generation_id":"generation-<returned-digest>"},"proof_id":"read-<returned-digest>"}
```

Selection checks the completed candidate proof against the workflow's **current**
local cut under the CAS transaction. A native write or configuration change after
proof preparation requires a new proof; an intentionally older cut is refused.
Selecting `read_source: {"kind":"sqlite"}` needs no remote proof and remains an
explicit configuration mutation. Neither operation changes command authority.

After selection, omit `binding_id` from `read-prepare` to read the saved unique
source. A replica read pins the latest immutable version established by confirmed
activation or a complete remote read proof, then obtains and verifies actual
bytes through that same carrier. Read proof never manufactures command receipts
or marks pending synchronization complete. An absent proven version, unavailable
transport, incomplete data or wrong scope returns an error without falling back
to SQLite. Once complete, `read-result` reports `freshness: current` or
`behind` against the current local authority cut. A normal native write does not
invalidate the pinned immutable read; a configuration change invalidates the
token and returns `configuration_conflict`. Tokens and raw read evidence survive
backup/restore, but inactive stores cannot prepare new reads or accept transport.

`configuration_revision` orders only this workflow's carrier/read selection.
`logical_revision` is the immutable `native-<digest>` source revision.
`native_state_revision` preserves the original native `sha256:<digest>` revision.
`provider_revision` is the replica's independent activation counter, or null for
SQLite. Digests and provider counters never share an ordering relation; freshness
uses retained snapshot identity and local sequence, not numeric comparison.

Schema-3 export uses `workflow-backup/3`. Validation preserves native history,
complete configuration history, generations, exact historical target membership,
pending commands, observations, read tokens and proof bytes. Restore is inactive
and retains the existing sole-successor activation protocol. Backup-1/2 formats
and validators remain compatible; no restore converts their schema.

## Explicitly stop capture for one schema-2 binding

Read `binding-status`, then explicitly submit `binding-disable` with its exact
`binding_digest` as `expected_binding_digest` and `snapshot_sequence` as
`expected_snapshot_sequence`. The write lock compares both values before recording
an immutable control in `source_operations`. Its receipt retains the original
request, target digest and cutoff sequence. Exact operation replay occurs before
CAS and inactive-store checks; a changed request under the same operation ID
conflicts. A different operation cannot disable an already disabled binding.

Only this explicit operation upgrades schema 2 to `workflow-sqlite/2.1`, atomically
with the disable receipt; reads and ordinary workflow writes do not upgrade it.
This marker makes older runtimes refuse to open the database. Schema 3 keeps its
separate explicit configuration operations; this operation does not migrate it.

Local reads/writes remain SQLite operations. Later snapshots do not enqueue an
intent for the disabled binding; other active bindings retain capture. No binding,
intent, prepared command, observation or historical bytes are deleted or rewritten.
Command preparation for the disabled binding fails with `binding_disabled`.
`mode: lookup` and `replica-observe` retain historical reconciliation only; lookup
can inspect a later pending intent without dispatching its pending predecessor.
The returned `command` in lookup mode is retained evidence; only `request` is the
lookup request. Disabled bindings cannot be implicitly reenabled or replaced.

Complete backup uses `workflow-backup/2.1`; preflight validates the control's
original request/digest, binding identity, store reference and exact cutoff, then
requires every snapshot/binding intent through that cut and none after it. The
format preserves existing tables and historical commands; restore remains
inactive. Existing schema-2 backups stay readable. Old runtimes refuse the new
backup format. Installation and binding status reads perform no control write,
provider dispatch, data migration or automatic disable.
