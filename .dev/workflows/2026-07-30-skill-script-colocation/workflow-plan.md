# Co-locate Skill-Owned Scripts With Canonical Skills

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-30-skill-script-colocation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-30-skill-script-colocation`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-07-30-skill-script-colocation`
- `created_at`: `2026-07-30T09:40:38+08:00`
- `updated_at`: `2026-07-30T10:04:01+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Authorization And Release Boundary

- The owner approved GitHub Issue [#65](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/65), `SKILL-002` implementation, and allocation as a required `v0.8.0` release blocker on 2026-07-30.
- This workflow may complete `SKILL-002` and update `v0.8.0` planning truth.
- This workflow must not create a release candidate, `.dev/releases/v0.8.0/`, a tag, a GitHub Release, or a published package.
- Release preparation and publication require a later, separately authorized workflow after every `v0.8.0` blocker is resolved.

## Objective And Scope

- Problem statement: Python executables and contract tests with one canonical skill owner are mixed with shared and source-only repository automation under `.ai/scripts/`, obscuring ownership and making skill portability harder to reason about.
- Authorized remediation scope: move only files with one evidence-backed canonical skill owner into `.ai/assets/skills/<skill-id>/scripts/`, keep shared automation centralized, retain necessary compatibility entrypoints, and synchronize active references, distribution classification, tests, indexes, and guides.
- Exclusions: release candidate creation, release publication, unrelated skill redesign, legacy identifier retirement, historical workflow rewrites, shell compatibility-entrypoint relocation, and provider redesign.
- Completion criteria: the ownership rule is documented; canonical files and active references are colocated; compatibility paths are explicit; focused and aggregate validation passes; package component classification remains deterministic; `SKILL-002` records implementation evidence without claiming publication.

## Ownership Classification

| Current Path | Owner | Action | Reason |
| --- | --- | --- | --- |
| `.ai/scripts/compare-ai-context-versions.py` | `ai-context-upgrader` | move | Read-only three-way upgrade comparison is exclusive to the upgrader lifecycle and is source-only. |
| `.ai/scripts/validate-software-development-orchestrator-acceptance.py` | `software-development-orchestrator` | move plus compatibility entrypoint | The canonical skill declares it as its acceptance validator; the published path remains callable. |
| `.ai/scripts/tests/test_software_development_orchestrator_acceptance.py` | `software-development-orchestrator` | move plus compatibility entrypoint | End-to-end acceptance belongs only to this skill. |
| `.ai/scripts/tests/test_software_development_orchestrator_capability_contract.py` | `software-development-orchestrator` | move plus compatibility entrypoint | Capability-profile checks belong only to this skill. |
| `.ai/scripts/tests/test_workflow_implementation_contract.py` | `software-development-orchestrator` | move plus compatibility entrypoint | The test covers the development implementation-task contract owned by the orchestrator. |
| Target provenance, workflow, handoff, package, release, provider, evaluation, and multi-skill transition tools | shared or source-repository-wide | keep under `.ai/scripts/` | They have multiple consumers or repository-wide lifecycle authority. |
| Published shell compatibility entrypoints | compatibility | defer | Their relocation requires separate shell lifecycle and downstream evidence; it is not silently included in this batch. |

## Artifact Contract

- Baseline assessment: not applicable; the user request and repository-native ownership evidence authorize this bounded cleanup.
- Remediation report: `.dev/workflows/2026-07-30-skill-script-colocation/reports/remediation-report.md`
- Verification assessment: not required for this bounded owner-requested cleanup; deterministic repository and package validation is mandatory.
- Tasks: `.dev/workflows/2026-07-30-skill-script-colocation/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `SKILL-002` | HIGH | `ai-context-governance` | remediate | `SKILL-002-script-colocation` | focused tests, package projection, AI-context/workflow validators, quick gate |

## Stages And Checkpoints

1. Register Issue #65, `SKILL-002`, and `v0.8.0` planning without creating a release candidate.
2. Freeze the single-owner versus shared/source-only inventory.
3. Move canonical Python implementations and tests; retain thin compatibility entrypoints where published commands require them.
4. Synchronize skill specs, active docs, runners, distribution rules, provider projection, and tests.
5. Run focused validation, package projection and upgrade-safety checks, repository validators, and the quick gate.
6. Record remediation evidence and resolve `SKILL-002` with `completed_in: v0.8.0` while leaving `published_in` unset.

## Resume Checkpoint

- Last completed action: canonical single-owner scripts were colocated, active routes were synchronized, compatibility entrypoints were exercised, and focused validation passed outside the Windows sandbox.
- Current task: `SKILL-002-script-colocation`.
- Exact next action: commit the immutable-tree checkpoint, then run package projection and aggregate repository gates against the new `HEAD`.
- Validation already completed: repository and skill inventory; duplicate open-Issue search; branch creation; canonical and compatibility orchestrator tests; AI-context, workflow, shell-asset, source-governance, active-reference, and colocation validation.
- Git state: `codex/2026-07-30-skill-script-colocation` from `main@fc878b934b8ac15fb6be2ae238c790ab9caad3cc`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: Windows sandbox cannot write Python temporary subdirectories, so temp-dependent tests must run outside the sandbox; release candidate creation and publication remain explicitly outside this workflow.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-30-skill-script-colocation` | `main@fc878b934b8ac15fb6be2ae238c790ab9caad3cc` | active | pending | local | `2026-07-30T09:40:38+08:00` | Implement `SKILL-002` without release publication. | Continue on this branch. |
