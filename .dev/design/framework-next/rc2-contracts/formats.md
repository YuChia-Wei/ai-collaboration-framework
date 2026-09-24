# rc.2 selectable installation format contract

Contract set: `aicf.rc2-selection/1`, selected for implementation by Issue #401
(S1 of program #322). This is a design contract. The current rc.1 parser does
**not** accept these new documents. JSON Schema files describe shapes; prose below
also supplies cross-document, lexical, ownership and digest constraints.

## Paths and version dispatch

| Document | Exact path | Discriminator | Owner |
| --- | --- | --- | --- |
| Desired installation | `.ai/custom/installation.json` | `selection_version: 1` | Project; explicit save/edit only |
| Skill operation settings | `.ai/custom/framework.json` | Existing config version 2 | Project; unchanged format, explicit caller argument |
| Content metadata | `src/knowledge/<id>/content-package.yaml` | `content_package_version: 1` | S2 content owner |
| Skill metadata | `src/skills/<id>/skill-package.yaml` | Existing `metadata_version: 1/2/3`; new 4 below | Skill owner; S3 reader |
| Source manifest | `src/distribution/manifest.yaml` | New `manifest_version: 2` | S3 only |
| Source preset | `src/profiles/<id>.yaml` | New `preset_version: 1` | S3 only |
| Parent catalog | `<catalog>/metadata/catalog.json` | `catalog_version: 1` | S3 builder |
| Parent file index | `<catalog>/metadata/catalog-files.json` | `catalog_files_version: 1` | S3 builder |
| Parent completion | `<catalog>/metadata/build.json` | `schema_version: 2`, `artifact_kind: catalog` | S3 builder |
| Selected candidate | `<subset>/metadata/selection.json` | `schema_version: 3`, `mode: catalog-subset` | S3 derivation |
| Selected file index | `<subset>/metadata/files.json` | `schema_version: 2` | S3 derivation |
| Selected completion | `<subset>/metadata/build.json` | `schema_version: 2`, `artifact_kind: subset` | S3 derivation |
| Standalone engine descriptor | `<engine>/engine.json` | `engine_package_version: 1` | S3 engine packaging |
| Installed lock | `.ai/framework.lock` | `lock_version: 2` | S3 installer only |

A subset also contains byte-identical `metadata/catalog.json` and
`metadata/catalog-files.json` from its parent, selected payload and rendered runtime
files. It does not include unselected package payload. A catalog holds every
explicitly published available component and adapter input, independently of any
installation. No downstream operation requires a source checkout.

The [schema bundle](schemas/contracts.schema.json) is authoritative for required
fields, field types and closed objects; each adjacent named schema selects one
root definition. All fields are required except `Selection.expanded_from` and the
two subset-only keys of `Build.identity_inputs`. Those keys MUST both be absent
for a catalog and both present for a subset. `null` is allowed only where the
schema explicitly says so. Metadata source YAML uses the same object meanings,
with duplicate keys, tags, anchors, aliases, merge keys and multiple documents
rejected. No unrecognized field is an extension point.

## Primitive and parsing rules

1. Decode strict UTF-8; reject BOM, duplicate JSON keys, nonfinite numbers, unpaired
   surrogates and extra trailing data. JSON versions/sizes are lexical integers:
   `true`, `1.0`, `1e0` and strings cannot stand for integer 1. JSON Schema alone
   cannot enforce this lexical boundary. Do not use Python equality as a type test.
2. Generated JSON uses `C(x)`: Unicode-preserving JSON, object keys sorted by
   Unicode code point, `indent=2`, `allow_nan=False`, UTF-8, exactly one final LF;
   standard JSON escaping and separators as Python `json.dumps(..., indent=2)`.
   Generated metadata and lock bytes MUST equal `C(parsed)`. Source YAML and
   payload bytes are hashed raw; never normalize them before file verification.
   Project JSON may have ordinary whitespace; parse and canonicalize only for
   the semantic selection digest, retaining its raw hash for drift/recovery.
3. Component IDs use the schema's lowercase ASCII grammar. Versions are exact
   canonical `MAJOR.MINOR.PATCH`; distribution versions additionally permit
   `-rc.N` with positive N. No ranges, build metadata, floating tags, network
   solver or numeric upgrade inference. Hashes are lowercase raw SHA-256; Git
   object IDs are full 40 or 64 lowercase hex and one source uses one Git format.
4. Arrays representing sets are unique and sorted: IDs lexically; components and
   dependencies by `(kind,id)`; files/build inputs by `path`; resources/bindings
   by `id`; adapters/presets by `id`; references by `(from,resource_id,target.package,
   target.path,target.anchor or empty)`. Ordered normative source prose is never
   sorted. A duplicate ID at two versions is invalid, not a version choice.
5. Paths are relative forward-slash exact paths. Reject empty segments, `.`, `..`,
   absolute/drive/UNC paths, backslashes, streams, reserved names, control bytes,
   trailing dots/spaces, aliases and case-fold collisions. Never resolve a path
   using an untrusted working directory. Root selection is a separate trusted
   operation input. No symlink, reparse point, hardlink, special file, path escape
   or change during observation is accepted. Windows direct-volume requirements
   and mode policy remain effective. Schema regexes are only a first filter.
6. Preserve existing caps: 4 MiB/document, 16 MiB/member, 128 MiB total materialized
   artifact, 4096 members/array, 128 components or protected inputs, 20000 directory
   entries, 100000 parsed nodes, depth 48, 256 KiB/source YAML, path 240 UTF-16 code
   units and segment 255. Apply aggregate budgets before allocation/read and after
   every expansion; embedded catalog documents count toward the lock's 4 MiB cap.
   Exceeding a cap is blocked; split explicitly selected content later, never
   silently increase limits or truncate inventories.

## Desired selection and presets

`Selection` requires `selection_version`, `catalog`, `skills`, `knowledge`,
`adapters`, and `bindings`. The catalog pin contains its independently computed
identity plus raw hashes of both parent metadata files. A caller separately supplies
the artifact root. A path, version label, branch or preset name is never a pin.
Each selected ID resolves to exactly one `(kind,id,version)` in that parent.
Adapters can be `[]`, `[codex]`, `[claude]` or both, in lexical order.

`bindings` is the minimal project adoption/consumer interface described in
[consumption.md](consumption.md). It references existing target authority rather
than copying rule decisions. An empty list is valid. Installation availability
alone does not imply applicability, adoption, authorization or specialist coverage.

A preset is a closed `Preset` object with exact version and explicit skill,
knowledge and adapter ID lists. Expand a selected preset **once** against the
pinned parent. Validate its dependencies, show the resulting explicit IDs and save
only when the caller requested saving configuration. Optional `expanded_from`
records preset ID/version, parent identity and `SHA256(C(preset))`. It is provenance,
not a resolver instruction. Later explicit edits are allowed; provenance does not
force equality with the preset. Removing provenance changes the desired digest.
Ordinary invocation never reevaluates a floating preset.

S3 converts the eight existing profiles to version `0.1.0` presets with their exact
current skill lists and adapter choices, `knowledge: []`. `complete` is its current
explicit 18 skills, not all future catalog items. New content selection is explicit;
S3 must not make engineering/knowledge profile names imply installing .NET content.
Empty skills plus selected knowledge is a valid reference-only core installation.
All-empty selection is a valid explicit managed deselection plan, still producing a
new lock; it grants no deletion of project data, custom files or unknown entries.

## Content packages and reference closure

`ContentPackage` is distinct from a skill: no `SKILL.md`, operations, execution
mode, runtime tools or auto-discovery entry is required. Version 1 has ID, component
version, `entrypoint` (selected as `README.md` for these two packages), complete
members, resources, dependencies and references. `content-package.yaml` itself is
one member of kind `metadata`; `README.md` is kind `index`.

Each resource ID is stable within its package and points to one declared member.
Original rule digests remain source provenance. Link-only relocation may change
rendered normative bytes: retain the original digest, record each substituted
link and the new text/file/catalog digests, and keep semantic applicability intact.
Duplicate active semantic owners for one stable rule ID fail closed, even when
text happens to match. Source/target retained catalogs remain under their own
versioned authority until explicit S5 reconciliation.
Kinds distinguish knowledge, illustrative examples, normative rules, catalogs,
templates and optional source includes. A catalog resource lists its exact stable
`rule_ids`; ordinary knowledge/example resources have `rule_ids: []`. A Markdown
file may contain a normative section and explanatory material: resource declarations
and catalog rule selectors preserve that distinction without promoting the whole
file. Resource capability/operation lists constrain loading, not target adoption.
`technology_profile: null` means no package technology restriction, not automatic
universal applicability. IDs for unregistered rules MUST NOT be derived from paths.

Member paths are exact package-relative strings. Materialize them only as
`.ai/core/knowledge/<id>/<member>`; skill paths remain `.ai/core/skills/<id>/<member>`.
No package may own roots, `.ai/custom`, lock/operation markers, other package roots
or runtime directories. Source includes and templates are inert references; no
copy into product source, compilation, project activation or tool execution occurs.

Each actionable cross-document reference is declared with its source member,
resource ID, destination package/member/optional exact heading anchor, requirement
and `on_missing: unavailable`. Same-package references name the same package.
Required references must resolve in the selected package closure. Cross-package
required references require a matching required dependency. Optional references
must use a capability/resource lookup guarded by availability; they cannot leave
an unconditional Markdown link to absent content. External URLs and provenance
identities are explicitly inert, never a required executable/loadable dependency.
Every local Markdown link in installed content resolves to a selected installed
member and valid anchor. No active `.ai/assets`, `.dev` source checkout, absolute
host path or undeclared file fallback is allowed.

Dependencies carry kind, ID and exact version. Required omissions, version mismatch,
self dependency, duplicate/overlapping required/optional keys and required cycles
block selection. Optional dependencies never install themselves; if selected they
must match the declared version. Absent optional resources return `unavailable` to
the requesting operation. Content-package dependency kinds must be `knowledge`; they cannot require
a skill or runtime adapter. No dependency installs itself. The dependency graph is over typed component keys.
For this migration, `dotnet-backend@0.1.0` requires
`knowledge/engineering-common@0.1.0`; engineering-common has no required package.

Skill metadata 4 is the existing closed metadata-3 contract plus required
`knowledge_consumption: [KnowledgeConsumption]` from the schema bundle. All other
metadata-3 fields, instruction/tool unions and configuration boundaries remain
unchanged. Versions 1–3 remain readable without this field; adding the field to
v3 is invalid. Each consumption row declares an exact optional/required content
package version, operation IDs and resource IDs; operations must already exist.
Required rows participate in dependency closure; optional rows use unavailable
semantics. S5 changes common skills only when they actually consume the interface,
bumping affected package versions. A shared method can remain useful without .NET;
a request promising .NET coverage must still resolve the target binding.

## Source manifest and immutable catalog

Manifest 2 uses typed components and explicit version/source/metadata/member maps;
the [manifest schema](schemas/manifest.schema.json) fixes its exact fields. Skill
source roots are `src/skills/<id>`, content roots `src/knowledge/<id>`. The manifest
member destination must equal the derived installed destination. Metadata member
closure and manifest closure must match exactly. Profiles reference versioned
preset files. Adapter roots are `src/adapters/<id>` with explicit version, template
and members; only Codex/Claude are supported. Unknown roots/adapter types fail closed.
S3 is the sole writer of this shared manifest and all source profiles.

A catalog is a distribution artifact, not an installation. It includes:

- The three catalog metadata documents listed above.
- Every declared component member at `packages/<kind>/<id>/<member>`.
- Every declared adapter input at `adapters/<id>/<member>`.

The file index lists exactly these input files, with kind, owner, member and full
source descriptor. Component descriptors bind typed ID/version, metadata version,
metadata filename, exact members and dependencies. Knowledge metadata_version is
exactly 1; skills allow 1–4. Descriptors and actual metadata must agree. Adapter
version is exact, prefix is `aicf-`, and its template is a declared member. There
are no generated runtime files in the parent catalog. Catalog generator ID is exactly `aicf-catalog-assembly`; subset generator ID is
exactly `aicf-subset-derivation`. Other combinations are unsupported. Catalog source and generator
provenance bind committed bytes, never uncommitted files. `build_inputs` is exactly
the union of metadata inputs, manifest, listed presets, all component/adapter
source members and generator implementation closure; reject extra/missing inputs.

Define `H(b)=SHA256(b)`. Parent identity inputs are the closed mapping:

```text
Icat = {"metadata/catalog.json": H(C(catalog)),
        "metadata/catalog-files.json": H(C(catalogFiles))}
Dcat = H(C(Icat))
parent = "catalog:1:" + release_version + ":" + source.commit + ":" + Dcat
```

Metadata contains no self hash. Catalog generator/build-input provenance and every
available member descriptor are inside this digest boundary. Completion time,
runtime observation and completion receipt bytes are outside identity, but build
shape and generator execution hashes must be checked before admitting the artifact.
A hash pin proves equality with supplied bytes; it does not establish publication
trust or authorize an upgrade.

## Subset derivation, adapters and installed identity

Selection 3 embeds the parsed desired selection and its canonical SHA-256, exact
parent pin, parent source/version, exact selected component/adapter descriptors,
and derivation generator source closure. No profile masquerades as an arbitrary
subset. The same parent can produce different subset identities.

Inventory 2 lists every selected core member and every selected runtime entry:

- Payload: `path = payload/ + destination`, typed owner `skill/<id>` or
  `knowledge/<id>`, source descriptor from the verified parent, `binding: null`.
- Runtime: `path = runtime/ + destination`, owner
  `adapter/<adapter-id>/skill/<skill-id>`, mode `100644`, `source: null`, non-null
  binding with adapter, stable skill ID, `aicf-<id>` name, exact installed core
  `SKILL.md`, and raw selected template hash.
- Codex destination: `.agents/skills/aicf-<id>/SKILL.md`; Claude destination:
  `.claude/skills/aicf-<id>/SKILL.md`. One entry per selected skill per selected
  adapter, none for content packages. Prefix is not user-configurable in v1.
- Descriptor equality covers mode/size/hash/owner/kind and origin/binding. The
  adapter renderer must reproduce exact runtime bytes from verified metadata and
  selected template; file presence or a copied wrapper is insufficient.
- The two adapters share exactly the selected `.ai/core` content. Runtime-only
  declaration differences belong to the adapters. All wrapper references resolve
  to installed core; no tool commands execute during rendering.

```text
Isub = Icat plus {"metadata/selection.json": H(C(subsetSelection)),
                  "metadata/files.json": H(C(subsetFiles))}
Dsub = H(C(Isub))
subset = "subset:3:" + release_version + ":" + source.commit + ":" + Dsub
```

Full parent metadata is verified even for a small subset; unselected payload need
not be copied. Catalog verification bounds and verifies the artifact before
selection; retained subset metadata then proves selected source membership without
requiring unselected bytes or the source repository. Parent/member hashes do not
justify skipping verification of selected raw bytes. Parent completion is checked
when deriving; subset completion separately checks the derivation implementation.
Build 2's `identity_inputs`, identity, kind and `executing_implementation` must
match the exact corresponding generator, and each execution hash must equal its
verified source hash. Completed timestamp requires explicit UTC offset. The three
`not-performed` fields do not become evidence of later installation or testing.

Lock 2 embeds both parent documents, subset selection and inventory, together with
stable installation ID, complete writer engine pin, mode policy and project-input
raw hashes. Recompute every parent/desired/subset identity when reading the lock.
The externally supplied expected raw lock SHA-256 guards observation/apply; never
place a self hash in the lock. Do not rederive it by deleting rows from lock 1.
Installed component versions come from its exact subset; human labels are not pins.
`project_inputs` includes the saved installation selection when used, all binding
authorities, framework config and each root/config touched by this transition.
Project inputs remain project-owned and outside the managed inventory.

Engine 2 uses ID `framework-managed-installation`, version `2.0.0`, API integer 2,
full source commit and the complete verified executable closure. Candidate source,
writer pin and prior installed writer pin are independent. An engine may be delivered as a standalone verified byte bundle: `engine.json`
contains exactly `engine_package_version: 1` and the closed `engine` pin. The caller
provides the expected pin independently; a self-described manifest is not trust.
The bundle contains exactly the descriptor and declared engine files at their
relative paths, including the isolated entry point; no source checkout is needed.
For this bundle branch, source_commit is immutable source provenance, not a claim
that a local Git checkout exists. When using a Git-checkout engine, retain the
existing observed-HEAD match as well as all raw-byte checks. This does not relax
the historical engine-1 branch. Engine packaging/delivery and actual execution
remain S3/R2/S6 work. New modules/templates
needed by catalog/adapter reading require explicit closure changes; do not import
ambient modules or silently reuse the rc.1 engine pin.

## Public failure outcomes

| Condition | Outcome / code | Required next step |
| --- | --- | --- |
| Unknown schema/metadata/API/adapter/engine version | `unsupported` / `unsupported-version` (or `unsupported-adapter`, `unsupported-engine`) | Select a capable explicitly pinned reader; no write |
| Request to emit rc.2 through API 1 or down-convert a lock | `unsupported` / `unsupported-write` | Use API 2 or exact recorded recovery owner |
| Missing/unknown fields, wrong types, duplicate keys, IDs, malformed paths | `blocked` / `invalid-shape` | Correct the explicit input; preserve existing state |
| Unknown selected ID, missing exact version/dependency | `blocked` / `selection-unavailable`, `dependency-closure`, `dependency-version` | Amend explicit selection; do not auto-install |
| Cycle, dangling required reference, absent rule/authority | `blocked` / `dependency-cycle`, `reference-closure`, `binding-unresolved` | Reconcile named item/target authority |
| Edited or unowned managed/name collision, unexpected alias/link | `blocked` / `managed-drift`, `unowned-collision`, `unsafe-path` | Preserve bytes; owner reconciliation |
| Pin/hash mismatch, changed input, absent marker/recovery evidence | `blocked` / `identity-mismatch`, `input-drift`, `recovery-incomplete` | Fresh bounded plan with correct fixed evidence |
| Missing optional knowledge or specialist requirement | `unavailable` consumer coverage result | Name missing resource and operation; common work may continue only within its truthful coverage |
| Incomplete/unknown filesystem or durability support | `unsupported` or `blocked` using existing safe diagnostic | No best-effort apply; retain the original failure |

Diagnostics expose bounded code, relative path when safe, reason and next action;
no host secrets, token values or raw host exception strings. A failed/unsupported
operation produces no success lock/receipt. A no-op requires matching complete
identity/inventory/mode and applicable project-input bindings, not only equal
selected file hashes.
