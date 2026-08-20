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
- `branch`: `codex/2026-08-20-upg-003-route-resolution-s1-admission`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-20T17:03:25+08:00`
- `updated_at`: `2026-08-20T19:21:28+08:00`
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
| UPG-003-S1 | pre-#207 generic bounded context / no canonical path | ai-context-upgrader | audit-failed, bounded repair locally validated | Terra Max performed live-contract, package-asset, package-projection, and typed-evidence repair work. Fresh Sol High audits failed prior heads; the 635abaeb audit found route/cutover receipt binding, duplicate-YAML, and candidate-authority defects. The current repair has focused tests only and is not yet a committed audit subject. | root / commit the repair, then new exact-head admission by a different fresh independent audit | `tasks/UPG-003-S1.json` |

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
| unit | passed | Host Python route resolver suite passed 20/20 after typed evidence repair, including sidecar/archive binding, validator argv and output receipts, owner approval, and symlink escape. | none |
| integration | passed | Isolated core-only extracted-package projection passed 1/1; validation registry passed 6/6 on the authorized host boundary. | Hosted exact-head checks remain an admission gate. |

## Spec Compliance Selection

- Selected: no
- Activation source: Live Issue #206 selects deterministic GWT and release gates, not a problem-frame compliance run.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance-traceable route fixtures and independent audit are the selected gates.

## Progress And Handoff

- Current stage: UPG-003-S1 passed independent exact-head audit at `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`. Draft PR #226 exists; its tracked deferred declaration requires a new exact-head audit and hosted admission before merge.
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
| 1 | `codex/2026-08-20-upg-003-route-resolution-s1-admission` | `main@ead96acb0ac4ea73a94c6de59604b47f1f78b5ae` | active-stage | `26d5ccbcd063e28df7d3cfddeb2a715c6f193644` | draft PR #226 / PR S1 | `2026-08-20T19:21:28+08:00` | Exact-head audit passed; tracked deferred declaration is being added. | Audit the declaration head, pass hosted admission, then merge S1 before branching S2 from integrated main. |

## Completion Summary

- Outcome: S1 remains in progress. Audit passed at `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`; draft PR #226 and its deferred declaration exist, while declaration-head audit, hosted admission, merge, and online read-back remain.
- Changed artifacts: Upgrade support policy, canonical matrix schema/template, read-only resolver and CLI, skill/profile registration, focused route and package-projection GWTs, validation registry, and this workflow evidence.
- Approved requirement/specification evidence: Live Issue #206 and explicit owner instructions.
- Implementation completion evidence: Resolver emits only four governed route kinds, cross-binds checksum sidecars, validator argv, canonical receipts, output bytes, and owner-approved deprecation evidence, and never accepts a target or invokes package apply. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` additionally cross-binds receipt from/to versions and ordered required cutover claims, rejects matrix duplicate keys, and uses retained canonical candidate authority bytes.
- Required test outcomes: Prior route 20/20, isolated package projection 1/1, validation registry 6/6, and shell-assets validation passed. The first full-module external attempt failed because its output capture was missing and remains failed evidence. The exact a57e484ba6456358971f86bcf3198acf04e6ac1e full-module task then failed after 156.213 seconds with GWT-014/GWT-020 fixture failures; it remains failed evidence and was not rerun unchanged. The repair committed at `14621d0c2f6bceb795d33d38f7ec86e2b607c354` passes route 24/24 in 0.895 seconds plus GWT-014 1/1 in 67.216 seconds and GWT-020 1/1 in 61.502 seconds on the normal Windows ACL boundary; those results need a fresh exact-head audit.
- Selected compliance evidence: Not applicable.
- Review disposition: Fresh exact-head independent audit passed at `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`; the later declaration commit must receive its own fresh audit.
- Validation evidence: Base identity `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; framework-source packet `b244520f8cb7653c067e2fe13a2aeef62f9974f8f345b0cac2dee3c63159ff05`; live published v0.6-v0.13 identities; historical packages have no portable validator and v0.10-v0.11 remains deferred-with-owner. Fresh Sol High audits of `f6de771bb37a6224fb09543edf911f61aa7ab2bc` and `a57e484ba6456358971f86bcf3198acf04e6ac1e` failed without repair in their audit contexts. The audit of `635abaeb532a2383dfb03cc1d13bd50e41f7e80b` likewise made no repair and found: edge receipts could be matrix-relabelled because they omitted `from_version`, `to_version`, and required cutover claims; route-matrix YAML accepted duplicate keys; and GWT-014/GWT-020 used placeholder candidate authority digests. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` contains the focused repair and requires a new audit. Failed sandbox, fixture, and external-capture attempts remain recorded and are not promoted.
- Workflow task state: in progress.
- Commits: `f6de771bb37a6224fb09543edf911f61aa7ab2bc`, `a57e484ba6456358971f86bcf3198acf04e6ac1e`, `71c4ec35ff180a70934333cdd296eb4b016050f8`, `ce0b4b6988030af1994edbbf37786fe7a7fbd952`, `635abaeb532a2383dfb03cc1d13bd50e41f7e80b`, `14621d0c2f6bceb795d33d38f7ec86e2b607c354`, and `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`.
- Branch / checkpoint / handoff evidence: Dedicated S1 admission branch `codex/2026-08-20-upg-003-route-resolution-s1-admission` continues from exact integrated main.
- Residual risks: Historical origin routes remain reconciliation-required until a later candidate supplies and proves an exact compatible edge validator; the local audit repair requires a new independent exact-head audit; Project-field restoration is owned by another conversation.
