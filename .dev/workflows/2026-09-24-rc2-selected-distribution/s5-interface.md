# S5 verified resource interface, version 1

Issue #406. This protocol is fixed for S5 integration; implementation is in progress
on this S3 branch. Source presence and direct AST checks are not behavioral evidence.

## Entry and ownership

`distribution.catalog.read_installed_resources(project_root, expected_lock_sha256, authorities)`
is read-only. Import it only through the verified engine-2 source closure in an
isolated `-I -B` host; never add an ambient checkout to a target's import search path.
The maintenance `inspect` request does not discover or save project configuration.
An instruction-only S5 consumer may follow the exact installed-file protocol below
using this same reader owner; it must not invent another lock/metadata parser.

Arguments:

- `project_root`: explicit canonical project root selected by the caller.
- `expected_lock_sha256`: exact externally observed raw SHA-256 of `.ai/framework.lock`.
- `authorities`: closed Authority rows `{path, sha256, selector}`. This is the exact
  deduplicated authority allowlist from the selected bindings, not a query expression
  for S3 to evaluate. Duplicated `(path, selector)` is invalid. Every raw hash must
  match the direct bounded project file. Different selectors may name one file.

The reader rejects incomplete markers, absent/legacy lock, stale lock identity,
managed drift, unknown formats, path aliases/links/hardlinks, undeclared authorities
or authority drift. It verifies the complete installed lock-2 identity/member closure
before returning any index. Failures raise the shared bounded `InstallationError`
or `DistributionError`; no partial resource result is returned.

Exact successful return keys:

```text
{
  lock_sha256, candidate_identity, desired_sha256,
  resources: [{package, version, resource_id, member, sha256, resource}],
  bindings: [Binding],
  authorities: [{path, sha256, selector,
                 status: "raw-hash-matched", semantic_applicability: "target-owned"}],
  semantic_applicability: "target-owned"
}
```

`resource` is the exact closed Resource from content-package 1, including kind,
rule_ids, capabilities, operations and technology_profile. `member` is the exact
installed `.ai/core/knowledge/<id>/<member>` path; `sha256` binds its raw bytes.
`bindings` is the exact saved desired selection binding list embedded in lock 2.
No binding means no adopted normative coverage. Index availability grants neither
applicability nor approval. Caller data remain unchanged.

S5 filters the verified index/bindings by the caller's explicit capability,
operation, execution mode, affected paths/file types, technology and requested
coverage; consults the named target owner for authority selectors and predicates;
and reads only those resource bytes through bounded direct file reads matching the
returned SHA-256. Re-observe the exact lock/markers and authority hashes around the
read; if drift occurs, discard the result. It returns the consumption result from
S1 consumption.md (available/unavailable/blocked, coverage and exact missing items).
No technology inference, source `.ai/assets` fallback or silent specialist success.

Metadata-4 consumer row shape is the S1 KnowledgeConsumption definition:
`{id, package, version, operations, resources, requirement, on_missing}`.
Rows sort by id; operations/resources are sorted unique sets. IDs/operations and
configuration semantics retain their owner. S5 returns exact metadata/member bytes,
component versions and hashes to S3; only S3 updates shared manifest/catalog rows.

## Project-owned transition seam

API-2 plan/apply adds required `project_edits` (possibly empty) to the existing
closed plan fields. An intent is exactly
`{path, before_sha256: hash|null, after_sha256: hash|null, after_content_ref: string|null}`.
Non-null after content uses `objects/<after_sha256>` under the explicit staging root.
The object must already exist, be bounded/direct and match the hash. A delete has
both after fields null. Absence is explicit and never inferred from a filename.

The caller separately authorizes each root/config/routing withdrawal. S3 verifies
preimages and object bytes, rejects any managed/protected/control path overlap,
retains exact before bytes/modes and after objects, and binds all edits into the plan
hash and journal 2. It never seeds target roots or writes config on ordinary inspect,
plan or invocation. `project_data_action` remains `none`. Final operation/journal
shape and phase transitions are published in api2-maintenance.md before S6 use.
