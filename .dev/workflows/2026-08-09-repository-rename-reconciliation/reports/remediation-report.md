# Repository Rename Identity And Link Reconciliation

## Report Metadata

- `workflow_id`: `2026-08-09-repository-rename-reconciliation`
- `issue`: `#150`
- `owner_skill`: `ai-context-governance`
- `status`: `pre-pr-verified`
- `subject_branch`: `codex/2026-08-09-repository-rename-reconciliation`
- `subject_commit`: `ee05a0d385d7c5739554f81e8a3767e31e5b7793`
- `updated_at`: `2026-08-09T21:04:07+08:00`

## Outcome

The rename reconciliation is implemented and independently verified for the selected repository and provider surfaces. Current operational coordinates use `YuChia-Wei/ai-collaboration-framework`, retained occurrences are governed by an executable fail-closed policy, and Project #3 reflects the owner-selected P1/v0.12.0 lifecycle. Pull-request, hosted, integration, and terminal work-item evidence remain pending.

## Baseline Finding Reconciliation

| Baseline finding | Result | Evidence |
| --- | --- | --- |
| `ASM-20260809-001#AIC-001` | addressed | Current operational repository coordinates and the security link use the current repository. |
| `ASM-20260809-001#AIC-002` | addressed | The identity validator classifies every retained occurrence exactly once and rejects unclassified, overlapping, stale, or operational exemptions. |
| `ASM-20260809-001#AIC-003` | addressed | The source closeout fixture uses the current coordinate; compatibility behavior has its own notice and tests. |
| `ASM-20260809-001#AIC-004` | addressed | Project read-back is `P1 High`, `In progress`, `v0.12.0`, `Not required`, and `Not yet published`. |

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
| Fresh hosted PR checks | pending | Requires the delivery pull request. |

## Provider Reconciliation

- Repository ID `1209513501` and node `R_kgDOSBe2HQ` resolve at the current coordinate; `main` remains the default branch and merge commits are allowed.
- HTTPS clone and the old-to-current redirect passed.
- The live SSH host fingerprint matches GitHub's official metadata, but credentialed clone is `blocked-by-environment` because this host has no GitHub private key.
- Issue #150 is open at the current coordinate.
- Project #3 fields are reconciled. The owner set Priority to `P1 High`; automation preserved that decision and read it back.
- The Project item's top-level title projection differs from the linked Issue title, but both use the current repository identity. No destructive remove-and-readd was justified.
- Latest pre-delivery PR, Actions, v0.11.0 Release, four assets, and a release-download probe resolve at the current coordinate.
- The security advisory route redirects to the current path and then to the expected login return target. Signed-in form usability remains `owner-readback-required`.
- Existing tags, Releases, assets, and Git history were not mutated.

The detailed provider receipt is `evidence/provider-after.yaml`.

## Delivery And Integration Contract

- The PR will reference Issue #150 without an auto-close keyword; Issue closure is a separate terminal provider mutation.
- The owner selected a true GitHub merge commit. Fast-forward, rebase-and-merge, and squash merge are prohibited.
- Integration is accepted only after the merge commit is read back with two parents.
- `Published in` remains `Not yet published`; this workflow does not publish v0.12.0.

## Residuals And Deferred Scope

- Optional owner read-back: the signed-in security advisory form.
- Environment follow-up: credentialed SSH clone from a host with a configured GitHub key.
- Product/package/archive/profile/namespace/CLI identity remains owned by #166.
- Broader `.ai`, `.dev`, and distribution inventories remain owned by #170, #171, and #172 and are not bundled into this delivery.

## Pending Terminal Steps

1. Commit and push the verified pre-PR evidence.
2. Open the Issue #150 pull request and run fresh hosted checks.
3. Merge through GitHub's merge-commit method and verify a two-parent commit.
4. Reconcile integrated `main`, workflow records, Issue state, and Project state without changing publication state.
