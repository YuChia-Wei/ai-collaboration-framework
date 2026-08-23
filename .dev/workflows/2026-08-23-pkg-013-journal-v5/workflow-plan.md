# PKG-013 Journal v5 Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-23-pkg-013-journal-v5`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `orchestrator_skill`: `software-development-orchestrator`
- `branch`: `codex/issue-239-journal-v5`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-23-pkg-013-journal-v5`
- `created_at`: `2026-08-23T18:53:54+08:00`
- `updated_at`: `2026-08-23T20:15:38+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #239 records quadratic write amplification because journal v4 rewrites the full completed-operation prefix after every durable operation.
- Authorization source: live GitHub Issue `YuChia-Wei/ai-collaboration-framework#239` and the owner delegation in the source Codex task.
- Authorized remediation scope: journal v5 persistence and recovery only; minimal v4 terminal/non-terminal mutation-safety classification; deterministic write-call/byte instrumentation; opt-in stderr progress; owning tests, schemas, templates, and documentation.
- Exclusions: v4 resume, rollback, migration, conversion, or dual recovery; Issues #149 and #168; CLI/runtime rewrite; downstream mutation; release notes; push, PR, merge, Issue/Project mutation, release allocation, tag, release, or publication.
- Completion criteria: v5 write work is linear or bounded; each completed operation is durable before the next starts; v5 resume/rollback/idempotency/crash boundaries remain exact; unfinished v4 blocks safely while terminal v4 does not; stdout remains unchanged without progress text; focused and proportionate validation pass on the exact reviewed commit.
- Release impact: breaking journal contract, provisionally suitable for a future minor release such as v0.15.0; allocation remains owner-unassigned.

## Artifact Contract

- Baseline assessment: `not-applicable`; live Issue #239 and current repository contracts are the accepted requirement baseline.
- Remediation report: `.dev/workflows/2026-08-23-pkg-013-journal-v5/reports/remediation-report.md`
- Independent review: `.dev/workflows/2026-08-23-pkg-013-journal-v5/review-report.md`
- Tasks: `.dev/workflows/2026-08-23-pkg-013-journal-v5/tasks/`

## Capability Routing

| Stage | Owning capability | Route | Disposition |
| --- | --- | --- | --- |
| Workflow coordination | `software-development-orchestrator` | direct orchestration | active |
| AI-context package lifecycle governance | `ai-context-governance` | workflow owner | active |
| GWT scenario design | `bdd-gwt-test-designer` | direct, pre-implementation | completed |
| Bounded implementation and concrete tests | `slice-implementer` | generic execution mode | completed |
| Test execution | target-owned Python unittest commands | explicit lifecycle validation | focused checks passed; fixed-head full suite pending |
| Independent fixed-head review | read-only independent auditor | exact commit | four candidates rejected; transaction-root ancestor boundary remediation pending fresh review |
| .NET code-review route | `code-reviewer` | not applicable to the Python and YAML/Markdown subject | not-applicable |
| Spec compliance | `spec-compliance-validator` | not selected by owner or target profile for this Issue | not-applicable |

## BDD Scenario Intent

The `bdd-gwt-test-designer` stage must cover at least:

1. Given N v5 apply operations, when each completes, then durable journal writes and bytes grow linearly and each completion is replayable before the next operation starts.
2. Given a crash immediately before or after an append durability boundary, when v5 resumes, then the affected operation is applied exactly once and the target is not corrupted.
3. Given partial v5 work, when rollback is interrupted and resumed, then each pre-state path is restored exactly once using append-only rollback progress.
4. Given an unfinished v4 journal, when a new apply would mutate the target, then mutation is blocked with stable unsupported-version guidance and no v4 recovery occurs.
5. Given only terminal or archival v4 journals, when a new v5 apply starts, then the v4 evidence does not block it and remains unchanged.
6. Given `--progress`, when apply/resume/rollback runs, then progress appears only on stderr and stdout preserves its existing machine-readable contract.

## Stages And Checkpoints

1. Bind Issue #239, branch, workflow, and current contracts.
2. Resolve framework-source effective-rule evidence for selected routed actions.
3. Design GWT scenarios and implement the bounded v5 slice plus tests and owning documentation.
4. Run focused validation, then broader repository-owned checks proportionate to risk.
5. Commit a clean implementation candidate and bind an independent read-only review to that exact commit.
6. Repair only within authorized scope; any repair invalidates the prior review and requires a new exact-head review.
7. Finalize workflow evidence and local commits without any remote or release mutation.

## Resume Checkpoint

- Last completed action: full suite passed at `679bc0bea9c08176c3495946fb0c228ef4f4e6a2`, but its audit rejected a transaction-root ancestor symlink/junction that bypassed leaf-only checks; GWT-070 now covers recovery, append, and target admission without external or next-operation mutation.
- Current task: `PKG-013-journal-v5` fourth fixed-head finding remediation.
- Exact next action: commit transaction-root boundary hardening, rerun full fixed-head validation, and obtain a fresh independent audit of the new SHA.
- Validation already completed: fixed-head suites at the first four candidates passed 82, 84, 86, and 87 tests but cannot override their failed audits; GWT-070 and focused normal resume, legacy, leaf-link, and safe-add tests pass after the current repair. A wrong normal-apply selector produced one retained unittest loader error before the corrected selector passed.
- Git state: branch `codex/issue-239-journal-v5`; four failed-audit candidates retained plus uncommitted transaction-root hardening.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: none; release allocation remains intentionally unassigned.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | local implementation | pending | none | `2026-08-23T18:53:54+08:00` | Issue #239 authorized local workflow and commits | continue locally |
