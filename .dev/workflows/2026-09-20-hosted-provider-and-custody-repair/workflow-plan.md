# Hosted Provider And Custody Repair

## Workflow Metadata

- `workflow_id`: `2026-09-20-hosted-provider-and-custody-repair`
- `plan_id`: `development-plan-2026-09-20-hosted-provider-and-custody-repair`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-20-hosted-provider-and-custody-repair`
- `base_branch`: `main`
- `status`: `in_progress`
- `updated_at`: `2026-09-20T17:42:45+08:00`
- `created_at`: `2026-09-20T13:11:34+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`

## Delivery Decision

One workflow and one pull request bind Issues #309 and #310: both repair the framework's hosted validation and delivery evidence contracts, use the same review and validation boundary, and can be reverted together. Two tasks retain separate acceptance and release/package dispositions. Workflow mode is justified by the preserved hosted-release failure, credential boundary, and cross-runtime custody state; no tasks were added merely for workflow cardinality.

## Scope And Authorization

- Owner authorization: the 2026-09-20 request linked to Issues #309 and #310.
- #309: make the Project-owner failure actionable without changing a credential, v0.18.0 tag, its assets, or run `35487203277`.
- #310: remove the prospective-pass cycle by separating a completion candidate, its actual bytes-bound validation receipt, and custody release/delivery.
- Exclusions: release/version allocation, package rebuild, tag movement, provider mutation, Issue/Project mutation, unrelated package/history/downstream matrices, and .NET product runtime changes.

## Validation Selection

| Issue | Selected narrow validation | Not selected |
| --- | --- | --- |
| #309 | `test_release_provider_reconciliation.py` | Hosted execution is deferred pending owner-approved release credential review; no release/package matrix rerun. |
| #310 | External-task delegation contract test module and schema validator | No package/history/downstream/model matrix; unit evidence does not claim actual delegated execution. |

## Issue Dispositions

| Issue | PR disposition | Reason / next terminal gate |
| --- | --- | --- |
| #309 | `Refs #309` | The code improves diagnosis, but a new hosted Project read requires an owner-reviewed credential boundary and a future authorized release execution. |
| #310 | `Closes #310` | The F-009-01 raw-bytes type-exactness repair and focused validation are complete; terminal closure remains subject to a fresh current-head independent audit, hosted required checks, admission, integration, and post-merge read-back. |

## Distribution Boundary

- #309 is source-only self-management: the release workflow and reconciliation script were not in the v0.18.0 package.
- #310 changes the distributed external-task validator, completion template, and runtime-coordination reference. It affects downstream AI collaboration behavior, not .NET product runtime behavior. No version is allocated here; normal release planning must include that package impact.

## Current Checkpoint

- Current task: `ISS310-completion-custody`; the workflow resumed after a fixed-head audit found F-009-01.
- Last completed action: replace ordinary raw-YAML mapping equality with recursive exact-type comparison and add focused candidate/dispatch regressions for YAML `true` and `1.0` versus an integer contract value; 35 focused tests passed.
- Exact next action: commit and push the F-009-01 corrective change to PR #311, synchronize its declared per-Issue disposition, then complete a fresh independent audit, current hosted checks, live admission, integration, and required provider read-back; do not merge or close either Issue before those gates complete.
- Preserved facts: v0.18.0 public assets were verified historically; run `35487203277` remains failed. The historical downstream outer receipt was blocked and its custody was released under an explicit exception.
- No cross-session handoff is required.
