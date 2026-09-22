# Independent fixed-subject review result

## Result

- Outcome: `failed`
- Parent action: `reroute`
- Execution commit: `8d00452d14bd1b6aa3e4cc9f74ffdbee084f14c8`
- Base commit: `237a01f437f3005ea57885714f6ebfc3037d196d`
- Content subject: `1247460e8592c41b57c6a97a9222392e631149141296eea3bbc25deef3a14494`
- Criteria digest: `5b514adaf82c6c9935721fc17a454f24c389f89516178363b9de682f7b0ee74d`
- Authority digest: `db820e5bcfa8b87b7f393e4ed7883e4dd185b371a098b0517411654a1c99dbe1`
- Canonical review-input digest: `ffcbe27bea3d9f01ca9d89c1d76d2d11c1ca30046ba9c5188f302411b835c5e8`

The implementation is not admissible at this subject. Two required exact-head checks fail, and the active workflow/report state does not describe the fixed review state. The restricted catalog behavior and the intended input-builder boundaries are otherwise well constrained by the inspected code and focused evidence.

## Findings

### F-001 — HIGH — Dynamic module state prevents the combined input-authoring suite from running

`execution_artifact_contract.load_module` installs a dynamically loaded module in `sys.modules` and restores the previous binding only when execution raises. `execution-artifacts.py` then imports `python_prerequisites`, whose registry path is derived from the importing fixture root. The combined required suite creates one fixture for `ArtifactBehaviorTests`, deletes it, and creates a second fixture for `InputAuthoringTests`; the cached prerequisite module still points at the deleted first fixture.

The exact-head hosted `execution-artifacts-tests` result therefore runs 26 earlier tests and then errors in `InputAuthoringTests.setUpClass` before any of the 11 new input-authoring tests execute. Six selected input cases pass when run in isolation, which narrows the defect to combined-process module isolation and does not cure the required-gate failure.

- Evidence: `.ai/scripts/execution_artifact_contract.py:72`, `.ai/scripts/execution-artifacts.py:13`, `.ai/scripts/tests/test_execution_artifacts.py:177`, `.ai/scripts/tests/test_execution_artifacts.py:458`
- Exact-head receipt: `.dev/ai-context/local/gap-ci-initial-artifacts/20260922T062615Z-2203/execution-artifacts-tests.result.json`
- Sealed log: `.dev/ai-context/local/gap-ci-initial-artifacts/20260922T062615Z-2203/execution-artifacts-tests.log` (`4505550876d536de08d169e67ffdb0415c4cdba8b2fde26253e7e736610fb468`)
- Impact: a required gate fails and the combined validation path omits every new input-authoring assertion, so isolated passes cannot support admission.
- Required postcondition: eliminate fixture-root module-state leakage and show the complete required test file passing on the repaired subject while retaining the dataclass loader behavior.

### F-002 — MEDIUM — Actionable README commands are not closed in the core-only package projection

The newly added review-input examples use concrete ignored request/output paths that do not exist in the projected payload. The same exact-head check also reports the existing focused catalog-test command target as absent from that projection. `test_gwt_009_given_core_only_selection_when_projected_then_review_and_role_dependencies_are_closed` fails with four missing actionable targets.

- Evidence: `.ai/scripts/README.md:89`, `.ai/scripts/README.md:90`, `.ai/scripts/README.md:324`
- Exact-head receipt: `.dev/ai-context/local/gap-ci-initial-artifacts/20260922T062615Z-2203/code-review-routing-contract.result.json`
- Sealed log: `.dev/ai-context/local/gap-ci-initial-artifacts/20260922T062615Z-2203/code-review-routing-contract.log` (`860fa9a6438907fd7ad34f6ba21e67dc999080ded39d2ea86b2c2260a55dc515`)
- Impact: a required core-only package integrity gate fails, so the documented commands are not portable under the repository's own projection contract.
- Required postcondition: make the actionable examples projection-safe and demonstrate that the exact failed reference-integrity case passes on the repaired subject.

### F-003 — MEDIUM — The active workflow and report point to already completed pre-review actions

The fixed commit already contains the implementation and is under independent review, but the active resume checkpoint and GAP-002 task still instruct the next actor to commit the candidate and dispatch independent verification. The report's current closure statement says the work is not committed. This conflicts with the exact subject and with the requirement that the workflow entrypoint expose current progress and next work.

- Evidence: `.dev/workflows/2026-09-22-artifact-gap-reduction/workflow-plan.md:46`, `.dev/workflows/2026-09-22-artifact-gap-reduction/tasks/GAP-002.json:36`, `.dev/workflows/2026-09-22-artifact-gap-reduction/reports/remediation-report.md:69`, `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md:70`
- Impact: resumption can repeat completed lifecycle actions and the retained report misstates the reviewed Git state.
- Required postcondition: project the failed independent review and its next repair/review action into the active workflow, task, and report without rewriting earlier failure evidence or claiming later provider admission.

## Pass A — Independent baseline

The implementation uses clear mechanical boundaries. The four input builders derive identities, validate current Git/input bytes, create only new contained ignored files, roll back only unchanged owned bytes, preserve failed evidence, and do not grant dispatch or admission. The three catalog selectors restrict changes to two `reason` fields and `derived_consumers`, validate exact citations and paths, and keep classification membership, reuse eligibility, and owner fields protected. The manual-gap table covers the original 16 rows and distinguishes executable partial fields, semantic-owner responsibility, and retained lifecycle work.

The baseline pass found the successful-load module-state leak, the package-unsafe command examples, and the stale current-state prose. It found no evidence that the builders execute the selected dependency callable, weaken gate classification, or claim universal writer coverage.

## Pass B — Repository-aware review

The repository-aware pass applied the fixed-head role, guardrails input, workflow artifact policy, exact-head hosted receipts, and Git-tracked fallback because the graph did not provide current changed-node provenance. It confirmed F-001 through a required hosted test failure with clean pre/post snapshots and F-002 through the core-only payload integrity gate. It elevated the stale prose to F-003 because the workflow entrypoint must lead to current progress and exact next work.

The exact-head artifact catalog suite passed 30 tests and supports the three restricted selectors and lifecycle registry checks. This evidence does not offset the two failed required checks. The separate terminal disposition failure observed after provider state changed is a later admission condition, not a defect conclusion about this fixed content subject.

## Pass comparison

- Confirmed in both passes: F-001 and F-002.
- Added by repository authority: F-003, because current resume truth is a required workflow property.
- Downgraded or deferred: none of the three findings.
- Excluded from the content verdict: provider disposition, final document intake, integration, Issue state, publication, credentials, releases, and downstream adoption.

## Gate dispositions

| Criterion | Disposition | Result | Evidence boundary |
| --- | --- | --- | --- |
| Four input builders | `re-executed` | `failed` | Six isolated exact-head cases passed, but the required combined exact-head gate failed before all 11 new cases ran; F-001 controls. |
| Three restricted catalog operations | `reused-with-proof` | `passed` | Exact-head hosted artifact-catalog result passed 30 tests with matching clean pre/post snapshot identity; code inspection confirmed protected fields and fixed source registry use. |
| Sixteen manual-gap dispositions and lifecycle routes | `re-executed` | `passed` | Git-tracked registry/table comparison found all 16 original rows disposed with 60 executable, 20 semantic-owner, 9 manual-gap, 4 external, and 1 creation-template current routes. |
| Report, workflow, and evidence truth | `re-executed` | `failed` | Earlier environment and behavior failures remain recorded, but current commit/review pointers are stale; F-003 controls. |
| Independent inspection and focused validation | `re-executed` | `failed` | Focused input cases passed; exact-head hosted execution and package-reference checks failed; F-001 and F-002 control. |
| Exact subject, authority, packet, lease, and cleanliness | `re-executed` | `passed` | Review-input, packet, and active lease preflights passed before and after behavior; tracked checkout remained clean at the fixed commit. |

## Evidence limits

- Retained `gap-input-*`, compatibility, route, profile, canonical, and catalog-worker logs are mutable-checkout supporting evidence only. They are not treated as immutable or hosted admission.
- The initial local focused run executed zero tests because the sandbox could not create the declared temporary fixture. Its failure remains in `.dev/ai-context/local/gap-audit-01/focused-input-tests.log`. Re-execution under the normal writable temporary boundary was a material environment change and passed six selected cases in 15.353 seconds.
- No full local matrix, provider mutation, credential access, repair, assessment publication, integration, or Issue lifecycle action was performed.
- This review does not authorize acceptance. Root owns repair, any affected-gate retry, current-subject rebinding, assessment publication, admission, and integration.
