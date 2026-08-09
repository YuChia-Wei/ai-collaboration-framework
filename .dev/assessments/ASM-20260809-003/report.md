# .ai Product Source, Ownership, And Portability Inventory

## Metadata

- `assessment_id`: `ASM-20260809-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-09`
- `created_at`: `2026-08-09T22:06:38+08:00`
- `updated_at`: `2026-08-09T22:06:38+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `3a60570d0e290f337f2a212d092c6797670528b4`
- `issue_ref`: `#170`
- `related_assessments`: `ASM-20260809-001`, `ASM-20260809-002`

## Executive Summary

- Overall assessment: the current `.ai` product/source boundary is explicit and internally consistent. All 595 requested `.ai` and adapter blobs are classified; 522 are effective package sources and 73 match named source-only exclusions.
- Product answer: portable canonical assets, selected runtime scripts/tests, and thin runtime wrappers/adapters are framework product. Distribution build controls, local evaluation, release/provider operations, release-closeout, and generic Codex worker profiles are source governance only.
- Projection answer: the current source contract resolves 643 unique repository sources into 659 target paths with 16 intentional projections, no collisions, and payload digest `9d559d...`.
- Decision: `handoff-required`, not broad remediation. #166 owns product/package/profile/alias identity; #172 owns archive read-back and any disposition-schema decision.
- Primary coupling: the packaged v0.6.0 skill-transition manifest retains source activation evidence and concrete references to excluded `.ai/evaluation/**` paths beside the portable compatibility alias map.

## Scope

### Included AI Context Surfaces

- `.ai/assets/skills/**`, `sub-agent-role-prompts/**`, `shared/**`, `tech-stacks/**`, and templates/schema entries.
- `.ai/distribution/**`, `.ai/scripts/**`, `.ai/evaluation/**`, and `.ai` entry/index documents.
- `.agents/**`, `.claude/**`, and `.codex/**` projection/adapter relationships.
- Current profile resolution and identity/package inputs for #166 and #172.

### Default Exclusions

- `src/**` and product implementation trees.
- Product tests outside the explicitly included `.ai/scripts/tests/**` AI-context surface.

### Additional Exclusions

- Material moves, deletions, semantic changes, package-byte changes, CLI runtime selection, and full archive read-back.
- Existing tag, Release, asset, historical evidence, or downstream target-owned truth mutation.

### Code Review Handoff

- Requested: `no`.
- Recommended skill: `not-applicable`; future boundary remediation belongs to `ai-context-governance` after a dedicated Issue.

## Methodology And Evidence

### Pass A: Independent Baseline

- Counted pinned Git blobs and bytes, not checkout bytes.
- Classified canonical assets, runtime scripts/tests, source controls, evaluation evidence, wrappers, aliases, and runtime adapters.
- Verified every excluded scoped path matches exactly one named profile exclusion.

### Pass B: Repository-Aware Skill Review

- Applied `PRODUCT-SOURCE-001`, distribution profile/schema, AI-context boundary/ownership rules, wrapper metadata, role execution contract, and source-governance validation.
- Resolved the current payload with repository package code: 659 target paths / 2,889,104 bytes, 643 unique source paths, 16 intentional projections, zero target collisions, and no payload reference-integrity error.

### Delegation

- Sub-agents used: `yes`.
- `.ai` content/ownership inventory: bounded general worker under `ai-context-auditor`, read-only, no nested delegation.
- Package/projection cross-check: bounded routine worker under `ai-context-auditor`, read-only, no nested delegation.
- Main-agent reconciliation: verified scope totals from Git blobs, confirmed exclusion lists and wrapper parity, and independently reviewed transition/evaluation coupling.

### Discovery Accelerators

| Tool / generated view | Source revision | Use | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- |
| Codebase Memory MCP | current indexed repository | Located package and validation entrypoints | Cannot prove full path coverage, package bytes, or provider state | Git tree, profile resolver, direct files |
| Distribution resolver | `3a60570d...` | Exact source/target/exclusion/component mapping | Does not prove published v0.11.0 archive bytes | #172 archive read-back |

## Repository Context Inventory

| Surface | Tracked | Effective package source | Classification |
| --- | ---: | ---: | --- |
| `.ai` entry documents | 4 / 20,320 bytes | 4 / 20,320 bytes | Portable product entry |
| `.ai/assets/**` | 408 / 1,328,710 bytes | 400 / 1,313,815 bytes | Portable canonical product with eight source-only exceptions |
| `.ai/scripts/**` | 110 / 1,552,061 bytes | 79 / 1,068,329 bytes | Portable runtime plus explicit source automation/tests |
| `.ai/distribution/**` | 11 / 45,137 bytes | 0 | Source package-control authority |
| `.ai/evaluation/**` | 19 / 14,708 bytes | 0 | Source evaluation evidence |
| `.agents/**` | 20 / 27,870 bytes | 19 / 26,947 bytes | Thin Codex-compatible wrapper projection |
| `.claude/**` | 20 / 28,438 bytes | 19 / 27,517 bytes | Thin Claude wrapper/adapter projection |
| `.codex/**` | 3 / 9,425 bytes | 1 / 770 bytes | One portable role adapter; two source-only worker profiles |

The exhaustive machine-readable matrix is in [`evidence/ai-inventory.yaml`](evidence/ai-inventory.yaml).

## Product And Source-Governance Boundary

### Framework Product

- Four `.ai` entry documents.
- Portable shared assets, 14 active packaged skills, two deprecated compatibility aliases, 18 canonical roles, the `dotnet-backend` profile, reusable templates, and selected scripts/tests.
- Sixteen Codex/Claude skill wrapper identities per packaged runtime after the source-only closeout wrapper is removed.
- The `context-translator` runtime-native role adapters; adapters remain projections of one canonical role.

### Source Governance Only

- Distribution profile/schemas/build controls and Source Maintainer CLI contracts.
- Evaluation corpus, fixtures, baselines, and model-in-loop/source evidence.
- Package/release/provider/repository validators and their source-only tests.
- `ai-context-release-closeout` and its wrappers/guide.
- `bounded-general-worker` and `bounded-routine-worker`; they are runtime execution profiles, not canonical roles.

### Generated Or Target-Owned Projections

- Package metadata, archives, files inventories, and staging trees are generated projections, never a second source.
- Three portable governance documents map to `.dev` target policies.
- Thirteen `ai-context-init` template sources also seed target-owned root/catalog paths.

## Strengths

1. All 73 scoped non-product paths match explicit exclusions; there are no unclassified `.ai`/adapter omissions.
2. Seventeen source canonical skills have wrapper parity in both runtime roots; product projection intentionally removes the one source-only skill and retains the two compatibility aliases.
3. All 18 canonical roles are portable, while generic runtime worker profiles remain explicitly outside the role taxonomy and package.
4. The actual resolver found no target collision, component ambiguity, exclusion overlap, or forbidden source-lifecycle reference.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIA-001 | MEDIUM | The packaged `transitions/v0.6.0.yaml` combines the current compatibility alias map with source-only activation/model evidence and concrete references to excluded `.ai/evaluation/**` paths. | `.ai/assets/skills/transitions/v0.6.0.yaml:7,33-73`; profile exclusion for `.ai/evaluation/**`. | The alias contract is portable, but its evidence is not reproducible from the package and remains coupled to one source release/history boundary. | Preserve the historical manifest. Let #166 select the versioned alias identity model; if a portable alias registry is needed, open a bounded governance Issue to derive it without rewriting the v0.6 evidence. | #166, then `ai-context-governance` if selected. |
| AIA-002 | LOW | Canonical asset `portability` and distribution inclusion are distinct classifications; `ai-context-release-closeout` is valid `repo-portable` metadata but intentionally source-only in the distribution profile. | `ai-context-release-closeout/skill.yaml:1-9`; profile lines 441-448; asset schema enum. | Humans or generic inventory tools can misread `repo-portable` as downstream product inclusion unless they also resolve the profile. The package resolver itself is unambiguous. | Treat the profile as current authority. Have #172 decide whether a cross-surface disposition field/registry is needed; do not change metadata in this audit. | #172 / `ai-context-governance`. |

## Identity And Drift Handoff To #166

| Identity class | Current value | Disposition |
| --- | --- | --- |
| Repository | `YuChia-Wei/ai-collaboration-framework` | Current operational coordinate; not product identity |
| Product description | AI collaboration context framework with retained .NET backend capability | #166 formalizes versioned product identity |
| Release model | `single-versioned-componentized-release` | Current profile contract |
| Distribution profile | `dotnet-backend` | Technology profile, not repository name |
| Package/archive template | `ai-context-dotnet-backend-v{version}` | #166 owner decision; do not infer rename |
| Mandatory components | `software-development-core`, `ai-context-lifecycle-core` | Current product contract |
| Optional components | `dotnet-backend`, `repo-backlog` | Preserve explicit selection/default rules |
| Deprecated aliases | `dev-workflow` → `software-development-orchestrator`; `repo-structure-sync` → `ai-context-init` | Retain until #166/versioned compatibility decision |
| Source-only skill | `ai-context-release-closeout` | Never downstream product under current contract |
| CLI identities | Distribution CLI, Portable Validator Engine, Source Maintainer CLI | Separate Feature/runtime decisions |

## Package Handoff To #172

- Exact scoped sources: 522 included, 73 explicitly excluded.
- Whole current contract: 643 unique sources → 659 targets, digest `9d559dec5d36975305e53bb7ee71403a1e711f76e59a8bf1c63352f86edfd6c1`.
- The digest is a current-contract projection at `3a60570d...`, not a published v0.11.0 archive verdict.
- #172 must compare actual ZIP/tar.gz members, modes, checksums, metadata, and profile/archive identities against the v0.11.0 artifacts.

## Baseline And Skill Comparison

### Confirmed

- Both passes found complete explicit disposition for the requested `.ai` and adapter scope.
- Wrapper and adapter parity is intact.
- Source release, provider, evaluation, package-control, and generic worker surfaces remain excluded.

### Added By Repository-Aware Review

- Actual profile resolution established the 643-to-659 projection and current payload digest.
- The transition manifest's portable alias/source-evidence coupling is not a target collision or reference-integrity failure, but it is a semantic boundary for #166.

### Downgraded Or Deferred

- Repeated `ai-context-dotnet-backend` values are consumers of one profile authority, not duplicate product authorities. Naming remains #166's decision.
- Archive-level regression is deferred to #172; focused/source-contract checks are not presented as an archive verdict.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git tree coverage | passed | 595 scoped blobs / 3,026,669 Git-blob bytes; entry sums exact. |
| Distribution resolution | passed | 659 targets / 2,889,104 bytes; no collisions or reference-integrity errors. |
| AI context static validation | passed | 26 indexes, 17 canonical skills, two wrapper roots, 35 manifests, and governed identities. |
| Wrapper metadata | passed / static and focused | 17 source wrappers per runtime; exact canonical references. |
| Source-governance registry | passed | 1,017 retired-name lines / 172 assignments / 9 rules. |
| File-disposition manifest | passed | Current registered historical disposition manifest validates. |
| Archive-level package suite | blocked-by-environment / deferred | One worker hit Windows temp ACL errors; another long run exceeded 180 seconds. No archive semantic verdict is claimed. |

### Not Applicable

- `validate-ai-context-target.py`: this source repository intentionally has no downstream `.dev/ai-context/provenance.yaml`.
- Product source/tests outside the AI-context scope.

## Recommended Action Order

1. Deliver this inventory without moving or rewriting `.ai` paths.
2. Feed the exact identity and compatibility list to #166.
3. Feed source/target/exclusion counts and the archive-level limitation to #172.
4. Only after #166/#172 decisions, open a bounded governance Issue if a portable alias registry or explicit cross-surface disposition schema is selected.

## Deferred Items

- Priority for #170: owner decision; `P1 High` is recommended.
- Product/package/archive/profile/alias naming: #166.
- Archive member/checksum/published-asset comparison: #172.
- Package bytes, CLI runtime, path moves, deletions, and semantic rewrites: not authorized here.

## Appendix

### Commands Run

```text
git fetch --prune origin
git ls-tree -r -l 3a60570d0e290f337f2a212d092c6797670528b4 -- .ai .agents .claude .codex
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-source-governance.py
python .ai/scripts/validate-file-disposition-manifest.py --manifest <v0.5.0 disposition manifest>
python .ai/scripts/tests/test_profile_projection_contract.py -v
python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v
python .ai/scripts/tests/test_ai_context_sub_agent_adapters.py -v
python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v
```

### Notes

- Counts and bytes use the pinned Git tree, not checkout encoding or local caches.
- Temp-writing and long package tests are reported exactly as environment-limited/deferred.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260809-003/report.md`
- Machine inventory: `.dev/assessments/ASM-20260809-003/evidence/ai-inventory.yaml`
- Stable findings: `ASM-20260809-003#AIA-001`, `#AIA-002`
- Identity handoff: Issue #166
- Package handoff: Issue #172
- Remediation intentionally not performed by this skill: `yes`
