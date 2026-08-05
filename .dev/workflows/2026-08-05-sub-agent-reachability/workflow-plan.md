# AI Context Maintenance Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `orchestrating_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-05-sub-agent-reachability-continuation`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `in_progress`
- `current_phase`: `integration`
- `artifact_root`: `.dev/workflows/2026-08-05-sub-agent-reachability`
- `created_at`: `2026-08-05T01:34:40+08:00`
- `updated_at`: `2026-08-05T09:00:09+08:00`
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
- Verification assessment: [`ASM-20260805-001`](../../assessments/ASM-20260805-001/assessment.yaml) is final at updated subject commit `4fd7ed991729836801e960c557fb019a25930146`; it records the #92-integrated combined-source read-back, bounded PR #122 hosted synchronization correction, and duplicate-binding fail-closed correction. Validation-script execution remains separately owner-arranged.
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
5. Runtime selection, execution evidence, and inline parity remediation — completed; three independent source-only reviews found the static reachability and #92 compatibility surfaces sound, then identified two MEDIUM execution-contract gaps which were corrected and independently re-reviewed as resolved.
6. #92-first sequential transport and combined verification — completed; #92 implementation PR #120 and records-only closeout PR #121 reached `main`, #94 was replayed from `main@3e200fd5e164ba363c3cde0c50219e18f0ca14de`, and duplicate patch `9240f3d` was omitted. Three final source-only passes and an ordering-clarity follow-up found no active defect.
7. Pull request, hosted evidence, merge-commit integration, and merged-main read-back — in progress. PR #122's first run produced three failures from one wrapper/validator sync gap, corrected in `a1741fb`. The second run passed package candidate, both prerequisite contracts, and Ubuntu quick gate; read-only governance alone exposed GWT-025 crediting the first of duplicate bindings, corrected fail-closed in `4fd7ed9`. A fresh all-green run is required. Local repository validators, fixture tests, test suites, and `check-all` remain deferred by owner direction.

## Proportionality And Delivery Decisions

- Two substantive tasks are sufficient because the implementation has exactly two coherent contracts with a one-way dependency. No validation-only or closeout-only task is invented to inflate workflow size.
- One workflow is appropriate because #118 and #119 share the same owner decisions, branch, reviewers, v0.9.0 target, rollback unit, and integration gate.
- `ai-context-governance` owns canonical-context remediation. `software-development-orchestrator` coordinates delegated execution, integration, and task evidence without taking over domain ownership.
- Integration gate: pull request to `main` under `.dev/TEAM-GIT-FLOW-RULES.MD`.
- Selected topology: merge-commit integration (`--no-ff`) because the owner explicitly requires the workflow boundary to remain visible.
- Validation boundary: do not run `check-all` or repository validation scripts. Implement fixtures and record manual/static review evidence; a separate owner-arranged task will review or run validation scripts.

## Parallel Work Coordination

- Concurrent #92 task `019fcd65-1745-78f3-8879-b5dc45ec4b30` owned rule/provider/effective-state sections and `loaded_rule_ids` resolver evidence; it is fully closed with no further source writes pending.
- This workflow owns `.ai/SUB-AGENT-SYSTEM.MD`, all `role_bindings` and `role_execution` sections, direct/delegated/unavailable/not-applicable semantics, test-design-to-slice-implementation mapping, no-delegation parity, and their fixtures.
- #92 kept `.ai/SUB-AGENT-SYSTEM.MD`, the reachability validator/fixtures, and all #94-owned role sections untouched. Its integrated RPB-006 changes add only sibling `effective_rule_consumption` sections and independent schema/test coverage; combined-state source review found no textual or semantic conflict with rebased #94 commits `46e7bd4` and `14a256e`.
- #92 commit `98484bd` and discarded local #94 commit `9240f3d` have the same stable patch ID `ac99550ac151a4ab4fe92ced69f8c4c15d7a8a56` for the moved-example validator paths. The continuation is based on #92 closeout `main@3e200fd5e164ba363c3cde0c50219e18f0ca14de`; `9240f3d` is not an ancestor, while the three destination files and path fix remain through #92.
- #94 remained the single writer for the universal role-taxonomy wording in `.dev/standards/rationale/skill-sub-agent-boundary-rationale.MD`, `.dev/standards/AI-CONTEXT-BOUNDARY.md`, and the three named human guides. Combined read-back retained both #92 engineering-identity/target-effective semantics and #94 sub-agent classification/placement semantics.
- #92 implementation PR #120 merged at `3bb03993675bb404dc467b8da6ad702c01919705`; records-only PR #121 merged at `3e200fd5e164ba363c3cde0c50219e18f0ca14de`. The #121 delta changes only five #92 workflow/index records and no canonical `.ai`, `.dev/standards`, or `.dev/guides` surface.
- This workflow will not edit #92-owned rule/provider/effective-state sections, target provider configuration, or `loaded_rule_ids` semantics.

## Resume Checkpoint

- Last completed action: Diagnosed the second PR #122 hosted run: four checks passed, and read-only governance alone exposed that duplicate role bindings still credited the first declaration as valid reachability. Commit `4fd7ed9` now removes only duplicated role IDs from the valid-owner result while retaining independent valid bindings.
- Current task: `SAR94-002` remains `in_progress` solely for pull-request, hosted-check, merge-commit, and merged-main lifecycle evidence. `SAR94-001` is completed with final combined-source reachability review.
- Exact next action: Commit this assessment/workflow reconciliation, push `4fd7ed9` and the records checkpoint to ready PR #122, require fresh all-green hosted results, then integrate with merge-commit topology and read back merged `main`.
- Validation already completed: Git branch/base and GitHub issue/comment read-back; earlier syntax parsing; root manual reviews; `git diff --check`; three independent final source-only reachability, execution, and cross-workflow compatibility reviews; the LOW ordering-clarity follow-up; confirmation that #121 is records-only outside #94 canonical surfaces; two rounds of PR #122 check/log inspection; manual exact wrapper-reference/v1.3 contract comparison for `a1741fb`; and duplicate-binding return-path review for `4fd7ed9`. The second hosted run passed four checks including Ubuntu quick gate; only read-only GWT-025 failed and is corrected. No local repository validation script, fixture test, test suite, or `check-all` run has been performed.
- Git state: branch `codex/2026-08-05-sub-agent-reachability-continuation` is based on `origin/main@3e200fd5e164ba363c3cde0c50219e18f0ca14de`; PR #122 currently points to `a6249e0`, and local fix `4fd7ed9` plus this records checkpoint await push. Duplicate patch `9240f3d` is not an ancestor; its path fix and destinations are present via #92 commit `98484bd`.
- Branch history and checkpoint handoffs: segment 1 published the pre-integration implementation checkpoint. Segment 2 opened ready PR #122 from final #92 closeout `main`, then retained the same branch for the owner-authorized hosted-gate correction; no merge exists yet.
- Blockers or unresolved decisions: none. Repository validation scripts remain separately owner-arranged and are not treated as passed; hosted checks and merged-main evidence remain pending lifecycle facts.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-sub-agent-reachability` | `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` | push-only implementation checkpoint | `f9f6a04` | `origin/codex/2026-08-05-sub-agent-reachability` | `2026-08-05T02:25:33+08:00` | #118/#119 implementation is reviewable while validation remains separately deferred | resume the same branch for validation reconciliation; then open the required PR without release packaging |
| 2 | `codex/2026-08-05-sub-agent-reachability-continuation` | `main@3e200fd5e164ba363c3cde0c50219e18f0ca14de` | ready PR plus hosted-fix checkpoint | `4fd7ed9` | PR #122 / local fix pending push | `2026-08-05T09:00:09+08:00` | #92-first transport and combined verification completed; two hosted runs exposed bounded deterministic gaps now corrected | push the fix and records checkpoint, require fresh all-green hosted evidence, then merge-commit only after required checks pass |
