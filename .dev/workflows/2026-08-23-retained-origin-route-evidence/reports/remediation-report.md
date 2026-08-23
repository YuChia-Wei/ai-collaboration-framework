# UPG-005 Retained-Origin Route Evidence Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-23-retained-origin-route-evidence`
- `workflow_id`: `2026-08-23-retained-origin-route-evidence`
- `owner_skill`: `ai-context-governance`
- `status`: `in_progress`
- `created_at`: `2026-08-23T16:21:28+08:00`
- `updated_at`: `2026-08-23T16:45:57+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `live GitHub Issue #237 and repository-owned reproduction`
- `verification_assessment`: `pending exact-head read-only verification`

## Remediation Summary

- Authorized scope: make retained-origin edge proof cover the archive-declared incoming portable validation boundary, close ambiguous payload identity, protect the v0.6.0, v0.9.0, and v0.13.0 routes, and preserve package-apply validation before target mutation.
- Completed implementation scope: route proof now executes and records the incoming-candidate manifest, validator identity and canonical argv, result, output digest, and package identity; route matrix schema `1.1` and edge receipt `v2` require that proof; matching package/release IDs with a different payload fingerprint fail closed.
- Confirmed impact: the v0.14.0 route evidence was a false positive and later incoming validation rejects the route archive. This evidence does not establish silent target corruption.
- Immutable boundary: no tag, hosted Release identity, published asset, downstream target, Issue, Project, or release allocation was mutated.
- Closure decision: `local-fix-focused-validation-passed-awaiting-fixed-head-review-and-owner-historical-recovery-choice`.

## Repository-Owned Reproduction

- `route-assets/validate-direct-edge.py` at the baseline returned exit `0` for v0.13.0, v0.9.0, and v0.6.0 against route archive SHA-256 `6f332f2a17549eb46109d1b2786cdefb32839eea18520cd65476c246d1337116`.
- The same archive's declared `payload/.ai/scripts/validate-ai-context-payload.py --package-root .` returned exit `1` with `package.yaml user_view reference_integrity fields are invalid`.
- The published v0.14.0 ZIP has SHA-256 `3577c01a3aff015794ea9593ce56daed1f02409dd6f0106d1d87e289190cde05`; it is not the route archive.
- Both archives use `package_id: ai-context-dotnet-backend-v0.14.0` and `release_id: REL-v0.14.0`, but the published payload fingerprint is `4406b96f6293f87c19338f10b61c3ead1d5b7b0684c270c1437ec51d4c4a7913` while the route archive payload fingerprint is `dbf122d31c4babcb3b221a1e907206335bfcbca5b8af3a9c407b83f0f8690f32`.
- No external analysis folder was read, copied, or cited.

## Finding Resolution Matrix

| Finding | Status | Changed Surface | Focused Evidence | Residual Risk |
| --- | --- | --- | --- | --- |
| `ISSUE-237#edge-proof-false-positive` | remediated locally | direct-edge validator, route schema/resolver, receipts contract | self-inconsistent v0.14.0 archive fails for all three retained origins | existing historical v0.14.0 receipts remain legacy and non-passing under the new resolver |
| `ISSUE-237#payload-identity-conflict` | remediated locally | target package identity plus portable receipt comparison | same package/release ID and different payload fingerprint produces `edge-package-payload-identity-conflict` | an explicitly different artifact identity still requires full validation before it can pass |
| `ISSUE-237#retained-route-regression` | remediated locally | route and packaging fixtures | matching proof passes v0.6.0, v0.9.0, and v0.13.0; legacy v0.14.0 proof is reconciliation-required | historical recovery choice remains owner-sensitive |
| `ISSUE-237#package-apply-boundary` | preserved | package-apply negative fixture | failing incoming validator leaves target bytes unchanged and creates no transaction | none observed in focused scope |

## Changes And Evidence

### Portable Edge Proof

- The edge validator extracts only into an isolated temporary directory, verifies archive member paths and declared validator bytes, removes inherited Python path overrides, executes the exact archive-declared incoming-candidate validator, and records the canonical authority, command, package identity, exit state, and output digest.
- A non-zero incoming validator exit makes the edge command fail; it cannot emit a passing edge result.

### Route Identity And Receipt Contract

- Upgrade route matrix schema `1.1` requires target `{package_id, release_id, payload_fingerprint}`.
- Edge receipt `upgrade-edge-validation/v2` requires `incoming-package-validation/v1` proof and exact equality with the target package identity.
- Legacy matrix `1.0` remains parseable so current historical data can be diagnosed, but every legacy route is reconciliation-required because it lacks portable proof and canonical target package identity.

### Focused Validation

- `python -B .ai/scripts/tests/test_ai_context_upgrade_routes.py -v`: 29/29 passed in 13.850 seconds.
- Focused `UpgradeRoutePackageProjectionGwtTests.test_gwt_021...`: 1/1 passed in 3.109 seconds.
- Focused package-apply GWT-049 and GWT-049a: 2/2 passed in 15.628 seconds.
- `python -B .ai/scripts/tests/test_ai_context_release_state.py -v`: 36/36 passed in 0.799 seconds.
- `python .ai/scripts/validate-workflow-artifacts.py`: passed for 91 post-adoption workflows, 111 indexed workflow directories, and 55 backlog items before the report/task closeout update; it must be rerun after those updates.
- Read-only AST parsing passed for the four changed Python implementation/test entrypoints; `git diff --check` passed.
- The first package-apply selector command used the wrong unittest class name and produced two loader errors without executing tests. The corrected selectors produced the passing evidence above.
- A sandbox execution of the direct-edge script was blocked by Windows temporary-directory ACL behavior; the exact host regression run passed and is the counted evidence.

## Immutable v0.14.0 Boundary

- Live remote `main` and the annotated v0.14.0 tag peel were both bound to commit `412bb14a16fe75ee65a020b16680def0acc0ff1b` at workflow start; tag object was `12f218ce02acc855da53899c52b73eb6b9df75e7`.
- Live GitHub Release `REL-v0.14.0` remained published and unchanged. Its four recorded asset digests were `3577c01a...cde05`, `044175a9...cf870`, `7cfa186a...bb91c`, and `4c4295c7...b83f`.
- This workflow did not push, create a PR, merge, close Issue #237, mutate Project state, tag, publish, allocate a release, replace a hosted asset, or mutate a downstream target.

## Historical Recovery Recommendation And Owner Decision

- Recommended release impact: batch the prospective schema/validator/runtime change into the next owner-selected framework release together with a newly built package whose distinct release identity and payload fingerprint validate consistently. This Issue supplies impact evidence but does not choose v0.14.1 or v0.15.0.
- Until such a package and v2 receipts exist, v0.14.0 retained-origin routes should remain `reconciliation-required`; no current evidence supports relabelling them as passed.
- Owner choice A (recommended): keep the committed implementation and tests, leave the historical v0.14.0 support matrix and receipt bytes as immutable historical evidence, and let a later release own the first passing v1.1/v2 route inventory.
- Owner choice B: separately authorize a repository-only historical truth correction that upgrades the source-side v0.14.0 matrix to schema 1.1 and records three v2 failed receipts bound to the route archive. This would not alter the tag, GitHub Release identity, or any of the four hosted asset bytes, and it would not make the routes pass.
- No choice may reuse the published package/release identity for the different route payload without an explicit distinct validated artifact identity.

## Verification And Next Action

- The implementation must first be committed on a clean immutable local head, then a read-only `ai-context-auditor` verification must bind to that exact head.
- If review finds a defect, repair creates a new head and invalidates the earlier review.
- After fixed-head review, stop for the owner to select historical recovery choice A or B. Do not infer release version, push, PR, merge, Issue closure, or publication authorization.
