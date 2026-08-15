# PKG-011 Durable Package Apply And Hybrid Identity Remediation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-14-pkg-011-durable-apply`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-14-pkg-011-durable-apply`
- `base_branch`: `main`
- `branch_segment`: `3`
- `status`: `in_progress`
- `current_phase`: `round-4-durable-commit-preparation`
- `artifact_root`: `.dev/workflows/2026-08-14-pkg-011-durable-apply`
- `created_at`: `2026-08-14T09:07:04+08:00`
- `updated_at`: `2026-08-15T08:17:23+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: package planning observes migration operation paths rather than the complete selected managed state, while apply snapshots rollback state only in memory and writes recovery evidence after mutations. Drift can be omitted, raw/EOL identity can create false reconciliation, Git mode is incompletely bound, and interruption can leave an unrecorded mixed state.
- Authorized remediation scope: GitHub Issues #200 and #209, `ASM-20260813-001#PKGAPPLY-001`, DS-01/02/03/10/11, and `OWNER-HYBRID-001`; implement complete managed-state inspection, Hybrid raw/Git identity, durable pre-mutation journal, explicit transaction states, idempotent resume/rollback, platform failure evidence, and boundary-first Git-ignore inspection.
- Authorization source: the owner authorized repository-native implementation of Issues #200-#208 and required all segments to complete locally before one cumulative push, PR, hosted-check gate, and merge; after Ubuntu 24.04 exposed the planner ordering regression, the owner explicitly instructed creation and implementation of Issue #209 on 2026-08-14.
- Normative truth: the live Issue #200 acceptance criteria, `.dev/assessments/ASM-20260813-001/evidence/owner-decisions.yaml`, package/provenance schemas, AI-context ownership policy, target validation policy, and the verified #201 selected-input proof contract.
- Exclusions: portable package closure remains owned and completed by #201; multi-version routing belongs to #206; prospective cutover and remediation packet belong to #203. Issue closure, Project/milestone allocation, tag, release, and publication remain unauthorized.
- Completion criteria: every selected managed path is observed; dirty-worktree changes cannot be hidden by canonical identity; raw SHA-256 and Git mode bind plan/journal/receipt; the journal is durable before mutation; planned/applying/interrupted/rolling-back/rolled-back/finalized transitions are validated; recovery is exact and idempotent; partial writes, ACL/readonly, symlink/reparse, mode, delete, rename, and EOL cases fail closed on Windows-compatible and POSIX paths; package-native validation and independent fixed-head verification pass.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260813-001/assessment.yaml`
- Prior package-closure verification: `.dev/assessments/ASM-20260814-002/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-14-pkg-011-durable-apply/reports/remediation-report.md`
- Verification assessment: pending under `.dev/assessments/<verification-assessment-id>/assessment.yaml`
- Tasks: `.dev/workflows/2026-08-14-pkg-011-durable-apply/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGAPPLY-001` / DS-01, DS-02, DS-10, DS-11 | HIGH | `ai-context-governance` coordinating `slice-implementer` | observe complete selected state and apply `OWNER-HYBRID-001` | `PKGAPPLY-001-hybrid-identity` | raw/Git identity, selected proof, unchanged-drift, autocrlf, dirty-tree, and mode fixtures |
| `ASM-20260813-001#PKGAPPLY-001` / DS-03 | HIGH | `ai-context-governance` coordinating `slice-implementer` | persist an exact pre-mutation transaction and recovery state machine | `PKGAPPLY-002-durable-transaction` | state transitions, fsync/atomic write, interruption at every boundary, idempotent resume/rollback |
| Issue #200 platform acceptance criteria | HIGH | `software-development-orchestrator` for bounded validation | prove fail-closed recovery and package-native compatibility | `PKGAPPLY-003-recovery-validation` | Windows/POSIX ACL, readonly, symlink/reparse, partial-write, EOL, delete, rename, mode, and full focused matrix |
| Issue #209 symlink planner regression | HIGH | `ai-context-governance` | reject symlink/reparse boundaries before selected-path Git-ignore inspection and retain a stable domain diagnostic | `PKGAPPLY-003-recovery-validation` | focused GWT-008 and full package-apply suite on `Ubuntu-24.04` |

## Implementation Routing Contract

- `intent`: `review-remediation` and `behavior-correction`.
- `execution_mode`: `generic`.
- `overlay`: `remediation`.
- `subject_revision`: `55551a8bf4fa53591f78fd85b3f5e2f67a9ddd82` before #200 artifacts.
- `in_scope`: `.ai/scripts/ai_context_package_apply.py`, apply planner/CLI entrypoint, provenance/receipt validation and schemas where required, focused package-apply tests, package-native validator compatibility, and this workflow.
- `non_goals`: architecture redesign, release publication, arbitrary package probe expansion, and unrelated upgrade or validation-runner work.
- `canonical_owner`: `ai-context-governance` implements the source-framework apply contract directly.
- `slice-implementer_evaluation`: not selected for execution. Its target-action packet requirement conflicts with this framework source repository's explicit `source_repository_rule`, which distributes the packet schema but prohibits creation of a live target packet. No packet or child invocation evidence is manufactured.
- `software-development-orchestrator`: coordinates only bounded Python tooling tests, review, long-running validation, and durable commit checkpoints without taking governance ownership.
- `role_execution`: not applicable because no slice-implementer execution is selected. The generic domain and ASP.NET/outbox/profile/test role bindings are also nonmatches for this Python source-framework transaction.

## Stages And Checkpoints

1. Baseline audit, live Issue read-back, verified #201 dependency checkpoint, graph-assisted apply-chain discovery, and stacked branch — completed.
2. Workflow, source-repository routing boundary, state-machine/schema design, and deterministic GWT matrix — completed.
3. Hybrid identity and full selected-state implementation with focused fixtures — completed.
4. Durable journal, recovery/resume/rollback implementation and forced-interruption validation — completed.
5. Cross-platform/package-native validation, Issue #209 boundary-order correction, fixed-clean-commit audit, finding reconciliation, and local closeout — in progress. Commit `df36a29ad36c6eb5103f44fe90e27da282a679de` passed its immutable 38-test package matrix, but its subsequent fixed-head audit failed on Windows replacement durability, finalization target/operation binding, parent symlink/reparse traversal, and pending-receipt rollback safety. Round 4 replaces unsupported Windows `ReplaceFileW` flags with `MoveFileExW(0x9)`, binds finalization to the resolved target and live `HEAD`, validates the exact sealed operation schema, rejects target parent boundaries, and permits rollback to delete only a deterministically reconstructed exact receipt. The final current-diff review returned no P1/P2/P3 findings.

## Validation Strategy

- Narrow tests first: `.ai/scripts/tests/test_ai_context_package_apply.py` and directly affected target/provenance/package validation contract modules.
- Deterministic interruption injection at every durable operation boundary; never use process timing as the oracle.
- Raw-byte, Git canonical identity, worktree dirtiness, Git mode, selected-input proof, and normalized diagnostic assertions remain separate.
- Windows-compatible fixtures avoid user Temp ACL ambiguity; POSIX validates executable mode, case, permissions, fsync/rename behavior, and interruption recovery at one immutable commit.
- Full matrices at or above the long-running threshold use the external-task contract on an exact clean commit with one terminal schema-valid receipt.

## Integration And Rollback Boundary

- This segment consumes but does not redefine #201 package validation/selected-input proof.
- Implementation commits remain Issue #200-bound and independently revertible before later upgrade work.
- Recovery artifacts live under the target Git administrative directory; only the finalized pending-validation receipt lives under the established target authority. Neither surface overwrites provenance, customization, or effective-rule truth.
- The cumulative PR to `main` remains deferred until all #200-#208 segments complete.

## Resume Checkpoint

- Last completed action: independent read-only round-4 re-review accepted the current five-file implementation diff with no P1/P2/P3 findings after receipt-parent boundary remediation.
- Current task: `PKGAPPLY-003-recovery-validation`.
- Exact next action: validate workflow artifacts, create a new Issue #200 durable commit, then dispatch the immutable Windows package-apply suite and final fixed-head audit.
- Validation already completed: commit `df36a29` fixed-HEAD package matrix 38/38 with a schema-valid receipt followed by a retained non-passing audit; after all round-4 code changes WSL `Ubuntu-24.04` passed 56/56 outside the sandbox in 21.963 seconds, affected Windows fixtures passed 4/4 and receipt-boundary fixtures passed 2/2, semantic customization lifecycle passed 7/7, semantic customization skill contract passed 5/5, AST parse and `git diff --check` passed, and the final current-diff review found no P1/P2/P3. The last full dirty-tree Windows run before the final receipt patch passed 55/55 with one symlink-privilege skip; it is supporting evidence only and must be replaced by the clean-commit external run.
- Git state: dirty unpushed round-4 working tree at base commit `df36a29ad36c6eb5103f44fe90e27da282a679de`; `main` is the ancestor, `main..HEAD` has no merge commits, and `refs/codex-safety/pre-squash-20260814-pkg-011` retains the pre-compression local checkpoint.
- Branch history and checkpoint handoffs: cumulative segment 3; no push, PR, merge, Issue close, or release mutation.
- Blockers or unresolved decisions: no implementation decision is required; a new immutable long-matrix receipt and fixed-head audit remain mandatory. A durable verification assessment ID cannot be allocated safely until Issue #213's collision mechanism is separately authorized and implemented, so the non-assessment audit result must remain transient in the meantime.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | `codex/2026-08-14-pkg-011-durable-apply` | `codex/2026-08-14-pkg-012-package-closure@55551a8bf4fa53591f78fd85b3f5e2f67a9ddd82` | local active stacked segment | workflow artifacts pending | not pushed | `2026-08-14T09:07:04+08:00` | durable apply consumes verified package identity and precedes upgrade correctness | validate rules, implement, verify, and locally close #200 |
| 3-rebase | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | local rebase and history-density reconciliation | 15 policy-valid commits; pre-compression recovery ref `refs/codex-safety/pre-squash-20260814-pkg-011` | not pushed | `2026-08-14T23:53:45+08:00` | incorporate merged #210 without a merge commit and reduce only same-stage unshared history | remediate fixed-head audit findings, then revalidate at a new clean commit |
| 3-audit-remediation | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | working-tree remediation before immutable validation | pending Issue #200 commit | not pushed | `2026-08-15T00:16:49+08:00` | close three P1 transaction findings and deterministic coverage gaps without changing delivery topology | durable commit, long matrix, and fixed-clean-HEAD audit |
| 3-audit-candidate-1 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | immutable non-passing audit checkpoint | `7b6bfbe85767d026d7f52a9df237da94ca4133dd` | not pushed | `2026-08-15T00:39:58+08:00` | preserve 38/38 long-matrix pass and two-P1 final-audit failure without relabeling either | remediate sealed operation post-state and journal-prefix correctness on the same branch |
| 3-audit-candidate-2 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | immutable non-passing audit checkpoint | `3e7723df2051e5dbb697cc2f3353f08ac951282b` | not pushed | `2026-08-15T01:12:00+08:00` | preserve the round-2 38/38 long-matrix pass and the subsequent two-P1 fixed-head audit failure | remediate rollback progress and finalization proof on the same branch |
| 3-audit-remediation-2 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | round-3 current-diff review | pending Issue #200 commit | not pushed | `2026-08-15T01:34:44+08:00` | close rollback crash-recovery and finalized-provenance proof defects without erasing the non-passing checkpoint | independent diff review, durable commit, long matrix, and final fixed-head audit |
| 3-audit-candidate-3 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | immutable non-passing audit checkpoint | `df36a29ad36c6eb5103f44fe90e27da282a679de` | not pushed | `2026-08-15T02:21:54+08:00` | preserve the round-3 38/38 matrix pass and subsequent fixed-head audit failure | remediate durability and finalization boundaries without rewriting the checkpoint |
| 3-audit-remediation-3 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | round-4 current-diff review accepted | pending Issue #200 commit | not pushed | `2026-08-15T08:17:23+08:00` | close Windows write-through, target binding, exact operation, parent boundary, and receipt rollback findings | durable commit, immutable Windows matrix, and fixed-clean-HEAD audit |
