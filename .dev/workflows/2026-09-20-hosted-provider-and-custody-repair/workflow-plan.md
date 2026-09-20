# Hosted Provider And Custody Repair

## Workflow Metadata

- `workflow_id`: `2026-09-20-hosted-provider-and-custody-repair`
- `plan_id`: `development-plan-2026-09-20-hosted-provider-and-custody-repair`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-20-hosted-provider-and-custody-repair`
- `base_branch`: `main`
- `status`: `active`
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
| #310 | `Refs #310` | Source repair and focused tests are proposed; terminal closure remains subject to the PR review and hosted required checks. |

## Current Checkpoint

- Current task: `ISS310-completion-custody`.
- Last completed action: #309 focused repair passed after preserving the command-syntax and sandbox-TEMP blocked attempts.
- Exact next action: complete #310 candidate/receipt contract review and focused validation, then commit the validated stage.
- Preserved facts: v0.18.0 public assets were verified historically; run `35487203277` remains failed. The historical downstream outer receipt was blocked and its custody was released under an explicit exception.
- No cross-session handoff is required.
