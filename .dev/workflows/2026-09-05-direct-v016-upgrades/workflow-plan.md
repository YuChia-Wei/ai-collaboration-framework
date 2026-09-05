# Direct Upgrades to v0.16.0

## Workflow Metadata

- `workflow_id`: `2026-09-05-direct-v016-upgrades`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-05-direct-v016-upgrades`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-09-05-direct-v016-upgrades`
- `created_at`: `2026-09-05T18:00:49+08:00`
- `updated_at`: `2026-09-05T18:00:49+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Authorization

Issue [272](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/272) requires actual v0.6.0, v0.9.0 and v0.15.1 direct upgrades to one v0.16.0 archive. The owner authorized continuation on 2026-09-05 after Issues 269 and 280 implementation was integrated. Source-specific semantic cutovers, target-owned reconciliation and recovery are in scope. The owner explicitly retained Issue 280 open in Verification until public v0.16.0 archive acceptance. Publication, tags and target-specific production customization decisions remain separate.

Baseline: clean main and origin/main at `013f39116962611c3dbd2825fecd9efca3ec8e3a`. The dedicated branch was created before material edits. Root holds the sole tracked-writer lease. The current code graph excludes the relevant script trees; bounded tracked-file discovery is recorded under the ignored Issue 272 validation root.

## Acceptance And Evidence

| ID | Observable acceptance | Required evidence |
| --- | --- | --- |
| UPG006-AC1 | Each origin resolves exactly one direct edge | Canonical matrix and three resolver receipts |
| UPG006-AC2 | Exact public origins upgrade to the same admitted archive | Actual isolated target plan/apply/validation/finalization records |
| UPG006-AC3 | Required semantic cutovers and customized ownership are reconciled | Origin-specific cutover assertions and bounded fixture decisions |
| UPG006-AC4 | Missing or tampered identity, ambiguity, validator disagreement and unresolved customization fail closed | Mutation/provenance boundary comparisons |
| UPG006-AC5 | Interruption resumes or rolls back without mixed provenance | Actual durable transaction execution and restored prestate proof |
| UPG006-AC6 | Retained support remains explicit and consumer entry is clear | Versioned source policy, migration guide and regression gates |
| UPG006-AC7 | Publication readiness preserves exact admitted bytes | Asset admission and independent review; fresh publication receipt remains pending |

Baseline audit UPG006-B1 found that historical edge validation executes portable archive checks but does not establish target upgrade completion. UPG006-B2 requires actual direct target apply, finalization and recovery for every origin. The baseline is retained in `evidence/baseline-audit.json`; it is analysis, not acceptance.

## Tasks And Validation

1. UPG006-contract: version the three-origin support horizon and direct release gate.
2. UPG006-direct-evidence: implement and execute the bounded actual upgrade matrix.
3. UPG006-release-readiness: bind immutable assets, independently verify and evaluate release readiness.

Focused checks precede immutable long-running execution. Long-running validation uses a read-only external agent with an exact command, validated packet and terminal report. Failed attempts remain visible and retries require material state change. Real fixture execution is labeled as isolated target evidence; it is not a production deployment.

## Branch Lifecycle And Resume

Use merge-commit topology for the coupled migration contracts, exact archive admission and retained execution evidence, preserving preparation commits as provenance. The current checkpoint is UPG006-direct-evidence. The first actual attempt failed before target execution because source-only release identity tools were included in the payload. The archive is not admitted. Independent runner review found three blocking gaps; repair 1 addresses each and retains the original findings and failure. Focused regression checks passed; the repaired actual matrix remains pending. Attempt 2 is authorized after the recorded material repairs, on a new immutable commit and fresh candidate archive. No implementation acceptance is established yet.

## Bounded Actual Execution Retry 3

Attempt 2 rejected a missing source manifest via FileNotFoundError; the runner expected only ApplyError and stopped before target writes. Its terminal fingerprint is retained in evidence/actual-attempt-2.json. Correction accepts this exact missing-file boundary, preserves target comparison, and redacts escaped host paths in terminal diagnostics. The second independent audit closed R1 and R2; its remaining R3 finding now submits the real exit-17 receipt to the receipt validator before asserting finalization remains blocked. This authorized implementation workflow permits one third immutable actual attempt after these material repairs. The package-selected files did not change, so reuse the exact preparation-package-3 archive with a deterministic selected-input proof rather than rebuild it.

## Bounded Actual Execution Retry 4

Attempt 3 was blocked by the execution sandbox while creating transaction prestate and cleaning its preparation directory. A same-path empty-directory differential probe failed under the default sandbox and passed under require_escalated. The OS attributes were normal; no global setting or permission was changed. The workflow authorizes one fourth isolated matrix attempt with the exact command under require_escalated and the same declared ignored output boundary. Additional harness corrections match the actual failed-receipt rejection, compare transaction evidence as well as target files, and record the runner digest plus restored rollback digest. Required actual release evidence and the candidate CI hook now enforce all three origins. No actual upgrade acceptance is claimed until the matrix passes.
