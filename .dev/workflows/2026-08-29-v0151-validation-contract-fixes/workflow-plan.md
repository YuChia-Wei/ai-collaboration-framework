# Restore v0.15.1 Validation Fingerprint And Registry Contracts

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-29-v0151-validation-contract-fixes`
- `plan_id`: `development-plan-2026-08-29-v0151-validation-contract-fixes`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-29-v0151-validation-contract-fixes`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-29T10:20:34+08:00`
- `updated_at`: `2026-08-29T10:39:30+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-29-v0151-validation-contract-fixes/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-29-v0151-validation-contract-fixes/`
- `work_item`: `https://github.com/YuChia-Wei/ai-collaboration-framework/issues/261`

## Development Objective

- Product or software outcome: deliver a cohesive v0.15.1 patch that restores fail-closed validation evidence reuse and registry/supervisor compatibility without intentionally changing the public contract.
- Current lifecycle entry point: authorized bug-fix implementation from clean `main@5fedaceef7e18b4cdcde3cb665adcc97070db2df` and live Issue #261.
- User constraints: create and read back the Issue before edits; use a dedicated branch; preserve exact-head evidence boundaries; do not use or commit the external analysis directory.
- Non-goals: push, pull request, merge, Issue or Project terminal mutation, tag, Release, publication, v0.16.0 capability work, blanket fixture classification, or subject-digest replacement for exact-head identity.

## Inputs

- Requirements: Issue #261 acceptance IDs VAL010-A1 through VAL010-A5.
- Specifications: `.ai/assets/shared/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md`, validation registry and process-supervisor contracts.
- Architecture decisions: reuse remains input-sensitive and runtime-sensitive; exact-head/provider gates remain identity-sensitive and fresh.
- Existing implementation or tests: `.ai/scripts/check-all.sh`, `.ai/scripts/validation-evidence.py`, `.ai/scripts/validation-profile-registry.sh`, `.ai/scripts/validation_process_supervisor.py`, their focused tests, and `.ai/distribution/templates/INSTALL.md`.

## Workflow-Value And Delivery Cohesion

- Mode: workflow.
- Unique state: this fresh-session delivery crosses shell, Python, registry, tests, distributed documentation, exact-head review, and a durable local commit checkpoint; Issue #261 alone cannot preserve task-level resume and evidence state.
- Cohesion: all four accepted corrections prevent false or unusable v0.15 validation outcomes, share one patch release horizon, validation boundary, reviewer, branch, and atomic rollback unit.
- Integration gate: pull request required if later authorized; no push or pull request is currently authorized.
- Proposed topology: linear, because the intended delivery is one coherent patch and no merge-node lifecycle boundary is currently authorized.

## Acceptance-To-Evidence Human Projection

The machine-readable authority is `acceptance-ledger.yaml`.

| Acceptance ID | Planned disposition | Required evidence |
| --- | --- | --- |
| VAL010-A1 | passed | canonical complete-set policy fingerprint, missing-input fail-closed test, and unavailable-identity no-reuse wiring |
| VAL010-A2 | passed | Python implementation/version/cache-tag/ABI/SOABI plus PyYAML runtime digest, cache schema 2.0.0 invalidation, and focused tests |
| VAL010-A3 | passed | explicit 60-second budgets for the three advisory checks and positive ASCII-integer registry validation |
| VAL010-A4 | passed | INSTALL readiness explanation plus diff/workflow validation |
| VAL010-A5 | pending | focused checks, source-governance validation, clean immutable commit, and fresh exact-head review evidence |

## Development Stages

### Stage 1: Validation fingerprint repair

- `stage_id`: `validation-fingerprint`
- Goal: make policy and runtime fingerprint failures disable reuse and migrate cache identity deterministically.
- Capability slot: implementation.
- Owner skill: `slice-implementer` in `generic` mode with `remediation` overlay, executed directly.
- Scope: VAL010-A1 and VAL010-A2 plus their regression tests.
- Non-goals: validator mutation-testing platform or observed dependency closure.
- Dependencies: framework-source effective-rule packet and current code/test inventory.
- Validation: focused evidence/cache/fingerprint tests and shell contract checks.
- Commit checkpoint: combine with Stage 2 after all focused validation passes.

### Stage 2: Registry and install contract repair

- `stage_id`: `registry-install-contracts`
- Goal: make every timeout supervisor-compatible and document post-init readiness truthfully.
- Capability slot: implementation.
- Owner skill: `slice-implementer` in `generic` mode with `remediation` overlay, executed directly.
- Scope: VAL010-A3 and VAL010-A4 plus their regression protection.
- Non-goals: advisory-to-enforced promotion or broader installation redesign.
- Dependencies: Stage 1 inventory and shared validation behavior.
- Validation: registry/process-supervisor focused tests, documentation checks, and `git diff --check`.
- Commit checkpoint: one coherent workflow commit after validation and workflow evidence are complete.

### Stage 3: Validation, review, and durable checkpoint

- `stage_id`: `validation-review-checkpoint`
- Goal: satisfy VAL010-A5 and record truthful terminal or blocked evidence.
- Capability slot: test-execution and review coordination.
- Owner skill: `software-development-orchestrator`; independent exact-head review remains read-only.
- Scope: focused tests, applicable source-governance checks, workflow validation, commit-policy validation, clean commit, and exact-head review.
- Non-goals: release/nightly-full execution on mutable state, hosted provider mutation, or publication.
- Dependencies: Stages 1 and 2 complete.
- Validation: target-owned focused commands first; long-running gates only from a clean immutable commit under their delegation contract.
- Commit checkpoint: required before any exact-head or long-running validation claim.

## Role Execution Coordination

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| validation-fingerprint | no applicable command/query/reactor/domain-test role | slice-implementer | direct | parent-inline generic slice; no child invocation | software-development-orchestrator / pending | `tasks/implement-validation-fingerprint.json` |
| registry-install-contracts | no applicable command/query/reactor/domain-test role | slice-implementer | direct | parent-inline generic slice; no child invocation | software-development-orchestrator / accepted | `tasks/repair-registry-and-install.json` |
| validation-review-checkpoint | independent read-only Codex review after commit | software-development-orchestrator | pending | exact-head subject does not exist until the local commit | software-development-orchestrator / pending | `tasks/validate-and-review.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | approved | User instruction in dedicated 0.15.1 conversation and Issue #261 owner-authorized outcome | none within accepted scope |

## Validation Strategy

- Requirement/spec traceability: preserve each Issue #261 acceptance ID separately in the ledger and human projection.
- Architecture validation: ensure no change collapses exact-head identity into content-sensitive reuse identity.
- Test and implementation validation: run repository-owned focused unit/contract tests before aggregate profiles.
- Review/compliance gates: spec compliance is not selected; fresh exact-head independent review is required after a clean immutable commit.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root.
- Target-owned commands: resolve exact focused commands from adjacent registered tests before execution.
- Prerequisites and environment boundary: repository Python/Bash prerequisites; no ambient credentials for deterministic validation.
- Target policy: `.ai/config/validation-routine-policy.yaml` or current tracked replacement, plus explicit lifecycle commands outside routine policy.
- Default selected levels: `unit`, `integration`.
- Conditional selected levels and activation source: release/nightly-full only if separately required after immutable commit; not authorized as publication evidence.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | validation evidence core 10/10; registry 9/9; Python compile passed |  |
| integration | passed | shell assets and workflow artifact validators passed; 125.113-second synthetic runner result retained as diagnostic-only |  |

## Spec Compliance Selection

- Selected: `no`
- Activation source: none; no problem-frame compliance gate is required by Issue #261.
- Outcome: `not-applicable`
- Coverage and evidence: not applicable by explicit selection.

## Progress And Handoff

- Current stage: `validation-review-checkpoint`.
- Completed stages: Issue creation/read-back, dedicated branch creation, validation fingerprint repair, registry timeout repair, INSTALL guidance, and short focused validation.
- Deferred stages and reasons: clean commit and fresh exact-head review await final tracked artifact validation.
- Open decisions: none inside accepted scope.
- Continuation instructions: rerun short focused checks, validate the complete commit message, create one local commit, verify a clean worktree, then run one independent read-only review against that exact commit.
- Target policy references: workflow, Git, work-management, validation-evidence lifecycle, and Issue #261.
- Registered handoff checkpoint: none; this conversation owns the active branch.
- Branch history and checkpoint handoffs: branch created from clean `main@5fedaceef7e18b4cdcde3cb665adcc97070db2df`; no push or merge.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-29-v0151-validation-contract-fixes` | `main@5fedaceef7e18b4cdcde3cb665adcc97070db2df` | local workflow start | pending | local only | `2026-08-29T10:20:34+08:00` | owner-authorized v0.15.1 work | remain on current branch |

## Completion Summary

- Outcome: pending.
- Changed artifacts: validation evidence helper/runner/tests, registry/tests, INSTALL guidance, and workflow evidence.
- Approved requirement/specification evidence: Issue #261 and this plan.
- Implementation completion evidence: VAL010-A1 through VAL010-A4 are passed in `acceptance-ledger.yaml`.
- Required test outcomes: short focused checks passed; the observed-long synthetic runner check is diagnostic-only.
- Selected compliance evidence: not applicable.
- Review disposition: pending.
- Validation evidence: pending.
- Workflow task state: two implementation tasks completed; exact-head validation/review task in progress.
- Commits: pending.
- Branch / checkpoint / handoff evidence: local branch only; no external transport authorized.
- Residual risks: exact-head review remains pending; no push, PR, hosted check, release, or publication is authorized.
