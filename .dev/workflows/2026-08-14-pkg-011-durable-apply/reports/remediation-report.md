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
- `status`: `audit-remediated-awaiting-fixed-head-verification`
- `created_at`: `2026-08-14T09:07:04+08:00`
- `updated_at`: `2026-08-15T00:16:49+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260813-001`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Issues #200 and #209 / `ASM-20260813-001#PKGAPPLY-001`, DS-01/02/03/10/11, and `OWNER-HYBRID-001`.
- Completed scope: complete selected managed-state and proof identity; narrow raw/clean-Git Hybrid identity; durable Git-admin prestates and journal; atomic publication of a complete journal; exact-target recovery; write-through Windows source removal; explicit recovery states; deterministic receipt bytes; resume/rollback CLI; schema-2 receipt and target gates; boundary-first Git-ignore inspection; stable symlink/reparse diagnostic; documentation and deterministic Windows/POSIX fixtures.
- Validation summary: the rebased fixed-HEAD package matrix passed 38/38 with a schema-valid receipt; the latest WSL `Ubuntu-24.04` package-apply suite passed 43/43 outside the sandbox; the latest Windows package-apply suite ran 43 with 42 passed and one documented symlink-privilege skip; extracted-package validation ran 17 with one platform skip; history compression retained an identical final tree and all assessment/workflow/commit validators passed.
- Closure decision: `awaiting-immutable-validation-and-final-audit`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGAPPLY-001` | HIGH | `audit-remediated-awaiting-fixed-head-verification` | apply engine, target receipt validator, CLI, focused tests, install/upgrader docs, workflow evidence | Windows 43 run / 42 pass / 1 privilege skip and WSL 43/43 after all audit remediations | pending | immutable long matrix and final independent audit remain |
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

### `Issue-209-acceptance`

- Changes: preflight each selected framework-managed path through the symlink/reparse boundary guard before `git check-ignore`; retain `symlink boundary` as a stable diagnostic phrase while preserving reparse-point coverage.
- Evidence: live Issue #209, focused GWT-008, and the complete 35-test package-apply suite on WSL distribution `Ubuntu-24.04` outside the sandbox.
- Validation: focused 1/1 and complete 35/35 passed with no skip.
- Remaining risk: the existing PKG-011 immutable-commit long matrix and fixed-head audit remain pending.

## Verification Assessment Reconciliation

- Independent auditor: the fixed-head auditor returned three P1 findings and one P2 coverage finding; the first current-diff review found no remaining P1 and identified two P2 test/receipt hardening items; after both were dispositioned, a second review returned no P1/P2/P3 findings and matched scoped diff `2632fb943e6b9662e67771cc8348778a853e6551` before evidence-only metadata refresh. Final fixed-head verification is not complete.
- Confirmed resolved: receipt bytes now bind the finalized journal and sealed plan; Hybrid CRLF identity now passes end to end through target validation.
- Recurring findings: none from the earlier receipt/Hybrid re-review scope.
- New or regressed findings: none known in the latest focused suites; immutable validation and a fresh independent audit remain the authoritative gate.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `ASM-20260813-001#PKGCLOSURE-001` | resolved by #201 and consumed as a dependency | completed #201 workflow | preserve the selected-input authority boundary |
| `ASM-20260813-001#UPGRADE-001` | target-prospective upgrade authority is separate | Issue #203 | continue after defect segments |

## Closure Evidence

- Required validations: latest Windows and WSL remediation-focused suites pass; workflow validators, a long package matrix on the new immutable commit, and a fresh fixed-head audit remain required.
- Commit status: unpushed history was compressed from 18 to 15 without changing the final tree; the next durable #200 commit will contain fixed-head audit remediation plus refreshed workflow evidence.
- Workflow/task status: audit remediation implemented; immutable recovery validation in progress.
- Final next action: complete current-diff re-review and workflow validation, create the Issue #200 durable commit, then dispatch the long matrix and final fixed-head audit.
