# Initialization and model maintenance coverage

This is the owner's requested bounded assessment during the #322/#434/#435
continuation. It describes source resources and the current source-project
installation, not downstream execution or a new accepted product design.

## Source policies are not generated product defaults

`.dev/standards/README.md`, `AI-CONTEXT-BOUNDARY.md` and
`AI-CONTEXT-OWNERSHIP.md` explicitly own this source repository's rules.
Current package metadata and the initialization source do not generate the
22 tracked files under `.dev/standards`. The current init structure map does
not supply a `.dev/standards` kit. For example, source development and commit
policies were reconciled by source commit `3ca6756c`; this is project history,
not proof of a portable initializer producing those files.

The installed `.ai/custom/installation.json` selects 17 skills, both adapters
and no knowledge. It does not select `ai-context-init`. There is consequently
no installed `.ai/core/skills/ai-context-init` directory. Absence there is not
absence of the source/package capability; conversely, a template in `src` is
not an initialized target policy.

The owner confirms that the prior #435 disposition's retained `.dev` history
is source-project knowledge, not a downstream product or a release blocker by
itself. That historical record remains unchanged. The selected external-AI
intake method is removed from common knowledge and its package declarations;
it is not replaced with an invented automatic retrospective facility.

## Existing portable resources

| Need | Current owner and exact resources | Coverage and limit |
| --- | --- | --- |
| Establish root collaboration guidance | `src/skills/ai-context-init/SKILL.md`, `references/initialize.md`, `templates/public-root/AGENTS.md` | Initialize or factual refresh; baseline precedence, scope, progressive loading, authorization, changes and truthful validation. Instruction-based authoring with normal file tools. |
| Human/runtime entry | Init `templates/public-root/README.md`, `CLAUDE.md` | Seeds requiring target facts and actual routes; no finished target environment. |
| `.dev` use and folder map | Init `references/project-structure.md`, `templates/public-catalogs/dev/README.MD`, `INDEX.md` | Optional responsibility/destination map and navigation seeds. Existing layouts win; no folder is required merely to match the example. |
| Repository/product technical inventory | Init `templates/project-config.template.yaml` | Optional evidence-backed repository, languages, constraints, roots, modules, runtime hosts, architecture, validation and documentation inventory. Not a framework configuration schema or shared automatic input contract. |
| Architecture and technology facts | Init `templates/architecture.md`, `templates/technology-requirements.md` | Authoring seeds; distinguish observed facts, accepted constraints and unknowns. |
| Product requirements and detailed specifications | `requirement-author`, `spec-author` with their declared resources | Separate requested artifacts and selected destinations; not automatic project-config generation. |
| Existing context/rule maintenance | `ai-context-governance` `propose` / `apply` | Maintain authorized project-owned content and rules. Preserve managed files; no installed package bypass. |
| Learning and decisions | `lesson-author`, `adr-author`; governance/orchestrator knowledge handoffs | Record evidence-qualified learning or decisions. No compulsory external AI consultation and no implemented automatic whole-workflow retrospective service. |

The optional project inventory is created/refreshed by `ai-context-init`; a
selected factual refresh remains there. Ongoing rule, ownership or maintenance
changes default to `ai-context-governance`. The original author is not a
permanent exclusive owner. No current package turns project-config into
automatic authority or requires every skill to parse it.

## First-team onboarding gaps

There is a usable minimum root entry and a structure map, but no complete
collaboration starter kit. The source catalog does not provide ready-to-adapt
team templates for branch/commit/PR cooperation, work-record lifecycle and
handoff, risk-based review/validation, or a routine reflection process tying
observations to Lessons/ADRs and authorized policy maintenance.

The current project-config seed is technical inventory. It lacks explicit
product purpose, intended users, business scope/non-goals and a clear mapping
to authoritative product requirements. Those can be authored elsewhere by
existing skills, but the introductory experience does not connect them into
one guided start. A team must currently select and compose these decisions.

Recommended bounded product direction, not implemented/adopted here: extend
`ai-context-init` with optional collaboration-plan and product-context seeds,
clear owners/navigation and a small first-task example. Keep reusable methods
in source, initialized documents target-owned, and governance/ADR/Lesson roles
distinct. Do not transplant this source project's Issue numbers, U001, leases,
release gates or mandatory GitHub structure. A `.dev/standards` destination
can be a suggested target convention rather than a universal requirement.

Whether this fuller starter kit is required for stable 0.19.0 is an owner
product-scope decision; existing local tests or historical policy retention do
not answer it. This is the material product gap identified by the request.

## Sub-agent maintenance

Current mechanisms already provide optional model-list discovery in the subset
CLI, explicit component selection, subset derivation, managed plan/apply and
drift checks. `ai-context-governance` can maintain authorized project-owned
runtime settings. No dedicated sub-agent/model maintenance skill exists in
the 18-skill catalog.

The selected repair separates role behavior from model generations. Policy 2
roles omit Codex model/effort/provider keys and use Claude `model: inherit`.
Discovery returns observations without pinning a model into their selection.
Users can change the runtime's normal model setting without editing managed
role files, so routine upstream model releases need no framework release.
Global/per-invocation overrides still require disclosure and user-selected cost
boundaries; inheritance is not a billing enforcement mechanism.

A dedicated skill is unnecessary for the ordinary inherit/update case. If
teams need per-role, per-runtime persistent overrides, a bounded extension to
the existing maintenance CLI would be preferable to another installer: inspect
effective settings, preview explicit changes, keep choices target-owned and
preserve them across role updates. This capability is not implemented by the
current repair. Do not claim generic merge/recovery for manually edited managed
profiles or infer consent to choose a higher-cost model from availability.
