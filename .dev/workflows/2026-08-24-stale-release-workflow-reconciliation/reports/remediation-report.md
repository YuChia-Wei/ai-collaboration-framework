# GOV-011 Stale Release Workflow Remediation

## Status

`in_progress` — implementation and focused validation are complete; immutable
aggregate validation and independent exact-head audit remain.

## Docs Updated

- `WORKFLOW-ARTIFACT-POLICY.md` owns the declared terminal-anchor schema,
  evidence shape, `complete`/`continue` semantics, offline boundary, and
  actionable failure contract.
- The canonical `ai-context-governance` skill and workflow/commit playbook route
  terminal-anchor reconciliation without teaching title, path, date, or version
  inference.
- `.ai/scripts/README.md` documents the validator behavior and credential-free
  boundary.

## Boundary Decisions

- Detection is opt-in and relationship-driven. A workflow without
  `terminal_anchor_contract` is not classified from its name or location.
- A tracked evidence observation supplies `satisfied`, `not-satisfied`, or
  `unknown`; ordinary validation performs no provider query.
- `on_satisfied: complete` rejects active workflow/task projection and names
  the workflow, anchor, task, and conflicting states.
- `on_satisfied: continue` requires a reason and the exact unfinished-task set,
  allowing separately authorized post-publication remediation to remain active.
- The v0.13 terminal source record remains `release-source status: validated`.
  Only the stale workflow/task projection was reconciled; no hosted object or
  package byte was mutated.
- Earlier failed, blocked, and intermediate v0.13 evidence remains unchanged.

## Finding Reconciliation

| Finding | Disposition | Evidence |
| --- | --- | --- |
| `GOV-011` / #243 | partially-resolved | Contract, validator, fixtures, routing, v0.13 tracked anchor, and focused validation pass; exact-head aggregate/audit pending. |

## Validation

- Workflow lifecycle fixtures: 16/16 passed, including stale rejection,
  completed acceptance, explicit post-publication continuation acceptance, and
  no-inference compatibility.
- Workflow artifact validator: passed for 94 post-adoption workflows, 114
  indexed directories, and 55 backlog items.
- AI-context validator: passed.
- Source-governance validator: passed.
- Validation-profile registry: 7/7 passed on the host boundary after a sandbox
  Git Bash signal-pipe block.
- Applicable CheckAll routing cases: 2/2 passed on the host boundary after a
  sandbox Temp ACL block.
- The broad CheckAll runner class was interrupted during unrelated cases and is
  not represented as passed.

## Residual Risk

- The point-in-time GitHub evidence is deterministic offline input, not a claim
  of continued provider parity.
- The implementation is not complete until the immutable commit passes the
  selected aggregate profile and independent read-only exact-head audit.

## Next Task

Create the durable implementation commit, run `check-all.sh --profile fast` on
that exact clean commit, and dispatch the independent read-only governance
audit. Any repair creates a new subject and requires a new audit.
