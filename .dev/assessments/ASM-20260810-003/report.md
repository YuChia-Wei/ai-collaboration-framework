# Distribution Source, Projection, And Published Artifact Inventory

## Metadata

- `assessment_id`: `ASM-20260810-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-10`
- `created_at`: `2026-08-10T22:29:58+08:00`
- `updated_at`: `2026-08-10T22:29:58+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `codex/2026-08-10-package-identity-consolidation`
- `subject_commit`: `343089ea2a05a10ee203fa5cbbc7a542db9b346f`
- `issue_ref`: `#172`
- `related_assessments`: `ASM-20260809-003`, `ASM-20260809-004`

## Executive Summary

- Overall assessment: the distribution model produces a materially classified and reproducible product artifact. Published v0.11.0 ZIP and tar.gz bytes are valid, cross-format equivalent, and exactly reproducible from the recorded source commit.
- Product result: v0.11.0 contains 658 payload files split across four components, with every file carrying source path, target path, component, ownership, install behavior, mode, size, and SHA-256 evidence.
- Current result: the pinned profile resolves 655 target files / 2,915,814 bytes from 639 unique sources. It preserves the four-component model and the 640 managed / 15 seed ownership boundary.
- Decision: `follow-up-required`, but no published-asset repair is required. #166 should consolidate scattered identity literals; #184 should make the 30 safe-but-implicit `.dev` omissions machine-readable.
- Release impact: #172 inventory acceptance is satisfied. Package bytes, archive names, schemas, migration behavior, and v0.11.0 assets remain unchanged.

## Scope

### Included AI Context Surfaces

- `.ai/distribution/**`, the current distribution resolver, component contract, mappings, exclusions, and generated metadata rules.
- The current Git-tree projection at `343089e...`.
- GitHub Release v0.11.0 online metadata and all four published assets.
- Portable/source-only/target-template/generated conclusions from `ASM-20260809-003` and `ASM-20260809-004`.

### Default Exclusions

- Product source and tests under `src/**` or equivalent implementation trees.
- Target-repository state and environment-specific downstream truth.

### Additional Exclusions

- Any mutation of tags, Releases, assets, package bytes, schemas, archive names, or migration behavior.
- CLI naming and implementation decisions.

### Code Review Handoff

- Requested: `no`.
- Product code was not scanned; the package resolver was used only as a governed projection and validation surface.

## Methodology And Evidence

### Pass A: Published Artifact Read-Back

- Downloaded all v0.11.0 assets from the public Release and independently computed size and SHA-256.
- Validated both sidecars, envelope roots, SHA256SUMS coverage, package/files/migration schemas, payload counts, per-file hashes, sizes, modes, and component records.
- Compared ZIP and tar.gz after removing only their common envelope root: relative paths, content bytes, and modes are identical.
- Replayed the distribution resolver at recorded commit `05199ed...`; all 658 projected payload paths, bytes, modes, and the payload fingerprint match the archive exactly.

### Pass B: Current Contract Reconciliation

- Resolved the current profile from the pinned Git tree rather than the Windows checkout bytes.
- Compared the 655-file current projection with the 658-file v0.11.0 manifest.
- Reconciled `.ai` authority with `ASM-20260809-003` and `.dev` lifecycle/disposition with `ASM-20260809-004`.
- Classified all differences as correct evolution, historical compatibility, product-boundary explainability, or identity consolidation work.

### Delegation

- Sub-agents used: `no`.
- The audit used focused local checks and direct GitHub read-back; no long-running full-history validation was required for this baseline.

### Discovery Accelerators

| Tool / view | Use | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- |
| Codebase Memory MCP | Located package collection, archive, and validation functions | Cannot establish release bytes or completeness | Direct source, Git tree, downloaded assets |
| Distribution resolver | Produced exact current and v0.11 source/target projections | Does not prove online publication | GitHub Release read-back and archive validation |
| GitHub CLI | Read online Release and asset metadata | Does not establish internal archive validity | SHA-256, sidecars, metadata, and per-file replay |

## Source-To-Product-To-Artifact Results

The complete machine-readable summary is [`evidence/source-to-product-artifact-inventory.yaml`](evidence/source-to-product-artifact-inventory.yaml). The published read-back is [`evidence/v0.11.0-published-archive-readback.yaml`](evidence/v0.11.0-published-archive-readback.yaml).

| Layer | Exact result | Interpretation |
| --- | --- | --- |
| Source authority | `.ai` canonical assets plus selected `.dev` governance/guides, adapters, scripts, and template mappings | Source repository content is not automatically product content. |
| Current product projection | 655 target files, 639 unique source files, 2,915,814 bytes | Allowlist and mapping produce a bounded product view. |
| Published v0.11.0 payload | 658 files; fingerprint `a2cf804c...` | Per-file manifest makes content and ownership auditable. |
| Published envelopes | 664 members in each format: 658 payload + 6 required envelope files | ZIP and tar.gz are structurally and semantically equivalent. |
| Ownership | v0.11: 643 managed / 15 seed; current: 640 managed / 15 seed | Target-owned seeds remain distinct from framework-managed files. |
| Components | v0.11: 341 software core, 110 lifecycle core, 205 .NET, 2 backlog | Componentization is present in the actual artifact, not only documentation. |

## Published v0.11.0 Read-Back

| Check | Result | Evidence |
| --- | --- | --- |
| Online asset size and digest | passed | ZIP `1,255,029` / `cd7010f...`; tar.gz `814,603` / `087810cd...`; both sidecars match. |
| ZIP internal contract | passed | 664 members, exact SHA256SUMS coverage, valid package/files/migration metadata. |
| tar.gz internal contract | passed | Same validation and member count. |
| Cross-format equivalence | passed | No relative-path, content, or mode differences. |
| Source replay | passed | Recorded commit and tree reproduce all 658 payload files and fingerprint. |
| Clean install / upgrade metadata | passed | 658 clean-install operations; migration source `0.10.0`; safety defaults are fail-closed. |
| Source-only leakage | passed | No workflow/assessment/release/backlog-item lifecycle paths or release-closeout sources in payload. |

The archived `source.repository` value is the pre-rename URL. That is immutable historical metadata, not a corrupt asset. The current profile already points at `ai-collaboration-framework`, while the old GitHub URL remains a compatibility alias.

## Current Versus v0.11.0

- Current projection: 655 files versus 658 published files.
- Added since v0.11.0: two paths; removed: five paths; content changed: 68 paths.
- No common path changed mode, component, ownership, install behavior, or source-path mapping.
- Current `dotnet-backend` count is 202 rather than 205. The difference follows reviewed source evolution; it is not an archive-format inconsistency.
- Current payload fingerprint is `ecd20b70...`; it is a projection diagnostic, not a claim that a v0.12.0 candidate or Release already exists.

## Strengths

1. The published artifact proves that component classification is operational: every file has a component, ownership class, install behavior, mode, size, and digest.
2. ZIP and tar.gz are true alternate envelopes around the same content, not independently drifting products.
3. Source-only workflow, assessment, release, backlog-item, transition, and release-closeout evidence stays outside the downstream payload.
4. The package distinguishes framework-managed replacement from target-template seeding, supporting safer clean installs and upgrades.
5. Repository identity and technology-profile semantics can remain distinct without renaming the established archive in v0.12.0.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| PKG-001 | MEDIUM | Thirty current `.dev` paths are safely omitted but match neither a package entry nor an explicit exclusion/disposition. | Machine inventory; 1,041 tracked `.dev` files = 117 packaged + 894 explicitly excluded + 30 implicit omissions. | Payload behavior is safe, but a machine cannot reproduce owner, retention, or omission reason from the distribution contract alone. | Add a versioned source-disposition contract and fail-closed implicit-omission validation without rewriting source evidence. | Issue [#184](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/184); `ai-context-governance`. |
| PKG-002 | MEDIUM | Repository, public product, framework release, technology profile, archive/package, and legacy alias identities are accurate in context but distributed across unmanaged literals. | Current profile uses the new repository URL; v0.11 metadata preserves the old URL; Release is `REL-v0.11.0`; profile is `dotnet-backend`; archive is `ai-context-dotnet-backend-v0.11.0`. | A future rename or toolchain addition could incorrectly couple unrelated identities or create ambiguous aliases. | Define a versioned registry, keep `dotnet-backend` and the v0.11 archive as compatible identities, and validate duplicate IDs / aliases. | Issue [#166](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/166); `ai-context-governance`. |

## Baseline And Skill Comparison

### Confirmed

- `ASM-20260809-003` correctly classifies canonical portable `.ai` inputs and source-only release-closeout capability.
- `ASM-20260809-004` correctly identifies implicit `.dev` omissions; the count grew from 29 to 30 when the current provider projection was added.
- The package excludes source lifecycle history and retains target-template seeds as a separate ownership class.

### Added By Published Read-Back

- Both public archive formats are byte-for-byte equivalent after envelope normalization and reproduce from the recorded source commit.
- v0.11.0's legacy repository URL is confined to immutable metadata and is compatible with the current repository redirect.
- Component and ownership classifications are embedded in the public `files.yaml`, demonstrating concrete packaging benefit.

### Corrected

- The current projection is 655 files, not the 659-file pre-remediation projection in the earlier assessments.
- The implicit `.dev` omission count is 30, not 29, because `github-project-current.yaml` is now a current source projection.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Published asset metadata | passed | Four assets match online size/digest records. |
| Archive native validation | passed | Both formats pass `validate_archive`; sidecars pass `validate_sidecar`. |
| Cross-format comparison | passed | Same relative path set, content, and mode. |
| Recorded-source replay | passed | 658/658 payload files match recorded commit/tree. |
| Current distribution resolution | passed | 655 targets, no collisions, deterministic payload fingerprint. |
| Current/v0.11 classification stability | passed | No common-path component, ownership, behavior, mode, or source mapping changes. |
| Exhaustive machine-readable omission reason | failed | 30 `.dev` paths require #184. This does not imply payload leakage. |

### Environment-Limited Checks

- None for the focused #172 evidence. Full repository validation is owned by the cohesive workflow verification stage, not this read-only baseline.

## Recommended Action Order

1. Close #172 as a completed inventory after committing this durable assessment.
2. Implement #166 from PKG-002 without renaming the current archive or deciding CLI identity.
3. Keep #184 Planned / Unassigned until the owner selects a release; it does not block the safe v0.11 read-back or #166 registry.
4. Independently verify #166 in `ASM-20260810-004`, then complete the shared workflow and hosted checks.

## Deferred Items

- Explicit source-disposition schema and validator: #184.
- CLI command, binary, installer, and registry package identity: #149/#168 or a later `feature:cli` Issue.
- v0.12.0 candidate generation, tag, Release, and publication: outside #172/#166.
- No existing tag, asset, package metadata, migration record, or historical reference was modified.

## Appendix

### Commands Run

```text
gh release view v0.11.0 --repo YuChia-Wei/ai-collaboration-framework --json ...
gh release download v0.11.0 --repo YuChia-Wei/ai-collaboration-framework --pattern ai-context-dotnet-backend-v0.11.0*
validate_sidecar(<zip and tar.gz>)
validate_archive(<zip and tar.gz>)
resolve collect_payload at 05199ed0... and 343089ea...
compare archive members, content, modes, metadata, and current projection
```

### Notes

- GitHub reads were executed outside the sandbox.
- Downloaded assets were held in an ephemeral local directory and were not added to the repository.
- Current projection evidence does not claim a v0.12.0 candidate exists.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260810-003/report.md`
- Stable findings: `ASM-20260810-003#PKG-001` and `#PKG-002`
- Identity remediation: Issue #166 / task `ID001-001`
- Source-disposition remediation: Issue #184
- Verification assessment: `ASM-20260810-004`
- Remediation intentionally not performed by this audit: `yes`
