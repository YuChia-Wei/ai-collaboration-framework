# Implementer Taxonomy and Domain Language Workflow

## Metadata

- `plan_id`: `workflow-plan-2026-06-implementer-taxonomy-domain-language`
- `owner_skill`: `dev-workflow`
- `status`: `completed`

## Context

- Problem statement:
  - Implementer skills currently mix architecture-role naming and scope/technique naming, causing routing ambiguity.
  - Domain ubiquitous language needs a target-repository-safe structure, templates, and migration boundary guidance.
- Current scope:
  - Implement two independent requirement streams in one workflow:
    - implementer taxonomy migration;
    - domain ubiquitous language structure.
- Why this workflow now:
  - Requirements have been drafted and updated enough for `dev-workflow` to orchestrate implementation without creating a separate `.dev/specs` document first.

## Requirement Inputs

- `.dev/requirement/SKILL-IMPLEMENTER-NAMING-REQUIREMENTS.MD`
- `src/knowledge/dotnet-backend/requirements/DOMAIN-UBIQUITOUS-LANGUAGE-REQUIREMENTS.MD`

## Target Direction

- Target architecture summary:
  - Scope-first implementer taxonomy:
    - `slice-implementer` for bounded implementation slices;
    - `local-change-implementer` for local class/object/symbol technical changes;
    - command/query/reactor become `slice-implementer` modes/references.
  - Domain ubiquitous language:
    - `.dev/domain-language/` human-facing target-repository truth area;
    - templates only, not product truth;
    - technical glossary and terminology skill remain deferred.
- Key constraints:
  - Use `ai-context-governance` for skill registry, wrapper, guide, and context boundary updates.
  - Use `repo-structure-sync` for target-repository domain language migration boundary updates.
  - Use `ddd-ca-hex-architect` only if DDD ubiquitous language semantics become ambiguous.
  - Remove old skill names directly; do not keep deprecated aliases.
  - Preserve original skill restrictions when migrating them into new skills or mode references.
- Non-goals:
  - Do not create a test implementer skill.
  - Do not create a technical glossary.
  - Do not rewrite historical workflow artifacts.

## Workstreams

### Workstream A: Implementer Taxonomy Migration
- Owner skill:
  - `ai-context-governance`
- Goal:
  - Replace mixed implementer taxonomy with `slice-implementer` and `local-change-implementer`.
- Expected outputs:
  - new canonical skill specs and references;
  - new runtime wrappers;
  - old implementer skill directories removed;
  - command/query/reactor rules preserved as `slice-implementer` modes;
  - registry, guides, root routing, and `dev-workflow` profile updated.

### Workstream B: Domain Ubiquitous Language Structure
- Owner skills:
  - `ai-context-governance`
  - `repo-structure-sync`
- Goal:
  - Create `.dev/domain-language/` structure and update migration boundary guidance.
- Expected outputs:
  - README and templates under `.dev/domain-language/`;
  - context boundary / index updates if needed;
  - repo-structure-sync migration boundary updates.

### Final Validation
- Owner skill:
  - `dev-workflow`
- Goal:
  - Validate JSON, references, deleted skill names, new skill names, domain-language structure, and whitespace.

## Spec Author Assessment

No separate `.dev/specs` document is required before implementation.

Reason:

- The requirements define the user decisions, target names, no-alias policy, domain-language storage root, and non-goals clearly enough.
- The main remaining detail is a migration file map and task execution order, which belongs in this workflow's task JSON rather than a product-style spec.
- If mode contracts become ambiguous during migration, capture them in `slice-implementer` references and escalate only if DDD semantics are unclear.

## Validation Strategy

- Parse workflow task JSON with `ConvertFrom-Json`.
- Run reference searches for old and new skill names.
- Validate domain-language paths and template links.
- Run `git diff --check`.

## Completion Summary

- Completed.
- Workstream A migrated active implementer routing to `slice-implementer` and `local-change-implementer`, with command/query/reactor preserved as `slice-implementer` mode references and old active skill entries removed.
- Workstream B created template-only `.dev/domain-language/` structure and updated `repo-structure-sync` migration boundaries so filled domain vocabulary is treated as target-repository truth.
- `ddd-ca-hex-architect` was not needed because no DDD ubiquitous language semantics became ambiguous; this workflow created templates and governance boundaries only.
