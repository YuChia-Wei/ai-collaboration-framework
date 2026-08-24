# GOV-011 Stale Release Workflow Remediation

## Status

`completed` — the bounded terminal-anchor implementation and the separately
authorized validation-platform repair are complete on the local dedicated
branch. Provider integration and Issue/Project/release actions remain outside
this repository completion state.

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
| `GOV-011` / #243 | resolved | Contract, validator, fixtures, routing, v0.13 tracked anchor, full runner suite, and selected fast/critical aggregate gates pass on the exact clean repair head. |

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
- A WSL `/tmp` retry at `c5f99794947f53f13c5b789e14c0f83e15a5d34d`
  was blocked before launch because that ephemeral path did not survive until
  delegated preflight. It is not represented as executed or passed.
- A persistent WSL-home ext4 retry at the same exact clean head completed in
  44 runner-reported seconds but failed closed: 42 selected, 21 executed, 22
  failed, 0 blocked. Linux supervision reported inconsistent raw duration and
  an unreadable receipt. This is not represented as passed.
- The second fixed-head audit accepted the bounded #243 implementation and all
  scoped checks, but reported P1 because the failed selected aggregate cannot
  be reclassified without owner authority. Its P3 administrative checkpoint
  finding is corrected by this blocked handoff.
- The canonical critical gate at
  `ceee8b30786c2e7a4587c75e534172c73e6edc21` also failed closed: 65 selected,
  32 executed, 32 failed, 0 blocked. The unchanged `package-apply` check timed
  out after 90 seconds and 31 later checks were not launched.
- The registered `GOV011-001-blocked.yaml` checkpoint contains every aggregate
  attempt and exact outcome, so a fresh receiver does not depend on ignored
  `.codex` or `artifacts` bytes to learn that history.
- The new checkpoint and the 9-entry handoff registry validate. Handoff tests
  passed 22/22 on the host after the sandbox run hit Temp ACL errors; the two
  exact sandbox-created Temp directories were removed after path verification.
- Final handoff review corrected the planned AI-context validation command to
  the actually supported and passing `python .ai/scripts/validate-ai-context.py`
  invocation; no unsupported `--mode` argument remains in this task.
- The broad CheckAll runner class was interrupted during unrelated cases and is
  not represented as passed.
- Under the owner's repair authorization, the multi-hop and package-apply
  ceilings are now 360 and 600 seconds respectively, with unchanged required
  enforcement and memberships. Focused registry coverage passed 7/7.
- The supervisor now retains monotonic duration as authoritative and explicitly
  authenticates UTC wall-clock adjustment. Focused positive/tamper-negative
  coverage passed, the Windows supervisor suite ran 20 tests with 12 passes and
  8 platform skips, and a repaired WSL diagnostic authenticated a 2.683342-second
  adjustment before returning `completed`, `true`, exit `0`.
- Workflow artifact, AI-context, and source-governance validators passed before
  the repaired aggregate attempts.
- Fast attempt 1 passed on `774ef5864dafd7e07fa6ceb63aa46c33cd99d158`:
  42 selected, 41 executed, 0 failed, 0 blocked, and 1 not applicable. Its
  338-second fast-budget excess was reported as an advisory warning.
- Critical attempt 1 on the same head timed out at the delegated 900-second
  boundary after 48 executed passes, 0 failures, 0 blocked, and 2 not
  applicable. It emitted no aggregate seal and remains non-passing.
- Direct diagnosis then ran all 74 aggregate-runner tests in 894.656 seconds.
  The only failures were two stale fixture assertions: one conflated scoped
  portable package projections with the source-only full package matrix; the
  other conflated supervised snapshot admission with validator launch. Both
  exact cases pass after correction, and the measured per-check ceiling is now
  1200 seconds with unchanged release/nightly membership.
- The full validation-evidence suite passed 37 tests with one platform skip in
  161.591 seconds; its existing 180-second ceiling did not fail and was not
  changed.
- The repaired full aggregate-runner suite passed 74/74 on exact clean head
  `c71f5532c733d7e4b6c19bc802eda4cbef21f4e8` in 894.081 runner seconds
  (928.756689-second external boundary).
- Fast attempt 2 on that head passed: 42 selected, 41 executed, 0 failed,
  0 blocked, and 1 not applicable in 341 runner seconds. The fast budget
  warning remained advisory.
- Critical attempt 2 on that head passed: 65 selected, 62 executed, 0 failed,
  0 blocked, and 3 not applicable in 1891 runner seconds, with a valid
  aggregate seal. No third aggregate attempt was needed.
- The completion checkpoint cryptographically binds the 35-line critical
  terminal output and references the retained blocked checkpoint rather than
  rewriting any earlier non-passing outcome.

## Residual Risk

- The point-in-time GitHub evidence is deterministic offline input, not a claim
  of continued provider parity.
- Aggregate receipts are ignored local artifacts, so durable workflow evidence
  records their exact subjects, counts, durations, outcomes, and critical-log
  digest. Their earlier failed and timed-out predecessors remain non-passing.
- Provider observations are point-in-time evidence. Management must read back
  live state before any later push, pull request, Issue/Project transition, or
  release action.
- Any tracked repair after the final fixed-head audit invalidates that audit and
  requires a new independent audit.

## Next Task

No repository implementation task remains. The management conversation owns
independent local-branch verification and any separately authorized provider
integration; push, pull request, merge, Issue/Project transitions, and release
mutation have not been performed.
