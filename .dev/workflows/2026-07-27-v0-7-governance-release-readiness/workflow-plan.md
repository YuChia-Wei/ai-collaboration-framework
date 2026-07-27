# v0.7.0 Governance And Release Readiness

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-27-v0-7-governance-release-readiness`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-27-v0-7-governance-release-readiness`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-07-27-v0-7-governance-release-readiness`
- `created_at`: `2026-07-27T23:02:00+08:00`
- `updated_at`: `2026-07-27T23:35:51+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `release_target`: `v0.7.0`

## Objective And Scope

- Problem statement: v0.7.0 needs a portable work-management contract, fail-closed release-note backlog traceability, and deterministic proof that source-only governance history and GitHub-specific policy do not enter downstream package defaults.
- Authorized remediation scope: resolve `GOV-002` and `PKG-004` after implementation and verification; add `GOV-003` for the completed AI execution provenance policy; update backlog, release-state, release-note rendering and validation contracts; produce package manifest and fixture evidence; complete independent verification and PR integration.
- Exclusions: do not create or modify GitHub Issues or Projects; do not design tracker fields, views, automation, mappings, or adoption flows; do not create a v0.7.0 tag, hosted release, publication, or formal release candidate unless an isolated test fixture requires a synthetic candidate; do not alter existing tags; do not decide future GitHub provider adoption.
- Completion criteria: canonical v0.7.0 backlog membership equals `release.yaml.planning.backlog_refs` and the release note `Included Work` set; portable/source-only/target-customization/deferred-provider boundaries are explicit; package/install/upgrade evidence passes; `UPG-001` and `INIT-001` invariants remain unchanged; `ASM-20260727-002` independently verifies the remediation; workflow commits pass range validation and a ready PR merges through required checks.

## Owner Authorization And Boundaries

- Authorization source: owner request on 2026-07-27 in the active Codex task.
- Approved direction: retain only provider-neutral work lifecycle and repository-truth semantics in the portable framework contract.
- Deferred owner concern: actual GitHub Issues/Projects adoption remains outside this workflow and does not block the portable contract.
- PR transport: permitted solely for repository integration and is not evidence of tracker adoption.

## Artifact Contract

- Baseline assessments: `.dev/assessments/ASM-20260725-001/assessment.yaml` and `.dev/assessments/ASM-20260727-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-07-27-v0-7-governance-release-readiness/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260727-002/assessment.yaml`
- Tasks: `.dev/workflows/2026-07-27-v0-7-governance-release-readiness/tasks/`

## Finding Triage

| Finding / Work | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `GOV-003` provenance release trace | HIGH | governance | resolve for v0.7.0; publication remains null | `VGR-001` | backlog and release-state tests |
| release-note canonical backlog set | HIGH | governance | implement prospectively from v0.7.0 | `VGR-002` | positive and negative renderer/validator tests |
| `GOV-002` portable policy classification | HIGH | governance | resolve portable boundary; defer provider adoption | `VGR-003` | policy, payload, workflow and AI-context validation |
| `PKG-004` downstream payload safety | HIGH | governance | resolve after deterministic package and fixtures pass | `VGR-004` | manifest, diff, clean-install and upgrade evidence |
| independent verification and closure | HIGH | auditor / governance | verify, reconcile, and close | `VGR-005` | assessment, commit-range, one aggregate gate |

## Stages And Checkpoints

1. Freeze current source evidence and bootstrap the workflow on its dedicated branch.
2. Implement backlog and prospective release-note traceability.
3. Classify portable work-management policy and isolate source-only/provider-specific truth.
4. Produce deterministic downstream payload, clean-install, and upgrade evidence.
5. Run focused validation and the single applicable aggregate gate.
6. Obtain independent `ai-context-auditor` verification, reconcile findings, close, commit, and integrate through a ready PR.

## Resume Checkpoint

- Last completed action: completed `VGR-003` and `VGR-004`; portable policy projection, immutable payload manifests, deterministic archives, clean install, and initialized v0.6.0 upgrade evidence pass.
- Current task: `VGR-005`.
- Exact next action: obtain independent `ai-context-auditor` verification before resolving `GOV-002` and `PKG-004`.
- Validation already completed: release-state 23/23, release-note renderer 6/6, backlog release 6/6, package matrix 25 passed with 1 environment skip not counted as passed, profile projection 3/3, package apply 23 passed with 1 Windows capability skip not counted as passed, actual clean install and initialized upgrade passed, workflow artifacts, YAML parse, Python compile, and diff checks passed.
- Git state: branch `codex/2026-07-27-v0-7-governance-release-readiness` from clean `main`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: none; GitHub provider adoption is explicitly deferred and non-blocking.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-27-v0-7-governance-release-readiness` | `main@24d280cd4f60e5d5da46dbb62b5934c0a2718062` | active implementation | pending | local | `2026-07-27T23:02:00+08:00` | Owner authorized full v0.7.0 governance readiness through PR merge. | Continue through verification and closure on this branch. |
