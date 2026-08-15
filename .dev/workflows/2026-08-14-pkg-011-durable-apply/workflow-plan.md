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
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-14-pkg-011-durable-apply`
- `created_at`: `2026-08-14T09:07:04+08:00`
- `updated_at`: `2026-08-15T11:22:12+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: package planning observes migration operation paths rather than the complete selected managed state, while apply snapshots rollback state only in memory and writes recovery evidence after mutations. Drift can be omitted, raw/EOL identity can create false reconciliation, Git mode is incompletely bound, and interruption can leave an unrecorded mixed state.
- Authorized remediation scope: GitHub Issues #200 and #209, `ASM-20260813-001#PKGAPPLY-001`, DS-01/02/03/10/11, and `OWNER-HYBRID-001`; implement complete managed-state inspection, Hybrid raw/Git identity, durable pre-mutation journal, explicit transaction states, idempotent resume/rollback, platform failure evidence, and boundary-first Git-ignore inspection.
- Authorization source: the owner authorized repository-native implementation of Issues #200-#208 and originally required all segments to complete locally before one cumulative push, PR, hosted-check gate, and merge; after Ubuntu 24.04 exposed the planner ordering regression, the owner explicitly instructed creation and implementation of Issue #209 on 2026-08-14. On 2026-08-15 the owner first requested checkpoint integration, then chose not to merge the partial checkpoint and explicitly authorized resuming #200 through implementation and verification before re-evaluating integration. This latest decision authorized #200's immutable matrix and independent fixed-head verification after its focused changes and durable candidate commit. PKG-011 is now locally complete; #203-#208 implementation, Issue closure, merge, release, and publication authority remain unchanged and separate.
- Normative truth: the live Issue #200 acceptance criteria, `.dev/assessments/ASM-20260813-001/evidence/owner-decisions.yaml`, package/provenance schemas, AI-context ownership policy, target validation policy, and the verified #201 selected-input proof contract.
- Exclusions: portable package closure remains owned and completed by #201; multi-version routing belongs to #206; prospective cutover and remediation packet belong to #203. Issue closure, Project/milestone allocation, tag, release, and publication remain unauthorized.
- Completion criteria: every selected managed path is observed; dirty-worktree changes cannot be hidden by canonical identity; raw SHA-256 and Git mode bind plan/journal/receipt; the journal is durable before mutation; planned/applying/interrupted/rolling-back/rolled-back/finalized transitions are validated; recovery is exact and idempotent; partial writes, ACL/readonly, symlink/reparse, mode, delete, rename, and EOL cases fail closed on Windows-compatible and POSIX paths; package-native validation and independent fixed-head verification pass.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260813-001/assessment.yaml`
- Prior package-closure verification: `.dev/assessments/ASM-20260814-002/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-14-pkg-011-durable-apply/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260815-001/assessment.yaml`
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
5. Cross-platform/package-native validation, Issue #209 boundary-order correction, fixed-clean-commit audit, finding reconciliation, and local closeout — completed. Commit `df36a29ad36c6eb5103f44fe90e27da282a679de` passed its immutable 38-test package matrix, but its subsequent fixed-head audit failed on Windows replacement durability, finalization target/operation binding, parent symlink/reparse traversal, and pending-receipt rollback safety. Round 4 replaced unsupported Windows `ReplaceFileW` flags with `MoveFileExW(0x9)`, bound finalization to the resolved target and live `HEAD`, validated the exact sealed operation schema, rejected target parent boundaries, and permitted rollback to delete only a deterministically reconstructed exact receipt. Commit `75e0c67a3a3002c77627dc279a2c3b2fc0d96fc8` durably retained that remediation. Round 5 closes preparation-to-mutation admission, journal-v3 deterministic target staging, apply/receipt/rollback staging recovery, retained-staging finalization rejection, and the exact effective-rule packet-root guard. A transient predecessor-handoff audit found and corrected pre-admission staging cleanup, package/receipt rejection mutations, exact-post automatic rollback, and planned-transition parity gaps; the final focused current-diff review found no remaining P1/P2/P3 in this round-5 scope. Commit `28613098f91f6cca52cfc3b1ff88ea2e4ce9d59b` durably retains the audited round-5 implementation. Candidate `52cb86533a23324e07a59c49ff44f59329c5760a` passed the exact external package matrix 38/38 in 145.791 seconds, its receipt pair passed the canonical validator, and `ASM-20260815-001` independently found no P1/P2/P3 defect at the clean fixed subject.

## Validation Strategy

- Narrow tests first: `.ai/scripts/tests/test_ai_context_package_apply.py` and directly affected target/provenance/package validation contract modules.
- Deterministic interruption injection at every durable operation boundary; never use process timing as the oracle.
- Raw-byte, Git canonical identity, worktree dirtiness, Git mode, selected-input proof, and normalized diagnostic assertions remain separate.
- Windows-compatible fixtures avoid user Temp ACL ambiguity; POSIX validates executable mode, case, permissions, fsync/rename behavior, and interruption recovery at one immutable commit.
- Full matrices at or above the long-running threshold use the external-task contract on an exact clean commit with one terminal schema-valid receipt.
- Owner sequencing remains strict for the cumulative #200-#208 delivery, except that the 2026-08-15 owner decision now authorizes #200's exact-commit immutable matrix and independent fixed-head verification after its focused changes, review, and durable commit are complete. Release and nightly-full validation remain prohibited.

## Integration And Rollback Boundary

- This segment consumes but does not redefine #201 package validation/selected-input proof.
- Implementation commits remain Issue #200-bound and independently revertible before later upgrade work.
- Recovery artifacts live under the target Git administrative directory; only the finalized pending-validation receipt lives under the established target authority. Neither surface overwrites provenance, customization, or effective-rule truth.
- The owner-authorized checkpoint PR includes the current cohesive stack and uses `Refs #200`, `Refs #201`, `Refs #202`, and `Refs #209`. Repository policy forbids closing keywords, so all four live Issues remain open through this checkpoint.
- Local resolution classification at closeout: #202 and #201 have completed workflows plus final independent assessments; #209 satisfies its focused and complete Ubuntu package-apply acceptance tests; #200 passed its final immutable matrix and independent fixed-head assessment `ASM-20260815-001`. All four Issues remain open because Issue closure is a separate authorization and hosted integration has not completed.
- Select merge-commit topology because this is an explicitly requested pre-completion checkpoint and the branch boundary carries durable audit, assessment, rollback, and continuation evidence.
- Do not compress the current 21-commit branch further. It was already reduced once under the unpushed-history rule, while the remaining sequence preserves #202/#201 assessment boundaries, #200 non-passing fixed-head checkpoints `7b6bfbe`, `3e7723d`, and `df36a29`, round-4/round-5 remediation checkpoints, and the owner integration-decision boundary. Rewriting would invalidate exact SHA evidence and require new fixed-head validation. Preserve `refs/codex-safety/pre-squash-20260814-pkg-011` as local recovery evidence.

## Resume Checkpoint

- Last completed action: committed final verification assessment `ASM-20260815-001` at `07ef6fff190d446804943e8fbd4887880c425943`, which records exact clean subject `52cb86533a23324e07a59c49ff44f59329c5760a`, a 38/38 immutable package matrix in 145.791 seconds, a schema-valid receipt pair, and an independent audit with no P1/P2/P3 finding.
- Current task: `PKGAPPLY-003-recovery-validation`.
- Exact next action: commit this workflow closeout, fast-forward PR #214 to the resulting branch head, and perform one exact-head hosted-check watch. Stop on any failed required gate; if all pass, return the merge decision to the owner.
- Validation already completed: the historical round-4 evidence remains unchanged. On the final round-5 working tree, GWT-023 passed all eight apply hard-death boundaries in 26.030 seconds, GWT-024 passed all four rollback boundaries in 12.415 seconds, GWT-036 passed all exact sealed-operation variants in 22.676 seconds, GWT-041-043 passed in 16.129 seconds, GWT-044-045 passed in 8.550 seconds, and GWT-009/039/040 passed in 7.334 seconds. After the owner resumed #200, the corrected prerequisite contract passed 14/14 and governance routing passed 8/8; the #200 hard-death pair passed 2/2 in 40.720 seconds and the adjacent admission/staging/receipt/rollback set passed 9/9 in 57.773 seconds on the approved Windows host route. The initial sandbox attempts are retained as `blocked-by-environment` because fixture creation under the repository and Windows TEMP returned `WinError 5`; no test was changed to mask that boundary. Exact clean candidate `52cb86533a23324e07a59c49ff44f59329c5760a` then passed the external package matrix 38/38 in 145.791 seconds, its dispatch/completion pair passed the canonical validator, and the independent fixed-head audit found no P1/P2/P3 defect.
- Git state at local closeout: assessment commit `07ef6fff190d446804943e8fbd4887880c425943` follows verified subject `52cb86533a23324e07a59c49ff44f59329c5760a`; remote branch remains at `7b7776868c96380ae2f94149ee3d4f0f82cf5834`. `main` and `origin/main` resolve to `0eee7f21f2c6ed00df4ea06e76c342a368c6a59b`; PR #214 is open and unmerged; `refs/codex-safety/pre-squash-20260814-pkg-011` retains the earlier local recovery checkpoint.
- Branch history and checkpoint handoffs: cumulative segment 3 and PR #214 remain the integration vehicle. The first hosted run is retained as a historical failure; local #200 terminal evidence now permits a fast-forward PR update and exact-head gate read-back, but no merge has been authorized.
- Blockers or unresolved decisions: no local PKG-011 blocker remains. Hosted gates and the owner's merge decision remain external integration boundaries. Issue #213 remains implementation-unauthorized, and this workflow does not imply its collision-prevention mechanism exists.

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
| 3-audit-candidate-4 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | round-4 durable implementation checkpoint | `75e0c67a3a3002c77627dc279a2c3b2fc0d96fc8` | not pushed | `2026-08-15T08:20:41+08:00` | retain round-4 remediation before the predecessor round-5 handoff | audit and complete round-5 without dispatching long validation |
| 3-audit-remediation-4 | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | round-5 durable implementation checkpoint | `28613098f91f6cca52cfc3b1ff88ea2e4ce9d59b` | not pushed | `2026-08-15T09:53:40+08:00` | close admission, deterministic staging, hard-death recovery, retained-finalization, and exact packet-root gaps while preserving invalid-input zero mutation | continue remaining #200-#208 local work; defer long validation until cumulative local completion |
| 3-checkpoint-pr | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | owner-authorized pre-completion merge checkpoint | `7b7776868c96380ae2f94149ee3d4f0f82cf5834`; 21 prior commits retained without further compression | remote branch pushed; PR #214 open and unmerged | `2026-08-15T10:38:41+08:00` | expose completed-local #202/#201, resolved-local #209, and then-partial #200 without erasing audit history | complete #200 locally before updating the same PR |
| 3-terminal-candidate | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | immutable passing #200 validation checkpoint | `52cb86533a23324e07a59c49ff44f59329c5760a` | local; external receipt pair ignored | `2026-08-15T11:18:26+08:00` | bind the resumed hosted-contract fixes, immutable 38/38 package matrix, and independent fixed-head audit to one clean subject | persist the final verification assessment without changing the subject |
| 3-verification-closeout | `codex/2026-08-14-pkg-011-durable-apply` | `main@0eee7f21f2c6ed00df4ea06e76c342a368c6a59b` | final local verification assessment | `07ef6fff190d446804943e8fbd4887880c425943` | local; push to existing PR #214 pending | `2026-08-15T11:22:12+08:00` | record `ASM-20260815-001` and close PKG-011 without claiming hosted integration | commit workflow closeout, fast-forward PR #214, watch exact-head hosted gates once, then return merge decision to owner |
