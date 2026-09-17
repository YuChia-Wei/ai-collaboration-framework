# Skill Cost And Messaging Baseline

## Metadata
- assessment_id: ASM-20260917-23-c18
- assessment_type: ai-context-audit
- owner_skill: ai-context-auditor
- status: final
- created_at: 2026-09-17T23:54:11+08:00
- updated_at: 2026-09-17T23:54:11+08:00
- template_source: .ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md
- template_version: 2.2.0
- subject_commit: f643b56cd68faec590f23a8c8a7436f813285e5d

## Scope And Method
This newly retained baseline records the pre-remediation source; it does not retroactively rename the preceding conversation as an assessment. Included: root guidance and selected skill/profile/runtime documents. Excluded: product source/tests, secrets, generated dependencies, broad historical archives. Pass A considered capability cohesion, task startup cost and risk proportionality independently of repository compliance. Pass B checked canonical ownership/routing and existing evidence contracts. Codebase Memory excludes relevant roots, so scoped Git inventory/direct files supply primary evidence.

## Strengths
Canonical/profile/target/runtime ownership is explicit. Review routing already loads selected file types and preserves target choices. Failure and actual-execution boundaries protect truthful reporting.

## Findings
### F-001 — MEDIUM: capability dispersion and startup indirection
Sixteen skills have separate canonical YAML and runtime wrappers; review-specific roles reside in the global role tree. The aggregate review role is bound by code-reviewer and points back to its routing. Root guidance has 12,035 characters; the role execution contract has 16,595. These are file metrics, not measured prompt tokens or proof of quality loss. Consolidate skill-private assets and test an executable progressive entry; shared standards stay shared. Owner: ai-context-governance.

### F-002 — MEDIUM: execution controls exceed some routine task risks
AGENTS requires a full packet/lease for every delegation. IMPLEMENTATION-SCOPE-ROUTING-CONTRACT always excludes class/interface extraction from local work, even for a settled private implementation detail. The rules are internally intentional, not evidence of unauthorized behavior. Propose risk-scoped ordinary execution and private-type boundaries while retaining authority, one-writer, terminal and real-execution protections. Owner: ai-context-governance.

### F-003 — MEDIUM: transactional messaging completion and lifetime gaps
Terra's read-only review of the supplied proposal found usecase-standards lines 175-218/258 and repository-standards lines 167-190 need explicit separation of orchestration/declaration from the one transaction completion owner. Existing guidance covers aggregate/outbox and generic duplicate handling but lacks inbox receipt versus completion, native anti-duplication, EF context/Factory identity, and detailed idempotency/disposition contracts. The supplied report's 10 exported artifact hashes matched; historical tests are not a fresh framework gate. Owner: ai-context-governance with architecture/content review.

## Comparison And Limitations
Pass B confirms F-001/F-002 are improvement hypotheses, not ordinary policy violations. F-003 combines existing correct boundaries with actual coverage gaps; do not discard existing aggregate or target-selection protections. No runtime A/B, source test suite or downstream execution was performed by this baseline. No critical finding or quantified savings claim is made.

## Next Action
Implement under `2026-09-17-v018-cost-and-messaging`, measure matched Terra/Luna tasks, and obtain a separate final-subject verification. This baseline remains immutable.
