# Workflow Plan

## Metadata

- `plan_id`: `workflow-plan-2026-04-14-legacy-decision-portability-consolidation`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `completed`

## Context

- Problem statement:
  - The repository still stores many architectural and collaboration decisions as legacy decision records under `.dev/adr/`.
  - The target direction is to retire those records as day-to-day entry points by landing their active guidance into portable `.ai` assets or `.dev` standards/guides, while keeping only minimal decision-governance rules if needed.
- Current scope:
  - `.dev/adr/`
  - `.dev/standards/`
  - `.dev/guides/`
  - `.ai/`
  - related wrapper and workflow references only when needed for traceability
- Why this workflow now:
  - The repo is being prepared as a reusable prompt and documentation framework for new or existing projects.
  - Reusable rules, constraints, and patterns need stable canonical locations instead of legacy-record-first discovery.

## Target Direction

- Target architecture summary:
  - Legacy decision content is classified into one of four canonical landing zones:
    - `.ai/` portable agent-facing rules, prompt assets, and reusable decision packages
    - `.dev/standards/` normative framework rules, checklists, and single source of truth
    - `.dev/guides/` human-facing usage guides, rationale, and pattern application tutorials
    - retired historical record or deletion when the legacy source no longer carries reusable value
- Key constraints:
  - Do not keep legacy decision records as duplicated active truth after landing the same rule elsewhere.
  - Do not move project-specific truth into `.ai/`.
  - Preserve traceability from each landed rule back to the originating legacy source until migration is complete.
  - Prefer one canonical target per rule family; avoid splitting one small rule across too many files.
- Non-goals:
  - Do not rewrite business/domain requirements as part of this workflow.
  - Do not redesign the repo architecture model itself unless a real rule conflict is discovered.
  - Do not bulk-convert every historical decision record if it has no ongoing reusable value.

## Legacy Decision Classification Matrix

### Bucket A: Portable Agent-Facing Rule
- Target:
  - `.ai/assets/shared/`
  - `.ai/assets/skills/`
  - `.dev/agents/`
  - `.ai/README.MD`, `.ai/SUB-AGENT-SYSTEM.MD`, or similar agent entry docs
- Use when:
  - The source record defines prompt architecture, sub-agent routing, reusable generation/review rules, or cross-agent canonical asset structure.
- Example types:
  - sub-agent modularization
  - skill/sub-agent boundaries
  - prompt portability rules

### Bucket B: Framework Standard / Constraint
- Target:
  - `.dev/standards/`
  - `.dev/ARCHITECTURE.MD`
  - `src/knowledge/dotnet-backend/requirements/TECH-STACK-REQUIREMENTS.MD`
  - `AGENTS.md` when the rule must remain repo-entry baseline
- Use when:
  - The source record defines mandatory structure, naming, dependency rules, architecture constraints, or reviewable coding requirements.
- Example types:
  - project structure
  - DI rules
  - repository constraints
  - outbox requirements
  - test isolation constraints

### Bucket C: Pattern Usage Guide
- Target:
  - `.dev/guides/design-guides/`
  - `.dev/guides/implementation-guides/`
  - `.dev/guides/ai-collaboration-guides/`
  - `.dev/standards/rationale/` when rationale needs a stable companion doc
- Use when:
  - The source record explains how and when to apply a pattern, not just that the pattern is mandatory.
- Example types:
  - profile configuration guidance
  - Docker restore cache usage
  - framework API integration walkthrough
  - AI collaboration workflow usage

### Bucket D: Historical / Delete
- Target:
  - remove after landing, or keep only if it still provides necessary decision history not duplicated elsewhere
- Use when:
  - The source record is superseded, migration-only, translation-only, tooling-history-only, or too project-specific to remain in the portable set.

## Conversion Workflow

### Stage 1
- Goal:
  - Build a legacy decision inventory and classify each source record into A/B/C/D.
- Scope:
  - Review every legacy decision record and record:
    - rule family
    - current status
    - portability level
    - target landing document
    - retire/keep decision
- Non-goals:
  - no content rewrite yet
- Risks:
  - one source record may contain multiple rule families and require splitting
  - historical non-.NET wording may hide the actual .NET canonical rule
- Recommended implementer:
  - main agent locally
- Sub-agent policy:
  - optional `explorer` sub-agent only if the legacy decision set becomes too large for fast inventorying

### Stage 2
- Goal:
  - Normalize landing zones before moving content.
- Scope:
  - Create or adjust missing canonical documents so each rule family has a clear destination.
  - Resolve overlaps such as:
    - `.ai` vs `.dev/standards/prompts`
    - `.dev/guides/*` vs `.dev/standards/rationale`
    - repo-entry docs vs deep implementation guides
- Non-goals:
  - no full source-record retirement yet
- Risks:
  - duplicated concepts already exist in multiple standards/guides
- Recommended implementer:
  - `ddd-ca-hex-architect`
- Sub-agent policy:
  - use sub-agents only for bounded, non-overlapping inventory comparisons

### Stage 3
- Goal:
  - Land active legacy decision rules into canonical docs.
- Scope:
  - Rewrite legacy decision content into:
    - concise normative rules in `.dev/standards/`
    - usage tutorials in `.dev/guides/`
    - portable agent-facing assets in `.ai/`
  - Add explicit cross-references where one rule needs both a standard and a guide.
- Non-goals:
  - no deletion until landing is validated
- Risks:
  - language drift between the original wording and the new canonical doc
  - accidental movement of project-specific truth into portable docs
- Recommended implementer:
  - `staged-refactor-implementer`
- Sub-agent policy:
  - allowed when write scopes are disjoint:
    - one worker for `.ai/`
    - one worker for `.dev/standards/`
    - one worker for `.dev/guides/`

### Stage 4
- Goal:
  - Validate that each retired legacy source has an exact canonical replacement or is intentionally removed.
- Scope:
  - Update `.dev/adr/INDEX.md`
  - annotate retirement status
  - remove duplicate active guidance
  - keep only governance files and any historical records that still carry irreplaceable context
- Non-goals:
  - no new architecture redesign
- Risks:
  - broken references from guides, standards, wrappers, or prompts
- Recommended implementer:
  - `code-reviewer`
- Sub-agent policy:
  - use review-oriented sub-agents if checking separate areas in parallel

### Stage 5
- Goal:
  - Package the result as a portable baseline workflow.
- Scope:
  - Update portability notes and transfer checklist
  - add a concise migration guide for future repos:
    - what to keep
    - what to regenerate
    - what to delete
- Non-goals:
  - no project-specific requirement/spec rebuild
- Risks:
  - migration guidance may still assume this repo's example domains
- Recommended implementer:
  - `ddd-ca-hex-architect`

## Decision Rules Per Source Record

For each source record, decide in this order:

1. Is the active value a hard rule?
   - Yes: land in `.dev/standards/` or `AGENTS.md`.
2. Is the active value agent-facing and reusable across repos?
   - Yes: land in `.ai/`.
3. Is the active value mostly "how to apply this pattern"?
   - Yes: land in `.dev/guides/`.
4. Is the content only historical, superseded, migration-only, or project-bound?
   - Yes: retire or delete.

If one source record contains both a hard rule and a tutorial:
- split it:
  - rule goes to `.dev/standards/` or `.ai/`
  - tutorial/rationale goes to `.dev/guides/` or `.dev/standards/rationale/`

## Validation Strategy

- Reviewer checkpoints:
  - every active decision family maps to exactly one primary canonical target
  - no portable `.ai/` file contains project-specific truth
  - no standard doc mixes tutorial-heavy usage content with mandatory rules unless the split would be artificial
  - no retired source record remains the only discoverable source of an active rule
- Tests/validation expectations:
  - link/reference sanity check across updated docs
  - migration boundary review against `.ai/assets/skills/repo-structure-sync/references/migration-boundaries.md`
  - terminology review to remove stale non-.NET-first wording where .NET canonical docs already exist

## Suggested Task Breakdown

1. `legacy-decision-inventory-and-bucketing`
   - Produce the inventory table and target mapping.
2. `landing-zone-normalization`
   - Create/merge/split canonical destination docs before content moves.
3. `legacy-decision-landing-ai-assets`
   - Move agent-facing reusable rules into `.ai/`.
4. `legacy-decision-landing-standards-and-guides`
   - Move human-facing standards/guides into `.dev/`.
5. `legacy-decision-retirement-and-index-cleanup`
   - Update the decision archive index and retire duplicates.
6. `portable-baseline-finalization`
   - Update packaging notes and transfer checklist.

## Sub-agent Use Policy

- Do not use sub-agents for the initial architecture decision itself.
- Use sub-agents only after the landing matrix and target documents are fixed.
- Good delegation candidates:
  - inventorying legacy decision metadata
  - comparing duplicate rule coverage between standard docs
  - migrating disjoint document sets
  - review passes on separate trees
- Avoid delegation when:
  - deciding canonical ownership for a rule family
  - resolving conflicts between `.ai`, `.dev/standards`, and `.dev/guides`

## Notes

- Completion note:
  - all workflow task artifacts are marked `done`;
  - active guidance was moved into canonical `.ai` assets or `.dev` standards/guides;
  - remaining questions are future governance considerations, not incomplete workflow tasks.
- Open questions:
  - whether `.dev/standards/prompts/` should remain as a human-facing prompt catalog or be reduced after `.ai/assets/` becomes the stronger canonical prompt source
  - whether some low-value historical decision records should be deleted immediately instead of being migrated
- Dependencies:
  - `.ai/assets/skills/repo-structure-sync/references/migration-boundaries.md`
  - `.dev/adr/README.md`
  - `.dev/adr/INDEX.md`
  - `.ai/DIRECTORY-RULES.MD`
  - `.ai/SUB-AGENT-SYSTEM.MD`
