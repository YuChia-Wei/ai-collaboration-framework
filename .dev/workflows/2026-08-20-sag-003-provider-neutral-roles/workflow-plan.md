# SAG-003 Provider-Neutral Capability Roles

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-sag-003-provider-neutral-roles`
- `plan_id`: `development-plan-2026-08-20-sag-003-provider-neutral-roles`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-20-sag-003-provider-neutral-roles`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-20T23:55:54+08:00`
- `updated_at`: `2026-08-21T00:45:00+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-sag-003-provider-neutral-roles/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-sag-003-provider-neutral-roles/`

## Development Objective

- Product or software outcome: Provide five reusable provider-neutral capability roles and one truthful Codex runtime projection without conflating canonical contracts, configured projections, current availability, or genuine invocation.
- Current lifecycle entry point: Inventory existing role, execution-evidence, provider-projection, runtime-schema, package, and validator surfaces before mutation.
- User constraints: Implement all five roles, keep Claude/Copilot deferred, preserve deterministic tool authority, and do not claim role existence/invocation before integration.
- Non-goals: Claude/Copilot adapters, Issue #208 opt-in policy, Project-field restoration, tag/Release/publication, or nightly activation.

## Inputs

- Requirements: Live Issue #207 and explicit repository-owner v0.14.0 delivery instructions.
- Specifications: Shared role execution contract, current specialized context-translator layering, runtime agent schemas, skill registry, and existing execution-evidence contract.
- Architecture decisions: Provider-neutral canonical contracts; provider-specific projection; skill-specific bindings; direct sequential parity; static/current/invoked state separation.
- Existing implementation or tests: #118/#119 reachability/execution evidence, current bounded workers, specialized context-translator adapter, package projection, and AI-context validators.

## Development Stages

### Stage 1

- `stage_id`: `SAG-003`
- Goal: Deliver the five canonical contracts, shared registries/bindings, Codex projection, validation, package proof, audit, and terminal Issue closeout.
- Capability slot: `ai-context-governance`
- Owner skill: `ai-context-governance`
- Scope: Mechanical evidence, reconciliation, semantic governance, evidence synthesis, and fixed-head audit roles; shared skill bindings; Codex-only runtime projection.
- Non-goals: Other provider projections, upgrade-only duplicates, or routine automatic terminal-auditor invocation.
- Dependencies: Integrated main `e27540bb34721a14d097316af8f5fd708b6982b2` and live Issue #207.
- Validation: Focused contract/runtime-schema/package tests, source AI-context validation, fresh exact-head Sol High audit, hosted checks, terminal-close admission.
- Commit checkpoint: One terminal-close PR for #207.

## Role Execution Coordination

Before #207 integrates, all delegated work remains generic pre-#207 context and is not evidence that the new canonical roles exist or were invoked.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| SAG-003 | pre-#207 generic bounded inventory and semantic-review contexts / no canonical path | ai-context-governance | completed / precommit PASS | Two Terra Max inventories and one fresh Terra Max read-only semantic review covered the candidate contracts, projection, validator, and package boundary without claiming canonical invocation. | root / create immutable implementation subject, then request fresh Sol High audit | `tasks/SAG-003.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| Live Issue #207 -> implementation | approved | Explicit repository-owner v0.14.0 delivery prompt | none |

## Validation Strategy

- Requirement/spec traceability: Map every live acceptance criterion to canonical fields, provider projection fields, skill binding, or negative fixture.
- Architecture validation: Prove provider fields cannot enter canonical contracts and configured/runtime/invoked states remain distinct.
- Test and implementation validation: Run focused schema/registry/runtime/package tests before immutable commit.
- Review/compliance gates: Fresh exact-head Sol High audit, required hosted checks, terminal-close merge admission, then online Issue/Project read-back.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root and isolated package fixtures.
- Target-owned commands: focused role/projection/schema/package validators selected by the repository validation registry.
- Prerequisites and environment boundary: Use the authorized normal Windows ACL boundary only after a concrete sandbox Temp/Git Bash environment failure.
- Target policy: Preserve failed, blocked, timed-out, and cancelled evidence; long-running validation waits for a clean immutable commit.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: hosted PR profile after exact-head audit.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | Provider projection 8/8; adapter 31/31 and wrapper 16/16 on the normal Windows ACL boundary after sandbox TEMP blocks; registry 7/7 after sandbox Git Bash signal-pipe block. | root |
| integration | passed | Provider role package projection 1/1 after retaining and repairing the first fixture-only output-collision failure; AI-context, shell-asset, workflow, AST/TOML, and diff checks passed. | root |

## Spec Compliance Selection

- Selected: no
- Activation source: Live Issue #207 selects contract/runtime/package validation rather than a problem-frame compliance run.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance-traceable fixtures and independent audit are the selected gates.

## Progress And Handoff

- Current stage: SAG-003 candidate implementation and focused validation complete; immutable commit and fixed-head audit pending.
- Completed stages: Online admission, inventories, implementation, focused validation, package/runner wiring, and precommit semantic review.
- Deferred stages and reasons: Claude/Copilot projections require separate design/validation/authorization; Issue #208 owns delegation opt-in and Codex advisory preflight.
- Open decisions: None; live owner decisions select Codex-only projection and sequential fallback.
- Continuation instructions: Record this evidence, commit the candidate, push/create the terminal-close PR, add the governed declaration, then obtain a fresh no-repair Sol High audit at the exact final head before hosted admission and merge.
- Target policy references: `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`; `.dev/standards/WORKFLOW-GATE-POLICY.md`; `.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 starts from exact integrated main `e27540bb34721a14d097316af8f5fd708b6982b2`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-sag-003-provider-neutral-roles` | `main@e27540bb34721a14d097316af8f5fd708b6982b2` | active-stage | `e27540bb34721a14d097316af8f5fd708b6982b2` | local branch / PR pending | `2026-08-20T23:55:54+08:00` | Start authorized #207 delivery without claiming pre-integration role existence. | Complete inventory, implementation, focused validation, and immutable audit subject. |

## Completion Summary

- Outcome: SAG-003 candidate implementation is locally focused-validated and precommit-reviewed; no new canonical role existence or invocation is claimed before integration.
- Changed artifacts: Five role/playbook candidates, registries/schemas, upgrader bindings, Codex-only static profiles, validators/fixtures, portable package projection, runner wiring, and synchronized derived references.
- Approved requirement/specification evidence: Live Issue #207 and explicit owner authorization.
- Implementation completion evidence: Provider-neutral/provider-specific separation, exact five-role coverage, read-only Codex profile projection, deterministic-authority enforcement, deferred provider states, and terminal-auditor selection guards pass focused validation.
- Required test outcomes: Focused local gates passed; immutable exact-head audit and hosted checks remain pending.
- Selected compliance evidence: Not applicable.
- Review disposition: Terra Max precommit semantic review PASS; final independent Sol High fixed-head audit pending.
- Validation evidence: Clean integrated base, live Issue admission, local focused pass evidence, retained environment/fixture failures, and Codex doctor partial diagnostics.
- Workflow task state: in progress.
- Commits: none.
- Branch / checkpoint / handoff evidence: Dedicated SAG-003 branch from `e27540bb34721a14d097316af8f5fd708b6982b2`.
- Residual risks: `codex doctor --json` cannot prove current-session provider availability and failed unrelated reachability/state checks; hosted gates and fresh fixed-head audit remain mandatory; #207 roles are not integrated or invoked until admitted merge.
