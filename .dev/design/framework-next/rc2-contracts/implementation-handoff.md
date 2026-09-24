# S2–S6 implementation interfaces and serialized ownership

S1 owns only this contract directory and its Issue #401 workflow. The contracts
are ready for dependent implementation after coordinator integration; no reader,
installation, adapter discovery or target adoption has occurred in S1.

## S2 content owner to S3 distribution owner

[package-members.json](package-members.json) is the exact initial member assignment:
`engineering-common@0.1.0` has 6 members; `dotnet-backend@0.1.0` has 229. Of the total
235, 232 map to individually identified source files; three are new package
metadata/index members. The profile root `README.MD` becomes `README.md`, preventing
a Windows case-alias collision with the selected entrypoint. The inventory includes
all 194 profile files, not merely a representative example set.

S2 owns `src/knowledge/engineering-common/` and `src/knowledge/dotnet-backend/` plus
its assigned records. It ports every declared reusable member, reconciles every
reference disposition and returns, for each package:

```text
{id, version, metadata_version: 1, entrypoint,
 members: [{path, mode, size, sha256, source_identity}],
 resources, required_dependencies, optional_dependencies, references,
 normative_rewrites: [{rule_id, source_text_sha256, installed_text_sha256,
                       link_rewrites, semantic_change: false}], unresolved: []}
```

This is a handoff shape, not the content-package disk schema. Use the latter from
[formats.md](formats.md) to write `content-package.yaml`. Exact destination maps are
already in the inventory. Semantic rules retain their IDs, original normative digests as source provenance,
override policy and applicability. Link-only rendering changes record both source
and new installed text digests plus exact link substitutions; they are not equal
byte identities. Regenerate catalog/file digests from actual relocated bytes. A
semantic change is outside this migration and returns to the coordinator. The three new members need an explicitly authored
index/metadata source, not fabricated historical provenance. New hashes are computed
from actual S2 bytes; old source hashes cannot be copied as new installed hashes.

No source execution override, target customizations or historical receipt becomes
portable active policy. Legacy role YAML in the member plan is reference-only
technical guidance: S2 removes dispatch/runtime activation clauses from that
projection and retains a source identity trail. Any normative meaning change or
required new member beyond the defined closure returns to the coordinator with the
exact delta; routine link repair and target-parameterization are S2's work. The
11 unregistered rules remain unregistered guidance. The 5 historical evidence files
and 4 obsolete forwarding entries remain explicitly retained/excluded.

S2 does not edit `src/distribution/manifest.yaml`, `src/profiles`, loaders or skill
consumers. It hands exact member rows to S3; S3 integrates them once, after S2's
commit is accepted. Resource proposals in the member file provide IDs, not a claim
that every operation loads every resource. S2 finalizes the corresponding declared
reference rows; S5 uses task-scoped lookup.

## S3 sole shared implementation owner

S3 owns `src/distribution/` except the two S4 renderer files assigned below, the
shared manifest/profiles, `src/tools/maintain_framework.py`, source builder/derivation
entry points and their immediate owned tests. It implements one semantic owner for
content metadata, parent catalog, selected subset and both installed-lock branches.
Filesystem input and retained recovery objects must call that same semantic reader.
Do not reproduce a more permissive parser for recovery, runtime projection or CLI.

Required interfaces (new contracts, names reserved here for S3):

| Function | Input | Output and side effect boundary |
| --- | --- | --- |
| `load_content_package(blob)` | Verified YAML source blob | Closed ContentPackage plus declared member/resource/dependency/reference sets; no execution |
| `read_catalog(root, expected_identity)` | Explicit artifact root and immutable parent pin | Verified catalog metadata/raw bytes/member index; bounded complete closure; no source checkout |
| `resolve_selection(catalog, desired)` | Verified catalog and parsed Selection 1 | Exact selected typed components, adapter inputs, binding observations, desired digest and unavailable optional references; no implicit writes |
| `expand_preset(catalog, id, version)` | Exact catalog and named versioned preset | Explicit desired ID arrays plus expansion provenance; saving remains caller-directed |
| `derive_subset(catalog, desired, output_root, scratch_root)` | Verified inputs and explicit disjoint roots | Complete new subset 3 plus exact identity and raw metadata; no install or target config edit |
| `read_candidate(root)` | Legacy or subset artifact | Discriminated verified result; legacy selection 1/2 or new 3, never field coercion |
| `read_lock(project_root)` | Existing installed raw lock | Absent, legacy lock 1 or new lock 2; absence grants no ownership |
| `plan/apply/recover` | Closed API version 2 request and independently pinned engine 2 | Existing safety contract plus selected catalog/knowledge/adapter/project-edit transition |

Existing call sites to update serially: `selection.select` currently accepts a
source profile and `assembly._assemble` invokes it; `assembly.assemble` and
`assemble_versioned` remain legacy entry points. `tools/build-development.py`
and `tools/build-candidate.py` keep their legacy invocation meanings; in particular,
`--profile` never becomes an implicit catalog/subset selection.

Preserving old invocation outcomes means the original pinned source/engine and
API 1/old builders retain their original behavior. A new implementation's legacy
mode accepts only the already supported manifest 1, profile 1 and skill metadata
1/2/3 shapes. A rc.2-only source shape, manifest 2, preset 1 or request requiring
metadata-4 output returns `unsupported` / `unsupported-write` before output
allocation. It must not strip new fields or reinterpret the request. There is no
promise that a newly adopted manifest 2 can still produce rc.1 through an old
writer. Explicit catalog/derivation entry points select the new branch. The graph
trace did not enumerate these callers reliably; tracked call sites were read directly.

`installation_state._selection_inventory`, `_candidate_documents`, `_packages`,
`read_candidate`, `_lock_bytes` and `_engine_shape` are the current shared semantic
choke points. `installation_plan.member_delta`, `is_noop` and `_prepare` consume
their exact descriptors. `installation._bundle`, `_read_operation`, `_capture`,
`_transition`, `apply`, `recover` and `execute` must preserve the same verified-byte
closure for new metadata and paired recovery. The bootstrap's `ENGINE_FILES`,
verified source importer, allowed engine identity and operation protocol must move
together with any new module. Preserve isolated `-I -B` execution and no ambient
import fallback. The engine-1 historical six-reader-file subset is not a writer pin.

API 2 uses the same four operation names and original base fields
`api_version`, `operation`, `project_root`, `engine_root`, `engine`. Exact additions:

| Operation | Closed additional fields |
| --- | --- |
| inspect | Optional `candidate_root`; no config writes or installation selection discovery |
| plan | Existing API-1 plan fields plus required `project_edits` (possibly empty) |
| apply | API-2 plan fields plus `expected_plan_sha256`, `maintenance` |
| recover | Existing recovery fields; exact `operation_root` and `operation_sha256` choose retained protocol; no new desired selection or project edit list may replace recorded intent |

The existing plan fields are `candidate_root`, `candidate_identity`,
`expected_lock_sha256` (null means absent), `mode_policy`, `scratch_root`,
`staging_root`, `recovery_root`, `durability`, `protected_inputs`,
`project_data_action: none`. Durability and maintenance retain their closed
API-1 fields and explicit fresh quiescence declaration. `project_edits` uses the
closed intents in [compatibility-and-recovery.md](compatibility-and-recovery.md).
API 2 plan pins these intents, all raw authority/config inputs and both identities.
The old API 1 must reject project_edits and any new format; there is no permissive
extra-field compatibility mode. S3 owns the exact operation/journal 2 shape needed
to retain these pre/post states, publishes it before S5/S6 use, and preserves
read-only/recovery support for existing operation 1 through its original engine.

## S4 adapter owner and S3 integration seam

S4 owns `src/adapters/codex/`, `src/adapters/claude/`,
`src/distribution/codex.py` and new `src/distribution/claude.py`, plus directly
assigned adapter tests. S3 reserves those paths and owns imports/dispatch/manifest/
profile/closure changes in all other distribution files. The coordinator serializes
handoff; S4 must not edit S3 shared files in parallel. If a shared helper is needed,
S4 returns its exact proposed bytes/path and S3 integrates it.

S1-R1 separates the legacy seam from the new rc.2 seam. S4 preserves the existing
`src/distribution/codex.py::project_entry` output semantics and the exact bytes of
`src/adapters/codex/skill-entry.md.template`. Neither becomes an alias or a forwarder
to v2. Add `project_entry_v2` in both renderer modules with the same parameter and
return shape:

```text
project_entry_v2(template_bytes: bytes, package_id: str, package_version: str,
                 description: str, destinations: dict[str,str],
                 *, configuration: dict | None) -> tuple[str,bytes]
```

| Explicit branch | Renderer source and callable | Exact template source | Runtime output |
| --- | --- | --- | --- |
| Legacy selection 1/2, lock 1 and supported legacy assembly | `src/distribution/codex.py::project_entry` | `src/adapters/codex/skill-entry.md.template` (preserved) | `.agents/skills/framework-<id>/SKILL.md` |
| rc.2 subset selection 3, Codex | `src/distribution/codex.py::project_entry_v2` | `src/adapters/codex/skill-entry-v2.md.template` (new) | `.agents/skills/aicf-<id>/SKILL.md` |
| rc.2 subset selection 3, Claude | `src/distribution/claude.py::project_entry_v2` | `src/adapters/claude/skill-entry-v2.md.template` (new) | `.claude/skills/aicf-<id>/SKILL.md` |

S3 owns explicit format/API dispatch at callers, manifests and engine-closure
boundaries. Adapter ID alone cannot choose a renderer: an API-2 reader checking a
legacy candidate/lock still selects legacy verification semantics, not v2. Legacy
generation and any projection reconstruction/verification use the preserved
legacy seam/template; catalog/subset derivation and new projection verification
use v2 with that catalog's verified new template. There is no legacy Claude branch.
Reject a mismatched renderer/template/format combination; do not fall back or
select a branch from a filename prefix. New manifest-2 adapter rows name the new
package-relative template `skill-entry-v2.md.template`; old branch mappings keep
`skill-entry.md.template`. S3 updates exact generator/engine closures and callers
without treating a changed module hash as the historical pin.

`destinations` contains only that selected skill's actual installed declared
members. Knowledge is accessed through the skill/selection binding, never by adding
unselected content links to this dict. Only the two v2 renderers use fixed `aicf-`
and their respective runtime roots. The new templates use exactly the existing
seven substitution keys: `runtime_name`, `description`, `package_identity`,
`installed_entrypoint`, `installed_metadata`, `configuration_guidance`, `resources`.
New instructions belong in the new templates; the legacy template remains unchanged.
No arbitrary template execution, provider calls or capability activation. Description
is escaped as a scalar; links resolve relative to the emitted entry. Metadata 4
instructions explain optional knowledge availability without a legacy dependency.

S4 returns `{adapter_id, version: 0.1.0, prefix: aicf-, template,
 members:[{path,sha256,size,mode}], renderer_path, renderer_callable: project_entry_v2,
 renderer_sha256, expected_output_path_rule}` for each new adapter to S3, plus the
retained legacy callable/template mapping and original source identities. It defines
exact runtime metadata and returns isolated projection examples. S3 derives and verifies new wrappers through
v2, with complete pinned renderer/template inputs, while preserving old branch
semantics. S3 owns old lock/new-name migration admission; S4 does not remove old
runtime directories. Actual Codex and Claude discovery/routing remain distinct S6 evidence.

## S5 consumer and adoption split

S5 first owns affected `src/skills/<id>` method/metadata changes. It uses
`knowledge_consumption` metadata 4 only when necessary, raises affected component
versions, and returns exact changed member/operation/dependency rows to S3. S3 alone
updates shared manifest/catalog/presets after those rows stabilize. Optional
knowledge must not turn all generic skills into mandatory .NET consumers.

The source's 21 capability identities (16 active legacy, 18 delivered packages,
13 overlapping) and retained duties are exhaustive in
[source-capabilities.json](source-capabilities.json). Source adoption selects all
18 delivered skill IDs, zero knowledge packages and explicit adapters; it must
reconcile each old operation and both discovery surfaces. Three old IDs—init,
upgrader and release-closeout—retain named owners. Partial legacy assessment,
workflow, SWF, target gate and release duties also remain explicit. Do not drop
those duties because a small illustrative profile omits them.

Actual source adoption and actual mq-lab adoption are separate coordinator-owned
assignments/worktrees/authority. Their owners submit explicit root/config/index/
withdrawal intents and recovery preimages to S3's transition contract. No S1/S2/S4
writer edits those targets. S5 target integration preserves all 20 route selectors,
14 rule meanings and original baseline digests plus four customizations before any old route is retired.
The existing target gate must accept the new exact candidate/engine/binding under
its own reviewed authority; U001 cannot waive that target gate. Real package use
is required for source dogfood, beyond installed-file inventory.

## Narrow S6 selected acceptance cases

All execution below remains `deferred-by-owner` in S1 (program #322 coordinator/P7).
S6 must choose the actual immutable candidate/engine and record each evidence kind.

| Case | Narrow observation | Evidence category |
| --- | --- | --- |
| S6-01 strict dispatch | Each new discriminator, one missing/extra field, bool/float version, duplicate ID/key; legacy versus v2 renderer/template selection; unsupported-write for rc.2-only input to a legacy builder | Focused fixture; not target adoption |
| S6-02 identity/subset | Same parent, source knowledge-empty vs mq-lab .NET selections; exact absent unselected bytes; tampered parent/subset/member denied | Focused fixture plus actual catalog read |
| S6-03 closure/binding | One required omission, optional unavailable, cycle/reference miss, stale target authority and unresolved specialist coverage | Focused fixture; real target semantics separate |
| S6-04 names/ownership | One unchanged framework-to-aicf transition, edited old entry, unowned new collision, case alias/hardlink/reparse refusal | Focused fixture/native where selected |
| S6-05 adapters/deselection | Codex-only, Claude-only, both and core-only; remove one adapter without removing shared core; dependency-bound package removal refused | Focused affected fixtures, no all-skill Cartesian matrix |
| S6-06 recovery | rc.1 lock 1 to subset/lock 2; interrupt at relevant core/runtime/lock/project-edit boundaries; restore exact paired state | Actual maintenance run with fixed identities; native limits explicit |
| S6-07 source dogfood | Real source work through installed selected skill with knowledge empty; retained source duties and single active runtime route checked | Actual source consumer evidence |
| S6-08 mq-lab route | Actual target gate and rule resolution, 14 rules/4 customizations/20 routes, unchanged EF/Dapper decisions, update and rollback | Actual target evidence plus separate target review |
| S6-09 Codex discovery | Discover and invoke one representative new entry plus affected prefix/config route; absent deselected entries | Actual Codex runtime evidence |
| S6-10 Claude discovery | Independently discover and invoke Claude entry; same selected core and distinct runtime metadata | Actual Claude runtime evidence |

Schema/example readability is neither a fixture test nor a runtime discovery pass.
A generated wrapper cannot establish either runtime's behavior. Fixture success
cannot satisfy actual source/target use. A rc.2 update cannot establish stable-input
upgrade, publication, cross-computer recovery, native driver/caller coverage or CI.
Failures remain beside subsequent results. #369 native/CI/policy restoration needs
its existing owner decision; this table does not enable it.
