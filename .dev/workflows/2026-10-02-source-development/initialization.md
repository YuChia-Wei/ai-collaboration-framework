# Optional initialization source delivery

Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/427

The owner extended this workflow on 2026-10-02 to create a new project
initialization/structure version, using the old init and MQ lab as references,
and to improve the old internal AGENTS template. This is separate from pending
source-policy adoption, CI activation and the removed general agent evaluations.

## Sources and decisions

- Former init at `c2e7071335d02d9b8d40ab4dcaf437e690791741`:
  `.ai/assets/skills/ai-context-init/templates/public-root/AGENTS.md`, thin CLAUDE
  adapter, public template manifest and document-target guidance. Preserve scope,
  progressive loading, truthful validation and the repository-specific fact zone;
  replace removed path assumptions and unconditional source policy dependencies.
- MQ lab read-only at `f88be639274f292210df2843780651b1cefe4859`: root AGENTS,
  `.dev/README.MD`, index, architecture, project inventory and target rule ownership.
  Reuse separation of responsibilities, not its domain names, technology choices,
  commands, permissions, history or stale `.ai/assets` navigation.
- New `src/skills/ai-context-init@0.1.0` uses metadata 3 instruction operations
  `initialize` and `refresh`. Current component version validation requires exact
  MAJOR.MINOR.PATCH; no version grammar change is needed.
- Seeds are declared read-only authoring references, consistent with instruction
  packages. Null configuration requires no artifact roles, schema-bound templates
  or store. No new renderer, record family or installation mechanism is introduced.
- Catalog now selects 18 skills; new `project-initialization` preset selects only
  init with Codex/Claude adapters. Existing presets, including `complete`, retain
  their previous selected set. Source installed core/runtime sets remain 17.
- Initialization applies only requested project-owned documents. Existing AGENTS
  custom sections, local edits and document ownership are preserved with preimage
  checks. Managed resources and project selection remain under the installer owner.

## Acceptance

| ID | Observable source result | Evidence and limits |
| --- | --- | --- |
| I1 | Evolved AGENTS retains the old collaboration intent with current target-resolved navigation | `templates/public-root/AGENTS.md`; instruction review, no target behavior claim |
| I2 | Project structure separates product documents, effective rules and managed installation | `references/project-structure.md`; MQ is a reference only |
| I3 | Seeds carry evidence/unknowns and command status, without copied project facts | Package authoring resources; YAML parse and reference closure |
| I4 | Existing/custom content is preserved by scoped refresh, preimage and read-back instructions | `references/initialize.md`; actual agent preservation scenarios not run |
| I5 | Init is independently optional and does not become a default root-file installer | New preset, unchanged existing selections and in-memory adapter projection |
| I6 | Narrow meaningful checks avoid installation/recovery/benchmark fixtures | Distribution suite and selected source gate; exact results in `validation.md` |

No downstream repository was initialized, restructured or installed. No public
release, provider activation or general agent evaluation is claimed. #43's wider
historical initialization/compatibility acceptance is not closed by this delivery.
