# v0.13 SDK-Free Framework Baseline Verification

## Metadata

- `assessment_id`: `ASM-20260811-002`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-11`
- `created_at`: `2026-08-11T10:14:06+08:00`
- `updated_at`: `2026-08-11T10:14:06+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `codex/2026-08-11-ctx-009-sdk-free-baseline`
- `subject_commit`: `889493a272bc272086c70dedd1a57d3f91eb790d`
- `issue_ref`: `#187`
- `baseline_assessment`: `ASM-20260811-001`

## Executive Summary

- Overall assessment: `verified-ready-for-local-closeout`.
- All five `ASM-20260811-001` findings are addressed for the framework baseline. The committed tree contains no `.csproj`, `.sln`, `.slnx`, or root `global.json`; the default package rejects compilable .NET artifacts and no longer seeds an SDK.
- Required framework profiles select a Python SDK-free contract and no `dotnet` command. The hosted portable workflow neither installs an SDK nor watches SDK/project paths.
- The bundled provider, activation records, controlled fixture, and framework-owned .NET tests are retired. The replacement mechanical-validation surface is reference-only, not selected, and assigns project creation, dependencies, severity, wiring, tests, CI, compatibility, and evidence to the target owner.
- A controlled PR run with `dotnet` absent selected 37 checks and recorded 37 passed, 0 failed, and 0 blocked: 15 were executed and 22 reused by identical input fingerprint. Eighteen other registry entries were not selected and remain `not-applicable`, not passed.
- The final package matrix recorded 36 passed and 1 skipped. The skipped downstream integration case required `AI_CONTEXT_DOWNSTREAM_REPO`, which was not supplied; it is not counted as passed and does not weaken the source package assertions.
- No new blocking finding was identified. One packaged `compatibility`/`advisory` shell entry retains a frozen legacy project-name message; its manifest replacement points to target-owned analyzer/test evidence, it is not a required check command, and it does not reintroduce an SDK gate.

## Scope

### Included AI Context Surfaces

- Required check registry, aggregate runner, portable hosted workflow, fail-closed contracts, and no-`dotnet` execution evidence.
- Tracked project/SDK inventory, package payload and seed selectors, dependency validation, and source-include evidence.
- Mechanical-validation recipes, diagnostic mappings, semantic rule ownership, active indexes, standards, guides, and root entry documents.
- Source-governance classification of retained compatibility scripts.

### Default Exclusions

- Product implementation and target-repository tests.
- Downstream repository compatibility, unless separately supplied as external evidence.

### Additional Exclusions

- Issue #179 and `EngineeringGuardrails.Contracts.*`.
- Ignored local `bin`/`obj` output and immutable dated history.
- Push, pull request, merge, Issue closure, tag, Release, or publication mutation.

### Code Review Handoff

- Requested: `no`.
- This assessment verifies AI-context governance and distribution contracts, not product .NET code.

## Methodology And Evidence

### Independent Subject Read-Back

- Bound the audit to committed subject `889493a272bc272086c70dedd1a57d3f91eb790d` with a clean tracked worktree.
- Enumerated the committed Git tree for project and SDK artifacts instead of relying on ignored working-directory output.
- Read the current registry, runner, workflow, distribution, evidence, recipe, shell-asset, and guidance authorities.
- Re-ran the SDK-free, dependency, source-governance, and AI-context checks against the subject checkout.
- Read the controlled PR receipt `20260811T015321Z-768` and kept executed, reused, passed, and not-selected dispositions distinct.
- Reconciled the final package result with the earlier timeout and interim failures rather than overwriting those receipts.

### Delegation

- Sub-agents used during this independent verification pass: `no`.
- Earlier bounded inventories informed remediation planning but do not replace this subject read-back.

### Evidence Authority

| Evidence | Authority | Limitation |
| --- | --- | --- |
| Git tree at `889493a` | Exact tracked source and deletion proof | Does not prove runtime selection alone |
| Registry, runner, and hosted workflow | Current required selection contract | Manual target commands remain outside framework ownership |
| Controlled PR receipt | Exact no-`dotnet` execution dispositions | Reused checks were not re-executed in the final invocation |
| Canonical packaging suite | Source package assertions | One external downstream integration case was unselected by environment |
| Recipe manifest and guidance | Current target-selection ownership | Does not prove any target has adopted or validated the recipe |

## Acceptance Reconciliation

| #187 / baseline criterion | Result | Evidence |
| --- | --- | --- |
| No active framework-owned project or root SDK pin | passed | Git tree contains zero `.csproj`, `.sln`, `.slnx`, and no root `global.json`; live dependency report has `managed_projects=0`. |
| Default payload has no compilable .NET project or SDK seed | passed | SDK-free and committed package projection contracts reject project suffixes, the retired provider path, and `global.json`. |
| Required profiles and hosted workflow do not install or invoke `dotnet` | passed | Registry/runner select the Python SDK-free contract; portable workflow has no `setup-dotnet`; controlled PR run passed with `dotnet` absent. |
| Analyzer/configuration validation is target-selected | passed | On-demand recipe is `reference-only` and `not-selected`, with target ownership of SDK, packages, wiring, severity, tests, CI, compatibility, and evidence. |
| Retained mappings/snippets do not claim activation | passed | DBA1001-DBA1017 remain enforcement labels attached to canonical semantics; no provider activation schema, evaluator, fixture, or executable provider remains. |
| Source-include evidence is not overstated | passed | Domain include is reference-only with no framework build/test command and explicit target compatibility ownership. |
| Canonical engineering semantics remain valid | passed | Engineering-rule catalog, owned-rule validation, document projection, and AI-context validation pass after provider retirement. |
| Independent verification distinguishes failures/skips/reuse from pass | passed | Earlier timeout and failures are preserved; final 15 executed/22 reused and package 1 skipped are reported explicitly. |

## Findings

No new blocking finding.

### Baseline Finding Reconciliation

| Finding | Baseline severity | Verification status | Evidence | Residual |
| --- | --- | --- | --- | --- |
| `ASM-20260811-001#SDKGATE-001` | HIGH | `addressed` | Required commands are SDK-free; controlled no-`dotnet` PR receipt has 37 selected checks passed, 0 failed, 0 blocked. | Hosted PR checks remain a later integration gate. |
| `ASM-20260811-001#SDKPAYLOAD-001` | HIGH | `addressed` | Zero tracked .NET projects/root SDK pin; no SDK seed; package project rejection and focused projections pass. | External downstream integration was not selected. |
| `ASM-20260811-001#SDKEVID-001` | HIGH | `addressed` | Source include is reference-only and its 4/4 structural contract passes. | Target compatibility evidence remains target-owned by design. |
| `ASM-20260811-001#SDKPROV-001` | HIGH | `addressed` | Bundled implementation/activation surface removed; target-owned on-demand recipe and diagnostic mapping retained. | No target activation or compatibility claim is made. |
| `ASM-20260811-001#SDKDOC-001` | MEDIUM | `addressed` | Authoritative docs, indexes, tests, registry, and package guidance align with the SDK-free boundary; AI-context and source governance pass. | Frozen advisory compatibility output retains one legacy project name, classified below. |

### Observed Non-Blocking Limitation

`.ai/scripts/code-review.sh` remains a packaged compatibility entrypoint and contains the legacy message `Run DotnetBackendValidation tests`. The shell-asset manifest classifies the file as `lifecycle: compatibility`, `authority: advisory`, supplies a target-owned analyzer/test replacement, and does not list it under `check_all_required_commands`. Source governance binds this file to immutable v0.5 candidate bytes and currently permits only the separately authorized Issue #178 drift set. The message is therefore retained transparently rather than silently changing an unrelated authorization contract. It is not evidence of a selected project, executable provider, or required SDK gate.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Tracked SDK/project inventory | passed | 0 `.csproj`, 0 `.sln`, 0 `.slnx`, no root `global.json` at the subject commit. |
| SDK-free framework contract | passed | 5/5 cases. |
| Dependency/version live check | passed | `source_mode=true`, 1 Python dependency, 0 managed projects, 0 NuGet dependencies. |
| Required profile registry | passed | 6/6 focused cases; no required framework `dotnet` selection. |
| Hosted workflow contract | passed | 9/9 focused cases; no SDK setup or project/SDK trigger. |
| Fail-closed aggregate contract | passed | 38/38 cases after controlled environment rerun. |
| Source-include evidence | passed | 4/4 cases; no executable/build claim. |
| Source governance | passed | 1 manifest, 1 repository identity policy, and 1 source disposition contract. |
| AI context | passed | 27 indexes, 17 skills, 380 language-policy files, 13 rules, 35 manifests, 10 mappings, 2 lessons. |
| Focused package projections | passed | 2/2 committed component-matrix and repository-seed cases. |
| Canonical package matrix | passed with explicit skip | 36 passed, 1 skipped in 890.131 seconds; downstream integration skip is not counted as pass. |
| Controlled PR profile without `dotnet` | passed | 37 selected checks passed: 15 executed, 22 fingerprint-reused; 18 unselected registry entries were `not-applicable`; 0 failed, 0 blocked. |
| Current source re-read | passed | SDK-free 5/5, dependency live check, source governance, and AI-context validator rerun during verification. |

### Preserved Failed And Interim Receipts

- The first canonical package attempt timed out at 364 seconds. Timeout remains failure evidence.
- The measured interim package run recorded 34 passed, 2 failed, and 1 skipped. The two failures were stale permission expectations for already-governed `issues: read`; the focused corrected cases passed 2/2 and the final full matrix passed its 36 selected cases.
- The first controlled no-`dotnet` PR run executed 37 selected checks and recorded 35 passed plus 2 failed from one source-governance byte drift. Restoring the immutable compatibility byte produced the final clean receipt.

### Environment-Limited Checks

- `test_gwt_031_given_real_downstream_when_installed_then_full_validation_passes` was skipped because `AI_CONTEXT_DOWNSTREAM_REPO` was not set. It is external target integration evidence, not a source SDK-free prerequisite, and is not represented as passed.
- Ignored local `tools/**/bin` and `tools/**/obj` outputs were not removed or used as tracked/package evidence.

## Recommended Action Order

1. Close the local `2026-08-11-ctx-009-sdk-free-baseline` workflow with this verification reference.
2. Validate the final assessment/workflow commit range and confirm a clean tracked worktree.
3. Only after separate owner authorization, push the branch and open a pull request for hosted validation.
4. Close Issue #187 only after integration read-back; keep v0.13.0 publication separate.

## Deferred Items

- Issue #179 and any `EngineeringGuardrails.Contracts` adoption or publication.
- Any future framework-provided analyzer package, contract assembly, `dotnet tool`, or compiled CLI.
- Target-specific analyzer/configuration project implementation and compatibility evidence.
- Push, pull request, merge, Issue closure, tag, Release, and v0.13.0 publication.

## Appendix

### Commands And Receipts Reviewed

```text
git ls-tree -r --name-only 889493a
python .ai/scripts/tests/test_sdk_free_framework_contract.py -v
python .ai/scripts/validate-dependency-versions.py
python .ai/scripts/validate-source-governance.py
python .ai/scripts/validate-ai-context.py
python .ai/scripts/tests/test_ai_context_packaging.py -v
bash .ai/scripts/check-all.sh --profile pr  # controlled PATH: dotnet absent
artifacts/validation/20260811T014708Z-1303  # preserved initial failure
artifacts/validation/20260811T015321Z-768   # final clean receipt
```

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260811-002/report.md`
- Verified findings: all five `ASM-20260811-001` findings
- Owning workflow: `2026-08-11-ctx-009-sdk-free-baseline`
- Remediation performed by this verification pass: `no`
- Local closeout readiness: `yes`
- Remote transport or integration authorized: `no`
