# v0.9.0 Release Allocation Addendum

## Addendum Metadata

- `addendum_id`: `release-allocation-2026-08-05-sub-agent-reachability`
- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-08-05T10:00:52+08:00`
- `updated_at`: `2026-08-05T10:31:24+08:00`
- `supplements`: `remediation-report-2026-08-05-sub-agent-reachability`
- `task`: `SAR94-003`

## Authorization And Boundary

The implementation remediation report remains final and unchanged. After PR #122 and records PR #123 reached merged `main`, the owner explicitly confirmed on 2026-08-05 that the seven-decision #94 outcome is intended for v0.9.0 and authorized canonical backlog, ROADMAP, provider-mapping, and GitHub Project reconciliation.

This addendum authorizes release allocation only. It does not authorize package generation, release configuration, tag creation or movement, GitHub Release creation, asset upload, or publication.

## Canonical Aggregation Decision

| Provider record | Canonical role | Release projection | Reason |
| --- | --- | --- | --- |
| Proposal #94 | intake and seven-decision provenance | no separate Included Work or Project release fields | preserves the original questions and owner ledger without counting a proposal as delivery |
| Issue #118 | representative provider projection for `SAG-002` | P1 High / Approved / v0.9.0 / Not yet published | owns the first bounded slice and represents the atomic #118/#119 delivery |
| Issue #119 | dependent implementation slice | no separate Included Work or Project release fields | runtime execution evidence depends on #118 and shipped in the same PR/rollback unit |
| `SAG-002` | canonical repository release item | resolved / completed in v0.9.0 / unpublished | supplies the exact future Included Work identity once |

## Repository Reconciliation

- Created `.dev/backlog/items/SAG-002.yaml` as a resolved v0.9.0 release blocker.
- Added `SAG-002` exactly once to ROADMAP and the Resolved / Awaiting Publication index.
- Increased the canonical provider item count, added the post-adoption identity, and classified `SAG-002` as a framework enabler.
- Preserved the final remediation report; this later owner decision is recorded only in this addendum and `SAR94-003`.
- Replayed after #92 allocation PR #124 and committed the canonical-before-provider checkpoint as `b9a6f0c76b8f45f5acd25f9592dfafc253f0404b` from `main@f4018e6bac7ce7df7367359278eeb07e204974a3`, preserving all six existing v0.9.0 items before adding `SAG-002` as the seventh.

## Provider Reconciliation

- Replaced merged PR #122 `Closes` keywords with `Refs` to match the repository provider policy without reopening correctly completed Issues.
- Added the `SAG-002` canonical and migration markers plus the aggregate-delivery note to representative Issue #118.
- Left Proposal #94 labels and non-formal relationships unchanged because they match the established #93 proposal pattern and `infer_sub_issues: false` policy.
- Set only Issue #118 to Done / P1 High / Owner review Approved / Target release v0.9.0 / Published in Not yet published. Proposal #94 and dependent #119 retain unset release fields.
- Read back Issue #118 as closed completed and the live `待發布` filter as `status:Done reason:completed -target-release:Unassigned published-in:"Not yet published"`; #118 satisfies it exactly once.
- Recorded the exact receipt in `.dev/backlog/provider-mappings/github-issues-SAG-002.yaml`.

## Validation Boundary

No local validation script, test, build, formatter, `check-all`, aggregate gate, or other verification program ran. Manual file inspection and hosted GitHub read-back supplied the permitted evidence; pull-request checks are recorded only as hosted evidence.

## Hosted Integration Evidence

- PR [#125](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/125) used only `Refs` traceability, passed all five hosted gates on corrected head `de16ca4854d28d58a536e28f4b41c7a3fef36cc5`, and merged at `2026-08-05T02:27:39Z` as merge commit `6eeed2b90054451d962a842decaefdee7fa96693` with parents `f4018e6bac7ce7df7367359278eeb07e204974a3` and `de16ca4`.
- The first hosted run `30969123106` found a deterministic workflow-index timestamp mismatch in the Ubuntu prerequisite job. Commit `de16ca4` synchronized the single index row; corrected runs `30969276832`, `30969276921`, and `30969276827` then passed governance, package candidate, Ubuntu prerequisite, Windows prerequisite, and Ubuntu quick-gate jobs.
- Merged-main read-back confirms the #92-integrated six-item v0.9.0 set remains intact and `SAG-002` is the only seventh item.

## Residual Provider Display Drift

Issue #118 and the Project item's linked Issue content both show `[SAG-002] Canonical Owning-Skill Reachability And Role Execution`. The Project `Title` text field still exposes the former title. GitHub rejected a direct field update because Title can be changed only for DraftIssues. No destructive remove/re-add was attempted because that would replace the stable Project item and its field/history identity. All release fields and `待發布` eligibility are exact, so this cosmetic provider limitation is not a release-allocation blocker.

## Current State

Canonical checkpoint `b9a6f0c76b8f45f5acd25f9592dfafc253f0404b`, provider receipt, PR #125 hosted evidence, merge-commit integration at `main@6eeed2b90054451d962a842decaefdee7fa96693`, and final Issue/Project/main read-back are complete. `SAG-002` is resolved in v0.9.0 with `published_in: null`; publication remains unauthorized.
