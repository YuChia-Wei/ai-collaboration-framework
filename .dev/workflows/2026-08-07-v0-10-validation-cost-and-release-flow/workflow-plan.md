# v0.10.0 Validation Cost And Release Flow

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-07-v0-10-validation-cost-and-release-flow`
- `plan_id`: `development-plan-2026-08-07-v0-10-validation-cost-and-release-flow`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-07-v0-10-validation-cost-and-release-flow`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-07T22:12:41+08:00`
- `updated_at`: `2026-08-07T23:21:27+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-07-v0-10-validation-cost-and-release-flow/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-07-v0-10-validation-cost-and-release-flow`

## Development Objective

- Product or software outcome: Deliver, publish, and close `v0.10.0 — Validation Cost And Release Flow` with distinct validation profiles, deterministic execution evidence, package content identity, and source-only closeout.
- Current lifecycle entry point: Online work normalization and the #133 nested-locator parser repair are complete; the #96 profile implementation slice is active.
- User constraints: Online GitHub Issues are the sole work-management authority; do not implement the native-language discussion package, a real downstream upgrader pilot, product-source-tree migration, #87, #90, or a handoff semantic change. Run WSL and `gh` only outside the sandbox.
- Non-goals: Go/Rust/.NET AOT selection or prototype, native toolchain/binary, real downstream upgrade, product-source migration, Distribution CLI, Copilot projection, and existing immutable tag mutation.

## Inputs

- Requirements: `AI-框架改善分析-v0.10.0-Terra完整實作工作包.md` (owner authorization, untracked user-supplied input).
- Specifications: Work-package Sections 8–13; online Issue acceptance criteria #96, #135, #134, #57, #133, and #137.
- Architecture decisions: Current `AGENTS.md`; release publication runbook; owner decision that #75 is superseded by #96 and runner work remains a #96 slice.
- Existing implementation or tests: `.ai/scripts/check-all.sh`, package/release validators, packaging scripts/tests, workflow validators, and GitHub Actions workflows discovered per task.

## Delivery Cohesion

The approved issues share one release horizon, candidate gate, required evidence, owner authorization, and publication/rollback boundary. They therefore begin in one cohesive workflow. Implementation and source-only closeout may use separately reviewed pull requests and continuation branches when their source-only boundary or release sequencing requires it; this does not create a second workflow.

The selected integration topology is a merge commit: candidate preparation, immutable publication, and closeout are a durable release-lifecycle boundary that must remain visible in history. Every integration still requires a pull request.

## Development Stages

### Stage 1 — Online scope normalization

- `stage_id`: `V010-ISSUES`
- Goal: Bind every material v0.10.0 scope to an online Issue and project the owner authorization.
- Capability slot: `workflow-orchestration`
- Owner skill: `software-development-orchestrator`
- Scope: #75, #95, #96, #57, #97, #133, #134, #135, #136, and #137.
- Non-goals: Repository implementation or release mutation.
- Dependencies: GitHub access.
- Validation: Provider read-back of Issue state, comments, parent relation, Project #3 field values, and baseline PR state.
- Commit checkpoint: Included in the workflow bootstrap commit with task artifacts.

### Stage 2 — Validation profile and packaging-cost remediation

- `stage_id`: `V010-VAL`
- Goal: Implement #96 profile registry, runner selection/output, packaging smoke/full separation, and hot-path remediation.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Scope: Existing aggregate validation runner, profiles, CI consumers, packaging tests, and direct-entrypoint compatibility.
- Non-goals: Native-language implementation, relaxed release semantics, duplicated release item for the runner, or handoff semantic change.
- Dependencies: #96 authorization and source inspection.
- Validation: Focused profile/runner/packaging tests, Windows and WSL evidence where applicable, and hosted PR checks after review.
- Commit checkpoint: Validated core implementation pull request.
- Current result: `5a24d04` completed the local stage. Windows Git Bash `fast` passed in 24 seconds (27 selected) and `pr` passed in 49 seconds (36 selected); both omit the full package matrix.

### Stage 3 — Package content identity

- `stage_id`: `V010-PKG`
- Goal: Implement #135 tree, selected-input, payload, and artifact identity with safe evidence reuse.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Scope: Package metadata, identity/evidence validators, compatibility migration, and negative fixtures.
- Non-goals: Existing tag rewrite, product-source migration, or artifact identity conflation.
- Dependencies: #135 authorization and Stage 2 interfaces. This source-framework task has no downstream target-effective packet.
- Validation: Legacy metadata, reuse/invalidation, message-only, documentation-only, environment-class, and archive-digest tests.
- Commit checkpoint: Validated identity implementation pull request.

### Stage 4 — Deterministic execution evidence

- `stage_id`: `V010-EVAL`
- Goal: Implement #134 without claiming the unimplemented remainder of parent #95.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Validator event schema, retained-output metadata, execution dispositions, and privacy-preserving evidence output.
- Non-goals: Provider-private token data, raw conversation data, or #95 full lifecycle completion.
- Dependencies: #134 parent relation and Stage 2 runner interfaces.
- Validation: Executed/reused/not-selected/timed-out/cancelled semantics and PR/release evidence comparability.
- Commit checkpoint: Validated evidence implementation pull request.

### Stage 5 — Source-only closeout capability and release-governance reconciliation

- `stage_id`: `V010-CLOSEOUT`
- Goal: Implement #57 and #137 with package-isolation, post-tag-only boundaries, and the owner-authorized v0.10.0 tag/publication policy reconciliation.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Scope: Source-only closeout assets, release runbook/policy adjustment, package negative tests, isolated-worktree behavior, and provider read-back.
- Non-goals: Candidate preparation by the closeout capability, tag mutation of existing releases, full matrix/.NET reruns during closeout, or a permanent unbounded tag-ownership change.
- Dependencies: #57, #137, and the current release runbook.
- Validation: Source-only leakage tests, closeout profile contract, release-state validation, and separate policy/reference checks.
- Commit checkpoint: Validated source-only capability and release-governance pull request.

### Stage 6 — Candidate, publication, and records-only closeout

- `stage_id`: `V010-RELEASE`
- Goal: Create and validate a v0.10.0 candidate, merge to main, create the new immutable tag under #137, publish the GitHub Release, and complete records-only closeout.
- Capability slot: `workflow-orchestration`
- Owner skill: `software-development-orchestrator`
- Scope: Release record, notes/migration, candidate and phase gates, tag/release/read-back, Issue/Project reconciliation, and final handoff/closeout evidence.
- Non-goals: Moving/recreating any tag, full packaging matrix or .NET rerun after tag, or additional product scope.
- Dependencies: Stages 2–5 integrated to main, all required local/hosted evidence, WSL evidence, and #137 policy integration.
- Validation: `fast`, `pr`, `release`, and `closeout` profile outcomes; synthetic clean install and upgrade; Windows/WSL/hosted evidence; tag/release/assets/sidecars/archive parity read-back.
- Commit checkpoint: Candidate, release finalization, and closeout records as policy requires.

## Role Execution Coordination

No task selects a canonical sub-agent role yet. The source-framework validation task is governed directly by `ai-context-governance`, because this repository has no target-effective rule packet and #96 explicitly assigns the work to that owner skill. No delegated work is inferred from planning metadata.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| V010-VAL | no canonical implementation role selected | ai-context-governance | `not-applicable` | no implementation attempt yet | workflow parent / pending | `tasks/V010-VAL.json` |
| V010-PKG | pending exact slice mode | slice-implementer | `not-applicable` | no implementation attempt yet | workflow parent / pending | `tasks/V010-PKG.json` |
| V010-EVAL | pending exact slice mode | slice-implementer | `not-applicable` | no implementation attempt yet | workflow parent / pending | `tasks/V010-EVAL.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `approved` | Owner's `AI-框架改善分析-v0.10.0-Terra完整實作工作包.md`; online projection #96, #135, #134, #57, #133, #136, #137 | None within the authorized scope. |

## Validation Strategy

- Requirement/spec traceability: Online GitHub Issue acceptance criteria and this workflow's task bindings are the work-management authority.
- Architecture validation: Keep source-only, portable package, and release lifecycle ownership boundaries; do not change excluded handoff semantics.
- Test and implementation validation: Use target-owned Python/package/validator commands and record exact outcome/disposition. WSL and `gh` run outside the sandbox.
- Review/compliance gates: Pull-request hosted checks and release-phase validators are mandatory; spec compliance is not selected because no problem-frame contract selects it.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root.
- Target-owned commands: Exact commands discovered from current validation registry and release profile; `.NET` test commands remain selected only when the profile selects them.
- Prerequisites and environment boundary: Windows native Python and Git; WSL Python/PyYAML available outside sandbox; WSL `dotnet` is currently `blocked-by-environment` because `dotnet` is not on PATH; `gh` is authenticated outside sandbox.
- Target policy: Work package Sections 3 and 13; `.dev/operations/runbooks/AI-CONTEXT-RELEASE-PUBLICATION-RUNBOOK.MD`.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: `hosted-ubuntu` and release publication are selected by the owner work package.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | `pending` | To be recorded per selected profile. |  |
| integration | `pending` | To be recorded per selected profile. |  |

## Spec Compliance Selection

- Selected: `no`
- Activation source: No target profile, problem frame, requirement, or owner decision selects the gate.
- Outcome: `not-applicable`
- Coverage and evidence: Not applicable.

## Progress And Handoff

- Current stage: `V010-VAL`.
- Completed stages: `V010-ISSUES`.
- Deferred stages and reasons: None.
- Open decisions: WSL .NET 10.0.302 is not currently available; no environment installation or global modification is authorized implicitly. It remains a release evidence risk while Windows/hosted alternatives are evaluated.
- Continuation instructions: Complete the exact source inventory and direct runner contract before starting the first implementation patch. Before any fresh-session, host, model, runtime, push, merge, candidate, tag, publication, or finalization continuation, create and verify a registered handoff checkpoint.
- Target policy references: `AGENTS.md`, current workflow/commit/handoff policies, release runbook, and #137.
- Registered handoff checkpoint: None; no handoff has occurred.
- Branch history and checkpoint handoffs: No branch checkpoint yet.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-07-v0-10-validation-cost-and-release-flow` | `main` | none |  |  | `2026-08-07T22:12:41+08:00` | Initial authorized workflow branch | Continue V010-VAL on this branch. |

## Completion Summary

- Outcome: In progress.
- Changed artifacts: Workflow bootstrap only; the user-supplied work package remains untracked and unmodified.
- Approved requirement/specification evidence: Owner work package and online Issue/Project read-back.
- Implementation completion evidence: Pending.
- Required test outcomes: Pending.
- Selected compliance evidence: `not-applicable`.
- Review disposition: Pending.
- Validation evidence: Online Issue/Project normalization read-back; preflight recorded.
- Workflow task state: V010-ISSUES completed; V010-VAL is in progress under the #96-recommended `ai-context-governance` owner; remaining tasks are pending.
- Commits: Pending workflow-bootstrap validation.
- Branch / checkpoint / handoff evidence: Dedicated branch exists; no checkpoint.
- Residual risks: WSL .NET unavailable; #137 must be implemented before any agent-created tag.
