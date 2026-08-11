# Selected-Payload Navigation And Component Closure

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-11-std-001-pkg-navigation-closure`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-std-001-pkg-navigation-closure`
- `base_branch`: `codex/2026-08-11-std-001-combined-validation`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-pkg-navigation-closure`
- `created_at`: `2026-08-11T21:47:55+08:00`
- `updated_at`: `2026-08-11T22:45:54+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #193 owns `ASM-20260811-003#PKG-001` and `#CMP-001`: archive parity can pass while the selected payload still contains broken local navigation, actionable references to excluded source-only authority, and component metadata whose mandatory reference graph closes only accidentally under the default profile.
- Authorized remediation scope: validate links and actionable local targets against the post-mapping selected payload; distinguish navigation from examples, templates, placeholders, and external URLs; repair or reclassify portable guidance that points to source-only content; add explicit component dependency and selection-closure metadata; make Code Reviewer core-only and dotnet-selected dispositions deterministic; verify ZIP/tar parity and the combined #191/#192 payload view. The owner additionally directed the active upgrade-test horizon to begin at v0.6.0, use only the immediate predecessor for routine later releases, and create a predecessor-only checkpoint at each breaking release.
- Exclusions: do not redefine Code Reviewer progressive disclosure or governance terminology; do not create a v0.13 release record, tag, Release, or publication; do not treat the validation-only combined branch as an authorized integration; Project allocation, push, PR, merge, Issue closure, and release actions remain separate decisions.
- Completion criteria for local implementation: genuine missing payload navigation and actionable local targets fail closed; code/example/template/placeholder cases are classified; portable instructions do not require excluded source-release records/runbooks/instances; component dependencies close for each supported selection; Code Reviewer has explicit core-only and dotnet-selected dispositions; ZIP/tar inventory and user-view validation agree; an independent assessment has no unhandled blocking source finding.
- External completion condition: a real governed v0.13 candidate and owner read-back remain required by Issue #193, cannot be substituted by this controlled combined projection, and must stay `deferred-with-owner` until release authority exists.

## Authorization And Combined Baseline

- Online Issue: [#193](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193), read back as OPEN on 2026-08-11.
- Owner authorization: [issue comment 5253059500](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193#issuecomment-5253059500) authorizes local implementation and result review while reserving Project allocation, transport, integration, Issue closure, tag, Release, and publication.
- Validation-only base: `b1aacf8c4f08da72392cafc88a0c6eca1fad19ee`, assembled locally from #191 final `f62f110`, #192 final `92e7383`, and #61 coordination `818d5da` with both assessment/workflow index rows retained.
- The combined base and this branch are local-only technical evidence. They are not a merge authorization, hosted integration record, or release candidate.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-003/assessment.yaml`
- Input verifications: `.dev/assessments/ASM-20260811-004/assessment.yaml`, `.dev/assessments/ASM-20260811-005/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-11-std-001-pkg-navigation-closure/reports/remediation-report.md`
- Planned verification assessment: `.dev/assessments/ASM-20260811-006/assessment.yaml`
- Tasks: `.dev/workflows/2026-08-11-std-001-pkg-navigation-closure/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#PKG-001` | HIGH | `ai-context-governance` / distribution validators | remediate | `STD193-001` | selected-payload link/action fixtures, archive user-view parity, portable source-only boundary |
| `ASM-20260811-003#CMP-001` | MEDIUM | distribution profile and component metadata | remediate | `STD193-001` | dependency graph closure, core-only/dotnet-selected Code Reviewer dispositions |

## Stages And Checkpoints

1. Read back Issue #193 and freeze the validation-only combined subject. `completed`
2. Inventory broken payload navigation, actionable local targets, component assignments, and selection closure. `completed`
3. Implement bounded distribution/validator remediation, the owner-directed upgrade-test horizon, and deterministic negative fixtures. `completed`
4. Build controlled ZIP/tar artifacts and validate identical inventory/user-view behavior. `completed`
5. Run independent post-remediation assessment and reconcile local findings. `completed`
6. Keep real governed v0.13 candidate review deferred to the owner-controlled release lifecycle. `deferred-with-owner`

## Resume Checkpoint

- Last completed action: Implemented selected-payload user-view and component closure at `ff80d590`, then recorded independent fixed-subject verification `ASM-20260811-006` at `cef711a`; both baseline findings are addressed with no new blocker.
- Current task: `STD193-001` is complete for the authorized local source scope.
- Exact next action: return the local result for owner review. Any push, PR, merge, Issue closure, Project allocation, or governed v0.13 candidate must be separately authorized.
- Validation already completed: selected-payload contract 6/6; version governance 23/23; packaging 36/36 with no skip; focused archive/metadata/apply 3/3; package apply 30/30 outside sandbox with one uncounted Windows symlink privilege skip; Code Reviewer routing 8/8; exact Git Bash fast profile 34/34 required with one not-applicable and a 99-second advisory-budget warning; workflow, assessment, context, version, shell, and whitespace validators passed.
- Git state: local branch `codex/2026-08-11-std-001-pkg-navigation-closure` contains implementation `ff80d590` and assessment `cef711a`; nothing is pushed or merged.
- Branch history and checkpoint handoffs: #191 remains at `f62f110`, #192 at `92e7383`, and the #193 combined lineage remains local. The controlled projection is not hosted integration or a release candidate.
- Blockers or unresolved decisions: none for local source completion. A real governed v0.13 candidate, downstream owner acceptance, provider read-back, transport, integration, and publication remain `deferred-with-owner`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `codex/2026-08-11-std-001-combined-validation@b1aacf8` | workflow bootstrap | `d918b9f` | local | `2026-08-11T21:47:55+08:00` | Execute #193 against the exact combined #191/#192 payload view without remote integration | Reproduce selected-payload and component-closure failures |
| 1 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `codex/2026-08-11-std-001-combined-validation@b1aacf8` | local verified implementation | `ff80d590`, `cef711a`, plus containing closeout commit | local | `2026-08-11T22:45:54+08:00` | Preserve bounded remediation, owner-directed upgrade-test horizon, and independent `ASM-20260811-006` evidence | Owner reviews the local result; all remote, integration, Issue, Project, and release actions remain separate |
