# v0.13 Downstream Upgrade And External Review Union Assessment

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260813-001`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-13`
- `created_at`: `2026-08-13T22:26:44+08:00`
- `updated_at`: `2026-08-13T22:58:53+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `5c93e81f1f26e0c55f98cea08d014fc5c5fdc83c`
- `related_assessments`: `ASM-20260804-002`, `ASM-20260810-005`, `ASM-20260811-001`, `ASM-20260811-002`, `ASM-20260811-003`, `ASM-20260811-006`

## Executive Summary

- Overall assessment: v0.13 is a successful real-world semantic-upgrade milestone, but the first complete downstream execution exposed package-apply, portable validation, changed-path selection, target-policy cutover, terminal-runner, and exact-predecessor-only upgrade-policy gaps that source-tree validation did not detect. Claude's v0.12 analysis adds one still-relevant validation incident cluster and one useful measurement gap. The company-project report is valuable as an upgrade-UX scenario but cannot establish current target defects because its actual v0.6 customization records were unavailable.
- Overall score: `N/A`; the downstream author separately reported `7.8/10` developer experience.
- Decision: `remediation-recommended`
- Primary strengths: exact-predecessor migration evidence, independent closeout audit, SDK-free framework baseline, explicit optional-provider selection, and durable external-review provenance.
- Primary risks: a non-transactional package apply boundary, incomplete portable dependency closure, target-hostile policy cutovers, exact-predecessor-only release compatibility, missing process-tree termination, and a .NET analyzer fallback contract that promises creation guidance but no longer carries source/test templates.

The normalized next-version intake is seven cohesive work items, not seventeen one-finding Issues. Existing #21, #149, and #179 remain separate and are not duplicated. Project allocation, implementation, merge, and release publication are not authorized by this assessment or by Issue creation.

## Scope

### Included AI Context Surfaces

- `.ai/scripts/ai_context_package.py` and `.ai/scripts/ai_context_package_apply.py`
- `.ai/scripts/check-all.sh`, validation registry, evidence, and fixture cleanup contracts
- `.ai/distribution/**` payload/profile/component projections
- `.dev/releases/v0.6.0`, `v0.9.0`, `v0.12.0`, and `v0.13.0` compatibility metadata and migration guidance
- migration source schema and repeatable package-builder inputs
- `.ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation/**`
- current GitHub Issue decisions and deduplication state
- exact retained downstream and Claude review bytes listed in `evidence/evidence-catalog.yaml`
- read-only Engineering Guardrails product evidence at `C:/Github/YuChia/dotnet-architecture-kit@d0d23e9`

### Default Exclusions

- `src/**`
- downstream product implementation and product tests
- generated and dependency trees

### Additional Exclusions

- Claude `archive/**`, because the supplied README explicitly marks those reports superseded and known-incorrect
- company-project defect claims that require unavailable current customizations
- implementation or remediation of any finding
- Project/milestone mutation, push, PR, merge, tag, release, or publication

### Code Review Handoff

- Requested: `no`
- Paths not scanned: downstream product code and tests
- Recommended skill: `not-applicable`; findings concern AI-context distribution, governance, and validation tooling

## Methodology And Evidence

### Pass A: Independent Baseline

- Preserved exact bytes and SHA-256 for the two current Claude reports, their source README, and six downstream closeout artifacts.
- Bound downstream evidence to clean commit `14e6fe9287c6e8e95f64c678ddff3009fb9092b2`.
- Reproduced the package planner, receipt, changed-path traversal, commit-cutover, package-test import, cleanup, EOF, schedule, and analyzer-template observations against current `main@5c93e81`.
- Compared retained-origin release metadata and confirmed that the migration schema/package builder can structurally carry more than one source migration even though release policy currently promises only the immediate predecessor.
- Inspected live GitHub Issues before proposing successor work.

### Pass B: Repository-Aware Skill Review

- Applied AI-context ownership, semantic-customization, assessment artifact, external-review intake, and remediation-lifecycle boundaries.
- Treated external reports as evidence/proposals, not canonical truth.
- Kept recommendation, default selection, implementation availability, package readiness, and release adoption as separate states.

### Delegation

- Sub-agents used: `none`
- Assigned surfaces: `not-applicable`

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory graph | `main@5c93e81` index | graph returned source-path symbol locations; worktree was clean | Python package planner/apply discovery | package byte closure, shell semantics, Git history, external reports | direct tracked-file reads, `git show`, retained exact bytes |
| GitHub connector | live repository state on 2026-08-13 | current at read time | open/closed Issue identity and bodies | local unpushed assessment content | repository files and retained assessment evidence |

## Evidence Reliability

| Source | Reliability for this assessment | Boundary |
| --- | --- | --- |
| Current framework files at `5c93e81` | high | canonical current repository evidence |
| dotnet-mq upgrade at `14e6fe9` | high for observed upgrade behavior | not authority for upstream design or implementation |
| Claude v0.12 framework analysis | medium-high after current-tree reproduction | historical baseline; several claims changed in v0.13 |
| Claude company-project upgrade report | medium for scenario design, low for target-specific defect claims | actual v0.6 customization files were unavailable; v0.5 was used only as a reference |
| Owner decisions in `owner-decisions.yaml` | high for intended direction | design direction is not implementation completion |
| Engineering Guardrails repository at `d0d23e9` | high for current product/source identity | package ID and publication readiness remain separately governed |

## Strengths

1. The downstream upgrade retained exact predecessor migrations, reconciliation, validation, assessment, and closeout evidence through v0.13.
2. The SDK-free baseline is real: current required framework checks no longer require a framework-owned .NET project.
3. The no-provider path remains honest. A target can complete an upgrade without an analyzer if the capability gap is explicit.
4. Engineering Guardrails already contains real Roslyn analyzer source and DBA1001-series diagnostic documentation; the provider is no longer only a conceptual future placeholder.
5. The existing Issue set provides clean boundaries: #179 owns optional Contracts adoption, #149 owns runtime strategy, and #21 owns richer workflow/timeline metadata.
6. Migration schema 3 and the package builder already support ordered/repeatable migration sources, so retained-origin support does not require replacing the package format before route policy and validation can begin.

## Architecture Kit / Engineering Guardrails Decision Reconciliation

The owner's interpretation is substantially correct, with one new implementation gap.

1. **Optionality was not overturned.** Earlier design evidence treated Architecture Kit as an optional .NET provider with independent versioning. Current #187 also requires that a target with no analyzer or Contracts can still use AI reasoning guidance. The owner now resolves the renamed product identity: Engineering Guardrails is the official recommended provider for .NET only, but it is not default-selected.
2. **The provider-removal timing was superseded.** Earlier #92/#106-era planning retained the bundled provider until the external readiness gate. The later v0.13 owner decision in #187 deliberately removed the framework-owned compilable provider first to obtain an SDK-free framework baseline. That is a later strategy replacement, not an unresolved contradiction. The remaining safety contract is to report the mechanical-validation gap honestly and never claim provider execution when none was selected.
3. **The external provider and Contracts are separate adoption surfaces.** Open #179 covers `EngineeringGuardrails.Contracts.*`; it does not authorize or fully describe analyzer-provider adoption. Engineering Guardrails product evidence explicitly makes analyzers independently adoptable and Contracts optional.
4. **The source-template fallback is currently missing.** The current on-demand profile states that it ships no compilable analyzer project, and `recipes/analyzer-project.md:5` states that it does not supply an analyzer implementation. Current tracked content has no `DiagnosticAnalyzer` implementation or analyzer test template. In contrast, `v0.12.0` carried complete analyzer and test sources. The repository therefore retains a recipe, mapping, severity snippet, and one test pattern, but not the source-template capability the owner now requires.
5. **Terminology is stale.** `recipe-manifest.yaml:42` still says `Architecture Kit availability or cutover`. Future remediation should use Engineering Guardrails while preserving historical evidence unchanged.

The desired steady state is therefore:

| Concern | Decision |
| --- | --- |
| Framework release dependency | SDK-free; no required .NET build/test gate |
| Recommended .NET analyzer provider | Engineering Guardrails |
| Default selection | none; explicit target owner selection |
| Provider availability claim | only after exact package/version/readiness evidence |
| Declined/unavailable provider | target may create its own analyzer from bounded reference-only source and test templates |
| Framework semantics | canonical rules/constraints remain provider-neutral; .NET binding is profile-owned |
| Contracts | optional and separately tracked by #179 |

## Cross-Version Compatibility Decision

The owner has converted the company-project multi-hop concern from an evidence-limited scenario into a normative compatibility direction for future releases.

1. **Support floor.** Starting with v0.14.0, every subsequent release must support its immediate predecessor, v0.9.0, and v0.6.0 as upgrade origins until an explicit owner deprecation decision.
2. **One entrypoint, not necessarily one delta.** A supported origin may use a validated direct migration or an automatically orchestrated chain of immutable predecessor migrations. The user must not manually apply every intermediate release.
3. **Direct is conditional.** A direct route is preferred only when it preserves all intervening semantic cutovers, owner decisions, validation authority, receipts, resume, and rollback evidence. Otherwise the resolver must select the internally orchestrated route.
4. **Current behavior is insufficient.** v0.13 declares only v0.12 as its minimum, reconciliation, and automatic source; its guide sends older sources to owner-reviewed reconciliation or manual checkpoint upgrades. v0.12, v0.9, and v0.6 similarly promise only their immediate predecessor.
5. **The package format is not the blocker.** The migration schema already accepts multiple ordered source entries, and the package builder accepts repeatable `--migration-source` inputs. Missing work is a durable support matrix, safe route resolver/orchestrator, retained immutable assets, generated route evidence, and release gates.

The support matrix must distinguish `direct`, `orchestrated-multi-hop`, `reconciliation-required`, and `unsupported`. A promised v0.6/v0.9 route that lacks an exact package, manifest, checksum, migration edge, or incoming validator must fail before mutation and must block the release candidate rather than silently degrading to unsupported.

## Downstream 17-Item Disposition

| Classification | Count | Items |
| --- | ---: | --- |
| Still valid | 14 | DS-02, DS-03, DS-04, DS-05, DS-07, DS-08, DS-09, DS-10, DS-12, DS-13, DS-14, DS-15, DS-16, DS-17 |
| Fixed | 0 | none |
| Design tradeoff with owner direction selected | 2 | DS-01 and DS-11 use the Hybrid decision in `owner-decisions.yaml`; implementation remains pending |
| Needs decision | 1 | DS-06 needs the exact pre-finalization packet schema and lifecycle |
| Downstream-only | 0 | each item maps to a reproducible or portable framework concern |

The full item-to-work-item mapping is machine-readable in `evidence/finding-disposition.yaml`.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| PKGAPPLY-001 | HIGH | Package planning and apply do not form a complete durable transaction over selected managed state. | `ai_context_package_apply.py:840-851` observes only migration operation paths; unchanged managed paths can be omitted. Lines 1019-1054 keep rollback snapshots in memory and write the pending receipt after mutations. | Drift can remain invisible in the plan, and process death/ACL failure can leave prefix mutations without a durable recovery record. | Inspect every selected required path, persist a journal before mutation, and implement the owner-selected Hybrid raw-byte/Git-mode/portable-proof identity contract. | `ai-context-governance` coordinating bounded tooling work |
| PKGCLOSURE-001 | HIGH | Portable package validation is not closed over the package's declared runtime and test surface. | Downstream stock validation reported 36 projection errors. Current tests still read `.ai/distribution/profiles/dotnet-backend.yaml` and import source-only `ai_context_package`; component projections disagree for `AI-CONTEXT-VERSION-POLICY.md`; two packaged documents end in duplicate LF bytes. | Source-tree success can mask extracted-package failure; predecessor validators can pass an incoming candidate they do not understand. | Validate an isolated extracted payload with incoming validators, generate component ownership from one source, classify source-only cases explicitly, and lint the full package delta. | `ai-context-governance` |
| VALSEL-001 | HIGH | Changed-path selection can omit transitive dependencies. | `check-all.sh:264` marks a direct match selected before `select_with_dependencies`; the guard at line 155 returns without traversing dependencies. | Narrow validation can skip required checks while reporting deterministic selection. | Expand dependencies before final selected-state marking, with cycle protection and exact-once evidence. | `ai-context-governance` |
| UPGRADE-001 | HIGH | Upgrade truth is not fully target-prospective or consumable before finalization. | Commit grammar switches on source commit time (`validate-git-commits.py:68-70`; policy fixed timestamp at line 15), migration guidance omits target adoption, incoming/predecessor validator authority can diverge, and evidence/resume references are structurally weak. The company scenario independently highlights seven-hop owner-decision burden. | Valid target history can be rejected retroactively; owners cannot safely remediate a candidate without stale packets or manual interpretation. | Define target adoption cutovers, incoming-candidate validation authority, a receipt-bound pre-finalization packet, and semantic evidence/resume validation. | `ai-context-governance` plus `ai-context-upgrader` contract owner |
| UPGCOMPAT-001 | HIGH | Release compatibility is exact-predecessor-only and has no retained-origin route contract. | v0.13 metadata and guide automatically support only v0.12; v0.12, v0.9, and v0.6 follow the same predecessor-only pattern. The real v0.6-to-v0.13 exercise required seven governed checkpoints. The migration schema and builder already accept multiple source migrations, but no support matrix or one-entrypoint route resolver exists. | Rapid releases multiply manual owner decisions and make adoption from the installed v0.6/v0.9 population increasingly expensive and error-prone. | Starting with v0.14, retain predecessor/v0.9/v0.6 support through validated direct or internally orchestrated routes, with one user entrypoint and fail-closed release gates until explicit owner deprecation. | `ai-context-upgrader` contract owner coordinated by `ai-context-governance` |
| VALRUN-001 | HIGH | Terminal validation policy improved in v0.13, but the runner still does not seal process trees or bind one immutable execution snapshot. | `ASM-20260810-005` findings remain reproducible: `check-all.sh:867-895` terminates a direct PID or uses `timeout --foreground`; no runner pre/post snapshot identity check exists; nested subprocess and fixture cleanup gaps remain; no scheduled nightly workflow exists. | Timed-out descendants can keep writing, evidence can span commits, and release-only regressions remain late and expensive. | Add cross-platform process-tree supervision, immutable pre/post identity, sealed logs, bounded nested subprocesses, visible cleanup failure, coverage de-duplication, and then schedule nightly-full. | `ai-context-governance`; #149 remains the future runtime comparison |
| GUARDRAILS-001 | MEDIUM | Current .NET profile does not encode the owner-selected official-provider relationship or the required source-template fallback. | Engineering Guardrails has real analyzers at `d0d23e9`; current framework recipe is reference-only and explicitly supplies no implementation; #179 covers Contracts only; stale Architecture Kit wording remains. | Targets either receive no concrete path beyond a project-file recipe or may confuse recommendation with selection/readiness. | Add a separately gated analyzer-provider binding and bounded non-selected source/test templates without reintroducing a framework .NET release gate. | `ai-context-governance`; Engineering Guardrails readiness remains external |
| EVAL-001 | LOW | Current evaluation root has no official context-load trace instances, but historical controlled v0.6 evidence exists. | `.ai/evaluation/context-load/` contains only README; `.dev/workflows/2026-07-24-v0-6-context-load-simplification/evidence/**` retains a controlled trace. | Current context-cost decisions lack a representative maintained baseline, but Claude's statement of "never measured" is too broad. | Defer a new Issue until a concrete decision requires fresh release/development traces; do not duplicate #149 or treat validator/source ratio as a defect. | owner planning decision |

## Claude And Company Report Reconciliation

### Confirmed

- `VALTIME-001` and `VALTEST-001` remain valid.
- `VALSNAP-001` is policy-improved by #194 and the long-running validation gate, but runner enforcement is still absent.
- `VALCOST-001` is interaction-cost-improved by external delegation, but coverage duplication and budget calibration remain unresolved.
- There is no scheduled `nightly-full` workflow.
- The company report's commit-policy concern corroborates the real downstream cutover failure.

### Corrected Or Superseded

- Claude's v0.12 statement that the semantic upgrader lacked a real target end-to-end execution is now superseded by the exact `dotnet-mq-arch-lab@14e6fe9` upgrade and closeout evidence.
- The current evaluation root has zero trace instances, but a historical controlled context-load measurement exists under the v0.6 workflow. The correct finding is a missing maintained/representative baseline, not zero historical measurement.
- The company report inferred that SDK-free #187 effectively resolved deferred analyzers. Owner clarification overturns that inference: no-provider remains valid, while Engineering Guardrails is the official recommended .NET provider and source-template fallback is required.

### Evidence-Limited

- The company report's nine overrides and six unresolved records are estimates from an older reference because current company-project customization files were unavailable. They may shape fixture design but must not be copied into canonical target state. Its general multi-hop UX risk is now independently adopted through the owner's retained-origin compatibility decision.
- Target branch, work-item provider, source repository rename, and old-name cleanup remain target-owned reconciliation inputs, not universal defaults.

### Covered By Existing Work

- Rich task timeline metadata: #21.
- Validator/runtime strategy and validator-code growth decision: #149.
- Engineering Guardrails Contracts prerelease adoption: #179.

## Proposed Online Work Items

| Candidate | Findings / feedback | Scope boundary | Online Issue |
| --- | --- | --- | --- |
| `PKG-011` | `PKGAPPLY-001`, DS-01/02/03/10/11 | transactional apply and Hybrid identity | [#200](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/200) |
| `PKG-012` | `PKGCLOSURE-001`, DS-04/07/13/14/15/17 | extracted-payload validation and component closure | [#201](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/201) |
| `VAL-006` | `VALSEL-001`, DS-05 | changed-path dependency closure only | [#202](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/202) |
| `UPG-002` | `UPGRADE-001`, DS-06/08/09/12 | target-prospective cutover and remediation packet | [#203](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/203) |
| `VAL-007` | `VALRUN-001`, DS-16, Claude validation cluster | current runner correctness and nightly readiness | [#204](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/204) |
| `CTX-010` | `GUARDRAILS-001`, owner Engineering Guardrails decisions | optional recommended .NET provider plus source-template fallback | [#205](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/205) |
| `UPG-003` | `UPGCOMPAT-001`, company multi-hop scenario, owner retained-origin decisions | v0.6/v0.9 retained support and one-entrypoint route selection | [#206](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/206) |

All seven are next-version candidates. UPG-003 defines v0.14.0 as the first compatibility-policy gate, but no Project field, milestone, delivery workflow, or release allocation is made by this intake.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state and subject identity | passed | clean `main@5c93e81` baseline; dedicated assessment branch |
| External source preservation | passed | nine retained files match catalogued byte counts and SHA-256 |
| Downstream source identity | passed | clean `dotnet-mq-arch-lab@14e6fe9` |
| Current code reproduction | passed | planner/apply, changed-path, commit cutoff, source-only imports, cleanup, EOF, schedule, and analyzer-template checks reproduced |
| Engineering Guardrails identity | passed | clean `dotnet-architecture-kit@d0d23e9`; analyzer source and diagnostic docs observed |
| GitHub deduplication and creation | passed | live open/closed Issues inspected; #21/#149/#179 retained separately; #200 through #206 created and read back without milestone or assignee |
| Assessment artifact validation | passed | `python .ai/scripts/validate-assessment-artifacts.py --root .` passed for 53 assessments after online Issue links and owner decisions were recorded |

### Skipped Validation

- No long-running release/nightly validation was run; this assessment changes only assessment-owned artifacts.
- No downstream product source or tests were scanned.
- No company-project checkout or unavailable customization record was inferred.
- No provider package restore/publication readiness was claimed.

## Recommended Action Order

1. Treat `UPG-003` as a v0.14 compatibility gate and design it with `UPG-002`, `PKG-011`, and `PKG-012`; route availability cannot be separated from per-hop correctness and durable receipts.
2. Prioritize `VAL-006` before relying on narrowed validation as evidence for the new route matrix.
3. Fix `VAL-007` before treating nightly or terminal evidence as a stronger release gate; then add scheduled nightly coverage.
4. Treat `CTX-010` as the owner-decision normalization item: provider recommendation, selection, readiness, and fallback templates must remain distinct.
5. Keep #21, #149, and #179 independent; reference this assessment rather than expanding them implicitly.
6. After explicit implementation authorization, create one or more delivery workflows based on shared files, validation, rollback, and release cohesion; Issue count alone must not decide workflow count.
7. Require an independent post-remediation assessment plus real pristine/customized v0.6 and v0.9 upgrade fixtures before closeout.

## Deferred Items

- Exact pre-finalization packet schema and retention lifetime require owner approval in `UPG-002`.
- Exact Engineering Guardrails package ID/version/feed and readiness gate remain external decisions.
- Fresh context-load traces are deferred until a concrete context-cost decision needs them.
- Priority among the seven Issues, Project allocation, milestone assignment, implementation topology, and publication remain separate owner decisions. The v0.14 compatibility entry gate is recorded, but no delivery allocation is implied.

## Appendix

### Commands And Read-Backs

```text
git status --short; git rev-parse HEAD
Get-FileHash -Algorithm SHA256 <retained external files>
git -C C:/Github/YuChia/dotnet-mq-arch-lab rev-parse HEAD
git -C C:/Github/YuChia/dotnet-architecture-kit rev-parse HEAD
git ls-tree -r --name-only v0.12.0
rg -n <bounded planner, validation, package, analyzer, schedule, and cleanup patterns>
Get-Content .dev/releases/v0.6.0|v0.9.0|v0.12.0|v0.13.0 release metadata and migration guides
codebase-memory search_graph/get_code_snippet for build_plan and apply_plan
GitHub connector fetch/search for #21, #92, #106, #135, #144, #149, #168, #179, #187, #193, and #194; create/read-back #200 through #206
```

### Retained Evidence

- [catalog](evidence/evidence-catalog.yaml)
- [owner decisions](evidence/owner-decisions.yaml)
- [finding disposition](evidence/finding-disposition.yaml)
- [Claude current-report package](evidence/external/original/claude-opus-5-framework-analysis/README.md)
- [downstream v0.13 upgrade feedback](evidence/external/original/dotnet-mq-arch-lab-v013-upgrade/upstream-feedback-brief.md)

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260813-001/report.md`
- Stable finding references: `ASM-20260813-001#PKGAPPLY-001`, `ASM-20260813-001#PKGCLOSURE-001`, `ASM-20260813-001#VALSEL-001`, `ASM-20260813-001#UPGRADE-001`, `ASM-20260813-001#UPGCOMPAT-001`, `ASM-20260813-001#VALRUN-001`, `ASM-20260813-001#GUARDRAILS-001`, `ASM-20260813-001#EVAL-001`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `not-created`
- Verification assessment: `not-created`
- Remediation intentionally not performed by this skill: `yes`
