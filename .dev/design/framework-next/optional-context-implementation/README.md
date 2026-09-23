# Optional context package source implementation

Issue [#357](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/357)
of program #322 delivers source for the six members below. Authority:
[U001](../../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md),
[P5 final selection](../p5-final-capability-contract.md) and D352-01..06 in the
[selected design](../optional-context-maintenance/README.md), including its
[auditor draft](../optional-context-maintenance/drafts/ai-context-auditor/SKILL.md)
and [governance draft](../optional-context-maintenance/drafts/ai-context-governance/SKILL.md).
The source owner remains the existing governance route; the newly authored
portable package does not replace current source policy or runtime routing.

## Exact mapping handoff

| Package | Member relative to package root | Role |
| --- | --- | --- |
| ai-context-auditor | SKILL.md | Lightweight entry for audit/compare |
| ai-context-auditor | skill-package.yaml | Metadata 3, package 0.1.0 |
| ai-context-auditor | references/audit.md | Actual audit/compare and output methods |
| ai-context-governance | SKILL.md | Lightweight entry for propose/apply |
| ai-context-governance | skill-package.yaml | Metadata 3, package 0.1.0 |
| ai-context-governance | references/maintenance.md | Actual propose/apply, output and optional handoff methods |

Package roots are `src/skills/ai-context-auditor/` and
`src/skills/ai-context-governance/`. Each is independently selectable with null
configuration, empty required/optional dependencies and empty artifact roles,
schemas, templates and tools. Each method is its sole reference. The runtime is
`skill-instruction-reader`, scoped to its own operations, with `on_missing:
unavailable`. All four operations declare `execution: instruction` and point to
their actual local method. `implemented` records source presence only.

## Selected decisions in source

| Decision | Source treatment |
| --- | --- |
| D352-01 | Independent instruction packages; neither skill is a prerequisite for the other or ordinary work. No shared runtime. |
| D352-02 | Prose default; requested export and selected project format use actual ownership/public operations. No new assessment family or record machinery. |
| D352-03 | Read-only audit subject; governance applies bounded project-owned edits under existing task authority, preserving managed core/projections/locks and others' work. |
| D352-04 | Full rules and necessary decision state remain with existing project owners; no second ledger or universal resolver. |
| D352-05 | Active source/legacy policy, historical/final records and original transaction recovery owners remain in force. |
| D352-06 | Optional semantic ADR/Lesson/promotion candidates; real public queries/digests/identities and separate candidate, acceptance, proposal, adoption, rule-content and effect facts. |

The actual public source interfaces for ADR 0.1.0, Lesson 0.2.0 and
standards-promotion 0.1.0 were read for the handoff wording. They were not invoked.
Portable methods require the receiving installed version's own public contract;
there are no imports or links to source designs, source policy or sibling packages.

## Remaining ownership

The coordinator assigns exact shared manifest mapping after reading these real
members. A future explicit context-maintenance profile may select both; ordinary
profiles must not acquire either implicitly. No mapping/profile/loader/adapter,
root/index, CI or other worker's files are part of this delivery.

Current source policy, #316 reconciliation, historical/final assessments and
ledgers, active legacy recovery, source catalog/release/CI and P6 installation/M01
remain with their original owners. No retirement, adoption, root cutover,
installation or behavior acceptance follows from source completion.

U001 verification beyond direct content/syntax/reference/Git/commit-message checks
is `deferred-by-owner`, owner program #322 coordinator / P7. P7 should select tiny
actual-use observations for standalone selection, read-only audit, comparison with
missing baseline, authorized direct edit, ownership conflict, selected export and
absent/present public knowledge handoff. No product CLI/help, product import,
schema validation, test/fixture, build/package/install/migration, audit/lease or
acceptance/effective-rule packet, or CI was executed for this source authoring.

Progress, actual checks and local handoff are owned by the
[workflow](../../../workflows/2026-09-23-optional-context-implementation/workflow-plan.md)
and [report](../../../workflows/2026-09-23-optional-context-implementation/reports/source-delivery.md).
