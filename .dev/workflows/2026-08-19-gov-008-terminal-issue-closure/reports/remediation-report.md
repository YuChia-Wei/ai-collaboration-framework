# GOV-008 Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `1.0.0`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`

## Current Disposition

- Status: `remediated-pending-fresh-verification`
- Finding: `GOV-008-CLOSURE-ASYMMETRY`
- Current delivery: PR A contract implementation, intentionally `deferred` for Issue #212.
- Deferred reason: `self-hosting contract must integrate before it can govern its own terminal closeout`.
- Next terminal gate: `continuation closeout PR after PR A merges`.
- Focused local validation began at 18 closure scenarios and reached 29/29 at the second repair head; GitHub provider, repository configuration, entrypoint and prerequisite registries, workflow/shell/source governance, downstream distribution, and AI-context contracts also passed locally. Sandbox Windows Temp permission failures were retained as blocked attempts; the same affected suites passed on the host.
- Independent exact-head audit, hosted checks, integration, and provider read-back remain pending and must not be inferred from this record.

## Failed Exact-Head Audit

- Subject: `4fe042f8a1d0483b311b327a22fa0b7e320300c4`
- Disposition: `FAIL`
- Blocking findings: no current PR/head binding; inline/qualified closing keywords bypassed deferred prohibition; review and required checks were neither exact-head-bound nor completeness-checked; workflow checkpoint predated the audit.
- Repair: separate declaration, merge-admission, and reconciliation validation stages; select exactly one current-PR record from the GitHub event; bind review and the exact required-context set to the same head; detect inline and qualified GitHub closing forms; refresh durable workflow truth.
- Provider binding: draft PR #220 was created at `8ae7ec75cbaf43c5b22b574006f182a2586bc33f`; its assigned number is now bound into the declaration record, and PR-event validation also requires the event head to equal the checked-out commit.

## Fresh Audit Of Provider-Bound Head

- Audited head: `40f0821b3443b79a5e9f4400dc77afc8e509f012`
- Disposition: `FAIL`
- Preserved fixes: current-PR selection, event/checkout head binding, inline and qualified closing-keyword detection, and exact-head provider-evidence validation all passed review.
- Blocking finding: the registered check validated a tracked `declaration` without mandating non-self-referential merge-admission evidence; workflow checkpoint text also lagged the audited head.
- Repair: make the required event check explicitly declaration-only and mandate a fresh untracked provider admission snapshot before merge, overlaid in memory and invalidated by head drift; refresh workflow truth.

## Fresh Audit Of Non-Mutating Admission Head

- Audited head: `1a54e94a3b07fcc1771b38484b594b457de904d8`
- Disposition: `FAIL`
- Preserved fixes: declaration-only event validation, exact PR/event/checkout binding, closing-keyword detection, and the untracked overlay model passed review.
- Blocking findings: the overlay could downgrade a later lifecycle record, and its required contexts/provider facts were self-declared rather than independently complete and fresh.
- Provider read-back: `Read-only governance contract` and `Ubuntu PR profile gate` failed at the audited head; three other jobs succeeded, and no review approval existed.
- Repair: only declarations may be overlaid; the tracked provider config owns the complete five-context set; admission now requires live GitHub verification of review/check-run IDs, timestamps, conclusions, and exact heads, with negative coverage for omission, stage downgrade, missing live verification, and snapshot/live mismatch.
- Focused validation: closure 35/35 and GitHub provider 20/20 passed with repository configuration, workflow, source-governance, AI-context, and diff checks.

## Fresh Audit Of Live Provider Capture Head

- Audited head: `5dca98d3da1a29b6d088c4bd44ce7161d5e901f2`
- Disposition: `FAIL`
- Preserved fixes: provider-owned complete contexts, live token replay/equality, declaration-only overlays, event/body/head binding, and prior closure semantics passed review.
- Blocking findings: a later comment could mask an effective change request; reviews/check runs were limited to one provider page; filesystem capture was vulnerable to reparse-root escape and overwrite races.
- Provider read-back: `Read-only governance contract` and `Ubuntu PR profile gate` failed; three other jobs succeeded and no review existed.
- Repair: only decisive review states supersede each other; provider pagination is complete, loop/host constrained, and fails closed at an unproven full page; live capture writes no path and emits verified evidence to stdout for trusted optional retention.
- Focused validation: closure 38/38 and GitHub provider 20/20 passed with repository configuration, workflow, source-governance, AI-context, and diff checks.
