# Round 2 Code Review Reference-Loading Baseline

## Evidence Boundary

- Subject: `main@df7012b6bf6ac360cfb47e2c79813384880665f8`.
- Measurement unit: exact Git blob bytes plus whitespace-word and line counts for the repository files declared by the current Code Reviewer entry and applicable role contracts.
- Runtime: Codex wrapper. The Claude wrapper differs by two bytes and does not change the conclusion.
- Excluded: system instructions, tool schemas, conversation history, generated effective-rule packets, model-internal accounting, and total prompt tokens.
- Interpretation: these are reproducible repository-backed declared load sets, not a claim that every runtime eagerly injects every byte or that bytes equal tokens.

## Current Load Graph

The current route has three layers:

1. `.agents/skills/code-reviewer/SKILL.md` points to the canonical skill and six top-level references.
2. `skill.yaml` requires the review index/checklist, evaluates four role bindings, and loads every matching role manifest and mandatory reference.
3. `role-execution.md` requires each applicable role manifest plus every reference it declares. The primary general role applies to every .NET review; aggregate, controller, and reactor roles add a second matching role.

| Representative review | Unique files | Exact bytes | Lines | Whitespace words | Current declared path |
| --- | ---: | ---: | ---: | ---: | --- |
| Top-level Code Reviewer entry | 8 | 43,747 | 974 | 5,465 | wrapper + canonical spec + all six declared top-level references |
| General .NET review | 14 | 65,017 | 1,489 | 8,132 | top level + general role + three shared references |
| Aggregate review | 17 | 71,120 | 1,642 | 8,839 | general route + aggregate role manifest/playbook/prompt |
| Controller review | 17 | 68,332 | 1,575 | 8,461 | general route + controller role manifest/playbook/prompt |
| Reactor review | 17 | 68,497 | 1,575 | 8,466 | general route + reactor role manifest/playbook/prompt |

The three shared role references alone are 16,712 bytes:

- `shared/code-review-checklist.md`: 2,445 bytes;
- `shared/common-rules.md`: 6,395 bytes;
- `shared/testing-strategy.md`: 7,872 bytes.

All four review roles declare the same three shared files. A controller-only or reactor-only review therefore loads aggregate, repository, outbox, general testing, profile, mapper, and other unrelated material before its small role-specific prompt is considered.

## Routing Coverage

`CODE-REVIEW-INDEX.MD` routes Aggregate, Use Case, Repository, Controller, Mapper, Outbox, and Test patterns. Six of those seven rows point to the complete `CODE-REVIEW-CHECKLIST.md` without a section anchor. Domain Event, Entity, Value Object, Projection, and Reactor detection appears elsewhere or only inside the monolith; it is not one complete entry-to-file-type routing table.

The monolith contains General, Domain, Use Case, Adapter, Test, Performance, Security, Documentation, and Projection sections. Existing granular standards already exist for Aggregate, Use Case, Repository, Controller, Mapper, Projection, Reactor, and Test, but the current Code Reviewer entry does not route directly to those owners.

## Semantic Drift Evidence

The duplicated projections are not byte-equivalent summaries:

- `CODE-REVIEW-INDEX.MD` applies `Apply/When` only to `EsAggregateRoot<TId>` and explicitly keeps non-ES aggregate review separate.
- `shared/code-review-checklist.md` lists direct constructor state assignment as a global must-fail and says aggregate state changes only through `Apply/When` without the ES predicate.
- The general role prompt fails any "Custom repository interfaces", while the current index permits measured target-specific batch ports and canonical doctrine permits distinct read-only ports.
- The aggregate prompt hard-codes `Contract.Require/Ensure/Invariant` naming even though current framework doctrine keeps guard/contract helpers target-selected.
- `skill.yaml` prohibits broad document scanning for rule semantics, while its current static reference list and role contracts direct the reviewer through broad, duplicated summaries.

This creates a correctness risk, not only a size concern: a shorter role prompt can select a stricter or obsolete summary before the canonical type predicate or target selection is applied.

## Keep / Move / Retire Disposition

| Surface | Disposition | Reason / replacement |
| --- | --- | --- |
| `code-reviewer/skill.yaml` | keep and shorten | Own triggers, review boundary, effective-rule preflight, role applicability, and output modes; point to one routing contract. |
| `references/output-contract.md` | keep, conditional load | Load for result formatting and durable-assessment mode; preserve `CRITICAL / MUST FIX / SHOULD FIX` and assessment behavior. |
| `references/role-execution.md` | keep, conditional load | Load only after an applicable role is selected or delegation evidence is required. |
| `CODE-REVIEW-INDEX.MD` | keep path as compact compatibility entry | Replace examples and repeated doctrine with file-type/finding routes and canonical owner links. |
| `checklist-reference.md` | move content into the routing contract; retain a compatibility stub for one migration window | It duplicates detection and priorities without owning doctrine. |
| `CODE-REVIEW-CHECKLIST.md` | split or reduce to a compatibility index | Move each normative section to its existing file-type owner; retain only cross-cutting checklist items that have no owner. |
| `shared/code-review-checklist.md` | retire duplicated normative body after compatibility | Replace review-role references with the routing contract and effective rule IDs. |
| `shared/common-rules.md` and `shared/testing-strategy.md` | keep files; remove them from unconditional Code Reviewer role loads | They have 50 and 46 active file consumers respectively, so Round 2 must not delete or globally relocate them. Load only a finding-specific section when required. |
| role `sub-agent.yaml` files | keep | Preserve applicability and provider-neutral role identity; replace generic references with role-specific routes. |
| role playbook/prompt pairs | consolidate | Keep one bounded role instruction per role; remove repeated semantic checklists and point to rule IDs/file-type owners. |
| `.ai/scripts/code-review.sh` | keep as compatibility entrypoint | It remains advisory and is not a semantic owner; do not include it in the review rule load set. |

No stable public path should be deleted in the first delivery. Compatibility stubs must name the replacement route and removal horizon; shared files used by non-review roles remain outside the Round 2 deletion scope.

## Before / After Equivalence Contract

The successor delivery must add a deterministic matrix covering at least:

- ES Aggregate and non-ES Aggregate;
- Domain Event, Entity, and Value Object;
- Command Use Case, Query Use Case, and Handler;
- write Repository and read-only Query port;
- Controller, Mapper, Outbox data, Projection, and Reactor;
- unit/use-case/integration Test.

For every case, before and after evidence must prove:

1. the same applicable effective `rule_id` set and exact normative-statement digests;
2. the same type-first and target-selection predicates;
3. the same finding priority and `CRITICAL / MUST FIX / SHOULD FIX` output categories;
4. the same transient-versus-durable output contract and assessment handoff;
5. the same applicable role identities and stop conditions;
6. no unrelated file-type standard in the after-load set;
7. strictly fewer repository-backed files and bytes than the matching baseline above, with no scenario exceeding its baseline;
8. compatibility paths and package references remain resolvable.

These checks should be fixture-driven and fail when a route omits a required rule, changes a digest, broadens to an unrelated file type, or silently substitutes a derived summary for its canonical owner.

## Finding Handoff

- `ASM-20260811-003#CRL-001`: current Code Reviewer routing is broad and not file-type/finding scoped.
- `ASM-20260811-003#CRL-002`: duplicated review projections can change applicability and target-selection semantics.
