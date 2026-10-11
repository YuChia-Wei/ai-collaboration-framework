---
name: workflow-records
description: Read and maintain explicitly selected workflow records through the bundled Git or local SQLite provider, preserving record identity, authorization and recovery evidence.
---

# Workflow Records

Use the [operation contract](references/operations.md) and the bundled
[CLI](tools/workflow-records.py) for an explicitly selected project and store.
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
