# .dev Governance Content And Lifecycle Inventory

## Metadata

- `assessment_id`: `ASM-20260809-004`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-09`
- `created_at`: `2026-08-09T22:06:38+08:00`
- `updated_at`: `2026-08-09T22:17:10+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `3a60570d0e290f337f2a212d092c6797670528b4`
- `issue_ref`: `#171`
- `related_assessments`: `ASM-20260809-001`, `ASM-20260809-002`

## Executive Summary

- Overall assessment: `.dev` has a coherent ownership model, but current navigation and work-management projections have drifted behind the immutable item/release evidence and live GitHub Project state.
- Inventory result: 1,011 tracked Git blobs / 5,810,865 bytes. The current profile selects 118 source files / 400,870 bytes, excludes or omits 893, and derives 129 `.dev` target paths after portable mappings.
- History result: all 68 post-adoption workflows are completed, 38 of 39 assessments are final, and all 14 release records are published. These are source-only evidence, not target truth.
- Decision: `follow-up-required`. Repair current projections and active references separately from immutable history; make validation-cadence and package-disposition schema decisions in their own work items.
- Primary risk: `ROADMAP.md`, backlog `INDEX.MD`, and the source GitHub provider contract describe an older release horizon even though item records, release records, and the online Project have advanced.

## Scope

### Included AI Context Surfaces

- All Git-tracked `.dev/**` blobs at the pinned source revision.
- Standards, guides, operations, ADRs, requirements, specs, problem frames, domain language, workflows, assessments, releases, lessons, backlog, roadmap, indexes, and lifecycle projections.
- Current distribution-profile inclusion, exclusion, omission, mapping, and ownership behavior.
- Issue #171 and Project #3 current fields; identity inputs for #166 and package inputs for #172.

### Default Exclusions

- `src/**`, product implementation, and product-test review.
- Generated/dependency/local state outside the explicitly scoped source governance records.

### Additional Exclusions

- Bulk cleanup, historical rewrite, lifecycle-policy mutation, and package-byte changes.
- Full v0.11.0 archive and published-asset read-back, owned by #172.

### Code Review Handoff

- Requested: `no`.
- Product source and tests were not scanned.
- Recommended skill: `not-applicable`; follow-up remediation belongs to `ai-context-governance`.

## Methodology And Evidence

### Pass A: Independent Baseline

- Used the pinned Git tree for path and blob-size totals, then classified every path by its top-level `.dev` group.
- Read current locators, item/release records, roadmap/index projections, provider contract, and active document references directly.
- Read back Project #3 outside the sandbox: #171 is `In progress`, targets `v0.12.0`, is `Not yet published`, and has no owner-selected Priority or Owner review value.

### Pass B: Repository-Aware Skill Review

- Applied `AI-CONTEXT-BOUNDARY`, `AI-CONTEXT-OWNERSHIP`, assessment/workflow artifact policy, product-source projection contract, and the current distribution profile.
- Resolved the actual profile with repository package code: 659 target paths, 643 unique source paths, no target collisions or exclusion overlap, and payload reference integrity passed.

### Delegation

- Sub-agents used: `yes`.
- `.dev` structure/content/lifecycle inventory: bounded general worker under `ai-context-auditor`, read-only, no nested delegation.
- Package/projection cross-check: bounded routine worker under `ai-context-auditor`, read-only, no nested delegation.
- Main-agent reconciliation: replaced checkout-byte counts with Git-blob counts, independently verified high-severity evidence and live provider state, and corrected the active broken-link total to seven occurrences across four canonical targets.

### Discovery Accelerators

| Tool / generated view | Source revision | Use | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- |
| Codebase Memory MCP | current indexed repository | Located validation entrypoints and traversal behavior | Cannot establish package completeness, current provider state, or document truth | Git tree, direct files, native validators |
| Distribution resolver | `3a60570d...` | Resolved source/target paths, exclusions, components, and mappings | Does not prove published v0.11.0 archive contents | #172 archive read-back |
| GitHub Project projection | provider read-back on 2026-08-09 | Current #171 lifecycle and field options | Does not authorize implementation or integration | Issue body, Git, assessment evidence |

## Content Type Matrix

| Type | Tracked facts | Authority | Package disposition |
| --- | --- | --- | --- |
| Reusable governance/guidance | 118 current profile source paths | Canonical `.ai` semantics plus selected `.dev` governance and human guides | Framework-managed or seed projection |
| Target-effective state | `.dev/ai-context/environment-policy.yaml` | Current repository evidence; downstream target owns its own state | Not packaged |
| Current source projections | Root/backlog/workflow/assessment/release indexes and provider config | Derived from locators, item records, release records, and provider read-back | Source-only |
| Immutable execution history | 68 completed workflows; 39 assessments | Each locator/report/task/evidence set | Never packaged; retain byte-stably |
| Immutable release history | 14 published release records | Each version's `release.yaml` | Never packaged; retain byte-stably |
| Compatibility/source operations | Rename notice, publication runbook, lessons | Source repository governance | Not packaged |

The exhaustive machine-readable matrix is in [`evidence/dev-inventory.yaml`](evidence/dev-inventory.yaml).

## Authority And Lifecycle Conclusions

1. Online Issues/Projects are the current work-management authority. Provider state does not by itself authorize implementation, but local backlog/index projections also cannot override the online queue.
2. Backlog item YAML remains historical decision and release evidence for the 55 migrated/local items. It is not a complete inventory of the 111 current Project items.
3. Workflow locators own execution lifecycle; assessment locators own observations; release manifests own version lifecycle. Their indexes are discovery projections, not competing truth.
4. Completed/published history must remain immutable and verifiable, but routine critical validation need not remain unboundedly history-proportional. A changed-path routine gate plus scheduled/release full-history gate is the recommended design, subject to owner approval.

## Strengths

1. The profile excludes all dated workflow, assessment, backlog-item, and release-instance history from downstream payloads.
2. All 68 post-adoption workflows, 39 assessments, and 14 release records pass their native structural validators.
3. Portable governance mappings deliberately use `.ai/assets/shared/governance/**` bytes instead of the three source-local work-management/Git policies.
4. The v0.11.0 annotated tag and peeled commit match the release record and are ancestors of the audit subject.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | HIGH | Current roadmap, backlog index, and source GitHub provider contract lag item, release, and live Project state. | `.dev/backlog/ROADMAP.md:5-9`; `.dev/backlog/INDEX.MD:8-45`; eight v0.9 item records; `.dev/releases/INDEX.MD:26-31`; `.dev/backlog/providers/github.yaml:127-153`; live Project fields include v0.11.0/v0.12.0 and 111 items. | Agents can read v0.9.0 as the current target or awaiting publication, while the Project is planning v0.12.0 and v0.11.0 is published. | Reconcile current projections and provider schema from authoritative records/read-back. Preserve all immutable receipts and history. | Issue [#175](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/175); `ai-context-governance`. |
| DEV-002 | MEDIUM | Active `.dev` documents contain seven broken references to four standards moved under `.ai/assets/tech-stacks/dotnet-backend/standards/`; the requirement guide also names four absent examples. | `.dev/ARCHITECTURE.md:3,18,32`; `EZDDD-FRAMEWORK-REFERENCE.md:24,26-27`; `DATABASE-MIGRATION-GUIDE.md:120`; `REQUIREMENT-GUIDE.MD:78-82`. | Current source navigation is misleading even though canonical targets exist. | Repair active documents only; leave historical assessment/workflow/release links byte-stable. | Same #175 governance remediation as DEV-001. |
| DEV-003 | MEDIUM | The critical validation profile revalidates all 68 completed workflows and their task records on every run. | `.ai/scripts/check-all.sh:1128-1145`; `validate-workflow-artifacts.py` traversal; local timing 5.419 s for workflows, 0.347 s for 39 assessments, 1.125 s for 14 releases. | Routine cost grows monotonically with immutable history, while changed current truth receives no stronger priority. | Design changed-path routine validation plus scheduled/release full-history validation, with fail-closed tamper detection and no coverage weakening. | Issue [#176](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/176); owner decision before implementation. |
| DEV-004 | MEDIUM | Twenty-nine `.dev` paths are not packaged but also match no explicit exclusion rule. | `dev-inventory.yaml`; profile resolution at `3a60570d...`. | Current bytes are safely omitted, but owner/classification/reason cannot be reproduced from the profile; #172 cannot prove exhaustive disposition from profile alone. | Have #172 classify the 29 paths and decide whether an explicit disposition registry/schema is required. Do not change package bytes in this assessment. | Issue #172; follow-up only if its inventory selects a schema change. |

## Baseline And Skill Comparison

### Confirmed

- Both passes classify workflow, assessment, release, provider-receipt, and backlog-instance history as source-only evidence.
- Both identify current roadmap/backlog projection drift and active documentation reference drift.
- Native validators pass despite current projection staleness, confirming a coverage gap rather than malformed artifacts.

### Added By Repository-Aware Review

- Live Project #3 already contains v0.11.0 and v0.12.0 options while the source provider contract stops at v0.10.0.
- Twenty-nine `.dev` files are implicit allowlist omissions rather than explicit source-only exclusions.
- Routine critical validation is history-proportional; the workflow validator alone took 5.419 seconds on this revision.

### Corrected

- Git checkout byte counts were rejected because Windows CRLF expansion differs from canonical Git blobs.
- Active link drift is seven occurrences across four canonical target documents, not a count derived from historical broken references.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git tree coverage | passed | 1,011 tracked `.dev` blobs / 5,810,865 Git-blob bytes; entry sums exact. |
| Distribution resolution | passed | 118 `.dev` sources, 129 `.dev` targets after mappings; whole payload 659 targets / digest `9d559dec5d36975305e53bb7ee71403a1e711f76e59a8bf1c63352f86edfd6c1`; no collisions or reference-integrity violations. |
| Assessment artifacts | passed | 39 assessments. |
| Workflow artifacts | passed | 68 post-adoption workflows, 88 indexed workflow directories, 55 backlog items. |
| AI context versions | passed | 14 release records. |
| Current document references | failed | Seven active references point to four moved standards; four named requirement examples are absent. |
| Provider state | passed for read-back | #171 is `In progress / v0.12.0 / Not yet published`; Priority and Owner review remain unset. |

### Environment-Limited Checks

- Temp-writing package/wrapper/adapter tests hit Windows `WinError 5` in the configured temporary directory. They are recorded as `blocked-by-environment`, not passed or failed semantically.
- `validate-ai-context-target.py` is `not-applicable`: this source repository intentionally has no downstream `.dev/ai-context/provenance.yaml`.

## Recommended Action Order

1. Use #175 for DEV-001 and DEV-002; their scope, reviewer, rollback, and validation are cohesive.
2. Use #176 for DEV-003 because it changes validation lifecycle rather than current content.
3. Hand DEV-004 and the exact 29-path list to #172; create no redundant package Issue before that inventory decides the schema need.
4. Feed the identity/alias/history list to #166 without renaming repository history, package IDs, technology profile, namespace, or CLI identity.

## Deferred Items

- Priority for #171: owner decision; `P1 High` is recommended.
- Routine/full historical validation cadence: owner decision in #176.
- Package-disposition schema and any byte changes: #172.
- Product/package/archive/profile identity: #166.
- No immutable workflow, assessment, release, tag, asset, or provider receipt was changed.

## Appendix

### Commands Run

```text
git fetch --prune origin
git ls-tree -r -l 3a60570d0e290f337f2a212d092c6797670528b4 -- .dev
gh project field-list 3 --owner YuChia-Wei --format json
gh project item-list 3 --owner YuChia-Wei --format json --limit 200
python .ai/scripts/validate-ai-context.py
python .ai/scripts/validate-assessment-artifacts.py
python .ai/scripts/validate-workflow-artifacts.py
python .ai/scripts/validate-ai-context-versions.py
python .ai/scripts/validate-source-governance.py
python .ai/scripts/validate-file-disposition-manifest.py --manifest <v0.5.0 disposition manifest>
```

### Notes

- `gh` was executed outside the sandbox as required by the owner.
- Package resolver output describes the current source contract at `HEAD`; it is not a v0.11.0 published-archive read-back.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260809-004/report.md`
- Machine inventory: `.dev/assessments/ASM-20260809-004/evidence/dev-inventory.yaml`
- Stable findings: `ASM-20260809-004#DEV-001` through `#DEV-004`
- Current projection/reference remediation: Issue [#175](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/175); `ai-context-governance`
- Immutable-history validation policy: Issue [#176](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/176); owner decision required before implementation
- Package handoff: Issue #172
- Identity handoff: Issue #166
- Remediation intentionally not performed by this skill: `yes`
