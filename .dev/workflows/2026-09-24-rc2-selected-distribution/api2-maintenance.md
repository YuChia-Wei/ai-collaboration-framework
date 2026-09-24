# API 2 operation and journal 2

Issue #406; source implementation contract. Behavioral acceptance remains
`deferred-by-owner` to selected S6/P7. No receipt here claims actual installation.

## Closed requests

All requests contain exactly `api_version: 2`, `operation`, `project_root`,
`engine_root`, and `engine`. Engine is the S1 Engine pin: ID
`framework-managed-installation`, version `2.0.0`, source_commit and complete files.

- `inspect`: optional `candidate_root`; no other fields.
- `plan`: `candidate_root`, `candidate_identity`, `expected_lock_sha256` (hash/null),
  `mode_policy`, `scratch_root`, `staging_root`, `recovery_root`, `durability`,
  `protected_inputs`, `project_data_action: none`, `project_edits`.
- `apply`: all plan fields plus `expected_plan_sha256` and `maintenance`.
- `recover`: `operation_root`, `operation_sha256`, `direction: finish|restore`,
  `expected_lock_sha256`, `expected_marker_sha256`, `maintenance`; optional exact
  boolean `reconstruct_missing_managed`, currently supported only as false for the
  paired protocol. Unknown/damaged project state is never synthesized. Engine-1
  whole-loss recovery remains owned by that original pin.

`durability` remains exactly `{declared_by, declaration_reference, failure_domain}`.
`maintenance` remains exactly `{declared_by, declaration_reference,
affected_capabilities, sessions_stopped, tools_stopped, external_writers_stopped}`.
The three booleans must be true; capability IDs equal the sorted old/new component
union from the plan. Existing native filesystem/failure-domain admission remains.

`protected_inputs` is sorted `{path, sha256: hash|null}`. Explicit project edits
cannot overlap managed members, either marker, lock, guard, Git/coordination
storage, another project edit or a protected input (including path/case prefixes).
An existing framework.json must be explicitly protected or edited. Binding
resources/authorities must match the selected subset; nonedited authorities are
included in the effective protected list. Config and binding meaning remains
project-owned. An explicitly saved installation.json must equal the desired
selection semantically; its exact whitespace/raw preimage remains recoverable.

## Intents, planned records and objects

Input intent: `{path, before_sha256: hash|null, after_sha256: hash|null,
after_content_ref: string|null}`. A non-null after reference is exactly
`objects/<after_sha256>` relative to the explicit staging root. It is read and
hashed before any operation allocation. Null after fields mean delete. Null before
means absent; matching unowned bytes never grant permission. Existing project modes
are preserved (0644/0755 on POSIX); a new file uses 100644. Windows modes remain
inventory-only. S3 never applies broad root templates or recursive directory removal.

The plan's `project_edits` contains sorted records:
`{intent: InputIntent, before: Descriptor|null, after: Descriptor|null}` where
Descriptor is exactly `{sha256, size, mode}`. Exact before/after objects are retained
under the operation's objects directory, named by SHA-256. The plan contains exact
managed delta, engine/candidate/lock identity, roots, durability, effective protected
inputs, `project_inputs` (non-null after-state pins), maintenance scope, unknown
siblings, path budget, prerequisites and an exact `noop` boolean. The entire
canonical plan is hashed and retained as an object. A project edit forces a paired
transaction even when its content hashes are equal; ordinary no-op has no edits and
requires identity/inventory/mode/project-input equality.

## Immutable operation.json / journal 2

Exact required keys (no optional keys):

```text
operation_version: 2
journal_version: 2
operation_id: 32 lowercase hex
installation_id: stable 32 lowercase hex
engine: Engine2
engine_objects: [{path, sha256}]  # exact engine.files, all raw objects retained
project_root: exact original root
operation_root: exact recovery parent/i-<operation_id>
durability: Durability
maintenance: Maintenance
plan_sha256: hash of retained canonical plan object
before_lock_sha256: hash|null
after_lock_sha256: hash
candidate_metadata: {metadata/catalog.json: hash,
                     metadata/catalog-files.json: hash,
                     metadata/selection.json: hash,
                     metadata/files.json: hash,
                     metadata/build.json: hash}
protected_inputs: [{path, sha256: hash|null}]
project_data_action: none
project_edits: [{intent, before, after}]
```

The immutable operation is the journal; there is no mutable phase field to trust.
Before locks preserve their original raw bytes and engine pin. After lock 2 embeds
the parent documents and subset/inventory plus independently selected writer pin.
Both candidate and retained recovery objects call the same semantic readers.
Before/after sides remain distinct even when lock hashes are equal. Restore uses
the exact captured project preimages, including an explicitly admitted preexisting
project edit; it never rewrites those bytes to recreate an older project-input pin.
Finish verifies all new lock project-input hashes. Project readiness and any stale
restored project-input bindings remain separately observable by the consumer reader.
Recovery recomputes all identities, validates both lock/content closures, reconstructs
runtime bytes with the proper legacy/v2 seam, checks exact engine objects and retained
plan binding, and rejects malformed or mismatched objects before any mutation.

## Observable phase transitions

1. **Prepared**: reader computes plan; no allocation or writes.
2. **Captured**: under writer exclusion and fresh quiescence, all content/engine/plan
   objects and immutable operation.json read back. No marker yet; partial preparation
   grants no mutation authority and is retained, not cleaned up automatically.
3. **Managed marker admitted**: `.ai/framework.operation` equals operation.json.
4. **Paired marker admitted**: `.ai/config-transition.operation` also equals the
   same exact bytes. Both sides are inactive while either marker remains.
5. **Transitioning**: each exact managed/project destination may match only its
   retained before or after state. Both markers remain. Unknown/torn bytes block.
6. **Lock published**: every requested side matches its target; lock is atomically
   published, then core/runtime/project inputs are read back. Both markers remain.
7. **Project marker removed**: managed marker remains as final activation barrier.
8. **Complete**: managed marker removed last; final bytes/lock/protected inputs and
   held writer identity read back. The result proves paired bytes only; target gates
   and runtime discovery are separate. Empty unknown directories/siblings remain.

An interruption before phase 3 has no recovery admission marker; preserve residue
for owner reconciliation. A managed-only marker is valid only with exact captured
before/after states (phase 3 or 7). A project-only marker or any other marker bytes
is unknown and blocked. Recovery accepts only the exact retained operation/engine,
explicit expected current lock/managed-marker hashes and a fresh maintenance
declaration. It supports finish/restore of the paired union; newly supplied desired
selection/project edits are forbidden. After both markers are absent, replay is
read-only and succeeds only if the requested entire target already matches.

## Isolation and CLI

`python -I -B ENGINE/src/tools/maintain_framework.py < request.json` keeps the
four-operation public protocol. Read-only consumer hosts use the same retained-byte
finder through `verified_engine`, described in s5-interface.md. New builders require
an independent `--engine-pin` JSON and verify bootstrap raw bytes before importing
any distribution module. No distribution directory is added to sys.path by those
new entrypoints. Legacy --profile writers keep their original meaning and reject
manifest 2/preset 1/metadata 4 as unsupported-write before output allocation.

Example commands (placeholders require separately selected actual pins/roots):

```text
python -I -B ENGINE/tools/build-catalog.py --repository ENGINE --commit FULL_COMMIT --engine-pin PIN_JSON --release-version 0.19.0-rc.2 --output-root OUTPUT --scratch-root SCRATCH --engine-output-root ENGINE_OUTPUT
python -I -B ENGINE/tools/derive-subset.py --engine-pin PIN_JSON --catalog-root CATALOG --catalog-identity EXACT_CATALOG_ID --preset complete --preset-version 0.1.0 --output-root OUTPUT --scratch-root SCRATCH
python -I -B ENGINE/tools/derive-subset.py --engine-pin PIN_JSON --catalog-root CATALOG --catalog-identity EXACT_CATALOG_ID --selection EXPLICIT_SELECTION_JSON --output-root OUTPUT --scratch-root SCRATCH
```

The latter two run from a standalone verified engine bundle without a source
checkout. A preset expands once; the resulting explicit desired object is returned.
There is no --save-selection switch. Explicit project saving is an authorized
installation.json intent in the same paired maintenance transition.
