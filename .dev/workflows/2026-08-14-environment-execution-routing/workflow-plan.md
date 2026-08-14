# Portable CLI Execution Routing

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-14-environment-execution-routing`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-14-environment-execution-routing`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-14-environment-execution-routing`
- `created_at`: `2026-08-14T21:40:34+08:00`
- `updated_at`: `2026-08-14T22:40:39+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #210 identifies the missing boundary between portable environment readiness and deterministic CLI execution routing. Repeated host, sandbox, WSL, and executable-selection failures cannot be safely prevented while concrete CLI routes exist only in conversation memory or tracked repository guidance.
- Authorized remediation scope: Implement the owner-approved Issue #210 contract: Git tracks only the portable CLI contract/schema, non-personal enforcement, and the ignore rule; personal CLI route values remain in a conventional Git-ignored local file; after bounded CLI diagnosis succeeds, the agent must ask before persisting the reusable route. Connector, CI, external-task, browser, and delegation routing remain outside the local record.
- Exclusions: Do not write a personal local binding without a separate post-recovery consent decision. Do not store credentials, tokens, sessions, private endpoints, usernames, or source-host defaults in tracked files. Do not push, open a pull request, merge, release, or publish.
- Completion criteria: A portable CLI contract and schema define command route, readiness, evidence, retry, fallback, consent, and storage semantics; the conventional local path is proven Git-ignored; deterministic validation rejects tracked, sensitive, ambiguous, unauthorized, and non-CLI bindings; downstream packaging exposes the portable contract but excludes personal values; focused Windows and Ubuntu-24.04 validation passes; independent verification is recorded after the owner reviews the result shape.

## Authorization And Delivery

- Work item: GitHub Issue `#210`, `[TOOL-005] Define Portable CLI Execution Routing Standard`.
- Authorization: Owner message on 2026-08-14: `OK，進行實作，我要看成果的樣態再跟你說怎麼調整`.
- Scope correction: Owner message on 2026-08-14: `OK，改 CLI-EXECUTION-ROUTING-CONTRACT`; the local contract is CLI-only and must not configure connector, CI, external-task, browser, or delegation routing.
- Delivery cohesion: Contract, local-binding boundary, validation, package projection, and agent behavior form one atomic portable capability and share one review, rollback, and compatibility boundary.
- Workflow justification: This changes canonical portable rules and future agent behavior across `.ai`, `.dev`, runtime discovery, packaging, and validation. The workflow preserves the owner review checkpoint before independent verification and closure.
- Planned topology: Merge-commit integration. The branch now contains durable owner-review, personal-binding consent, named WSL cross-host validation, and independent verification checkpoints that should remain grouped as one review and rollback unit.

## Artifact Contract

- Baseline assessment: `not-applicable`; Issue #210 plus completed readiness Issue #147 are the approved design baseline.
- Remediation report: `.dev/workflows/2026-08-14-environment-execution-routing/reports/remediation-report.md`
- Verification assessment: `ASM-20260814-001`; final at fixed subject commit `cca50f67` with no blocking finding.
- Tasks: `.dev/workflows/2026-08-14-environment-execution-routing/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `Issue-210-contract` | high | `ai-context-governance` | implement | `ENVROUTE-001-contract-schema` | schema and contract tests |
| `Issue-210-local-persistence` | high | `ai-context-governance` | implement | `ENVROUTE-002-local-binding` | ignore, consent, and sensitive-field negative tests |
| `Issue-210-downstream` | high | `ai-context-governance` | implement | `ENVROUTE-003-downstream-integration` | package, init/upgrade, Windows, and WSL checks |
| `Issue-210-verification` | high | `ai-context-auditor` | verified | `VERIFY-001-independent-audit` | `ASM-20260814-001` |

## Stages And Checkpoints

1. Freeze Issue #210 authorization and inventory existing readiness, package, init, upgrade, and validation boundaries. `completed`
2. Implement the provider-neutral contract and schema. `completed`
3. Implement Git-ignored local-binding validation and post-recovery consent behavior. `completed`
4. Integrate downstream packaging and compatibility checks. `completed`; lifecycle component projection passed against immutable commit `0970685`.
5. Run focused Windows and explicit `Ubuntu-24.04` WSL validation outside the sandbox. `completed`; the immutable commit passed 8/8 in Ubuntu-24.04.
6. Present the implementation shape for owner review and adjustment. `completed`; the owner approved CLI-only scope, requested the per-machine binding, and authorized PR integration.
7. After owner review, obtain independent verification and reconcile the workflow. `completed`; `ASM-20260814-001` found no blocking regression.
8. Push, open a ready pull request, require hosted checks and stable head, then merge to `main` using merge-commit topology. `authorized external delivery gate`; this transport step does not redefine workflow completion.

## Resume Checkpoint

- Last completed action: `ASM-20260814-001` independently verified fixed subject commit `cca50f67` after owner acceptance; Windows and Ubuntu-24.04 focused tests, source validation with four local routes, package projection, ignore checks, and assessment validation passed.
- Current task: Local workflow closure is complete. Remote PR transport and hosted integration are the authorized next gate, not an unfinished remediation task.
- Exact next action: Validate the full workflow commit range, push the branch, create a ready PR to `main`, watch hosted checks once, and merge only if the head remains unchanged and all gates pass.
- Validation already completed: CLI-only routing GWT 9/9 on Windows and Ubuntu-24.04; wrapper metadata 16/16; language policy 10/10; Python entrypoints 4/4; committed package lifecycle projection 1/1; source AI-context and assessment validators passed; local route remains ignored/untracked; `git diff --check` passed.
- Git state: Verification assessment commit `a6a0625` follows the validated implementation at `cca50f67` on `codex/2026-08-14-environment-execution-routing`; no push, pull request, or merge at this checkpoint.
- Branch history and checkpoint handoffs: None.
- Blockers or unresolved decisions: None locally. Hosted checks and stable-head read-back remain fail-closed external merge gates.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-14-environment-execution-routing` | `main` | local-owner-review | `0970685` | local | `2026-08-14T22:05:43+08:00` | Implemented and validated Issue #210 without creating personal local state | Present result shape; adjust on this branch or proceed to independent verification after owner decision |
| 2 | `codex/2026-08-14-environment-execution-routing` | `main` | local-owner-adjustment | `f7529ee` | local | `2026-08-14T22:22:26+08:00` | Restricted the contract and local binding to CLI-only execution routing | Present corrected shape; retain `VERIFY-001` as pending until owner acceptance |
| 3 | `codex/2026-08-14-environment-execution-routing` | `main` | local-verification | `a6a0625` | local | `2026-08-14T22:40:39+08:00` | Owner accepted the shape, requested the machine-local binding, authorized PR integration, and `ASM-20260814-001` found no blocking regression | Validate and push this branch; create a ready PR and merge only after hosted gates pass |
