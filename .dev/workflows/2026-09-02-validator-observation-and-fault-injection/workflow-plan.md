# Validator Observation And Incident Fault-Injection Plan

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-02-validator-observation-and-fault-injection`
- `plan_id`: `development-plan-2026-09-02-validator-observation-and-fault-injection`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-02-validator-observation-and-fault-injection`
- `base_branch`: `main`
- `base_commit`: `c7f348694421048245da824dd79742372179f730`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-09-02T22:43:57+08:00`
- `updated_at`: `2026-09-02T23:21:04+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-09-02-validator-observation-and-fault-injection/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-09-02-validator-observation-and-fault-injection/`

## Development Objective

- Product or software outcome: Deliver Issues [#268](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/268) and [#267](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/267) as one v0.16.0 safety-precondition delivery while preserving their independent acceptance outcomes.
- Current lifecycle entry point: Owner-authorized implementation from a clean worktree at the verified `main` head.
- User constraints: Complete #268 first, then use #267 to falsify the validation chain; create local durable commits only.
- Non-goals: #270 production manifest/rebind implementation, reuse pilot enablement, push, pull request, merge, release/publication, Issue closure, or terminal Project mutation.

## Authority And Preflight

- Live GitHub read-back on 2026-09-02 found #267 and #268 open, Project status `Inbox`, and target release `v0.16.0`; their Issue bodies are the acceptance authority.
- Live `origin/main` and the new worktree both resolved to `c7f348694421048245da824dd79742372179f730`; the worktree was clean before branch creation.
- The owner authorization is the source-task delegation from thread `01a05526-95b8-7723-b23f-50bba311ce06`, which expressly authorizes branch/workflow creation, accepted-scope repository mutation, validation, and local commits.
- Issue #270 owner decision [comment 5478024060](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/270#issuecomment-5478024060) and read-only design checkpoint `3df455bd0ae6502b863990fd6aa104239d6f86ed` establish dependency-first sequencing and the no-pilot boundary. The commit is not cherry-picked.
- Effective-rule attempt 1 used an unsupported `source` technology profile and failed with `source-rule-selection`; after correcting the request to the repository's exact `dotnet-backend` source catalog route, the framework-source packet resolved with `loaded_rule_ids=[AICTX-EVIDENCE-001]` and packet digest `7d3cdae66882a5669daf7813f17353292137abcc77b126a8ca329ac1a8d328da`.
- Code graph: a moderate exact-baseline index named `ai-collaboration-framework-1dcf-c7f3486` indexed 30,053 nodes and 33,127 edges, but explicitly excluded `.ai/scripts`, `.ai/assets`, and `.ai/evaluation/fixtures`; direct tracked-file fallback is authoritative for those paths.
- Routine validation: `.dev/project-config.yaml` is absent at the verified base, so the orchestrator default is `manual`; no routine command is auto-selected. Explicit Issue-owned tests and lifecycle validation remain selected.

## Delivery Cohesion

One workflow and branch are used because #267 and #268 share the same safety outcome, base, release horizon, validation infrastructure, reviewer/owner boundary, and acceptable atomic rollback. Separate ledgers retain every acceptance identifier and evidence digest; one aggregate success flag is prohibited.

## Inputs

- Requirements: live Issue #268 and live Issue #267 bodies.
- Specifications: #270 owner-decision comment and the read-only design at `3df455bd0ae6502b863990fd6aa104239d6f86ed`.
- Architecture decisions: extend `.ai/evaluation/` and registered validation surfaces; observation is a lower bound and cannot shrink declarations; always-fresh gates remain fresh.
- Existing implementation or tests: `.ai/evaluation/`, `.ai/scripts/validate-ai-behavior-evaluation.py`, `.ai/scripts/tests/test_ai_behavior_evaluation.py`, `.ai/scripts/check-all.sh`, and `.ai/scripts/validation-profile-registry.sh`.

## Development Stages

### Stage 1 — VAL-012 bounded dependency observation

- `stage_id`: `VAL012-implementation`
- Goal: Observe bounded file, subprocess, Git, environment, and runtime signals and compare them with declarations using privacy-safe lower-bound reports.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Issue #268 production harness, schema/fixtures, focused tests, and registered validation surface.
- Non-goals: complete transitive closure claims, automatic declaration edits/removal, or reuse enablement.
- Dependencies: live Issue authority, resolved effective-rule packet, existing validation registry/evidence contracts.
- Validation: focused unit tests, representative harness fixtures, schema/registry checks, and tracked-worktree comparison.
- Commit checkpoint: one validated local commit when every VAL012 acceptance is evidenced.

### Stage 2 — VAL-011 incident-derived fault injection

- `stage_id`: `VAL011-implementation`
- Goal: Add deterministic critical known-incident mutants and exploratory reporting, with a gate that fails on any surviving critical mutant.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Issue #267 mutant corpus, runner/schema integration, focused tests, and release/nightly registration.
- Non-goals: stochastic model/judge evaluation, mutation of tracked source during execution, or #270 pilot enablement.
- Dependencies: completed VAL-012 stage and its lower-bound/blind-spot vocabulary.
- Validation: focused mutation tests, injected critical-survivor negative test, deterministic corpus validation, registry checks, and tracked-worktree comparison.
- Commit checkpoint: one validated local commit when every VAL011 acceptance is evidenced.

## Role Execution Coordination

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| VAL012-implementation | all slice role bindings | slice-implementer | `not-applicable` | Generic Python validation-tooling slice; no domain/use-case role applies. | primary Codex / accepted after 9 focused and 10 registry tests passed | `tasks/VAL012-implementation.json` |
| VAL011-implementation | mutation-testing-sub-agent / `.ai/assets/sub-agent-role-prompts/mutation-testing-sub-agent/sub-agent.yaml` | slice-implementer | `in-progress` | Owner-authorized mutation-test implementation; direct inline execution is selected because no child delegation was requested. | primary Codex / pending | `tasks/VAL011-implementation.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `approved` | 2026-09-02 source-task owner delegation | none within #267/#268 accepted scope |
| #267/#268 completion -> #270 production implementation or pilot | `awaiting-approval` | explicit user exclusion and #270 owner comment | separate future authorization required |

## Validation Strategy

- Requirement/spec traceability: maintain `acceptance-ledger.val-012.yaml` and `acceptance-ledger.val-011.yaml` independently.
- Architecture validation: confirm lower-bound observation semantics and unchanged always-fresh admission boundaries.
- Test and implementation validation: run the new focused test modules first, then existing AI-behavior/registry/lifecycle validators affected by the changed paths.
- Review/compliance gates: self-review against both ledgers and repository policies; spec compliance remains unselected and `not-applicable`; no independent fixed-head audit is claimed.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root
- Target-owned commands: focused Python unittest modules and registered validation entrypoints introduced or changed by each stage.
- Prerequisites and environment boundary: Python 3.11+, PyYAML, Git, and Bash only where the registry integration is exercised; no credentials.
- Target policy: Issue acceptance plus `.ai/scripts/validation-profile-registry.sh` and affected repository validators.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: release/nightly lifecycle registration is validated structurally; no release profile execution is authorized or selected in this workflow.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | `passed-for-VAL012` | 9 of 9 bounded dependency observation tests passed at `d8105e3dc038880d70803383a8928fc017a9f2f1`; VAL011 remains pending | none |
| integration | `passed-for-VAL012` | 10 of 10 registry tests, 3 of 3 source-entrypoint tests, shell-asset validation, and clean exact-head status passed; VAL011 remains pending | none |

## Spec Compliance Selection

- Selected: `no`
- Activation source: none; no problem-frame compliance gate was requested.
- Outcome: `not-applicable`
- Coverage and evidence: not applicable.

## Acceptance-To-Evidence Human Projection

### Issue #268 / VAL-012

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| VAL012-A1 | passed | `24d0bb6cc1ee86a6131bc23ee5d451000a178ea90f97c32852924cbae4f1ac28` |
| VAL012-A2 | passed | `546934cddc9f418bc5e693400202d789b07f859ac87bf7678aed50b3b163f7fe` |
| VAL012-A3 | passed | `a18734f11acc76c4a34eef1fa3d275bb908b6785984ddf1401dfe948049f24a1` |
| VAL012-A4 | passed | `4c5252c8f2f17e83a4f9cb1912b690abc35ab21568860972567e25c980dcd2b5` |
| VAL012-A5 | passed | `184abdda3bd2f9c098ed57fcfd89971c706319ae1d1fc247ae48abd4215a5c5c` |
| VAL012-A6 | passed | `6461fbd488becf5777d1c1ed3974eeae63bac4ebf018cdd5b808102411bd614f` |

### Issue #267 / VAL-011

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| VAL011-A1 | pending | pending |
| VAL011-A2 | pending | pending |
| VAL011-A3 | pending | pending |
| VAL011-A4 | pending | pending |
| VAL011-A5 | pending | pending |
| VAL011-A6 | pending | pending |

## Progress And Handoff

- Current stage: VAL011-implementation.
- Completed stages: provider/baseline/policy preflight, workflow bootstrap, and VAL012 bounded dependency observation at local commit `d8105e3dc038880d70803383a8928fc017a9f2f1`.
- Deferred stages and reasons: #270 production and pilot are outside authorization.
- Open decisions: none within the accepted #267/#268 scope.
- Continuation instructions: load and follow the canonical mutation-testing role, complete VAL011 against the closed VAL012 ledger, retain separate ledgers, and do not enable reuse.
- Target policy references: workflow gate, workflow artifact, handoff, Git commit, and branch policies named in the locator.
- Registered handoff checkpoint: none; this task remains in the same session/runtime.
- Branch history and checkpoint handoffs: branch created directly from verified `main@c7f348694421048245da824dd79742372179f730`; no push or merge authorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `main@c7f348694421048245da824dd79742372179f730` | local workflow bootstrap | `d66eec5915584a7e6df48ac6ab61a7261f1f134c` | local only | `2026-09-02T22:43:57+08:00` | cohesive #267/#268 delivery | continue VAL012 locally |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `d66eec5915584a7e6df48ac6ab61a7261f1f134c` | local validated stage | `d8105e3dc038880d70803383a8928fc017a9f2f1` | local only | `2026-09-02T23:21:04+08:00` | VAL012 acceptance passed independently | continue VAL011 locally |

## Completion Summary

- Outcome: in progress; VAL012 passed and VAL011 is active.
- Changed artifacts: workflow bootstrap plus the bounded observation contract, schema, CLI, fixtures, tests, and validation registration.
- Approved requirement/specification evidence: live Issues #267/#268, owner instruction, #270 owner decision and read-only design checkpoint.
- Implementation completion evidence: VAL012 is complete at `d8105e3dc038880d70803383a8928fc017a9f2f1`; VAL011 is pending.
- Required test outcomes: VAL012 focused and affected integration validation passed; VAL011 remains pending.
- Selected compliance evidence: not applicable.
- Review disposition: pending; no independent fixed-head audit claimed.
- Validation evidence: VAL012 9/9 focused, 10/10 registry, 3/3 source-entrypoint, shell-asset, commit-message, diff, and clean-status checks passed; failed and sandbox-blocked earlier attempts remain recorded in the task.
- Workflow task state: VAL012 completed; VAL011 in progress.
- Commits: `d66eec5915584a7e6df48ac6ab61a7261f1f134c`, `d8105e3dc038880d70803383a8928fc017a9f2f1`.
- Branch / checkpoint / handoff evidence: local branch only; no remote transport.
- Residual risks: runtime observation remains a lower bound; VAL011 critical mutants must all be detected before closeout.
