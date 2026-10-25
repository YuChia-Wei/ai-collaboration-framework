---
name: workflow-records
description: Read and maintain selected Git or SQLite workflow records, or prepare and accept Board V2 queries through an explicit host MCP binding, preserving identity, authorization and recovery evidence.
---

# Workflow Records

Use the [operation contract](references/operations.md) and the bundled
[CLI](tools/workflow-records.py) for an explicitly selected project and store.
For Board V2 reads and receipt lookup, use the separate
[Board query contract](references/board-query.md) and [CLI](tools/board-query.py).
Its `board-query-prepare` and `board-query-accept` operations require an explicit
binding and a caller-supplied MCP transport; preparation does not execute a query.
Keep its native numeric revisions, project scope and opaque cursors intact.
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
`checkpoint`, `init`, `create`, `write-document`, `export`, `preflight`, `restore`,
`deactivate` or `activate` only for the caller's selected effect and destination.
Apply the runtime's operation-specific concurrency and recovery contracts;
do not invent successful retries or infer success from a process interruption.

Report the actual result, mutation state, limitations and next action. A local
record write, export or restoration does not establish a Git commit, push,
provider update, workflow completion, acceptance or deployment. Keep existing
Git records on their selected provider unless migration is separately requested.
