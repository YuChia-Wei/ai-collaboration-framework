# Legacy Decision Inventory

## Purpose

This inventory is the Stage 1 artifact for `workflow-plan-2026-04-14-legacy-decision-portability-consolidation`.
It maps the current legacy decision set to landing buckets and primary canonical targets so later migration work can proceed without re-deciding ownership.

## Bucket Legend

- `A`
  - portable agent-facing rule in `.ai/`
- `B`
  - framework standard or hard constraint in `.dev/standards/`, `.dev/ARCHITECTURE.MD`, `.dev/requirement/`, or `AGENTS.md`
- `C`
  - pattern usage guide in `.dev/guides/` or `.dev/standards/rationale/`
- `D`
  - retire/delete after landing or because the value is only historical

## Inventory Table

| Focus | Current Status | Bucket | Primary Landing Target | Notes |
| --- | --- | --- | --- | --- |
| Use case package and namespace structure | Landed in Standards | B | `.dev/standards/project-structure.md` | Keep as standard only; legacy source can retire after reference cleanup. |
| ORM configuration location | Landed in Standards | C | `src/knowledge/dotnet-backend/guides/PERSISTENCE-CONFIGURATION-GUIDE.md` | Usage/application guidance, not a top-level portable AI asset. |
| DI and configuration structure | Landed in Standards | B | `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` | Historical non-.NET naming should be normalized when references are cleaned. |
| AI task execution SOP | Landed in Standards | C | `.dev/guides/ai-collaboration-guides/AI-COLLABORATION-WORKFLOW-GUIDE.md` | Keep workflow rules in guide form; repo-entry minimum may stay in `AGENTS.md`. |
| Command/query sub-agent separation | Landed in Standards | A | `.ai/SUB-AGENT-SYSTEM.MD` | Agent-facing routing rule. |
| Explicit service registration | Landed in Standards | B | `.dev/standards/coding-standards/usecase-standards.md` | Normative rule should stay in standards rather than only in guides. |
| Outbox pattern implementation | Landed in Standards | B+C | `.dev/standards/coding-standards.md` | Split normative rules to standards; keep implementation walkthrough in a guide. |
| Archive/query model implementation | Landed in Standards | B | `.dev/standards/coding-standards/archive-standards.md` | Standardized pattern rules. |
| Aggregate field initialization pattern | Landed in Standards | B | `.dev/standards/coding-standards/aggregate-standards.md` | Hard modeling rule. |
| Outbox mapper completeness requirement | Landed in Standards | B+C | `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md` | Split mapper requirements into standards if not already explicit enough. |
| Test isolation and domain event mapper | Landed in Standards | B | `.dev/standards/coding-standards/test-standards.md` | Test constraint. |
| Mutation testing exclusion policy | Landed in Standards | B | `.dev/standards/coding-standards.md` | Constraint/policy. |
| Reactor interface definition | Landed in Standards | B | `.dev/standards/coding-standards/reactor-standards.md` | Hard architectural interface rule. |
| Transaction outbox pattern | Landed in Standards | B | `.dev/standards/coding-standards.md` | Rule-level source. |
| Profile/environment configuration loading | Landed in Standards | B | `.dev/standards/coding-standards/profile-configuration-standards.md` | Hard environment/config rule. |
| Mapper serialization requirements | Landed in Standards | B | `.dev/standards/coding-standards/mapper-standards.md` | Hard mapper rule. |
| Audit fields in event metadata | Landed in Standards | B | `AGENTS.md` | Repo-entry baseline constraint. |
| Profile-based dependency injection | Landed in Standards | B+C | `.dev/standards/coding-standards/profile-configuration-standards.md` | Keep hard rules in standards and usage guidance in implementation guides. |
| Sub-agent prompt modularization | Landed in Standards | A | `.ai/SUB-AGENT-SYSTEM.MD` | Agent-facing asset structure rule. |
| Shared project classification | Landed in Standards | B | `.dev/standards/project-structure.md` | Structural rule. |
| Solution folder structure | Landed in Standards | B | `.dev/standards/project-structure.md` | Structural rule. |
| Docker restore-cache csproj copy rule | Landed in Standards | C | `.dev/guides/implementation-guides/DOCKER-RESTORE-CACHE-GUIDE.md` | Pattern usage guide. |
| Script generation from markdown documentation | Landed in Standards | A | `.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md` | Portable agent-facing script workflow. |

## Multi-Bucket ADRs That Must Be Split

These ADRs should not migrate as one-to-one copies because they contain both rules and usage/tutorial content:

| Decision Family | Split Strategy |
| --- | --- |
| Outbox pattern | Put must-follow outbox constraints in standards; keep implementation steps and testing walkthrough in a design/implementation guide. |
| Outbox mapper completeness | Put mapper completeness requirements in standards if missing; keep framework-specific integration flow in guide form. |

## Early Normalization Findings

### 1. `.ai` vs `.dev/standards/prompts`

- Prompt architecture and reusable agent instructions should keep converging on `.ai/assets/`.
- Human-facing prompt catalogs can remain in `.dev/standards/prompts/` only if clearly marked as wrapper or usage examples, not canonical prompt source.

### 2. Historical naming still leaks into current docs

- Some configuration-related files still use non-.NET legacy naming.
- These should be treated as historical filenames or renamed when reference cleanup is safe.

### 3. Some guide targets currently hold normative rules

- Explicit registration and profile-specific DI both still had guide-heavy coverage.
- During Stage 2, decide whether these need a companion standards/checklist file so hard rules are not buried only in prose guides.

## Recommended Retirement Order

1. Retire AI-asset ADRs after `.ai` references are confirmed.
2. Retire pure standards ADRs after standards docs are cross-linked and complete.
3. Retire guide-oriented ADRs after guide/checklist split is normalized.
4. Keep only governance files in `.dev/adr/` unless a genuinely active architecture decision remains uncaptured elsewhere.
