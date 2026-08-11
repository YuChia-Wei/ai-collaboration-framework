# Round 3 Governance Terminology Matrix

## Evidence Boundary

- Subject: `main@df7012b6bf6ac360cfb47e2c79813384880665f8`.
- Active search roots: root collaboration guides, active standards/guides/operations, canonical skills and portable governance, distribution controls, source release validators, and hosted workflow definitions.
- Excluded from frequency counts: dated workflow/assessment instances and versioned historical release directories.
- Counts are discovery signals, not proof that every occurrence is a duplicate definition.

| Term | Matches | Files |
| --- | ---: | ---: |
| `candidate` | 141 | 46 |
| `validated` | 96 | 47 |
| `integrated` | 9 | 6 |
| `integration` | 173 | 70 |
| `publication` | 104 | 42 |
| `published` | 102 | 28 |
| `closeout` | 64 | 30 |
| `finalization` | 41 | 19 |
| `lifecycle` | 137 | 55 |

## Namespace And Owner Matrix

| Qualified term | Meaning | Current canonical owner / machine contract | Current ambiguity | Recommended placement |
| --- | --- | --- | --- | --- |
| framework version candidate | governed source record being prepared before tag/publication | source release policy, `.dev/releases/<version>/release.yaml`, release validator | often shortened to `candidate`, which is also used for package, skill, and migration selections | source-only release policy and validator; consumers say `framework version candidate` |
| package candidate | deterministic archive built for validation; not publication | package builder, package-candidate workflow, archive metadata | can be mistaken for a validated release record | source distribution contract; always qualify as `package candidate` |
| migration `automatic-candidate` | unchanged framework file proposed for automatic replacement | upgrader comparison contract and migration schema | not a release lifecycle state | keep exact machine value; contextual prose links to upgrader owner |
| skill/provider candidate | a selectable capability under evaluation | skill discovery or provider-selection owner | bare `candidate` collides with release language | qualify by subject; no shared lifecycle meaning |
| release source status `validated` | terminal governed source state for v0.12+ | `release.yaml.status` and `validate-ai-context-release-state.py` | version policy also describes conceptual Planned/Validated/Integrated/Published states, but Integrated and provider Published are not source status values | split conceptual lifecycle from source field definition; never write provider state into v0.12+ source status |
| repository integration | reviewed change enters the configured integration branch | source `.dev/TEAM-GIT-FLOW-RULES.MD`; portable projection under `.ai/assets/shared/governance/` | `integration` also means system/API integration and is sometimes treated as workflow completion or publication | keep branch integration definition in Git policy and require a contextual link when lifecycle evidence depends on it |
| workflow completion | all workflow tasks terminal and lifecycle contract satisfied | `WORKFLOW-ARTIFACT-POLICY.md` and workflow validator | prose often calls this `closeout`; checkpoint integration does not complete workflow | prefer machine term `completed`; use `workflow closeout` only as explanatory prose linked to the policy |
| assessment final | report conclusions/finding IDs frozen | `ASSESSMENT-ARTIFACT-POLICY.md` and assessment validator | `final` can be confused with release finalization | always qualify as `assessment final` |
| hosted publication | immutable user-owned tag triggers Release/assets/provider reconciliation | source release policy, publication runbook, tag workflow, release validator | version policy exposes source-only procedures to downstream payload; `published` is provider state but historical records may also have source status `published` | source-only release/publication policy; downstream version policy refers only to an installed published framework version |
| publication validation phase | read-only hosted Release and asset parity check | release phase contract and validator `publication` phase | phase name can be read as mutation authority | define as validation phase; mutation belongs to tag-triggered workflow authority |
| finalization validation phase | post-publication hosted parity/read-back; no v0.12+ source rewrite | release phase contract and validator `finalization` phase | legacy `published` records and v0.12 terminal `validated` records follow different branches | keep machine phase for compatibility; prose says `hosted finalization validation` |
| release closeout | historical verification or explicitly authorized exception recovery | `ai-context-release-closeout` skill | generic closeout wording can incorrectly add a normal post-tag source stage | keep source-only skill; every reference states `historical/exception release closeout` |
| lifecycle | state machine belonging to one governed subject | each subject's owning policy | bare use conflates workflow, task, assessment, release, customization, migration, and provider state | require a qualifier (`workflow lifecycle`, `release lifecycle`, and so on) |

## Definition Placement Recommendation

Do not create a terminology-specific skill. Extend the existing AI-context ownership standard/registry with a compact governance-term routing section that records:

- stable qualified term;
- subject namespace;
- canonical definition owner;
- machine field/value when one exists;
- allowed contextual aliases;
- forbidden unqualified use;
- portable versus source-only classification.

Definitions remain in their existing owning policies. Consumers carry one sentence of contextual meaning at most, then link to the owner. This keeps one normative definition without adding a second glossary authority.

The current `AI-CONTEXT-VERSION-POLICY.md` should be separated by projection rather than copied:

- source repository: a release/publication policy owns version-candidate, tag, hosted publication, finalization, and historical compatibility;
- downstream target: a portable version/provenance/upgrade policy owns installed published version identity and upgrade safety;
- the package may map the portable projection to the stable downstream path, as it already does for branch policy.

## Contextual Link Rules

1. Normative text uses a qualified term on first use; bare aliases are allowed only within the same clearly headed section.
2. A consumer links to one canonical owner and must not copy its state transition table.
3. A conceptual lifecycle state, machine status, validation phase, and provider state must be labeled separately.
4. Existing machine values (`automatic-candidate`, `validated`, `published`, `candidate`, `tag`, `publication`, `finalization`) do not change without a schema/version migration.
5. Source-only operations must not appear as actionable downstream guidance. If mentioned for provenance, label them upstream/source-only and do not link to excluded payload files.
6. Historical records retain original wording. Active guides may explain legacy meaning without rewriting history.

## Validator And Migration Impact

| Consumer | Required disposition |
| --- | --- |
| `validate-ai-context-release-state.py` | preserve four phase literals and the v0.12+ terminal `validated` branch; update messages/tests only when terminology is qualified |
| release record/template and renderer | preserve historical `published` compatibility and current `validated` source status; no silent schema rewrite |
| workflow and assessment validators | preserve existing status enums; documentation links to their separate owners |
| workflow handoff contract | preserve release handoff phase literals; label them validation/transport phases, not lifecycle status |
| upgrader comparison and migration schema | preserve `automatic-candidate`; path moves need explicit transition/migration entries |
| distribution profile | classify source release policy/templates/scripts as source-only and project only target-safe version/provenance guidance |
| package reference validation | reject active local links or actionable commands whose targets are excluded from the selected payload |

## Finding Handoff

- `ASM-20260811-003#GTM-001`: active governance uses overlapping bare terms across conceptual lifecycle, machine status, validation phase, migration category, and provider state without one namespace/owner routing contract.
