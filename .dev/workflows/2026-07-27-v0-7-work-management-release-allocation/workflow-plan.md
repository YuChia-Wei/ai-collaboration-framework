# v0.7.0 Work-Management Release Allocation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-27-v0-7-work-management-release-allocation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-27-v0-7-work-management-release-allocation`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-07-27-v0-7-work-management-release-allocation`
- `created_at`: `2026-07-27T21:39:33+08:00`
- `updated_at`: `2026-07-27T21:46:37+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `release_target`: `v0.7.0`

## Objective And Scope

- Problem statement: PR #10 integrated a completed source-repository work-management policy into `main`. The policy changed framework-managed package paths, but it was not assigned to a release scope and has not been classified as portable versus source-only truth.
- Authorized remediation scope: create durable v0.7.0 backlog identities, record PR #10 as scope-candidate evidence, add release gates that prevent unclassified policy bytes from publishing, and prepare a GitHub-issue-ready handoff without creating online tracker resources.
- Exclusions: do not create GitHub Issues or Projects; do not create a v0.7.0 package, tag, GitHub Release, or publication; do not alter the completed PR #10 policy; do not decide the portable policy implementation or perform payload cleanup in this allocation workflow.
- Completion criteria: `GOV-002` and `PKG-004` are indexed v0.7.0 release blockers with immutable source evidence, the roadmap records the new gate, no fabricated tracker identifier exists, and the workflow artifacts pass structural validation.

## Evidence And Allocation Decision

| Evidence | Allocation consequence |
| --- | --- |
| PR #10 merged as `a01e53c` | The completed source policy is recorded as evidence, not as a released package candidate. |
| `2026-07-25-work-management-policy` and `ASM-20260725-001` / `ASM-20260726-001` | The source-repository policy and its verification are complete and traceable. |
| `.ai/distribution/profiles/dotnet-backend.yaml` | Framework-managed standard globs can include policy bytes, while dated execution records are source-only. |
| Owner authorization on 2026-07-27 | Create durable backlog items and treat the policy as a v0.7.0 scope candidate; block publication until portable classification and package proof are complete. |

`candidate_for_release: v0.7.0` in this workflow means a selected scope contribution. It does not mean a formal release-candidate archive, tag, or hosted release exists.

## Artifact Contract

- Baseline assessment: not applicable; this workflow allocates existing policy evidence and does not remediate the policy itself.
- Remediation report: `.dev/workflows/2026-07-27-v0-7-work-management-release-allocation/reports/remediation-report.md`
- Verification assessment: not applicable; structural and reference validation cover this bounded allocation change.
- Tasks: `.dev/workflows/2026-07-27-v0-7-work-management-release-allocation/tasks/`

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `WMR-001` | Create `GOV-002` and preserve the approved v0.7.0 scope-candidate evidence without fabricating a GitHub Issue. | `completed` |
| `WMR-002` | Verify `PKG-004`, the v0.7.0 release gate, and the allocation artifacts before closure. | `completed` |

## Release Handoff

- GitHub issue mapping: deferred until the owner starts the online tracker design. Use backlog IDs as the external Issue titles or references; add only real Issue numbers later.
- Implementation handoff: `GOV-002` owns portable policy classification and `PKG-004` owns candidate payload proof. Each needs a separate authorized execution workflow before its implementation begins.
- Release handoff: no v0.7.0 package candidate may be built or published merely from this allocation. `GOV-002` and `PKG-004` must be resolved first.

## Resume Checkpoint

- Last completed action: recorded the allocation report, completed WMR-002, and closed the scope-allocation workflow after the local allocation checkpoint `36adb6c`.
- Current task: none; WMR-001 and WMR-002 are completed.
- Exact next action: open a separate authorized workflow for GOV-002 or PKG-004 only when the owner is ready to determine portable policy and package behavior; create GitHub Issues later using the real backlog IDs and tracker numbers.
- Validation already completed: YAML and JSON parsing; `validate-workflow-artifacts.py`; backlog release, governance workflow, and workflow lifecycle contract tests; `git diff --check`; workflow commit-range validation will cover both allocation commits before PR transport.
- Git state: branch `codex/2026-07-27-v0-7-work-management-release-allocation` from `main`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: the portable implementation and actual GitHub tracker design remain separate future work.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-27-v0-7-work-management-release-allocation` | `main@1a2b146cf2fe5389c8bd6a809cd8ab18de5973ff` | local allocation checkpoint | `36adb6cd5d9986ac106d3d1b449db3828d383be3` | local | `2026-07-27T21:46:37+08:00` | Preserve the owner-authorized GOV-002 and PKG-004 allocation before closure evidence. | Commit the closure report and request PR transport when desired. |
