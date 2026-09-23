# Path, owner and disposition matrix

All observations bind to `b4a147c1bc8ec00fcdb92a7006c142209c61a29f`.
Rows below are proposed transitions, not deletion or activation authority.
A path prefix classifies ownership; it never grants recursive mutation.
Existing project and legacy authorities remain until their stated cutover.

## Product and project surfaces

| Current exact path or bounded set | Current owner / meaning | Proposed disposition and successor | Retirement or activation condition |
| --- | --- | --- | --- |
| `src/skills/<id>/` for the 13 IDs below | Delivered editable product source | Retain; exact declared members map to `.ai/core/skills/<id>/<member>` | Correct shared mapping, candidate and P7 evidence; never edit installed bytes back into source |
| `src/distribution/manifest.yaml`; `src/profiles/{lesson-minimal,knowledge,work-management,collaboration}.yaml` | Shared selection owner; 5 mapped packages | Retain source; add only actual selected members/profiles via assigned owner | #346 permission resolution and subsequent mapping of #356/#357; this proposal makes no edits |
| `src/adapters/codex/skill-entry.md.template` and `src/distribution/codex.py` | Codex generated projection owner | Retain; exact `.agents/skills/framework-<id>/SKILL.md` links to installed entry/metadata/resources | Candidate-selected Codex adapter and byte read-back; no new common launcher |
| `src/distribution/installation_state.py`, `installation_plan.py` | #354 read-only public reader/planner | #359 owns necessary integration with maintenance engine | #359 final source handoff and P7 actual behavior; six reader files do not pin the complete writer |
| Proposed `.ai/core/skills/`, `.ai/framework.lock` (absent) | No inferred existing managed owner | Installer owns only inventory-listed files and actual lock | Selected candidate, all-old drift and collision checks, separate project activation |
| `AGENTS.md`, `AGENTS.zh-TW.md`, `CLAUDE.md`, `README.md`, `README.en.md` | Project rules, language parity, runtime pointer, human source entry | Retain project ownership; apply precise routing proposal in root-bindings.md | Coordinator adoption window; translate changed AGENTS rules with parity; no whole-file seed replacement |
| `.ai/assets/skills/README.MD`, `.ai/INDEX.MD`, `.dev/INDEX.md`, `.agents/skills/README.md`, `.claude/skills/README.md` | Legacy navigation, currently advertises canonical assets | Later annotate per-row installed/source-only/legacy status; retain historical IDs | Shared index owner changes rows with actual cutover; do not claim everything under `.ai/assets` retired |
| `.ai/assets/shared/`, `.ai/assets/tech-stacks/dotnet-backend/`, `.ai/assets/sub-agent-role-prompts/`, `.ai/assets/templates/` | Mixed active legacy reusable rules, references and project selections | Preserve until each real consumer is classified; extracted product meaning gets one `src` owner; source-specific meaning stays project policy | #342 exact rows plus missing #347 scope and P7 guardrail selection; no blanket copy/delete or mandatory .NET import |
| `.ai/scripts/`, `.ai/distribution/` | Legacy consumer mechanics plus source build/release/validation owners | Keep source duties and old readers; new distribution selection lives in `src/distribution/`; `tools/build-development.py` is source orchestration | Per-operation replacement, old release/history support and active recovery reconciliation; no directory retirement |
| `.dev/standards/`, `.dev/TEAM-GIT-FLOW-RULES.MD`, `.dev/ai-context/environment-policy.yaml` | Source policy, ownership, work-management, environment truth | Retain; later update only conflicting current-source placement/routing selections | Explicit source policy adoption; U001/P7 transition is separate from package installation |
| `.dev/ai-context/` and `.ai/custom/` (latter absent here) | Project truth/customization, not package input | Preserve; explicit `.ai/custom/framework.json` only for new package settings | Never rename legacy YAML/provenance/ledger into config 2; M01 is not a legacy converter |
| `.dev/lessons/`, `.dev/adr/` | Project Markdown knowledge and indexes | Preserve originals, links and identities; new JSON collections below | Select new authoring route and exact collection, label old templates legacy; no inferred read/import support |
| `.dev/workflows/`, `.dev/assessments/`, `.dev/design/`, `.dev/requirement/`, `.dev/specs/`, `.dev/problem-frames/` | Project execution, assessment, design and specifications | Preserve project authority/history; new workflow/CBF formats get separate bindings | Active records finish with their owner; a fresh linked successor can be explicitly authored without rewriting old evidence |
| `.dev/backlog/` | Frozen pre-2026-08-24 evidence | Preserve frozen bytes and links; no new backlog writes | `SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml` keeps live GitHub Issues/Project as work authority; selecting local-backlog cannot reactivate it |
| `.dev/releases/`, `.github/`, source release/governance standards | Source release identity, publication, provider and CI duties | Retain source-only authority; neither mandatory product dependency nor optional maintenance takeover | P7 pipeline dispositions and separate publication authority; source merge is not a release |
| `.gitattributes`, `.gitignore` | Project Git behavior | Narrow reviewed changes in root-bindings.md | Must precede staging selected generated outputs; never normalize historical originals or remove ignore protections wholesale |
| `.dev/ai-context/local/` (already ignored), proposed `.ai/local/`, `dist/` | Machine-local state / proposed scratch | Keep existing protection; add bounded local/scratch ignores if created later | No unique backup/recovery data may depend on ignored RAM scratch; no cleanup authority |

## Exact current package set and desired selections

`src/skills/<id>/skill-package.yaml` is the observed metadata path for each ID.
Member suffixes are the exact Git-tracked files in that package, enumerated in
[source-observation.json](../../../workflows/2026-09-23-source-adoption-design/evidence/source-observation.json).
Shared mappings must equal metadata-declared members, not a directory glob.
All versions are `0.1.0` except Lesson `0.2.0`.

| ID | Metadata / members | Current manifest | Proposed later root selection |
| --- | --- | --- | --- |
| lesson | 2 / 9 | mapped | Pilot and ordinary root |
| adr | 2 / 8 | mapped | Ordinary root knowledge |
| standards-promotion | 2 / 9 | mapped | Ordinary root proposals; no automatic rule adoption |
| pr | 2 / 10 | mapped | Ordinary root local preparation; provider writes separately authorized |
| local-backlog | 2 / 8 | mapped | Exclude by default; optional separate collection only if actual need |
| software-development-orchestrator | 2 / 10 | unmapped | Ordinary root; pending #346 |
| code-reviewer | 3 / 3 | unmapped | Ordinary common review; pending #346; selected .NET coverage still needs explicit evidence |
| requirement-author | 3 / 4 | unmapped | Ordinary root; pending #346 |
| spec-author | 3 / 7 | unmapped | Ordinary root; pending #346 |
| problem-frame-author | 3 / 10 | unmapped | Ordinary selectable CBF owner; later #356 mapping |
| spec-compliance-validator | 3 / 6 | unmapped | Ordinary selectable scoped compliance; later #356 mapping; not automatic validation |
| ai-context-auditor | 3 / 3 | unmapped | Optional only; later #357 mapping |
| ai-context-governance | 3 / 3 | unmapped | Optional only; later #357 mapping; source duties remain separate |

#346's blocked first mapping batch is nine packages / 68 members (first five plus
workflow, review, requirement, spec). It does not include #356/#357's four packages /
22 members. Loader/adapter metadata-3 source is delivered; mapping is still absent.
#347's `diagnostic-analyst`, `ddd-ca-hex-architect`, `bdd-gwt-test-designer`,
`local-change-implementer`, `slice-implementer` source directories are absent here.
These are precise dependencies, not permission to replace either blocked writer.

## Each legacy skill route and exit condition

Every ID below currently has all three exact route paths:
`.ai/assets/skills/<id>/skill.yaml`, `.agents/skills/<id>/SKILL.md`, and
`.claude/skills/<id>/SKILL.md`. The table expands `<id>` by its row, without
claiming directory-wide ownership. Root AGENTS and the canonical registry select
them. For any activated successor, remove the old ordinary route from discovery
on **both** runtime surfaces in the same project cutover, preserving its canonical
history/recovery material. Merely preferring a new prefixed name is insufficient.
Codex is the only delivered new adapter: affected ordinary Claude capability is
explicitly unavailable until a separately selected adapter exists; no silent
fallback to the retired old implementation. Unaffected legacy skills remain active.

| Exact legacy ID | Successor / scoped retained owner | Individual exit condition |
| --- | --- | --- |
| code-reviewer | `src/skills/code-reviewer` -> installed common review | #346 mapping + actual common review selection; resolve required technology coverage before claiming replacement of a selected legacy .NET review |
| requirement-author | `src/skills/requirement-author` -> installed draft/normalize | #346 mapping + caller destination/template; retain source requirements and old source policy |
| spec-author | `src/skills/spec-author` -> installed draft/normalize | #346 mapping + selected specification kind and target format; no automatic conversion |
| software-development-orchestrator | `src/skills/software-development-orchestrator` -> new records | #346 mapping + new store and source Issue-binding policy; old active workflows complete through their original owner or explicit semantic handoff |
| problem-frame-author | `src/skills/problem-frame-author` | #356 mapping + new CBF binding and reader evidence; old CBF/SWF have semantic intake only, no machine compatibility |
| spec-compliance-validator | `src/skills/spec-compliance-validator` | #356 mapping + actual criterion/subject/evidence contract; legacy CBF/SWF helpers do not become the new validator |
| diagnostic-analyst | Pending #347 actual package | Do not retire until source, mapping, selected diagnosis output and P7 observations exist |
| ddd-ca-hex-architect | Pending #347 actual package | Same, with explicit architecture/ADR handoff and project rules |
| bdd-gwt-test-designer | Pending #347 actual package | Same, with observable scenario/test-level contract; no implied test execution |
| local-change-implementer | Pending #347 actual package | Same, with accepted local radius and project commands |
| slice-implementer | Pending #347 actual package | Same, with accepted architecture/slice scope and explicit technology selection |
| ai-context-auditor | Optional `src/skills/ai-context-auditor`; source assessment owner retained | Optional mapping/adoption only; generic audit may switch, but selected legacy assessment persistence/finalization remains with its existing owner until explicitly replaced |
| ai-context-governance | Optional `src/skills/ai-context-governance`; source governance remains project-owned | Optional ordinary maintenance can switch; source policy/release/routing/legacy-ledger work retains an explicit source-only route to the current canonical skill and policies, never two owners for the same operation |
| ai-context-init | New installation mechanics via #359 plus explicit project onboarding | New framework install only after selected checks and bindings; no automatic provenance/semantic-ledger seed. Retain old release adoption support as explicit legacy scope |
| ai-context-upgrader | #359 managed update for the new lock format | New managed update is not old multi-hop upgrade. Retire ordinary old upgrade suggestion only after all affected active old transactions are recovered/completed by their original owner; keep version-bound support material |
| ai-context-release-closeout | No portable successor; current source-only owner | Never retired by pilot or optional maintenance; historical/exception release obligations continue under current source policy |

## Knowledge and format routes without legacy skill wrappers

| Current path / meaning | Selected future binding | Concrete retirement limit |
| --- | --- | --- |
| `.dev/lessons/README.MD`, `templates/lesson-template.md`, `INDEX.MD`, category indexes | New Lesson route -> `.dev/lessons/records` JSON; package `templates/lesson.md` | Pilot creates a bounded new collection only; legacy Markdown lifecycle remains for its existing records. Broader adoption labels old template historical-only for new entries and keeps links to retained originals |
| `.dev/adr/README.md`, `ADR-TEMPLATE.md`, `WHEN-TO-CREATE-ADR.MD`, `INDEX.md` | New ADR route -> `.dev/adr/records`; package `templates/adr.md` | Preserve ADR-001 and other originals; new draft/decision evidence does not import historical approval |
| `.dev/standards/` rule owners and Lesson promotion prose | New `standards-promotion` proposals -> `.dev/knowledge/promotions` | Actual source policy owner still applies any adopted rule; package has no apply authority; old normative files are not retired by a proposal |
| Existing `.dev/workflows/<id>/workflow.yaml` and task/report files | New ordinary record collection `.dev/workflows-v2` | Current source workflow policy remains until explicitly reconciled; new product aggregate is not a drop-in locator replacement; preserve active #322 issue records and frozen terminals |
| `.dev/backlog/items/`, `ROADMAP.md`, provider receipts | No default new local writer | Frozen; optional `.dev/local-work-items` would be a new collection, never a current GitHub mirror or replacement authority |
| Legacy `.dev/problem-frames/` file sets | New `.dev/problem-frames/records` for `problem-frame.cbf@1.0.0` | No mechanical SWF/legacy conversion; carry selected criteria and uncertainty through explicit semantic intake |

#342 F01-F17 remain the exhaustive retained **kind** dispositions; this document
adds repository routing, not another registry. In particular F06 legacy YAML and
provenance are preserved, F07's 14 old transaction kinds remain with their exact
recorded original readers/recovery owners, and F11's ten distribution/release kinds
remain source-only. F01/F04/F12/F13 validation machinery awaits P7 selections.
A record being historically labeled retired never authorizes abandoning active
recovery. Active old transaction locations/status are a required operator input,
not an absence conclusion from this limited checkout inspection.
