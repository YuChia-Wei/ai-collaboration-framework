# PKG-012 AI Context Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-14-pkg-012-package-closure`
- `workflow_id`: `2026-08-14-pkg-012-package-closure`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-14T07:03:23+08:00`
- `updated_at`: `2026-08-14T08:33:30+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260813-001`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Issue #201 / `ASM-20260813-001#PKGCLOSURE-001`.
- Completed scope: schema 2.3 selected-input proof, profile-owned component projection, incoming candidate validator, source-only test exclusion, full-payload integrity gate, workflow integration, and focused Windows regression coverage.
- Validation summary: immutable `d30a1b7` real archives and fresh candidate passed on Windows and Ubuntu WSL. Full-matrix attempt 1 remains blocked by user-Temp ACL; attempt 2 is rejected as non-trusted; attempt 3 credibly ran 38 cases in 83.597 seconds and failed with two missing-portable-fixture failures plus one fixture Git error. The fixed `ba7bc3f` independent audit also found incomplete schema/component authority and help-only runtime closure. The working remediation now passes 17 extracted-validator fixtures (one Windows casefold skip), all three attempt-3 failures, 30 apply-reader tests (one Windows symlink skip), 17 dependency tests, and 4 registry tests; it is not accepted until committed and verified on a new immutable HEAD.
- Closure decision: `not-ready`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGCLOSURE-001` | HIGH | `independent-findings-remediated-verification-pending` | producer, profile, schema, incoming validator, workflow, candidate CI, dependency registry validation, tests, source-only exclusions, projected EOF normalization, and source-matrix isolation | fixed-HEAD audit failed at `ba7bc3f`; all audit/matrix findings now pass focused in the working tree | commits through `ba7bc3f162a60a9739551a7a5cd570e68d43551d`; remediation commit pending | new immutable real-package/full-matrix pass and independent assessment remain |

## Changes And Evidence

### `ASM-20260813-001#PKGCLOSURE-001`

- Changes: package schema `2.3.0` persists exact canonical selected-input proof and deterministic incoming validator identity; profile is the sole component assignment authority; source-only tests are excluded; every payload byte/path/case/mode/EOF is validated; candidate CI runs the validator from a fresh extraction.
- Evidence: Issue #201, baseline DS-04/07/13/14/15/17, read-only #200 boundary analysis, focused synthetic fixtures, apply read compatibility, implementation commits `06e27ed7585360dccf07f3933f0dce7cdd325561` and `fcfb3a83ded56c29e6c8dab47a028961d75bbe34`, and both preserved failed fixed-HEAD real-build attempts.
- Validation: Windows real package and both archives passed; fresh extraction reported 587 governed payload files, 14 portable entrypoints, and source-only exclusion. Ubuntu WSL passed 9/9 validator fixtures including case-fold collision, the same two archives, tar extraction, and candidate validator. The first external full matrix is retained as blocked-by-environment with 38 run, 9 passed, 28 Temp ACL errors, and 1 skipped; two focused cases pass with the correction. Earlier failed attempts and Windows skips are not relabeled as passed.
- Independent audit at `ba7bc3f`: failed with `PKG012-VERIFY-001` through `004`; no result was relabeled as passing.
- Remediation: exact package schema keys and identity metadata, component dependency and selection closure, user-view/capability ownership, inventory/migration/clean-install parity, selected envelope template proof, INSTALL/requirements closure, exact registry records and pins, installed dependency version, and recursive lazy-import closure now fail closed. Candidate CI installs the candidate's own checksummed requirements in an isolated venv before invoking its validator.
- Matrix correction: portable registry-declared paths are copied into every synthetic producer, skill-owned paths are included by the fixture profile, Git failures retain stderr, and short normal-ACL fixture roots prevent platform path/ACL noise.
- Remaining risk: commit-bound real archive/fresh extraction, full packaging matrix, POSIX confirmation, and independent assessment remain.

## Verification Assessment Reconciliation

- Independent auditor: failed at exact clean `ba7bc3f162a60a9739551a7a5cd570e68d43551d`; remediation re-audit pending on a later immutable HEAD.
- Confirmed resolved: none.
- Recurring findings: pending.
- New or regressed findings: `PKG012-VERIFY-001` incomplete schema/component projection; `PKG012-VERIFY-002` help-only dependency closure; `PKG012-VERIFY-003` failed full matrix; `PKG012-VERIFY-004` stale workflow evidence. All have working-tree remediations but none are yet independently verified.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `ASM-20260813-001#PKGAPPLY-001` | target mutation and Hybrid identity are owned by #200 | later #200 workflow | consume the proven #201 package/selection identity without broadening this workflow |

## Closure Evidence

- Required validations: focused implementation suites passed; fixed-HEAD and independent validations pending.
- Commit status: implementation/corrections through `ba7bc3f162a60a9739551a7a5cd570e68d43551d`; independent-finding and matrix remediation pending Issue-bound commit.
- Workflow/task status: in progress.
- Final next action: create an Issue-bound durable remediation commit, then run real candidate, immutable full matrix, POSIX confirmation, and independent re-audit.
