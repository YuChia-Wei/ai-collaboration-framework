# Project skill management

## Authority and fixed start

The owner explicitly requested completing the sub-agents merge first, then
revising online Feature #482 to use the solution established by that work before
implementing skills. PR #488 is merged at
`1f473ecdb5a7544233299dd69bc6376a43a6c912`; its tree matches PR head
`7ea3e60f5f09eaaaabe00a117a2c55b6dca7b909`, whose hosted Source change gate passed
in run `39824592118`. Local main was fast-forwarded and clean. The source CI is
PR-triggered; no additional main-commit CI run is inferred. Issue #487 remains
OPEN and its Project status remains Inbox; manual Antigravity analysis of the
separate preview is owner-pending.

The online #482 and #484 plans were rewritten on 2026-10-23 before source work.
Their former optional-manifest/design-only decision is superseded by the owner.
Current acceptance is Feature #482 F-AC01 through F-AC11; #484 preserves the
design contract and original AC mapping. The historical design files retain
their original meaning and are not overwritten.

Authorized here: Issue-plan reconciliation, local source implementation,
necessary tests, isolated consumer validation and independent review. The prior
#487 transport authorization has been fulfilled; this Feature does not silently
inherit push/PR/merge, publication, existing-project self-installation, custom
migration/deletion, Issue closure or Project mutation authority.

## Accepted design and bounded implementation

- Version-1 project-owned `.ai/project/skill-registry.json` and authoring under
  `.ai/project/skills/<id>/`, with coherent legacy-only layout support and a
  visible ambiguity error when both roots exist.
- Keep provenance, intent/acceptance, capability, complete member hashes,
  baseline bytes/ref, integration evidence/decision references and explicit
  purpose/adapter routes separate. Never add labels to the framework lock.
- A skill projection is a destination-relative member to authoring-member map,
  not the sub-agent manager's single native file. Require `SKILL.md` and matching
  frontmatter name; preserve references, templates, schemas, scripts and sibling
  modules without implicitly rewriting their imports or links. Adapter-specific
  entry sources may share declared resources. Initial support is bounded UTF-8;
  reject opaque/binary content before mutation and disclose that boundary.
- Use existing framework metadata/reference readers only when a project package
  declares supported framework metadata. Ordinary native project skills need not
  impersonate framework packages. Missing declared resources/hash drift blocks
  the selected operation; directory presence is not proof of discovery.
- Project routes verify full authoring and selected projection. Framework routes
  use canonical ID plus verified installed binding/owner and its actual original
  or prefixed entry name; do not guess the native directory.
- Compare baseline/local/candidate member unions, including additions/deletions.
  Missing baseline is unknown; coverage, proposal, adoption, mechanical apply,
  discovery and behavior remain distinct and evidence-qualified.
- Preserve managed drift/collision rules and all unregistered unknown content.
  Same-bytes unowned adoption requires explicit current hashes. Detach only
  selected registered matching files; retain the existing skill record, provenance
  and baseline while clearing selected projections/routes. Reject record deletion
  through plan/apply; never recursively delete a skill directory or authoring resources. Join `project_layout.writer`, publish registry
  last, resume only exact accepted plans and protect completed replay.
- Add source-owned `distribution.skill_registry` and pinned
  `src/tools/manage-skills.py`. Reuse existing low-level safeguards without a
  generic registry-platform refactor. Freeze the current 27-file engine closure
  alongside historical 23/25/26 closures; old artifacts remain readable, while
  new execution requires the complete new pin. Preserve old wrapper convention.
- Extend explicit legacy layout migration to registered skill references,
  projections and hashes rather than moving a directory with stale references.

A read-only Sol/medium semantic-governance subagent analyzed this adaptation
against the fixed start through the installed `ddd-ca-hex-architect` route.
It identified the multi-file projection, installed binding and legacy-migration
differences above; it made no implementation or acceptance claim. The parent
owns integration and all provider decisions. Use `slice-implementer` generic
mode for this coordinated behavior slice, with one tracked writer.

## Validation and delivery

Select focused tests for registry inspect/plan/apply/compare/route, references and
support-file closure, adoption/collision/detach, partial recovery and completed
replay, legacy layouts and historical artifact compatibility. Test fixtures use
resolved direct temporary roots, with an existing bounded RAM-disk scratch path.
Run broader distribution/schema/loader checks only for actually affected closure
or contracts. Do not rerun on identity-only record changes.

After a fixed source commit, run the actual packaged public CLI in an isolated
consumer with both native projections, representative install/update/deselection
protection, and full resource readback. For an available explicitly selected
runtime, obtain native discovery/resource-resolution evidence separately;
Codex/Claude remain separate, and unavailable native evidence is unverified,
never a file-derived pass. No account login or paid model test is implied.

Installation/ownership/recovery changes require independent scoped read-only
review of an immutable commit. Repair material findings and return only affected
changes for review. Record exact commands, failures and evidence limits in
validation.md. No preview rewrite is planned while the owner uses the #487
snapshot for manual analysis. Subsequent transport requires its actual authority.

## Completed local delivery

Implementation and selected local validation are complete at fixed source commit
`87b85018b32e43db1e705c33e7e54972cc1426eb`. Initial independent review identified
two P2 defects; the actual packaged consumer found an equal-lock migration bug.
All three were repaired. The affected 39-test run passed and independent repair
review reported both findings resolved with no new actionable defect in scope.

Actual pinned public CLIs exercised both native projections, explicit adoption,
original/prefixed framework routes, protected upgrade/deselection, legacy
migration, replay rejection, fresh repair, rename/coexist and precise detach.
Authoring, provenance, baseline, protected project files and unknown siblings
were preserved. See validation.md for source identities, commands, retained
failures, criterion-by-criterion coverage and evidence limits.

Codex native traversal failed on F: with os error 1. A second small consumer was
created through the same public manager in a verified ignored workspace folder;
Codex discovered its entry and read all seven resources with matching hashes.
No model turn was started. Claude native discovery and AI behavior remain
unverified, separately from mechanically verified Claude projections/routes.

The owner-requested #487 preview and manual Antigravity prompt remain unchanged.
Feature #482/#484 remain OPEN. Their earlier plan reconciliation is present;
fresh readback found that the later implementation-progress addition was not
published. Automatic approval review rejected both the complete progress update
and a concise addition through the full-body Issue API. The precise external
progress update requires renewed explicit owner approval; local work is complete.
No Feature #482 push/PR/merge, hosted CI, public
release, real-project self-installation or Project mutation has been performed.
The next owner-selected action may be transport and its required PR gate, or
additional runtime acceptance; neither changes this completed local work record
into an already integrated or published result.
