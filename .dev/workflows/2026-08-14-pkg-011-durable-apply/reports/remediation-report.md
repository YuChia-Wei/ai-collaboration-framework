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
- `status`: `round-5-focused-validated-awaiting-durable-commit`
- `created_at`: `2026-08-14T09:07:04+08:00`
- `updated_at`: `2026-08-15T09:49:40+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260813-001`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Issues #200 and #209 / `ASM-20260813-001#PKGAPPLY-001`, DS-01/02/03/10/11, and `OWNER-HYBRID-001`.
- Completed scope: complete selected managed-state and proof identity; narrow raw/clean-Git Hybrid identity; durable Git-admin prestates and journal; atomic publication of a complete journal; exact-target recovery; supported write-through Windows replacement and removal; sealed active-operation post-state; validated journal prefixes and target surfaces; package-independent rollback; durable journal-v2 rollback progress; journal-v3 deterministic target staging; preparation and recovery admission before cleanup or target/journal mutation; exact package and receipt binding; apply/receipt/rollback hard-death recovery; retained-staging finalization rejection; finalized transition, operation prefix, plan post-state, receipt artifact, removal, resolved-target, live-HEAD, exact-operation, parent-boundary, and exact effective-rule packet-root validation; resume/rollback CLI; schema-2 receipt and target gates; boundary-first Git-ignore inspection; stable symlink/reparse diagnostic; documentation and deterministic Windows/POSIX fixtures.
- Validation summary: the round-5 focused Windows fixtures passed GWT-023 in 26.030 seconds, GWT-024 in 12.415 seconds, GWT-036 in 22.676 seconds, GWT-041 through GWT-043 in 16.129 seconds, GWT-044 through GWT-045 in 8.550 seconds, and adjacent GWT-009/GWT-039/GWT-040 in 7.334 seconds. Three changed Python files parsed, the task JSON parsed, the repository workflow-artifact validator passed all 82 post-adoption workflows, 102 indexed workflow directories, and 55 backlog items, and scoped `git diff --check` passed. A scoped transient current-diff audit found three zero-mutation/parity risks in the predecessor handoff; all were remediated and the final scoped review found no remaining P1/P2/P3 issue. No long-running, full-matrix, release, or nightly-full command was run because the owner requires all planned #200-#208 local changes, focused tests, reviews, and commits first.
- Closure decision: `awaiting-round-5-durable-commit`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGAPPLY-001` | HIGH | `round-5-focused-validated-awaiting-durable-commit` | apply engine, target receipt validator, focused tests, workflow evidence | prior fixed-head failures remain retained; round-5 GWT-023/024/036/041-045 plus adjacent GWT-009/039/040 passed and scoped current-diff review is accepted | prior non-passing checkpoints retained; round-5 commit pending | cumulative immutable Windows matrix and final fixed-head audit remain sequencing-deferred |
| `Issue-209-acceptance` | HIGH | `resolved-locally` | `.ai/scripts/ai_context_package_apply.py`, workflow evidence | GWT-008 passed 1/1 and complete package-apply suite passed 35/35 on `Ubuntu-24.04` outside the sandbox | pending | clean fixed-head validation remains shared with PKG-011 |

## Changes And Evidence

### `ASM-20260813-001#PKGAPPLY-001`

- Changes: plan schema 2 and complete managed observation; CRLF-only clean Git fallback with raw authority; exact #201 proof pointer/digest propagation; Git-admin durable plan/prestates/journal; native atomic writes; atomic journal publication; exact-target recovery; Windows write-through tombstones; explicit lifecycle and recovery CLI; deterministic YAML receipts; strict receipt-to-journal/plan binding; active-transaction target gate; raw artifact SHA/Git mode receipts; target-owned authority preservation; documentation.
- Evidence: live Issue #200, DS-01/02/03/10/11, `OWNER-HYBRID-001`, verified #201 proof contract, 56 focused GWT cases, lifecycle/effective-rule regressions, 38-case package matrix, and independent read-only review/re-review.
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

### Fixed-Head Audit And Current-Diff Review Round 4

- Immutable evidence: commit `df36a29ad36c6eb5103f44fe90e27da282a679de` remained clean and passed the exact external package matrix 38/38 in 148.405 seconds; the owner-authorized replacement dispatch/completion pair passed the canonical schema validator. Its later fixed-head audit remained non-passing.
- P1 Windows durability: existing-file and journal replacement used unsupported `ReplaceFileW` write-through semantics. Windows atomic replacement now uses `MoveFileExW` with replace-existing plus write-through (`0x9`) for absent and existing destinations.
- P1 finalization authority: the target gate now binds the sealed plan to the current resolved target root and live `HEAD`, validates the exact operation keys and semantic transitions, and rejects selected target reads or finalization writes crossing symlink/reparse parents.
- P1/P2 receipt rollback: rollback now rejects receipt parent and leaf boundaries, reconstructs the only legal receipt bytes from the sealed plan and current exact post-state without the package, refuses mismatched ordinary receipts before journal or target mutation, and removes an exact receipt before entering `rolling-back`.
- Deterministic evidence: GWT035-040 cover Windows replacement flags, malformed resealed operations, copied-root/changed-HEAD finalization, simulated and POSIX parent boundaries, ordinary/dangling receipt rejection, and the exact receipt-after-publication rollback case. WSL passed 56/56 after all fixes; the latest current-diff review found no P1/P2/P3.

### Current-Diff Review Round 5

- Reviewed surface: the predecessor's three-file uncommitted handoff on `75e0c67a3a3002c77627dc279a2c3b2fc0d96fc8`, followed by each remediation delta. This remained a transient read-only audit and did not allocate the Issue #213 durable assessment.
- P1 recovery admission: resume and rollback could remove deterministic staging before rejecting target, HEAD, target-surface, package, or receipt drift. Recovery now performs read-only journal-derived admission, exact package/receipt validation, and a second surface check before staging cleanup or any journal/target mutation.
- P1 preparation admission: a hard death after preparation could leave intended post-state bytes written externally; automatic rollback from a still-`planned` journal could then overwrite bytes the transaction never applied. The runner now persists an `applying` copy before mutating the live journal, and a rejected one-step preparation leaves the original planned journal and external bytes unchanged.
- P2 transition parity: persisting a rejection transition on the untouched planned journal made a later valid resume fail finalization parity. Rejected preparation now preserves transition sequence zero and no `last_error`; the exact-post fixture proves later resume and target validation succeed after the original prestate is restored.
- Final disposition: strengthened GWT-041, GWT-042, GWT-044, and GWT-045 cover dirty target, changed HEAD, validation-time target drift, wrong package, invalid pending receipt, and retained staging with exact zero-mutation assertions. The final scoped diff review found no remaining P1/P2/P3 issue.

### `Issue-209-acceptance`

- Changes: preflight each selected framework-managed path through the symlink/reparse boundary guard before `git check-ignore`; retain `symlink boundary` as a stable diagnostic phrase while preserving reparse-point coverage.
- Evidence: live Issue #209, focused GWT-008, and the complete 35-test package-apply suite on WSL distribution `Ubuntu-24.04` outside the sandbox.
- Validation: focused 1/1 and complete 35/35 passed with no skip.
- Remaining risk: the existing PKG-011 immutable-commit long matrix and fixed-head audit remain pending.

## Verification Assessment Reconciliation

- Independent auditor: prior fixed-head audits successively exposed recovery, sealed-prefix, rollback-progress, finalization, Windows durability, target-binding, and receipt-boundary defects. Each non-passing checkpoint and its successful matrix remains retained separately. The round-5 predecessor-work audit was transient and scoped to the current diff; it found and remediated three admission/parity risks, then found no remaining P1/P2/P3 issue. Final clean-commit verification is not complete and is not relabeled as passed.
- Confirmed resolved: receipt bytes now bind the finalized journal and sealed plan; Hybrid CRLF identity now passes end to end through target validation.
- Recurring findings: none from the earlier receipt/Hybrid re-review scope.
- New or regressed findings: round 5 found pre-admission staging cleanup, automatic rollback from a still-planned transaction, and rejected-transition parity risks in the predecessor handoff. All were corrected with deterministic no-mutation and successful-resume fixtures; the final scoped review found no P1/P2/P3.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `ASM-20260813-001#PKGCLOSURE-001` | resolved by #201 and consumed as a dependency | completed #201 workflow | preserve the selected-input authority boundary |
| `ASM-20260813-001#UPGRADE-001` | target-prospective upgrade authority is separate | Issue #203 | continue after defect segments |

## Closure Evidence

- Required validations: round-5 focused recovery, finalization, packet-root, target, HEAD, and receipt fixtures pass after the review fixes; a cumulative immutable Windows full suite and fixed-head audit remain required after the owner sequencing gate opens.
- Commit status: `7b6bfbe`, `3e7723d`, and `df36a29` remain retained non-passing audit checkpoints; `75e0c67` remains the round-4 durable implementation checkpoint, and the next durable `#200` commit will contain the round-5 audited remediation.
- Workflow/task status: round-5 focused review passed only after the three predecessor-work corrections above. Long-running/full-matrix/release/nightly-full validation remains intentionally deferred until all planned #200-#208 local changes, focused tests, reviews, and commits are complete. Durable verification assessment allocation remains gated by Issue #213 and is not inferred from implementation completion.
- Final next action: create the round-5 Issue #200 durable commit, then continue the remaining #200-#208 local work without dispatching long validation yet.
