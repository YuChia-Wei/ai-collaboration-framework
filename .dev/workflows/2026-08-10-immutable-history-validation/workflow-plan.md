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
- `branch`: `codex/2026-08-10-immutable-history-validation`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-08-10-immutable-history-validation`
- `created_at`: `2026-08-10T00:38:23+08:00`
- `updated_at`: `2026-08-10T00:42:19+08:00`
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
- Verification assessment: planned independent `ai-context-auditor` assessment; identifier not allocated yet.
- Tasks: `.dev/workflows/2026-08-10-immutable-history-validation/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260809-004#DEV-003` | `SHOULD FIX` | `ai-context-governance` | decision-gated remediation | `VAL004-001-layered-history-validation` | deterministic routine/full fixtures, full-profile parity, and independent audit |
| Commit title notation ambiguity | `MUST FIX` | `ai-context-governance` | authorized prospective policy correction with legacy compatibility | `GIT-001-commit-grammar` | focused validator fixtures and policy/reference consistency checks |

## Owner Decision Gate For `VAL004-001`

The Issue records four decisions as required. The following recommended packet was sent to the owner on `2026-08-10`; implementation of this task remains pending until an explicit owner selection is recorded.

1. Routine proof: an already-verified baseline receipt binding content/tree digest and validator/schema fingerprint, plus `git diff --name-status <receipt-source>..HEAD` constrained by a closed allowlist. Any immutable-history path, validator, schema, or index change invalidates the receipt and fails closed.
2. Required full gates: release candidate, scheduled governance run, validator/schema change, and immutable-history path change.
3. Receipt reuse: bind to full 40-character source SHA, history tree/content digest, and validator/schema fingerprint; allow reuse only when no full gate is selected and the first-parent diff remains within the closed allowlist. No time-based freshness window; invalidation is event/fingerprint based.
4. Profile boundary: keep source-repository and downstream profiles explicit and distinct. Source validates workflow, assessment, and release history; downstream validates target-local AI context without shipping source history.

## Stages And Checkpoints

1. Bootstrap workflow and freeze baseline references.
2. Inventory current validators, profiles, schemas, and tests.
3. Complete the independent commit-title grammar correction with legacy compatibility fixtures.
4. Await and record owner decision for layered validation; implement only the selected contract.
5. Run full-profile parity, request independent post-remediation audit, reconcile evidence, and close or defer explicitly.

## Validation Strategy

- Workflow structural validation: `python .ai/scripts/validate-workflow-artifacts.py`.
- Commit grammar correction: focused `validate-git-commits.py` tests and direct policy/reference checks; preserve historical commit validation through a named compatibility branch in the grammar.
- Layered validation after decision: deterministic fixtures for add, modify, delete, unindexed item, stale receipt/digest, validator or schema fingerprint changes, immutable-history tampering, and full-profile execution.
- Independent verification: `ai-context-auditor` on the relevant validator, policy, profile, and fixture surfaces after remediation; this workflow will not self-author audit conclusions.
- Spec compliance: not selected; no problem-frame or owner decision selects it.

## Resume Checkpoint

- Last completed action: Completed the prospective commit-title grammar correction with explicit pre-cutover compatibility and deterministic fixture coverage.
- Current task: `VAL004-001-layered-history-validation` (pending owner decision).
- Exact next action: Record the owner's explicit selection of routine proof, full gates, receipt reuse, and source/downstream profile boundary before changing layered validation behavior.
- Validation already completed: commit policy GWT tests passed; root bilingual structural-parity tests passed outside the sandbox after the sandbox blocked temporary-fixture creation; AI context navigation validation passed.
- Git state: uncommitted commit-grammar remediation and task-state update.
- Branch history and checkpoint handoffs: no push or merge checkpoint.
- Blockers or unresolved decisions: `VAL004-001-layered-history-validation` awaits the four owner decisions above. The commit grammar task is independent and may proceed.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-10-immutable-history-validation` | `main` at `a2f6fe53f2f50d436e6be7e27eb4d7de1bc4c828` | local bootstrap | pending | local | `2026-08-10T00:38:23+08:00` | Establish decision-gated validation remediation and independent grammar correction. | Commit bootstrap, then inventory validators. |
