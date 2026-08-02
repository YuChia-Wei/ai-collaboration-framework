# Standardize Python Prerequisite Diagnostics Across Validator Entrypoints

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-02-python-prerequisite-diagnostics`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics`
- `created_at`: `2026-08-02T10:32:53+08:00`
- `updated_at`: `2026-08-02T10:47:18+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Authorization And Decision Boundary

- Work-item binding: GitHub Issue [#69](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69).
- Baseline evidence: `.dev/assessments/ASM-20260730-001/assessment.yaml` and `ASM-20260730-001#AIC-004`.
- Authorization source: the repository owner requested on 2026-08-02 that this workflow be opened, that design decisions be discussed one at a time with impact explanations, and that approved design continue into implementation without closing this workflow.
- Authorized now: workflow bootstrap, repository-backed impact inventory, design discussion, and durable decision recording.
- Approval gate: implementation edits remain pending until the owner explicitly approves the accumulated design direction.
- Provider state: Issue #69 remains open with its existing proposal/triage labels; this workflow does not infer authorization from those labels and has not mutated the Issue.

## Objective And Scope

- Problem statement: the aggregate shell runner emits a repository-owned Python prerequisite diagnostic, while directly invoked validator and package entrypoints may raise raw `tomllib` or `yaml` import exceptions before they can explain the Python 3.11+ and pinned-dependency prerequisites.
- Authorized remediation scope: inventory supported user-facing Python entrypoints, decide a consistent fail-closed prerequisite contract, implement the approved design, add deterministic unsupported-version and missing-dependency coverage, synchronize user-facing commands and package projections, and verify that diagnostics occur before mutation or success claims.
- Exclusions: weakening validation, package, upgrade, or release gates; claiming support for Python versions below 3.11; silently installing dependencies; broad unrelated validator refactoring; release preparation or publication.
- Completion criteria: every approved supported entrypoint reports the selected executable/version, Python 3.11+ requirement, missing required dependency when applicable, sanctioned installation command, and pre-mutation stop state; deterministic negative-path tests pass; aggregate and direct behavior remain compatible; an independent post-remediation AI-context assessment reconciles `AIC-004`.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260730-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/reports/remediation-report.md` (created during remediation evidence consolidation)
- Verification assessment: `.dev/assessments/<verification-assessment-id>/assessment.yaml` (created after implementation and validation)
- Tasks: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/tasks/`
- Entrypoint inventory: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.md`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260730-001#AIC-004` | MEDIUM | `ai-context-governance` | design in progress; implementation authorized only after explicit design approval | `AIC-004-diagnostic-design`, then `AIC-004-diagnostic-implementation` | entrypoint inventory, deterministic prerequisite tests, affected validators/package tests, aggregate gates, independent verification assessment |

## Initial Impact Assessment

- Repository-native inventory found 74 tracked Python files on the candidate surfaces. Seventy have a direct `__main__` execution path: 25 production CLIs and 45 test CLIs; four are import-only support modules.
- The 25 production CLIs split into 12 portable payload entrypoints and 13 source-only maintainer/CI entrypoints under the current distribution profile.
- Twenty-three of the 25 production CLIs require PyYAML directly or through a local module. Two are standard-library-only. `validate-ai-context.py` additionally imports Python 3.11's `tomllib` before `main`.
- The package planner already has a one-off PyYAML diagnostic and a bytecode-suppression guard. Other dependency-bearing direct entrypoints generally import before a repository-owned diagnostic, so the current contract is inconsistent rather than wholly absent.
- Write-capable risk is concentrated in package apply and several source-only build/render/evaluation tools. Read-only validators still need the version gate so they cannot report success under an unsupported interpreter.
- The main design cost is not only a helper module: the approved boundary will affect entrypoint registration, import order, bytecode/no-write behavior, package projection, direct-command documentation, deterministic subprocess fixtures, and aggregate validation.
- Detailed evidence, category lists, and reproduction commands are retained in `evidence/entrypoint-inventory.md`.

## Discussion Contract And Decision Log

- Ask exactly one owner-decision question at a time.
- Before each question, explain the affected entrypoints, compatibility boundary, implementation/test cost, and failure-mode impact.
- Record each answer here before moving to the next decision.
- Keep the workflow active after design approval and transition directly to bounded implementation.

| Decision | Topic | Status | Owner Decision | Impact Summary |
| --- | --- | --- | --- | --- |
| `D-001` | Supported user-facing entrypoint boundary | pending |  | Determines which direct validators, skill-owned scripts, package tools, and compatibility paths must share the prerequisite contract. |
| `D-002` | Diagnostic delivery architecture | pending |  | Chooses shared bootstrap, wrapper routing, or bounded per-entrypoint handling and therefore affects coupling and package portability. |
| `D-003` | Diagnostic output and exit contract | pending |  | Defines stable fields, channel, exit status, and compatibility expectations for humans and automation. |
| `D-004` | Dependency prerequisite inventory and sanctioned install command | pending |  | Determines whether only PyYAML or every required runtime dependency is checked and how downstream users recover. |
| `D-005` | Pre-mutation guarantee and proof boundary | pending |  | Determines where checks must run and which write-capable paths require negative-path evidence. |
| `D-006` | Package/downstream projection and compatibility | pending |  | Determines what is portable, which documented commands change, and whether thin compatibility entrypoints remain. |
| `D-007` | Deterministic test matrix | pending |  | Determines interpreter/dependency simulation, platform coverage, and required closeout gates. |
| `D-008` | Documentation and migration communication | pending |  | Determines whether this is behavior clarification only or a documented command/contract migration. |

## Stages And Checkpoints

1. Bootstrap the governance workflow and freeze Issue #69 plus `AIC-004` as source evidence.
2. Inventory supported Python entrypoints, import timing, write potential, package inclusion, documented invocation, and current test coverage.
3. Resolve `D-001` through `D-008` one question at a time and obtain explicit approval for the accumulated design.
4. Implement the approved bounded remediation without broad validator redesign.
5. Run focused negative-path tests, affected validator/package checks, workflow/AI-context validation, and applicable aggregate gates.
6. Request an independent `ai-context-auditor` verification assessment and reconcile `AIC-004` in the remediation report.
7. Verify commits, task state, residual risks, and close the workflow only after implementation and verification complete.

## Resume Checkpoint

- Last completed action: created the workflow and completed a repository-native inventory of tracked Python entrypoints, distribution classification, prerequisite imports, direct documentation/runtime references, and current negative-path coverage.
- Current task: `AIC-004-diagnostic-design`.
- Exact next action: ask only `D-001` and record the owner's selected supported-entrypoint boundary before evaluating diagnostic architecture.
- Validation already completed: confirmed clean `main@2263744bb2dc876f8077547e961fc68be28b0074` before branching; verified the final baseline assessment; verified the inventory against `git ls-files`, direct file reads, distribution profile, shell registry, active documentation, and existing tests; parsed both task JSON files; `git diff --check`, `validate-workflow-artifacts.py`, and `validate-ai-context.py` passed.
- Validation environment note: the host `python` App Execution Alias has no installed interpreter. Validation used the Codex bundled Python 3.12.13 with `PyYAML==6.0.3` installed into an isolated temporary directory; no repository dependency files were changed.
- Git state: active branch `codex/2026-08-02-python-prerequisite-diagnostics`, created from `main@2263744bb2dc876f8077547e961fc68be28b0074`; durable workflow bootstrap commit `88a01bebfe95f696763c1b310c363f354949f205` exists locally.
- Branch history and checkpoint handoffs: bootstrap commit `88a01bebfe95f696763c1b310c363f354949f205`; no push or merge handoff has occurred.
- Blockers or unresolved decisions: `D-001` through `D-008` remain unresolved; implementation edits are paused pending explicit design approval.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | bootstrap | `88a01bebfe95f696763c1b310c363f354949f205` | local | `2026-08-02T10:45:48+08:00` | Preserve the authorized workflow and initial impact inventory before owner decisions. | Ask `D-001`; keep implementation pending until the accumulated design is explicitly approved. |
