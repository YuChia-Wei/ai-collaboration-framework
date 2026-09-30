# v0.4.0 Standards, Examples, And Script Usage Assessment

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260715-001`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-15`
- `created_at`: `2026-07-15T21:25:18+08:00`
- `updated_at`: `2026-07-15T21:25:18+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `82b88b7287deb7a64e0311fde6b1b53ea0d194b1`
- `artifact_branch`: `codex/assessment/asm-20260715-001`
- `previous_assessment`: none
- `workflow_refs`: none; this is a standalone durable assessment

## 1. Executive Summary

The standards and runtime-routing spine is healthy enough to support v0.4.0 planning, but the examples and transitional script surfaces are not yet reliable enough to be presented as uniformly current or verified. The repository has strong canonical governance, wrapper parity, workflow evidence, and deterministic structural validators. The main risk is not missing files; it is that derived summaries, templates, examples, and validator success messages sometimes express stronger or different truth than their canonical owners.

- Overall score: **7.1/10**
- Decision: **remediation-recommended**
- Primary strengths:
  - root routing, canonical skill registry, and both runtime wrapper inventories are coherent;
  - governance policies have direct routing and machine-readable enforcement;
  - core .NET standards have real workflow and analyzer evolution evidence;
  - examples have been maintained in several workflows, disproving the hypothesis that the whole tree is unused.
- Primary risks:
  - profile/environment examples directly contradict the canonical profile standard;
  - conditional soft-delete policy is restated as unconditional in active summaries;
  - “Verified Templates (Single Source of Truth)” is unsupported by compilation or semantic validation;
  - EzDDD/uContract intent is preserved, but working .NET realization and original Java-source equivalence are incomplete or unverifiable;
  - transitional shell registry, documentation, and active command routing disagree about lifecycle state.

The correct v0.4.0 objective is to reduce routing and maintenance cost by clarifying ownership and verification tiers. A blanket deletion of `.dev/standards/examples/` is not supported.

## 2. Scope And Exclusions

### Included

- [`.dev/standards/**`](../../standards/README.md), including all examples, rationales, templates, prompts, and nested guides;
- [`.dev/guides/**`](../../guides/README.MD);
- [`.ai/scripts/**`](../../../.ai/scripts/README.md);
- [`.ai/assets/skills/**`](../../../.ai/assets/skills/README.MD);
- [`.agents/skills/**`](../../../.agents/skills/README.md) and [`.claude/skills/**`](../../../.claude/skills/README.md);
- [`AGENTS.md`](../../../AGENTS.md) and [`CLAUDE.md`](../../../CLAUDE.md);
- standards-related validators, workflow artifacts, indexes, and Git history;
- `tools/**` only where analyzer or validation projects provide enforcement evidence.

### Excluded

- `src/**`, `tests/**`, product `test/**`, and `docker-compose/**`;
- `bin/**`, `obj/**`, generated output, dependencies, and unrelated product implementation;
- GitHub Release verification, as explicitly excluded by the user;
- any tag mutation, release mutation, remediation, or v0.4.0 workflow creation.

The C# files under `.dev/standards/examples/**` were assessed as context artifacts, not as product code. The only repository projects treated as enforcement evidence were the intentional validator/analyzer projects under `tools/**`.

## 3. Evidence And Method

The assessment used two deliberately separated passes.

1. Pass A used general knowledge-base, documentation architecture, validation, and maintenance principles without using skill conclusions as the rubric.
2. Pass B applied `ai-context-auditor`, its evidence contract, the repository assessment policy, and the placement/routing rules required by `ai-context-governance`.
3. Three read-only sub-agents inventoried standards/examples, routing, and enforcement/Git/workflow evidence. The primary agent reopened and verified all high-severity evidence.
4. Repository-native evidence was authoritative: tracked files, literal links, direct file content, Git history, and deterministic validators.

### Discovery Accelerators

| Tool / view | Subject revision | Freshness | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory-mcp full index | working tree at `82b88b7` | refreshed at audit start; tree clean | 10,002 nodes / 13,461 edges; explicitly excluded `.claude`, caches, and build output | complete hidden-file inventory, Markdown link edges, actual AI reads, semantic completeness | `rg -uu`, `git ls-files`, direct reads, Git history, validators |
| PowerShell inventories | working tree at `82b88b7` | live | requested allowlist | semantic use and actual AI reads | direct file review and Git evidence |

The graph exposed useful C# relationships inside examples and `tools/**`, but a File-node query returned no hidden-document rows and the index reported `.claude` as excluded. It was therefore not used to establish completeness or absence.

### Evidence Class Definitions

| Class | Meaning in this report |
| --- | --- |
| Exists | Tracked or directly present at the assessed revision. |
| Linked | An active repository document contains a resolvable inbound path or Markdown link. |
| Skill-navigated | A canonical skill or runtime wrapper directs an agent to the surface. |
| Validator-enforced | A deterministic validator checks an explicit part of the contract. |
| Workflow-evidenced | A retained workflow records a concrete use, change, or validation action. |
| Possible AI reading | Cannot be proven or disproven from repository evidence; never inferred from missing session logs. |

## 4. Baseline Analysis Without Skill

### Strengths

- [`AGENTS.md`](../../../AGENTS.md) establishes a clear root precedence and routing spine; [`CLAUDE.md`](../../../CLAUDE.md) remains a thin import rather than a second owner.
- Fourteen canonical skill specs match fourteen `.agents` wrappers and fourteen `.claude` wrappers.
- Governance standards are directly routed and have machine-readable counterparts where appropriate.
- Core .NET standard families have coherent local navigation and substantial Git/workflow maintenance history.
- Current example content is .NET-shaped; the primary concern is maturity and semantic drift, not an active Java implementation tree.

### Baseline Risks

- Active derived content sometimes contradicts canonical rules, especially profile selection and soft deletion.
- Examples are labeled more strongly than their validation supports.
- Several exact duplicate fixtures and competing indexes increase maintenance cost.
- Human guides and migration-only prompt bodies remain nested under the normative standards root despite its own placement rules.
- Shell assets are all registry-retained even though the script README assigns several to replacement or retirement directions.
- The Git history begins with an already-transformed .NET context snapshot, so original Java-document coverage cannot be established by a line-by-line provenance comparison.

## 5. Skill-Assisted Analysis

The formal pass applied:

- [`ai-context-auditor`](../../../.ai/assets/skills/ai-context-auditor/skill.yaml), including its scope, evidence, persistence, and comparison contracts;
- [`AI-CONTEXT-BOUNDARY.md`](../../standards/AI-CONTEXT-BOUNDARY.md), especially `AICTX-EVIDENCE-001`;
- [`AI-CONTEXT-LANGUAGE-POLICY.md`](../../standards/AI-CONTEXT-LANGUAGE-POLICY.md);
- [`AI-CONTEXT-OWNERSHIP.md`](../../standards/AI-CONTEXT-OWNERSHIP.md) and its [registry](../../standards/AI-CONTEXT-OWNERSHIP.yaml);
- the placement and audit-lifecycle lenses from `ai-context-governance` without authorizing remediation.

The skill pass confirmed that the root skill/wrapper model is healthy and that weak direct inbound counts do not by themselves make locally indexed standards orphaned. It added stronger findings where repository policy makes a mismatch actionable: derived examples and checklists must not become second normative owners; human guides should live under `.dev/guides/`; and optional graph output cannot prove hidden-tree completeness.

## 6. Comparison Between Both Passes

### Confirmed

- profile/environment truth is inconsistent across canonical standards, templates, and examples;
- soft-delete applicability is weakened in derived summaries/checklists;
- example verification claims exceed executable evidence;
- EzDDD/uContract preservation is incomplete as a working .NET realization;
- duplicate and competing example discovery surfaces add maintenance cost;
- transitional scripts have lifecycle and routing drift.

### Added By The Skill-Assisted Pass

- placement of `.dev/standards/guides/` and migration-only `.dev/standards/prompts/` violates the repository's folder-first governance model;
- the standards README is not a complete lookup surface even though a skill calls it the lookup index;
- graph omissions must be documented as a tool limitation, not interpreted as missing files;
- examples and checklists repeating `MUST` language can create a second normative owner even when canonical ownership is otherwise clear.

### Downgraded Or Deferred

- low inbound counts for focused coding standards were downgraded from possible orphaning to `reference-only`, because the local coding-standards README provides a valid navigation path;
- parallel `.agents` and `.claude` wrappers were not classified as duplicated canonical truth because they are intentional thin runtime projections;
- `inquiry-archive` was not classified as stale solely because of its name; current archive standards and workflow evidence still route to it.

### Overturned

- the hypothesis that `.dev/standards/examples/` as a whole is unused or deletion-ready was overturned by active index links and multiple synchronization workflows.

## 7. Standards Inventory

The assessed standards tree contains **182 files** and approximately **507 KB**.

| Area | Files | Primary role | Current classification |
| --- | ---: | --- | --- |
| Root standards | 19 | governance, entry standards, checklists, broad .NET guidance | mostly `active-canonical`; selected legacy/reference files need reclassification |
| `coding-standards/` | 11 | focused .NET coding rules and local index | `active-canonical`, partly `validator-enforced` |
| `rationale/` | 6 | design rationale | `reference-only`; one orphan candidate |
| `guides/` | 4 | human setup/how-to guides | content may be useful; placement is stale |
| `prompts/` | 3 | legacy prompt bodies | `stale` / migration-only / duplicated ownership risk |
| `templates/` | 3 | configuration templates | `reference-only`, with profile contradictions |
| `examples/` | 136 | illustrative C#, configuration, test, and reference material | mixed `example-only`, `reference-only`, `workflow-evidenced`, `stale`, and `decision-required` |

### Root And Focused Standard Classification

| Surface | Classification | Basis |
| --- | --- | --- |
| AI context boundary, language, ownership, version, assessment, workflow, and Git policies | `active-canonical`, `routing-required`, several `validator-enforced` | direct AGENTS/skill routing and machine contracts |
| `coding-standards.md` and focused standards | `active-canonical`, `routing-required`, partly `validator-enforced` | local index, skills, analyzer/workflow evidence |
| `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` | `active-canonical`, `skill-navigated`, `workflow-evidenced` | slice modes and July alignment workflow |
| `project-structure.md` | `active-canonical` conditional profile | direct skill navigation and policy text |
| `CODE-REVIEW-CHECKLIST.md` and ASP.NET checklist | `routing-required`, derived checklist | code-review/root routing; not independent normative owners |
| `best-practices.md`, `anti-patterns.md` | `reference-only`, possible `duplicated` | broad overlap with focused standards and weaker conditional framing |
| `coding-guide.md` | `historical/reference-only` | explicitly labeled legacy |

## 8. Inbound Reference And Enforcement Matrix

| Surface | Exists | Linked | Skill-navigated | Validator-enforced | Workflow-evidenced | Assessment |
| --- | --- | --- | --- | --- | --- | --- |
| Governance policies | yes | strong | strong | structural/machine contracts | strong | retain |
| Focused coding standards | yes | local index + selective direct links | strong for architecture/review/slices | eight-file structure check; analyzer coverage varies | strong | retain; correct drift |
| Profile/reactor focused standards | yes | local index | selective | omitted from eight-file integrity array | workflow evidence varies | retain; improve enforcement description |
| Standards examples | yes | category/local links, uneven | selective | no semantic/build validation | strong for some folders | tier and consolidate |
| Standards rationales | yes | uneven | selective | no | selective | retain routed items; decide orphan |
| Standards nested guides/prompts/templates | yes | weak/uneven | prompts referenced by historical workflows | no | mostly historical | move/archive/rewrite candidates |
| AI scripts | yes | README + runner/guide links | validator skill routes to selected scripts | registry/mode/runner parity | strong for runner; uneven per script | classify lifecycle precisely |
| Canonical skill specs | yes | canonical registry | root routing | schema and wrapper parity | strong | retain |
| Runtime wrappers | yes | wrapper indexes | runtime entry | parity/metadata validation | strong | retain as thin projections |
| Root AGENTS/CLAUDE | yes | direct | mandatory | structural parity for root entries | strong | retain |

## 9. Usage Evidence Matrix

| Candidate surface | Link evidence | Validator evidence | Workflow/Git evidence | Usage conclusion |
| --- | --- | --- | --- | --- |
| `examples/usecase/` | index and standards links | none semantic | commit `75041dd`; July use-case workflow | `workflow-evidenced`, but placeholder-bearing |
| `examples/controller/` | index/standard links | analyzer validates production patterns, not example file | July use-case review found inconsistency | used as reference; current example stale |
| `examples/outbox/` | guide, standards, code-review reference links | no example compilation | repository-alignment workflow | strong reference path; tier as illustrative |
| `examples/inquiry-archive/` | index and archive standard links | no example compilation | commit `64100e0` and alignment workflow | not orphaned; terminology decision remains |
| BDD/test example families | test standard and indexes | no compilation contract | historical normalization | overlapping, partly duplicated |
| `examples/contract/`, `profile-configs/`, `generation-templates/`, `reference/` | mainly local README/index | none semantic | weak or historical | `reference-only` / `decision-required` |
| `.versions.json` | no inbound reference | none | only initial `92b02d5` history | stale metadata candidate |
| core governance validators | direct README/runner references | required in quick gate | repeated workflow execution | active and enforced |
| retained C# grep scripts | sparse active references | registry enforces retention, not semantic authority | transition workflows document replacement direction | transitional/manual; lifecycle unclear |

No conclusion about actual AI reading is made. Repository evidence can show a plausible route or a recorded workflow action, not whether a particular session loaded a file.

## 10. Duplicate, Stale And Orphan Candidates

### Exact Duplicates

- [`bdd-gherkin-example/OUTBOX-TEST-CONFIGURATION.md`](../../standards/examples/bdd-gherkin-example/OUTBOX-TEST-CONFIGURATION.md) and [`bdd-given-when-then-example/OUTBOX-TEST-CONFIGURATION.md`](../../standards/examples/bdd-given-when-then-example/OUTBOX-TEST-CONFIGURATION.md);
- `bdd-gherkin-test/TestHostFixture.cs` and `test/TestHostFixture.cs`;
- `bdd-gherkin-test/UseCaseTestFixture.cs` and `test/UseCaseTestFixture.cs`;
- `aspnet-core/appsettings.InMemory.json` and `aspnet-core/appsettings.Test.InMemory.json`.

### Stale Or Misleading

- [`.versions.json`](../../standards/examples/.versions.json) claims a sync to absent `src/Domain/Plan/Plan.cs` and has no validator or inbound consumer;
- [`TEMPLATE-INDEX.md`](../../standards/examples/TEMPLATE-INDEX.md) mirrors a source template index and overlaps the current category index;
- [`reference/nuget-dependencies.md`](../../standards/examples/reference/nuget-dependencies.md) lists Moq despite the current prohibition;
- [`CreateTaskController.cs`](../../standards/examples/controller/CreateTaskController.cs) uses a synchronous contract inconsistent with current async use-case/controller rules;
- profile templates/examples use `Profiles:Mode`, `Repository:Mode`, and hyphenated environment names that conflict with the canonical environment-only policy;
- [`validation-command-templates.md`](../../../.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md) points to removed `check-repository-compliance.sh`.

### Orphan Or Weak-Routing Candidates

- [`rest-api-resource-path-rationale.MD`](../../standards/rationale/rest-api-resource-path-rationale.MD): coherent content, no active inbound filename reference;
- [`MULTI-STACK-CONTEXT-PLACEMENT-NOTES.md`](../../guides/design-guides/MULTI-STACK-CONTEXT-PLACEMENT-NOTES.md): exploration content omitted from local guide catalog;
- [`PERSISTENCE-CONFIGURATION-GUIDE.md`](../../../src/knowledge/dotnet-backend/guides/PERSISTENCE-CONFIGURATION-GUIDE.md): no active inbound route found;
- selected example subfolders that depend only on local README/index navigation.

These are decision candidates, not automatic deletion candidates.

## 11. Example Folder Assessment

| Example group | Evidence | Quality state | v0.4.0 disposition candidate |
| --- | --- | --- | --- |
| aggregate | substantial and graph-readable | placeholder-heavy | retain concepts; rewrite verification label |
| aspnet-core / profile-configs / use-case-injection | routed | conflicts with profile standard | rewrite/merge first |
| usecase / controller | workflow-evidenced | usecase maintained; controller stale | retain and align |
| outbox / mapper / projection / inquiry-archive | standards/workflow links | useful but not compiled; some placeholders | retain as illustrative/reference tiers |
| test / bdd-gherkin-test / bdd-gherkin-example / bdd-given-when-then-example | multiple routes | overlapping and exact duplicates | consolidate by test mode |
| contract / reference | conceptual migration material | unresolved uContract/EzDDD names | mark reference-only or archive after concept matrix |
| generation-templates | local routing | “used for generation” unproven; placeholders | rewrite claim; decide whether true generators belong elsewhere |
| nuget | local routing | version snapshot not build-attached | move to reference or validate through a fixture project |
| root examples docs | competing README/INDEX/TEMPLATE-INDEX | duplicated navigation | keep README purpose + one complete index |

The folder should not be judged by file count. A smaller, tiered surface with explicit `runnable`, `validated-structure`, `illustrative`, `reference-only`, and `historical` labels would reduce agent ambiguity more than indiscriminate deletion.

## 12. Findings

### AIC-001 — Profile Selection Truth Conflicts Across Active Surfaces

- Severity: **HIGH**
- Affected paths: `profile-configuration-standards.md`, `templates/*.md`, `examples/aspnet-core/**`, `examples/profile-configs/**`, `examples/use-case-injection/**`
- Repository-native evidence: the [canonical profile standard](../../standards/coding-standards/profile-configuration-standards.md) requires only `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` and names `TestInMemory` / `TestOutbox`; templates and examples use `Profiles:Mode`, `Repository:Mode`, `Test-InMemory`, and `Test-Outbox`.
- Why it matters: agents can generate incompatible configuration branches from a surface presented as a template.
- Confidence: **high**
- Recommended disposition: **rewrite and merge** around the canonical environment-only model.
- User decision required: **yes**, for final template/example placement; not for recognizing the conflict.

### AIC-002 — Conditional Soft Deletion Becomes Unconditional In Derived Guidance

- Severity: **HIGH**
- Affected paths: `AI-CONTEXT-OWNERSHIP.yaml`, `coding-standards/aggregate-standards.md`, `coding-standards/README.md`, `coding-standards.md`
- Repository-native evidence: [`DELETE-SOFT-001`](../../standards/AI-CONTEXT-OWNERSHIP.yaml) applies only when a target adopts aggregate soft deletion; the [coding-standards README](../../standards/coding-standards/README.md) says every aggregate must support `IsDeleted`, and the aggregate checklist remains unqualified.
- Why it matters: a summary or checklist can impose a stricter architecture than the canonical owner and target evidence allow.
- Confidence: **high**
- Recommended disposition: **rewrite** derived summaries/checklists; retain the canonical conditional rule.
- User decision required: **no** for semantic alignment; **yes** only if the canonical conditionality itself is reconsidered.

### AIC-003 — Example Verification Claims Exceed Available Evidence

- Severity: **HIGH**
- Affected paths: `examples/README.md`, `examples/.versions.json`, all example/template groups named “verified”
- Repository-native evidence: [examples README](../../standards/examples/README.md) says “Verified Templates (Single Source of Truth)”; no example `.csproj` or semantic validator exists; [`.versions.json`](../../standards/examples/.versions.json) tracks one file against an absent source path and has no inbound consumer.
- Why it matters: agents and maintainers can mistake illustrative snippets for buildable, current contracts.
- Confidence: **high**
- Recommended disposition: **rewrite** verification claims, define verification tiers, then **delete or replace** stale sync metadata.
- User decision required: **yes**, for whether v0.4.0 adds runnable fixtures or explicitly narrows examples to illustrative/reference material.

### AIC-004 — Active Skill Reference Routes To A Removed Validator

- Severity: **HIGH**
- Affected path: `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`
- Repository-native evidence: the active template invokes absent `.ai/scripts/check-repository-compliance.sh`; transition records state that repository validation moved to DBA1001.
- Why it matters: an agent following current skill guidance receives a broken command despite the newer analyzer path existing.
- Confidence: **high**
- Recommended disposition: **rewrite** the active command template to the current analyzer/tool contract.
- User decision required: **no**, unless the intended replacement command is being redesigned.

### AIC-005 — EzDDD/uContract Intent Is Preserved But Coverage Is Incomplete And Provenance Is Insufficient

- Severity: **HIGH**
- Affected paths: standards examples/reference/contract/aggregate/usecase/outbox/test surfaces and selected guides/scripts
- Repository-native evidence: the standards README requires preserving concepts via TODOs; placeholder namespaces and types remain in [`ezddd-import-mapping.md`](../../standards/examples/reference/ezddd-import-mapping.md), `UseCaseContracts.cs`, `OutboxContracts.cs`, aggregate bases, tests, and NuGet comments. Git history begins with an already-adapted .NET snapshot (`92b02d5`), not an original Java corpus.
- Why it matters: deleting residue before mapping concepts could lose intended architecture; presenting placeholders as current APIs can generate invalid .NET code.
- Confidence: **high** for incomplete realization; **medium** for original-concept completeness because the source corpus is absent.
- Recommended disposition: **decision-required**; build a concept coverage/provenance matrix, retain portable concepts in canonical standards, and **archive or rewrite** placeholder import maps.
- User decision required: **yes**.

### AIC-006 — Example Duplication And Competing Indexes Increase Maintenance Cost

- Severity: **MEDIUM**
- Affected paths: duplicate test/config files; `examples/README.md`, `INDEX.md`, `TEMPLATE-INDEX.md`
- Repository-native evidence: four exact SHA-256 duplicate groups; three overlapping discovery surfaces; the current index omits several groups while the older template index mirrors source history.
- Why it matters: fixes must be repeated, and readers cannot reliably identify the current entry point.
- Confidence: **high**
- Recommended disposition: **merge** shared fixtures/docs, keep README for purpose/usage, keep one complete category index, and **archive or delete** `TEMPLATE-INDEX.md` after review.
- User decision required: **yes** for physical consolidation choices.

### AIC-007 — Standards Placement And Routing Do Not Match Folder-First Governance

- Severity: **MEDIUM**
- Affected paths: `.dev/standards/README.md`, `standards/guides/**`, `standards/prompts/**`, selected guide catalogs and rationales
- Repository-native evidence: the standards README says setup guides and prompt guides do not belong there; the boundary policy places human guides under `.dev/guides/`; prompt README already calls its bodies non-canonical migration material; standards README omits active standards while a skill calls it the lookup index.
- Why it matters: normative, human tutorial, migration, and reference material share one routing surface, increasing context selection cost.
- Confidence: **high**
- Recommended disposition: **move/archive** nested guides and legacy prompts, clarify README-versus-index ownership, and add routes for retained rationales/guides.
- User decision required: **yes** for move/archive/delete dispositions.

### AIC-008 — Coding Standards Validator Overstates Its Coverage

- Severity: **MEDIUM**
- Affected paths: `src/tools/dotnet/check-coding-standards.sh`, `.ai/scripts/check-all.sh`, `.ai/scripts/README.md`
- Repository-native evidence: the required script checks the main file plus eight focused standards for existence, headings, links, size, and syntax; it omits examples and the profile/reactor standards, yet reports “complete and well-organized.”
- Why it matters: a green gate can be mistaken for semantic completeness and hide contradictions such as AIC-001 and AIC-002.
- Confidence: **high**
- Recommended disposition: **rewrite** output and documentation to say “structural integrity,” and explicitly list excluded semantic relationships.
- User decision required: **no** for wording accuracy; **yes** if v0.4.0 expands validator scope.

### AIC-009 — Shell Asset Lifecycle Registry Conflicts With Replacement Direction

- Severity: **MEDIUM**
- Affected paths: `.ai/scripts/shell-assets.yaml`, `.ai/scripts/README.md`, retained grep-based checks, `code-review.sh`
- Repository-native evidence: all 14 shell files are `retained` and none are retirement candidates; the README says several must move to Roslyn analyzers, dotnet tools, tests, or CI. Some have only historical or weak active routing.
- Why it matters: `retained` conflates executable packaging/mode retention with long-term architectural endorsement.
- Confidence: **high**
- Recommended disposition: **rewrite** lifecycle taxonomy and classify each script as active-orchestrator, manual-advisory, transitional, or retirement candidate.
- User decision required: **yes**, for retirement timing and compatibility needs.

### AIC-010 — Selected Examples And References Contradict Current .NET Rules

- Severity: **MEDIUM**
- Affected paths: `examples/controller/CreateTaskController.cs`, `examples/reference/nuget-dependencies.md`, profile/config examples
- Repository-native evidence: controller example is synchronous while current controller/use-case rules require async contracts; NuGet reference lists Moq while current test standard prohibits it.
- Why it matters: direct copy/paste or AI retrieval can reintroduce prohibited patterns.
- Confidence: **high**
- Recommended disposition: **rewrite** or **archive** the affected examples after verification-tier decisions.
- User decision required: **no** for aligning current rules; **yes** if retained as explicit negative examples.

### AIC-011 — Coherent But Weakly Routed Reference Material Needs Explicit Disposition

- Severity: **LOW**
- Affected paths: REST path rationale, multi-stack placement notes, persistence configuration guide, selected example subfolders
- Repository-native evidence: no active inbound filename route or omission from the applicable local catalog; content remains coherent enough that absence of links is not deletion evidence.
- Why it matters: unrouteable content costs maintenance without reliably informing agents or humans.
- Confidence: **high** on routing gap; **medium** on final disposition.
- Recommended disposition: **retain and link**, **move/archive**, or **delete after content comparison**.
- User decision required: **yes**.

## 13. v0.4.0 Candidate Actions

| Action | Candidates | Priority rationale |
| --- | --- | --- |
| Retain | canonical governance policies, focused coding standards, root skill/wrapper routing, workflow-evidenced example concepts | stable ownership and real use evidence |
| Merge | duplicate test fixtures/docs, overlapping BDD families, example discovery surfaces, broad best-practice material with focused standards | lowers repeated maintenance |
| Rewrite | profile/config examples, soft-delete summaries, verification claims, removed-validator route, controller/Moq examples, validator success wording | removes active behavioral ambiguity |
| Move | human guides from standards to `.dev/guides/`; reusable agent prompt bodies to canonical `.ai` only if still needed | restores folder-first routing |
| Archive | source-mirror template index, EzDDD import mapping after concept extraction, exploratory notes, obsolete prompt bodies | preserves provenance without active routing |
| Delete | stale `.versions.json`, exact duplicates after consolidation, superseded prompt/index files after content comparison | deletion follows proven replacement, not low reference counts |

## 14. Decisions Required From Me

1. Should v0.4.0 make examples buildable/testable fixtures, or explicitly classify them as illustrative/reference-only?
2. Is aggregate soft deletion intended to remain conditional, as the ownership registry states?
3. Which EzDDD/uContract concepts are strategic framework concepts versus historical source-stack vocabulary?
4. Should transitional shell scripts remain distributable/manual compatibility assets, or should v0.4.0 retire them as their replacements become authoritative?
5. Should `inquiry-archive` remain current terminology, be renamed, or be retained only as a compatibility reference?
6. Should coherent but weakly routed rationales/guides be linked, archived, or removed after comparison?

## 15. Deferred Or Unverifiable Items

- A complete Java-to-.NET semantic parity claim is unverifiable because the original Java document corpus is not present in reachable repository history; the earliest content snapshot is already a .NET adaptation.
- No session-log claim was used. The assessment cannot prove whether any file was ever read by an AI.
- Example compilation was not run because the example tree has no project file or declared compilation fixture.
- Package-version currency was not researched on the internet; this audit evaluates repository claims and routing, not latest package releases.
- Product source/test/container paths remained excluded.
- Historical workflows were used only as evidence of past actions, not as current normative truth.

## 16. Recommended Remediation Slices

After the user selects findings, `ai-context-governance` should create a workflow with bounded slices in this order:

1. **Truth-conflict slice:** AIC-001, AIC-002, AIC-004, and AIC-010.
2. **Example contract slice:** AIC-003 and the verification-tier decision.
3. **EzDDD provenance slice:** AIC-005 concept coverage matrix and disposition.
4. **Example consolidation slice:** AIC-006 and selected AIC-011 routes.
5. **Placement/routing slice:** AIC-007, including README/INDEX ownership.
6. **Validator/lifecycle slice:** AIC-008 and AIC-009.
7. **Independent verification:** a new `ai-context-auditor` assessment linked to this baseline and the remediation workflow.

Each slice should preserve stable references such as `ASM-20260715-001#AIC-001` and must not copy this report into workflow artifacts.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Release baseline | pass | `main` and `origin/main` at `82b88b7`; annotated `v0.3.0` peels to `1e78290` |
| Git state before assessment writes | pass | clean dedicated assessment branch |
| AI context validator | pass | 16 active indexes, 14 canonical skills, two runtime roots, eight owned rules |
| Shell asset validator | pass | 14 retained executable assets, zero retirement candidates |
| Workflow validator | pass | 16 post-adoption workflows, 36 indexed workflow directories, nine backlog items |
| Coding standards integrity check | pass with scope caveat | 2,998 lines checked across main + eight focused files; semantic completeness not tested |
| Wrapper inventory parity | pass | 14 canonical specs, 14 `.agents` wrappers, 14 `.claude` wrappers |
| Markdown relative link scan | pass with parser caveat | no verified missing relative link; six regex false positives were C#-like bracket syntax |
| Exact duplicate scan | findings recorded | four SHA-256 duplicate groups in assessed surfaces |
| Java/EzDDD residue scan | findings recorded | no active Java implementation tree; extensive EzDDD placeholders remain |

## Appendix A — Commands Run

```text
git fetch origin --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git show-ref --dereference --tags v0.3.0
codebase-memory-mcp index_repository (full)
rg --files -uu <included roots>
rg -n -uu <targeted path/reference/residue patterns>
git log --all -- <standards and scripts>
git grep -n -F <candidate paths>
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-shell-assets.py
python .ai/scripts/validate-workflow-artifacts.py
C:/Program Files/Git/bin/bash.exe ./src/tools/dotnet/check-coding-standards.sh
```

## Appendix B — Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260715-001/report.md`
- Stable finding references: `ASM-20260715-001#AIC-001` through `ASM-20260715-001#AIC-011`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: none
- Verification assessment: none
- Remediation intentionally not performed by this skill: **yes**
