# AI Context Maintenance Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-04-framework-managed-ignore-detection`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-04-framework-managed-ignore-detection`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-08-04-framework-managed-ignore-detection`
- `created_at`: `2026-08-04T21:49:30+08:00`
- `updated_at`: `2026-08-04T22:41:37+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: A selected framework-managed package path can be written below a target Git ignore rule, remain invisible to `git status`, and reach a pending-validation receipt without the planner or target validator preserving the ignored-path identity.
- Authorized remediation scope: Implement the smallest portable fail-closed package-plan, apply, target-validation, and finalization contract for Git-ignored selected framework-managed paths, with synthetic cross-platform fixtures and canonical guidance.
- Authorization: The owner explicitly authorized arranging and executing GitHub Proposal #93 on 2026-08-04. Issue #93 is an optional work-item binding, not the authorization by itself.
- Exclusions: REL-004; GitHub Proposals #92 and #94; release allocation or publication; automatic modification of target-owned ignore configuration; repository-wide terminology rename; product implementation trees.
- Completion criteria: The plan records exact ignored path/component/ownership/rule and permitted owner dispositions; apply fails before writes for unresolved selected paths; pending-receipt target validation and provenance finalization reject the same missing or ignored managed path; Windows/POSIX and exact-case fixtures pass; a separate verification assessment and durable handoff are complete.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260804-003/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-04-framework-managed-ignore-detection/reports/remediation-report.md`
- Verification assessment: allocated only after a refreshed all-branch assessment-ID check.
- Tasks: `.dev/workflows/2026-08-04-framework-managed-ignore-detection/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260804-003#AIC-001` | HIGH | `ai-context-governance` | authorized remediation | `IGN93-002` | focused package/apply and semantic-lifecycle GWT suites; target critical-gate route |

## Stages And Checkpoints

1. Baseline audit and evidence freeze — completed at `main@4e7b5e0d59be831453b5c34f5f1eb3a1daae1245`.
2. Finding triage and remediation authorization — completed from the delegated owner authorization and current Issue #93 acceptance criteria.
3. Bounded remediation and focused validation — completed.
4. Independent post-remediation audit — in progress.
5. Finding reconciliation, commit verification, and closure — pending.

## Workflow Proportionality And Delivery Decisions

- This one-issue workflow is retained because it preserves an explicit owner authorization, a durable cross-surface safety contract, a baseline-to-verification assessment lifecycle, and a receiving checkpoint. These states are not adequately owned by Issue #93, a commit, or a pull request alone.
- Delivery grouping: #93 only. It has independent scope, validation, review, rollback, and release boundaries from REL-004, #92, and #94.
- Integration gate: pull request to `main` under `.dev/TEAM-GIT-FLOW-RULES.MD`.
- Proposed topology: linear integration, unless a later checkpoint/handoff makes the branch boundary durable integration evidence.

## Resume Checkpoint

- Last completed action: Implemented shared exact-path Git-ignore evidence, receipt identity binding, apply rejection, target validation/finalization/init fail-closed checks, and critical-gate routing.
- Current task: `IGN93-003`.
- Exact next action: Independently audit the bounded remediation under `ai-context-auditor`, reconcile `ASM-20260804-003#AIC-001`, then run final validation and create the #93 pull request.
- Validation already completed: Refreshed `origin/main`; checked all local and remote refs for `ASM-20260804-*`; indexed the repository; read Issue #93; reproduced the current behavior; then passed package/apply GWT (29, one Windows symlink privilege skip), critical-gate routing GWT (31), semantic lifecycle GWT (7), full package compatibility GWT (29, one external-downstream skip), and `git diff --check`.
- Git state: remediation and workflow artifacts are ready for a first durable stage commit.
- Branch history and checkpoint handoffs: segment 1 began from `origin/main@4e7b5e0d59be831453b5c34f5f1eb3a1daae1245`; no push or merge checkpoint.
- Blockers or unresolved decisions: none. Issue #93 acceptance authorizes fail-closed behavior and explicit owner dispositions without an additional design decision.
