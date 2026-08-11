# Code Review File-Type And Finding-Scoped References Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-11-std-001-r2-review-routing`
- `workflow_id`: `2026-08-11-std-001-r2-review-routing`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-11T20:20:48+08:00`
- `updated_at`: `2026-08-11T20:20:48+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260811-003`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Implement GitHub Issue #191 for `CRL-001` and `CRL-002` as one bounded Code Reviewer routing delivery.
- Completed scope: pending.
- Validation summary: pending.
- Closure decision: `not-ready`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#CRL-001` | HIGH | `not-addressed` | pending | pending | pending | broad unconditional reference loading |
| `ASM-20260811-003#CRL-002` | HIGH | `not-addressed` | pending | pending | pending | duplicated semantic projections can drift |

## Changes And Evidence

### `ASM-20260811-003#CRL-001`

- Changes: pending.
- Evidence: pending.
- Validation: pending.
- Remaining risk: pending.

### `ASM-20260811-003#CRL-002`

- Changes: pending.
- Evidence: pending.
- Validation: pending.
- Remaining risk: pending.

## Verification Assessment Reconciliation

- Independent auditor: pending.
- Confirmed resolved: none yet.
- Recurring findings: pending.
- New or regressed findings: pending.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `ASM-20260811-003#GTM-001` | owned by #192 | separate successor workflow | execute after #191 |
| `ASM-20260811-003#PKG-001`, `CMP-001` | owned by #193 | separate successor workflow | execute after #192 |

## Closure Evidence

- Required validations: pending.
- Commit status: workflow bootstrap pending.
- Workflow/task status: remediation in progress.
- Final next action: inventory and remediate Code Reviewer routing.
