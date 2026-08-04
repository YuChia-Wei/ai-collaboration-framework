# Downstream Architecture Kit And Sub-Agent Proposal Evidence Intake

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260804-002`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-04`
- `created_at`: `2026-08-04T23:11:05+08:00`
- `updated_at`: `2026-08-04T23:11:05+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `4e7b5e0d59be831453b5c34f5f1eb3a1daae1245`
- `related_assessments`: [`ASM-20260715-002`](../ASM-20260715-002/report.md), [`ASM-20260730-001`](../ASM-20260730-001/report.md)
- `workflow_refs`: none
- `backlog_refs`: `STD-001`, `SAG-001`

## Executive Summary

- Overall assessment: the downstream discussion contains valuable, owner-led design evidence for layered engineering-rule ownership and post-contract sub-agent reachability. Its main conclusions are reproducible against the current source repository, but the evidence must be retained upstream and the bundled .NET provider needs an explicit interim placement and activation contract before Architecture Kit cutover.
- Overall score: `N/A`
- Decision: `remediation-recommended`
- Primary strengths: the discussion separates semantic ownership from mechanical enforcement, keeps Architecture Kit opt-in and independently versioned, distinguishes target semantic deviations from enforcement tuning and tooling waivers, and correctly splits sub-agent reachability from runtime-adapter installation drift.
- Primary risks: the only complete reasoning record is on a downstream discussion branch that the owner intends to remove; Issue #92 still identifies `tools/**` as the interim provider without defining its canonical profile placement or target activation; and Issue #94 needs durable evidence links without prematurely answering its seven owner decisions.

This assessment preserves bounded source bytes, assigns stable finding IDs, and records bidirectional proposal relationships. It does not adopt either proposal, authorize implementation, reopen `SAG-001`, or turn the downstream workflow into an upstream workflow.

## Scope

### Included AI Context Surfaces

- `.dev/standards/**` ownership and placement boundaries, including the flat `AI-CONTEXT-OWNERSHIP.yaml` rule registry.
- `.ai/assets/tech-stacks/dotnet-backend/**` as the current portable .NET profile projection.
- `.ai/distribution/profiles/dotnet-backend.yaml`, especially component identity and the managed `tools/**` entry.
- `tools/DotnetBackendAnalyzers/**` and `tools/DotnetBackendValidation/**`.
- `.ai/SUB-AGENT-SYSTEM.MD` and the canonical owning-skill specifications for `slice-implementer`, `problem-frame-author`, `bdd-gwt-test-designer`, `code-reviewer`, and `software-development-orchestrator`.
- GitHub [Issue #92](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/92) and [Issue #94](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/94), read on 2026-08-04 before their approved evidence corrections.
- Bounded downstream evidence from `dotnet-distributed-architecture-lab@b29ef357d7c6c7cb202d11896466a039e1e17483`.
- Read-only Architecture Kit planning state at `dotnet-architecture-kit/proj-temp@da45952d4962e4e0f11b046d09022847519657d9`.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- The downstream workflow locator, task, handoff, branch history, and continuation state as upstream workflow identity.
- Architecture Kit implementation, package publication, Diagnostic parity, or provider cutover.
- Relocating `tools/**`, editing the distribution profile, or changing target `.slnx`, `Directory.Build.props`, or `.editorconfig`.
- Issue #93 execution. Its installation-drift work is owned by a separate Codex task.
- Product naming changes. The proposals must use the repository's canonical naming rather than reopen a rename.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product implementation and product tests
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Read the source repository at `main@4e7b5e0` before importing external claims.
- Compared current rule ownership, customization identity, distribution component mapping, source-included tool contracts, canonical role routing, and owning-skill references.
- Read Architecture Kit's current local planning branch, tag inventory, and packability declarations without treating it as a released provider.
- Read the current online proposal bodies and separated proposal visibility from canonical backlog or implementation authority.

### Pass B: Repository-Aware Skill Review

- Applied the assessment intake boundary from `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`.
- Applied `ai-context-auditor` to reproduce claims and assign stable findings.
- Applied `ai-context-governance` to classify universal semantics, .NET profile assets, target-owned configuration, runtime reachability, and future remediation ownership.
- Preserved the downstream files as exact external bytes and cataloged their origin and SHA-256 in [evidence-catalog.yaml](evidence/evidence-catalog.yaml).
- Mapped proposal sections and questions to both downstream evidence and repo-native findings in [proposal-traceability.yaml](evidence/proposal-traceability.yaml).

### Delegation

- Sub-agents used: `no`
- Assigned surfaces: not applicable

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| Git and PowerShell read-only inventory | source `4e7b5e0`; downstream `b29ef35`; Architecture Kit `da45952` | all three inspected worktrees clean | governance, profile, tool, and role-routing text; product code excluded | cannot authorize adoption or implementation | direct file reads and pinned Git refs |
| GitHub connector issue read | #92 updated 2026-08-04T12:35:42Z; #94 updated 2026-08-04T12:35:08Z | live at intake time | proposal title, body, labels, and state | mutable provider state is not canonical backlog truth | retained assessment relationships and merged-main links |

## Repository Context Inventory

| Surface | Audience | Current state | Assessment relevance |
| --- | --- | --- | --- |
| `.dev/standards/**` | agents and maintainers | owns normative standards; the ownership registry uses stable flat `rule_id` entries | supports the semantic-ownership direction but does not yet provide the normalized concept/rule/constraint/binding model proposed by #92 |
| `.ai/assets/tech-stacks/dotnet-backend/**` | agents | contains .NET references, shared projections, and source includes | natural portable owner for .NET-specific rules, constraints, bindings, and bundled mechanical-validation source |
| `.ai/distribution/profiles/dotnet-backend.yaml` | packaging and lifecycle tools | maps `tools/**` directly to component `dotnet-backend`; the broad `.ai/assets/**` entry defaults to `software-development-core` unless overridden | relocation under `.ai/assets/tech-stacks/dotnet-backend/**` requires an explicit component override or dedicated entry |
| `tools/DotnetBackendAnalyzers` | framework and target developers | source-included Roslyn analyzer, `IsPackable=false`, wired into a target through target-owned configuration | current bundled static-analysis capability |
| `tools/DotnetBackendValidation` | framework and target developers | source-included runtime/configuration helper, `IsPackable=false` | belongs in the same mechanical-validation bundle but is not a Roslyn analyzer and needs separate activation |
| Architecture Kit | package planners | no local tags observed; analyzer remains `IsPackable=false` on `proj-temp@da45952` | future provider only after a separate cutover gate |
| `.ai/SUB-AGENT-SYSTEM.MD` | agents | maps active roles to owning skills; dynamic loading is default; only `context-translator` is runtime-native | establishes inventory and policy but does not prove an owning skill loaded or invoked a role |

## Strengths

1. The downstream record clearly distinguishes AI Context engineering semantics, profile-owned technology bindings, target-owned effective policy, and mechanical provider behavior.
2. It corrects its own earlier assumptions through explicit superseding decisions rather than silently rewriting history.
3. It treats Architecture Kit as independently versioned and explicitly opt-in, with no reverse dependency on AI Context identities.
4. It identifies provider cutover as a future breaking change rather than claiming a package that does not yet exist as an operational validator.
5. It separates sub-agent reachability from adapter promotion and later separates ignored framework-managed paths into Issue #93.
6. Issues #92 and #94 already carry substantial normalized proposal content and clearly state that proposal creation is not implementation authorization.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | Portable .NET rule and mechanical-validation ownership is structurally split across normative `.dev/standards/**`, agent projections under `.ai/assets/tech-stacks/dotnet-backend/**`, and a root `tools/**` distribution entry. Moving the tools beneath the profile without an explicit component override would classify them under the broad `canonical-ai-assets` default component. | `.ai/distribution/profiles/dotnet-backend.yaml`; `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml`; current tech-stack directories; retained discussion DEC-022 through DEC-031 | A nominal relocation could blur normative versus projection ownership or ship .NET assets as software-development core. | Use a file-by-file migration matrix. Keep cross-technology semantics shared, place .NET rules/constraints/bindings/tooling under the .NET profile, retain source/target governance under `.dev`, and declare the distribution component explicitly. | `ai-context-governance`; Issue #92 discussion |
| AIC-002 | HIGH | Issue #92 defines the bundled provider as the sole supported pre-cutover provider but does not yet define its stable identity, canonical profile location, inactive-by-default source delivery, or target activation/materialization contract. | Issue #92 current Provider transition; analyzer and validation READMEs; both projects `IsPackable=false`; Architecture Kit has no observed tag and remains non-packable | A target could receive source without knowing whether it is active, or an installer could mutate target-owned solution/configuration files while trying to make it active. | Add a stable bundled-provider ID, canonical profile path, separate analyzer/runtime-validation capabilities, explicit `reference-in-place` versus `materialize-to-tools` selection, provenance, and a no-silent-target-config-mutation rule. | `ai-context-governance`; Issue #92 discussion |
| AIC-003 | MEDIUM | The source has a canonical active-role map and a dynamic-loading policy, but mapping alone does not prove owning-skill reachability or distinguish inline application from delegated invocation. `slice-implementer` exposes only command/query/reactor/generic modes; `bdd-gwt-test-designer` stops before final test implementation; the other mapped owning skills do not cite their role manifests in the same explicit way. | `.ai/SUB-AGENT-SYSTEM.MD`; canonical skill specs; retained discussion DEC-033 and DEC-034; retained sub-agent follow-up Problems 1 through 6 | Active roles can remain inert or produce incomparable execution evidence, and test design can hand off to an undefined implementation owner. | Keep all seven questions in Issue #94 unresolved until owner discussion defines mapping authority, applicability, direct/delegated/unavailable semantics, mode alignment, test implementation ownership, and evidence. Do not bulk-generate runtime-native adapters. | `ai-context-governance`; Issue #94 discussion |
| AIC-004 | HIGH | The complete reasoning and follow-up evidence exists only on a downstream discussion branch that is temporary, while the proposals link an older fixed commit. | retained raw evidence; downstream current branch `b29ef35`; Issue #92 and #94 evidence links to `85212e4`; owner intent to remove downstream discussion | Removing the downstream record would break the durable explanation and weaken proposal verification. | Retain exact bounded bytes under this assessment, link proposals to the merged assessment and traceability map, and never import the downstream workflow identity into `.dev/workflows/`. | `ai-context-auditor` intake completed; GitHub proposal correction |

## Proposal Relationships

| Proposal | Assessment role | Canonical backlog context | Stable findings | Authority |
| --- | --- | --- | --- | --- |
| [#92](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/92) | normalized layered-rule and provider-transition design proposal | `STD-001` | `AIC-001`, `AIC-002`, `AIC-004` | proposal and evidence only; no standard adoption, implementation, package publication, or cutover authority |
| [#94](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/94) | normalized post-`SAG-001` owning-skill reachability proposal | `SAG-001` historical/resolved contract context | `AIC-003`, `AIC-004` | proposal and evidence only; its seven questions remain owner decisions |

The locator uses `backlog_refs` only for canonical backlog IDs. GitHub Issue numbers are provider proposals, so their durable relationship is recorded here and in [proposal-traceability.yaml](evidence/proposal-traceability.yaml). After this assessment is merged, each Issue body must link back to these stable artifacts. Future accepted implementation backlog items may add `origin_refs` and selected finding references; this assessment does not create that adoption.

### Issue #93 Boundary

The downstream `AICDISC-ADAPTER-001` observation and follow-up Problems 7 and 8 concern a framework-managed adapter path excluded during downstream install or upgrade. They are mapped only to [Issue #93](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/93). They are not evidence that all canonical roles require runtime-native adapters and are not a blocker for discussing Issue #94. Issue #93 is already being handled in a separate Codex task and was not modified here.

## Recommended Interim Provider And Directory Disposition

This is a proposal correction, not an implemented standard:

| Concern | Recommended owner/location |
| --- | --- |
| Cross-technology engineering concepts and reusable semantics | `.ai/assets/shared/engineering/**` when an agent projection is needed, backed by the applicable normative source |
| .NET-specific rules, observable constraints, examples, bindings, and bundled tooling | `.ai/assets/tech-stacks/dotnet-backend/**` |
| Bundled mechanical-validation source | `.ai/assets/tech-stacks/dotnet-backend/tooling/bundled-mechanical-validation/**` |
| Roslyn analyzer capability | separate activation under the bundle; preferred target selection is `reference-in-place` |
| Runtime/configuration validation helper | same bundle, separate non-analyzer capability and activation |
| Target materialization fallback | explicit `materialize-to-tools` with origin, digest, selected capability, and reconciliation record |
| Target `.slnx`, `Directory.Build.props`, and `.editorconfig` | target-owned; no silent mutation |
| Source/target governance and effective policy | `.dev/**` |
| Human-facing explanation | `.dev/guides/**` |

Analyzer tests remain framework validation assets and are not automatically installed into a target solution. Architecture Kit remains a future replacement provider only after an immutable package identity, Diagnostic-to-constraint mapping, behavior/parity evidence, consumer guidance, compatible profile range, target proof, and owner approval exist.

## Baseline And Skill Comparison

### Confirmed

- The flat source rule registry, customization subject kinds `capability | rule | contract`, managed `tools/**` entry, source-included/non-packable tools, and lack of a current Architecture Kit binding match the downstream record.
- Dynamic canonical role loading is the default and only `context-translator` has runtime-native adapters.
- Issue #92 is the normalized main design proposal; Issue #94 is a deliberately separate reachability proposal.

### Added By Repository-Aware Review

- Moving the bundled provider under `.ai/assets/**` needs explicit distribution component ownership because the broad entry defaults to `software-development-core`.
- `DotnetBackendValidation` belongs in the portable mechanical-validation bundle but must not be described or activated as a Roslyn analyzer.
- A source-present profile asset must remain inactive until the target selects and records an activation mode.
- Assessment-to-proposal traceability must be bidirectional and stable independently of the downstream branch.

### Downgraded Or Deferred

- Architecture Kit package adoption and cutover remain future planning, not a currently executable NuGet path.
- The downstream adapter blocker is assigned to Issue #93 and does not block Issue #94 discussion.
- Product renaming is excluded; neither proposal should reopen it.

### Overturned

- Any reading that Architecture Kit currently supplies the source framework's mechanical validation is rejected by the observed non-packable, untagged planning state.
- Any reading that the downstream workflow itself should be copied into upstream `.dev/workflows/**` is rejected by the assessment/workflow ownership boundary.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | `observed-only` | source, downstream, and Architecture Kit worktrees were read as clean at their pinned commits |
| External byte integrity | `recorded` | source byte counts and SHA-256 values are in [evidence-catalog.yaml](evidence/evidence-catalog.yaml); this is retention metadata, not a validation claim |
| Registry and wrapper parity | `not-run-owner-directed` | no validation script executed |
| Path and reference checks | `not-run-owner-directed` | no validation script executed |
| Schema / structured file parse | `not-run-owner-directed` | no validation script executed |
| Repository aggregate validation | `not-run-owner-directed` | deferred to hosted CI |

### Skipped Validation

Per explicit owner direction, this delivery did not run `validate-assessment-artifacts.py`, `validate-ai-context.py`, `check-all.sh`, `dotnet build`, `dotnet test`, format/lint/package validators, or any other local validation program. Hosted CI is the only requested validation surface for the assessment branch. A hosted failure must be reported without reproducing it locally unless the owner later changes that instruction.

## Recommended Action Order

1. Merge this assessment after hosted CI reports an acceptable result.
2. Update Issue #92 with the interim bundled-provider placement/activation contract, directory migration boundary, acceptance criteria, and stable `AIC-001`, `AIC-002`, and `AIC-004` evidence links.
3. Update Issue #94 only with stable `AIC-003` and `AIC-004` evidence relationships and the Issue #93 split; preserve all seven questions without answering them.
4. Discuss #92 and #94 separately with the owner in dedicated Codex tasks.
5. Only after each discussion produces owner decisions, create bounded implementation Issues and decide whether canonical backlog or workflow adoption is authorized.

## Deferred Items

- #92 design decisions and implementation issue decomposition.
- #94 answers to Questions 1 through 7 and implementation issue decomposition.
- #93 installation/upgrade drift remediation in its already-separated task.
- Any actual migration from `tools/**`, distribution-profile change, target activation implementation, or validation contract.
- Architecture Kit package identity, publication, parity proof, and provider cutover.

## Appendix

### Retained External Evidence

- [discussion-record.md](evidence/external/original/dotnet-distributed-architecture-lab/discussion-record.md)
- [ai-context-rule-architecture-issue-draft.md](evidence/external/original/dotnet-distributed-architecture-lab/ai-context-rule-architecture-issue-draft.md)
- [sub-agent-follow-up-notes.md](evidence/external/original/dotnet-distributed-architecture-lab/sub-agent-follow-up-notes.md)
- [evidence-catalog.yaml](evidence/evidence-catalog.yaml)
- [proposal-traceability.yaml](evidence/proposal-traceability.yaml)

### Commands Run

```text
git fetch origin main
git status / rev-parse / branch / remote / tag read-only queries
PowerShell Get-Content / Get-ChildItem / Select-String read-only inventory
Get-FileHash -Algorithm SHA256 for external evidence retention metadata
GitHub connector read for Issues #92 and #94
```

No local validation command was run.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260804-002/report.md`
- Stable finding references: `ASM-20260804-002#AIC-001` through `ASM-20260804-002#AIC-004`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: none; proposals remain unaccepted design intake
- Verification assessment: deferred until separately authorized implementation exists
- Remediation intentionally not performed by this skill: `yes`
