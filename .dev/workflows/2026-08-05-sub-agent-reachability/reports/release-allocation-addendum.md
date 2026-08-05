# v0.9.0 Release Allocation Addendum

## Addendum Metadata

- `addendum_id`: `release-allocation-2026-08-05-sub-agent-reachability`
- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-05T10:00:52+08:00`
- `updated_at`: `2026-08-05T10:00:52+08:00`
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

## Planned Repository Reconciliation

- Create `.dev/backlog/items/SAG-002.yaml` as a resolved v0.9.0 release blocker.
- Add `SAG-002` exactly once to ROADMAP and the Resolved / Awaiting Publication index.
- Increase the canonical provider item count, add the post-adoption identity, and classify `SAG-002` as a framework enabler.
- Preserve the final remediation report; record this later owner decision only in this addendum and `SAR94-003`.

## Planned Provider Reconciliation

- Replace merged PR #122 `Closes` keywords with `Refs` to match the repository provider policy without reopening correctly completed Issues.
- Add the canonical backlog marker and aggregate-delivery note to representative Issue #118.
- Leave Proposal #94 labels and non-formal relationships unchanged because they match the established #93 proposal pattern and `infer_sub_issues: false` policy.
- Set only Issue #118 to Done / P1 High / Owner review Approved / Target release v0.9.0 / Published in Not yet published.
- Read back the exact Project field values and the `待發布` filter conditions before recording the provider receipt.

## Validation Boundary

No local validation script, test, build, formatter, `check-all`, aggregate gate, or other verification program will run. Manual file inspection and hosted GitHub read-back are permitted. Pull-request checks will be treated as hosted evidence only.

## Current State

Canonical allocation changes are being prepared on `codex/2026-08-05-sub-agent-reachability-cont-03` from `main@2aa61dd7a33916782170b8e3cc6de2e098c555d8`. External provider mutation and hosted CI have not yet occurred.
