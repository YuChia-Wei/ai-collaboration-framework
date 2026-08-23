# Retained-Origin Route Evidence Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-23-retained-origin-route-evidence`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-23-retained-origin-route-evidence`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-23-retained-origin-route-evidence`
- `created_at`: `2026-08-23T16:21:28+08:00`
- `updated_at`: `2026-08-23T17:33:48+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: GitHub Issue #237 records that the v0.14.0 retained-origin direct-edge proof can pass an archive whose embedded portable validator rejects its own package metadata.
- Authorized remediation scope: Independently reproduce the repository-owned failure; make edge proof execute and record the portable validation authority and result; fail closed on package metadata/validator disagreement and conflicting payload identity; protect the v0.6.0, v0.9.0, and v0.13.0 routes; preserve package-apply pre-mutation validation; provide a historical recovery recommendation.
- Exclusions: No external analysis folder; no downstream target mutation; no journal performance work; no public Release body changes; no retained-origin expansion/deprecation; no push, PR, merge, Issue/Project mutation, release allocation, tag, Release, or publication; no change to v0.14.0 tag, Release identity, or published asset bytes.
- Completion criteria: All Issue #237 acceptance criteria have repository-native evidence; focused route, package, and upgrade regressions pass; independent read-only verification is bound to the final immutable local commit; workflow and commits validate.

## Artifact Contract

- Authorization and baseline problem statement: live GitHub Issue #237 plus repository-owned reproduction evidence; no external assessment is imported.
- Remediation report: `.dev/workflows/2026-08-23-retained-origin-route-evidence/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/<verification-assessment-id>/assessment.yaml` if an independent retained assessment is required by the final review boundary.
- Tasks: `.dev/workflows/2026-08-23-retained-origin-route-evidence/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ISSUE-237#edge-proof-false-positive` | high | `ai-context-governance` | remediate | `UPG-005-S1`, `UPG-005-S2` | Self-inconsistent archive must fail edge proof. |
| `ISSUE-237#payload-identity-conflict` | high | `ai-context-governance` | remediate | `UPG-005-S2` | Same package/release identity with different payload fingerprint must fail closed unless explicit distinct identity validates. |
| `ISSUE-237#retained-route-regression` | high | `ai-context-governance` | remediate | `UPG-005-S2`, `UPG-005-S3` | v0.6.0, v0.9.0, and v0.13.0 routes and package-apply pre-mutation gate remain covered. |
| `ISSUE-237#historical-recovery` | medium | repository owner | recommend without mutation | `UPG-005-S3` | Evidence-backed options preserve immutable v0.14.0 bytes and defer release allocation. |

## Stages And Checkpoints

1. Reproduce and freeze repository-owned edge, archive, identity, and live-provider evidence.
2. Implement the smallest fail-closed proof and identity contract with focused regression fixtures.
3. Validate all retained-origin routes and preserve package-apply pre-mutation behavior.
4. Bind read-only review to a clean immutable local commit and reconcile findings.
5. Complete workflow records and durable local commits without transport or release mutation.

## Resume Checkpoint

- Last completed action: Third exact-head audit accepted `bf9dbd11021846a88d421a96af89fa19ddf2b7d7` with P0=0/P1=0/P2=0/P3=0; owner selected historical recovery option A.
- Current task: none; `UPG-005-S1`, `UPG-005-S2`, and `UPG-005-S3` are completed.
- Exact next action: None in this workflow. Release management may later batch the prospective schema-1.1/v2 package into an owner-selected release without rewriting v0.14.0 history.
- Validation already completed: route 30/30, packaging 1/1, package-apply 2/2, release-state 36/36, production-path multi-hop 1/1, workflow artifacts 91/91, three-commit policy validation 3/3, AST syntax and diff checks, and accepted third exact-head audit.
- Git state: Durable implementation commits are `6c3e1e2c`, `04fe7875`, and accepted audited head `bf9dbd11`; this final workflow closeout metadata is pending one local commit.
- Branch history and checkpoint handoffs: Segment 1 only; no push or merge.
- Blockers or unresolved decisions: None in Issue #237. Owner selected option A: historical v0.14.0 source matrix and receipt bytes remain unchanged and non-passing; version allocation remains outside this workflow.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-23-retained-origin-route-evidence` | `main` | local workflow start | `412bb14a16fe75ee65a020b16680def0acc0ff1b` | local worktree | `2026-08-23T16:21:28+08:00` | Authorized Issue #237 implementation | Continue `UPG-005-S1` on this branch. |
