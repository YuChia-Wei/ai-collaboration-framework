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
- `branch`: `codex/2026-08-08-v0-10-release-candidate`
- `base_branch`: `main`
- `branch_segment`: `4`
- `status`: `active`
- `created_at`: `2026-08-07T22:12:41+08:00`
- `updated_at`: `2026-08-08T01:43:37+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-07-v0-10-validation-cost-and-release-flow/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-07-v0-10-validation-cost-and-release-flow`

## Development Objective

- Product or software outcome: Deliver, publish, and close `v0.10.0 — Validation Cost And Release Flow` with distinct validation profiles, deterministic execution evidence, package content identity, and source-only closeout.
- Current lifecycle entry point: PR #138 and PR #139 are merged on `main` at `697061d51f4e4c3308e36902095c64b78200daf0`; this fresh continuation branch owns the candidate, publication, and records-only closeout stages.
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
- Current result: `703cead` completed the repaired local stage. Windows Git Bash `fast` passed in 24 seconds (27 selected) and `pr` passed in 49 seconds (36 selected); both omit the full package matrix.

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
- Current result: `e78a66c` records tree and fingerprint identity while preserving legacy reader compatibility; message-only and unselected-documentation fixtures remain eligible, while payload and profile configuration changes invalidate identity.

### Stage 4 — Deterministic execution evidence

- `stage_id`: `V010-EVAL`
- Goal: Implement #134 without claiming the unimplemented remainder of parent #95.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Scope: Validator event schema, retained-output metadata, execution dispositions, and privacy-preserving evidence output.
- Non-goals: Provider-private token data, raw conversation data, or #95 full lifecycle completion.
- Dependencies: #134 parent relation, Stage 2 runner interfaces, and #135 identity fields. This source-framework task has no downstream target-effective packet.
- Validation: Executed/reused/not-selected/timed-out/cancelled semantics and PR/release evidence comparability.
- Commit checkpoint: Validated evidence implementation pull request.
- Current result: `17a4f66` records privacy-preserving per-validator evidence, cache eligibility, retained-output metadata, and distinct timeout/reuse dispositions. Windows `fast` passed 27/27 in 24 seconds, an unchanged run reused 27/27 in 3 seconds, the synthetic runner suite passed 35/35, and WSL `fast` passed 27/27 in 192 seconds with one budget advisory.

### Stage 5 — Source-only closeout capability and release-governance reconciliation

- `stage_id`: `V010-CLOSEOUT`
- Goal: Implement #57, #133, and #137 with package-isolation, online-Issue binding, post-tag-only boundaries, and the owner-authorized v0.10.0 tag/publication policy reconciliation.
- Capability slot: `implementation`
- Owner skill: `ai-context-governance`
- Scope: Source-only closeout assets, source-repository online-Issue policy, release runbook/policy adjustment, package negative tests, isolated-worktree behavior, and provider read-back.
- Non-goals: Candidate preparation by the closeout capability, tag mutation of existing releases, full matrix/.NET reruns during closeout, or a permanent unbounded tag-ownership change.
- Dependencies: #57, #133, #137, and the current release runbook.
- Validation: Source-only leakage tests, closeout profile contract, release-state validation, and separate policy/reference checks.
- Commit checkpoint: Validated source-only capability and release-governance pull request.
- Current result: `f7904bf` implements the source-only capability, package exclusions, required closeout profile, online-Issue binding policy, and v0.10.0-only new-tag exception; `f76ae17` reconciles the governed direct-entrypoint count and reserves its blocked-by-environment exit code. The WSL closeout profile selected and executed its required contract. The WSL aggregate-runner fixture remains a pre-existing test-environment exception (clock stub / intentionally stripped PATH); it is not a selected closeout profile gate.

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
| V010-PKG | no canonical implementation role selected | ai-context-governance | `not-applicable` | identity stage completed in `e78a66c` | workflow parent / accepted | `tasks/V010-PKG.json` |
| V010-EVAL | no canonical implementation role selected | ai-context-governance | `not-applicable` | evidence stage completed in `17a4f66` | workflow parent / accepted | `tasks/V010-EVAL.json` |

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

- Current stage: `V010-RELEASE`.
- Completed stages: `V010-ISSUES`, `V010-VAL`, `V010-PKG`, `V010-EVAL`, and `V010-CLOSEOUT`.
- Deferred stages and reasons: None.
- Open decisions: WSL .NET 10.0.302 is not currently available; no environment installation or global modification is authorized implicitly. It remains a release evidence risk while Windows/hosted alternatives are evaluated.
- Continuation instructions: The candidate PR #140 is merged as `5878f213b50bdbb4b3123a60525cdc206fd5be04`; the owner-authorized annotated `v0.10.0` tag and GitHub Release are published. Push and merge the records-only closeout PR, then reconcile canonical GitHub Issues and Project #3. Before any fresh-session, host, model, runtime, push, merge, candidate, tag, publication, or finalization continuation, create and verify a registered handoff checkpoint.
- Target policy references: `AGENTS.md`, current workflow/commit/handoff policies, release runbook, and #137.
- Registered handoff checkpoint: `.dev/workflows/2026-08-07-v0-10-validation-cost-and-release-flow/handoff-checkpoints/V010-RELEASE-finalization.yaml` pins published-records commit `3815a93f07634872e646f6f7817b8b7280826b1b` after hosted finalization and records-only closeout validation. The prior candidate checkpoints remain registered historical evidence.
- Branch history and checkpoint handoffs: Segment 3 merged as PR #139; segment 4 has a refreshed release-candidate checkpoint and may push PR #140's focused CI repair for hosted revalidation.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-07-v0-10-validation-cost-and-release-flow` | `main` | pushed format-invalid checkpoint | `0c4d21c` | `origin/codex/2026-08-07-v0-10-validation-cost-and-release-flow` | `2026-08-08T00:29:00+08:00` | Preserve pushed evidence without rewriting it. | Rebuild the same stages on segment 2. |
| 2 | `codex/2026-08-08-v0-10-core-repair` | `main` | active repair continuation | `a7fba5c` | local | `2026-08-08T00:30:00+08:00` | Current validator requires structured bodies that the pushed checkpoint lacks. | Validate and push this branch for the core PR. |
| 3 | `codex/2026-08-08-v0-10-closeout` | `main` at `aeaa9c1` | source-only closeout checkpoint plus hosted-CI repair | `f7904bf`, `f76ae17` | local | `2026-08-08T01:25:00+08:00` | Core PR #138 is merged; #57/#133/#137 are implemented and their direct-entrypoint contract is repaired for hosted integration. | Push, merge, then start the release-candidate continuation from updated main. |
| 4 | `codex/2026-08-08-v0-10-release-candidate` | `main` at `697061d` | repaired release-candidate handoff | `6f8072e874a73ae696228d2acf9d6aaa16e3c974` | local | `2026-08-08T13:25:00+08:00` | PR #140 exposed missing Actions token wiring for live Issue read-back; focused repair and final candidate gates passed. | Commit and push refreshed checkpoint, then wait for PR #140 hosted checks. |
| 5 | `codex/2026-08-08-v0-10-closeout-records` | `main` at `5878f213` | post-tag records-only finalization | `3815a93f07634872e646f6f7817b8b7280826b1b` | local | `2026-08-08T14:03:56+08:00` | v0.10.0 is tagged and published; governed registry and Release body now agree. | Commit/push the finalization checkpoint, then merge the records-only closeout PR. |

## Completion Summary

- Outcome: In progress.
- Changed artifacts: Workflow bootstrap only; the user-supplied work package remains untracked and unmodified.
- Approved requirement/specification evidence: Owner work package and online Issue/Project read-back.
- Implementation completion evidence: #96/#135/#134 core stages are merged in PR #138; #57/#133/#137 source-only closeout and its hosted-CI contract repair are merged in PR #139 as `697061d51f4e4c3308e36902095c64b78200daf0`; release records/publication remain pending.
- Required test outcomes: Windows `release` 52/52 and `pr` 37/37 passed on repaired candidate `6f8072e`; targeted GitHub workflow contract tests 7/7 and WSL `closeout` 1/1 passed. Earlier fast 27/27 evidence remains valid; WSL `.NET` remains blocked-by-environment and was not selected by the WSL closeout profile.
- Selected compliance evidence: `not-applicable`.
- Review disposition: Pending.
- Validation evidence: Candidate phase passed with live online Issue read-back at `6f8072e874a73ae696228d2acf9d6aaa16e3c974`; a fresh critical gate passed with 52 selected checks and 0 failures/blocks.
- Workflow task state: V010-ISSUES, V010-VAL, V010-PKG, V010-EVAL, and V010-CLOSEOUT completed; V010-RELEASE is in progress under `software-development-orchestrator`.
- Commits: `0d40533`, `703cead`, `3e11779`, `e78a66c`, `f28f3fb`, `17a4f66`, `a7fba5c`, `f7904bf`, and `f76ae17` reconstruct the validated workflow stages with current commit-policy bodies.
- Branch / checkpoint / handoff evidence: The refreshed candidate handoff checkpoint pins the exact repaired candidate commit; its containing commit must be created next.
- Residual risks: WSL .NET remains unavailable; actual candidate/tag/publication must not begin until the source-only PR is merged. The WSL aggregate-runner fixture has its independent clock/PATH test limitations, while the selected WSL closeout profile passes.
