# Portable Skill Contract, Initial Design

Status: implementable design for Issue #325 / P1-A, not an installed or executed product. The Lesson package is a design specimen. A declared operation does not prove implementation or authorization. Normative wording describes intended P2 behavior, not new rules for executing this source repository today.

## 1. Boundary and authority

A capability package can run without an organizational workflow. This slice has one Lesson package, one filesystem store and one record family. There is no download service, global registry, generic dependency solver, provider sync, full migration engine or mass relocation.

The package owns instructions, public operations, schemas, default templates and tools. The project owns accepted settings, permissions, custom templates, standards and records. The runtime owns actual capability observations and results. No metadata grants external-write permission or proves approval, tests or publication.

P1-B (#326) owns source placement, distribution allowlists, installation inventory, framework.lock and runtime projections. P1-A owns the package-relative interface, settings semantics and Lesson schema. Runtime projections are generated from one source, never another manually editable owner. Custom data/local state do not become distribution inputs merely by proximity to core.

## 2. Package identity and versions

A package contains `SKILL.md`, `skill-package.yaml` and declared resources. Resource paths are package-relative, never relative to cwd, installation parent or the source repository. Declare all references; private `../other-skill/...` dependencies and mandatory `.dev/...` lookups are invalid.

| Field | Type and meaning |
| --- | --- |
| `metadata_version` | Integer `1`; unknown versions stop loading. |
| `id` | Stable lowercase dotted namespace: `[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*`; initial ID `lesson`. |
| `version` | Exact `MAJOR.MINOR.PATCH`, no range/prerelease in this initial contract. `0.1.0` is a design value, not a release. |
| `delivery_status` | `design-only` here; later `implemented` requires actual payload. Neither means validated. |
| `entrypoint` | Existing package-relative `SKILL.md`. |
| `dependencies` | Explicit `required` and `optional` arrays, even when empty. |
| `runtime` | Capabilities/libraries, version constraints, affected operations, absence result; not availability evidence. |
| `configuration` | Namespace and complete defaults for this slice. |
| `artifact_roles` | Logical role, authority owner, schema, operations and storage semantics. |
| `resources` | Owned schemas, templates, tools and references; paths stay inside the package. |
| `operations` | Stable operation IDs, inputs/outputs, tool and implementation status. |

YAML is restricted to the JSON data model: unique string keys, no custom tags, merge keys or aliases; versions are strings. Unknown metadata/config keys are errors in version 1. Arbitrary extensions exist only in the record's namespaced `extensions` map. A planned tool may have a null entrypoint; an implemented tool must name an existing package-contained executable, and a loader must never invoke a design-only package. Nested metadata keys are exactly those defined by the specimen and this contract; future fields require a metadata version decision, not silent fallback.

Framework distribution version, skill version, metadata version, project `config_version` and record `schema_version` are distinct axes. Framework selection does not convert project records. P1-B's lock binds selected packages and content; this design neither owns its serialization nor invents a digest for an unbuilt package.

Custom skills use distinct namespaced IDs. Duplicate providers for an ID are a conflict, not precedence-based shadowing. Replacing a package binding requires explicit project selection, never an ordinary local setting override.

## 3. Dependency closure and missing capabilities

Required entries are `{id, version}` with exact versions. Packaging includes their transitive required closure; invocation verifies identities and required resources. Reject cycles, duplicate IDs at different versions, undeclared cross-package references and missing resources. Do not fetch or choose alternative versions. An incompatible preselected set is rejected without a dependency solver.

Optional entries are `{id, version, operations, on_missing}`. `operations` lists dependency public operations used only by explicit collaboration; `on_missing` is `return-candidate` or `unsupported`. Optional entries are excluded from required closure and never auto-invoked. Only their exact declared version is supported initially. Before calling an installed optional package, verify its required closure too. Reject a repeated skill/operation pair in the invocation stack to bound recursion.

Illustrative shape only, not actual Lesson dependencies or capability availability:

```yaml
required:
  - {id: example.helper, version: '0.1.0'}
optional:
  - id: example.decision
    version: '0.1.0'
    operations: [propose]
    on_missing: return-candidate
```

Lesson declares **both arrays empty**: complete skill closure `lesson@0.1.0`. Runtime libraries are separate, not skills. Project standards are explicit task context when needed, not another skill's private policies. Missing optional cooperation preserves the primary Lesson result and returns a candidate/unsupported disposition; it never pretends to have written an ADR or Issue.

| Condition | Behavior |
| --- | --- |
| Unknown version or missing package/schema/resource | `unsupported`; no guessing or write. |
| Required runtime capability/library missing | `unavailable`; identify it; no silent manual-write substitute. A separate prose draft is not persisted execution. |
| Optional capability missing | Its declared candidate/unsupported disposition; primary output remains intact. |
| Permission or writable storage unavailable | `blocked`; no fallback path, disk or credential change. |
| Invalid input/config/schema/template | `invalid-input`; reject before record mutation. |
| Content changed or writer lock held | `conflict`; require a fresh read. |
| Provider operation requested | `unsupported` in this filesystem-only slice. |

Results name the selected operation, actual outcome and actual output references. `not-executed` differs from `succeeded`. Readers compute raw-byte SHA-256 for conflict checking; examples do not invent digests. No execution receipt schema is introduced here.

## 4. Ownership and update boundary

| Class | Owner / writer | Preservation rule |
| --- | --- | --- |
| Installed instructions/schema/tools/default template | Framework; installer owns exact file inventory | Replace only verified managed/unmodified payload. Modified core requires reconciliation; ownership is not deletion authority. |
| Config, constraints, custom templates, adopted standards | Project | Package updates never overwrite these. |
| Lesson record | Project; Lesson tool performs authorized operations | Preserve content and identity according to operation; package updates do not migrate records. |
| Rendered view | Derived from record plus template | Regenerate on request; never authoritative input. No implicit persisted copy. |
| Local override/cache | Machine/project operator | Ignored, outside core; no team permission or shared history authority. No cache is needed initially. |
| Store writer lock and replacement temp file | Active invocation | Transient, store-confined; only their owning invocation cleans them. Stale locks need explicit recovery. |
| Git tracking / installation inventory | Project / P1-B tooling respectively | Tracking is intent, not proof or permission to stage, ignore, commit or publish. |

Root agent instructions remain project-owned. Standalone Lesson use needs no workflow locator, Git repository, network, credentials, index or source checkout.

## 5. Configuration and precedence

The package-owned [configuration contract](lesson/references/configuration.md) defines all input fields, defaults, locks, four-layer precedence and `explain`. It ships with the Lesson instructions so standalone use never requires this design directory.

## 6. Filesystem roles and paths

The same [configuration contract](lesson/references/configuration.md#filesystem-roles-and-paths) owns store-scoped references, frozen bindings, canonical containment, external-store permission and partial-read behavior. No universal artifact registry is required.

## 7. Schema, tools and migration

The sole record family is `lesson.record@1.0.0`, owned by `lesson`. Its [schema](lesson/schemas/lesson-record.schema.json) owns structure; [operations](lesson/references/operations.md) own semantics. Metadata/config use this closed field contract, not a generalized schema hierarchy.

| Artifact | Producer / reader | Initial operations | Version disposition |
| --- | --- | --- | --- |
| Package metadata | Package author / loader | Author/inspect; implementation preflight | Unsupported versions rejected; no conversion edge. |
| Project config | Project / resolver | Explicit edit and `explain` | Preserve original; conversion unsupported. |
| Lesson record | Create/revise / inspect/query/render/validate | Candidate-only content operations | Unknown format preserved and reported; no rewrite. |
| Template | Package/project / renderer | Bind and read fixed tokens | Invalid tokens reject rendering. |
| View | Renderer / human | Regenerate | Regenerate from supported record; no reverse import. |
| Execution result | Actual tool / caller | Observe actual outcome | Re-execute when new evidence needed; never synthesize history. |

All declared tool operations are **planned**. `accept`, `supersede`, `retire`, `promote`, delete, import, conversion, store move and provider sync are unsupported in the initial P2 slice. P3-A owns later lifecycle/promotion; P6 owns required data transitions; P7 owns validation.

Preserve namespaced extensions semantically; they cannot grant permissions. Unknown fields/lossy structures need reconciliation, not silent dropping. JSON has no comments; YAML or historical Markdown import is not implied. Future migrations must declare exact version edges, preview, input digest, backup/recovery and actual outcomes. No edge exists now; no historical approvals/execution may be invented.

## 8. Acceptance and integration

P1-B consumes stable ID/version, package-relative files and required closure. It chooses physical source/install/projection paths. `skill-package.yaml` is the coordinator-aligned metadata filename; distribution manifest and lock remain separately owned. This issue workflow and source release tools are not package dependencies.

| Issue #325 criterion | Evidence |
| --- | --- |
| Complete inputs, outputs and closure without private layout | Metadata resources/runtime, empty skill closure, operation table and standalone walkthrough. |
| Clear owners, configurable paths/templates | Ownership table, four layers, project constraints and custom path example. |
| Schema/tool/operation/migration dispositions without fabricated evidence | Planned tool/null entrypoint, candidate family, explicit unsupported operations, synthetic examples. |
| One skill/store/small family | One record schema; no index, shared resolver extraction, provider or solver. |
| Concrete design, example, workflow and zh-TW explanation | This contract, Lesson specimen, examples, README and issue workflow. |

Coordinator/#326 selects exact physical layout and projections; P2 implements the tool. No unresolved choice blocks this design delivery. Nothing here constitutes runtime or compatibility verification.
