# GOV-011 Stale Release Workflow Remediation

## Status

`in_progress` — implementation and every Issue-scoped validation are complete
at `ea1852fd8944cad29c2c6dfe31abbe1cc091d023`; independent audit of the
validation-reconciled head remains.

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
| `GOV-011` / #243 | partially-resolved | Contract, validator, fixtures, routing, v0.13 tracked anchor, and every Issue-scoped validation pass; exact-head independent audit remains. |

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
- Git commit policy: 1/1 commit passed for `main..ea1852fd8944cad29c2c6dfe31abbe1cc091d023`.
- Repository-wide `check-all.sh --profile fast` at that exact clean head failed
  closed: 42 selected, 22 executed, 20 failed, 0 blocked. The unchanged
  `multi-hop-upgrade-transaction` suite exceeded its registry-owned 90-second
  timeout; the remaining 19 required checks were not launched after that
  timeout. This result is not represented as passed.
- The exact GWT-023 case at the timeout boundary passed 1/1 when run alone on
  the host in 13.228 seconds. That diagnostic does not convert the aggregate
  failure into a pass.
- Fixed-head implementation audit found no P1-P3 contract defect; it failed
  closed overall only because the self-selected repository-wide fast aggregate
  was not green.
- The broad CheckAll runner class was interrupted during unrelated cases and is
  not represented as passed.

## Residual Risk

- The point-in-time GitHub evidence is deterministic offline input, not a claim
  of continued provider parity.
- The repository-wide fast profile is not green at this point-in-time. Its
  unchanged multi-hop timeout and the later not-launched checks remain a
  separate residual validation risk outside #243; no timeout or unrelated test
  code was changed to conceal it.
- Independent read-only audit of the validation-reconciled exact head remains
  required before repository workflow closeout.

## Next Task

Commit this validation reconciliation and dispatch an independent read-only
governance audit of the new exact head against the Issue-scoped workflow,
AI-context, source-governance, and routing gates. Any repair creates a new
subject and requires a new audit.
