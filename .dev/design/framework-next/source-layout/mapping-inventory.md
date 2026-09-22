# Source and output mapping inventory

## Evidence used

This is a manually curated transition inventory for #326, not a generated complete per-file migration manifest. Baseline: `53c9c8e58615e87e36f7b74ea8851fe845312daa`; inspected 2026-09-23. Evidence: tracked paths and direct reads of the skill registry, distribution README/profile, ownership registry, governance templates, Lesson README/template/index, root entry and U001. No symbol/code-graph discovery or code relationship claim was needed for this document/config inventory.

Reproduce the bounded path observations with `git ls-tree -r --name-only 53c9c8e58615e87e36f7b74ea8851fe845312daa -- src .ai/assets/skills .ai/assets/shared .ai/assets/templates .ai/assets/tech-stacks .ai/distribution .dev/lessons .dev/standards .agents .claude`. Open the named evidence below to resolve content. Group rows describe handling, not permission to move every descendant. Workflows, assessments, releases, backlog history, code bodies and tests were not exhaustively inventoried.

Current `src/readme.md` is a tracked placeholder (one byte in this checkout), not a working product layout. The skill registry contains no Lesson skill entry. Current Lesson knowledge combines a reusable template, project lifecycle/history, and actual records. These need separate ownership dispositions.

## Classification summary and mapping

| Current input/group | Classification | Proposed source / installed output | Disposition/phase |
| --- | --- | --- | --- |
| `.dev/lessons/templates/lesson-template.md` | Reusable template candidate with project lifecycle assumptions | Adapt to `src/skills/lesson/templates/lesson.md` -> `.ai/core/skills/lesson/templates/lesson.md` | P2 extraction reconciled with P1-A schema; no blind copy of authority/link assumptions |
| `.dev/lessons/README.MD` | Portable concepts plus source history/rules/reference topology | Selected concepts in Lesson `SKILL.md`/references; source-specific remainder stays project-owned | P2 bounded extraction, never whole-file shipping |
| `.dev/lessons/INDEX.MD`, category indexes and actual `LESSON-*.md` | Project knowledge/navigation | Preserve current or explicitly configured project store | No distribution or P2 record migration |
| `.ai/assets/skills/<id>/skill.yaml` and owner-local assets | Reusable capability source, possibly source-coupled | Per-skill reconciliation to `src/skills/<id>/` -> `.ai/core/skills/<id>/` | P5 selected components; replace former canonical entry at cutover |
| `.ai/assets/skills/ai-context-release-closeout/` | Source-only historical/exceptional release maintenance | Source maintainer tools/docs if separately scoped | Never downstream; preserve historical contracts |
| Other `ai-context-*` skills | Mixed portable maintenance/source governance | Optional `src/skills/<id>/` for retained portable operations | P5 split; none required by Lesson |
| `.ai/assets/shared/` | Reusable contracts mixed with broad governance | Demonstrably necessary primitives to `src/shared/` -> `.ai/core/shared/` | No shared package by default in P2; classify remaining contracts in P5 |
| `.ai/assets/tech-stacks/dotnet-backend/` | Stack-specific assets | Later selected profile-owned assets under `src` | P5 explicit destinations; no all-.NET common bootstrap |
| `.ai/assets/templates/` and skill templates | Reusable template candidates | Owning skill's `templates/` | P5 actual producer/consumer classification, no universal dumping ground |
| `.ai/assets/sub-agent-role-prompts/` | Reusable/private roles with possible governance coupling | Retained owner-local/shared selected resources in `src` | P5 review; no role selected by first Lesson |
| `.ai/scripts/` | Mixed skill tools, primitives, build/release/validation | Consumer tools to owning `src/skills`; justified primitives to `src/shared`; maintainer orchestration to `tools/` | P5/P6 per-operation classification; P7 validator/test redesign |
| `.ai/distribution/profiles/dotnet-backend.yaml` | Broad source packaging policy | Narrow `src/distribution/manifest.yaml` and selection profiles | P2 first Lesson; P6 old machinery disposition; no inherited mandatory lifecycle core |
| `.ai/distribution/identity-registry.yaml` and historical package schemas | Public/source identity and old protocol evidence | Retain until P6 defines mapping and historical read boundary | No silent identity rename or old compatibility promise |
| `.ai/assets/shared/PRODUCT-SOURCE-PROJECTION-CONTRACT.md` | Current source/projection authority | One-owner concepts inform new design | Active until scoped replacement; not copied into first package |
| `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml` and standards | Source registry/governance; some portable semantics | Governance stays project-owned; extracted meaning gets a selected `src` owner | P5 preserve existing semantic IDs, no path-derived re-identification |
| `.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml` | Framework-source execution selection | Source project governance | Excluded from downstream |
| `.ai/assets/skills/ai-context-init/templates/public-root/AGENTS.md` | Optional reusable initial seed | Later initializer/installer source template if selected | Seed suggestion only; root project AGENTS is never the generic template |
| `.agents/skills/`, `.claude/skills/` | Derived runtime entries | Exact entries from `src/adapters` plus installed skill identity | P2 Codex only; later adapters explicit; preserve custom/unknown entries |
| Root `AGENTS*`, `CLAUDE.md`, `README*` | Project entrypoints | Project-owned installed-artifact references | Coordinator's P2/P6 pointer changes; no whole-file overwrite |
| `.dev/adr/`, `.dev/backlog/`, `.dev/workflows/`, `.dev/assessments/`, `.dev/releases/` | Decisions/tracking/history | Retain authority and references | Excluded; no mass migration/history rewrite; frozen backlog stays frozen |
| `.dev/ai-context/` | Project customization/provenance/local state | Reconcile individually into configured bindings | P6 export/classification; unknown custom structures not auto-converted |
| `.github/`, future `tools/`, `tests/`, `docs/` | Source operations/tests/product documentation | Source-side unless a specific reusable document is deliberately owned under `src` | No implicit shipping; P7 test/CI remains deferred |
| Proposed root `.ai/core`, `.ai/custom`, lock, `dist` | Installed outputs/config/scratch | Not source/build inputs | P2/P6 creation; none created by P1-B |

## Bounded initial move and creation list

This is a P2 proposal ceiling, not work performed by #326. The coordinator aligned the exact P1-A specimen names under `.dev/design/framework-next/portable-contracts/lesson/`: stable ID `lesson`, record family `lesson.record` version `1.0.0`, schema `schemas/lesson-record.schema.json`, template `templates/lesson.md`, references `references/configuration.md` and `references/operations.md`, and planned tool `lesson.fs` with null entrypoint. Both dependency lists are empty. Cross-review matched the metadata/configuration files to P1-A commit `c3891615f97625e7c59cd871abea3c2b27b5021f`; the six-member mapping includes both references. The selected project configuration is JSON under P1-A. No speculative executable fills the tree; implementation tools add explicit members later.

| Operation | Proposed target/input | Boundary |
| --- | --- | --- |
| Create canonical capability entry | `src/skills/lesson/SKILL.md` | P1-A capability plus selected portable Lesson concepts; no required governance/workflow |
| Create metadata | `src/skills/lesson/skill-package.yaml` | #325 field contract, `required=[]`; no parallel schema |
| Adopt first schema member | `src/skills/lesson/schemas/lesson-record.schema.json` | Exact P1-A name; adopt #325 content without a second schema owner |
| Extract/adapt template | `.dev/lessons/templates/lesson-template.md` -> `src/skills/lesson/templates/lesson.md` | Supported fields only; preserve records; retire old reusable ownership at cutover |
| Adopt configuration contract | `src/skills/lesson/references/configuration.md` | Exact P1-A member; JSON config semantics stay with #325 |
| Adopt operation contract | `src/skills/lesson/references/operations.md` | Exact P1-A member; tool `lesson.fs` stays planned/null until implementation |
| Implement filesystem operations when authorized | File path selected by P2 and added explicitly to metadata/manifest | No `scripts/lesson.py` placeholder is packaged; explicit project/config roots |
| Add one runtime template | `src/adapters/codex/skill-entry.md.template` | Exact prefixed runtime entry routes to installed core |
| Add selection/mapping | `src/profiles/lesson-minimal.yaml`, `src/distribution/manifest.yaml` | Same closure for stable/development; P2 development candidate only; no repo copy |
| Add maintainer invocation if needed | `tools/build-development.py` | Orchestrate manifest; no hidden consumer behavior or second manifest |
| Install/wire root | Selected `.ai/core`, `.ai/framework.lock`, `.agents/skills/framework-lesson/SKILL.md`, `.ai/custom/framework.json`, reviewed root pointer | Coordinator adopted tracked stable core/lock/runtime and copied Codex entry; P2 only development. Root/shared/tracking/ignore edits remain separately owned; none here |

## Boundary hotspots and later inventory

1. P2: split first Lesson portable entry/template from project knowledge. Preserve legacy records without claiming conversion. Switch reusable entry only when candidate/runtime pointer agree; `src/readme.md` navigation can change within that slice.
2. P3/P4: add ADR/Lesson operations, promotion, PR/backlog/provider and workflow owners. Each capability owns its schemas/tools; configured stores never become package sources. Each record/store has one writable authority.
3. P5: inspect existing skills/references/roles/stack assets/tools for hidden `.dev`, source policy and other skill-private dependencies. Extract portable content, preserve project rules, retire old product ownership explicitly. Group rows are not migration or deletion authorizations.
4. P6: reconcile old installed/custom paths, affected config/record versions and distribution identity. Produce operation-specific export/seed/convert/preserve/unsupported decisions and paired recovery. Retain originals where no active consumer requires conversion. No all-version upgrade engine is assumed.
5. P7: design/exercise focused checks, actual install, collisions/drift and recovery; then review CI restoration. This inventory provides no runtime acceptance evidence.

## Deferred items

No relocation, package acquisition/build, install, migration, runtime activation, cleanup, benchmark, suite or legacy validator was executed. Exact #325 names are aligned by coordinator read-back; final field-semantics cross-review belongs to integration. Whole replacement is a managed-content property; conversion is a separate owned operation with paired backups in [design.md](design.md).
