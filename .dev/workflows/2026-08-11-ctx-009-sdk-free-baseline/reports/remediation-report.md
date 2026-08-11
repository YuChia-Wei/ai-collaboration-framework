# v0.13 SDK-Free Framework Baseline Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-11-ctx-009-sdk-free-baseline`
- `workflow_id`: `2026-08-11-ctx-009-sdk-free-baseline`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-11T09:03:09+08:00`
- `updated_at`: `2026-08-11T09:14:35+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260811-001`
- `verification_assessment`: `pending`

## Remediation Summary

- Authorized scope: Implement GitHub Issue #187 locally for v0.13.0 by removing framework-owned .NET SDK gates and compilable provider payload while preserving canonical engineering semantics as target-selected reference guidance.
- Completed scope: Required validation and CI selection is Python-only; the bundled provider and root analyzer tests are retired; the SDK seed is removed; source includes are reference-only; on-demand analyzer and projection-test recipes preserve the target-owned adoption path.
- Validation summary: Focused workflow, registry, source-include, shell-asset, dependency, SDK-free, fail-closed, repository-configuration, example, profile, document, source-disposition, and repository-identity contracts pass. Terminal no-`dotnet`, package-projection, full aggregate, and independent verification evidence remain pending.
- Closure decision: `not-ready`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260811-001#SDKGATE-001` | high | `partially-resolved` | `.ai/scripts/check-all.sh`, `.ai/scripts/validation-profile-registry.sh`, `.github/workflows/portable-gates.yml` | focused registry and workflow contracts pass | pending | controlled no-`dotnet` aggregate run pending |
| `ASM-20260811-001#SDKPAYLOAD-001` | high | `partially-resolved` | `.ai/assets/tech-stacks/dotnet-backend/tooling/**`, `.ai/distribution/profiles/dotnet-backend.yaml`, `global.json`, `tools/**` | SDK-free inventory 5/5 passed; dependency validator reports zero managed projects | pending | committed package projection validation pending |
| `ASM-20260811-001#SDKEVID-001` | high | `resolved` | `.ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml`, `.ai/scripts/validate-ai-context.py` | 4 source-include evidence tests pass | pending | target compatibility remains target-owned by design |
| `ASM-20260811-001#SDKPROV-001` | high | `partially-resolved` | `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/**` | recipe and diagnostic-mapping assertions pass | pending | package projection validation pending after commit |
| `ASM-20260811-001#SDKDOC-001` | medium | `partially-resolved` | root and dotnet-backend README files, active standards, guides, scripts README, release runbook | AI-context, workflow, and focused contract validation in progress | pending | independent active-reference audit pending |

## Changes And Evidence

### `ASM-20260811-001#SDKGATE-001`

- Changes: Removed all required `dotnet test` and provider-activation checks from the profile registry and aggregate runner, introduced a required Python SDK-free contract, and removed hosted .NET setup from the portable PR workflow.
- Evidence: The required check registry selects `sdk-free-framework-contract` for `fast`, `pr`, `release`, and `nightly-full`; portable gates contain no `setup-dotnet` step.
- Validation: Registry contract 6/6 passed outside the sandbox after the sandboxed Git Bash signal-pipe failure; GitHub workflow contract 9/9 passed.
- Remaining risk: The full PR profile still requires controlled execution with `dotnet` absent from `PATH`.

### `ASM-20260811-001#SDKPAYLOAD-001`

- Changes: Removed the bundled provider implementation, controlled fixture, root SDK pin, and framework-owned test projects; removed the downstream SDK seed and changed packaging assertions to reject compilable .NET artifacts.
- Evidence: Staged changes remove the canonical provider project tree and `global.json`; the distribution profile contains no SDK seed.
- Validation: SDK-free contract 5/5 passed; `git ls-files` returns no `.csproj`, `.sln`, `.slnx`, or `global.json`; the dependency validator reports `managed_projects=0` and `nuget_dependencies=0`.
- Remaining risk: Committed package projection validation remains pending.

### `ASM-20260811-001#SDKEVID-001`

- Changes: Reclassified the domain source include as reference-only, removed build/test command claims, and made target validation responsibility explicit.
- Evidence: The manifest contains an empty framework command set and the validator rejects executable or build claims.
- Validation: Source-include evidence contract 4/4 passed outside the sandbox after the sandboxed Windows Temp ACL failure.
- Remaining risk: None inside the framework baseline; downstream compatibility evidence remains target-owned.

### `ASM-20260811-001#SDKPROV-001`

- Changes: Replaced provider identity, activation schemas, fixtures, source projects, and materialization language with a non-selecting on-demand recipe manifest, analyzer project recipe, severity snippet, diagnostic mapping, and projection-registration recipe.
- Evidence: The recipe declares `reference-only`, `not-selected`, no SDK, no provider activation, and explicit target ownership of dependencies, wiring, severity, tests, CI, compatibility, and evidence.
- Validation: Recipe-only and DBA1001-DBA1017 mapping assertions pass.
- Remaining risk: Independent audit and committed package projection remain pending.

### `ASM-20260811-001#SDKDOC-001`

- Changes: Reconciled repository entry docs, dotnet-backend indexes, active standards, spec-compliance templates, persistence guidance, dependency policy, scripts guidance, pull-request guidance, and publication prerequisites with the SDK-free boundary.
- Evidence: Active guidance distinguishes framework reference semantics from target-selected implementation and target-owned validation.
- Validation: AI-context validation and shell-asset validation pass; focused contract and link-sensitive package tests remain in the terminal matrix.
- Remaining risk: Independent auditor must confirm there is no active contradictory selection surface.

## Verification Assessment Reconciliation

- Independent auditor: `ai-context-auditor` via planned `ASM-20260811-002`.
- Confirmed resolved: pending.
- Recurring findings: pending.
- New or regressed findings: pending.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `#179` EngineeringGuardrails Contracts adoption | Explicitly outside Issue #187 and this workflow | repository owner / separate lifecycle | Plan and authorize independently |

## Closure Evidence

- Required validations: focused checks complete; package projection, full aggregate PR profile without `dotnet`, commit policy, and independent verification pending.
- Commit status: remediation changes are staged but uncommitted.
- Workflow/task status: `CTX009-002` in progress; `CTX009-003` pending.
- Final next action: Commit the remediation checkpoint, validate the committed package projection, and run the full PR profile with `dotnet` absent from `PATH`.
