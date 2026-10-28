# Source Workflow Store Policy

This policy selects daily workflow storage for this framework source project
only. It does not select storage for downstream projects or alter the generic
product contract. The owner's 2026-10-29 scope for Issues #416 and #514 selects
SQLite as this repository's sole read authority and write target. Online Board
development and multi-agent acceptance remain separately planned work.
Policy adoption, actual store configuration and repository integration are
separate observations.

## Authority and explicit runtime selection

New daily execution workflows and explicitly continued existing workflows use
the selected local SQLite store. Disabling the existing source replica binding
explicitly advances its format to `workflow-sqlite/2.1`; older runtimes must
refuse that format. The approved persistent configuration
is `%LOCALAPPDATA%\AI-Collaboration\ai-collaboration-framework\store-config.json`;
the database is `records.sqlite` in that same directory. Its selected identity is:

- `default_provider`: `local`;
- provider ID: `local`, store ID: `framework-workflows`;
- repository ID: `ai-collaboration-framework`.

Retain a complete `WorkflowRef` with `provider_id`, `store_id`, `workflow_id` for
every selection and handoff. Human workflow IDs remain immutable. Missing or
unavailable configuration, runtime, store or required binding stops the dependent
operation; do not fall back to Git, initialize a replacement, create configuration
or switch authority implicitly. Never put credentials in this configuration.

The optional `workflow-records` package is not installed in this source project's
managed skill selection. Use the actual source CLIs explicitly from the selected
checkout; a source invocation does not prove installation or automatic discovery.
Select a Python environment providing the prerequisites in the
[native operation contract](../../src/skills/workflow-records/references/operations.md)
and [source-store contract](../../src/skills/workflow-records/references/source-store.md).
From the repository root, these are the two invocation forms:

```powershell
python -I -B src/skills/workflow-records/tools/workflow-records.py --root . --config "$env:LOCALAPPDATA\AI-Collaboration\ai-collaboration-framework\store-config.json" --request "<native-request.json>"
python -I -B src/skills/workflow-records/tools/source-store.py --root . --config "$env:LOCALAPPDATA\AI-Collaboration\ai-collaboration-framework\store-config.json" --request "<source-request.json>"
```

Requests are explicit bounded UTF-8 JSON files. Configuration and request-file
creation are not automatic side effects. Read `status`, mutation/local result,
receipt and synchronization separately; exit status alone is not acceptance.

## Discovery and complete reads

Use native `capabilities`, `find`, `context` and `resume` with explicit configuration.
For a known workflow, a context request is:

```json
{"contract_version":"workflow-records/1","operation":"context","workflow_ref":{"provider_id":"local","store_id":"framework-workflows","workflow_id":"<workflow-id>"}}
```

`context` is a bounded projection and `resume` adds a bounded entrypoint read.
Neither exposes every preserved metadata/task extension. Before a decision or
revision requiring complete source state, use the public source-store reads:

1. Call `source-list` with `contract_version: workflow-records/source-store/1`,
   `store_ref: {provider_id: local, store_id: framework-workflows}`, `offset: 0`
   and a bounded `limit`. Follow `result.next_offset` until null as needed to find
   the selected original `workflow_id` with `kind: native-workflow`. Archive kinds
   remain historical copies and are not native continuation records.
2. Call `source-read` with that exact `snapshot_id`. Require
   `result.manifest.source.native_revision` to equal the native `context.revision`.
   If it differs, reread context and select the matching current snapshot; do not
   combine revisions or substitute the mapped `source_revision` as a native hash.
3. In `manifest.files`, select `_native/state.json`. For its declared `size`,
   call `source-chunk` with the same snapshot ID, that path and each zero-based
   `index` from 0 through `ceil(size / 49152) - 1`. Decode `content_base64`;
   verify returned snapshot/path/index, each chunk's `chunk_hash` and expected
   length, then the assembled file's complete size and manifest `sha256`.
4. Require the assembled state's SHA-256 to match the native revision, parse the
   verified UTF-8 JSON, and read its full `metadata` and `tasks`. Retain unknown
   fields. Document bodies are separate blobs: use public native `read` paging
   or the corresponding manifest document chunks when full content is needed.

Each source request above has the source-store contract version and complete
store reference. Reads are local and do not dispatch Board commands. Retain the
selected native revision for the next CAS mutation; if inputs advance, reconcile
the new state before writing.

## Explicit native continuation and historical provenance

Existing `.dev/workflows/` files and imported `archive-workflow` or
`archive-root-index` units retain their historical meaning and original bytes.
An archive copy is not a series of native execution events and does not prove
that every historical workflow migrated into native authority.

To continue a selected existing workflow, first select its baseline and actual
authorization on the dedicated continuation branch. Use the public native
`create` operation to establish that workflow in the selected store. Preserve
the human workflow ID, existing tasks and metadata, source timestamps, template
identity and selected entrypoint document; include required generic record fields
from actual source authority rather than inventing past actions. Preserve all
applicable bounds and unknown fields. Record the baseline's Git commit/path and
any uncommitted inputs actually used as honest provenance in metadata/the current
entrypoint. Never claim dirty inputs came from the commit alone. Creation records
an actual cutover event at the present time; it does not backdate native events
to the preserved historical timestamps. Read back the accepted native record
before treating continuation as performed. Do not keep editing the historical
Git locator/plan as a second current execution authority.

Formal design, requirements, specifications, ADRs, assessments and their evidence
remain Git-owned at their selected paths. Native execution records reference
them by path and source revision; record-only progress does not create a Git
artifact, commit or push obligation. Assessment references follow schema `1.1`
when carrying complete native identities; see the
[assessment policy](ASSESSMENT-ARTIFACT-POLICY.md).

## Daily progress and lifecycle

Use native `create-task` for new tasks and `revise-workflow` for one atomic
progress transition. Supply the complete workflow reference, stable operation ID,
current `expected_revision` and `expected_source_head`; for example:

```json
{"contract_version":"workflow-records/1","operation":"revise-workflow","workflow_ref":{"provider_id":"local","store_id":"framework-workflows","workflow_id":"<workflow-id>"},"operation_id":"<stable-operation-id>","expected_revision":"<context-revision>","expected_source_head":"<context-source-head>","metadata_patch":{"current_phase":"review","updated_at":"<actual-time-with-offset>"},"task_patches":[{"task_id":"<current-task>","status":"completed","updated_at":"<actual-time-with-offset>","result":{"summary":"<observed-result>","finding_status":"<addressed-status>"}},{"task_id":"<next-task>","status":"in_progress","updated_at":"<actual-time-with-offset>"}],"documents":{"<existing-entrypoint-document>":"<complete updated plan/report text>"}}
```

Retain actual task result fields from the selected source template; the example
does not impose a generic product result schema. Update the existing entrypoint
document and any named report documents in the same revision when their contents
form the transition. This operation does not change the entrypoint identity.
The source [artifact policy](WORKFLOW-ARTIFACT-POLICY.md) owns minimum metadata,
timestamps, completion and the selected exactly-one-`in_progress` lifecycle;
the generic product validates record shape, not this project's status meanings.
Complete the current task, start its successor and change phase atomically when
that lifecycle applies. For terminal completion, satisfy its terminal conditions
without inventing a successor.

Retain the exact request and receipt. Same-request replay uses the same operation
ID; a changed payload requires a new operation. A missing/lost response is not
proof of rollback: reconcile the original receipt before retry or new work.

## SQLite-only operation and recovery

The existing Board binding must be disabled through public `binding-status`
and CAS-bound `binding-disable`, retaining the original request and receipt.
After its cutoff, new local revisions capture no intents for that binding;
command preparation is refused. Keep prior snapshots, bindings, pending intents,
commands and observations unchanged as history. Do not dispatch retained pending
commands, create a new remote target or select a remote read source under this
policy. Historical lookup/observation support is not delivery authorization.
Local reads and writes continue without Board or network availability.

Use complete native `export`, `preflight` and inactive `restore` for selected
backup/recovery checks, retaining archive/snapshot digests. A restored copy is
inactive; successful backup or inspection does not transfer write authority.
Deactivation, activation or replacement requires its separately selected recovery
procedure and authorization. Preserve the existing database and recovery evidence.
This policy neither performs native cutover nor claims backup, transport or
runtime acceptance merely because these instructions exist.

Use `export-files` and `preflight-files` for readable current `workflow.yaml`,
tasks and documents, with explicit project-owned schema/template selection when
needed. That projection does not replace the complete archive or authorize
re-import, migration, disaster promotion or activation.
