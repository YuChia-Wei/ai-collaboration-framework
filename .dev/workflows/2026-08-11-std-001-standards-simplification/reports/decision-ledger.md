# STD-001 Round 2 / Round 3 Decision Ledger

## Ledger State

- Status: `approved`
- Owner approval: `approved on 2026-08-11`
- Evidence subject: `main@df7012b6bf6ac360cfb47e2c79813384880665f8`
- Baseline assessment: `ASM-20260811-003`
- Release boundary: no v0.13 record, tag, Release, or publication is authorized by this ledger.

## Stable Findings

| Finding | Severity | Delivery authority |
| --- | --- | --- |
| `ASM-20260811-003#CRL-001` | HIGH | Code Reviewer entry, routing, roles, and .NET review references |
| `ASM-20260811-003#CRL-002` | HIGH | canonical rule ownership, target selection, and semantic equivalence |
| `ASM-20260811-003#GTM-001` | HIGH | governance terminology owners and source/portable release boundaries |
| `ASM-20260811-003#PKG-001` | HIGH | package projection, selected-payload navigation, and archive validation |
| `ASM-20260811-003#CMP-001` | MEDIUM | distribution component identity and selection closure |

## Approved Successor Deliveries

### Delivery A — Code Review Progressive Disclosure

- Online Issue: [#191 — `[STD-001/R2] Make Code Review References File-Type And Finding Scoped`](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/191)
- Findings: `CRL-001`, `CRL-002`.
- Canonical owners: `code-reviewer`, .NET engineering-rule catalog, file-type standards, review role manifests.
- Main change: introduce one compact routing contract; make output/role execution conditional; route file types and findings to canonical rule IDs/owners; remove generic shared files from unconditional role references.
- Compatibility: keep current index/checklist/reference paths as explicit stubs for one declared migration window; do not delete shared common/testing files used by other capabilities.
- Validator: add fixture-driven before/after rule-ID/digest, role, severity, output-contract, missing-route, unrelated-load, byte, and package-reference checks.
- Rollback: one bounded review-routing delivery; no release terminology or package component mutation.

### Delivery B — Governance Term Namespace And Release Projection

- Online Issue: [#192 — `[STD-001/R3] Qualify Governance Terms And Separate Source Release Doctrine`](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/192)
- Finding: `GTM-001`.
- Canonical owners: AI-context ownership registry, workflow/assessment policies, source release/version policy, portable governance projections.
- Main change: register qualified term namespaces and owners; keep definitions in existing owner policies; split source release/publication procedure from target version/provenance/upgrade guidance.
- Compatibility: preserve machine enum strings and historical records; map the portable target version policy to the stable downstream path; add explicit source-to-portable migration records for moved content.
- Validator: terminology-owner/link checks plus existing workflow, assessment, release, handoff, language, and migration tests.
- Rollback: one terminology/projection delivery; no Code Reviewer routing or component selection mutation.

### Delivery C — Selected-Payload Navigation And Component Closure

- Online Issue: [#193 — `[STD-001/PKG] Fail Closed On Broken Payload Navigation And Component References`](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193)
- Findings: `PKG-001`, `CMP-001`.
- Canonical owners: distribution profile, package builder/validator, component mapping, package tests.
- Main change: validate local links against the selected payload after mappings/exclusions; remove or re-route source-only entries from portable indexes/guides; classify the .NET Code Reviewer entry and roles consistently with their mandatory dotnet references.
- Compatibility: keep archive schema and stable target paths; treat component reassignment as migration metadata, not silent deletion; source-only catalog entries may remain only when visibly non-actionable and link-safe.
- Validator: negative fixtures for excluded Markdown targets, unavailable commands, cross-component mandatory references, and default/optional selection closure.
- Rollback: one distribution-only delivery; does not change doctrine or release lifecycle semantics.

These three deliveries change different authorities, validators, compatibility contracts, and rollback units. They should not share one implementation PR merely because they originate from #61. Parent #61 remains the coordination Issue for the before/after v0.13 inventory and final candidate user review.

## Move / Delete Authorization Matrix

| Candidate content | Canonical owner | Replacement entry | Compatibility / migration | Successor / implementation state |
| --- | --- | --- | --- | --- |
| full Code Review index examples and repeated rules | file-type routing contract plus canonical standards | stable `CODE-REVIEW-INDEX.MD` compatibility entry | stub first; removal only after declared migration window | #191 created; implementation pending separate authorization |
| `checklist-reference.md` duplicated detection text | routing contract | stable stub linking to route | package reference and wrapper migration | #191 created; implementation pending separate authorization |
| monolithic checklist sections | existing file-type standards / rule catalog | type and finding routes | rule-ID/digest equivalence required | #191 created; implementation pending separate authorization |
| role prompt/playbook duplicated checklists | role manifest plus targeted owner refs | one bounded role instruction | preserve role ID/applicability/stop conditions | #191 created; implementation pending separate authorization |
| Code Reviewer references to shared common/testing | shared files remain for other consumers | finding-specific rule/section route | no global file deletion | #191 created; implementation pending separate authorization |
| source release procedure inside target version guidance | source-only release policy | portable target version/provenance projection | stable target path; explicit source projection mapping | #192 created; implementation pending separate authorization |
| package links to excluded source files | selected portable owner or non-actionable source-only note | link-safe target | package negative fixtures | #193 created; implementation pending separate authorization |
| Code Reviewer core component classification | `dotnet-backend` component | component-closed selection | migration metadata preserves managed files | #193 created; implementation pending separate authorization |

## Owner Decisions And Issue Creation

1. The owner approved the three-delivery split on 2026-08-11.
2. The owner approved extending the existing AI-context ownership registry for governance-term routing instead of creating a terminology-specific skill or a second definition authority.
3. Successor Issues #191, #192, and #193 were created and read back as open with the approved scope and labels.
4. Repository automation added all three Issues to Project #3 in `Inbox`; no Priority, Target release, Owner review, Published in, or other Project field was configured by this workflow.
5. Keep #61 open as v0.13 coordination until successor before/after evidence and the real governed v0.13 package-candidate review are complete.
