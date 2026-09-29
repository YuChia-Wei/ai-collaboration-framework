# v0.4.0 AI Context Successor Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260717-001`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-17`
- `created_at`: `2026-07-17T07:16:38+08:00`
- `updated_at`: `2026-07-17T07:16:38+08:00`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `codex/2026-07-16-v0-4-0-ai-context-remediation`
- `subject_commit`: `26c958069510f56818752368bec4bd7ad83e5038`
- `artifact_branch`: `codex/assessment/asm-20260717-001`
- `previous_assessment`: [`ASM-20260716-001`](../ASM-20260716-001/report.md)
- `baseline_assessment`: [`ASM-20260715-002`](../ASM-20260715-002/report.md)
- `workflow_ref`: [`2026-07-16-v0-4-0-ai-context-remediation`](../../workflows/2026-07-16-v0-4-0-ai-context-remediation/workflow.yaml)

## Executive Summary

- Overall assessment: the history rewrite and five of six previous verification findings are fully resolved, but one active profile projection conflict escaped the prior validator scope.
- Overall score: **8.8/10**
- Decision: **remediation-recommended; not release-ready**
- Primary strengths: 30/30 workflow commits pass; the full gate passes 20/20 with zero advisories; profile templates/guides, override-aware testing guidance, async use-case projections, BuildingBlocks behavior, shell lifecycle, migration, assessment, and release registries all pass their declared checks.
- Primary risk: active `.ai` agent-loading projections still use `test-inmemory` and `test-outbox`, while the fail-closed profile projection test scans only `.dev` surfaces.
- Secondary follow-up: a deferred manual DI helper still warns against non-default mocking libraries without resolving the target technology selection; it is not selected by automatic gates.

The branch must not close or be treated as the v0.4.0 release candidate until `ASM-20260717-001#SVF-001` is remediated and independently reverified. No tag or main-branch operation was performed.

## Scope

### Included AI Context Surfaces

- root collaboration entries; `.dev/standards/**`, examples, guides, release and workflow artifacts;
- `.ai/scripts/**`, canonical skills, dotnet-backend projections and source includes;
- `.agents/skills/**` and `.claude/skills/**` wrappers;
- standards-related validators, indexes, manifests, tool-owned verification projects, and Git history.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**` outside tools-owned verification projects
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- `docker-compose/**`, product code review, GitHub Release verification, v0.3.0 tag mutation, full Observability/AOP design, and clean-room downstream product construction.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and tests listed above
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Inspected active/canonical declarations, inbound routes, exact profile names, script selection, history topology, release state, and validator scan boundaries without accepting repository policy claims as proof.
- Distinguished existence, linking, skill navigation, validator enforcement, workflow evidence, and unverifiable AI-session reading.
- Reproduced the active `.ai` projection conflict with `rg -n -uu` and read the validator allowlist directly.

### Pass B: Repository-Aware Skill Review

- Applied `ai-context-auditor`, `AICTX-EVIDENCE-001`, assessment policy, governance lifecycle, workflow policy, ownership/technology-selection rules, and repository release/commit contracts.
- Re-ran the full aggregate gate, focused profile/document/source-include/commit tests, workflow and assessment validators, version/disposition/shell validators, and tool-owned .NET verification projects.

### Delegation

- Sub-agents used: `yes`, read-only
- Assigned surfaces: standards/examples/BuildingBlocks; routing/wrappers/scripts; Git/workflow/release/history.
- The primary agent independently reproduced the only HIGH finding and reconciled all results.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| `codebase-memory-mcp` moderate index | subject working tree at `26c9580` | refreshed before assessment; clean | excluded `.claude`, `.ai/assets`, `.ai/scripts`, `.dev/standards/examples`, `tools`, and other listed roots | Markdown links, hidden-tree completeness, actual AI reading | `rg -uu`, `git ls-files`, direct reads, validators, and Git history |

## Repository Context Inventory

| Surface | Audience | Scope | State | Notes |
| --- | --- | --- | --- | --- |
| Root entries | agent/human | repository | active | AGENTS is canonical; CLAUDE remains a thin import |
| `.dev/standards/**` | agent/human | governance and dotnet-backend | active canonical plus tiered references | canonical profile names are correct |
| `.dev/guides/**` | human | repository/dotnet-backend | routed | override and async projection contracts pass |
| `.ai/assets/**` | agent | universal/dotnet-backend | canonical/projection | two routed projections retain stale profile names |
| `.ai/scripts/**` | agent/tooling | repository | mixed lifecycle | automatic gate is clean; one deferred helper has override-unaware wording |
| runtime wrappers | agent | runtime adapters | active | canonical/agents/claude parity passes |
| release/workflow/assessments | human/agent | governance | active | rewrite evidence and registries are coherent; workflow awaits successor remediation |

## Strengths

1. The guarded rewrite corrected the complete first-parent range without moving `main`, the v0.3.0 tag, or the assessment branch.
2. Example tiers, BuildingBlocks executable evidence, technology override policy, soft-delete/purge semantics, async use-case guidance, and file dispositions are machine-checkable and pass.
3. The aggregate full gate now runs 20 required checks with zero advisories, including BuildingBlocks 5/5, analyzers 49/49, and validation 2/2.
4. Full Observability design remains correctly bounded to open backlog item [`OBS-001`](../../backlog/items/OBS-001.yaml).

## Previous Finding Reconciliation

| Previous finding | Result at `26c9580` | Evidence |
| --- | --- | --- |
| `ASM-20260716-001#VFY-001` | **partially resolved; regressed coverage claim** | `.dev` projections pass, but two active `.ai` projections retain stale names; see `SVF-001` |
| `#VFY-002` | resolved | technology-selection and document projection tests pass; routed guidance resolves target selection |
| `#VFY-003` | resolved | document projection test and direct reads show async/cancellation vocabulary |
| `#VFY-004` | resolved | required aggregate gate runs BuildingBlocks tests; 5/5 and source-include contract 4/4 pass |
| `#VFY-005` | resolved with LOW residual | retired helper is never selected; another deferred manual helper retains override-unaware advice; see `SVF-002` |
| `#VFY-006` | resolved | 30 first-parent commits pass; exact lease and mapping evidence are coherent |

## Findings

### SVF-001 — Active Agent-Loading Profile Projections Retain Noncanonical Names

- Severity: **HIGH**
- Affected paths: [testing strategy](../../../.ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md), [common rules](../../../.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md), and [profile projection contract test](../../../.ai/scripts/tests/test_profile_projection_contract.py)
- Repository-native evidence: the canonical [profile standard](../../standards/coding-standards/profile-configuration-standards.md) defines `TestInMemory` and `TestOutbox` with environment-only selection. The two `.ai` projections use `test-inmemory`/`test-outbox` and are explicitly routed by multiple sub-agent specs. The validator's active roots list covers `.dev/standards/templates`, `.dev/standards/examples`, and `.dev/guides`, but omits `.ai/assets/tech-stacks/dotnet-backend/shared`.
- Why it matters: agents can load stale environment names even though the focused test and full gate are green; this is both an active truth conflict and a fail-closed coverage gap.
- Confidence: **high**
- Recommended disposition: rewrite the two active projections to the canonical names and add the agent-loading projection root/files to the validator contract. Keep reference-only legacy examples down-tiered unless they claim current configuration truth.
- User decision required: **no**; the canonical profile decision is already adopted.
- Owner / next skill: `ai-context-governance`

### SVF-002 — Deferred DI Helper Retains Override-Unaware Mocking Advice

- Severity: **LOW**
- Affected path: [check-test-di-compliance.sh](../../../src/tools/dotnet/check-test-di-compliance.sh)
- Repository-native evidence: the helper recommends NSubstitute and warns on Moq/FakeItEasy without resolving `testing.mocking`; the shell manifest and aggregate runner classify it as transitional/deferred and do not execute it automatically.
- Why it matters: manual use can still imply an invariant where policy defines an overridable default, but it cannot make the release gate green incorrectly.
- Confidence: **high**
- Recommended disposition: remove the mocking-library judgment or retire the helper in a bounded later slice; keep it excluded from automatic gates meanwhile.
- User decision required: **no** for continued deferral; **yes** only if selecting repair versus retirement now.
- Owner / next skill: `ai-context-governance`

## Baseline And Skill Comparison

### Confirmed

- Both passes found the two active `.ai` projections and the validator coverage omission.
- Both passes confirmed that history, release registries, examples, BuildingBlocks evidence, routing, and automatic shell gates are coherent.

### Added By Repository-Aware Review

- `SVF-001` is release-blocking because it contradicts adopted canonical profile truth and escapes an explicitly fail-closed release check.
- `SVF-002` is LOW because lifecycle metadata and runner selection correctly isolate it from required/advisory execution.

### Downgraded Or Deferred

- stale profile names in explicitly reference-only or historical examples are nonblocking unless promoted or presented as current executable truth;
- clean-room architectural reconstruction remains a deferred exercise, not proof that a committed reference product is required;
- full Observability design remains outside this workflow in `OBS-001`.

### Overturned

- the prior conclusion that `VFY-001` was fully resolved is overturned for the two active agent-loading `.ai` projections;
- a passing profile projection test is not evidence of all active projections because its allowlist omits the affected root.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state and subject pin | pass | clean subject `26c9580`; origin branch matched |
| Workflow commit range | pass | 30 first-parent commits |
| Aggregate full gate | pass but semantically incomplete for `SVF-001` | 20/20 required; zero failures/advisories; 4 deferred; 2 not applicable |
| AI context / wrapper / index contracts | pass | 24 active indexes, 14 canonical skills, 2 runtime roots, 32 manifests, 10 mappings |
| Profile projection test | 3/3 pass with coverage defect | `.ai` active projection root omitted |
| Document/source-include contracts | pass | 2/2 and 4/4 |
| BuildingBlocks/analyzer/validation tests | pass | 5/5, 49/49, 2/2 |
| Workflow/assessment/release/disposition/shell validators | pass | 17 workflows, 3 prior assessments, 5 releases, manifest valid, 14 shell assets |
| v0.3.0 immutability | pass | annotated tag still peels to `1e782909b7753b2889014516595d72f703a260f3` |
| Observability deferral | pass | `OBS-001` remains open and outside verification scope |

### Skipped Validation

- GitHub Release and external publication checks were intentionally not repeated.
- Windows symlink privilege probe remained skipped by the packaging suite; this is an environment limitation already isolated by the test harness.
- Actual AI-session reading and clean-room downstream reconstruction are not verifiable from repository evidence.

## Recommended Action Order

1. Remediate `SVF-001` in the existing workflow: align the two projections and expand the profile validator allowlist.
2. Run the focused contract, complete full gate, and a new independent verification assessment.
3. Keep `SVF-002` explicitly deferred or select repair/retirement; it is not a release blocker while excluded from all automatic routes.
4. Reconcile the workflow and only then prepare deterministic release-candidate/package evidence.

## Deferred Items

- `SVF-002` manual helper modernization or retirement;
- clean-room architectural reconstruction;
- NuGet/package-product decisions for analyzers and BuildingBlocks;
- full CrossCutting Observability/AOP design in `OBS-001`;
- product remediation in downstream labs.

## Appendix

### Commands Run

```text
rg -n -uu <profile, routing, script, and active-reference patterns>
python tools/maintenance/validate-git-commits.py --range ed5f8fb...26c9580 --workflow-id 2026-07-16-v0-4-0-ai-context-remediation
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-workflow-artifacts.py
python tools/maintenance/validate-assessment-artifacts.py
python .ai/scripts/validate-ai-context-versions.py
python tools/maintenance/validate-file-disposition-manifest.py --manifest <workflow-manifest>
python .ai/scripts/validate-shell-assets.py
python .ai/scripts/tests/test_profile_projection_contract.py -v
python .ai/scripts/tests/test_document_projection_contract.py -v
python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v
python .ai/scripts/tests/test_git_commit_policy.py -v
dotnet test tools/DotnetBackendBuildingBlocks.Tests/DotnetBackendBuildingBlocks.Tests.csproj --no-restore
dotnet test tools/DotnetBackendAnalyzers.Tests/DotnetBackendAnalyzers.Tests.csproj --no-restore
dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj --no-restore
C:/Program Files/Git/bin/bash.exe ./.ai/scripts/check-all.sh --full
git diff --check
```

### Notes

- codebase-memory was refreshed but excluded the exact hidden roots implicated by `SVF-001`; it was used only as a discovery accelerator.
- No assessed surface was edited on this assessment branch.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260717-001/report.md`
- Stable finding references: `ASM-20260717-001#SVF-001`, `ASM-20260717-001#SVF-002`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-07-16-v0-4-0-ai-context-remediation`
- Verification assessment: this assessment
- Remediation intentionally not performed by this skill: `yes`
