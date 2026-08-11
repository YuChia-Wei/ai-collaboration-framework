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
- `status`: `final`
- `created_at`: `2026-08-11T09:03:09+08:00`
- `updated_at`: `2026-08-11T10:16:43+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260811-001`
- `verification_assessment`: `ASM-20260811-002`

## Remediation Summary

- Authorized scope: Implement GitHub Issue #187 locally for v0.13.0 by removing framework-owned .NET SDK gates and compilable provider payload while preserving canonical engineering semantics as target-selected reference guidance.
- Completed scope: Required validation and CI selection is Python-only; the bundled provider and root analyzer tests are retired; the SDK seed is removed; source includes are reference-only; on-demand analyzer and projection-test recipes preserve the target-owned adoption path.
- Validation summary: Focused workflow, registry, source-include, shell-asset, dependency, SDK-free, fail-closed, repository-configuration, example, profile, document, source-disposition, repository-identity, and committed payload/seed projection contracts pass. The initial 364-second package timeout and interim 34-pass/2-fail/1-skip result remain preserved; after correcting the two stale permission expectations, the final full package matrix recorded 36 passed and 1 external-downstream skip in 890.131 seconds. The first controlled no-`dotnet` PR run preserved 35 passes and 2 source-governance failures; after restoring the immutable compatibility byte, the final receipt recorded 37 selected checks passed with 15 executed and 22 fingerprint-reused, 18 unselected entries not-applicable, 0 failed, and 0 blocked. `ASM-20260811-002` independently verified all five baseline findings as addressed.
- Closure decision: `ready-for-local-closeout`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260811-001#SDKGATE-001` | high | `resolved` | `.ai/scripts/check-all.sh`, `.ai/scripts/validation-profile-registry.sh`, `.github/workflows/portable-gates.yml` | focused contracts and controlled no-`dotnet` PR receipt pass | `4abb7f1`, `889493a` | hosted PR gate remains separate |
| `ASM-20260811-001#SDKPAYLOAD-001` | high | `resolved` | `.ai/assets/tech-stacks/dotnet-backend/tooling/**`, `.ai/distribution/profiles/dotnet-backend.yaml`, `global.json`, `tools/**` | SDK-free inventory 5/5, zero managed projects, and committed payload/seed projection pass | `4abb7f1` | none inside the default payload |
| `ASM-20260811-001#SDKEVID-001` | high | `resolved` | `.ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml`, `.ai/scripts/validate-ai-context.py` | 4 source-include evidence tests pass | `4abb7f1` | target compatibility remains target-owned by design |
| `ASM-20260811-001#SDKPROV-001` | high | `resolved` | `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/**` | recipe, diagnostic mapping, committed payload assertions, and independent audit pass | `4abb7f1` | no target activation or compatibility claim |
| `ASM-20260811-001#SDKDOC-001` | medium | `resolved` | root and dotnet-backend README files, active standards, guides, scripts README, release runbook, packaging permission contract | focused context contracts, final package matrix, source governance, clean aggregate, and independent active-reference audit pass | `4abb7f1`, `3fdd7a1`, `889493a` | one frozen compatibility/advisory message is non-authoritative and not a required command |

## Changes And Evidence

### `ASM-20260811-001#SDKGATE-001`

- Changes: Removed all required `dotnet test` and provider-activation checks from the profile registry and aggregate runner, introduced a required Python SDK-free contract, and removed hosted .NET setup from the portable PR workflow.
- Evidence: The required check registry selects `sdk-free-framework-contract` for `fast`, `pr`, `release`, and `nightly-full`; portable gates contain no `setup-dotnet` step.
- Validation: Registry contract 6/6 passed outside the sandbox after the sandboxed Git Bash signal-pipe failure; GitHub workflow contract 9/9 passed.
- Remaining risk: Hosted PR execution remains an integration gate after push/PR authorization; the local no-`dotnet` requirement is satisfied.

### `ASM-20260811-001#SDKPAYLOAD-001`

- Changes: Removed the bundled provider implementation, controlled fixture, root SDK pin, and framework-owned test projects; removed the downstream SDK seed and changed packaging assertions to reject compilable .NET artifacts.
- Evidence: Commit `4abb7f1` removes the canonical provider project tree and `global.json`; the distribution profile contains no SDK seed.
- Validation: SDK-free contract 5/5 passed; `git ls-files` returns no `.csproj`, `.sln`, `.slnx`, or `global.json`; the dependency validator reports `managed_projects=0` and `nuget_dependencies=0`; committed component-matrix and repository-seed projections both pass.
- Remaining risk: None inside the default payload; ignored local `bin`/`obj` output is not tracked or packaged.

### `ASM-20260811-001#SDKEVID-001`

- Changes: Reclassified the domain source include as reference-only, removed build/test command claims, and made target validation responsibility explicit.
- Evidence: The manifest contains an empty framework command set and the validator rejects executable or build claims.
- Validation: Source-include evidence contract 4/4 passed outside the sandbox after the sandboxed Windows Temp ACL failure.
- Remaining risk: None inside the framework baseline; downstream compatibility evidence remains target-owned.

### `ASM-20260811-001#SDKPROV-001`

- Changes: Replaced provider identity, activation schemas, fixtures, source projects, and materialization language with a non-selecting on-demand recipe manifest, analyzer project recipe, severity snippet, diagnostic mapping, and projection-registration recipe.
- Evidence: The recipe declares `reference-only`, `not-selected`, no SDK, no provider activation, and explicit target ownership of dependencies, wiring, severity, tests, CI, compatibility, and evidence.
- Validation: Recipe-only and DBA1001-DBA1017 mapping assertions pass.
- Remaining risk: No target activation or compatibility claim is made; target evidence remains target-owned.

### `ASM-20260811-001#SDKDOC-001`

- Changes: Reconciled repository entry docs, dotnet-backend indexes, active standards, spec-compliance templates, persistence guidance, dependency policy, scripts guidance, pull-request guidance, and publication prerequisites with the SDK-free boundary.
- Evidence: Active guidance distinguishes framework reference semantics from target-selected implementation and target-owned validation.
- Validation: AI-context and shell-asset validation pass. The earlier 364-second timeout and interim 34-pass/2-fail/1-skip package receipt remain visible; the two corrected permission cases passed 2/2 and the final full matrix recorded 36 passed plus 1 external-downstream skip. The first controlled no-`dotnet` run recorded 35 passes and 2 failures from one unauthorized `code-review.sh` byte drift; restoring the immutable candidate byte produced a final receipt with 37 selected checks passed, 15 executed, 22 reused, 0 failed, and 0 blocked. `ASM-20260811-002` found no contradictory required selection surface.
- Remaining risk: `code-review.sh` retains one frozen legacy project-name message, but its manifest authority is advisory/compatibility and its replacement is target-owned; it is not selected as a required command.

## Verification Assessment Reconciliation

- Independent auditor: `ai-context-auditor` via final `ASM-20260811-002` at subject commit `889493a272bc272086c70dedd1a57d3f91eb790d`.
- Confirmed resolved: `SDKGATE-001`, `SDKPAYLOAD-001`, `SDKEVID-001`, `SDKPROV-001`, and `SDKDOC-001`.
- Recurring findings: none on required or authoritative framework surfaces.
- New or regressed findings: none blocking; one transparent frozen advisory compatibility message is recorded as a non-blocking limitation.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| `#179` EngineeringGuardrails Contracts adoption | Explicitly outside Issue #187 and this workflow | repository owner / separate lifecycle | Plan and authorize independently |

## Closure Evidence

- Required validations: focused checks and committed projections pass; final package matrix records 36 passed and 1 explicit external-downstream skip; final controlled no-`dotnet` PR receipt records 37 selected checks passed, 15 executed, 22 reused, 18 unselected not-applicable, 0 failed, and 0 blocked; independent verification is final.
- Commit status: remediation `4abb7f1`; permission-contract follow-up `3fdd7a1`; immutable compatibility-byte restoration `889493a`; assessment and terminal workflow records are in the containing closeout commit.
- Workflow/task status: `CTX009-001`, `CTX009-002`, and `CTX009-003` completed; workflow locally completed.
- Final next action: Wait for separate owner authorization before push or pull-request creation. Merge, Issue closure, tag, and v0.13.0 publication remain later decisions.
