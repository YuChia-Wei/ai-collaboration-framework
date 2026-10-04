# Documentation disposition

Input commit: `b52c68d64373bb54688109b9174bd4a9cea2b577`. Scope: tracked `.dev/guides`, `.dev/contracts`,
`.dev/standards` documents (48 input files); existing historical exception roots
are not cleaned. Product metadata, product manuals and root navigation are
updated only to close the selected placement/reference change.

Useful methods are retained in `src/knowledge/engineering-common/references/`:
context ownership, technology selection, skill/role taxonomy and external AI
intake. Human guide authoring is in `docs/maintaining-documentation.md`.

| Input document | Disposition | Evidence/rationale |
| --- | --- | --- |
| `.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/CLI-EXECUTION-ROUTING-CONTRACT.md` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/ROLE-EXECUTION-CONTRACT.md` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/VALIDATION-DEPENDENCY-OBSERVATION-CONTRACT.md` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/agent-execution-guardrails.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/cli-execution-routing.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/provider-neutral-capability-registry.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/provider-neutral-capability-registry.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/provider-projection-registry.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/provider-projection-registry.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/validation-dependency-observation.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/validation-evidence-lifecycle.schema.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/contracts/validation-gate-classification.yaml` | retain | Source execution/binding or unique compatible-record schema semantics; no ordinary-source/tool availability is inferred. |
| `.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md` | remove after extraction | Obsolete .ai/assets layout; reusable ownership/placement now in source context method. |
| `.dev/guides/ai-collaboration-guides/AI-SKILL-GUIDE-STANDARDS.md` | remove after extraction | Obsolete human-guide owner and wrapper layout; guide-writing method preserved in docs/maintaining-documentation.md. |
| `.dev/guides/ai-collaboration-guides/EXTERNAL-AI-DISCUSSION-ROUNDTRIP-GUIDE.md` | remove after extraction | Reusable method moved into source, dropping obsolete version deadlines and mandatory source-project workflow intake. |
| `.dev/guides/ai-collaboration-guides/PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md` | remove | Commands and registry unavailable; current prerequisites already documented by installation manual and source policy. |
| `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md` | remove after extraction | Taxonomy preserved in source without retired role layout or source-project dependencies. |
| `.dev/guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md` | retain | Experience value: explains retirement/restoration decisions and current responsibility boundaries. |
| `.dev/guides/design-guides/MULTI-STACK-CONTEXT-PLACEMENT-NOTES.md` | remove after extraction | Unadopted obsolete layout exploration; reusable profile boundary/maintenance criteria preserved in source ownership method. |
| `.dev/guides/implementation-guides/FRAMEWORK-RELEASE-DRAFT-GUIDE.md` | retain | Source-project draft packaging/release procedure with current actual tooling. |
| `.dev/guides/implementation-guides/PORTABLE-TEST-FIXTURE-ACCELERATION-GUIDE.md` | remove after extraction | Retired classifier/runner examples; safety and evidence distinctions preserved in root/source policy and protected historical records. |
| `.dev/standards/AI-CONTEXT-BOUNDARY.md` | rewrite | Current source-project ownership/navigation replaces obsolete portable-layout assertions. |
| `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/AI-CONTEXT-OWNERSHIP.md` | rewrite | Current source-project ownership/navigation replaces obsolete portable-layout assertions. |
| `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml` | retain | Selected compatibility/record interpretation or retained U001 owner obligations; excluded historical records retain this meaning. |
| `.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml` | retain | Selected compatibility/record interpretation or retained U001 owner obligations; excluded historical records retain this meaning. |
| `.dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/AI-CONTEXT-VERSION-POLICY.md` | remove after extraction | Compatibility notice points exclusively to removed portable owner; release/support separation already in source release policy. |
| `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/DEPENDENCY-VERSION-CONSISTENCY-POLICY.md` | remove after extraction | Unavailable legacy offline gate and removed template; source policy owns current pinned checks, source evidence method preserves consistency/currency distinction. |
| `.dev/standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md` | retain | Selected compatibility/record interpretation or retained U001 owner obligations; excluded historical records retain this meaning. |
| `.dev/standards/GIT-COMMIT-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/GIT-COMMIT-POLICY.yaml` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/INDEX.MD` | rewrite | Current source-project ownership/navigation replaces obsolete portable-layout assertions. |
| `.dev/standards/README.md` | rewrite | Current source-project ownership/navigation replaces obsolete portable-layout assertions. |
| `.dev/standards/SOURCE-DEVELOPMENT-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/TECHNOLOGY-SELECTION-POLICY.md` | remove after extraction | Reusable method migrated to engineering-common; this framework source is not a downstream .NET application. |
| `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/WORKFLOW-GATE-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |
| `.dev/standards/WORKFLOW-HANDOFF-POLICY.yaml` | retain | Active source-project policy/configuration or selected compatible source records; source development policy resolves ordinary-source applicability. |

## Historical references and compatibility

The two rule catalogs retain old `.dev`/`.ai/assets` paths only inside historical
provenance, never as required members or active document links. They retain full
source identity and describe that provenance as inert. Current semantic owners,
profile documents and cross-package links resolve inside product source.

Do not rewrite the five excluded roots or release/support history to update
removed paths. Retrieve historical bytes with `git show <input-commit>:<path>`.
Retained compatibility schemas preserve unique record interpretation; deleting
a retired ordinary gate does not authorize deleting its tooling or evidence.
No legacy validator restoration, core generation or installation is performed.

## Remaining project/product documentation

The tracked `.dev` entries outside the three reviewed documentation areas and
five excluded history roots were inventoried separately. Keep the repository
rename compatibility notice (ongoing identity/support responsibilities), Git flow
(current source collaboration), environment policy (actual source bindings), and
two evidence-backed lessons with their indexes (experience-transfer value).
`docs` manuals remain product documentation with their explicit RC4/source
version boundary. Obsolete paths in the current `.dev` navigation were removed;
no release/support/history corpus was reconstructed or removed.

The ten removed documents have their useful methods extracted first where
needed. Existing compatibility schemas and registry content remain unique
record-interpretation evidence, qualified by the adopted source policy. The
catalogs no longer register removed skill consumer routes as current bindings;
this does not invent replacement routing or reinstall a capability.
