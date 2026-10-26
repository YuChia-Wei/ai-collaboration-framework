---
name: workflow-board-experimental
description: Explicitly opt in to experimental Board V2 query and command bridges without selecting a store or dispatching network operations.
---

# Experimental Workflow Board

This experimental package requires the explicitly selected `workflow-records`
core. Ordinary presets install neither package. Installing this package does not
activate it, bind a service, change the read source or grant external-write
permission. Actual online acceptance is separately scheduled; local fixtures do
not establish login, ACL, sharing or real-client continuation support.

For the caller's explicitly selected operation, use the [query contract](references/board-query.md)
and [CLI](tools/board-query.py), or the [command contract](references/board-command.md)
and [CLI](tools/board-command.py). Supply `--activate` on each CLI invocation and
the explicit nonsecret binding/request. Without activation the CLI returns
`experimental_not_activated` before loading its runtime or reading the request.
These bridges prepare and validate supplied data; they never dispatch network
calls, retrieve credentials, select a different identity or retry automatically.
The host must separately select and authorize actual transport effects.

Retain the complete original prepared command before host dispatch. On unknown
outcomes reconcile the original operation; replay only its exact original
command. Preserve native revisions, project scope and opaque cursors. Never
substitute a local acceptance result for Board acceptance.

When upgrading a former combined `workflow-records` installation, inspect the
normal installer plan: select this package explicitly if Board bridges are still
wanted. Do not infer that choice from stored bindings or automatically edit
configuration. The core preserves old replica data; removing this package does
not delete pending commands or change SQLite writer authority. Package selection,
activation, local validation and online acceptance are separate states.
