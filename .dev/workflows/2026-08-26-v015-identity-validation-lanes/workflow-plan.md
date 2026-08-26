# v0.15 Public Identity And Validation Lanes

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-26-v015-identity-validation-lanes`
- `plan_id`: `development-plan-2026-08-26-v015-identity-validation-lanes`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-26-v015-identity-validation-lanes`
- `base_branch`: `main`
- `base_sha`: `a1ca1d178fa193b0dc5ed3edc4c1775db45f001d`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-26T12:01:52+08:00`
- `updated_at`: `2026-08-26T12:01:52+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-26-v015-identity-validation-lanes/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-26-v015-identity-validation-lanes`
- `work_items`: `GitHub Issues #250 and #252`
- `constraint_only_work_item`: `GitHub Issue #254`

## Development Objective

- Product or software outcome: deliver one cohesive local implementation of the v0.15 public identity migration and its fast, medium, and long validation lanes, ready for an owner pull-request decision.
- Current lifecycle entry point: authorized implementation from current `origin/main`, consuming integrated #251 process instrumentation and #249/#253 validation guardrails.
- User constraints: preserve all v0.14-and-earlier public bytes and names; use only a synthetic v0.15 candidate in ignored output; keep platform and actual-execution outcomes truthful; stop before every provider, release, publication, allocation, CLI, registry, installer, or external-repository mutation.
- Non-goals: complete #254, implement #213, publish v0.15, push, create a pull request, merge, close Issues, mutate Project fields, tags, Releases, assets, or external toolchains.

## Delivery Cohesion Decision

#250 and #252 are one delivery because they share the version-aware identity outcome, branch, package/upgrade implementation, validation environments, owner/reviewer boundary, v0.15 release horizon, and an acceptable atomic rollback boundary. #254 remains a later integrated-main constraint and is not a workflow completion target.

## Inputs

- Requirements: live GitHub Issue #250 and #252 bodies, labels, comments, and Project state read back on `2026-08-26`; owner delegation in source task `01a036af-3b1f-7283-97ab-eb6b7caabf93`.
- Specifications: owner naming contract and three validation-lane contract in the delegation; tracked package, upgrade, release, validation-freeze, and agent-execution contracts.
- Architecture decisions: explicit version-aware identity selection; no filename guessing or dual current canonical identity; separate synthetic and actual execution evidence; real-storage durability lane.
- Existing implementation or tests: historical #250 head `2497597b17a00a7bebcee36c4ae0fb3a97a977a2` is discovery evidence only and requires semantic reconciliation against this workflow base.

## Development Stages

### Stage 1 - ID-002 Semantic Integration

- `stage_id`: `ID002-001`
- Goal: reconcile and integrate the v0.15 public identity registry, schemas, validators, consumers, workflows, documentation, tests, and v0.14-to-v0.15 route without regressing integrated main contracts.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Dependencies: current-main graph/fallback evidence; framework-source effective-rule packet; #251 Git snapshot/process instrumentation.
- Validation: identity, package, route, release-note, version-governance, repository-identity, source-entrypoint, workflow, and diff checks.
- Commit checkpoint: coherent validated identity integration.

### Stage 2 - VAL-009 Validation Lanes

- `stage_id`: `VAL009-001`
- Goal: implement independently executable fast identity/archive, medium clean-install, and long actual published-v0.14 to synthetic-v0.15 durability commands with mutually exclusive terminal outcomes.
- Capability slot: `implementation`
- Owner skill: `software-development-orchestrator`
- Dependencies: Stage 1 identity matrix; integrated #251 metrics; #249 freeze/reuse and #253 packet/lease/ledger/retry contracts.
- Validation: deterministic lane tests, budgets, receipt/digest/snapshot/process/cleanup assertions, retry fingerprints, and aggregate non-projection tests.
- Commit checkpoint: coherent validated lane implementation.

### Stage 3 - Frozen Validation And Independent Audit

- `stage_id`: `ID002VAL009-VAL-001`
- Goal: freeze a clean immutable head, run focused gates, dispatch required long read-only validation through one event wait, obtain a fresh exact-head independent audit, and produce truthful PR-decision evidence.
- Capability slot: `test-execution`
- Owner skill: `software-development-orchestrator`
- Dependencies: Stages 1 and 2 committed; schema-valid packet, exclusive lease, acceptance ledger, and graph-freshness record.
- Validation: fast/medium/long terminal records, Windows/Linux classification, exact-head audit, workflow/commit/source governance, clean status.
- Commit checkpoint: final tracked evidence before the always-fresh exact-head audit; ignored terminal outputs do not mutate the subject.

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `approved` | owner delegation and live Issues #250/#252 | none |
| local completion -> push/PR/merge/provider/release/publication | `awaiting-approval` | owner explicitly retained each action | owner decision after local handoff |

## Validation Strategy

- Preserve separate #250 and #252 acceptance IDs in `acceptance-map.yaml` and `acceptance-mapping.md`; terminal receipts live only in declared ignored validation roots.
- Run the narrowest focused identity and lane checks first. A fast or medium pass never satisfies actual-upgrade acceptance.
- Treat `passed`, `failed`, `blocked-by-environment`, `not-applicable`, and `deferred-with-owner` as mutually exclusive. A required missing Windows or Linux trusted run keeps #254 unsatisfied.
- Freeze only after tracked mutation and focused validation, then use a validated packet, exclusive tracked-writer lease, read-only delegated task, one parent event wait, and one schema-valid terminal report.
- Exact-head audit is always fresh; any later tracked mutation invalidates it.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root of this dedicated worktree
- Target-owned commands: three new lane entrypoints plus their focused deterministic tests and existing package/upgrade validators
- Prerequisites and environment boundary: Python and Bash as resolved by repository entrypoints; real storage for durability; no ambient GitHub credentials for deterministic checks
- Target policy: Issues #250/#252 and repository validation/agent guardrails
- Default selected levels: `unit`, `integration`, `environment-dependent`

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | `not-applicable` | pending implementation and selection | none |
| integration | `not-applicable` | pending implementation and selection | none |
| environment-dependent | `not-applicable` | pending trusted Windows/Linux run | owner if a platform remains unavailable |

## Spec Compliance Selection

- Selected: `no`
- Activation source: none
- Outcome: `not-applicable`
- Coverage and evidence: no problem-frame compliance gate selected.

## Progress And Handoff

- Current stage: `ID002-001`
- Completed stages: isolated worktree and live provider/base read-back.
- Deferred stages and reasons: #254 integrated-main release-readiness remains outside this local delivery.
- Open decisions: none for authorized implementation; push/PR/merge/release actions remain owner-controlled.
- Continuation instructions: resume from this branch, locator, current task, acceptance mapping, and Git evidence; do not depend on hidden chat state.
- Target policy references: root `AGENTS.md`, workflow policies, agent execution guardrails, and live Issues #250/#252/#254.
- Registered handoff checkpoint: none yet.
- Branch history and checkpoint handoffs: segment 1 started from verified `origin/main@a1ca1d178fa193b0dc5ed3edc4c1775db45f001d`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-26-v015-identity-validation-lanes` | `main@a1ca1d178fa193b0dc5ed3edc4c1775db45f001d` | local isolated start | pending | local only | `2026-08-26T12:01:52+08:00` | cohesive #250/#252 delivery | continue this branch |

## Completion Summary

- Outcome: pending.
- Changed artifacts: workflow bootstrap only.
- Approved requirement/specification evidence: owner delegation plus live Issues #250/#252.
- Implementation completion evidence: pending.
- Required test outcomes: pending.
- Selected compliance evidence: not applicable.
- Review disposition: pending exact-head independent audit.
- Validation evidence: pending.
- Workflow task state: one in progress, two pending.
- Commits: pending.
- Branch / checkpoint / handoff evidence: isolated local branch; no push or PR.
- Residual risks: trusted Windows and Linux actual-upgrade evidence may remain blocked/deferred; any such state prevents #254 readiness.
