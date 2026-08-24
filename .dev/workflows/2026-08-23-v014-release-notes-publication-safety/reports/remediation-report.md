# v0.14.0 Release Notes Publication-Safety Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-23-v014-release-notes-publication-safety`
- `workflow_id`: `2026-08-23-v014-release-notes-publication-safety`
- `owner_skill`: `ai-context-governance`
- `status`: `completed`
- `created_at`: `2026-08-23T23:09:27+08:00`
- `updated_at`: `2026-08-24T08:20:53+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `not-applicable; live Issue #241 and provider baseline are authoritative`
- `verification_assessment`: `renderer review passed at a3a77a3a15156046e93acfe8e190aa4a884ccd08; final source, route, and workflow-truth review passed at 908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac; provider receipt head d988359acd6a79fce71ee2949996828fa36e4768 passed fresh exact-head review with no findings`

## Remediation Summary

- Authorized scope: source notes, effective renderer/validator path, focused tests, deterministic body, bounded v0.14.0 retained-origin route-evidence remediation that preserves the existing source set, exact-head independent review, and exactly one hosted body-only correction from commit `908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac`. The latest owner authorization also permits push, PR, merge, and Issue #241 close when all remaining gates pass.
- Completed scope: consumer-facing source notes, v0.13.0+ structured publication-content contract across release notes and migration guidance, exact-defect and valid-counterexample GWT coverage, deterministic corrected body, retained-origin route evidence, focused validation, exactly-once hosted body correction, and mechanical before/after parity evidence.
- Validation summary: renderer 25/25, route 31/31, and release-state 37/37 passed; deterministic and hosted body SHA-256 is `07b17d1f47e5ee1489b2f4049da89f52e4acf50efedbf549e39a25582603737e`; post-mutation publication and finalization phases passed at tagged commit `412bb14a16fe75ee65a020b16680def0acc0ff1b`.
- Closure decision: `accepted-for-terminal-integration`

## Finding Resolution Matrix

| Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| REL016-F001 | high | resolved | source notes, renderer, tests, hosted body | focused and hosted parity pass | `915959a7f9f9aacac646276373e2764fc6016ed6` | None within Issue #241. |
| REL016-F002 | high | resolved | source notes, renderer, tests, hosted body | focused and hosted parity pass | `915959a7f9f9aacac646276373e2764fc6016ed6` | None within Issue #241. |
| REL016-F003 | high | resolved | source notes, renderer, tests, hosted body | focused and hosted parity pass | `915959a7f9f9aacac646276373e2764fc6016ed6` | None within Issue #241. |
| REL016-F004 | high | resolved | renderer, tests | durable status counterexamples pass | `915959a7f9f9aacac646276373e2764fc6016ed6` | Future durable section names require an explicit allowlist change. |
| REL016-F005 | high | resolved | rendered body and before/after provider evidence | exact 3785-byte hosted parity and publication/finalization pass | provider write from `908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac` | No further Release mutation is authorized. |
| REL016-F006 | high | resolved | v0.14.0 route matrix, published-package evidence, v2 receipts, route evidence, focused tests | 3 focused route tests, 31 full route tests, 37 release-state tests, hosted publication command, and independent review passed | `6bbf536baaeb98c27e902ac3c745162703ac9f5c` / `908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac` | Pre-existing three-source declaration remains unchanged by owner instruction. |

## Changes And Evidence

### Issue #241 baseline

- Changes: corrected source notes and a structured publication-content validation boundary are implemented; exact-pattern GWT regressions and deterministic rendered body evidence are present.
- Evidence: live Issue and live v0.14.0 Release were frozen immediately before the one PATCH. The immutable annotated tag object is `12f218ce...e7`, peeled commit is `412bb14a...ff1b`, Release is non-draft/non-prerelease, and the four `ai-context-dotnet-backend-v0.14.0*` asset tuples are unchanged.
- Validation: focused renderer, route, and release-state suites pass. Exact before/after receipts prove the hosted body changed from SHA-256 `d1fa92cb...a14b` to the expected `07b17d1f...3737e`; post-mutation publication and finalization phases pass.
- Remaining risk: workflow commit-range validation failed on four reviewed/provider-bound commit messages. Those SHAs remain preserved at pushed evidence head `d988359acd6a79fce71ee2949996828fa36e4768`; repository integration uses compliant PR #242 history with bounded tree-equivalence proof. Issue #241 currently has Project status `Inbox`; live Project #3 metadata proves the built-in `Item closed` workflow is enabled and is expected to set `Done`, but post-merge read-back remains mandatory. Direct Project mutation and any further Release mutation remain unauthorized.

## Verification Assessment Reconciliation

- Independent auditor: transient `ai-context-auditor` reviews bound to `d29d75e1f5bd7d22635dce3a95c6e730081264b5`, `b3a4d200706c099065274099685b1dcc2bd25acf`, and `d102fa534a86affe1ab7296219da295150854e0b` found the three HIGH bypasses; final source review at `a3a77a3a15156046e93acfe8e190aa4a884ccd08` passed 25/25 focused tests and 18/18 independent adversarial fixtures.
- Confirmed resolved: phase-neutral source notes and deterministic body evidence at the first reviewed commit.
- Recurring findings: none. Final review at `908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac` accepted source, route, and workflow truth with no findings.
- New or regressed findings: HIGH — migration guidance was appended after release-note-only claim validation; repaired by applying the same claim contract and exact regressions to both authored inputs. HIGH — a claim immediately following a Markdown heading shared the skipped heading block; repaired by retaining adjacent authored text for claim validation. HIGH — migration heading titles themselves bypassed the scanner; repaired by scanning heading titles without Markdown markers and reusing the exact defect corpus for migration headings.

## Authorized Retained-Origin Continuation

- Owner authorization: on 2026-08-24 the owner first authorized bounded retained-origin remediation. After its validation and exact-head review, the owner explicitly authorized exactly one v0.14.0 body-only update from `908eac7879ec7dcb1d9713f2ee5e5ec0e106c3ac`, overriding the interim no-Release-mutation boundary, and authorized push, PR, merge, and Issue close when no blocker remains.
- Diagnosis: all three routes fail for one shared reason—the matrix expects validator SHA-256 `beac0e76...b046c` while the current hardened validator is `ea4fd652...c278c`. Updating that digest alone would still leave legacy schema-1.0 receipts without portable proof.
- Feasible bounded repair: the unchanged hosted ZIP SHA-256 `3577c01a...cde05` passes its declared incoming validator and the hardened direct-edge validator for the existing v0.13.0, v0.9.0, and v0.6.0 origins. No retained-origin or `automatic_upgrade_sources` change is required.
- Implemented repair: schema-1.1 matrix identities and upgrade-edge-validation/v2 receipts now bind all three unchanged routes to the exact hosted ZIP, checksum sidecar, package manifests, source commit `412bb14a...ff1b`, and payload fingerprint `4406b96f...7913f`. The historical self-inconsistent archive remains preserved as rejected evidence.
- Test evidence: the first sandbox suite run was blocked by 31 Windows Temp ACL errors; the first host suite run then exposed three stale expected-message assertions. After correcting only those assertions, 3 focused route tests, all 31 route tests, and all 37 release-state tests passed.
- Provider receipt: `REL016-001-hosted-before.json` and `REL016-001-hosted-after.json` retain the complete bodies and bounded Release/tag/asset fields. The payload contained only `body`; every bounded non-body invariant is unchanged. GitHub's server-managed `updated_at` advanced while `created_at` and `published_at` remained unchanged.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| Package/archive identity rename | Explicitly deferred by Issue #241 and owner delegation. | Owner | Make a separate future naming decision; do not create ID-002 here. |

## Closure Evidence

- Required validations: focused source validation, route/release-state suites, and final exact-head source/route/workflow review passed. Exactly-once provider read-back and post-mutation publication/finalization phases passed. Workflow commit-range validation failed on `6bbf536b`, `831b6390`, `92ca302f`, and `908eac78`; this failure is retained. Provider receipt head `d988359acd6a79fce71ee2949996828fa36e4768` then passed fresh independent review and was pushed before the non-rewriting squashed delivery continuation was created. On segment 2, the sandbox Temp ACL block recurred, then host renderer 25/25, route 31/31, release-state 37/37, workflow, AI-context, bounded evidence-tree equivalence, hosted publication, and hosted finalization all passed.
- Commit status: workflow bootstrap `b12747531feb2249217935fbe8549e0a7671dc25`; implementation `d29d75e1f5bd7d22635dce3a95c6e730081264b5`; migration-input repair `b3a4d200706c099065274099685b1dcc2bd25acf`; heading-adjacent repair `855e101d61fdf38682a348400250b89e5dbe4dcf`; blocked receipt `d102fa534a86affe1ab7296219da295150854e0b`; migration-heading repair `915959a7f9f9aacac646276373e2764fc6016ed6`; final renderer receipt `a3a77a3a15156046e93acfe8e190aa4a884ccd08`; test-count receipt `4086a6d024f7c683ab493fdb33cdf1592abc9620`; route-evidence repair `6bbf536baaeb98c27e902ac3c745162703ac9f5c`.
- Workflow/task status: completed / REL016-001 and REL016-002 are completed; PR #242 repository integration remains a distinct provider lifecycle.
- Final next action: validate and independently audit the exact final PR #242 head, satisfy hosted checks and merge admission, merge with merge-commit topology, then read back the PR integration commit, Issue `CLOSED / COMPLETED`, and Project `Done`.
