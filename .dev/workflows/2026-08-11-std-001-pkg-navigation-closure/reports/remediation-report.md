# Selected-Payload Navigation And Component Closure Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-11-std-001-pkg-navigation-closure`
- `workflow_id`: `2026-08-11-std-001-pkg-navigation-closure`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-08-11T21:47:55+08:00`
- `updated_at`: `2026-08-11T22:45:54+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: `ASM-20260811-003`
- `verification_assessment`: `ASM-20260811-006`

## Remediation Summary

- Authorized scope: Implement GitHub Issue #193 for `PKG-001` and `CMP-001` against the validation-only combined #191/#192 subject.
- Completed scope: fail-closed selected-payload navigation, anchors, actionable commands, excluded-lifecycle references, component selection/dependency/capability closure, portable guidance repair, Code Reviewer dotnet ownership, archive/apply parity, and the owner-directed v0.6.0 bounded upgrade-test horizon.
- Validation summary: implementation `ff80d590` passed the focused, packaging, apply, routing, aggregate, and governance suites; independent `ASM-20260811-006` found no new blocking finding.
- Closure decision: `local-source-scope-complete`

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| `ASM-20260811-003#PKG-001` | HIGH | `addressed` | package validator/schema, portable guidance, focused fixtures | 628-file fixed-commit payload plus ZIP/tar/apply validation | `ff80d590` | real governed v0.13 candidate must repeat the contract |
| `ASM-20260811-003#CMP-001` | MEDIUM | `addressed` | dotnet profile, capability ownership/availability metadata, selection fixtures | all 22 Code Reviewer paths dotnet-owned; core-only unavailable; dotnet-selected closed | `ff80d590` | future optional capabilities need explicit selection matrices |

## Changes And Evidence

- Package schema `2.2.0` requires a selected-payload user-view contract and reuses one validator during build and archive validation.
- The validator covers local links and directory targets, GitHub-style anchors, actionable local command targets, excluded lifecycle references, component selections, dependency closure, capability ownership, and declared availability.
- The exact committed projection contains 628 files across software-development core 322, AI-context lifecycle core 110, dotnet-backend 194, and repo-backlog 2.
- All 22 Code Reviewer capability paths now belong to `dotnet-backend`; core-only explicitly marks the capability unavailable and dotnet-selected marks it available.
- Active upgrade testing begins at v0.6.0. Each later governed package has one immediate-predecessor automatic route; a breaking release establishes a predecessor-only migration checkpoint. Pre-v0.6 matrix fixtures remain readable history outside routine discovery.
- Legacy package schemas retain read compatibility; source release records were not rewritten.

## Verification Assessment Reconciliation

- Independent auditor: `ai-context-auditor`, fixed subject `ff80d590`.
- Confirmed addressed: `ASM-20260811-003#PKG-001`, `ASM-20260811-003#CMP-001`.
- Recurring findings: none.
- New or regressed findings: none blocking; package and fast-profile duration remain non-blocking optimization opportunities.

## Deferred Work

| Item | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| Real governed v0.13 candidate review | No canonical v0.13 release record or separately authorized release lifecycle exists | repository owner / future release workflow | Build and read back the real candidate only after release authority exists; never substitute the controlled projection |

## Closure Evidence

- Required validations: selected-payload 6/6; version governance 23/23; packaging 36/36; focused archive/metadata/apply 3/3; package apply 30/30 outside sandbox with one uncounted symlink-privilege skip; routing 8/8; exact Git Bash fast profile 34/34 required with one not-applicable; repository validators passed.
- Preserved failure/advisory receipts: a first generic `bash` invocation resolved to WSL and timed out after 304.1 seconds; the exact Git Bash run later passed in 99 seconds but exceeded the 30-second advisory budget. Sandboxed ACL blocks were not counted as passes.
- Commit status: implementation `ff80d590`; independent assessment `cef711a`; containing workflow closeout commit is local only.
- Workflow/task status: completed for the authorized local source scope.
- Final next action: owner review. Project allocation, push, PR, merge, Issue closure, real v0.13 candidate, tag, Release, and publication remain separately gated.
