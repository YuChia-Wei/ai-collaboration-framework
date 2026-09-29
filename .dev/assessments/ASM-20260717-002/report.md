# v0.4.0 AI Context Final Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260717-002`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-17`
- `created_at`: `2026-07-17T07:28:50+08:00`
- `updated_at`: `2026-07-17T07:28:50+08:00`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `codex/2026-07-16-v0-4-0-ai-context-remediation`
- `subject_commit`: `36c0add48129eff6bfa503b2244a45c4a802b5c5`
- `artifact_branch`: `codex/assessment/asm-20260717-002`
- `previous_assessment`: [`ASM-20260717-001`](../ASM-20260717-001/report.md)
- `workflow_ref`: [`2026-07-16-v0-4-0-ai-context-remediation`](../../workflows/2026-07-16-v0-4-0-ai-context-remediation/workflow.yaml)

## Executive Summary

- Overall assessment: `ASM-20260717-001#SVF-001` is independently resolved and no substantive standards conflict remains.
- Overall score: **9.4/10**
- Decision: **remediation-recommended; closeout gate not yet composable**
- Primary strengths: active `.ai` profile projections use canonical names; validator coverage includes the routed shared root and rejects an injected stale name; focused and tool-owned tests pass; 32 workflow commits pass; history/tag/main invariants remain intact.
- Primary risk: the aggregate full gate fails only when its required closeout `COMMIT_RANGE` and `WORKFLOW_ID` variables are exported, because the nested synthetic runner inherits them and invalidates its own N/A-count fixture.

No source-of-truth content remediation remains from the preceding assessments. One bounded validator-harness fix is required before strict workflow closure.

## Scope

### Included AI Context Surfaces

- PROFILE-003 projections, routes, validator allowlist, negative behavior, workflow/assessment/release records, aggregate runner, shell lifecycle, tool-owned verification projects, and Git history.

### Default Exclusions

- `src/**`, product `tests/**`, product implementation trees, generated/dependency output.

### Additional Exclusions

- `docker-compose/**`, product code review, GitHub Release re-verification, v0.3.0 tag mutation, full Observability design, and downstream clean-room implementation.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and tests
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Enumerated active profile projections and inbound routes, inspected exact validator roots, injected a stale name in a temporary directory, and ran the composed closeout environment rather than assuming separate green checks compose.

### Pass B: Repository-Aware Skill Review

- Applied `ai-context-auditor`, evidence, assessment, workflow, shell-lifecycle, commit, and release contracts; reconciled `ASM-20260717-001#SVF-001` and `#SVF-002` against current files and execution output.

### Delegation

- Sub-agents used: `yes`, read-only
- Assigned surfaces: active profile projection truth and final release/governance gate composition.
- The primary agent reproduced both the resolved profile behavior and the composed-gate failure.

### Discovery Accelerators

| Tool / generated view | Source revision | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| `codebase-memory-mcp` | pre-PROFILE-003 index at `26c9580` | stale for subject and excluded affected hidden roots | omitted `.ai/assets`, `.ai/scripts`, `.claude`, examples, and tools | links, hidden completeness, runtime selection | not used for conclusions; `rg -uu`, direct reads, validators, and Git used |

## Strengths

1. `SVF-001` is resolved in both content and enforcement: `TestInMemory`/`TestOutbox` are canonical, the shared projection root is scanned, and an injected stale token is rejected.
2. VFY-002/003/004 remain resolved: technology selection 3/3, documents 2/2, source-include 4/4, and BuildingBlocks 5/5 pass.
3. Workflow history passes 32 first-parent commits; `main`, v0.3.0, assessment branches, and the absence of a v0.4.0 tag remain correct.
4. `SVF-002` is explicitly LOW/deferred and enumerated but not executed by the aggregate runner.

## Previous Finding Reconciliation

| Finding | Result | Evidence |
| --- | --- | --- |
| `ASM-20260717-001#SVF-001` | resolved | canonical names in both projections; 185-file allowlist includes them; 3/3 and injected negative fixture pass |
| `#SVF-002` | deferred, nonblocking | helper is transitional/deferred; `run_deferred_check` records it but does not invoke it |
| `ASM-20260716-001#VFY-001` through `VFY-006` | resolved | focused tests, 32-commit validation, rewrite evidence, full gate without closeout variables, and registries pass |

## Findings

### FVF-001 — Synthetic Aggregate-Runner Tests Inherit Closeout-Only Variables

- Severity: **MEDIUM**
- Affected paths: [fail-closed runner tests](../../../.ai/scripts/tests/test_fail_closed_validation.py) and [aggregate runner](../../../.ai/scripts/check-all.sh)
- Repository-native evidence: with `COMMIT_RANGE=ed5f8fb...HEAD` and `WORKFLOW_ID=2026-07-16-v0-4-0-ai-context-remediation`, the outer commit check passes 32/32, but `test_gwt_006_given_no_spec_inputs_when_quick_runs_then_spec_is_not_applicable` fails because `SyntheticRunnerRepo.execute` removes `SPEC_FILE` and `TASK_NAME` while retaining the two closeout variables. Its nested quick run therefore records one N/A instead of the fixture's expected two. The same suite passes 18/18 without inherited closeout variables.
- Why it matters: the repository cannot run its complete declared workflow-closeout gate in one composed environment even though each underlying contract passes separately.
- Confidence: **high**
- Recommended disposition: make the synthetic runner environment deterministic by removing `COMMIT_RANGE` and `WORKFLOW_ID` before applying test-specific overrides. Then re-run the focused suite and the full gate with both variables exported.
- User decision required: **no**; this is test isolation, not a governance-policy change.
- Owner / next skill: `ai-context-governance`

## Baseline And Skill Comparison

### Confirmed

- Both passes confirm PROFILE-003 and all substantive standards remediation.
- Both passes reproduce the closeout-only nested fixture failure.

### Added By Repository-Aware Review

- Separate full-gate and explicit commit-range passes are useful evidence but do not satisfy the stricter composed closeout contract while the single declared invocation fails.

### Downgraded Or Deferred

- `SVF-002` remains LOW because it is enumerated as deferred but never selected for execution.
- Down-tiered legacy example names remain nonblocking unless promoted.

### Overturned

- The pre-PROFILE-003 HIGH profile finding is overturned by current file and negative-fixture evidence.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Profile projection contract | pass | 3/3; active shared root included |
| Injected stale-name fixture | pass | `test-inmemory` rejected |
| Document/technology/source-include | pass | 2/2, 3/3, 4/4 |
| BuildingBlocks/analyzer/validation | pass | 5/5, 49/49, 2/2 |
| Commit range | pass | 32 first-parent commits |
| Workflow/assessment/release/disposition/shell | pass | all repository-native validators pass |
| Full gate without closeout variables | pass | 20/20, zero advisories |
| Full gate with closeout variables | **fail** | outer commit check passes; nested fail-closed fixture fails 1/18 |
| Git/tag/ref invariants | pass | main unchanged; v0.3.0 unchanged; no v0.4.0 tag |

### Skipped Validation

- GitHub Release, external publication, product code, downstream clean-room construction, and full OBS-001 design.
- Windows symlink privilege probe remains an isolated environment skip.

## Recommended Action Order

1. Remediate `FVF-001` by scrubbing closeout-only variables in the synthetic runner fixture.
2. Run the focused 18-test suite and full gate with `COMMIT_RANGE`/`WORKFLOW_ID` exported.
3. Perform a final independent verification checkpoint, reconcile `VERIFY-001`, and close or explicitly defer every finding.
4. Proceed to deterministic package/release-candidate evidence without tagging or merging main.

## Deferred Items

- `SVF-002` manual helper advice/retirement;
- clean-room reconstruction, NuGet productization, and full Observability design in `OBS-001`;
- downstream product remediation.

## Appendix

### Commands Run

```text
rg -n -uu <profile, route, helper, and environment patterns>
python .ai/scripts/tests/test_profile_projection_contract.py -v
python .ai/scripts/tests/test_fail_closed_validation.py -v
python tools/maintenance/validate-git-commits.py --range ed5f8fb...HEAD --workflow-id 2026-07-16-v0-4-0-ai-context-remediation
COMMIT_RANGE=ed5f8fb...HEAD WORKFLOW_ID=2026-07-16-v0-4-0-ai-context-remediation check-all.sh --full
python .ai/scripts/validate-workflow-artifacts.py
python tools/maintenance/validate-assessment-artifacts.py
python .ai/scripts/validate-ai-context-versions.py
python tools/maintenance/validate-file-disposition-manifest.py --manifest <workflow-manifest>
python .ai/scripts/validate-shell-assets.py
dotnet test <three tool-owned verification projects>
git status --short --branch
```

### Notes

- Assessed surfaces remained read-only on this branch.
- codebase-memory was not used as completeness or relationship evidence.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260717-002/report.md`
- Stable finding reference: `ASM-20260717-002#FVF-001`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-07-16-v0-4-0-ai-context-remediation`
- Verification assessment: this assessment
- Remediation intentionally not performed by this skill: `yes`
