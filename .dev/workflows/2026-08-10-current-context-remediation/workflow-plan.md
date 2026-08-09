# Current Governance State And Active Context Remediation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-10-current-context-remediation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-10-current-context-remediation`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-08-10-current-context-remediation`
- `created_at`: `2026-08-10T00:33:41+08:00`
- `updated_at`: `2026-08-10T01:10:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: `ASM-20260809-004#DEV-001` and `#DEV-002` show current roadmap/provider/link drift, while Issue #178 confirms active and distributed ez-series/uContract branding no longer represents the intended .NET capability boundary.
- Authorized remediation scope: Deliver Issues #175 and #178 Phase A together; align current work-management projections, repair active links, remove or neutralize active/distributed ez-series and uContract names, preserve neutral engineering contracts and conditional .NET provider choices, and obtain independent post-remediation verification.
- Exclusions: Do not modify immutable assessments, completed workflows, releases, tags, package publication state, downstream target truth, or EngineeringGuardrails prerelease adoption. Do not create, edit, or propose course acknowledgement text; that content is exclusively owner-authored.
- Completion criteria: Current roadmap/backlog/provider projections and active links agree with their authorities; active/distributed ez-series and uContract scans are zero; neutral DDD/SbE/BDD/DbC/CQRS/Event-Sourcing/outbox/MQ/DI guidance remains usable; native validators and package projection checks pass; an independent audit reconciles the baseline findings.

## Authorization And Delivery

- Work items: `#175`, `#178`; bounded addendum: the commit-title alternative clarification requested under `#176`.
- Authorization: Owner message on 2026-08-10: `開始 #175＋#178 Phase A，並行處理 #176`.
- Delivery cohesion: #175 and #178 share active guide files, governance ownership, package projection checks, review, and rollback, so they use one workflow and pull request.
- #176 boundary: This workflow includes only the independently authorized commit-title grammar clarification. The layered immutable-history receipt/profile design remains in its separate workflow and requires owner decisions 1–4.
- Planned topology: merge commit, because multiple meaningful remediation and independent-verification stages form one review and rollback boundary. Integration remains owner-controlled.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260809-004/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-10-current-context-remediation/reports/remediation-report.md`
- Verification assessment: `TBD by independent ai-context-auditor`
- Tasks: `.dev/workflows/2026-08-10-current-context-remediation/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260809-004#DEV-001` | medium | `ai-context-governance` | remediate | `GOV009-001` | provider read-back, backlog/source validators |
| `ASM-20260809-004#DEV-002` | low | `ai-context-governance` | remediate with #178 overlap | `CTX007-001`, `GOV009-001` | active-link validation and direct reference scan |
| `#178 Phase A` | owner-selected P1 | `ai-context-governance` | remediate | `CTX007-001` | deterministic branded-reference and package projection checks |

## Stages And Checkpoints

1. Freeze the #170/#171 assessment baseline and owner decisions. `completed`
2. Neutralize active/distributed ez-series and uContract guidance without removing .NET capability contracts. `completed`
3. Align current roadmap/backlog/provider truth and repair active links. `completed`
4. Run native, package, reference, and provider validation. `in progress`; worktree gates passed and committed-tree package proof is next.
5. Obtain an independent post-remediation audit and reconcile findings.
6. Commit verified closure evidence; push, pull request, and merge require their own authorization/state read-back.

## Resume Checkpoint

- Last completed action: Completed the #175/#178 worktree remediation, source-governance successor authorization, and focused validation.
- Current task: `VERIFY-001`
- Exact next action: Commit the remediation checkpoint, run HEAD package proof, and obtain an independent ai-context-auditor assessment.
- Validation already completed: AI-context, workflow, assessment, version, source-governance, provider, commit-policy, projection, example-manifest, language, wrapper, and adapter checks passed.
- Git state: Branch is based on `main` at `a2f6fe53f2f50d436e6be7e27eb4d7de1bc4c828`; bootstrap commit is `e6979439e68d3aa0731541f36bd555b5f45b9bda`; remediation checkpoint is pending.
- Branch history and checkpoint handoffs: Bootstrap committed locally; nothing pushed and no pull request or merge exists.
- Blockers or unresolved decisions: None for #175/#178 Phase A. `LightBDD` remains an owner-named candidate, not a selected provider. Course acknowledgement is owner-only and excluded. The separate #176 layered-validation workflow awaits owner decisions 1–4.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-10-current-context-remediation` | `main` | active | `e6979439e68d3aa0731541f36bd555b5f45b9bda` | local | `2026-08-10T01:10:00+08:00` | Authorized cohesive #175/#178 delivery plus bounded #176 title clarification | Commit remediation checkpoint and continue `VERIFY-001` |
