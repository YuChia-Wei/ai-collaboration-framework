# UPG-003 Retained-Origin Multi-Hop Upgrade

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-upg-003-multi-hop-upgrade`
- `plan_id`: `development-plan-2026-08-20-upg-003-multi-hop-upgrade`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-20-upg-003-route-resolution-s1`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-20T17:03:25+08:00`
- `updated_at`: `2026-08-20T17:43:00+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/`

## Development Objective

- Product or software outcome: Preserve supported v0.6.0, v0.9.0, and immediate-predecessor upgrades behind one user operation while resolving exact routes before mutation.
- Current lifecycle entry point: S1 read-only support policy, matrix, resolver, package projection, and fail-closed route evidence.
- User constraints: Use one online Issue #206 and this one technical workflow across three sequential PRs; S1 and S2 defer closure, S3 terminal-closes #206.
- Non-goals: Target mutation in S1; duplicating #200 transactions or #203 remediation/finalization; changing historical backlog/roadmap; Project-field restoration; tag, Release, publication, or nightly activation.

## Inputs

- Requirements: Live Issue #206, open release-coordination Issue #222, and explicit repository-owner v0.14.0 instructions.
- Specifications: Existing package/migration schemas, checksums, validators, provenance and semantic-customization contracts.
- Architecture decisions: Four exact route kinds; proven direct first unless a semantic cutover would be bypassed; ambiguity and missing assets fail before mutation; deprecation requires explicit owner evidence.
- Existing implementation or tests: #200 durable package apply, #201 package closure, #203 single-hop remediation correctness, and published release assets.

## Development Stages

### Stage 1

- `stage_id`: `UPG-003-S1`
- Goal: Deliver the support policy, machine-readable support matrix, and read-only route resolver.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Immediate predecessor, v0.9.0, and v0.6.0 origins; direct, orchestrated-multi-hop, reconciliation-required, unsupported; exact edges/assets/cutovers; ambiguity, missing-asset, bypass, and deprecation gates.
- Non-goals: Target mutation, transaction sequencing, resume, rollback, or final provenance.
- Dependencies: Integrated #200, #201, #203 and live published release identities.
- Validation: Focused route GWTs, isolated package projection, source governance, exact-head independent audit, hosted checks, deferred Issue read-back.
- Commit checkpoint: One deferred PR with `Refs #206`; #206 remains open because S2 transaction and S3 v0.14 candidate proof remain.

### Stage 2

- `stage_id`: `UPG-003-S2`
- Goal: Compose one user operation from immutable per-hop transactions with interruption, resume, rollback, and no mixed provenance.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Compose S1 with #200, #201, and #203; retain per-hop package, manifest, checksum, validator, decision, and receipt evidence.
- Non-goals: Final v0.14.0 source candidate or Issue closure.
- Dependencies: Merged S1 deferred PR.
- Validation: Focused multi-hop transaction, interruption, resume mismatch, rollback, cutover, and validation-disagreement GWTs; exact-head independent audit and hosted checks.
- Commit checkpoint: One deferred PR with `Refs #206`; #206 remains open pending S3 release proof.

### Stage 3

- `stage_id`: `UPG-003-S3`
- Goal: Instantiate and prove the governed v0.14.0 source candidate across retained origins.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Release matrix, notes, migration guide, phase checks, route evidence, exact candidate package and retained-origin proof.
- Non-goals: Tag, Release, asset/package publication, or coordination-Issue closure.
- Dependencies: Merged #203, #205, #207, #208 and S1/S2.
- Validation: Candidate package, v0.13/v0.9/v0.6 routes, release profile, provider/delegation paths, fixed-head audit, hosted provider preflight.
- Commit checkpoint: One terminal-close PR for #206; coordination Issue #222 remains open.

## Role Execution Coordination

Before #207 integrates, every delegated context is generic and is not evidence that #207 canonical roles exist or were invoked.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| UPG-003-S1 | pre-#207 generic bounded context / no canonical path | ai-context-upgrader | completed-current-slice | Terra Max performed live-contract, package-asset, package-projection, and code-surface work; root repaired and verified the core resolver. | root / exact-head admission only after fresh independent audit | `tasks/UPG-003-S1.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| Issue contract -> S1 implementation | approved | Explicit repository-owner v0.14.0 delivery prompt authorizes #206 S1/S2/S3 implementation, PR, audit, and merge. | none |

## Validation Strategy

- Requirement/spec traceability: Bind every S1 owner requirement to matrix fields, resolver outcomes, or a fail-closed GWT.
- Architecture validation: Keep resolution read-only and reuse, never duplicate, package/transaction/remediation authority.
- Test and implementation validation: Run focused deterministic route tests first, then isolated package projection and clean immutable hosted validation.
- Review/compliance gates: Fresh exact-head Sol High independent audit, required hosted checks, live merge admission, merge at admitted head, then #206 open/In-progress read-back.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root or isolated package fixture selected by repository tests.
- Target-owned commands: focused route resolver/schema/package tests plus repository-owned validation profiles.
- Prerequisites and environment boundary: Follow the existing ignored CLI routing binding only when a selected command crosses the sandbox boundary.
- Target policy: Preserve first failures/timeouts; long-running validation requires a clean immutable commit and one external task.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: `release` only in S3 candidate proof.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | Host Python route resolver suite passed 13/13, including direct, multi-hop, deferred edge, ambiguity, asset failure, cutover, deprecation, and mutation-sentinel cases. | none |
| integration | passed | Isolated core-only extracted-package projection passed 1/1; validation registry passed 6/6 on the authorized host boundary. | Hosted exact-head checks remain an admission gate. |

## Spec Compliance Selection

- Selected: no
- Activation source: Live Issue #206 selects deterministic GWT and release gates, not a problem-frame compliance run.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance-traceable route fixtures and independent audit are the selected gates.

## Progress And Handoff

- Current stage: UPG-003-S1 final local admission before commit and independent audit.
- Completed stages: Live Issue/Project/PR read-back, exact existing-surface inventory, route contract, resolver, CLI, portable projection, focused source tests, and isolated package test.
- Deferred stages and reasons: S2 waits for merged S1; S3 waits for S2 plus #207/#208 integration.
- Open decisions: None for S1; unavailable or ambiguous assets become reconciliation-required rather than inferred.
- Continuation instructions: Complete S1 on the current branch, deliver one deferred PR, keep #206 open, then create a fresh S2 branch from integrated main while retaining this workflow.
- Target policy references: `.ai/assets/skills/ai-context-upgrader/skill.yaml`; `.dev/standards/WORKFLOW-GATE-POLICY.md`; `.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 starts from clean integrated main `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-upg-003-route-resolution-s1` | `main@ead96acb0ac4ea73a94c6de59604b47f1f78b5ae` | active-stage | pending | local / PR S1 | `2026-08-20T17:03:25+08:00` | Read-only route resolution must integrate before transaction composition. | Complete S1, then branch S2 from integrated main. |

## Completion Summary

- Outcome: S1 implementation and focused validation complete; commit, exact-head audit, hosted checks, PR merge, and online read-back remain.
- Changed artifacts: Upgrade support policy, canonical matrix schema/template, read-only resolver and CLI, skill/profile registration, focused route and package-projection GWTs, validation registry, and this workflow evidence.
- Approved requirement/specification evidence: Live Issue #206 and explicit owner instructions.
- Implementation completion evidence: Resolver emits only four governed route kinds, binds raw matrix and exact selected edge evidence, and never accepts a target or invokes package apply.
- Required test outcomes: Route 13/13; isolated package projection 1/1; validation registry 6/6; shell-assets validation passed.
- Selected compliance evidence: Not applicable.
- Review disposition: Pending fresh exact-head independent audit.
- Validation evidence: Base identity `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; framework-source packet `b244520f8cb7653c067e2fe13a2aeef62f9974f8f345b0cac2dee3c63159ff05`; live published v0.6-v0.13 identities; historical packages have no portable validator and v0.10-v0.11 remains deferred-with-owner; focused passing results above. Failed sandbox/fixture attempts remain recorded in the task artifact and are not promoted.
- Workflow task state: in progress.
- Commits: pending.
- Branch / checkpoint / handoff evidence: Dedicated S1 branch created from exact integrated main.
- Residual risks: Historical origin routes remain reconciliation-required until a later candidate supplies and proves an exact compatible edge validator; Project-field restoration is owned by another conversation.
