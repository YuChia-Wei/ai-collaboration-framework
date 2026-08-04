# AI Context Maintenance Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `orchestrating_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-05-sub-agent-reachability`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-05-sub-agent-reachability`
- `created_at`: `2026-08-05T01:34:40+08:00`
- `updated_at`: `2026-08-05T01:52:18+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: The canonical active-role map and dynamic-loading policy do not prove that owning skills can reach their roles, do not distinguish inline application from genuine delegated invocation, and leave concrete test implementation ownership and no-delegation parity underspecified.
- Authorized remediation scope: Implement the seven owner decisions recorded on Issue #94 through the two smallest coherent slices: #118 for owning-skill bindings and validator-backed static reachability, then #119 for provider-neutral runtime execution evidence and inline fallback parity.
- Authorization: The owner completed decisions D94-Q1 through D94-Q7 and explicitly authorized workflow creation and implementation on 2026-08-05. The Issue #94 decision-ledger comment, not the assessment, Issue state, or v0.9.0 allocation alone, is the implementation authority.
- Exclusions: Issue #92 rule/provider/effective-state ownership; Issue #93 target ignore/install/upgrade drift and `AICDISC-ADAPTER-001`; Copilot-specific projection work; external orchestration packages; product source/tests; provider configuration; bulk runtime-native adapter generation; v0.9.0 packaging, tagging, publication, and release configuration.
- Completion criteria: Every active canonical role has a valid owning-skill binding and explicit applicability/load obligation; the derived routing view and deterministic validator enforce static reachability without claiming execution; slice mode/test ownership matches D94-Q4/Q5; provider-neutral `role_execution` evidence covers direct, delegated, unavailable, not-applicable, retry, fallback, no-delegation parity, and final integration ownership; #92-owned sections remain untouched; tasks and remediation evidence are reconciled for review.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260804-002/assessment.yaml`
- Evidence traceability: `.dev/assessments/ASM-20260804-002/evidence/proposal-traceability.yaml`
- Owner decision ledger: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/94#issuecomment-5182504544`
- Implementation issues: `#118`, `#119`
- Remediation report: `.dev/workflows/2026-08-05-sub-agent-reachability/reports/remediation-report.md`
- Verification assessment: not allocated; the owner will arrange validation-script review separately.
- Tasks: `.dev/workflows/2026-08-05-sub-agent-reachability/tasks/`

## Owner Decision Baseline

| Decision | Choice | Durable outcome |
| --- | --- | --- |
| `D94-Q1` | A | Owning `skill.yaml.role_bindings` is canonical; each role manifest owns only the role contract; central routing is derived. |
| `D94-Q2` | C | Mandatory bindings and validator-backed projection prove only `statically-reachable`. |
| `D94-Q3` | A | Direct by default; delegate only after all safety gates and at least one material-value trigger. |
| `D94-Q4` | C | One command/query/reactor/generic primary slice mode; other implementation roles are conditional bindings. |
| `D94-Q5` | B | `slice-implementer` owns concrete test implementation; BDD design and test execution remain separate. |
| `D94-Q6` | A | Owning skills produce a provider-neutral `role_execution`; the orchestrator aggregates it with bounded retry/fallback evidence. |
| `D94-Q7` | A | No-delegation runtimes apply the same stage contract inline and record `direct`, never a synthetic child invocation. |

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Evidence boundary |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260804-002#AIC-003` | MEDIUM | `ai-context-governance` | owner-authorized remediation | `SAR94-001`, `SAR94-002` | Assessment establishes the gap; Issue #94 decisions establish the adopted contract and implementation authority. |
| `ASM-20260804-002#AIC-004` | HIGH | `ai-context-governance` | preserve retained evidence and traceability | `SAR94-001`, `SAR94-002` | Do not alter or import downstream workflow identity; retain exact assessment evidence and stable links. |

## Stages And Checkpoints

1. Evidence freeze and owner discussion — completed; all seven decisions and the implementation authority are preserved on Issue #94.
2. Bounded issue decomposition and duplicate search — completed; #118 and #119 are the smallest coherent slices and #119 depends on #118.
3. Workflow bootstrap — completed on the dedicated branch from `origin/main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` in commit `9880255`.
4. Static owning-skill reachability remediation — `SAR94-001` / #118 completed with repository validation scripts deferred by explicit owner direction.
5. Runtime selection, execution evidence, and inline parity remediation — `SAR94-002` / #119 in progress.
6. Orchestrator integration review and durable handoff — pending; repository validation scripts are intentionally outside this workflow.

## Proportionality And Delivery Decisions

- Two substantive tasks are sufficient because the implementation has exactly two coherent contracts with a one-way dependency. No validation-only or closeout-only task is invented to inflate workflow size.
- One workflow is appropriate because #118 and #119 share the same owner decisions, branch, reviewers, v0.9.0 target, rollback unit, and integration gate.
- `ai-context-governance` owns canonical-context remediation. `software-development-orchestrator` coordinates delegated execution, integration, and task evidence without taking over domain ownership.
- Integration gate: pull request to `main` under `.dev/TEAM-GIT-FLOW-RULES.MD`.
- Selected topology: merge-commit integration (`--no-ff`) because the owner explicitly requires the workflow boundary to remain visible.
- Validation boundary: do not run `check-all` or repository validation scripts. Implement fixtures and record manual/static review evidence; a separate owner-arranged task will review or run validation scripts.

## Parallel Work Coordination

- Concurrent #92 task `019fcd65-1745-78f3-8879-b5dc45ec4b30` owns rule/provider/effective-state sections and `loaded_rule_ids` resolver evidence.
- This workflow owns `.ai/SUB-AGENT-SYSTEM.MD`, all `role_bindings` and `role_execution` sections, direct/delegated/unavailable/not-applicable semantics, test-design-to-slice-implementation mapping, no-delegation parity, and their fixtures.
- Potential shared surfaces are `.ai/assets/CANONICAL-SCHEMA.MD` and applicable action-skill `skill.yaml` files. If #92 needs an essential edit there, both workflows will name the exact section and use one sequential writer.
- This workflow will not edit #92-owned rule/provider/effective-state sections, target provider configuration, or `loaded_rule_ids` semantics.

## Resume Checkpoint

- Last completed action: Integrated #118 canonical bindings, the 18-row derived projection, fail-closed static-reachability validation, and GWT fixtures after root review corrected multi-owner and projection-parity behavior.
- Current task: `SAR94-002` is `in_progress`; `SAR94-001` is completed awaiting the separately arranged validation-script review.
- Exact next action: Commit the #118 task boundary, then delegate disjoint #119 runtime-contract, owning-skill handoff, and acceptance-fixture units to `gpt-5.6-terra` sub-agents under root integration ownership.
- Validation already completed: Git branch/base checks; GitHub duplicate search and issue/comment read-back; worker PyYAML parse and exact 18-role path/asset/status matrix; worker Python AST syntax parse of the validator and test file; root/worker `git diff --check`. No repository validation script or test suite has been run.
- Git state: branch `codex/2026-08-05-sub-agent-reachability`, based on `origin/main@d8580df4516155ff7b1a139d9a064a8b0d4b2019`; workflow bootstrap commit `9880255` is local and the #118 task changes are ready for their bounded commit.
- Branch history and checkpoint handoffs: segment 1 began from updated `origin/main`; no push or merge checkpoint yet.
- Blockers or unresolved decisions: none. Shared-file coordination with #92 is established and will fail closed to sequential integration if an overlap materializes.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-sub-agent-reachability` | `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` | active | pending | local | `2026-08-05T01:34:40+08:00` | owner-authorized #94 implementation | continue `SAR94-001` after workflow bootstrap |
