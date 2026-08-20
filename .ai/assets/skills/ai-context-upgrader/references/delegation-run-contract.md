# Delegation Run Contract

This contract records one per-independent-run delegation choice for
`ai-context-upgrader`. It composes with the shared `role_execution` contract;
it does not replace a role binding, alter route or transaction evidence, or
prove a child invocation.

## Scope And Record Boundary

- Create one record before stage execution for each independent run.
- Retain the record only with workflow execution evidence or, for direct
  conversation work, in the bounded execution evidence. It never enters target
  provenance, target customizations, a package, or a retained downstream
  transaction.
- A static projection is not current-run support or invocation evidence. An
  unknown support state remains unknown until exact evidence is retained.
- Deterministic tools and validators remain the mechanical authority. A role
  result only supplies its bounded evidence to the owning upgrader.

## Modes

| Mode | Meaning |
| --- | --- |
| `none` | Run every canonical stage root-sequentially. No child selection is attempted. |
| `analysis-only` | Evaluate only applicable read-only analysis work. It does not permit mutation delegation, skipped canonical stages, or automatic terminal audit selection. |
| `full-recommended` | Evaluate recommended applicable bounded roles under the shared role-execution gates. Selection is still optional and must be evidenced per role. |

The mode is a run choice, not availability evidence. All modes retain the same
canonical stages in the same order:

1. `route-and-evidence-discovery`
2. `three-way-classification-and-reconciliation`
3. `semantic-customization-and-governance-analysis`
4. `plan-report-handoff-or-feedback-synthesis`
5. `terminal-fixed-head-independent-audit`

A root-sequential path satisfies the same stage obligations. A role that does
not apply is recorded through its bounded role-execution result; it is never a
silent stage omission.

## Prompt And Resume

- Ask at most once for an independent run.
- An explicit owner choice sets `decision_source: explicit-owner-choice`,
  `prompt.count: 0`, and `prompt.disposition:
  suppressed-by-explicit-choice`.
- A prompted owner choice records exactly one prompt and its decision evidence.
- A resumed run reuses the existing record and must set
  `resume.repeat_prompt: false`. It does not ask again.

## Support And Fallback Evidence

`execution_support.state` is `unknown`, `verified-available`, or
`verified-unavailable`. The latter two require exact evidence references;
`unknown` has no evidence reference and never authorizes an invocation claim.

When a non-`none` run follows a root-sequential path after selection was
considered, retain an explicit fallback record. It includes the bounded scope,
trigger, owner or workflow authorization evidence, exact evidence references,
and the canonical stages preserved by that fallback. No fallback is implicit.

`recommended-role-execution` falls back only to `root-sequential` with all
five canonical stages. `terminal-independent-audit` falls back only to a
`fresh-independent-context` with the terminal stage. The record does not erase
earlier role-execution attempts or their invocation evidence.

## Terminal Independent Audit

The terminal audit is always required for a terminal release or high-risk gate,
but it is selected only by an explicit terminal-or-high-risk basis. Routine
work, a static profile, and the selected mode do not start it automatically.

Its result is fail closed: only `passed`, bound to one exact clean subject and
retained evidence, can satisfy the terminal audit gate. `pending`, `failed`,
and `blocked` do not pass it. A fallback audit remains fresh and independent.

## Projection Boundary

Runtime-specific preferences live only in their own projection. They are
advisory, do not change the portable run record, and cannot block an otherwise
valid root-sequential path solely because a static preference differs. Deferred
projections remain deferred rather than being treated as permanent rejection.
