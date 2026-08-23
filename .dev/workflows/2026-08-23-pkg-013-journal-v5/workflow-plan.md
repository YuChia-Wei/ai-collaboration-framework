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
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-08-23-pkg-013-journal-v5`
- `created_at`: `2026-08-23T18:53:54+08:00`
- `updated_at`: `2026-08-23T21:48:08+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #239 records quadratic write amplification because journal v4 rewrites the full completed-operation prefix after every durable operation.
- Authorization source: live GitHub Issue `YuChia-Wei/ai-collaboration-framework#239` and the owner delegation in the source Codex task.
- Authorized remediation scope: journal v5 persistence and recovery only; minimal v4 terminal/non-terminal mutation-safety classification; deterministic write-call/byte instrumentation; opt-in stderr progress; owning tests, schemas, templates, and documentation.
- Exclusions: v4 resume, rollback, migration, conversion, or dual recovery; Issues #149 and #168; CLI/runtime rewrite; downstream mutation; release notes; Issue/Project mutation, release allocation, tag, release, or publication. Push, PR #240, and merge-commit integration are now separately owner-authorized.
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
| Test execution | target-owned Python unittest commands | explicit lifecycle validation | fixed-head full suite passed 90/90 with one capability skip at `5b1060be`; final evidence-head rerun pending |
| Independent fixed-head review | read-only independent auditor | exact commit | `5b1060be` confirmed both prior P1 repairs and failed on one P2 stale-lifecycle contradiction; fresh evidence-head review pending |
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
7. Reconcile PR-head review evidence, then admit and integrate only an exact clean head with successful full validation, hosted checks, independent audit, and live provider read-back; keep Issue/Project/release actions separate.

## Resume Checkpoint

- Last completed action: `d2a471ec2210ffc429f81734853cea7223357747` passed 90/90 full validation, but its audit retained P2=1 because its `updated_at` value preceded the completion receipt it recorded.
- Current task: this SHA-neutral candidate contains only the chronology repair and retained failure evidence; exact-head full validation and independent review are pending.
- Exact next action: rerun immutable-head full validation and independent review, require five successful hosted checks, capture live admission, then integrate PR #240 using merge-commit topology.
- Validation completed: `5b1060be`, `0bcb6e25`, `5b65ca6c`, and `d2a471ec` each passed 90 tests with 0 failures and 1 Windows capability skip using schema-valid dispatch/completion evidence; their respective P2 audit failures remain retained.
- Git state: branch `codex/issue-239-journal-v5`; the current PR candidate contains the committed timestamp-chronology repair and must remain unchanged through its exact-head gates.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: merge is blocked until the reconciled exact head passes full validation, independent audit, hosted checks, and live admission; release allocation remains intentionally unassigned.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | local implementation | `c3ffc2f4d2b576943595f2b0b99692f39d7895e5` | none | `2026-08-23T20:27:05+08:00` | Issue #239 implementation, full validation, and accepted fixed-head audit complete | historical local-only checkpoint; superseded by segment 2 owner authorization |
| 2 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | PR-head remediation | `5b1060bed0056271ba7406810e5e4c5f519ffffc` | PR #240 | `2026-08-23T21:10:52+08:00` | Full suite passed and implementation P1 findings resolved; audit retained one P2 stale-lifecycle contradiction | reconcile all workflow truth, commit, and rerun exact-head gates |
| 3 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | lifecycle-evidence reconciliation | `0bcb6e25d8a1490e0ecb33d3ab7d3cd3d6754eb5` | PR #240 | `2026-08-23T21:10:52+08:00` | Full suite passed; audit retained one P2 self-referential pending/current-state contradiction | commit SHA-neutral current truth and rerun exact-head gates |
| 4 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | lifecycle-timestamp repair | `5b65ca6c266c637353393279ce2717bcac9143d4` | PR #240 | `2026-08-23T21:34:50+08:00` | Full suite passed; audit retained one P2 stale `updated_at` metadata finding | update every materially changed lifecycle surface and rerun exact-head gates |
| 5 | `codex/issue-239-journal-v5` | `main` at `92270db07404602210d1c24594a669709dbd5b1f` | timestamp chronology repair | `d2a471ec2210ffc429f81734853cea7223357747` | PR #240 | `2026-08-23T21:48:08+08:00` | Full suite passed; audit retained one P2 because `updated_at` preceded the recorded completion receipt | use a timestamp after both validation and audit evidence, then rerun exact-head gates |
