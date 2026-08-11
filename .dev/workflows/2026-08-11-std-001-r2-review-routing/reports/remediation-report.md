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
- `updated_at`: `2026-08-11T20:42:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260811-003`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Implement GitHub Issue #191 for `CRL-001` and `CRL-002` as one bounded Code Reviewer routing delivery.
- Completed scope: canonical 14-route contract, route-first root/wrapper/skill guidance, selected-route role loads, compatibility stubs, engineering-rule ownership projection, negative/equivalence fixtures, and active fail-closed validation.
- Validation summary: focused and structural suites passed; full package matrix timed out at 244 seconds and remains failed. Commit-bound focused package projection and independent audit are pending.
- Closure decision: `not-ready`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#CRL-001` | HIGH | `remediated-awaiting-verification` | routing contract, entries, roles, compatibility paths, validator | focused 7/7 plus measured load reduction | pending | independent audit and commit-bound package view |
| `ASM-20260811-003#CRL-002` | HIGH | `remediated-awaiting-verification` | rule ownership, prompts/playbooks, negative fixtures | rule-ID/catalog parity and drift fixtures passed | pending | independent semantic verification |

## Changes And Evidence

### `ASM-20260811-003#CRL-001`

- Changes: added a single route contract with fourteen file-type routes; made root guidance, canonical skill, wrappers, and four review roles select routes before standards; replaced three broad checklist paths and the quick reference with bounded compatibility stubs for `v0.13.x`.
- Evidence: eager-load measurements fell from 43,747 to 24,005 bytes at top level, 65,017 to 36,557 general, 71,120 to 48,732 aggregate, 68,332 to 40,181 controller, and 68,497 to 35,334 reactor (31.5%-48.4% reduction).
- Validation: `test_code_reviewer_routing_contract.py` proves every declared route is below its baseline and no review role statically references the old shared bundle.
- Remaining risk: package selection is evaluated against committed Git blobs, so its focused check follows the implementation commit.

### `ASM-20260811-003#CRL-002`

- Changes: stable rule IDs are attached only to finding-scoped predicates; catalog/ownership projections cite the route contract; role prose no longer owns duplicated MUST-fail doctrine.
- Evidence: negative fixtures distinguish event-sourced and non-event-sourced aggregates, allow target-specific repository ports, and cover mapper/test rules. Aggregate prompts no longer hard-code Contract APIs or TODO doctrine.
- Validation: rule-ID/catalog consumer parity, fixture route/rule identity, role-execution acceptance, effective-rule action contract, wrapper/adapter contracts, and AI-context validation passed.
- Remaining risk: independent auditor reconciliation remains required before closure.

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

- Required validations: focused routing 7/7; role execution 6/6; adapter 31/31; wrapper 16/16; language/parity 10/10; profile 3/3; document 2/2; effective-rule 3/3; registry 6/6; shell assets and `validate-ai-context.py` passed. Full package matrix timed out at 244 seconds and is explicitly failed.
- Commit status: implementation snapshot pending commit.
- Workflow/task status: remediation implemented; verification in progress.
- Final next action: commit, run commit-bound focused package projection, and perform the independent assessment.
