# PERF-001 Portable Test Fixture Acceleration Plan

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-24-portable-test-fixture-acceleration`
- `plan_id`: `development-plan-2026-08-24-portable-test-fixture-acceleration`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-24-portable-test-fixture-acceleration`
- `base_branch`: `main`
- `base_sha`: `4be33ff90de061dc1db221f60e57ff6130cab54a`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-24T22:33:23+08:00`
- `updated_at`: `2026-08-25T07:42:20+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-24-portable-test-fixture-acceleration/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-24-portable-test-fixture-acceleration/`

## Development Objective

- Product or software outcome: Implement GitHub Issue #246 (`PERF-001`) as a zero-configuration portable baseline plus one explicit opt-in accelerated fixture root, with fail-closed storage-semantics routing and privacy-safe reproducible diagnostics and benchmarks.
- Current lifecycle entry point: Accepted Issue solution contract and explicit owner authorization to implement in this independent Codex worktree.
- User constraints: Preserve default behavior, use `AI_CONTEXT_TEST_TMP_ROOT` unless tracked evidence proves a more compatible name, do not infer or install accelerated storage, keep durability and platform semantics off accelerated roots, delegate long-running validation, and perform exact-head independent audit.
- Non-goals: Push, pull request, merge, Issue or Project mutation, target-release allocation, tag, release, publication, package bytes, archive naming, global `TEMP`/`TMP`, privilege elevation, or changes to the #245 checkout/branch.

## Inputs

- Requirements: GitHub Issue #246 body and owner comments read back at `2026-08-24T22:30+08:00`; explicit implementation authorization in source task `01a02d8e-8fb8-7771-beac-b3520923e6d7` delegation.
- Specifications: The Issue #246 solution contract and acceptance checklist are normative for this delivery.
- Architecture decisions: Tracked test classification must own routing; unclassified tests retain current behavior; only proven disposable fixtures may consume the accelerated root.
- Existing implementation or tests: To be inventoried from current tracked files at base SHA `4be33ff90de061dc1db221f60e57ff6130cab54a`.

## Workflow Justification

Workflow mode preserves unique state not owned by the Issue or a single commit: cross-skill architecture/test-design/implementation transitions, long-running external validation receipts, exact-head independent audit identity, and the mandatory blocked-on-#245 integration checkpoint. These states remain independently resumable and fail closed if the subject head changes.

## Development Stages

### Stage 1 — Inventory and architecture

- `stage_id`: `inventory-design`
- Goal: Inventory benchmark surfaces and tracked test/fixture routing, then fix the smallest compatible contract and migration set.
- Capability slot: `architecture`
- Owner skill: `ddd-ca-hex-architect`
- Scope: Repository-owned test runners, fixture creation, validation profiles, and portable guidance.
- Non-goals: Moving unclassified fixtures or redefining durability/platform semantics.
- Dependencies: Current tracked files, Git, Issue #246, and freshness-verified framework-source rule evidence.
- Validation: Direct tracked-file verification, inventory evidence, and workflow artifact validation.
- Commit checkpoint: Workflow bootstrap and validated inventory/design may form one durable checkpoint.

### Stage 2 — Deterministic test design

- `stage_id`: `test-design`
- Goal: Define GWT scenarios for resolver precedence, preflight, unique run directories, containment, cleanup, routing isolation, platform normalization, diagnostics, and outcome parity.
- Capability slot: `test-design`
- Owner skill: `bdd-gwt-test-designer`
- Scope: Test scenarios and assertion points for Issue #246 acceptance.
- Non-goals: Claiming unavailable platform or RAM-disk results.
- Dependencies: Stage 1 inventory and selected architecture.
- Validation: Scenario-to-acceptance traceability.
- Commit checkpoint: Included with the coherent implementation batch unless it becomes independently resumable.

### Stage 3 — Implementation

- `stage_id`: `implementation`
- Goal: Implement resolver/preflight/containment/cleanup, tracked classification/routing, diagnostics, benchmark profile, tests, documentation, and opt-in local/CI profile.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Only tracked files required by the accepted Issue contract.
- Non-goals: Provider lifecycle, release state, unrelated refactors, or #245 work.
- Dependencies: Stages 1 and 2; explicit owner authorization already recorded.
- Validation: Narrow deterministic tests first, then affected focused profiles.
- Commit checkpoint: One or more coherent validated local commits.

### Stage 4 — Validation and benchmark

- `stage_id`: `validation`
- Goal: Run focused checks locally, then dispatch any aggregate/full/benchmark command expected or observed at 120 seconds or more to one read-only external task with one terminal delivery.
- Capability slot: `test-execution`
- Owner skill: `software-development-orchestrator`
- Scope: Target-owned commands and owner-provided Windows/WSL accelerated roots after runtime preflight.
- Non-goals: Polling, fabricated performance results, or treating blocked environments as passed.
- Dependencies: Clean immutable implementation commit.
- Validation: Canonical delegated-receipt validator and exact command outcomes.
- Commit checkpoint: Validation evidence update after terminal receipt.

### Stage 5 — Exact-head audit and integration handoff

- `stage_id`: `audit-handoff`
- Goal: Revalidate the #245-synchronized subject, obtain a fresh read-only independent audit of the exact head, and prepare a clean PR/merge-decision handoff without performing provider or main integration.
- Capability slot: `review`
- Owner skill: `code-reviewer` plus the repository-required fixed-head independent auditor role where applicable.
- Scope: Exact-head findings, workflow state, #245 overlap/resync instructions, and residual risks.
- Non-goals: Push, PR, merge, Issue closure, Project mutation, or waiting/polling for #245.
- Dependencies: Final validation commit; after any subject mutation, repeat affected validation and audit.
- Validation: Exact SHA binding, clean status, audit disposition, and handoff validator if transferred across session/runtime.
- Commit checkpoint: Final clean local checkpoint; workflow remains `in_progress` or tasks `deferred` while blocked on #245.

## Role Execution Coordination

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| inventory-design | Canonical DDD/CA/HEX route not applicable to test tooling | `ddd-ca-hex-architect` | `not-applicable` | direct scope evaluation | primary implementation task / accepted | `tasks/perf-001-inventory-design.json` |
| test-design | No role bindings | `bdd-gwt-test-designer` | `not-applicable` | direct scenario design | primary implementation task / accepted | `tasks/perf-001-test-design.json` |
| implementation | Canonical slice roles do not apply to generic Python repository tooling | `slice-implementer` | `not-applicable` | parent-inline implementation; no role invocation invented | primary implementation task / accepted | `tasks/perf-001-implementation.json` |
| audit-handoff | Fixed-head independent audit route to be resolved | `code-reviewer` or owning skill | `pending` | none | primary implementation task / pending | `tasks/perf-001-audit-handoff.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `approved` | Explicit #246 implementation delegation from source task `01a02d8e-8fb8-7771-beac-b3520923e6d7` | none |
| implementation -> push/PR/merge/provider mutation | `awaiting-approval` | Explicitly prohibited by the same delegation | Owner/management task decision after #245 integration and fresh evidence |

## Validation Strategy

- Requirement/spec traceability: Map every Issue #246 acceptance criterion to deterministic test or truthful platform/benchmark evidence.
- Architecture validation: Verify classification metadata, resolver precedence, containment, and fail-closed bypass against tracked code and runner contracts.
- Test and implementation validation: Run narrow unit/fixture tests before affected focused, fast, critical, aggregate/source-governance, and benchmark profiles.
- Review/compliance gates: Spec compliance is unselected and not applicable; exact-head independent review is mandatory.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root
- Target-owned commands: To be resolved from current runner/config inventory before execution.
- Prerequisites and environment boundary: Portable local Python/Git/Bash where available; Windows and WSL accelerated roots are explicit owner-provided inputs and must pass runtime preflight.
- Target policy: Issue #246, root `AGENTS.md`, workflow/commit/long-running validation policies.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: aggregate/source-governance and benchmark are selected by Issue #246; external delegation applies at the 120-second gate.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | pending | focused commands to be resolved | none |
| integration | pending | affected runner/profile commands to be resolved | none |
| environment-dependent benchmark | pending | Windows RAM-backed and WSL tmpfs owner-provided roots; actual preflight required | owner if reference evidence is unavailable |

## Spec Compliance Selection

- Selected: `no`
- Activation source: none
- Outcome: `not-applicable`
- Coverage and evidence: Issue #246 is the accepted solution contract; no problem-frame compliance workflow was selected.

## Progress And Handoff

- Current stage: `validation`
- Completed stages: `inventory-design`, `test-design`, `implementation`
- Deferred stages and reasons: Fresh aggregate validation, Windows/WSL benchmark, and exact-head audit remain pending after synchronizing merged #245.
- Open decisions: Cold-cache benchmark evidence remains unavailable unless the owner supplies a safe deterministic cache-reset procedure; warm runs must not be relabeled as cold.
- Continuation instructions: #245 was merged by PR #247 at `476ddfb0c12f2cf4965ea123249bf7a62363b70e` and integrated into this branch by merge commit `7f8be0248948fc691c349f27efbc07d2efdef479`. Complete fresh aggregate validation, Windows/WSL benchmark, and exact-head audit before any PR/merge decision.
- Target policy references: See workflow locator.
- Registered handoff checkpoint: none yet.
- Branch history and checkpoint handoffs: Segment 1 started from `main` at `4be33ff90de061dc1db221f60e57ff6130cab54a`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-24-portable-test-fixture-acceleration` | `main@4be33ff90de061dc1db221f60e57ff6130cab54a` | merge-from-main | `7f8be0248948fc691c349f27efbc07d2efdef479` | `origin/main@476ddfb0c12f2cf4965ea123249bf7a62363b70e` | `2026-08-25T07:41:12+08:00` | Preserve durable #246 checkpoints while consuming merged #245 | Run fresh aggregate, benchmark, and exact-head audit |

## Completion Summary

- Outcome: In progress.
- Changed artifacts: Workflow, classified fixture runtime and runner, three migrated test suites, validation profiles, deterministic tests, bilingual agent guidance, human guide, and manual opt-in CI workflow.
- Approved requirement/specification evidence: Issue #246 plus explicit owner delegation.
- Implementation completion evidence: 20 focused routing tests plus matching 86-test default and accelerated profile outcomes.
- Required test outcomes: Post-integration fixture, source-work-management, source-governance, workflow, registry, entrypoint, shell-asset, and GitHub-workflow focused checks passed; fresh aggregate and benchmarks remain pending.
- Selected compliance evidence: not applicable.
- Review disposition: pending exact-head independent audit.
- Validation evidence: pending.
- Workflow task state: inventory, test design, implementation, and validation completed; `perf-001-audit-handoff` in progress and blocked from main integration until #245 is merged and synchronized.
- Commits: Local implementation commits through `621765a18f664200b0c79e37e6fa943517281052`; #245 synchronization merge `7f8be0248948fc691c349f27efbc07d2efdef479`.
- Branch / checkpoint / handoff evidence: local dedicated branch; #245 merged into the feature branch only; no push, PR, or merge into `main`.
- Residual risks: Fresh aggregate/benchmark evidence and exact-head audit are mandatory because synchronization changed the subject head.
