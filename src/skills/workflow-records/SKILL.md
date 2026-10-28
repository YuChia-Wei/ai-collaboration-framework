---
name: workflow-records
description: Read and maintain selected Git or SQLite workflow records and local source snapshots, preserving identity, authorization and recovery evidence without requiring an online adapter.
---

# Workflow Records

For readable `workflow.yaml`, task YAML and byte-preserved document/attachment
exports of one current native/group record, use [file export](references/file-export.md).
Explicit project-owned schema/template selection validates without inserting
defaults. File export/preflight do not replace complete recovery archives or
provide a historical import/restore adapter.

For an explicitly initialized offline Local file authority, optional same-workflow
SQLite carrier, and project-owned provider controls, use the additive
[local-group contract](references/local-group.md) and [CLI](tools/local-group.py).
It selects one carrier for both reads and writes and preserves fixed delivery
targets. Its SQLite schema and backup format are distinct from native schemas
1/2/3. Remote descriptors are disabled by default; host-mediated prepare/observe
never launches code or proves backend acceptance. Do not reinterpret the older
source-store/2 read selector as command-authority transfer.

For explicitly selected unified SQLite source authority and Board source-copy
delivery, use the additive [source-store profile](references/source-store.md) and
[CLI](tools/source-store.py). Fresh schema 2 is an explicit selection; never upgrade
a v1 database implicitly. Preserve archive kinds/raw bytes, original identities,
fixed targets and exact pending commands. Local acceptance and replica completion
are separate, and each host dispatch remains explicit.

The versioned `/2` source-store profile initializes fresh schema 3 with SQLite
as the sole command authority and default read source. It adds workflow-scoped
configuration revisions, immutable carrier generations and explicitly selected
read proofs. Existing schema-1/2 stores are never upgraded by these operations.
Read-source selection changes no writer authority. Preserve original accepted
delivery targets when a future configuration adds, removes or replaces a carrier.

Use the [operation contract](references/operations.md) and the bundled
[CLI](tools/workflow-records.py) for an explicitly selected project and store.
Board V2 execution bridges are supplied only by the separately selected
`workflow-board-experimental` package, which is not included in ordinary presets.
Installation does not activate that package; its CLI requires an explicit
`--activate` selection on each invocation. Core never discovers or loads it.
Core source-store configuration, prepare/observe and exact read proofs only
process local data; the host dispatches any external operation explicitly.
The inert SourceReplica contract stays here to preserve strict validation of
existing replica history and backups. Missing replica validation prerequisites
stop that selected operation, without discarding pending data or switching stores.
This optional skill supplies the executable and its complete local modules;
selecting or installing it does not select a store, initialize a database,
migrate records or adopt workflow governance.

Obtain the caller's project root, requested operation, record or store identity,
and permitted effect. Reuse existing authorization for the same bounded work.
Read `capabilities` before depending on a selected provider operation. Missing
prerequisites or an unavailable provider stop the affected operation; do not
switch stores, install dependencies or save configuration implicitly.

Use `find`, `context`, `read`, `resume`, `validate` and `operation` for bounded
reads. Preserve the returned revision and complete workflow reference. Perform
`checkpoint`, `init`, `create`, `create-task`, `write-document`, `revise-workflow`,
`export`, `preflight`, `restore`, `deactivate` or `activate` only for the caller's
selected effect and destination.
Apply the runtime's operation-specific concurrency and recovery contracts;
do not invent successful retries or infer success from a process interruption.

Report the actual result, mutation state, limitations and next action. A local
record write, export or restoration does not establish a Git commit, push,
provider update, workflow completion, acceptance or deployment. Keep existing
Git records on their selected provider unless migration is separately requested.
