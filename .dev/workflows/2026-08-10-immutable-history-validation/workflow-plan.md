# Layer Immutable .dev History Validation Without Weakening Evidence Integrity

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-10-immutable-history-validation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-10-immutable-history-validation-cont-02`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-08-10-immutable-history-validation`
- `created_at`: `2026-08-10T00:38:23+08:00`
- `updated_at`: `2026-08-10T08:31:18+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: `ASM-20260809-004#DEV-003` identifies monotonically growing immutable `.dev` workflow, assessment, and release history in critical checks. Issue #176 requires a routine/full validation contract that preserves fail-closed evidence integrity while avoiding repeated full-history scans when immutable history is unchanged.
- Authorized remediation scope: Implement #176 after owner decisions are recorded; retain full-history validation as the authority through parity and cutover. Also correct the user-confirmed documentation and machine rule ambiguity where `|` was intended as meta-notation for alternatives in commit-title examples, not as a literal required title character.
- Authorization source: Owner conversation on `2026-08-10`: `開始 #175＋#178 Phase A，並行處理 #176`. The same turn authorizes the commit grammar clarification.
- Baseline assessment: `.dev/assessments/ASM-20260809-004/assessment.yaml`, finding `ASM-20260809-004#DEV-003`.
- Exclusions: Do not modify immutable workflow, assessment, or release evidence; do not change hosted workflows before a separately authorized hosted-workflow scope; do not write course acknowledgement content; do not push, open a pull request, merge, tag, or publish from this execution slice.
- Completion criteria: A decision-backed, fail-closed layered validation contract has deterministic fixtures and full-profile parity evidence; the commit grammar documents and enforces issue-or-scope forms prospectively while explicitly accepting compatible historical titles; an independent `ai-context-auditor` verification assessment is requested and linked before workflow closure.

## Delivery Cohesion

Issue #176 changes source-of-truth validation behavior across policy, executable validators, fixtures, and check profiles; it needs a decision gate and independent audit. The commit grammar correction is a small, independently authorized policy/validator consistency repair on the same branch because its legacy-compatibility boundary and commit-policy validation overlap #176's validation surfaces. This workflow has two substantive tasks; its unique workflow state is the owner decision gate, staged parity/cutover evidence, and mandatory independent verification.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260809-004/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-10-immutable-history-validation/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260810-002/assessment.yaml`; the independent auditor verified receipt subject `99df2e0b1716b8f6b3def5a464b9f92c6802d823` with no active finding.
- Tasks: `.dev/workflows/2026-08-10-immutable-history-validation/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260809-004#DEV-003` | `SHOULD FIX` | `ai-context-governance` | decision-gated remediation | `VAL004-001-layered-history-validation` | deterministic routine/full fixtures, full-profile parity, and independent audit |
| Commit title notation ambiguity | `MUST FIX` | `ai-context-governance` | authorized prospective policy correction with legacy compatibility | `GIT-001-commit-grammar` | focused validator fixtures and policy/reference consistency checks |

## Owner Decision Gate For `VAL004-001`

The Issue records four decisions as required. The owner explicitly adopted the following packet on `2026-08-10` with: `同意，我會觀察之後的狀況再來看有沒有需要調整`. These decisions authorize implementation while preserving later evidence-based adjustment.

1. Routine proof: an already-verified baseline receipt binding content/tree digest and validator/schema fingerprint, plus `git diff --name-status <receipt-source>..HEAD` constrained by a closed allowlist. Any immutable-history path, validator, schema, or index change invalidates the receipt and fails closed.
2. Required full gates: release candidate, scheduled governance run, validator/schema change, and immutable-history path change.
3. Receipt reuse: bind to full 40-character source SHA, history tree/content digest, and validator/schema fingerprint; allow reuse only when no full gate is selected and the first-parent diff remains within the closed allowlist. No time-based freshness window; invalidation is event/fingerprint based.
4. Profile boundary: keep source-repository and downstream profiles explicit and distinct. Source validates workflow, assessment, and release history; downstream validates target-local AI context without shipping source history.

## Stages And Checkpoints

1. Bootstrap workflow and freeze baseline references.
2. Inventory current validators, profiles, schemas, and tests.
3. Complete the independent commit-title grammar correction with legacy compatibility fixtures.
4. Record the adopted layered-validation decision packet and implement it without broadening the hosted-workflow scope. `completed`
5. Run full-profile parity, establish the receipt commit, request independent post-remediation audit, reconcile evidence, and close or defer explicitly. `completed`

## Validation Strategy

- Workflow structural validation: `python .ai/scripts/validate-workflow-artifacts.py`.
- Commit grammar correction: focused `validate-git-commits.py` tests and direct policy/reference checks; preserve historical commit validation through a named compatibility branch in the grammar.
- Layered validation after decision: deterministic fixtures for add, modify, delete, unindexed item, stale receipt/digest, validator or schema fingerprint changes, immutable-history tampering, and full-profile execution.
- Independent verification: `ai-context-auditor` on the relevant validator, policy, profile, and fixture surfaces after remediation; this workflow will not self-author audit conclusions.
- Spec compliance: not selected; no problem-frame or owner decision selects it.

## Resume Checkpoint

- Last completed action: Reconciled final independent assessment `ASM-20260810-002`, which verified `ASM-20260809-004#DEV-003` addressed at receipt subject `99df2e0b1716b8f6b3def5a464b9f92c6802d823` with no active finding.
- Current task: `VAL004-001-layered-history-validation` (`completed`).
- Exact next action: The containing closure commit must be followed immediately by a generated receipt-only commit; verify `routine-reusable`, then perform no further workflow mutation in this execution slice.
- Validation already completed: immutable-history fixtures passed 19/19 with one Windows privilege skip limited to the executable symlink fixture; fail-closed aggregate-runner fixtures passed 40/40; profile registry passed 5/5; the selected governance/integration contract suites passed 40 tests; commit policy passed 19/19; AI-context, source-governance, workflow, assessment, version, shell-asset, dependency/version, profile-projection, source-include, and diff validators passed. The independent semantic review has no open correctness, security, fail-open, or contract-test finding. Windows temporary-directory restrictions required fixture suites to run outside the sandbox where noted.
- Git state: Bootstrap `5258e7c08e97ec4354898a0d798210af95a855ad`, grammar correction `7daeebfeb2b1b8a74ed25db35a991ef8edb1bb89`, implementation `6da4d4a41058f6a2ce9436a4f65b205d5a2121d4`, receipt baseline `99df2e0b1716b8f6b3def5a464b9f92c6802d823`, and independent assessment `cacdc5e` are committed locally.
- Branch history and checkpoint handoffs: No push or merge checkpoint. Segment 2 starts locally from `7daeebf` because segment 1 remains checked out in its isolated worktree.
- Blockers or unresolved decisions: None for the selected #176 implementation contract. The symlink execution fixture was skipped because Windows denied symlink creation (`WinError 1314`); the same ordering rule passed static semantic review and remains a truthful environment limitation. Hosted-workflow mutation, transport, pull request, merge, release, and publication remain outside this execution slice.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-10-immutable-history-validation` | `main` at `a2f6fe53f2f50d436e6be7e27eb4d7de1bc4c828` | local bootstrap | pending | local | `2026-08-10T00:38:23+08:00` | Establish decision-gated validation remediation and independent grammar correction. | Commit bootstrap, then inventory validators. |
| 2 | `codex/2026-08-10-immutable-history-validation-cont-02` | segment 1 at `7daeebf` | local implementation, receipt, and verification checkpoints | `cacdc5e` | local | `2026-08-10T08:31:18+08:00` | Complete the owner-approved implementation and independent verification without mutating or removing the isolated segment-1 worktree. | Commit terminal reconciliation, generate its immediate receipt-only child, and stop without transport. |
