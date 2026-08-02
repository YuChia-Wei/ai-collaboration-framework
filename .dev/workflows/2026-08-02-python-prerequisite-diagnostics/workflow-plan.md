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
- `updated_at`: `2026-08-02T12:39:54+08:00`
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
- Exclusions: weakening validation, package, upgrade, or release gates; claiming support for Python versions below 3.11; silently or implicitly installing Python/dependencies without a later explicit owner decision; broad unrelated validator refactoring; release preparation or publication.
- Completion criteria: every approved supported entrypoint reports the selected executable/version, Python 3.11+ requirement, missing required dependency when applicable, sanctioned installation command, and pre-mutation stop state; deterministic negative-path tests pass; aggregate and direct behavior remain compatible; an independent post-remediation AI-context assessment reconciles `AIC-004`.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260730-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/reports/remediation-report.md` (created during remediation evidence consolidation)
- Verification assessment: `.dev/assessments/<verification-assessment-id>/assessment.yaml` (created after implementation and validation)
- Tasks: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/tasks/`
- Entrypoint inventory (English agent-facing source): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.md`
- Entrypoint inventory (complete Traditional Chinese Taiwan owner-review translation): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/entrypoint-inventory.zh-TW.md`
- Runtime fallback and ownership assessment (English agent-facing source): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/runtime-fallback-and-ownership-assessment.md`
- Runtime fallback and ownership assessment (complete Traditional Chinese Taiwan owner-review translation): `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/runtime-fallback-and-ownership-assessment.zh-TW.md`
- Python runtime selection history, OS-native alternatives, and translation-routing deviation: `.dev/workflows/2026-08-02-python-prerequisite-diagnostics/evidence/python-runtime-selection-history-and-native-options.md`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260730-001#AIC-004` | MEDIUM | `ai-context-governance` | D-001 approved; remaining design in progress; implementation authorized only after explicit accumulated-design approval | `AIC-004-diagnostic-design`, then portable `AIC-004-diagnostic-implementation`, then `AIC-004-source-diagnostic-implementation` | entrypoint inventory, fallback/ownership assessment, deterministic prerequisite tests, affected validators/package tests, aggregate gates, independent verification assessment |

## Initial Impact Assessment

- Repository-native inventory found 74 tracked Python files on the candidate surfaces. Seventy have a direct `__main__` execution path: 25 production CLIs and 45 test CLIs; four are import-only support modules.
- The 25 production CLIs split into 12 portable payload entrypoints and 13 source-only maintainer/CI entrypoints under the current distribution profile.
- Twenty-three of the 25 production CLIs require PyYAML directly or through a local module. Two are standard-library-only. `validate-ai-context.py` additionally imports Python 3.11's `tomllib` before `main`.
- The package planner already has a one-off PyYAML diagnostic and a bytecode-suppression guard. Other dependency-bearing direct entrypoints generally import before a repository-owned diagnostic, so the current contract is inconsistent rather than wholly absent.
- The current Windows host exposed a separate bootstrap boundary: `python` and `python3` resolve to unprovisioned Windows App Execution Aliases, so a direct `python <script>.py` invocation fails before repository Python code can run. A later probe found a usable uv-managed `python3.14` command that the current resolver misses, but that interpreter and the current Codex bundled Python both lack PyYAML. Candidate discovery and dependency readiness must therefore remain separate checks.
- Write-capable risk is concentrated in package apply and several source-only build/render/evaluation tools. Read-only validators still need the version gate so they cannot report success under an unsupported interpreter.
- The main design cost is not only a helper module: the approved boundary will affect entrypoint registration, import order, bytecode/no-write behavior, package projection, direct-command documentation, deterministic subprocess fixtures, and aggregate validation.
- D-001 is approved as Option A with an ordered portable-first rollout: the 12 downstream/portable CLIs form the first implementation and validation batch; the 13 source-only CLIs form a second batch that cannot start until the first reaches its approved gate.
- Existing ownership policy and deterministic tests currently classify two canonical skill-owned production scripts, one root compatibility entrypoint, and 22 repo-common production scripts. The owner requested a fresh ownership decision before implementation; the preliminary per-entrypoint matrix remains a recommendation, not an approval.
- Git history contains no current comparison-backed ADR that selects Python as the canonical validator runtime. Python entered incrementally, PyYAML spread when nested YAML validation was added, and dependency/bootstrap declarations followed clean-environment failures. Retaining Python is therefore a pending design decision rather than established owner-approved rationale.
- A historical, now-retired `ADR-052` acknowledged that its Markdown parser required Python but treated that prerequisite as a consequence; it did not compare runtime alternatives. Full OS-native validator rewrites would create multiple platform implementations and YAML parsing gaps, while thin OS-native launchers remain a bounded candidate for discovery and diagnostics.
- The two existing zh-TW evidence files were produced by the primary `gpt-5.6-sol` agent even though active routing assigns finalized derived translations to the low-cost `context-translator` (`gpt-5.6-terra`, low reasoning). Their parity checks passed, but the cost-routing process was not followed; corrective handling is pending owner direction.
- Detailed inventory and fallback/ownership evidence are retained in the English evidence files with complete owner-review translations in their `.zh-TW.md` companions.

## Discussion Contract And Decision Log

- Ask exactly one owner-decision question at a time.
- Before each question, explain the affected entrypoints, compatibility boundary, implementation/test cost, and failure-mode impact.
- Record each answer here before moving to the next decision.
- Keep the workflow active after design approval and transition directly to bounded implementation.

| Decision | Topic | Status | Owner Decision | Impact Summary |
| --- | --- | --- | --- | --- |
| `D-001` | Supported user-facing entrypoint boundary | resolved | Option A: cover all 25 production CLIs, exclude 45 direct test CLIs and four import-only modules; implement and validate the 12 portable/downstream CLIs before the 13 source-only CLIs. | Establishes complete production coverage while creating two ordered, separately reviewable implementation batches. |
| `D-002` | Diagnostic fallback and delivery architecture umbrella | decomposed | Evaluate fail-closed behavior, automatic installation, host/versioned/provider-runtime discovery, and OS-native launchers one subdecision at a time. | Prevents unlike trust, mutation, portability, and launcher questions from being collapsed into one approval. |
| `D-002A` | Default action when no fully ready environment is found | resolved | Perform read-only discovery only; if no fully ready environment exists, do not execute the target CLI, install anything, create an environment, or modify the host/repository. Fail closed with diagnostics and explicit recovery guidance. | Establishes a no-work/no-mutation terminal state while leaving separately invoked, explicitly authorized bootstrap options open for D-004. |
| `D-002B` | Trusted interpreter discovery sources and order | pending |  | Determines precedence for owner overrides, generic/versioned host commands, uv or other managers, and optional agent-tool adapters. |
| `D-002C` | OS-native launcher coverage and delegation boundary | pending |  | Determines Windows/POSIX support and whether native scripts only resolve/diagnose or duplicate Python validator semantics. |
| `D-003` | Diagnostic output and exit contract | pending |  | Defines stable fields, channel, exit status, and compatibility expectations for humans and automation. |
| `D-004` | Dependency prerequisite inventory and sanctioned recovery/install operation | pending |  | Determines whether only PyYAML or every required runtime dependency is checked, which recovery command is printed, and whether an explicit isolated bootstrap mode is offered. |
| `D-005` | Pre-mutation guarantee and proof boundary | pending |  | Determines where checks must run and which write-capable paths require negative-path evidence. |
| `D-006` | Canonical script ownership, shared prerequisite placement, package projection, and compatibility | pending |  | Determines which CLIs remain skill-owned or repo-common, where shared prerequisite code lives, what is portable, and which thin compatibility entrypoints remain. |
| `D-007` | Deterministic test matrix | pending |  | Determines interpreter/dependency simulation, platform coverage, and required closeout gates. |
| `D-008` | Documentation and migration communication | pending |  | Determines whether this is behavior clarification only or a documented command/contract migration. |
| `D-009` | Canonical validator runtime disposition | pending |  | Determines whether Python remains the canonical implementation under Issue #69, a runtime migration enters this workflow, or runtime replacement becomes a separate governed proposal. This must be resolved before implementation can entrench the current dependency. |
| `D-TR-001` | Corrective handling for the two primary-agent zh-TW translations | pending |  | Determines whether the low-cost `context-translator` should replace/revalidate both derived files before substantive design discussion continues. |

## Translation Routing Deviation

- Active repository routing assigns finalized derived Traditional Chinese translations to `context-translator`; the Codex adapter selects `gpt-5.6-terra` with low reasoning.
- The primary agent instead translated `entrypoint-inventory.zh-TW.md` and `runtime-fallback-and-ownership-assessment.zh-TW.md` using `gpt-5.6-sol` with high reasoning.
- Cause: the primary agent consulted the language/governance policies but failed to discover and apply `.ai/SUB-AGENT-SYSTEM.MD` before translation. No runtime limitation required this bypass.
- Impact: structural and semantic parity checks passed, so the content is not automatically invalid, but the requested low-cost delegation contract was violated.
- Correction remains pending `D-TR-001`; no translation is being represented as low-cost-sub-agent output retroactively.

## Stages And Checkpoints

1. Bootstrap the governance workflow and freeze Issue #69 plus `AIC-004` as source evidence.
2. Inventory supported Python entrypoints, import timing, write potential, package inclusion, documented invocation, and current test coverage.
3. Resolve the remaining decision log one question at a time and obtain explicit approval for the accumulated design.
4. Implement and validate the approved 12-entry portable/downstream batch without broad validator redesign.
5. Begin the 13-entry source-only batch only after the portable batch reaches its approved checkpoint.
6. Run focused negative-path tests, affected validator/package checks, workflow/AI-context validation, and applicable aggregate gates.
7. Request an independent `ai-context-auditor` verification assessment and reconcile `AIC-004` in the remediation report.
8. Verify commits, task state, residual risks, and close the workflow only after implementation and verification complete.

## Resume Checkpoint

- Last completed action: resolved D-002A as fail-closed/no-work/no-mutation, reconstructed the incremental Python/PyYAML adoption history, assessed OS-native alternatives, and recorded the missed low-cost translation route without retroactively changing provenance.
- Current task: `AIC-004-diagnostic-design`.
- Exact next action: ask only `D-TR-001` whether the two existing owner-review translations should be replaced/revalidated by the promoted low-cost `context-translator` before returning to runtime-design decisions.
- Validation already completed: confirmed clean `main@2263744bb2dc876f8077547e961fc68be28b0074` before branching; verified the final baseline assessment; verified the inventory against `git ls-files`, direct file reads, distribution profile, shell registry, active documentation, and existing tests; parsed both task JSON files; `git diff --check`, `validate-workflow-artifacts.py`, and `validate-ai-context.py` passed.
- Current discussion-checkpoint validation: Git-history probes established the adoption timeline; the active sub-agent manifest and Codex adapter established the missed low-cost route; the changed task JSON parsed with PowerShell; locator/index state was checked directly; and `git diff --check` passed. Full Python-backed repository validators were not rerun because every discovered interpreter lacks PyYAML and D-002A now forbids implicit installation; this checkpoint records that result as `blocked-by-environment`, not passed.
- Validation environment note: generic `python` and `python3` resolve to unusable Windows aliases. A versioned uv-managed Python 3.14.1 and the Codex bundled Python 3.12.13 can start, but neither currently imports PyYAML. Prior artifact validation used Codex Python with isolated temporary `PyYAML==6.0.3`; no repository dependency files were changed.
- Git state: active branch `codex/2026-08-02-python-prerequisite-diagnostics`, created from `main@2263744bb2dc876f8077547e961fc68be28b0074`; the latest durable design commit before this discussion is `d5ae808626508cba857ea412ae1d543fa86095e6`.
- Branch history and checkpoint handoffs: bootstrap commits `88a01bebfe95f696763c1b310c363f354949f205` and `4e93c0f09cae2c50bf6a330de0cca05c8b52fec6`; absent-interpreter boundary commit `cd58c2b0391dccb4a8487f33938b8a3c5d060500`; inventory translation commit `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0`; D-001/fallback assessment commit `d5ae808626508cba857ea412ae1d543fa86095e6`; no push or merge handoff has occurred.
- Blockers or unresolved decisions: `D-TR-001`, `D-002B` onward, and `D-009` remain unresolved; implementation edits are paused pending explicit accumulated-design approval.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | bootstrap | `88a01bebfe95f696763c1b310c363f354949f205` | local | `2026-08-02T10:45:48+08:00` | Preserve the authorized workflow and initial impact inventory before owner decisions. | Ask `D-001`; keep implementation pending until the accumulated design is explicitly approved. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | design evidence | `cd58c2b0391dccb4a8487f33938b8a3c5d060500` | local | `2026-08-02T10:57:23+08:00` | Preserve the observed absent-interpreter boundary without resolving D-001 or D-002. | Provide the requested complete zh-TW inventory, then ask only `D-001`. |
| 1 | `codex/2026-08-02-python-prerequisite-diagnostics` | `main@2263744bb2dc876f8077547e961fc68be28b0074` | owner-review translation | `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0` | local | `2026-08-02T11:05:29+08:00` | Preserve the complete Traditional Chinese Taiwan inventory used for the D-001 owner decision. | Record D-001 and evaluate fallback/ownership before asking D-002A. |
