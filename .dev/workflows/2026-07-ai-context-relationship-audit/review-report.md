# AI Context Relationship Audit Report

## Evidence Used

- Root entry docs: `README.md`, `README.en.md`, `agents.md`, `agents.zh-tw.md`
- Governance standards: `.dev/standards/AI-CONTEXT-BOUNDARY.md`, `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`, `.dev/standards/WORKFLOW-GATE-POLICY.md`, `.dev/standards/GIT-COMMIT-POLICY.md`
- Canonical AI assets: `.ai/INDEX.MD`, `.ai/README.MD`, `.ai/DIRECTORY-RULES.MD`, `.ai/SUB-AGENT-SYSTEM.MD`, `.ai/assets/**`
- Runtime wrappers: `.agents/skills/**`, `.claude/skills/**`
- Project governance docs: `.dev/README.MD`, `.dev/INDEX.md`, `.dev/guides/**`, `.dev/specs/**`, `.dev/requirement/**`, `.dev/operations/**`, `.dev/workflows/**`
- Mechanical scans:
  - `rg --files -uu .ai .dev .agents .claude -g "*.md" -g "*.MD" -g "*.yaml" -g "*.yml" -g "*.json"`
  - targeted `rg -n -uu` searches for context paths, stale runtime roots, TODO markers, retired assets, and missing wrapper names
  - PowerShell referenced-path existence check over `.ai`, `.dev`, `.agents`, `.claude`, and root entry docs
- Sub-agent audits:
  - `.ai/**` canonical assets: score `76/100`
  - `.agents/**` and `.claude/**` runtime wrappers: score `94/100`
  - `.dev/**` governance and project knowledge docs: score `68/100`

## Classification Summary

| Area | Audience | Dominant Scope | Language State | Action |
| --- | --- | --- | --- | --- |
| Root entry docs | both | repo-specific / framework entry | bilingual-entry | keep, index-sync |
| `.ai/**` | agent | universal, dotnet-backend, skill, sub-agent | mixed `zh-TW` / `en` | rewrite, split, index-sync |
| `.agents/**` | agent | runtime-wrapper | en | keep |
| `.claude/**` | agent | runtime-wrapper | en | keep |
| `.dev/standards/**` | agent / human | universal, dotnet-backend, repo-specific | mostly en with some mixed docs | keep, rewrite selectively |
| `.dev/guides/**` | human | mixed human guide / dotnet-backend | zh-TW or en allowed | keep, index-sync |
| `.dev/specs/**` | agent / human | repo-specific templates and specs | en | index-sync, defer |
| `.dev/operations/**` | human / agent | repo-specific operations truth templates | mixed | rewrite, defer |
| `.dev/workflows/**` | agent / human | workflow state / historical record | mostly en | keep, defer archival references |

## Overall Score

Overall AI context governance score: `76/100`.

Scoring weights:

- `.ai/**`: 40%
- `.dev/**`: 40%
- `.agents/**` and `.claude/**`: 20%

Reasoning: `.ai` and `.dev` carry canonical context, governance, and source-of-truth relationships. Runtime wrappers are important but intentionally thin and mostly synchronized.

## Boundary Hotspots

### 1. `.dev` Index And Directory Promises Are Stale

High impact relationship problems are concentrated in `.dev` entry and guide docs:

- `.dev/README.MD` advertises `lessons/`, but the directory is absent.
- `.dev/INDEX.md` points to absent paths such as `requirement/README-UML.md`, `requirement/requirement.md`, `lessons/`, `lessons/dotnet/`, and `legacy/ask/`.
- `src/skills/spec-author/references/spec-guide.md` and `src/skills/spec-author/references/spec-organization-guide.md` describe `.dev/specs/domains/` as the production-spec root, but that subtree is absent.
- `.dev/operations/*-GUIDE.MD` names canonical operation truth files such as `.dev/operations/context-map.md`, `.dev/operations/event-catalog.md`, and `.dev/operations/mq-topology.md`, but those files do not exist.

Action: `index-sync`, then either create explicit templates or rewrite these docs as guide-only placeholders.

### 2. `.ai` Agent-Facing Entry Docs Violate The Language Policy

The `.ai` layer is structurally coherent, but several agent-facing canonical docs are heavily Traditional Chinese mixed with English:

- `.ai/INDEX.MD`
- `.ai/README.MD`
- `.ai/DIRECTORY-RULES.MD`
- `.ai/SUB-AGENT-SYSTEM.MD`
- `.ai/assets/README.MD`
- `.ai/assets/skills/README.MD`
- `.dev/agents/README.MD`

This conflicts with `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`, which sets `.ai/**` default language to English.

Action: `rewrite` English canonical entry docs, and move human-facing zh-TW explanation to `.dev/guides/**` where needed.

### 3. Sub-Agent `human_guide` Fields Point Back Into `.ai`

The `.ai` sub-agent manifests use `human_guide: ".ai/SUB-AGENT-SYSTEM.MD"` across the sub-agent role prompt set. This is a relationship mismatch because the field name says human-facing guide, but the target is an agent-facing canonical `.ai` document.

Examples reported by the `.ai` audit:

- `.dev/agents/aggregate-code-review-sub-agent/sub-agent.yaml`
- `.dev/agents/problem-frame-sub-agent/sub-agent.yaml`
- `.dev/agents/controller-test-sub-agent/sub-agent.yaml`

Action: `rewrite` the field semantics or repoint to `.dev/guides/ai-collaboration-guides/**`.

### 4. `.ai/SUB-AGENT-SYSTEM.MD` Mixes Active Routing With Roadmap And Legacy Notes

The file is useful, but it mixes active canonical routing with migration notes and future assets:

- references retired `.ai/assets/commands/*`
- references future `reconciler-sub-agent/` as TODO
- contains active routing, artifact rules, and role inventory in one large surface

Action: `split` active canonical routing from roadmap or migration notes.

### 5. Runtime Wrappers Are Healthy But Have Drift Surface

The wrapper inventories are in sync:

- `.ai/assets/skills/README.MD`
- `.agents/skills/README.md`
- `.claude/skills/README.md`

All three expose the same 12 skill names. Wrappers are thin and English-only.

The only placement hotspot is duplicated runtime metadata:

- `.agents/skills/ddd-ca-hex-architect/agents/openai.yaml`
- `.claude/skills/ddd-ca-hex-architect/agents/openai.yaml`

Action: `keep`, with optional labeling or rehoming if this metadata becomes ambiguous.

## Recommended Actions

1. Fix `.dev` entry/index references first.
   - Update `.dev/INDEX.md` and `.dev/README.MD` so every advertised directory either exists or is explicitly labeled as a future/template placeholder.

2. Decide the `.dev/specs/domains/` contract.
   - If active production specs are expected, create the subtree and a README/template.
   - If not, rewrite spec guides to describe the current template-only state.

3. Reconcile `.dev/operations/` guide files with actual canonical files.
   - Either create target-repo template files for context map, event catalog, MQ topology, and runbook roots, or downgrade guide wording so it does not promise active operation truth.

4. Normalize `.ai` canonical entry docs to English.
   - Keep canonical agent instructions concise.
   - Move zh-TW explanatory/tutorial content into `.dev/guides/**`.

5. Repoint or rename sub-agent `human_guide` fields.
   - Use actual human-facing `.dev/guides/**` paths, or change the field to an agent-facing reference if the target remains `.ai/SUB-AGENT-SYSTEM.MD`.

6. Split `.ai/SUB-AGENT-SYSTEM.MD`.
   - Keep active sub-agent routing in the canonical file.
   - Move roadmap, TODO, and retired compatibility notes into a workflow record or guide.

## Deferred Items

- Historical workflow references under `.dev/workflows/**` intentionally mention retired scripts, removed source-project specs, old product artifacts, or migration targets. These should not be treated as active broken links unless the workflow is reopened.
- `.dev/project-config.yaml` is expected to be generated by `repo-structure-sync` in a target repository. References to it are acceptable when clearly optional or template-scoped.
- TODO-heavy .NET examples are not automatically context-boundary violations because this repository preserves a dotnet-backend template profile. They should be cleaned only as part of a dotnet-backend template readiness workflow.
- Runtime wrapper duplication across `.agents` and `.claude` is expected. It becomes a problem only if indexes or wrapper content drift from `.ai/assets/skills/**`.

## Validation

- Confirmed workflow mode requirement from `.dev/standards/WORKFLOW-GATE-POLICY.md`.
- Confirmed commit timing and validation expectations from `.dev/standards/GIT-COMMIT-POLICY.md`.
- Used hidden-directory scans with `rg -uu` so `.ai`, `.dev`, `.agents`, and `.claude` were included.
- Performed a referenced-path existence scan and classified expected generated/template paths separately from active broken references.
- No production code or repository content was changed outside workflow audit artifacts.

## Remediation Result

Remediation completed for the active workflow scope.

Updated governance score: `92/100`.

Completed changes:

- High-level README files now explain purpose, scope, and usage, while INDEX files own file and directory catalogs.
- `.dev/INDEX.md` no longer advertises absent active paths such as `lessons/`, `legacy/ask/`, `.gemini/commands/README.md`, or `.github/prompts/README.md`.
- `.dev/specs/domains/` is now documented as a target-repository convention, not an active framework subtree.
- `.dev/operations/` guides now read as authoring/template guidance instead of claiming live runtime truth files exist.
- Selected `.ai` agent-facing entry docs were normalized to English.
- Sub-agent `human_guide` fields now point to `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`.
- `.ai/SUB-AGENT-SYSTEM.MD` now contains active routing and explicitly marks the non-existent reconciler role as non-active.
- Runtime `openai.yaml` metadata files are labeled as runtime metadata, not canonical skill content.

Validation completed:

- `git diff --check`
- active-surface referenced-path existence scan, excluding archival workflow records and retired requirement references
- targeted `.ai` language scan for remediated agent-facing docs
- targeted sub-agent `human_guide` routing scan
- targeted stale entry reference scans
- JSON parsing for workflow task files

Remaining deferred scope:

- Historical workflow records under `.dev/workflows/**` still mention removed legacy paths as part of their archival record.
- Retired or historical requirement documents may still mention removed skill names or old migration targets as historical context.
- TODO-heavy .NET example code remains out of scope for this AI context relationship workflow.
