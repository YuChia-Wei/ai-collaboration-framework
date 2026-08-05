# AI Context Maintenance Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-05-sub-agent-reachability`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `orchestrating_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-05-sub-agent-reachability-cont-04`
- `base_branch`: `main`
- `branch_segment`: `5`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-05-sub-agent-reachability`
- `created_at`: `2026-08-05T01:34:40+08:00`
- `updated_at`: `2026-08-05T10:31:24+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: The canonical active-role map and dynamic-loading policy do not prove that owning skills can reach their roles, do not distinguish inline application from genuine delegated invocation, and leave concrete test implementation ownership and no-delegation parity underspecified.
- Authorized remediation scope: Implement the seven owner decisions recorded on Issue #94 through the two smallest coherent slices: #118 for owning-skill bindings and validator-backed static reachability, then #119 for provider-neutral runtime execution evidence and inline fallback parity.
- Authorization: The owner completed decisions D94-Q1 through D94-Q7 and explicitly authorized workflow creation and implementation on 2026-08-05. The Issue #94 decision-ledger comment, not the assessment or provider state, is the implementation authority. After PR #122 and records PR #123 reached merged `main`, the owner separately authorized canonical v0.9.0 allocation and Project reconciliation on 2026-08-05; this follow-up does not authorize packaging or publication.
- Exclusions: Issue #92 rule/provider/effective-state ownership; Issue #93 target ignore/install/upgrade drift and `AICDISC-ADAPTER-001`; Copilot-specific projection work; external orchestration packages; product source/tests; provider configuration; bulk runtime-native adapter generation; v0.9.0 packaging, tagging, publication, and release configuration.
- Completion criteria: Every active canonical role has a valid owning-skill binding and explicit applicability/load obligation; the derived routing view and deterministic validator enforce static reachability without claiming execution; slice mode/test ownership matches D94-Q4/Q5; provider-neutral `role_execution` evidence covers direct, delegated, unavailable, not-applicable, retry, fallback, no-delegation parity, and final integration ownership; #92-owned sections remain untouched; tasks and remediation evidence are reconciled for review.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260804-002/assessment.yaml`
- Evidence traceability: `.dev/assessments/ASM-20260804-002/evidence/proposal-traceability.yaml`
- Owner decision ledger: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/94#issuecomment-5182504544`
- Implementation issues: `#118`, `#119`
- Remediation report: `.dev/workflows/2026-08-05-sub-agent-reachability/reports/remediation-report.md`
- Release-allocation addendum: `.dev/workflows/2026-08-05-sub-agent-reachability/reports/release-allocation-addendum.md`
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
7. Pull request, hosted evidence, merge-commit integration, and merged-main read-back — completed. PR #122's final head `e2757e2c2a382192866d1a52bfa8c74f6ce762a0` passed all five required checks, then merged to `main@0a9089f7d463f343dabc3da71a2ab5b20287f6cd` with parents `3e200fd...` and `e2757e2...`. Issues #94, #118, and #119 closed completed. Local repository validators, fixture tests, test suites, and `check-all` remain deferred by owner direction.
8. Owner-authorized v0.9.0 release-allocation addendum — completed under `SAR94-003`. Canonical `SAG-002`, ROADMAP, provider configuration, representative Issue #118, PR #122 reference keywords, Project fields, live `待發布` filter, provider receipt, hosted CI, PR #125 merge-commit integration, and final merged-main/Project read-back are reconciled. Packaging, tag, GitHub Release, and publication remain excluded.

## Proportionality And Delivery Decisions

- Two substantive tasks are sufficient because the implementation has exactly two coherent contracts with a one-way dependency. No validation-only or closeout-only task is invented to inflate workflow size.
- One workflow is appropriate because #118 and #119 share the same owner decisions, branch, reviewers, v0.9.0 target, rollback unit, and integration gate.
- `ai-context-governance` owns canonical-context remediation. `software-development-orchestrator` coordinates delegated execution, integration, and task evidence without taking over domain ownership.
- Integration gate: pull request to `main` under `.dev/TEAM-GIT-FLOW-RULES.MD`.
- Selected topology: merge-commit integration (`--no-ff`) because the owner explicitly requires the workflow boundary to remain visible.
- Validation boundary: do not run `check-all` or repository validation scripts. Implement fixtures and record manual/static review evidence; a separate owner-arranged task will review or run validation scripts.
- Follow-up proportionality: one addendum task is justified because repository canonical release truth and the external GitHub Project lifecycle must be ordered, synchronized, and resumed safely. No validation-only or closeout-only padding task is created.

## Parallel Work Coordination

- Concurrent #92 task `019fcd65-1745-78f3-8879-b5dc45ec4b30` owned rule/provider/effective-state sections and `loaded_rule_ids` resolver evidence; it is fully closed with no further source writes pending.
- This workflow owns `.ai/SUB-AGENT-SYSTEM.MD`, all `role_bindings` and `role_execution` sections, direct/delegated/unavailable/not-applicable semantics, test-design-to-slice-implementation mapping, no-delegation parity, and their fixtures.
- #92 kept `.ai/SUB-AGENT-SYSTEM.MD`, the reachability validator/fixtures, and all #94-owned role sections untouched. Its integrated RPB-006 changes add only sibling `effective_rule_consumption` sections and independent schema/test coverage; combined-state source review found no textual or semantic conflict with rebased #94 commits `46e7bd4` and `14a256e`.
- #92 commit `98484bd` and discarded local #94 commit `9240f3d` have the same stable patch ID `ac99550ac151a4ab4fe92ced69f8c4c15d7a8a56` for the moved-example validator paths. The continuation is based on #92 closeout `main@3e200fd5e164ba363c3cde0c50219e18f0ca14de`; `9240f3d` is not an ancestor, while the three destination files and path fix remain through #92.
- #94 remained the single writer for the universal role-taxonomy wording in `.dev/standards/rationale/skill-sub-agent-boundary-rationale.MD`, `.dev/standards/AI-CONTEXT-BOUNDARY.md`, and the three named human guides. Combined read-back retained both #92 engineering-identity/target-effective semantics and #94 sub-agent classification/placement semantics.
- #92 implementation PR #120 merged at `3bb03993675bb404dc467b8da6ad702c01919705`; records-only PR #121 merged at `3e200fd5e164ba363c3cde0c50219e18f0ca14de`. The #121 delta changes only five #92 workflow/index records and no canonical `.ai`, `.dev/standards`, or `.dev/guides` surface.
- This workflow will not edit #92-owned rule/provider/effective-state sections, target provider configuration, or `loaded_rule_ids` semantics.

## Implementation Closeout Record

- Final completed action: PR [#122](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/122) merged at `2026-08-05T01:08:50Z` by the owner-selected merge-commit topology. Its head was `e2757e2c2a382192866d1a52bfa8c74f6ce762a0`; merged `main` is `0a9089f7d463f343dabc3da71a2ab5b20287f6cd`, with parents `3e200fd...` (base) and `e2757e2...` (head).
- Task result: `SAR94-001` and `SAR94-002` are completed. Merged-main ancestry and the full #92/#94 combined artifact read-back passed. Issues #94, #118, and #119 are closed completed.
- Hosted validation: all five required checks were green on final head `e2757e2`: AI Context Governance `30965252258`; Package AI Context Candidate `30965252246`; and Portable AI Context Gates `30965252383` (Ubuntu prerequisite, Windows prerequisite, Ubuntu quick gate). The final Ubuntu quick gate passed on its first attempt; no transient rerun was needed.
- Failure diagnosis retained: earlier PR runs exposed deterministic wrapper/validator synchronization and duplicate-binding fail-closed defects, corrected in `a1741fb` and `4fd7ed9`. They were not classified as an Ubuntu quick-gate flake.
- Local validation boundary: no local repository validator, fixture test, test suite, or `check-all` ran, per owner direction. Green hosted gates are separate evidence and do not reclassify local commands as run.
- Cross-workflow boundary: #92 remains fully closed. Merged `main` retains both #92 effective-rule/provider semantics and #94 role reachability/execution semantics; duplicate patch `9240f3d` remains omitted while #92 path fix `98484bd` is integrated.
- Exclusions retained: v0.9.0 packaging, tagging, release configuration, and publication remain outside this workflow.
- Implementation-closeout next action at that checkpoint: none for the completed implementation scope. The later owner-authorized allocation decision is governed by the explicit addendum below; local validation-script review remains separately owner-arranged.

## Release Allocation Addendum

- Authorization: on 2026-08-05, after merged-main read-back, the owner explicitly confirmed that the seven-decision #94 delivery is intended for v0.9.0 and authorized canonical backlog, ROADMAP, provider-mapping, and Project reconciliation.
- Canonical aggregation: create one `SAG-002` release blocker represented by #118 and supported by dependent #119. Proposal #94 remains intake and owner-decision provenance and is not a second Included Work entry.
- Project projection: keep #94 and #119 as non-canonical provenance/supporting cards without release allocation fields; set representative #118 to Done / P1 High / Owner review Approved / v0.9.0 / Not yet published so it is eligible for `待發布` exactly once.
- Provider reconciliation: replace merged PR #122 closing keywords with `Refs`, preserve the already verified completed Issue state, and add exact canonical markers/read-back evidence to representative #118 without creating formal sub-issue relationships that the provider policy forbids inferring.
- Current task: `SAR94-003` is completed on records-only continuation `codex/2026-08-05-sub-agent-reachability-cont-04` from merged allocation `main@6eeed2b90054451d962a842decaefdee7fa96693`. Canonical checkpoint `b9a6f0c` preserves all six existing v0.9.0 items and adds only `SAG-002` as the seventh.
- Provider read-back: PR #122 now uses `Refs #94`, `Refs #118`, and `Refs #119`; Issue #118 carries the exact `SAG-002` markers, remains closed completed, and is the only card with P1 High / Approved / v0.9.0 / Not yet published. The live `待發布` filter is `status:Done reason:completed -target-release:Unassigned published-in:"Not yet published"`; #94 and #119 retain unset release fields.
- Hosted integration: PR #125 corrected one deterministic workflow-index timestamp mismatch in `de16ca4`, then all five hosted gates passed. It merged as `6eeed2b90054451d962a842decaefdee7fa96693` with parents `f4018e6` and `de16ca4`.
- Exact next action: integrate this records-only closeout by merge commit after hosted CI. No implementation, release preparation, tag, GitHub Release, or publication action remains authorized.
- Validation boundary: do not run local validation scripts, tests, builds, formatters, `check-all`, aggregate gates, or other validation programs. Manual file inspection and hosted Issue/Project/PR read-back are allowed; hosted CI is the only executable gate.
- Publication boundary: no package build, release configuration, tag, GitHub Release, asset upload, or publication is authorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-sub-agent-reachability` | `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` | push-only implementation checkpoint | `f9f6a04` | `origin/codex/2026-08-05-sub-agent-reachability` | `2026-08-05T02:25:33+08:00` | #118/#119 implementation is reviewable while validation remains separately deferred | resume the same branch for validation reconciliation; then open the required PR without release packaging |
| 2 | `codex/2026-08-05-sub-agent-reachability-continuation` | `main@3e200fd5e164ba363c3cde0c50219e18f0ca14de` | merge-commit integration | `e2757e2c2a382192866d1a52bfa8c74f6ce762a0` | `main@0a9089f7d463f343dabc3da71a2ab5b20287f6cd` via PR #122 | `2026-08-05T09:08:50+08:00` | final hosted run passed all five required checks after two bounded deterministic corrections | merged-main ancestry/read-back passed; create records-only closeout continuation from merged main |
| 3 | `codex/2026-08-05-sub-agent-reachability-cont-02` | `main@0a9089f7d463f343dabc3da71a2ab5b20287f6cd` | closeout records | `9af809b30e2a783187d06e80041095677a3083f8` | `main@2aa61dd7a33916782170b8e3cc6de2e098c555d8` via PR #123 | `2026-08-05T09:21:14+08:00` | preserve the completed implementation segment while recording final workflow evidence | records-only merge topology and completed task read-back passed; await separately authorized follow-up |
| 4 | `codex/2026-08-05-sub-agent-reachability-cont-03` | `main@f4018e6bac7ce7df7367359278eeb07e204974a3` | merge-commit release allocation | `de16ca4854d28d58a536e28f4b41c7a3fef36cc5` | `main@6eeed2b90054451d962a842decaefdee7fa96693` via PR #125 | `2026-08-05T10:27:39+08:00` | replay preserved the complete #92 six-item allocation, added only `SAG-002` as the seventh, and corrected one hosted workflow-index timestamp mismatch | merged-main and hosted Project read-back passed; create records-only closeout continuation |
| 5 | `codex/2026-08-05-sub-agent-reachability-cont-04` | `main@6eeed2b90054451d962a842decaefdee7fa96693` | active records-only closeout | pending | local branch | `2026-08-05T10:31:24+08:00` | record final PR #125, hosted CI, merged-main, Project, and residual provider-title evidence without reopening implementation | commit and integrate the records-only closeout by merge commit; publication remains separately unauthorized |
