# v0.5.0 Disposition Reconciliation

## Scope

This record closes the `GOV-001` and `CAP-001` disposition gates and selects the
remaining implementation owned by `VAL-001`. It changes current backlog truth
only. Legacy workflow artifacts remain unmodified historical evidence.

## GOV-001 Reconciliation

| Legacy marker | Current evidence | Disposition |
| --- | --- | --- |
| Repository-pattern follow-up for a separate Use Case/Handler boundary workflow | `.dev/workflows/2026-07-usecase-command-handler-boundary/workflow-plan.md` is completed, records D1-D12, aligns standards/context/analyzers, and reports 47 analyzer tests with `DBA1014` through `DBA1017`. | satisfied; do not duplicate |
| Legacy decision inventory and landing tasks retained `follow_up_needed: true` while the parent plan says all tasks are done | `.dev/workflows/2026-04-14-legacy-decision-portability-consolidation/workflow-plan.md` records completed status and states remaining questions are future governance considerations. The prompt catalog proposed for later reduction no longer exists at `.dev/standards/prompts/`; ADR governance remains intentionally represented by `.dev/adr/ADR-TEMPLATE.md` and `src/skills/adr/references/WHEN-TO-CREATE-ADR.MD`. | superseded by later cleanup or retained by explicit governance direction; no active task |
| Optional future ADR example, generated checklist, and final review suggestions | No acceptance criterion, owner decision, or later release gate promotes these suggestions. Current validators and ADR governance files are present. | close as non-requirement; reopen only through a new backlog item with current evidence |

The old `done`, `deferred`, and `follow_up_needed` values are not rewritten
because those files predate the current lifecycle contract. Their historical
meaning is preserved while this record owns current disposition.

## CAP-001 Decision

No terminology-specific skill is introduced in v0.5.0.

- `.dev/domain-language/` already owns noun-like, target-repository vocabulary
  through templates and migration boundaries.
- The source workflow explicitly deferred a technical glossary and terminology
  skill.
- Current evidence does not show a repeated action workflow with stable inputs,
  steps, validation, and output that would justify a new skill.
- Future terminology work should first extend the existing document pattern.
  A new skill requires new usage evidence and a separate backlog decision.

This is a resolved capability decision, not an indefinite deferral.

## VAL-001 Decision

The original gap is split by objective ownership:

| Concern | Current evidence | Disposition |
| --- | --- | --- |
| Repository convention validation | The completed Phase 3 and repository-pattern workflows replaced transitional repository grep checks with dotnet-native analyzers and retained design-intent review where syntax cannot prove semantics. | superseded; no new repository validator |
| Dependency/version consistency | `.ai/scripts/check-all.sh` still declares `check-dependencies.sh` as deferred, and no deterministic offline consistency validator owns declared tool/runtime dependency versions. | implement in `V050-006` |
| Latest-version and vulnerability lookup | Requires network state that is neither deterministic nor always available to downstream packages. | advisory only; not a required offline release gate |

`VAL-001` therefore remains `in_progress` until `V050-006` implements the
offline consistency validator, removes the permanent deferred placeholder, and
records focused plus aggregate validation.

## Resume Contract

- Completed gate: `V050-002`
- Next task: `V050-003`
- Next action: write failing schema and exact-source-selection fixtures for the
  PKG-003 multi-source upgrade contract.
- Remaining user decisions: none for these three disposition items.
