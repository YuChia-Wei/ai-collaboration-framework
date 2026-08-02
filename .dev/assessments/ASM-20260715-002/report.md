# v0.4.0 Standards Lineage And Downstream Adoption Reassessment

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260715-002`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-15`
- `created_at`: `2026-07-15T23:43:06+08:00`
- `updated_at`: `2026-08-02T21:20:17+08:00`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `82b88b7287deb7a64e0311fde6b1b53ea0d194b1`
- `artifact_branch`: `codex/assessment/asm-20260715-002`
- `previous_assessment`: `ASM-20260715-001` (superseded)
- `workflow_refs`: none; this is a standalone durable assessment

## Privacy Corrigendum (2026-08-02)

Two host-local absolute checkout paths were replaced with the portable
`<local-source-checkout>` placeholder to avoid retaining a workstation username.
The pinned evidence revision, score, decision, finding IDs, relationships, and
assessment conclusions are unchanged.

## 1. Executive Summary

This reassessment supersedes [ASM-20260715-001](../ASM-20260715-001/report.md) after two new evidence sources became available: the original Java/EzDDD tree at `ai-coding-exercise@f7ed0b9b5b23822ec012c375261df44f6f03a97f`, and the corrected v0.1.0 downstream at `dotnet-mq-arch-lab@0f71e5ca694ceadacf7616a72805a14b2eef2309`.

- Overall score: **7.3/10**
- Decision: **remediation-recommended**
- The original Java corpus proves direct structural and conceptual lineage. The earlier claim that provenance was unavailable is overturned.
- The multi-domain mono-repo standard is a strong, downstream-proven architecture profile and should be retained.
- The main remaining defect is applicability ownership: portable invariants, framework defaults, target-selected options, and target overrides are not consistently distinguished.
- Examples are neither globally unused nor globally adopted. The lab contains the copied tree but has no workflow reference or target adaptation commit for the examples; its product architecture independently realizes many of their concepts.
- A blanket deletion of `.dev/standards/examples/` remains unsupported. Reduce routing cost by tiering, consolidating, and replacing source-specific examples with small verified reference slices.

The reassessment confirms nine prior findings, narrows two, splits one concern into a new finding, and adds two findings exposed by lineage/downstream comparison. No assessed surface was remediated.

## 2. Scope And Exclusions

### Included

- [`.dev/standards/**`](../../standards/README.md), [`.dev/guides/**`](../../guides/README.MD), [`.ai/scripts/**`](../../../.ai/scripts/README.md);
- [canonical skills](../../../.ai/assets/skills/README.MD), [`.agents` wrappers](../../../.agents/skills/README.md), and [`.claude` wrappers](../../../.claude/skills/README.md);
- [`AGENTS.md`](../../../AGENTS.md), [`CLAUDE.md`](../../../CLAUDE.md), validators, indexes, workflow artifacts, and Git history;
- immutable Git-tree evidence from `<local-source-checkout>/ai-coding-exercise` at `f7ed0b9`;
- target-owned manifests, architecture documents, workflow records, validators, indexes, and Git history from [`dotnet-mq-arch-lab`](../../../../dotnet-mq-arch-lab/AGENTS.md) at `0f71e5c`.

### Excluded

- product source/test quality review in all repositories;
- `docker-compose/**`, build output, generated/dependency trees;
- GitHub Release verification and any v0.3.0 tag operation;
- remediation, standards edits, or creation of a v0.4.0 remediation workflow.

Product manifests and narrow symbol/path checks in the lab were used only to establish architecture adoption, package choice, and analyzer wiring. They are not code-review findings.

## 3. Evidence And Method

The same two-pass discipline was repeated, then extended with two external evidence lenses.

1. Baseline pass: general documentation architecture, truth ownership, routing, validation, and maintenance analysis without using skill conclusions.
2. Formal pass: `ai-context-auditor` evidence and output contracts, plus the assessment lifecycle and placement rules required by `ai-context-governance`.
3. Three bounded read-only sub-agents analyzed Java lineage, downstream adoption, and finding reconciliation. The primary agent verified all HIGH-severity conclusions.
4. Repository-native files, immutable Git objects, literal inbound references, hashes, commits, workflows, and validators were authoritative.

### Discovery Accelerators And Limits

| Index | Revision indexed | Result | Material exclusions | Authoritative fallback |
| --- | --- | --- | --- | --- |
| framework | `82b88b7` | 10,002 nodes / 13,461 edges | `.claude` and hidden document relationships incomplete | `rg -uu`, `git ls-files`, direct reads |
| original repo | current migration branch, not `f7ed0b9` | 15,420 / 22,173 | `.claude`, `.git` | `git ls-tree/show/grep f7ed0b9` |
| downstream lab | `0f71e5c` | 9,084 / 14,458 | `.claude`; `.agents` directory showed no children; exclusion list truncated | `git ls-files`, `rg -uu`, hashes, direct reads |

The indexes accelerated exploration only. They cannot establish hidden-tree completeness, Markdown routing, actual AI reading, or historical contents. The original commit contains 411 files, including 229 under `.ai`, 171 under `.dev`, and 6 under `.claude`, proven by Git-tree enumeration.

### Usage Evidence Vocabulary

| Term | Meaning |
| --- | --- |
| exists | tracked at the pinned revision |
| linked | resolvable inbound reference exists |
| skill-navigated | canonical skill or runtime wrapper routes to it |
| validator-enforced | deterministic check enforces an explicit contract |
| workflow-evidenced | retained workflow records use/change/validation |
| provenance-evidenced | source lineage is established, not present use |
| downstream-adopted | target truth or enforcement explicitly adopts it |
| possible AI reading | unknowable from repository evidence and never inferred from missing logs |

## 4. Baseline Analysis Without Skill

### Strengths

- Root routing, skill ownership, wrapper parity, assessment policy, and machine-readable governance form a coherent spine.
- [`project-structure.md`](../../standards/project-structure.md) accurately describes the desired multi-bounded-context `DomainCore` / `Presentation`, `BC-Contracts`, `BuildingBlocks`, `SharedKernel`, and MQ-only integration shape.
- The Java tree and staged migration commits show deliberate conversion of DDD core, CQRS/application, query, integration, testing, and reference families.
- The lab proves that aggregate roots, event-sourced aggregates, repository/use-case ports, BC contracts, Wolverine adapters, outbox/inbox, and source-included analyzers can be realized without EzDDD runtime dependency.

### Risks

- Mechanical conversion preserved obsolete source-product claims and configuration topology after canonical ownership changed.
- Copied context is easily mistaken for adopted target truth: 172 of 182 framework standards are byte-identical in the lab, while target-owned Moq and Dapper choices differ from focused defaults.
- Example labels claim verification that neither framework nor downstream validators perform.
- The example portfolio remains centered on a single Plan/Task domain and does not demonstrate the canonical cross-BC structure.
- Script registry retention conflates packaging, current execution, transition state, and long-term endorsement.

## 5. Skill-Assisted Analysis

The formal pass applied the [`ai-context-auditor`](../../../.ai/assets/skills/ai-context-auditor/skill.yaml) scope, evidence, persistence, and comparison contract; [`AI-CONTEXT-BOUNDARY.md`](../../standards/AI-CONTEXT-BOUNDARY.md); [`AI-CONTEXT-OWNERSHIP.md`](../../standards/AI-CONTEXT-OWNERSHIP.md) and its [registry](../../standards/AI-CONTEXT-OWNERSHIP.yaml); and the placement/audit-lifecycle lens of `ai-context-governance`.

It confirmed that provenance is not adoption, installation is not enforcement, and workflow success is not semantic completeness. It also requires this successor rather than silently rewriting a final assessment, and prohibits remediation until the user selects findings.

## 6. Comparison Between Both Passes

### Confirmed Or Strengthened

- AIC-001 through AIC-004, AIC-007, AIC-008, and AIC-011 remain valid.
- AIC-002 and AIC-003 now have direct source-history explanations and downstream counter-evidence.
- AIC-004 has higher practical impact because the lab already integrates the DBA1001 analyzer replacement.

### Narrowed

- AIC-005 no longer claims unavailable provenance; it is limited to unresolved example/API realization.
- AIC-006 preserves the deliberate BDDfy and Gherkin dual modes while consolidating shared fixtures and navigation.
- AIC-009 does not treat all shell scripts as retirement candidates; the defect is lifecycle vocabulary.

### Split Or Added

- AIC-010 retains the stale synchronous controller finding. Moq/NSubstitute applicability becomes AIC-013.
- AIC-012 records a target-specific `Lab.*` namespace in canonical structure guidance.
- AIC-014 records the gap between the canonical multi-BC architecture and the example portfolio.

### Overturned

- `ASM-20260715-001#AIC-005` statements that the original Java corpus was absent or concept provenance could not be assessed are overturned.
- The idea that Moq is inherently stale is overturned: the lab explicitly owns `xUnit + Moq + Shouldly`.
- The hypothesis that examples are globally unused remains overturned, but downstream installation alone is not adoption evidence.

## 7. Standards Inventory

The framework tree remains 182 files (approximately 507 KB): 19 root standards, 11 focused coding standards, 6 rationales, 4 nested guides, 3 prompts, 3 templates, and 136 example files.

| Surface | Classification after cross-repo evidence |
| --- | --- |
| governance and ownership policies | `active-canonical`, `routing-required`, partly `validator-enforced` |
| focused architecture standards | `active-canonical`; applicability strength requires clarification |
| project structure | `active-canonical`, conditional multi-BC profile, `downstream-adopted` |
| derived checklists/summaries | `routing-required`; not independent owners |
| rationales and retained migration guides | `reference-only`, selectively weak-routed |
| examples | mixed `example-only`, `reference-only`, `workflow-evidenced`, `stale`, `decision-required` |
| canonical skills and thin wrappers | `routing-required`, parity-enforced |
| scripts | active orchestrators/validators plus manual/transitional assets; registry taxonomy insufficient |

### Java-To-.NET Lineage Summary

The original Java profile has 152 files; 64 have exact relative paths in current standards and 37 more have direct Java-to-C# same-stem equivalents. A normalized mapping accounts for 109 of 141 original standards/examples/guides/prompts/templates. Original examples had 17 groups; current examples have 18, with 71 of 101 original unique basenames retained.

| Concept family | Original state | Current state | Downstream evidence | Conclusion |
| --- | --- | --- | --- | --- |
| aggregate/entity/value object/events | EzDDD-oriented, mandatory soft delete | portable bases/placeholders; soft delete conditional | aggregate and ES roots; Product deletion has no universal `IsDeleted` | concept preserved; derived rule stale |
| command/query repository separation | three-operation Java repository | async write ports; query ports separated | DBA1001 and project-owned ports | refined and adopted |
| use case/controller | synchronous interface + Service | async use-case/handler rule; stale synchronous example | explicit `ExecuteAsync`; DBA1015/1017 | rule refined; example stale |
| projection/archive/reactor/outbox | Java/Spring implementations | portable patterns with TODO types | Dapper read models, Wolverine adapters, durable outbox/inbox | concepts preserved |
| profiles/persistence | Spring profiles/JPA | environment policy plus conflicting copied modes; EF/Dapper references | target selects Dapper and environment/config truth | source topology not canonical |
| tests/contracts | ezSpec/uContract | BDDfy/Reqnroll and contract placeholders | target selects xUnit/Moq/Shouldly | test intent preserved; package/API default unresolved |

## 8. Inbound Reference And Enforcement Matrix

| Surface | Linked | Skill-routed | Validator | Framework workflow | Downstream adoption | Assessment |
| --- | --- | --- | --- | --- | --- | --- |
| governance policies | strong | strong | structural/machine contracts | strong | target reconciliation workflows | retain |
| focused coding standards | local + selective direct | strong | structural; selected Roslyn rules | strong | aggregate/use-case standards explicitly cited | retain; clarify strengths |
| project structure | selective | architecture skill | no semantic validator | current alignment history | solution/manifests match | retain/promote conditional profile |
| examples | uneven local indexes | selective | no build/semantic validation | selected sync workflows | zero downstream workflow references | tier/consolidate |
| AI scripts | README/runner | selected skills | registry/mode/runner parity | strong for quick gate | orchestrators/validators used; analyzers replace selected grep checks | classify lifecycle |
| canonical skills/wrappers | strong indexes | root runtime routing | schema/parity | strong | copied and reconciled | retain |
| weak guides/rationales | weak/omitted catalogs | little | none | selective/historical | no decisive evidence | decision-required |

## 9. Usage Evidence Matrix

| Candidate | Exists/linked | Provenance | Framework workflow | Downstream evidence | Classification |
| --- | --- | --- | --- | --- | --- |
| aggregate/usecase standards | yes | direct Java conversion and later refinement | analyzer/alignment workflows | explicit task specifications and build analyzers | `active-canonical`, `downstream-adopted` |
| project-structure standard | yes | .NET refinement | routed by architecture skills | lab solution and architecture match | conditional canonical strength |
| examples tree | yes, uneven | direct conversion | selected synchronization history | copied at `e8e3f85`; no example workflow refs or adaptation commits | mixed example/reference only |
| `.versions.json` | exists, unlinked | real Java source-sync ancestor | none after initial snapshot | copied unchanged | stale provenance metadata |
| controller example | linked | synchronous Java lineage | inconsistency previously recorded | conflicts with target async ports/analyzers | stale |
| BDD families | linked | explicit BDDfy plus retained Gherkin migration decisions | normalization history | target selects separate test truth | retain modes; merge shared fixtures |
| quick gate/context/workflow validators | strongly linked | evolved from scripts | repeated | validated in lab workflows | active/enforced |
| repository grep check | removed but still referenced | existed in Java source | replacement history | DBA1001 integrated into product builds | broken active route |

No evidence class establishes whether a particular AI session read a file.

## 10. Duplicate, Stale And Orphan Candidates

### Duplicate Or Merge Candidates

- exact duplicate outbox test configuration documents and two pairs of shared test fixtures;
- duplicate ASP.NET in-memory configuration files;
- three overlapping example discovery surfaces: README, INDEX, and source-mirror TEMPLATE-INDEX;
- broad best-practice prose that restates focused canonical standards.

### Stale Or Rewrite Candidates

- [`.versions.json`](../../standards/examples/.versions.json): original Java metadata tracked real product files; current single entry points to absent `src/Domain/Plan/Plan.cs`;
- [profile templates/examples](../../standards/examples/profile-configs/README.md): converted Spring-profile topology conflicts with current environment-only ownership;
- [`CreateTaskController.cs`](../../standards/examples/controller/CreateTaskController.cs): synchronous Java-shaped contract conflicts with current async rule;
- [`validation-command-templates.md`](../../../.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md): routes to a removed repository check;
- `Lab.MessageSchemas.<Domain>` in canonical structure guidance;
- verification/SSOT language inherited from Java source despite TODO and placeholder content.

### Weak-Routing Or Decision Candidates

- REST resource-path rationale, multi-stack placement notes, persistence guide, selected example subfolders;
- EzDDD import mapping and uContract material after portable concepts are extracted;
- AiPlan/Plan/Task/Tag source-domain fixtures that add no distinct teaching value.

Weak routing is not evidence of non-use and is not a deletion criterion.

## 11. Example Folder Assessment

| Group | Lineage/adoption evidence | Quality state | Candidate disposition |
| --- | --- | --- | --- |
| aggregate/entity/value object | direct lineage; concepts implemented in lab | placeholders and oversized single-domain examples | retain concepts; replace with small verified slice |
| aspnet/profile/use-case injection | converted profile topology; no lab adoption | canonical conflict | rewrite/merge |
| usecase/controller | lineage + workflow evidence; async target adoption | usecase useful, controller stale | align and verify |
| projection/archive/reactor/outbox/mapper | concepts realized downstream | illustrative/TODO-bearing | retain as reference; verify a representative slice |
| BDDfy/Gherkin/GWT/test | deliberate dual-mode migration | exact fixture duplication | keep modes; consolidate shared infrastructure |
| contract/reference | source provenance now known | unresolved package/type placeholders | reference/archive after concept extraction |
| generation templates | direct lineage | generation and verification claims unproven | rewrite claim or move to real generator ownership |
| NuGet snapshot | copied reference | package choices target-dependent | convert to default-profile guidance, not invariant |
| root discovery docs | copied competing indexes | incomplete/overlapping | README purpose + one catalog |

The lab should not be copied wholesale into examples. A minimal cross-BC reference slice can prove the desired architecture while avoiding a second product repository inside context.

## 12. Findings

### AIC-001 — Converted Profile Topology Conflicts With Canonical Environment Selection

- Severity: **HIGH**
- Affected paths: `profile-configuration-standards.md`, templates, `examples/aspnet-core/**`, `profile-configs/**`, `use-case-injection/**`
- Repository-native evidence: original Spring profiles explain the topology; current [canonical standard](../../standards/coding-standards/profile-configuration-standards.md) requires `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT`, while converted examples use `Profiles:Mode`, `Repository:Mode`, `Test-InMemory`, and `Test-Outbox`.
- Why it matters: templates can generate mutually incompatible selection mechanisms.
- Confidence: **high**
- Recommended disposition: **rewrite and merge** around one canonical mechanism, with target-owned persistence choices.
- User decision required: **yes** for supported profile variants.

### AIC-002 — Source-Specific Mandatory Soft Delete Survived A Conditionalization

- Severity: **HIGH**
- Affected paths: ownership registry, aggregate standard, focused README, broad checklist
- Repository-native evidence: original Java aggregate standard required `isDeleted` universally; [`DELETE-SOFT-001`](../../standards/AI-CONTEXT-OWNERSHIP.yaml) now applies only when adopted, but derived summaries remain unconditional. The lab test spec retains hard/soft-delete choice and its Product model does not establish a universal property.
- Why it matters: derived guidance can impose source-product architecture on targets.
- Confidence: **high**
- Recommended disposition: **rewrite** summaries/checklists to project conditional ownership.
- User decision required: **no**, unless conditionality itself changes.

### AIC-003 — Converted Examples Retain Unsupported Verification And Source-Sync Claims

- Severity: **HIGH**
- Affected paths: examples README, `.versions.json`, all “verified” groups
- Repository-native evidence: the Java ancestor's verification language and metadata pointed to real `tw/teddysoft/aiplan` source; current metadata has one absent .NET source path, examples have no compilation fixture, and green framework/downstream validators do not inspect semantic currency.
- Why it matters: agents can treat illustrative or placeholder material as executable truth.
- Confidence: **high**
- Recommended disposition: define verification tiers; **replace or delete** stale sync metadata.
- User decision required: **yes**, runnable fixtures versus explicit illustrative/reference tiers.

### AIC-004 — Active Skill Routes To A Removed Validator Despite A Working Replacement

- Severity: **HIGH**
- Affected path: `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`
- Repository-native evidence: `check-repository-compliance.sh` existed in `f7ed0b9` but is absent now; transition records and the lab analyzer README identify DBA1001 as its replacement, integrated at `fd80fb7`.
- Why it matters: current skill execution fails even though the replacement is operational.
- Confidence: **high**
- Recommended disposition: **rewrite** active command routing.
- User decision required: **no** unless the replacement contract is redesigned.

### AIC-005 — Portable Concepts Are Traceable But Framework Examples Still Contain Unresolved APIs

- Severity: **HIGH**
- Affected paths: examples for contract, aggregate, usecase, outbox, mapper, tests, and EzDDD mapping
- Repository-native evidence: Java-to-.NET mapping and staged conversion commits establish broad concept preservation; the lab realizes the core architecture without EzDDD. Current example files still declare placeholder namespaces/types, TODO replacements, and state that uContract has no .NET equivalent.
- Why it matters: preserving placeholders as active examples can generate invalid code, while deleting them before concept extraction loses migration rationale.
- Confidence: **high**
- Recommended disposition: **rewrite/reference/archive** based on a concept-to-owner-to-downstream matrix.
- User decision required: **yes** for uContract/EzDDD vocabulary and DateProvider/TimeProvider direction.

### AIC-006 — Example Duplication And Competing Indexes Increase Maintenance Cost

- Severity: **MEDIUM**
- Affected paths: duplicate fixtures/configs; examples README, INDEX, TEMPLATE-INDEX
- Repository-native evidence: four exact duplicate groups and three overlapping catalogs; BDDfy and Gherkin were intentionally retained as distinct modes in migration commits.
- Why it matters: shared material drifts, while indiscriminate consolidation would erase deliberate test modes.
- Confidence: **high**
- Recommended disposition: **merge shared fixtures/navigation**, retain distinct modes with explicit routing.
- User decision required: **yes** for physical consolidation.

### AIC-007 — Standards Placement And Routing Retain Source-Package Topology

- Severity: **MEDIUM**
- Affected paths: standards README, nested guides/prompts, selected catalogs/rationales
- Repository-native evidence: Java tech-stack packaging explains co-location; current boundary policy places human guides under `.dev/guides` and canonical prompts under `.ai`; the lab's README-purpose/INDEX-catalog model demonstrates cleaner routing.
- Why it matters: normative, tutorial, migration, and reference content compete for context.
- Confidence: **high**
- Recommended disposition: **move and retain** useful content; archive/delete only after comparison.
- User decision required: **yes**.

### AIC-008 — Structural Standards Validator Overstates Semantic Coverage

- Severity: **MEDIUM**
- Affected paths: `check-coding-standards.sh`, `check-all.sh`, scripts README
- Repository-native evidence: inherited “complete and well-organized” wording covers existence/shape of a subset; framework and lab gates pass while AIC-001 through AIC-004 remain. Examples and some focused standards are outside semantic validation.
- Why it matters: green output can be mistaken for architecture completeness.
- Confidence: **high**
- Recommended disposition: rename output to **structural integrity** and state exclusions; optionally add relationship checks.
- User decision required: **no** for wording; **yes** for expanded scope.

### AIC-009 — Shell Lifecycle Registry Conflates Retention With Endorsement

- Severity: **MEDIUM**
- Affected paths: shell registry, scripts README, grep checks, runners
- Repository-native evidence: all 14 shell assets are `retained` and none are retirement candidates; downstream workflows actively use runners/context validators while source-included Roslyn analyzers replace selected grep checks.
- Why it matters: packaging, execution, advisory compatibility, transition, and long-term ownership require different decisions.
- Confidence: **high**
- Recommended disposition: classify active-orchestrator, context-validator, manual-advisory, transitional, and retirement-candidate separately.
- User decision required: **yes** for compatibility and retirement timing.

### AIC-010 — Synchronous Controller Example Contradicts Current Async Use-Case Rules

- Severity: **MEDIUM**
- Affected path: `examples/controller/CreateTaskController.cs`
- Repository-native evidence: direct synchronous Java lineage remains as `_createTaskUseCase.Execute(input)`; current controller/use-case standards and downstream explicit ports/DBA1015 require async execution.
- Why it matters: copy/paste or retrieval reintroduces a prohibited contract.
- Confidence: **high**
- Recommended disposition: **rewrite** and include it in a verified slice, or archive as migration history.
- User decision required: **no** for alignment.

### AIC-011 — Coherent But Weakly Routed References Need Explicit Disposition

- Severity: **LOW**
- Affected paths: REST rationale, multi-stack placement notes, persistence guide, selected example groups
- Repository-native evidence: catalog omissions or no active inbound filename routes; neither external repository proves content invalidity or non-use.
- Why it matters: unrouteable context has maintenance cost without predictable consumption.
- Confidence: **high** on routing gap; **medium** on disposition.
- Recommended disposition: **link, move/archive, or delete after comparison**.
- User decision required: **yes**.

### AIC-012 — Target-Specific Namespace Appears In Canonical Structure Guidance

- Severity: **MEDIUM**
- Affected path: `.dev/standards/coding-standards.md`
- Repository-native evidence: `Lab.MessageSchemas.<Domain>` appears in broad canonical guidance while [`project-structure.md`](../../standards/project-structure.md) uses the portable `<Company>.BoundedContextContracts.<Domain>` shape.
- Why it matters: a source/target name can leak into generated repositories as framework truth.
- Confidence: **high**
- Recommended disposition: **rewrite** to the canonical placeholder or link to the owner.
- User decision required: **no**, unless `Lab.*` is intentionally the default.

### AIC-013 — Conditional Technology Guidance Is Restated As Mandatory Policy

- Severity: **HIGH**
- Affected paths: standards README, focused README, `test-standards.md`, NuGet references, ownership registry
- Repository-native evidence: root guidance frames NSubstitute, EF Core, and Wolverine as target-selected/conditional; focused test standards prohibit Moq and mandate NSubstitute. The lab's target-owned requirement explicitly selects xUnit, Moq, and Shouldly and says not to infer NSubstitute.
- Why it matters: portable context can overwrite legitimate target truth during initialization or upgrade.
- Confidence: **high**
- Recommended disposition: define and project four strengths: framework invariant, default profile, target-selected option, and target override.
- User decision required: **yes**, especially whether NSubstitute is a default or invariant.

### AIC-014 — Example Portfolio Does Not Demonstrate The Canonical Multi-BC Architecture

- Severity: **MEDIUM**
- Affected paths: project-structure standard and the Plan/Task-centered examples portfolio
- Repository-native evidence: the canonical standard specifies multi-BC contracts, building blocks, per-context DomainCore/Presentation, and MQ integration; the lab implements Products/Orders/Inventory in that shape. Current examples remain local patterns from a single source-product domain.
- Why it matters: the strongest canonical architecture lacks a compact verified teaching path, while a large lower-value portfolio consumes routing budget.
- Confidence: **high**
- Recommended disposition: add one minimal verified cross-BC reference slice or explicitly declare the portfolio a local-pattern library; do not copy the lab wholesale.
- User decision required: **yes**.

## 13. v0.4.0 Candidate Actions

| Action | Candidates |
| --- | --- |
| Retain | governance spine; focused portable concepts; multi-BC project structure; distinct BDDfy/Gherkin modes; active runners/validators |
| Merge | shared test fixtures/configs; example catalogs; repeated broad summaries; profile examples after truth selection |
| Rewrite | profile selection, soft-delete projections, verification claims, removed command, controller, validator wording, namespace, technology strengths |
| Move | human guides to `.dev/guides`; retained migration references to an explicit reference/archive surface |
| Archive | EzDDD/uContract import mappings after concept extraction; source-product Plan/Task fixtures with only provenance value; obsolete prompt bodies |
| Delete | stale `.versions.json`, exact duplicates after consolidation, superseded catalogs/prompts only after replacement links exist |

Priority is reduced context routing and ownership ambiguity, not deletion count.

## 14. Decisions Required From Me

1. Should examples become buildable/test-executed fixtures, or be explicitly tiered as illustrative/reference-only?
2. Which package choices are framework defaults versus invariants, especially NSubstitute/Moq, EF/Dapper, and Wolverine?
3. Should uContract/EzDDD names remain migration vocabulary, become portable abstractions, or be archived after concept extraction?
4. Should the minimal multi-BC reference be a runnable cross-BC slice or only a documented topology?
5. Which shell compatibility assets must ship in v0.4.0, and on what retirement horizon?
6. Should DateProvider remain a framework abstraction or converge on `TimeProvider`?
7. Which weakly routed rationales/guides should be linked, archived, or removed after comparison?

## 15. Deferred Or Unverifiable Items

- Line-by-line Java-to-.NET semantic equivalence was not claimed; structural lineage and concept families are established.
- The lab proves downstream realization, not universal suitability or example adoption.
- No session-log absence was used to claim a file was never read.
- Example compilation remains unverified because the framework example tree has no declared project fixture.
- Package-version currency was not researched; target package choice was read only from repository truth.
- External product source/test code quality remained excluded.
- The current-checkout original-repo graph cannot represent immutable `f7ed0b9`; Git-tree evidence is authoritative.

## 16. Recommended Remediation Slices

After user selection, `ai-context-governance` should create one remediation workflow with bounded slices:

1. applicability/ownership model: AIC-002, AIC-013;
2. active truth conflicts: AIC-001, AIC-004, AIC-010, AIC-012;
3. example contract and verified cross-BC slice: AIC-003, AIC-014;
4. lineage extraction and placeholder disposition: AIC-005;
5. example discovery/shared-fixture consolidation: AIC-006;
6. placement and weak-route cleanup: AIC-007, AIC-011;
7. validator and script lifecycle truth: AIC-008, AIC-009;
8. independent successor verification assessment.

Use stable references `ASM-20260715-002#AIC-001` through `ASM-20260715-002#AIC-014`. Do not copy this report into workflow truth.

## Validation

| Check | Result | Notes |
| --- | --- | --- |
| framework release baseline | pass | `main`/`origin/main` `82b88b7`; v0.3.0 annotated tag peels to `1e78290` |
| original Git tree | pass | `f7ed0b9` exists; read via immutable Git object; no checkout mutation |
| downstream state | pass | clean `main`/`origin/main` at `0f71e5c` |
| graph limitation fallback | pass | hidden-tree inventories verified with Git and `rg -uu` |
| downstream context validator | pass | 8 indexes, 13 canonical skills, two runtime roots |
| downstream workflow validator | pass | 3 post-adoption workflows, 5 indexed workflow directories |
| downstream shell validator | pass | 14 retained, zero retirement candidates |
| downstream example workflow scan | pass | 8 workflow files reference standards; zero reference examples paths |
| framework assessment validation | pass | two locators/index rows valid; 9/9 fail-closed tests passed |
| framework quick gate | pass | all required checks passed; one Windows symlink test skipped because the privilege is unavailable |

## Appendix A — Pinned Evidence And Commands

```text
framework: C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend@82b88b7287deb7a64e0311fde6b1b53ea0d194b1
origin: <local-source-checkout>/ai-coding-exercise@f7ed0b9b5b23822ec012c375261df44f6f03a97f
downstream: C:/Github/YuChia/dotnet-mq-arch-lab@0f71e5ca694ceadacf7616a72805a14b2eef2309

git ls-tree -r --name-only <pinned-commit>
git show <pinned-commit>:<path>
git grep <pattern> <pinned-commit>
git log --all -- <path>
git ls-files
rg -n -uu <targeted patterns>
codebase-memory-mcp full index (exploration only)
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-workflow-artifacts.py
python .ai/scripts/validate-shell-assets.py
```

## Appendix B — Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260715-002/report.md`
- Supersedes: `ASM-20260715-001`
- Stable finding references: `ASM-20260715-002#AIC-001` through `ASM-20260715-002#AIC-014`
- Remediation owner after authorization: `ai-context-governance`
- Related remediation workflow: none
- Remediation intentionally not performed: **yes**
