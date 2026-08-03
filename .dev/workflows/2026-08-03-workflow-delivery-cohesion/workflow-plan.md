# Workflow Delivery Cohesion And Linear Merge Rules

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-03-workflow-delivery-cohesion`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-03-workflow-delivery-cohesion`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-08-03-workflow-delivery-cohesion`
- `created_at`: `2026-08-03T23:47:10+08:00`
- `updated_at`: `2026-08-03T23:59:37+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: workflow and Git decisions currently over-weight broad trigger lists, Issue count, and a default non-fast-forward rule. This can create one small workflow per Issue even when the team intends one branch and pull request, and can retain merge commits for changes whose review risk does not require grouped topology.
- Authorized remediation scope: implement the owner-selected `STD-001` round-one outcome, bind it to GitHub Issue #86 / `GOV-004`, update workflow and Git policy, add representative validation, and retain baseline plus post-change verification.
- Exclusions: no direct-push permission for ordinary README history changes; no inferred successor version; no provider state as authorization; no rewrite of historical workflow records or merged Git history.
- Completion criteria: workflow-value, delivery-cohesion, and integration-topology rules are canonical and portable; representative cases are validated; `GOV-004` is a required gate for the next owner-allocated successor release; an independent verification assessment has no unresolved finding in scope.

## Authorization Record

- The owner explicitly authorized persistence, a new Issue, related documentation corrections, and inclusion in the next release gate on 2026-08-03.
- The owner selected linear integration for this delivery. This is a positive topology selection, not an exception request.
- The baseline, remediation, and verification commits are self-describing and share one outcome, reviewer boundary, validation path, and rollback posture. No checkpoint, handoff, release, or external-host boundary gives an extra merge node independent value, so the selected linear topology remains coherent despite multiple stage commits.
- Issue #86 records the approved outcome. GitHub provider state remains a projection and did not authorize execution.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260803-004/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-03-workflow-delivery-cohesion/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260803-005/assessment.yaml`
- Tasks: `.dev/workflows/2026-08-03-workflow-delivery-cohesion/tasks/`

## Delivery Cohesion Decision

- One GitHub Issue, one workflow, one branch, and one integration path own this change.
- The two tasks below are independent normative outcomes, not one task per discussion topic or per Issue.
- Generic validation, evidence formatting, provider read-back, and workflow closeout are lifecycle steps and do not count as extra delivery tasks.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260803-004#WFG-001` | HIGH | `ai-context-governance` | remediate | `GOV004-001` | policy fixtures and repository context validators |
| `ASM-20260803-004#WFG-002` | HIGH | `ai-context-governance` | remediate | `GOV004-001` | multi-Issue delivery-cohesion fixtures |
| `ASM-20260803-004#WFG-003` | MEDIUM | `ai-context-governance` | remediate | `GOV004-002` | merge-topology fixtures and policy consistency checks |

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `GOV004-001` | Define workflow value, low-task review signals, and many-Issue-to-one-delivery cohesion. | `completed` |
| `GOV004-002` | Define normal linear and merge-commit topology rules and register the next-release gate. | `in_progress` (policy complete; verification and linear integration pending) |

## Stages And Checkpoints

1. Baseline audit and evidence freeze.
2. Workflow-value and delivery-cohesion policy remediation.
3. Linear integration and successor-release gate remediation.
4. Deterministic validation and independent post-remediation audit.
5. Linear pull-request integration and provider/main read-back.

## Resume Checkpoint

- Last completed action: implemented both normative tasks and passed focused policy, governance-workflow, AI-context, workflow, language, wrapper, backlog, and orchestrator acceptance validation.
- Current task: independent `ai-context-auditor` verification.
- Exact next action: create `ASM-20260803-005`, reconcile the remediation report, and prepare linear integration.
- Validation already completed: live GitHub PR inventory; workflow artifact inventory; CTX-002 historical commit inspection; six workflow-delivery policy cases; seven governance-workflow cases; three orchestrator acceptance cases; ten language/parity cases; sixteen wrapper cases; AI-context, workflow, backlog, and diff checks.
- Git state: workflow branch created from clean `main@80b013803ee29ca2f4dd458a393eb1da451212e1`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: successor release identity remains intentionally unassigned; this does not block defining its activation gate.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-03-workflow-delivery-cohesion` | `main@80b013803ee29ca2f4dd458a393eb1da451212e1` | active | pending | Issue #86 / future PR to `main` | `2026-08-03T23:59:37+08:00` | Implement one cohesive governance delivery with owner-selected linear topology. | Run independent verification, then open one PR. |
