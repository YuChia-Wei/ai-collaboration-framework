# Artifact and format ownership proposal

Status: design only. [95 exact rows](legacy-artifact-dispositions.json) retain original kind, ordinal, baseline refs, model paths, owner, authoring label, producers, validators, readable/writable/migration limits and applicability. Every row has an explicit proposal_ref to its complete reader/writer/validator/version/migration group contract; shared text is stored once without losing kind identities. Model Git blobs and SHA-256 pin implicit Markdown/Python formats too. Schema-definition versions are not inferred as record versions.

## Legacy families

| Group | Count | Proposed boundary | Future responsibility |
| --- | ---: | --- | --- |
| F01 | 9 | Execution/authority packets preserve-unsupported | P7 selects guardrails; authorization remains semantic, leases actual custody. |
| F02 | 1 | Optional local CLI route deferred | P8 operator/runtime owner; no automatic config write. |
| F03 | 3 | Source role/provider catalogs | Source maintainer; no downstream registry. |
| F04 | 12 | Validation/provider observations preserve-unsupported | P7 actual execution/reuse; no template-generated passes. |
| F05 | 3 | Optional project context records deferred | P5-M2 selects need; ordinary use independent. |
| F06 | 4 | Legacy config/provenance replaced-preserved | P6 new config/install identity; target owns decisions. |
| F07 | 14 | Legacy upgrade/apply transactions retired-preserved | P6 new contract; original owner recovers active old transactions. |
| F08 | 8 | Workflow/external execution replaced-preserved | P4 #341 owns source/design/version. |
| F09 | 1 | Optional dotnet example evidence | Technology owner; no general requirement. |
| F10 | 5 | Source/external EngineeringGuardrails formats | Provider owns compatibility/execution/readiness; source owns selection/contract. |
| F11 | 10 | Source distribution/release | Source maintainer; no portable history. |
| F12 | 5 | Source evaluation | P7 separates corpus/mutants from actual results. |
| F13 | 10 | Source policy/catalog/history | Source/P7; #274/#275 separate. |
| F14 | 4 | Old metadata/registry replaced-preserved | Per-package source and explicit selection; no generic registry/converter. |
| F15 | 1 | Optional assessment persistence | P5-M1 concrete format/tools; conclusions semantic. |
| F16 | 4 | Project prose and problem-frame artifacts | P5-A1 prose, P5-A2 selected structured contracts. |
| F17 | 1 | External runtime preserved | Provider format authority; selected adapter only. |

These total 95 kinds, not schemas. Proposed source-only count 33 is a new responsibility grouping, not old applicability count 34. A historical portable label does not force shipping. External format authority does not transfer to this repository. Unsupported history stays inspectable; it is not deleted, converted to current truth or silently resumed.

Retained active source formats keep their original model/producer/validator from each observed row until explicitly replaced. P7 selects whether/how checks return. P5 implements no new readers/writers and claims no universal legacy readability. New unsupported consumers must report the original format/version and leave bytes intact. Frozen model blobs establish the selected legacy contract identity where no independent record version exists.

## Current src record schemas outside the legacy inventory

[Exact paths, versions, roles and operations](current-src-formats.json) bind all five actual source packages. Runtime verification remains deferred.

| Format | Reader | Writer | Validator owner | Version/migration |
| --- | --- | --- | --- | --- |
| lesson.record@1.0.0, lesson/schemas/lesson-record.schema.json | Lesson 0.2 inspect/query/validate/render, derive input | No 0.2 in-place v1 writer | lesson.py validate_record/legacy_semantics + frozen schema | Read-only legacy; derive creates new v2 identity, not migration. |
| lesson.record@2.0.0, lesson/schemas/lesson-record-v2.schema.json | inspect/query/validate/render | create/revise/derive/accept/retire/supersede | lesson.py structure/state/evidence checks + schema | Exact v2; unknown unsupported; no conversion. |
| adr.record@1.0.0, adr/schemas/adr-record.schema.json | inspect/query/validate/render | create/revise/derive/decide/retire/supersede | adr.py validate_record/decision/state + schema | Exact v1; preserve unknown; no conversion. |
| standards-promotion.record@1.0.0, standards-promotion/schemas/promotion-record.schema.json | inspect/query/validate/render | propose/revise/withdraw/supersede/reconcile | standards_promotion.py validate_record/observation interpretation + schema | Exact v1; adoption/effect evidence external; no automatic rule application. |
| local-backlog.record@1.0.0, local-backlog/schemas/local-backlog-record.schema.json | inspect/query/render | create/revise/transition | local_backlog.py validate_record on operations; no standalone validate operation declared | Exact v1; no conversion/provider sync or legacy backlog reactivation. |
| pr.record@1.0.0, pr/schemas/pr-record.schema.json | inspect/query/render; adapter candidate read | prepare/revise | pr.py validate_record/subject checks + schema | Exact v1; provider effect separate from local authoring; no conversion. |

Project owns records. Package owns structure/lifecycle tools; installer does not rewrite records when replacing managed files. Same-document schema references are structure, not executed compliance. No universal registry owns these families.

## Other closed and generated formats

N01-N16 are report navigation IDs, not new runtime kinds.

| ID / format/version | Source/owner | Reader, writer, validation and migration |
| --- | --- | --- |
| N01 skill-package integer metadata 1/2 | distribution/package.py:load_package and package-local readers; package author | Author writes; loaders read closed fields and check resources. Unknown rejected; no automatic conversion. Proposed 3 is D342-01 only. |
| N02 project/local JSON config integer 1 | lesson.py:config and references/configuration.md; project | Closed Lesson-only namespaces. Local forbids constraints. Package parser reads/checks; project writes. Preserve; unimplemented M01 is 1 -> 2. Legacy YAML project-config is different. |
| N03 project/local JSON config integer 2 | Five package-owned config functions; selected D-P3-01 | Project roots config_version/skills/constraints; local config_version/skills only. Namespace envelope checked globally, selected namespace deeply read. No shared parser/registry or installer edit. Selected project/local versions must match. |
| N04 selected settings/constraints, package-version-bound | Each references/configuration.md and settings/config/Binding | Project writes, selected package reads. Store leaves merge, template replaces atomically; invocation > local > project > defaults. Lesson/ADR decision_sources, promotion evidence targets, PR provider settings and backlog namespace stay isolated. Unknown own keys fail; foreign objects inert. No permission union or implicit conversion. |
| N05 manifest integer manifest_version 1 | src/distribution/manifest.yaml; selection.py:select | Shared distribution owner writes, select reads/checks collisions/ownership/exact members. Current mapping incomplete; #337 owns it. No globs/autodiscovery/migration. |
| N06 profile integer profile_version 1 | src/profiles/lesson-minimal.yaml; select | Coordinator-selected shared owner writes; exact package versions/adapter selection read and checked. No version solver or auto-upgrade. |
| N07 adapter template, Git-blob-bound unversioned text | src/adapters/codex/skill-entry.md.template; codex.py:project_entry | Shared author writes; six placeholders runtime_name, description, package_identity, installed_entrypoint, installed_metadata, resources. Parser checks exact placeholders/contained links. No schema needed; regenerate from selected inputs. D342-01 needs operation-neutral wording. |
| N08 generated Codex entry Markdown/frontmatter | project_entry + package.py:check_references | Actual adapter writes, runtime reads; selected metadata binds generated path/digest. No hand edits/reverse migration. Preserve user-owned files/collisions. Expected links are not installation evidence. |
| N09 metadata/selection.json integer schema_version 1 | assembly.py:assemble; distribution owner | Actual builder writes development mode, null release_version, source, exact components/dependencies/adapters/build inputs/generator. P6 reader still to be selected; no current installer claim. Regenerate from actual inputs; no release relabel. |
| N10 metadata/files.json integer schema_version 1 | assembly.py and selection.py:Member.identity | Builder writes exact path/destination/owner/kind/mode/size/hash/source inventory; read-back binds bytes. Future P6 consumer needs checks. Distinct from legacy package-files schema; regenerate, no historical conversion. |
| N11 metadata/build.json integer schema_version 1 | assembly.py:assemble | Actual completed builder writes outcome/identity/runtime/materialization last. P6/P7 future consumers; marker alone is not install/behavior. No marker produced here, no fabricated result or conversion. |
| N12 operation request JSON, package-version-bound | scripts execute/main and operations references; pr/github.py | Caller supplies closed operation-specific fields, owner parses/checks. Semantic content/grant/evidence comes from real authority. No universal request schema or cross-package conversion. |
| N13 result/query/diagnostics/rendered views, package-version-bound | scripts main/execute/query/render | Only actual operations produce digests/state/observations/partial failures. Caller reads. Markdown is derived, not record input. No edited success or synthetic history; regeneration requires actual invocation. |
| N14 Markdown view templates, package/project-owned | src/skills/*/templates/*.md; render/validate_template | Author writes, owning renderer checks supported tokens and escapes output. Preserve custom templates; unsupported tokens fail, no silent migration or generic templating engine. |
| N15 external mapped evidence / GitHub projection | Decision/adoption/effect adapters; pr/github.py:projection | Project/provider owns facts/source format. Package reads exact pointers/digests, checks mapped fields, records observation; never authors approval. Projection/expected_state_sha256 is not provider truth or server CAS. No generic migration of external facts. |
| N16 lock/temp/replacement/directory observations, implementation-bound | Package Writer/local_write_backend and distribution OwnedDirectory | Active invocation owns transient writes/cleanup. No migration or generic janitor. Stale/interrupted state requires owning recovery; presence does not authorize deletion. |

N09-N11 are closed source output constructions, not independently verified general-purpose readers/schemas. Future readers must implement exact version handling before claiming compatibility. Package-local validation exists in source but has not run here.

L96, supplemental legacy omission: diagnostic-analyst/references/output-contract.md defines closed JSON diagnostic schema_version string 1.0, with scripts/validate-diagnostic-record.py as reader/validator. Semantic author supplies hypotheses and actual observations; no mechanical writer can invent incident facts. P5-R2 may port a useful validate operation; prose remains schema-free. Preserve history, unknown versions unsupported, no conversion. This is not a 96th registry row.

## Evidence boundaries

A declared producer is not executable coverage. Semantic-owner and external may be correct dispositions. Approval, execution, compatibility and provider facts require real inputs. Plain prose may stay unversioned; one kind may span documents or share schema. Source history does not ship by historical portable label. P6 adoption and P7 verification remain pending even for actual P3 source; failures/unsupported are never collapsed into passed.

Subsequent dependency state: [P3 integrated mapping and P4 selected contract](dependency-update.md). Baseline inventory remains pinned; P4 source is not yet delivered.
