# PKG-011 AI Context Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-14-pkg-011-durable-apply`
- `workflow_id`: `2026-08-14-pkg-011-durable-apply`
- `owner_skill`: `ai-context-governance`
- `status`: `round-3-current-diff-reviewed-awaiting-durable-commit`
- `created_at`: `2026-08-14T09:07:04+08:00`
- `updated_at`: `2026-08-15T01:48:09+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260813-001`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Issues #200 and #209 / `ASM-20260813-001#PKGAPPLY-001`, DS-01/02/03/10/11, and `OWNER-HYBRID-001`.
- Completed scope: complete selected managed-state and proof identity; narrow raw/clean-Git Hybrid identity; durable Git-admin prestates and journal; atomic publication of a complete journal; exact-target recovery; write-through Windows source removal; sealed active-operation post-state; validated journal prefixes and target surfaces; package-independent target-template rollback; durable journal-v2 `rolling-back` progress and sealed rollback-start surface; finalized transition, operation prefix, plan post-state, receipt artifact, and removal cross-binding; deterministic receipt bytes; resume/rollback CLI; schema-2 receipt and target gates; boundary-first Git-ignore inspection; stable symlink/reparse diagnostic; documentation and deterministic Windows/POSIX fixtures.
- Validation summary: commit `3e7723df2051e5dbb697cc2f3353f08ac951282b` passed the immutable package matrix 38/38 with a schema-valid receipt but its fixed-head audit returned two P1 findings; after reconciling the first round-3 current-diff review, GWT034 passed all five resealed variants, WSL `Ubuntu-24.04` passed 50/50 outside the sandbox in 25.660 seconds, Windows ran 50 in 103.617 seconds with 49 passed and one documented symlink-privilege skip, and adjacent semantic customization suites passed 7/7 plus 5/5 outside the sandbox.
- Closure decision: `awaiting-round-3-durable-commit`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGAPPLY-001` | HIGH | `round-3-remediated-awaiting-current-diff-review` | apply engine, target receipt validator, CLI, focused tests, install/upgrader docs, workflow evidence | commits `7b6bfbe` and `3e7723d` each passed their matrix but failed the subsequent fixed-head audit; round-3 working tree passes Windows 49/50 plus WSL 50/50 | `7b6bfbe` and `3e7723d` retained non-passing audit checkpoints; round-3 commit pending | independent diff review, immutable long matrix, and final fixed-head audit remain |
| `Issue-209-acceptance` | HIGH | `resolved-locally` | `.ai/scripts/ai_context_package_apply.py`, workflow evidence | GWT-008 passed 1/1 and complete package-apply suite passed 35/35 on `Ubuntu-24.04` outside the sandbox | pending | clean fixed-head validation remains shared with PKG-011 |

## Changes And Evidence

### `ASM-20260813-001#PKGAPPLY-001`

- Changes: plan schema 2 and complete managed observation; CRLF-only clean Git fallback with raw authority; exact #201 proof pointer/digest propagation; Git-admin durable plan/prestates/journal; native atomic writes; atomic journal publication; exact-target recovery; Windows write-through tombstones; explicit lifecycle and recovery CLI; deterministic YAML receipts; strict receipt-to-journal/plan binding; active-transaction target gate; raw artifact SHA/Git mode receipts; target-owned authority preservation; documentation.
- Evidence: live Issue #200, DS-01/02/03/10/11, `OWNER-HYBRID-001`, verified #201 proof contract, 43 focused GWT cases, lifecycle/effective-rule regressions, 38-case package matrix, and independent read-only review/re-review.
- Validation: working-tree suites passed; the 38-case runner exceeded 120 seconds and must be repeated against the clean implementation commit through the external-task contract.
- Remaining risk: the remediated working tree still requires a new clean immutable commit, long matrix receipt, and independent fixed-head audit.

### Fixed-Head Audit Remediation

- P1 target authorization: recovery locks and validates caller target B but previously allowed the sealed plan to name target A; resume or rollback could mutate A without A's lock.
- P1 preparation publication: transaction root and prestates were created before the initial journal, so a crash could leave a journal-less root that blocked retry and could not be resumed or rolled back.
- P1 Windows deletion durability: `Path.unlink()` followed by a Windows no-op directory fsync allowed journal advancement without a write-through removal of a rename/remove source path.
- P2 boundary evidence: existing fixtures covered only `after_operation` and `after_destination_replace`, not every journal, source-removal, receipt, finalization, or rollback persistence boundary.
- Disposition: exact-target recovery rejects a copied transaction before mutation; transaction preparation publishes only a complete journaled root; Windows removal uses a same-volume `MOVEFILE_WRITE_THROUGH` tombstone; deterministic fixtures cover every declared preparation/apply/source-remove/receipt/finalize/rollback boundary plus cross-volume, retained-tombstone, and mixed-key receipt cases. The previous audit result remains non-passing historical evidence until a new fixed-head audit passes.

### Fixed-Head Audit Round 2

- Immutable evidence: commit `7b6bfbe85767d026d7f52a9df237da94ca4133dd` remained clean and passed the exact external package matrix 38/38 in 140.096 seconds; its dispatch/completion pair passed the canonical schema validator.
- P1 target-template rollback: rollback reconstructs post-state only from `required_framework_paths`, which intentionally excludes `target-template`; a clean-install add such as `AGENTS.md` can therefore raise `KeyError` without a package root instead of restoring exact prestate.
- P1 completed-prefix binding: journal load accepts inconsistent `next_apply_index` and `completed_operation_ids`; runner skips the asserted prefix, while final receipt construction declares remove/rename sources absent without observing them.
- Required disposition: bind deterministic expected post-state for every active touched path to the sealed plan; validate prefix, lifecycle, and target-surface invariants before recovery mutation and finalization; keep rollback package-independent; add a persisted `after_progress_journal` boundary plus target-template, corrupt-prefix, restored-source, resume, and rollback fixtures.
- Disposition: unpublished apply-plan schema 2.1 seals deterministic post-state for every active operation path while receipt schema remains 2.0; recovery validates ordered prefix, lifecycle, digest, and exact safe target surface before state mutation; rollback consumes sealed plan/prestate only; receipt creation requires a complete prefix and observed remove/rename absence; `after_progress_journal` and GWT028-031 prove fresh CLI rollback, corrupt evidence rejection, false-finalization rejection, and idempotent persisted-prefix recovery.

### Fixed-Head Audit Round 3

- Immutable evidence: commit `3e7723df2051e5dbb697cc2f3353f08ac951282b` remained clean and passed the exact external package matrix 38/38 in 133.222 seconds; its dispatch/completion pair passed the canonical schema validator.
- P1 rollback progress: rollback could restore a completed apply-prefix path and die before persisting progress, leaving the old journal to require post-state and wedging a fresh `--rollback` attempt.
- P1 finalization proof: the target provenance gate did not independently validate finalized apply index, completed operation IDs, operation-order digest, transition parity, sealed plan 2.1 post-state, or receipt artifact/removal agreement.
- Disposition: journal schema v2 adds `rolling-back`, seals the exact rollback-start observation before mutation, and persists a reverse-prestate path prefix after every restored path; fresh rollback accepts only the one explainable in-flight pre/start state and remains idempotent. Target provenance now requires a structurally valid sealed 2.1 plan, exact full finalized prefix, possible transition count, empty rollback progress, and receipt artifact/removal identity matching the sealed post-state. GWT032-034 cover rollback death before and after progress persistence, finalized journal corruption, malformed resealed operations, unsupported schema, and semantically impossible post-state.

### Current-Diff Review Round 3

- Reviewed diff: `30da33d2d6cce952818a2ca591d9992e52273017` at base `3e7723df2051e5dbb697cc2f3353f08ac951282b` was retained as a non-passing current-diff review result.
- P1 exact boolean identity: the apply and target validators used dictionary equality for absent post-state, where Python accepts integer zero as equal to `False`; a self-consistently re-sealed remove or rename-source could therefore pass malformed `exists: 0` evidence.
- P2 evidence timing: the first reviewer could not verify the complete post-GWT034 50-case reruns from its bounded input and required a rerun before retaining those counts.
- Disposition: both validators now require `exists is False` before accepting the exact absent record; GWT034 adds re-sealed remove and rename-source integer-zero variants and directly asserts the apply-side parser also rejects them. The complete Windows and outside-sandbox WSL 50-test suites were rerun after the fix with the exact outcomes and durations recorded above. Independent re-review accepted exact diff `222253299fa2d327383a3c9530e153d637fbe31a` with no P1/P2/P3 findings.

### `Issue-209-acceptance`

- Changes: preflight each selected framework-managed path through the symlink/reparse boundary guard before `git check-ignore`; retain `symlink boundary` as a stable diagnostic phrase while preserving reparse-point coverage.
- Evidence: live Issue #209, focused GWT-008, and the complete 35-test package-apply suite on WSL distribution `Ubuntu-24.04` outside the sandbox.
- Validation: focused 1/1 and complete 35/35 passed with no skip.
- Remaining risk: the existing PKG-011 immutable-commit long matrix and fixed-head audit remain pending.

## Verification Assessment Reconciliation

- Independent auditor: the first fixed-head auditor returned three P1 findings and one P2 coverage finding; current-diff review accepted their remediation; the max-effort auditor on clean commit `7b6bfbe` found two additional P1 recovery-evidence defects; after their remediation and a clean matrix, the max-effort auditor on `3e7723d` found two further P1 rollback/finalization defects. Final fixed-head verification is not complete.
- Confirmed resolved: receipt bytes now bind the finalized journal and sealed plan; Hybrid CRLF identity now passes end to end through target validation.
- Recurring findings: none from the earlier receipt/Hybrid re-review scope.
- New or regressed findings: the first round-3 current-diff review found one P1 exact-boolean validation gap and one P2 evidence-timing gap; both are reconciled and the independent re-review found no P1/P2/P3.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `ASM-20260813-001#PKGCLOSURE-001` | resolved by #201 and consumed as a dependency | completed #201 workflow | preserve the selected-input authority boundary |
| `ASM-20260813-001#UPGRADE-001` | target-prospective upgrade authority is separate | Issue #203 | continue after defect segments |

## Closure Evidence

- Required validations: round-3 Windows and WSL focused suites plus adjacent semantic lifecycle suites pass after the review fix; current-diff re-review passed; a new immutable long matrix and new fixed-head audit are required.
- Commit status: unpushed history was compressed from 18 to 15 without changing the final tree; `7b6bfbe` and `3e7723d` are retained non-passing audit checkpoints and the next durable `#200` commit will contain round-3 remediation.
- Workflow/task status: the first round-3 current-diff review failed, its P1/P2 are reconciled, and independent re-review passed; immutable gates remain pending. Durable verification assessment allocation remains gated by Issue #213 and is not inferred from implementation completion.
- Final next action: create the next Issue #200 durable commit, then repeat the immutable long matrix and fixed-head audit.
