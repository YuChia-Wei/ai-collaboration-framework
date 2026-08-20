# UPG-004 Delegation Opt-In And Codex Advisory Preflight

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-21-upg-004-delegation-preflight`
- `plan_id`: `development-plan-2026-08-21-upg-004-delegation-preflight`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-21-upg-004-delegation-preflight`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-21T01:35:16+08:00`
- `updated_at`: `2026-08-21T02:03:19+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-21-upg-004-delegation-preflight/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-21-upg-004-delegation-preflight/`

## Development Objective

- Product or software outcome: Implement Issue #208 as a provider-neutral per-run delegation selection contract plus a Codex-only advisory model/reasoning/speed preflight without making mismatch, refusal, or unknown runtime state an upgrade blocker.
- Current lifecycle entry point: Reuse integrated SAG-003 role bindings and existing `role_execution` evidence while keeping prompt/run state outside target provenance and semantic customizations.
- User constraints: Selection is `full-recommended`, concurrency is 2, Terra-unavailable fallback is root sequential, Sol Max auditor-unavailable fallback is fresh Sol High, and Fast/priority is disabled; do not ask again.
- Non-goals: Claude/Copilot runtime equivalence, permanent global preferences, Fast activation, Project-field restoration, tag/Release/publication, or changes to external repositories.

## Inputs

- Requirements: Live GitHub Issue #208 and the explicit v0.14.0 owner prompt.
- Specifications: Integrated SAG-003 provider-neutral capability registry, provider projection registry, upgrader role bindings, and role execution contract.
- Official evidence: OpenAI model guidance and current model catalog identify Sol as frontier, Terra as balanced, Luna as efficient/high-volume; Fast/priority is premium and not universally available.
- Runtime evidence: Codex CLI `0.147.0` bundled schema exposes model/reasoning/speed metadata, while `codex doctor` proves only static config and reports failed provider reachability/state checks; active-session detection remains unknown.

## Development Stages

| Stage | Goal | Exit Evidence |
| --- | --- | --- |
| UPG-004-A | Inventory reusable run-state, binding, projection, and validation surfaces. | Exact file/API/fixture plan with no provider-neutral leakage. |
| UPG-004-B | Implement canonical selection/fallback contract and Codex advisory projection. | Focused none/analysis-only/full-recommended/resume/fallback fixtures pass. |
| UPG-004-C | Prove portable package/runtime-schema behavior and fail-closed audit boundary. | Package projection, AI-context validation, hosted checks, and fresh exact-head audit pass. |

## Role Execution Coordination

- A generic Terra Max bounded context completed the authorized inventory and implementation surface; it is not claimed as invocation of an integrated canonical role.
- If implementation is delegated, exact role/profile/session evidence must be recorded separately from static configuration.
- Final independent audit runs serially on a fixed clean head and cannot be performed by a writer of that head.

## Approval Gates

- Implementation: approved by the explicit repository-owner v0.14.0 delivery prompt.
- Delegation choice: already specified as `full-recommended`; repeat prompt is prohibited for this run.
- Fast/priority: explicitly disabled; no activation is authorized.
- Merge: requires exact-head independent audit, hosted checks, terminal-close admission, and provider read-back.

## Validation Strategy

- Validate exact modes `none`, `analysis-only`, and `full-recommended` against identical canonical stage obligations.
- Validate explicit choice suppression, ask-once state, resume behavior, unknown runtime detection, advisory mismatch, and exact consent-bound fallback evidence.
- Validate root sequential execution and fail-closed final independent audit.
- Validate Codex-only fields do not leak into canonical or Claude/Copilot contracts.

## Test Execution Contract

- Run focused deterministic fixtures first, each below 120 seconds.
- Preserve sandbox/environment failures separately and rerun only on the authorized host boundary when needed.
- Long release/full profiles require a clean immutable commit and one external terminal report.

## Spec Compliance Selection

- Activation source: Issue #208 selects contract/runtime/package fixtures rather than a problem-frame compliance run.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance fixtures and independent exact-head audit are the selected gates.

## Progress And Handoff

- Current stage: UPG-004-C package, hosted, and independent-audit admission.
- Completed stages: #207 integrated; official OpenAI mapping and local Codex runtime-schema evidence refreshed; UPG-004-A inventory and UPG-004-B contract/validator implementation passed focused validation.
- Deferred stages and reasons: Claude/Copilot runtime projection and any Fast activation require separate Issues/authorization.
- Open decisions: None; owner selections are fixed in this workflow.
- Continuation instructions: Reconcile the retained execution evidence, commit a clean exact head, obtain a fresh independent audit plus hosted admission, then merge only the admitted head.
- Target policy references: `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; `.ai/assets/skills/ai-context-upgrader/skill.yaml`; `.dev/standards/WORKFLOW-GATE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 starts from integrated #207 main `f7591d8499ade36fb88193408e434710cbf437a0`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-21-upg-004-delegation-preflight` | `main@f7591d8499ade36fb88193408e434710cbf437a0` | active-stage | `f7591d8499ade36fb88193408e434710cbf437a0` | local branch / PR pending | `2026-08-21T01:35:16+08:00` | Start authorized #208 delivery from integrated SAG-003 contracts. | Complete inventory and implementation on this branch. |

## Completion Summary

- Outcome: In progress; the contract and focused validation are complete, but no #208 completion, canonical-role invocation, PR, merge, or release claim exists yet.
- Changed artifacts: Portable delegation run contract/schema/template, upgrader spec and wrappers, Codex advisory projection, AI-context validator, focused/package fixtures, and workflow execution evidence.
- Approved requirement/specification evidence: Live Issue #208 and explicit owner authorization.
- Implementation completion evidence: Provider-neutral run-state and Codex-only advisory surfaces are implemented without transaction/provenance changes.
- Required test outcomes: Focused UPG-004 12/12, provider projection 11/11, wrapper metadata 16/16 on the normal ACL boundary, package projection 1/1, AST/YAML/diff checks, and AI-context validation passed; the sandbox wrapper attempt remains retained as blocked by `%TEMP%` ACL. Hosted and exact-head gates remain pending.
- Selected compliance evidence: Not applicable.
- Review disposition: Pending fresh exact-head independent audit.
- Validation evidence: Integrated main identity, live Issue read-back, official documentation, and local runtime-schema diagnostics.
- Workflow task state: in progress pending independent audit, hosted admission, and integration.
- Commits: workflow bootstrap pending.
- Branch / checkpoint / handoff evidence: Dedicated #208 branch from `f7591d8499ade36fb88193408e434710cbf437a0`.
- Residual risks: Static Codex config cannot prove active session state; provider reachability/state diagnostics failed and remain non-blocking unknown evidence.
