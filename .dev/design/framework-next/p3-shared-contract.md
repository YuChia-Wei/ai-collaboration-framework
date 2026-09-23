# P3 shared contract decisions

Status: selected implementation contract for #334, #335 and #337 under program #322. This addendum resolves the two design checkpoints; it is not runtime verification, installation, release or project adoption. Original proposals remain historical inputs. Each package must carry its own complete public contract; installed skills must not depend on this source design file.

## Inputs and selected versions

- Knowledge lifecycle checkpoint: `99adb0762328c8f8d6cff7338f17caec99685c0a` (#334).
- Work-management checkpoint: `446a579d03a25edf1b6e64b5e5c13016740025c0` (#335).
- P2/main integration: `ba36554b418977a2c8a12d51152c7b625bf48124`; dispatch main: `3f2a8e9b67be019933b506715bcf47e11eea3cd6`.
- Select lesson@0.2.0, adr@0.1.0, standards-promotion@0.1.0, pr@0.1.0 and local-backlog@0.1.0. All five use metadata_version 2 and empty required/optional skill dependencies. These are source package versions, not published releases.

## D-P3-01: isolated project configuration version 2

Adopt C334-01's version boundary and WM-C1's namespace isolation. Version 1 was explicitly closed to Lesson; retain that interpretation. Version 2 changes accepted namespace semantics and project constraints, so use an explicit version instead of silently expanding the closed v1 envelope. The coordinator's earlier tentative config-v1 preference is superseded by this joint decision.

The version-2 project object has required exact integer config_version=2 and optional skills/constraints; the local object permits skills only. Root keys are closed. Each namespace follows `[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*` and maps to a JSON object. Reject duplicate keys, invalid Unicode, non-finite numbers, bool/float versions and malformed namespace envelopes. Parse JSON globally, then validate only the selected skill settings and selected constraints strictly. Other namespace objects are inert: no deep validation, tool loading, capability claim or authority. Explain may list ignored names, never dump their values. Unknown selected fields fail. Never combine permissions across namespaces.

Keep invocation > local > project > package defaults; merge store leaves, replace template atomically; explicit project write roots/locks and caller narrowing remain independent of ordinary settings. Local constraints are forbidden for all namespaces. Selected project/local files must use the same version. Omitted configuration means package defaults, no lifecycle adoption authority. Explicitly missing input remains an error. No global namespace registry or shared parser is introduced.

Lesson 0.2.0 also reads v1 with the exact P2 closed Lesson-only envelope and constraints; new evidence-adapter fields require v2. ADR/promotion/PR/backlog require v2 for selected config files. This is an intentional old-tool compatibility limit: P2 Lesson rejects v2. No invocation or install edits configuration. An owner-authored version change is distinct from tool migration; automated conversion edges remain P6 work.

## D-P3-02: metadata v2 readable and writable schema identities

Select C334-02. Keep the metadata-v1 loader and closed fields. Metadata v2 changes only schema identity and project artifact-role readability:

- Schema resource identity is the exact `(id, version)` pair. Repeated IDs at different versions are allowed only for schemas; duplicate pairs fail. Resource paths stay distinct package-contained declared members. Schema IDs cannot collide with tool/template IDs; template/tool identities remain unique across their kinds.
- Every project role retains `schema` as its sole writable `id@version` and adds required nonempty unique `read_schemas` of declared exact `id@version` values, including the writable schema. No implicit highest-version choice, version range, fallback or conversion. Role ID is unique. Derived role fields are unchanged; their source must remain a declared project role.
- All other closed metadata fields, store/template defaults, operation ownership and exact member rules remain. No helper/member field, provider-owned artifact role or global registry.
- All five P3 packages use metadata v2. PR/backlog add one readable schema equal to the writable one; their operation/member counts do not change. Lesson declares legacy v1 read plus v2 read/write. Read support does not grant writes to legacy records.
- New owned schemas may use same-document `#/$defs/...` references. Resolve only inside the already selected document; reject external/remote/file references and unbounded resolution. This is not permission to execute schema validation during P3.

#337 implements shared distribution support; package workers implement their own metadata readers. Distribution never imports or invokes package tools. Existing v1 consumer behavior remains available.

## D-P3-03: lifecycle and standards promotion

Select #334's Lesson v2, ADR lifecycle and independent standards-promotion owner. Preserve the existing v1 Lesson schema blob `8bced2d86584c87d34f8ca2927aab95b7802a3ac` and existing record bytes. Explicit derive creates a new identity, resets decision state and preserves source evidence; it is not migration. Keep cross-skill dependencies empty.

Promotion produces one-file replacement proposals and observes actual adoption, target bytes and declared effect independently. It never applies a project rule or creates its own approval evidence. Project-local mapped evidence has the disclosed ownership/access trust basis; actor strings are not authenticated identities. Keep unresolved observations visible. Required actual execution or enforcement cannot be inferred from a declaration.

Correction to the proposal wording: when adoption has ever been observed, revise remains blocked. Resolving conflicts then requires a NEW proposal identity and new matching adoption, not a revision of the adopted proposal. Clarify this consistently in the owned contract/operations. Preserve unrelated known observations even when another dimension is unresolved. Do not add a generic authority engine or provider adapter to this slice.

## D-P3-04: independent work-management and GitHub operations

Select #335's independent local-backlog and PR packages with its 8/10 exact members. `pr.github` is a second package-owned public tool, never a helper field or mandatory separate skill. Both use config v2 and metadata v2 as above. Local backlog is the sole writer of its selected local items; provider links are reference-only and do not reactivate this repository's legacy backlog.

Select WM-C3 coordinated single-writer provider create/update with exact expected-state preflight and actual post-read. Explicitly require that operating mode; a caller requiring server-enforced CAS receives unsupported. A caller-supplied mode or grant reference is not proof of coordination or human permission. No tool credential/approval engine, blind retry, fabricated rollback or claim of undetectable concurrent-write safety.

The [GitHub conditional-request documentation](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api#use-conditional-requests) says unsafe methods are unsupported unless specifically documented; the [PR update endpoint](https://docs.github.com/en/rest/pulls/pulls#update-a-pull-request) does not document a conditional PATCH contract. These are documentation findings, not provider trial evidence. Git's [attr-source documentation](https://git-scm.com/docs/git) supports selecting committed attributes; source handling must pin/reject remaining ambient inputs as proposed. Provider write authority, artifact content and real execution observations stay separate.

## D-P3-05: source ownership and sequence

| Issue | Exclusive implementation ownership | First local return |
| --- | --- | --- |
| #334, same task | src/skills/lesson/, src/skills/adr/, src/skills/standards-promotion/; own knowledge-lifecycle design and workflow | Three complete package source sets with exact member/operation list, compatibility limits and deferred checks |
| #335, same task | src/skills/pr/, src/skills/local-backlog/; own work-management design and workflow | Two complete source sets and package-owned GitHub adapter with exact members/operations and deferred checks |
| #337, new independent task | src/distribution/package.py and necessary direct src/distribution/ call sites; distribution-implementation design; own p3-distribution workflow | Metadata-v2 source support; keep Issue/workflow in progress until later actual package mappings |
| Coordinator | This shared contract, coordinator workflow, shared indexes, integration and first push | Reconcile actual deliveries, then assign #337 final exact manifest/profile mapping in the SAME task |

Package/member proposals: #334 interface-proposal.yaml and #335 integration-proposal.json. They are expected inventories, not evidence of built/installed files. #337 must not add manifest/profile entries for absent implementations. After source return, coordinator integrates package commits and supplies that concrete subject to the same #337 task for final mappings. No broad shared runtime, legacy validator rewrite or root runtime/core/config cutover. P5/P6/P7 retain their existing later responsibilities.

Only direct content/syntax/reference/Git inspection and exact planned message validation are allowed under U001. No product CLI even --help, build, tests, schema validation, migration/install trial or CI execution. Record all such verification deferred-by-owner to program #322/P7. Return coherent local commits before push; preserve these referenced checkpoints.
