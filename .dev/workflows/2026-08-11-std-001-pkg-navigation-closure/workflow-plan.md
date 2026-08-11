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
- `status`: `in_progress`
- `current_phase`: `bounded-remediation`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-pkg-navigation-closure`
- `created_at`: `2026-08-11T21:47:55+08:00`
- `updated_at`: `2026-08-11T21:47:55+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #193 owns `ASM-20260811-003#PKG-001` and `#CMP-001`: archive parity can pass while the selected payload still contains broken local navigation, actionable references to excluded source-only authority, and component metadata whose mandatory reference graph closes only accidentally under the default profile.
- Authorized remediation scope: validate links and actionable local targets against the post-mapping selected payload; distinguish navigation from examples, templates, placeholders, and external URLs; repair or reclassify portable guidance that points to source-only content; add explicit component dependency and selection-closure metadata; make Code Reviewer core-only and dotnet-selected dispositions deterministic; verify ZIP/tar parity and the combined #191/#192 payload view.
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
2. Inventory broken payload navigation, actionable local targets, component assignments, and selection closure. `in_progress`
3. Implement bounded distribution/validator remediation and deterministic negative fixtures. `pending`
4. Build controlled ZIP/tar artifacts and validate identical inventory/user-view behavior. `pending`
5. Run independent post-remediation assessment and reconcile local findings. `pending`
6. Keep real governed v0.13 candidate review deferred to the owner-controlled release lifecycle. `pending`

## Resume Checkpoint

- Last completed action: Read back OPEN Issue #193 and owner authorization comment `5253059500`, then fixed validation-only combined base `b1aacf8` from the independently verified #191/#192 checkpoints.
- Current task: `STD193-001`.
- Exact next action: reproduce the seven baseline payload navigation failures against the combined subject, inventory all component-reference edges after mapping, and identify the smallest validator/profile/guidance correction set.
- Validation already completed: combined #191 Code Reviewer routing 8/8; combined #192 governance routing 8/8; workflow and assessment indexes validate with both final assessments present.
- Git state: local branch `codex/2026-08-11-std-001-pkg-navigation-closure` at validation-only base `b1aacf8`; nothing is pushed or merged.
- Branch history and checkpoint handoffs: #191 remains at `f62f110`, #192 at `92e7383`, parent #61 at `818d5da`; the combined base is local and must not be reported as integration.
- Blockers or unresolved decisions: none for local source implementation. A real governed v0.13 candidate/owner read-back is externally deferred and cannot be fabricated.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `codex/2026-08-11-std-001-combined-validation@b1aacf8` | workflow bootstrap | pending | local | `2026-08-11T21:47:55+08:00` | Execute #193 against the exact combined #191/#192 payload view without remote integration | Reproduce selected-payload and component-closure failures |
