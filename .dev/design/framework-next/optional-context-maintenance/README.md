# Optional context maintenance design

Issue [#352](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/352),
P5-E of program #322. Status: complete design proposal for coordinator selection;
no package, schema, installation or root-route activation is delivered here.
Source subject: `731d658b6004110fd59224ca39aa3a5d63891d91`.

This proposal addresses [D342-03/D342-06](../p5-selected-contract.md).
Ordinary project work remains usable without either maintenance skill.
Installation alone grants no rule-edit, provider, release or adoption authority.

## Proposed decisions

| ID | Recommendation | Consequence |
| --- | --- | --- |
| D352-01 | Two independently selectable instruction packages: ai-context-auditor and ai-context-governance. | No package dependency, common runtime, automatic invocation or pre-task health gate. |
| D352-02 | Default to prose plus caller-owned optional export; reuse a project-selected structured format through its existing owner. | No new assessment schema, allocator, store, query index or finalize tool. |
| D352-03 | Governance edits explicitly selected project-owned context under actual task authority. | Protected core/projections and installation locks go to P6; no broad cleanup or private cross-package calls. |
| D352-04 | Preserve necessary intent with its project rule/decision owner; do not generate a second customization ledger. | Unknown authority is unresolved for the affected action. No universal effective-rule engine. |
| D352-05 | Keep source self-maintenance and legacy recovery with current owners until explicit replacement. | #316, history, final conclusions, pending journals and old root routes remain separately governed. |
| D352-06 | Offer ADR/Lesson/standards-promotion candidates only when useful and selected. | Candidate, acceptance, proposal, rule edit, adoption and observed effect remain distinct. |

These recommendations are not new effective source rules. U001 permits this
design checkpoint; the coordinator selects implementation separately.

## Persistence alternatives

| Option | Useful when | Ownership and cost | Decision and limits |
| --- | --- | --- | --- |
| A. Prose-only optional audit plus caller export | One-off analysis, scoped drift review or comparison of known subjects | Skill owns method and truthful observations; caller owns export destination, retention, tracking and review process. No machine family. | Recommended default. No built-in query, lock, immutable-final enforcement or lifecycle validator. Prose is not a validated assessment record. |
| B. Reuse project-selected structured format | A project already has an adequate review record or Issue format and accountable owner | Existing format/tool owns identity, versions, read/query/write, validation, finalization and recovery; skill supplies semantic content and a field mapping. | Recommended opt-in. Unsupported versions or unclear ownership yield prose/mapping only, never an improvised adapter. |
| C. Own a minimal assessment record | Named machine consumers need stable finding queries and protected conclusions without an adequate project format | Requires real producer, inspect/query/validate/revise/finalize/supersede tools, version owner and persistence/concurrency/recovery contract. | Not selected: no such new consumer is selected by #352. A schema alone cannot supply these behaviors. |

A and B are complementary, not sequential stages. Exporting A does not require
B. Neither introduces a workflow/audit/receipt chain. This future portable choice
does not waive the source repository's existing assessment policy before cutover.

Reconsider C only for a named unmet use case with selected implementation
ownership. Before selection, name its semantic producer, mechanical writer,
reader/query consumer, structural/lifecycle validator, finalization authority,
version/migration owner, stable record/finding identities, assessed subject,
states, revision/supersession and crash rules. Freeze final conclusions; a successor
cannot inherit acceptance. Preserve unsupported history. No schema is proposed here.

## Deliverables

- [Boundaries and necessary semantic state](responsibility-boundaries.md).
- [Operations, persistence and knowledge handoffs](operations-and-handoffs.md).
- Entry/method drafts: [auditor](drafts/ai-context-auditor/SKILL.md) and
  [governance](drafts/ai-context-governance/SKILL.md).
- [Slices, open selections and P7 observations](implementation-plan.md).
- [Pinned evidence](../../../workflows/2026-09-23-optional-context-maintenance-design/evidence/source-evidence.json).
- [Work plan](../../../workflows/2026-09-23-optional-context-maintenance-design/workflow-plan.md)
  and [delivery report](../../../workflows/2026-09-23-optional-context-maintenance-design/reports/design-delivery.md).

Only direct content, UTF-8/JSON syntax, references, Git/diff and complete planned
commit-message checks run. Product execution (including help), schema validation,
tests/fixtures, build/install/migration, legacy validation, audit/lease machinery
and CI are deferred-by-owner under U001, owner program #322 coordinator / P7.
Syntax is not implementation or behavioral verification.
