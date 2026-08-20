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
- `branch`: `codex/2026-08-21-upg-004-delegation-preflight-admission`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `in_progress`
- `created_at`: `2026-08-21T01:35:16+08:00`
- `updated_at`: `2026-08-21T02:38:13+08:00`
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
- Runtime evidence: Codex CLI `0.147.0` bundled schema exposes model/reasoning/speed metadata. A fresh `codex doctor --json` receipt reports overall `warning`, with provider, WebSocket, and state checks passing and rollout parity warning; it still does not prove the active session model, effort, or service tier, so those values remain unknown.

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

- Current stage: The clean-history replacement implementation and local focused gates are complete; its first policy-compliant commit, replacement PR, terminal declaration, exact-head audit, and hosted merge admission remain pending.
- Completed stages: #207 integration, official OpenAI and local Codex runtime-schema refresh, UPG-004 inventory, contract/validator implementation, focused/package validation, execution-evidence reconciliation, and preservation of the failed PR #230 audit and hosted evidence.
- Deferred stages and reasons: Claude/Copilot runtime projection and any Fast activation require separate Issues/authorization.
- Open decisions: None; owner selections are fixed in this workflow.
- Continuation instructions: Create and push one policy-compliant clean-history implementation commit, open the replacement draft PR, add its exact terminal declaration in a second compliant commit, obtain a fresh no-repair Sol High exact-head audit plus hosted checks, then merge only that admitted head and read back Issue #208. Project-field restoration remains outside this workflow.
- Target policy references: `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; `.ai/assets/skills/ai-context-upgrader/skill.yaml`; `.dev/standards/WORKFLOW-GATE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 records the rejected original PR #230 head. Segment 2 is a no-rewrite squash reconstruction from integrated #207 main `f7591d8499ade36fb88193408e434710cbf437a0`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-21-upg-004-delegation-preflight` | `main@f7591d8499ade36fb88193408e434710cbf437a0` | audit-failed-superseded | `5cb4c46fdd571ad692a72ae7fed42ab60820a342` | closed PR #230 | `2026-08-21T02:08:34+08:00` | Preserve the four exact-head audit blockers and five passing hosted checks without rewriting history. | Reconstruct on segment 2 with compliant commits and repaired product evidence. |
| 2 | `codex/2026-08-21-upg-004-delegation-preflight-admission` | `main@f7591d8499ade36fb88193408e434710cbf437a0` | replacement-implementation-ready | pending first commit | replacement PR pending | `2026-08-21T02:38:13+08:00` | Carry the repaired implementation, exact fallback semantics, and fresh runtime receipt as one clean-history candidate. | Commit, push, create replacement PR, then add its terminal declaration. |

## Completion Summary

- Outcome: UPG-004 implementation is locally complete on a clean-history replacement candidate. PR #230 is closed and superseded after a fresh audit found four blockers; no active terminal declaration exists until the replacement PR is created.
- Changed artifacts: Portable delegation run contract/schema/template, upgrader spec and wrappers, Codex advisory projection, AI-context validator, focused/package fixtures, and workflow execution evidence.
- Approved requirement/specification evidence: Live Issue #208 and explicit owner authorization.
- Implementation completion evidence: Provider-neutral run-state and Codex-only advisory surfaces are implemented without transaction/provenance changes.
- Required test outcomes: Focused UPG-004 18/18, provider projection 17/17, wrapper metadata 16/16 on the normal ACL boundary, package projection 1/1, AST/YAML/diff checks, and AI-context validation passed; the sandbox wrapper attempt remains retained as blocked by `%TEMP%` ACL. Replacement hosted and exact-head gates remain pending.
- Selected compliance evidence: Not applicable.
- Review disposition: PR #230 exact-head audit failed on commit-policy, missing root preflight, weak mode/fallback validation, and missing reproducible delivery-time evidence. The replacement still requires a fresh independent audit at its final declaration head; the writer does not certify its own head.
- Validation evidence: Integrated main identity, live Issue read-back, official documentation, local runtime-schema diagnostics, and `.dev/workflows/2026-08-21-upg-004-delegation-preflight/evidence/codex-runtime-preflight.yaml`.
- Workflow task state: in progress; replacement PR admission and integration remain separate.
- Commits: rejected segment 1 heads `99dcb440864c1186d6fe64701065da08a7fb143d` and `5cb4c46fdd571ad692a72ae7fed42ab60820a342` are historical evidence only; segment 2 has no commit yet.
- Branch / checkpoint / handoff evidence: Dedicated clean-history replacement branch from `f7591d8499ade36fb88193408e434710cbf437a0`.
- Residual risks: Static Codex config cannot prove active session state; fresh diagnostics are warning-only because rollout-file/state inventory differs, while active session model/effort/tier remain unknown.
