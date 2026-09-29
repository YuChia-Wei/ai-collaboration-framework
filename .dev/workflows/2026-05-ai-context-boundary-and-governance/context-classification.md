# AI Context Classification

This inventory classifies current documentation and AI context by audience, scope, language, and expected action. It is a planning artifact for `workflow-plan-2026-05-ai-context-boundary-and-governance`; it does not move files by itself.

## Classification Rules

| Field | Values |
| --- | --- |
| Audience | `agent`, `human`, `both` |
| Scope | `universal`, `dotnet-backend`, `repo-specific`, `runtime-wrapper` |
| Language target | `en`, `zh-TW`, `bilingual-entry` |
| Action | `keep`, `split`, `move`, `rewrite`, `index-sync`, `defer` |

## High-Level Inventory

| Path | Audience | Scope | Language target | Action | Notes |
| --- | --- | --- | --- | --- | --- |
| `.ai/README.MD` | agent | universal | en | rewrite | Current file is mixed zh-TW/en and should become an English agent-facing entry. |
| `.ai/INDEX.MD` | agent | universal | en | rewrite | Should remain a concise English navigation file. |
| `.ai/DIRECTORY-RULES.MD` | agent | universal | en | rewrite | Current rules are mostly zh-TW and mix `.NET` assumptions with general placement rules. |
| `.ai/assets/README.MD` | agent | universal | en | rewrite | Should describe canonical assets and new tech-stack folders. |
| `.ai/assets/CANONICAL-SCHEMA.MD` | agent | universal | en | keep | Machine-readable asset schema direction is broadly reusable. |
| `.ai/assets/shared/` | agent | universal | en | keep | Universal shared rules only after moving .NET backend-specific files to `tech-stacks/dotnet-backend`. |
| `.ai/assets/tech-stacks/dotnet-backend/` | agent | dotnet-backend | en | keep | New home for .NET backend-only reusable AI context. |
| `.ai/assets/skills/` | agent | mixed | en | split | Skill specs are reusable as structure, but several skills are .NET backend-specific by purpose. |
| `.dev/agents/` | agent | mixed | en | split | Command/query/reactor/aggregate roles are .NET backend-specific; generic role rules can remain shared. |
| `.dev/agents/frontend-sub-agent/` | agent | out-of-scope | en | defer | Frontend role exists but is not part of the .NET backend-only profile; decide later whether it belongs in a separate full-stack template. |
| `.ai/assets/templates/` | agent | universal | en | keep | Template schemas can stay reusable if examples avoid backend-only assumptions. |
| `.ai/scripts/` | agent | dotnet-backend | en | move-or-index | Most scripts validate .NET backend rules and should be grouped or indexed as tech-stack-specific. |
| `.agents/skills/` | agent | runtime-wrapper | en | rewrite | Runtime wrappers should stay thin and English-only. |
| `.claude/skills/` | agent | runtime-wrapper | en | rewrite | Claude wrappers should mirror `.agents` policy and remain thin. |
| `.dev/requirement/` | human | repo-specific | zh-TW | keep | Requirements may use Traditional Chinese Taiwan wording and project-specific truth. |
| `.dev/specs/` | agent | repo-specific | en | keep | Specs are structured execution truth; English is preferred for agent consumption. |
| `.dev/standards/` | both | mixed | en | split | Execution standards should move toward English; human-only explanatory guides can remain zh-TW or get entry translations. |
| `.dev/guides/ai-collaboration-guides/` | human | mixed | zh-TW | split | Human-facing skill guides may use zh-TW; policy-like execution contracts should be English or referenced from standards. |
| `.dev/guides/design-guides/` | human | dotnet-backend | zh-TW | keep | Human-facing .NET backend design guides. |
| `.dev/guides/implementation-guides/` | human | dotnet-backend | zh-TW | keep | Human-facing .NET backend implementation guides. |
| `.dev/operations/` | human | repo-specific | zh-TW | keep | Runtime truth for this distributed backend sample. |
| `.dev/problem-frames/` | agent | repo-specific | en | keep | Machine-readable frame artifacts should remain English. |
| `.dev/workflows/` | both | repo-specific | mixed | keep | Workflow artifacts may use English for machine-readable tasks and zh-TW for human reports as policy allows. |
| `agents.md` | both | repo-entry | bilingual-entry | split | Root agent entry may need `agents.en.md` / `agents.zh-tw.md` policy later. |
| `README.md` | human | repo-entry | bilingual-entry | split | Human entry should support zh-TW; English variant may be useful for agents and external users. |

## Duplication and Boundary Hotspots

- `.ai/assets/tech-stacks/dotnet-backend/shared/` now owns .NET backend-specific shared rules that were previously under `.ai/assets/shared/`.
- `.ai/assets/skills/ddd-ca-hex-architect`, command/query/reactor implementers, and spec compliance validator are strongly tied to the current .NET backend architecture.
- `.dev/agents/frontend-sub-agent` is a real capability but does not fit the declared .NET backend-only profile.
- `.dev/standards/` currently mixes human explanatory material, executable review standards, examples, and backend-specific rules.
- Runtime wrappers are already thin, but their README files are zh-TW and should be English if they are treated as agent-facing runtime context.

## Initial Action Plan

1. Define durable boundary and language policy before moving files.
2. Add dedicated `ai-context-governance` skill so AI documentation cleanup is not routed through BDD or code implementation skills.
3. Keep using `.ai/assets/tech-stacks/dotnet-backend/` for backend-only agent context.
4. Move additional low-risk backend-specific supporting materials in small batches; defer high-link-count moves until indexes are stable.
5. Keep bilingual variants limited to entry files to avoid translation sprawl.
