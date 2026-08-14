# CLI Execution Routing Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-14-environment-execution-routing`
- `workflow_id`: `2026-08-14-environment-execution-routing`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-14T21:58:42+08:00`
- `updated_at`: `2026-08-14T22:22:26+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `not-applicable; GitHub Issue #210 is the approved baseline`
- `verification_assessment`: `pending owner review`

## Remediation Summary

- Authorized scope: implement GitHub Issue #210 as a CLI-only local routing contract while keeping personal CLI values Git-ignored and requiring post-recovery consent before a local write.
- Completed scope: portable CLI contract and schema, exact ignore boundary, source and target validation, agent behavior, init/upgrader preservation rules, package exclusion, indexes, wrappers, and guides. Connector, CI, external-task, browser, and delegation routing are explicitly excluded.
- Validation summary: narrowed CLI-only routing GWT tests pass 9/9 on Windows and immutable Ubuntu-24.04, including non-CLI surface rejection; wrapper 16/16, language 10/10, and Python entrypoint 4/4 suites pass; committed package lifecycle projection 1/1, source AI-context validation, workflow validation, and whitespace checks pass.
- Closure decision: `not-ready`; owner review and independent verification remain.

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `Issue-210-contract` | high | `resolved` | shared CLI contract, schema, indexes | CLI-only routing GWT and source validator | `f7529ee` | Versioned migration is required for a future incompatible schema. |
| `Issue-210-local-persistence` | high | `resolved` | `.gitignore`, validators, root agent guidance | ignore, tracked, consent, sensitive-field, retry tests | `f7529ee` | No personal binding exists without a separate owner decision. |
| `Issue-210-downstream` | high | `resolved` | package profile, target validator, init/upgrader, wrappers, guides | package projection, Windows, immutable WSL | `f7529ee` | No downstream target repository has adopted the standard yet. |
| `Issue-210-verification` | high | `not-addressed` | none | independent audit intentionally deferred | pending | Owner adjustments must precede independent verification. |

## Changes And Evidence

### `Issue-210-contract`

- Changes: defined authority order, portable route vocabulary, readiness versus execution evidence, bounded fallback, retry, consent, and fail-closed behavior.
- Evidence: `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md` and `.ai/assets/shared/cli-execution-routing.schema.yaml` contain no populated personal route or non-CLI selector.
- Validation: source AI-context validator passed; the CLI-only routing suite covers the unconfigured source state and rejects connector surface/selector input.
- Remaining risk: owner review may adjust vocabulary or record shape before independent verification.

### `Issue-210-local-persistence`

- Changes: reserved `.dev/ai-context/local/cli-execution-routing.yaml` under the tracked `/.dev/ai-context/local/` ignore rule and implemented deterministic validation.
- Evidence: validation rejects missing ignore coverage, tracked or staged bindings, symlink boundaries, implicit consent, sensitive fields, invalid fallback, and repeated attempts.
- Validation: Windows CLI routing suite passed 9/9 outside the sandbox after the sandbox blocked the Python Temp fixture.
- Remaining risk: local persistence is intentionally not exercised because no owner approval has been given to create the personal file.

### `Issue-210-downstream`

- Changes: init creates only the tracked ignore boundary; upgrader preserves ignored local state without reading or migrating it; target validation consumes the shared validator; package rules include portable assets and exclude local state and test fixtures.
- Evidence: wrapper metadata, language policy, Python entrypoint, source validator, and Ubuntu-24.04 routing tests pass.
- Validation: the lifecycle component projection passed 1/1 against immutable commit `f7529ee`; Ubuntu-24.04 passed the CLI routing suite 9/9 against the same commit.
- Remaining risk: no downstream target repository has adopted the standard yet.

## Verification Assessment Reconciliation

- Independent auditor: pending owner review.
- Confirmed resolved: pending.
- Recurring findings: pending.
- New or regressed findings: pending.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| Personal local binding | Requires a separate disclosed consent decision after a stable successful route | repository owner | Review the proposed path and fields; approve, adjust, or decline. |
| Independent post-remediation audit | Owner requested to inspect and adjust the result shape first | `ai-context-auditor` | Run only after owner review. |
| Push, PR, merge, Issue closure, release | Not authorized | repository owner | Decide separately. |

## Closure Evidence

- Required validations: owner review and independent verification remain.
- Commit status: local CLI-only scope-correction checkpoint `f7529ee` is validated and unpushed.
- Workflow/task status: `ENVROUTE-001` and `ENVROUTE-002` completed; `ENVROUTE-003` remains active for owner review; `VERIFY-001` pending.
- Final next action: present the result shape without creating personal local state; apply owner adjustments or proceed to independent verification only after the owner decides.
