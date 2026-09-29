# v0.4.0 AI Context Remediation Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260716-001`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-16`
- `created_at`: `2026-07-16T23:10:20+08:00`
- `updated_at`: `2026-07-16T23:10:20+08:00`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `codex/2026-07-16-v0-4-0-ai-context-remediation`
- `subject_commit`: `e7ca51a7f03c114d5ce5826a15eeb15338efea76`
- `artifact_branch`: `codex/assessment/asm-20260716-001`
- `related_assessment`: [`ASM-20260715-002`](../ASM-20260715-002/report.md)
- `workflow_ref`: [`2026-07-16-v0-4-0-ai-context-remediation`](../../workflows/2026-07-16-v0-4-0-ai-context-remediation/workflow.yaml)

## 1. Executive Summary

This assessment independently verifies the remediation applied for
[`ASM-20260715-002`](../ASM-20260715-002/report.md). It does not modify the
assessed surfaces.

- Overall score: **7.6/10**
- Decision: **remediation-recommended; not release-ready**
- Ten baseline findings are resolved.
- Three baseline findings are only partially resolved: `AIC-001`, `AIC-005`,
  and `AIC-013`.
- Six verification findings remain: one HIGH content conflict, four MEDIUM
  truth/enforcement gaps, and one HIGH release-process blocker.
- The five-tier example evidence model, interface-first BuildingBlocks
  contract, optional tested `EsAggregateRoot<TId>`, soft-delete/purge policy,
  workload grammar, routing/index cleanup, migration manifest, and shell
  lifecycle taxonomy are materially stronger and evidence-backed.
- Full Observability architecture remains correctly deferred to
  [`OBS-001`](../../backlog/items/OBS-001.yaml). Only the approved
  CrossCutting/Domain dependency boundary is present in the verified subject.

The branch must not be tagged or published as v0.4.0 until the HIGH findings
are closed and the remaining MEDIUM findings receive an explicit disposition.

## 2. Scope And Exclusions

### Included

- [standards](../../standards/README.md), [guides](../../guides/README.MD),
  [scripts](../../../.ai/scripts/README.md), canonical skills, runtime wrappers,
  tech-stack references/source-includes, root collaboration entries, indexes,
  validators, manifests, workflow artifacts, release candidate metadata, and
  Git history;
- tool-owned analyzer, configuration, and BuildingBlocks test projects only as
  verification mechanisms;
- direct reconciliation against `ASM-20260715-002#AIC-001` through `AIC-014`.

### Excluded

- `src/**`, product tests, `docker-compose/**`, and product code review;
- GitHub Release re-verification and every operation that could move, recreate,
  or delete the immutable v0.3.0 tag;
- full CrossCutting Observability/AOP design, which remains in `OBS-001`;
- clean-room creation of a new downstream product repository.

## 3. Evidence And Method

The verification used the requested two-pass method.

1. **Baseline pass without skill conclusions:** inspected canonical/derived
   truth, active routing, example claims, shell behavior, manifests, Git
   history, and validation output using repository-native evidence.
2. **Formal skill pass:** applied the `ai-context-auditor` scope, evidence,
   comparison, finding, and durable-assessment contracts.
3. **Parallel read-only verification:** bounded sub-agents checked
   standards/examples, routing/skills/guides, and validators/migration/history.
   The primary agent re-ran material checks and reconciled conflicting
   interpretations.

Evidence vocabulary remains distinct:

| Evidence class | Meaning |
| --- | --- |
| exists | tracked at the pinned subject revision |
| linked | a resolvable inbound Markdown or catalog route exists |
| skill-navigated | a canonical skill or runtime wrapper routes to it |
| validator-enforced | an automated check rejects contract violations |
| workflow-evidenced | retained workflow artifacts record execution/use |
| possible AI reading | not inferable from repository evidence |

`codebase-memory-mcp` was not callable in this session. This is a tool
availability limitation, not evidence of repository incompleteness. Hidden
trees and non-code relationships were verified with `git ls-files`, direct
reads, Git history, and `rg -uu`.

## 4. Baseline Analysis Without Skill

The independent pass found a coherent governance spine and substantial
improvement over the baseline assessment. It also found that green structural
validation does not imply semantic consistency:

- active profile templates and guides still contradict the canonical
  environment/profile grammar;
- active guides and routed reference material bypass the generic technology
  override mechanism by stating unconditional NSubstitute rules;
- an active design guide and a reference-only example retain synchronous
  `Execute(...)` vocabulary;
- the executable-tested BuildingBlocks claim is true today, but its behavior
  tests are not part of the aggregate release gate;
- the full gate exits successfully while a transitional test script computes
  the wrong source root and still treats Moq as universally prohibited;
- the workflow's own commit-range validator rejects fourteen pushed commits.

## 5. Skill-Assisted Analysis

The formal pass confirmed the baseline risks and sharpened their ownership:

- profile contradictions are active canonical/derived-truth drift, not harmless
  historical example noise;
- default technology selection is correctly modeled in ownership/schema truth,
  but several human routes do not resolve the target override before advising;
- the stale shell helper is transitional/advisory, so it does not invalidate
  the shell taxonomy, but its presence in full-mode output still carries
  maintenance and interpretation cost;
- the commit-range failure is a release-process blocker. The auditor does not
  authorize rewriting already-pushed history or weakening commit policy.

The skill pass also confirmed wrapper parity, complete catalogs, honest evidence
tiers, and the correct separation of assessment evidence from remediation
authority.

## 6. Comparison Between Both Passes

### Confirmed By Both

- `AIC-001` remains partially resolved with a HIGH active-profile conflict.
- `AIC-005` and `AIC-013` retain MEDIUM routed-reference/default-override drift.
- the BuildingBlocks source include passes its focused tests but lacks aggregate
  gate enforcement;
- workflow commit validation blocks closure.

### Added Or Sharpened By The Skill Pass

- transitional shell behavior is classified as a residual lifecycle problem,
  not evidence that `AIC-009` core taxonomy failed;
- clean-room architectural reconstruction remains deferred verification rather
  than a defect or justification for adding a reference product fixture.

### Downgraded Or Rejected

- no blanket orphan/deletion conclusion is supported for examples;
- direct routes to reference-only material are not automatically stale, but
  they must preserve tier and override context;
- no claim is made that an unobserved file was never read by an AI session.

## 7. Standards Inventory

| Surface | Verified state | Classification |
| --- | --- | --- |
| governance/ownership policies | coherent, machine registered | `active-canonical`, partly `validator-enforced` |
| focused architecture standards | materially aligned except profile projections | `active-canonical` |
| project structure | one logical workload grammar, target-owned physical layout | `active-canonical`, `routing-required` |
| BuildingBlocks reconstruction contract | interface-first; sole optional ES base; seven equivalence criteria | `active-canonical`, partly `executable-tested` |
| standards templates | cataloged, but profile templates retain conflicts | mixed canonical support and `stale` |
| examples | all machine-tiered; legacy defaults downward | `example-only`, `reference-only`, `historical` |
| guides | complete README/INDEX routing; several semantic residuals | `routing-required`, mixed quality |
| canonical skills/wrappers | exact 14/14/14 directory parity | `routing-required`, parity-enforced |
| shell scripts | 3 active, 4 compatibility, 7 transitional | lifecycle classified; one stale advisory path |
| release candidate | planned with null tag/commit | honest pre-release metadata |

## 8. Inbound Reference And Enforcement Matrix

| Surface | Linked | Skill-routed | Validator-enforced | Workflow-evidenced | Result |
| --- | --- | --- | --- | --- | --- |
| ownership and technology selections | yes | yes | schema/tests | yes | canonical truth passes |
| profile standard | yes | architecture routes | structural only | yes | derived conflicts remain |
| example evidence tiers | root catalog + manifest | selective | fail-closed validator/tests | yes | passes |
| BuildingBlocks source include | indexes/contracts | architecture skill | manifest shape; focused manual test | yes | aggregate gate gap |
| guide catalogs | complete | selected | path/exact-case | yes | semantic residuals remain |
| canonical/runtime skills | indexes | root routing | parity validator | yes | passes |
| shell registry | README/runner | selected | schema/fail-closed tests | yes | taxonomy passes |
| file disposition manifest | release/migration routes | upgrader guidance | full coverage validator | yes | passes |
| workflow commit range | workflow policy | governance | commit validator | yes | fails |

## 9. Usage Evidence Matrix

| Candidate | Existence/link evidence | Strongest use evidence | What is not proven |
| --- | --- | --- | --- |
| profile templates | active templates INDEX | direct reusable template route | semantic correctness |
| example portfolio | evidence manifest and INDEX | workflow classification and validator | actual AI reading or target adoption |
| BuildingBlocks ES base | canonical contract/source include | 5/5 focused behavior tests | continuous execution by `check-all.sh` |
| skills/wrappers | three matching registries | validator and workflow routing | semantic quality of every reference |
| shell helpers | machine registry | aggregate runner selects lifecycle roles | product applicability of advisory grep rules |
| migration manifest | tracked release artifact | 134 changed paths covered by 135 entries | automatic authorization to overwrite target truth |

## 10. Duplicate, Stale And Orphan Candidates

The remediation eliminated the material duplicate catalogs and documented the
one retained in-memory configuration alias. No new deletion candidate is
justified solely by low inbound links.

Residual candidates are:

- **stale/rewrite:** profile templates and guide snippets using `Profiles:Mode`,
  `Repository:Mode`, `Test-InMemory`, `Test-Outbox`, or lower-case hyphenated
  environment names;
- **stale/rewrite:** unconditional NSubstitute statements in active guides and
  routed reference examples;
- **stale/rewrite:** synchronous `Execute(...)` examples in an active design
  guide and a reference-only inquiry archive guide;
- **transitional-retire-or-repair:** `check-test-compliance.sh`, which resolves
  the wrong source root in this repository and ignores technology overrides;
- **decision-required:** pushed commits that do not satisfy current commit
  trailer validation.

No active canonical file was proven orphaned. Multi-stack exploration remains
intentionally catalog-only and reference-only.

## 11. Example Folder Assessment

The example folder is now governed by a five-tier, machine-readable evidence
contract. Existing legacy content defaults downward and no example currently
claims `executable-tested`. This resolves the previous unsupported “verified
SSOT” posture.

| Group | Current tier/use | Verification conclusion |
| --- | --- | --- |
| controller | illustrative | async contract aligned |
| profile configs/ASP.NET | reference/illustrative | stale profile names and selection remain |
| outbox/usecase/reference tests | reference-only/historical | direct NSubstitute wording bypasses override context |
| inquiry archive | reference-only | synchronous `Execute(...)` vocabulary remains |
| BDDfy/Gherkin | separate routed modes | intentional distinction retained |
| BuildingBlocks source include | outside examples; executable-tested | 5/5 passes, but aggregate gate does not run it |

The correct v0.4.0 direction remains a small evidence-tiered pattern library,
not a committed reference product or wholesale copy of either downstream lab.

## 12. Findings

### VFY-001 — Active Profile Guidance Still Contradicts Canonical Selection

- Severity: **HIGH**
- Affected paths: [`profile-isolated-configurations.md`](../../standards/templates/profile-isolated-configurations.md), [`application-properties-templates.md`](../../standards/templates/application-properties-templates.md), profile/ASP.NET examples, broad coding standards, and multiple implementation/design guides
- Repository-native evidence: the canonical [profile standard](../../standards/coding-standards/profile-configuration-standards.md) requires environment selection and current names such as `TestInMemory`/`TestOutbox`; active templates use `Profiles:Mode`, examples use `Repository:Mode` and `Test-Outbox`, and routed guides use `test-inmemory`/`test-outbox`.
- Why it matters: agents can generate mutually incompatible configuration and registration mechanisms from simultaneously active guidance.
- Confidence: **high**
- Recommended disposition: rewrite all active projections against one canonical grammar; retain target-selected persistence implementations.
- User decision required: **no**; the canonical decision already exists.

### VFY-002 — Active Test Guidance Bypasses Technology Override Resolution

- Severity: **MEDIUM**
- Affected paths: [`DOTNET-DI-TEST-GUIDE.md`](../../guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md), [`NEW-PROJECT-TEST-SETUP-GUIDE.md`](../../../src/knowledge/dotnet-backend/guides/NEW-PROJECT-TEST-SETUP-GUIDE.md), and routed examples under `examples/outbox`, `examples/usecase`, and `examples/reference`
- Repository-native evidence: ownership/schema truth correctly defines NSubstitute as a default-profile selection with a generic target override, while active guidance says “NSubstitute only” or “Use NSubstitute” without first resolving `testing.mocking`.
- Why it matters: copied guidance can overwrite a product's valid Moq or other target-owned selection even though the canonical mechanism permits it.
- Confidence: **high**
- Recommended disposition: route prose and snippets through the generic technology-selection resolution rule; keep NSubstitute as the default.
- User decision required: **no**; the default and override mechanism are already approved.

### VFY-003 — Routed Documents Retain Synchronous Use-Case Vocabulary

- Severity: **MEDIUM**
- Affected paths: [`TEST-DATA-PREPARATION-GUIDE.md`](../../../src/knowledge/dotnet-backend/guides/TEST-DATA-PREPARATION-GUIDE.md) and [`inquiry-archive/USAGE-GUIDE.md`](../../standards/examples/inquiry-archive/USAGE-GUIDE.md)
- Repository-native evidence: the active design guide awaits `_createProductUseCase.Execute(input)` in four snippets, and the reference-only example invokes `_useCase.Execute(...)`; current use-case/controller truth requires `ExecuteAsync` with cancellation propagation.
- Why it matters: retrieval or copy/paste can reintroduce the pre-.NET asynchronous contract even after the main controller example was repaired.
- Confidence: **high**
- Recommended disposition: rewrite the active guide; align or explicitly historical-label the reference example.
- User decision required: **no**.

### VFY-004 — Executable-Tested BuildingBlocks Behavior Is Not In The Aggregate Gate

- Severity: **MEDIUM**
- Affected paths: [`source-includes/evidence-manifest.yaml`](../../../.ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml) and [`.ai/scripts/check-all.sh`](../../../.ai/scripts/check-all.sh)
- Repository-native evidence: the manifest declares the BuildingBlocks build/test commands and 5/5 focused tests pass, but the validator checks only manifest shape and `check-all.sh --full` does not run `DotnetBackendBuildingBlocks.Tests`.
- Why it matters: the sole reusable ES base can behaviorally drift while the aggregate release gate remains green.
- Confidence: **high**
- Recommended disposition: add the focused BuildingBlocks test project as a required aggregate check.
- User decision required: **no**.

### VFY-005 — Transitional Test Compliance Helper Is Stale And Misleading

- Severity: **MEDIUM**
- Affected paths: [`src/tools/dotnet/check-test-compliance.sh`](../../../src/tools/dotnet/check-test-compliance.sh), [`src/tools/dotnet/check-test-di-compliance.sh`](../../../src/tools/dotnet/check-test-di-compliance.sh), shell registry, and aggregate runner
- Repository-native evidence: full mode exits zero with one advisory because the helper resolves `BASE_DIR` outside the repository and searches `/c/Github/YuChia/src`; both helpers also flag Moq without resolving the approved technology override.
- Why it matters: even as transitional/advisory assets, their output adds noise and communicates policy that contradicts canonical applicability.
- Confidence: **high**
- Recommended disposition: repair the root and override semantics if compatibility still has value, otherwise retire the helpers and their full-mode route.
- User decision required: **yes** for repair-versus-retire timing.

### VFY-006 — Workflow Commit Range Fails Required Trailer Validation

- Severity: **HIGH**
- Affected paths: Git history from `ed5f8fb9e7cefe849dcd129571d21a92f31c830d` through `e7ca51a7f03c114d5ce5826a15eeb15338efea76`, [`GIT-COMMIT-POLICY.md`](../../standards/GIT-COMMIT-POLICY.md), and the remediation workflow closeout
- Repository-native evidence: `validate-git-commits.py --range ... --workflow-id 2026-07-16-v0-4-0-ai-context-remediation` rejects fourteen commits (`5926b26` through `e7ca51a`) because the final non-empty line is not a valid `Co-Authored-By` trailer.
- Why it matters: VERIFY and release closure cannot claim policy compliance while the workflow's own mandatory commit validator fails.
- Confidence: **high**
- Recommended disposition: obtain an explicit decision between a coordinated rewrite of the already-pushed assessment/remediation branch history and a documented policy-compliant prospective exception/repair mechanism. Do not weaken the validator silently.
- User decision required: **yes**; rewriting shared remote history is materially disruptive, while defining an exception changes governance.

## 13. v0.4.0 Candidate Actions

| Action | Candidates |
| --- | --- |
| Retain | governance spine, evidence tiers, interface-first BuildingBlocks contract, optional tested ES base, soft-delete/purge policy, workload grammar, complete catalogs, migration manifest |
| Merge | repeated profile guidance into one canonical projection path |
| Rewrite | profile templates/guides, technology-default prose, synchronous snippets |
| Move | no additional move is justified by this verification |
| Archive | only legacy reference material that cannot preserve current tier/override context after rewrite |
| Delete | no new example deletion is justified; transitional test helpers may be retirement candidates after decision |

Priority remains reduction of context-routing ambiguity and maintenance cost,
not deletion count.

## 14. Decisions Required From Me

1. For `VFY-006`, should the already-pushed branch history be rewritten in a
   coordinated force-push, or should governance define a prospective,
   validator-recognized exception/repair path for these commits?
2. For `VFY-005`, should the transitional test grep helpers be repaired for
   compatibility or retired from the v0.4.0 full gate/package?

No further decision is required for NSubstitute: it remains the default while
targets may override the generic `testing.mocking` selection.

## 15. Deferred Or Unverifiable Items

- A clean-room target was not reconstructed end to end. Routing, the seven
  architectural-equivalence criteria, analyzer routes, and ES mechanics are
  verified; full reconstructability remains a future exercise.
- Actual AI session reading cannot be established from repository files.
- Full Observability architecture remains in `OBS-001` for a separate design
  workflow after v0.4.0 remediation or explicit prioritization.
- Package-version currency and external product code quality were not assessed.
- `codebase-memory-mcp` was unavailable; hidden-tree completeness used
  repository-native fallbacks.

## 16. Recommended Remediation Slices

Return these stable findings to the existing
`2026-07-16-v0-4-0-ai-context-remediation` workflow:

1. profile truth convergence: `ASM-20260716-001#VFY-001`;
2. technology override and async documentation alignment:
   `#VFY-002`, `#VFY-003`;
3. release-gate enforcement: `#VFY-004`;
4. transitional helper disposition: `#VFY-005`;
5. commit-history governance decision and execution: `#VFY-006`;
6. run a successor verification assessment after remediation.

Do not create a second remediation workflow. Do not expand these slices into
the deferred `OBS-001` design.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| subject pin and clean assessment branch | pass | assessed `e7ca51a`; assessed surfaces remained unchanged |
| AI context structure | pass | 24 active indexes, 14 canonical skills, two runtime roots, 13 owned rules, 32 manifests, 10 mappings |
| wrapper parity | pass | canonical, `.agents`, and `.claude` sets are 14/14/14 |
| example evidence | pass | 4/4 tests; legacy material defaults downward |
| placeholder disposition | pass | 3/3 tests |
| technology selections | pass | 3/3 tests |
| BuildingBlocks behavior | pass outside aggregate gate | 5/5 focused tests |
| analyzer tests | pass | 49/49 |
| configuration tests | pass | 2/2 |
| migration manifest | pass | 134 changed distributable paths covered by 135 entries |
| release version registry | pass | five records; v0.4.0 remains planned with null tag/commit |
| aggregate full gate | pass with warning | 16 required passed; one advisory warning; four deferred |
| workflow commit range | **fail** | fourteen invalid/missing final AI co-author trailers |
| assessment artifacts | pass | three locators/index rows valid; 9/9 fail-closed tests passed |
| packaging safety suite | pass with environment limitation | 25 checks passed; one Windows symlink privilege probe skipped |

## Appendix A — Baseline Finding Reconciliation

| Baseline finding | Verification status | Evidence/disposition |
| --- | --- | --- |
| `AIC-001` | partial | `VFY-001` |
| `AIC-002` | resolved | soft delete is profile-default with explicit opt-out; purge is separate restricted capability |
| `AIC-003` | resolved | five-tier machine-readable example evidence; stale sync metadata removed |
| `AIC-004` | resolved | removed grep route replaced by DBA1001/analyzer guidance |
| `AIC-005` | partial | canonical placeholder contract resolved; routed legacy/default wording remains in `VFY-002` |
| `AIC-006` | resolved | one catalog; deliberate BDD modes retained; documented semantic config alias |
| `AIC-007` | resolved | guides/prompts relocated or retired; catalogs complete |
| `AIC-008` | resolved | structural claim is accurately bounded and tested |
| `AIC-009` | resolved with residual | lifecycle taxonomy passes; stale transitional behavior is `VFY-005` |
| `AIC-010` | resolved with residual | controller fixed; other routed synchronous snippets are `VFY-003` |
| `AIC-011` | resolved | rationales/guides cataloged; exploration-only material correctly reference-only |
| `AIC-012` | resolved | no active `Lab.*` namespace leakage |
| `AIC-013` | partial | generic override truth passes; active prose residual is `VFY-002` |
| `AIC-014` | resolved subject to deferred exercise | architecture equivalence contract and workload grammar exist; clean-room reconstruction deferred |

## Appendix B — Commands And Evidence

```text
git ls-files
rg -n -uu <targeted standards, guide, example, skill, and script patterns>
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-shell-assets.py
python tools/maintenance/validate-file-disposition-manifest.py
python .ai/scripts/validate-ai-context-versions.py
python tools/maintenance/validate-git-commits.py --range <base>..<subject> --workflow-id <workflow>
dotnet test tools/DotnetBackendBuildingBlocks.Tests/DotnetBackendBuildingBlocks.Tests.csproj
C:/Program Files/Git/bin/bash.exe ./.ai/scripts/check-all.sh --full
git diff --check
```

## Appendix C — Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260716-001/report.md`
- Stable finding references: `ASM-20260716-001#VFY-001` through `VFY-006`
- Remediation owner: `ai-context-governance`
- Related remediation workflow:
  `2026-07-16-v0-4-0-ai-context-remediation`
- Verification assessment: this assessment
- Remediation intentionally not performed on the assessment branch: **yes**
