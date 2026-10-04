# AI Context Boundary

This policy governs this framework source repository. The owner adopted the
source/project/product separation in Issue #435 on 2026-10-03. The
[source development policy](SOURCE-DEVELOPMENT-POLICY.md) governs execution,
review and integration. Target repositories retain their own placement policy.

## Framework Source Repository Exception

This repository develops the framework and consumes an installed copy. Editable
product sources and installed projections may therefore contain duplicate files.
Edit the source owner; duplication does not authorize editing managed outputs.

| Path | Owner and purpose |
| --- | --- |
| `src/skills/` | Reusable skill operations, resources and deterministic tools |
| `src/knowledge/` | Reusable cross-technology and selected-profile engineering knowledge |
| `src/sub-agents/` | Reusable bounded roles and their product-owned projections |
| `src/distribution/`, `src/profiles/` | Product packaging and explicit component selection |
| `.ai/core/`, `.agents/skills/`, `.claude/skills/` | Managed installed projections |
| `.ai/custom/` | This repository's installation selection and customization |
| `.dev/` | Source-project rules, decisions, records, collaboration and evidence |
| `docs/` | Human-facing product instructions, limitations and manuals |
| `releases/` | Source release identity and compatibility/support records |

## Source Resource Closure

Resources needed by an advertised framework capability belong inside `src` and
its component declarations. Declare required cross-package knowledge references.
Do not package source-project standards, provider bindings or execution records
as downstream rules. A reference to target facts must identify caller-selected
inputs; it must not require this project's private document names.

Historical source identities may remain inert provenance with a revision/digest
and an explicit historical meaning. They are not files to resolve at runtime,
package members or current authority. Do not infer a working legacy route from
an old filename, installed example, static provider profile or migrated record.

## Project Documentation And Cleanup

Keep source governance, project-specific guides and actual collaboration records
under `.dev`. Put product use, installation and authoring documentation under
`docs`. If a project document contains reusable capability knowledge, prepare
that knowledge in `src` first. Self-installation/upgrade is a separately selected
operation after the product changes are ready; do not hand-edit generated core.

Remove obsolete instructions without independent experience-transfer value.
Preserve useful reasoning, compatibility interpretation and actual support duties
with their owners. Existing `.dev/design`, `.dev/assessments`, `.dev/requirement`,
`.dev/adr` and `.dev/workflows` records are excluded from this cleanup. Do not
batch rewrite their history to resemble current guidance. Git can retrieve a
removed document at the recorded source revision; that does not make it current.

## Tool-Neutral Evidence Boundary

Rule ID: `AICTX-EVIDENCE-001`. The reusable rule owner is the engineering-common
catalog in `src/knowledge/engineering-common/engineering-rule-catalog.yaml`.
This project applies direct tracked evidence and source-policy checks. Graphs
and indexes accelerate discovery; verify their revision and coverage, and use an
explicit tracked-file fallback when stale or incomplete. Empty search results
alone do not prove absence. Record actual commands, exclusions and outcomes.

## Retained Source Duties

Source work authority, release/support, U001 and selected legacy obligations
remain project-owned. Keep existing compatible contracts and record meaning;
removed validators, resolvers and roots remain unavailable. This placement
change does not restore them or establish downstream/native acceptance.
