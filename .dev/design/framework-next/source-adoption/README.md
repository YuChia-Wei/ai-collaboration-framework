# Source repository adoption proposal

Issue [#361](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/361),
program #322; design only under [U001](../../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md).
Fixed inspected source: `b4a147c1bc8ec00fcdb92a7006c142209c61a29f`.
This proposal changes no active route, configuration, managed file, record or CI setting.
Source delivery, root adoption, verification and publication are separate outcomes.

## Review and continuation

1. [Path and owner matrix](path-dispositions.md): actual predecessors, exact successor
   bindings, active legacy scope and individual retirement conditions.
2. [Root, configuration and Git proposal](root-bindings.md): concrete future edits,
   tracking, templates and stores; [pilot config proposal](pilot-framework.proposal.json).
3. [Adoption, activation and recovery](adoption-and-recovery.md): staged execution,
   quiescence, separately owned backups, public-reader questions and dependencies.
4. [Local delivery report](../../../workflows/2026-09-23-source-adoption-design/reports/source-delivery.md):
   actual checks, failures, deferrals and receiving instructions.

## Selected design decisions

- First P7 pilot is exactly `lesson-minimal` / `lesson@0.2.0` / `codex`.
  It observes one installed capability in a separately selected project binding;
  even success cannot establish whole-repository adoption.
- Preserve `src/` as the sole editable reusable product source after each
  component's cutover. Installed core and generated runtime are consumption.
  Root entries and source governance remain project-owned.
- Propose a later source-repository selection of ten currently delivered ordinary
  packages (76 source members), excluding local backlog and optional maintenance.
  No existing profile expresses it. Profile authoring belongs to the shared owner.
  Five undelivered engineering capabilities remain explicit legacy dependencies.
- Preserve original records in place. New JSON collections use separate named
  project-owned directories; no historical record or approval is converted.
- New pilot configuration uses exact integer version 2. M01 stays **unassigned**:
  no actual P2 config 1 was observed at the explicitly inspected paths.
- Managed install recovery covers managed bytes only. Source, routes, configuration,
  project records and active old transactions have separate owners and recovery.
  Installer `project_readiness` remains `not-assessed`.

## Evidence used and limits

Inputs are the [assignment](../p6-source-adoption-handoff.md),
[execution plan](../../../assessments/ASM-20260923-00-6oq/execution-plan.md),
[source layout](../source-layout/design.md),
[portable contract](../portable-contracts/contract.md),
[P3](../p3-shared-contract.md), [P4](../p4-selected-contract.md),
[P5](../p5-selected-contract.md), [P5 final](../p5-final-capability-contract.md),
[P6 selection](../p6-selected-contract.md) and [writer assignment](../p6-writer-handoff.md).
Earlier specimens and proposals do not override actual package metadata.

Reuse #342's [16-skill inventory](../capability-consolidation/legacy-skills.json),
[95-kind / 17-group dispositions](../capability-consolidation/legacy-artifact-dispositions.json)
and [format ownership](../capability-consolidation/format-ownership.md).
They are pinned historical inventories, not current execution or a replacement registry.
Current Git/metadata observation confirms **13 packages / 90 members**, all with
empty required/optional skill dependencies; manifest currently maps **5 / 44**.
Package presence and direct parsing establish neither buildability nor behavior.

Actual handoffs: [distribution](../distribution-implementation/README.md),
[authoring](../portable-authoring/design.md),
[frame/compliance](../problem-frame-implementation/README.md),
[optional context](../optional-context-implementation/README.md),
[reader/planner](../installation-planning/handoff.md).
The distribution README describes its earlier eight-member Lesson; current
metadata/manifest select nine members for Lesson 0.2, including both record schemas.
The reader's six-file engine closure is not #359's final mutation closure.

Current observations cover root `AGENTS.md`, `CLAUDE.md`, selected README/index
route text, `.gitattributes`, `.gitignore`, tracked runtime entry names, package
metadata/profiles/manifest, named configuration and proposed collection paths.
No historical archive contents, recovery stores, other checkout, arbitrary config
locations or all legacy scripts/tests were scanned. No code graph claims are made;
this is direct non-code contract/Git inventory, not implementation discovery.
Live Issue #361 was read as OPEN; no other Issue/Project/CI state is asserted live.
See [source observation](../../../workflows/2026-09-23-source-adoption-design/evidence/source-observation.json).

## Deferred verification

All product CLI/help/import, schema validation, test/fixture/build/package/install/
migration/probe, independent audit/lease/effective-rule/acceptance packets and CI:
**deferred-by-owner**, authority **U001**, owner **program #322 coordinator / P7**.
Next action: integrate selected source, resolve inputs, choose and perform bounded
new-contract verification before activation. Direct syntax/reference checks are
not schema, behavioral, native durability or independent-review evidence.
