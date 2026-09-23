# P3 metadata v2 distribution support

This is the first-stage source implementation for [Issue #337](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/337), under [D-P3-02 and D-P3-05](../p3-shared-contract.md). It extends the [P2 assembly interface](README.md). The source has not been run: product CLI, builders, schema validation, tests, installation/migration and CI are `deferred-by-owner` under U001 to program #322 coordinator / P7.

## Explicit metadata versions

`src/distribution/package.py:load_package` consumes exact integer `metadata_version` 1 or 2. Booleans, floats, strings and other versions are rejected; there is no implicit negotiation or conversion. Both versions keep the same closed top-level fields, package identity/version, implemented-only delivery gate, `SKILL.md` entrypoint, dependencies, runtime requirements, operations, resource ownership, configuration namespace and store/template defaults.

| Boundary | Metadata 1 | Metadata 2 |
| --- | --- | --- |
| Schema identity | Unique schema `id`; existing `named()` reader | Unique exact `(id, version)` pair; one ID may declare multiple versions |
| Schema resource fields | `id`, `version`, `path`, `owner`, `migration` | Same fields; unknown fields rejected |
| Cross-kind resource identity | Schema/template/tool IDs cannot collide | Same rule; repeated schema ID at different versions is not a cross-kind collision |
| Project role | Existing closed fields including sole writable `schema` | Same fields plus required `read_schemas` |
| Readable schemas | Existing v1 interpretation; `read_schemas` remains unknown | Nonempty unique array of exact declared `id@version` values; must include writable `schema` |
| Derived role | Existing fields and a declared project `source_role` | Unchanged; `read_schemas` is not a derived-role field |
| Schema references | Existing package-relative reference check | Only same-document `#/$defs/` pointers; no external/file reference resolution |

All resource paths still enter `Paths`: duplicate paths, case aliases, traversal and file/directory prefix collisions remain errors. Same-ID schema versions need separate declared package members. Tool/template/operation/dependency IDs retain their existing rules. Duplicate role IDs still fail. Writable `schema` remains one exact string; `read_schemas` adds no write permission, version ranges, fallback, highest-version selection, migration or conversion.

The metadata stays in its original data shape in `Package.metadata`; `Package.members` remains the exact declared member set. The shared `named()` helper is unchanged. No metadata helper/member field or runtime dependency is added.

## Reference inspection without schema execution

`check_references` retains Markdown inline/reference-definition package containment, never fetches web citations, reads strict JSON and checks the Draft 2020-12 declaration. Metadata 1 keeps its existing schema-reference route. Metadata 2 inspects `$ref` and `$dynamicRef` values with a finite same-document JSON pointer lookup:

- Require literal `#/$defs/` prefix. External HTTP/HTTPS/file references, package file references, root fragments and named anchors do not enter a resolver.
- Check percent/JSON pointer escapes, locate every object key or canonical array index inside the already selected JSON document and require an object/boolean target. Missing targets or traversal through scalars fail.
- Never recursively expand a reference target. A chain or cycle cannot trigger unbounded resolution in the builder because no reference expansion occurs. This is not a claim that recursive schemas or their runtime semantics have been validated.

The private pointer helper performs content-reference inspection only. No jsonschema validator, remote registry, package-tool import or package operation is invoked. Schema semantics, nested resource scopes and actual runtime behavior remain package-owner/P7 responsibilities. Project config version 2 is also package-owned; the builder does not parse another project configuration.

## Existing consumers and later mapping

Source inspection of `selection.select` shows that it already consumes `Package.members`, compares the manifest's exact member set, loads only selected Git blobs and calls `check_references`. `assembly.assemble` preserves each package's actual `metadata_version` in selection metadata. `tools/build-development.py` remains a thin CLI. No direct call-site change is needed for this source stage.

Actual P3 source delivery is a later integration input. This checkpoint does not add manifest/profile entries or pretend that the five selected packages have arrived. The coordinator must supply the real integrated commit, exact member inventories and profile selection decisions to this same #337 task. Existing missing-member and closure checks are not relaxed.

## Deferred focused cases for P7

P7 selects and runs checks after restoration authority: unchanged v1 packages and v1 rejection of v2-only fields; exact version types; same-ID/different-version schemas; duplicate schema pairs, path aliases and cross-kind collisions; absent/empty/duplicate/undeclared `read_schemas`; missing writable inclusion; duplicate/derived roles; unknown fields; same-document pointer targets, escapes, missing/scalar targets, arrays and external/file references; bounded reference handling without schema execution; exact actual member mappings and independent five-package selection. These are unexecuted case descriptions, not test results or build acceptance.
