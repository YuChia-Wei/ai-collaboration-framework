# Local file authority, SQLite synchronization and project provider controls

`workflow-records/local-group/1` owns one logical workflow per explicitly initialized
local group. The selected member owns **both** reads and accepted commands. A fresh
group uses an ordinary JSON file. SQLite is optional and has the distinct schema
`workflow-local-group-sqlite/1`; native schemas 1/2/3 cannot be attached or upgraded.
Existing Git, native workflow and source-store requests keep their meanings.
`source-store/2` still selects reads while SQLite remains its writer.

Run Python 3.11+ with PyYAML 6 and the complete package:

```powershell
python -I -B <package>/tools/local-group.py --root C:/Project --config C:/Records/group-config.json --request request.json
```

`--request -` accepts strict UTF-8 JSON on stdin. No network, code discovery,
adapter import, subprocess execution, credential loading or installation occurs.
SQLite support uses Python's standard library only when a SQLite carrier is used.

## Explicit configuration and initialization

Create persistent local parent directories explicitly; do not put durable records
on a RAM disk. The locator config is separate from mutable authority selection:

```json
{"contract_version":"workflow-records/local-group-config/1","group_ref":{"group_id":"project-a","project_id":"project-a","workflow_id":"workflow-a"},"control_directory":"C:/Records/workflow-a-control","file_path":"C:/Records/workflow-a.json"}
```

Paths must be absolute, local and distinct. Carrier paths cannot lie in the control
directory. Links, reparse points, hard-linked storage and network drives are
refused. Project root binding is exact; clones are not automatically adopted.
Only initialization or inactive restore creates storage. Missing selected storage
never causes creation, failover or another source lookup.

Every request has `contract_version`, `group_ref` and `operation`. Unknown fields
fail. Optional `max_output_bytes` is 2048–2097152, default 2097152. Requests are
bounded at 2 MiB; large results fail as a whole. After an ambiguous write/output
failure, query `group-operation` with the original operation ID.

```json
{"contract_version":"workflow-records/local-group/1","group_ref":{"group_id":"project-a","project_id":"project-a","workflow_id":"workflow-a"},"operation":"group-init","operation_id":"initialize-a"}
```

## Public operations

Mutations require `operation_id`. Except init/restore, they also require
`expected_configuration_revision`, `expected_authority_epoch`, `expected_revision`
(null before the first cut). Get these from `group-configuration`. Identical replay
returns the original result before CAS checks; a changed semantic request using
that ID conflicts. Output budget is not part of the semantic digest.

| Operation | Additional fields |
| --- | --- |
| `group-init`, `group-configuration`, `group-context`, `group-resume`, `group-sync-status` | None |
| `group-read` | `collection: documents|attachments`, `document` |
| `group-operation` | `lookup_operation_id` |
| `group-create` | `record: {metadata,tasks,entrypoint,documents,attachments}` |
| `group-create-task` | `task` with unique `task_id` |
| `group-checkpoint` | Native checkpoint shape: summary, authority, completed, pending, blockers, evidence, next_action |
| `group-write-document` | `document`, `content` |
| `group-revise-workflow` | `metadata_patch`, `task_patches` keyed by existing task ID, `documents`, `attachments` |
| `member-add` | Fresh `member_id`, `kind: file|sqlite`, absolute fresh `path` |
| `member-remove` | `member_id`, `expected_generation`; selected authority cannot be removed |
| `group-sync` | Original local `intent_id` from sync status |
| `group-resume-intent` | Original local/remote `intent_id`, `additional_attempts` (1–32) |
| `select-authority` | `member_id`, `expected_generation` |
| `group-export` | Fresh `destination`; no operation ID or CAS |
| `group-preflight` | `archive`, `archive_digest`; no operation ID or CAS |
| `group-restore` | `archive`, `archive_digest`, complete `member_paths` mapping IDs to fresh absolute paths |
| `group-deactivate` | Complete export's `snapshot_digest` |
| `group-activate` | `original_control_directory`, `retirement_seal` |

Metadata requires string `title` and `status`; nested extension fields in metadata
and tasks are retained. Documents/attachments map safe relative names to
`{"encoding":"utf-8|base64","content":"..."}`. Stored content is canonical
base64 plus raw hash and size. Empty, binary and CRLF bytes stay exact. Entrypoint
must name a document. Revisions patch provided fields; no implicit deletion exists.

For example, after init use the returned configuration revision 0, epoch 1 and null
revision to create:

```json
{"contract_version":"workflow-records/local-group/1","group_ref":{"group_id":"project-a","project_id":"project-a","workflow_id":"workflow-a"},"operation":"group-create","operation_id":"create-a","expected_configuration_revision":0,"expected_authority_epoch":1,"expected_revision":null,"record":{"metadata":{"title":"Offline work","status":"active"},"tasks":[{"task_id":"T1"}],"entrypoint":"plan.md","documents":{"plan.md":{"encoding":"utf-8","content":"Next action\r\n"}},"attachments":{"sample.bin":{"encoding":"base64","content":"AP8="}}}}
```

## Acceptance, exact synchronization and authority transfer

The file is one bounded atomic envelope, with immutable hashed event history,
full workflow bytes, provider generations, command receipts and fixed targets.
File commit flushes and atomically replaces one file in the same directory.
SQLite uses one `BEGIN IMMEDIATE` transaction and full envelope CAS. Commands
reduce content once. The accepted event retains its original request, content,
cut, parent, operation ID and targets before dispatch can occur.

Adding a member records an explicit baseline intent; it does not copy on a timer.
Use `group-sync-status`, then `group-sync` for each pending local target in the
returned order. Each apply copies the retained immutable prefix to the original
member generation after checking its exact expected parent. Lost responses can be
reconciled by replaying the original request. Replica drift fails instead of
overwriting or changing expected revisions. Removal retains earlier targets and
bytes; the member remains available to explicitly finish those older intents.

Local command acceptance and synchronization completion are distinct. A response
with `local_result: accepted` establishes that operation only; inspect retained
sync status for every target. Failed dispatches do not roll back an earlier local
command. No background or automatic remote dispatch exists.
Local apply failure returns a retained `result.state: conflict|unknown` observation
with its error code and attempt count; it is not a synchronization success. Replaying
that outer operation returns that same observation. An explicit retry uses a new
outer operation ID with the unchanged original intent/target/payload, up to 32
attempts. A new command payload or target is never generated by retry.
At the dispatch limit, status and remote lookup remain available. Explicit
`group-resume-intent` records a CAS-protected budget extension (up to 1024 total)
and authorizes dispatch of that exact original intent, including a disabled/retired
remote generation when explicitly selected. It changes no future provider binding.

Authority selection requires identical complete immutable event history and
baseline closure, acknowledged local deliveries, and current member generation.
Under the same OS lock, it copies the latest auxiliary reconciliation state and
atomically changes control authority/epoch/configuration. Requests from the old
epoch cannot write. Missing selected authority returns failure with no fallback.
Pending remote intents remain pinned across a local authority switch.

All supported reads/mutations use a stable OS lock; Windows uses kernel byte-range
locking released on process exit, not lock-file existence. Administrative changes
persist a transition before publishing member/control changes. The next operation
finishes that same transition after exact before/after checks; divergent bytes
stop recovery. No guarantee covers arbitrary direct file/SQL edits or multiple
copies of active storage. Physical power-loss behavior has not been established.

## Project-owned experimental provider controls

Use `contract_version: workflow-records/provider-control/1` with the same CLI,
identity, operation IDs and local CAS. Registrations and provider configuration
live only in the selected carrier; local member/authority control lives in
`control.json`. Provider register/update/enable/disable also require
`expected_provider_configuration_revision`, returned by `group-configuration`.
That separate revision advances only for those provider configuration operations.

| Operation | Additional fields |
| --- | --- |
| `provider-list` | None; read |
| `provider-inspect` | `provider_id`; read |
| `provider-register` | `registration` |
| `provider-update` | `registration`, `expected_generation` |
| `provider-enable`, `provider-disable` | `provider_id`, `expected_generation` |
| `provider-prepare` | Original remote `intent_id`, `mode: command|lookup` |
| `provider-observe` | `handoff_id`, unchanged `observation` envelope |

Registration shape:

```json
{"provider_id":"my-provider","implementation_ref":"adapters/my-provider.py","implementation_version":"1.0.0","protocol_version":"workflow-records/provider-handoff/1","project_id":"project-a","scope":"personal","capabilities":["replicate"],"settings_non_secret":true,"settings":{"endpoint_label":"project-owned"}}
```

Alternatively use `settings_file: "settings/provider.json"` instead of `settings`.
Registration reads that explicit project-owned JSON once and retains its canonical
snapshot and digest. Missing/malformed data fails before acceptance. Later file
edits never change old generations or their handoffs. Settings must be non-secret;
credentials remain with the downstream host. References cannot select managed
`.ai`, `.agents`, `.claude` or `.codex` resources. Implementation references are
never loaded or run. Backend-specific settings semantics remain project-owned.

Register/update creates an immutable disabled generation. Explicit enable selects
that current generation for future command targets. Two IDs remain distinct.
Update never replaces older generations or retargets their pending operations.
Disable/retirement prevents command preparation for that generation; original
lookup remains available. No capability declaration selects remote command authority.

Prepare returns the original pinned `workflow-records/provider-handoff/1` command,
request digest, generation, registration/settings snapshot, complete project/workflow
scope, exact state bytes and expected provider revision. The downstream host chooses
and executes its own code. Acceptance freezes the predecessor intent identity.
First prepare resolves its expected provider revision from that predecessor's
accepted observation, or null for a fresh generation, then persists the exact
command/digest. Subsequent prepare and lookup retain that original command.
Provider revisions are opaque and distinct from local logical cuts; earlier
intents must be accepted first. Command preparation has an initial bound of 32
attempts per intent. Lookup does not consume that dispatch budget.

The host supplies an observation with exactly the command's `contract_version`,
`group_ref`, `provider_id`, `generation`, `operation_id`, `request_digest`,
`logical_revision`, plus
`outcome: accepted|rejected|conflict|unknown` and `provider_revision` (nonempty opaque
text for an accepted result, text/null otherwise). The logical revision echoes the
delivered cut separately. Unknown results require the original lookup
or exact command; never change provider or identity. Accepted evidence is monotonic.
Initially 64 observations are retained per intent; explicit resume extends this
budget by twice its added dispatch budget, with a hard bound of 4096.

An observation is a **host-correlated assertion**, not identity/backend attestation.
Registration/configuration fixtures do not verify downstream code, credentials,
networks, availability, remote storage or actor behavior. Workflow Board keeps its
existing separately supplied experimental adapter and DTOs; this contract neither
relabels it nor launches it.

## Complete recovery and bounds

`workflow-local-group-backup/1` exports control and every retained member envelope,
all receipts, generations/settings snapshots, fixed targets, payloads, observations
and pending intent state under the group lock. Preflight checks hashes, identities,
event closure and member prefixes. Restore selects fresh paths for all members,
preserves pending work, creates a new inactive instance and sends no external IO.
Complete export requires every retained carrier to be readable, including removed
members whose original intents/history remain retained. An unavailable member
prevents complete export; it is never silently omitted. Restore may select a new
project root; activation verifies the original control against its original root
binding and the restored group against its explicitly selected new root.

Export, restore, retire the original exact snapshot, then activate the restored
instance using the original retirement seal. Activation claims the original's
single-successor slot before enabling the restore. Interruption allows only that
same instance to resume. Another restore cannot activate; unavailable original
control fails closed. Never copy files and treat both copies as active stores.

Bounds refuse instead of pruning: 2 MiB request/response, 32 MiB complete object,
1 MiB raw document, 128 tasks/documents/attachments each, 256 immutable events,
8 local members, 16 providers with 32 generations each and 4096 auxiliary/control
records. Acceptance reserves complete-group backup headroom. The history stores
full immutable state; it is deliberately bounded rather than a compaction service.
