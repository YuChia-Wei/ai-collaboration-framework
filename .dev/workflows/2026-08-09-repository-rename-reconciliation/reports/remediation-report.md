# Repository Rename Identity And Link Reconciliation

## Report Metadata

- `workflow_id`: `2026-08-09-repository-rename-reconciliation`
- `issue`: `#150`
- `owner_skill`: `ai-context-governance`
- `status`: `completed`
- `subject_branch`: `codex/2026-08-09-repository-rename-reconciliation`
- `subject_commit`: `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005`
- `updated_at`: `2026-08-09T21:39:20+08:00`

## Outcome

The rename reconciliation is implemented, independently verified, integrated, and terminally reconciled. Fresh checks passed for PR head `a6e01dea27f53fdfe3659e119ceb25fe952af25e`; GitHub merged PR #173 through the required two-parent merge commit `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005`. Issue #150 is `CLOSED / COMPLETED`, and Project #3 is `Done / P1 High / v0.12.0 / Not required / Not yet published`.

## Baseline Finding Reconciliation

| Baseline finding | Result | Evidence |
| --- | --- | --- |
| `ASM-20260809-001#AIC-001` | addressed | Current operational repository coordinates and the security link use the current repository. |
| `ASM-20260809-001#AIC-002` | addressed | The identity validator classifies every retained occurrence exactly once and rejects unclassified, overlapping, stale, or operational exemptions. |
| `ASM-20260809-001#AIC-003` | addressed | The source closeout fixture uses the current coordinate; compatibility behavior has its own notice and tests. |
| `ASM-20260809-001#AIC-004` | addressed | Terminal Project read-back is `P1 High`, `Done`, `v0.12.0`, `Not required`, and `Not yet published`; Issue #150 is closed as completed. |

Independent verification is retained in `ASM-20260809-002` with the decision `healthy-with-followups`.

## Validation Summary

| Surface | Result | Notes |
| --- | --- | --- |
| Repository identity policy | passed | 1,016 retired-name lines, 171 file assignments, 9 active rules at the verified subject commit. |
| Identity GWT suite | passed | 7/7 outside the sandbox. |
| Aggregate fail-closed suite | passed | 35/35 outside the sandbox; an earlier timeout was superseded by the completed run. |
| Source and hosted governance contracts | passed | Source governance, workflow contracts, dependency contracts, source entrypoints, and shell assets passed. |
| Source-only packaging boundary | passed | Focused exclusion contract 1/1; the voluntarily attempted full matrix was interrupted without a verdict. |
| Hosted-equivalent fast profile | passed | 29 selected, 0 failed, 0 blocked. |
| Assessment and AI-context artifacts | passed | 39 assessments; AI-context validation passed. |
| Initial hosted PR checks | failed / addressed locally | Run `31315015812`: four jobs passed; Ubuntu prerequisite contract found stale 27-entry assertions after the registry grew to 28. |
| Focused CI correction | passed locally | Exact hosted job suites passed 14/14, 4/4, and 5/5 outside the sandbox. |
| Fresh corrected-head checks | passed | Runs `31316137412`, `31316137415`, and `31316137431` all succeeded at `a6e01dea27f53fdfe3659e119ceb25fe952af25e`; PR profile selected/executed 38 with 0 failed and 0 blocked. |
| Merge topology | passed | Merge commit `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005` has two parents: base `e1dedd688707d84f5e7a26c7c7532f74a9860a94` and PR head `a6e01dea27f53fdfe3659e119ceb25fe952af25e`. |

## Provider Reconciliation

- Repository ID `1209513501` and node `R_kgDOSBe2HQ` resolve at the current coordinate; `main` remains the default branch and merge commits are allowed.
- HTTPS clone and the old-to-current redirect passed.
- The live SSH host fingerprint matches GitHub's official metadata, but credentialed clone is `blocked-by-environment` because this host has no GitHub private key.
- Issue #150 is closed as completed at the current coordinate with closeout comment `5231804695`.
- Project #3 fields are terminally reconciled and Status is `Done`. The owner set Priority to `P1 High`; automation preserved that decision and read it back.
- The Project item's top-level title projection differs from the linked Issue title, but both use the current repository identity. No destructive remove-and-readd was justified.
- Latest pre-delivery PR, Actions, v0.11.0 Release, four assets, and a release-download probe resolve at the current coordinate.
- The security advisory route redirects to the current path and then to the expected login return target. Signed-in form usability remains `owner-readback-required`.
- Existing tags, Releases, assets, and Git history were not mutated.

The detailed provider receipt is `evidence/provider-after.yaml`.

## Delivery And Integration Result

- PR #173 referenced Issue #150 without an auto-close keyword; Issue closure remained a separate terminal provider mutation.
- GitHub's `merge` method produced commit `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005` with two parents. Fast-forward, rebase-and-merge, and squash were not used.
- Integration and terminal Issue/Project states were read back separately before this records-only closeout.
- `Published in` remains `Not yet published`; this workflow does not publish v0.12.0.

## Residuals And Deferred Scope

- Optional owner read-back: the signed-in security advisory form.
- Environment follow-up: credentialed SSH clone from a host with a configured GitHub key.
- Product/package/archive/profile/namespace/CLI identity remains owned by #166.
- Broader `.ai`, `.dev`, and distribution inventories remain owned by #170, #171, and #172 and are not bundled into this delivery.

## Terminal Closeout

- Implementation PR #173: merged.
- Fresh hosted checks: passed.
- Required two-parent merge commit: verified.
- Issue #150: closed as completed.
- Project #3: `Done`; publication remains `Not yet published`.
- This records-only continuation changes no implementation, package, Release, tag, or asset. Its only remaining delivery action is integration through a merge commit.
