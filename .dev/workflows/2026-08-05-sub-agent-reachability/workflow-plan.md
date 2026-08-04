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
- `current_phase`: `sequential-integration-wait`
- `artifact_root`: `.dev/workflows/2026-08-05-sub-agent-reachability`
- `created_at`: `2026-08-05T01:34:40+08:00`
- `updated_at`: `2026-08-05T07:36:38+08:00`
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
- Verification assessment: [`ASM-20260805-001`](../../assessments/ASM-20260805-001/assessment.yaml) is a source-only draft at subject commit `5dc854749f39397058d95bace415cccab8c6300e`; it remains non-final until #92-first integration and combined-state read-back are assessed. Validation-script execution remains separately owner-arranged.
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
5. Runtime selection, execution evidence, and inline parity remediation — implementation completed; three independent source-only reviews found the static reachability and #92 compatibility surfaces sound, then identified two MEDIUM execution-contract gaps which were corrected and independently re-reviewed as resolved.
6. Sequential integration handoff — in progress; #92 must integrate its complete workflow first. This workflow will then continue from updated `main`, retain the #94 role commits and review corrections, and omit the duplicate moved-example path patch already carried by #92.

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
- #92 kept `.ai/SUB-AGENT-SYSTEM.MD`, the reachability validator/fixtures, and all #94-owned role sections untouched. Its RPB-006 commit `08f24eb` added only sibling `effective_rule_consumption` sections and independent schema/test coverage; an independent three-way source review found no textual or semantic conflict with #94 commits `a80d6a6` and `f9f6a04`.
- #92 commit `98484bd` and local #94 commit `9240f3d` have the same stable patch ID `ac99550ac151a4ab4fe92ced69f8c4c15d7a8a56` for the moved-example validator paths. Because the destination files arrive through #92, the owner workflows selected #92-first transport: do not publish the duplicate #94 patch, then omit it when replaying #94 from updated `main`.
- #94 is the single writer for the universal role-taxonomy wording in `.dev/standards/rationale/skill-sub-agent-boundary-rationale.MD`, `.dev/standards/AI-CONTEXT-BOUNDARY.md`, and the three named human guides. #92 commit `69603f1` changes different `AI-CONTEXT-BOUNDARY.md` sections; final integration must read back both semantic sets after the branches meet.
- This workflow will not edit #92-owned rule/provider/effective-state sections, target provider configuration, or `loaded_rule_ids` semantics.

## Resume Checkpoint

- Last completed action: Corrected both MEDIUM source-review findings: dynamic roles now apply inline by default unless delegation gates and evidence pass, and attempt 3+ authorization freshness is defined, enforced, and covered by a reused-authorization negative fixture. The same independent reviewer then returned `pass-for-manual-review` with no new finding.
- Current task: `SAR94-002` remains `in_progress` for sequential integration and final verification. `SAR94-001` is completed and its independent source-only reachability audit returned `pass-for-manual-review` with no finding.
- Exact next action: Wait for #92 to complete RPB-007, its independent assessment, and `main` integration. Then create a continuation branch from updated `main`, replay #94 commits and this review correction while skipping duplicate patch `9240f3d`, and perform the final combined read-back before opening the required PR.
- Validation already completed: Git branch/base and GitHub issue/comment read-back; earlier syntax parsing; root manual reviews; `git diff --check`; independent source-only reachability, execution, and cross-workflow compatibility reviews; and a source-only follow-up that resolved both execution findings. No repository validation script, fixture test, test suite, or `check-all` run has been performed.
- Git state: branch `codex/2026-08-05-sub-agent-reachability`; remote checkpoint through `99a9de2`; local duplicate patch `9240f3d` must not be published and will be omitted after #92 reaches `main`. The current source-review correction is prepared for a local durable checkpoint.
- Branch history and checkpoint handoffs: segment 1 began from updated `origin/main`; push-only checkpoint `f9f6a04` was published to `origin/codex/2026-08-05-sub-agent-reachability` at `2026-08-05T02:25:33+08:00`. Resume from that branch for validation; no merge checkpoint or pull request exists.
- Blockers or unresolved decisions: no owner decision is pending. Sequential transport waits only for #92 to reach `main`; repository validation scripts remain separately owner-arranged. Final shared-file read-back must include #92 commit `69603f1`, RPB-006 `08f24eb`, the moved-example destination files, and their integrated successors.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-sub-agent-reachability` | `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` | push-only implementation checkpoint | `f9f6a04` | `origin/codex/2026-08-05-sub-agent-reachability` | `2026-08-05T02:25:33+08:00` | #118/#119 implementation is reviewable while validation remains separately deferred | resume the same branch for validation reconciliation; then open the required PR without release packaging |
