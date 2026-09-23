# Portable requirement and specification authoring

## Decision and source boundary

This is Issue #348's source delivery design under the
[selected P5 contract](../p5-selected-contract.md), especially D342-01/D342-03 and
P5-C. [Live Issue #348](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/348)
and the [coordinator assignment](../../../workflows/2026-09-23-framework-redesign-control/tasks/ISSUE-348.json)
select the exact write scope. Package consumers do not depend on this document,
the source workflow or U001.

Baseline: `842b73ca09d701d1561109255193d80439dc996b`;
worktree `F:/framework-next/348`;
branch `codex/2026-09-23-portable-authoring`.
The coordinator later reported design integration at
`5079fdf8e92e281cee0d5b9d26e6a1c9afa4166a` via PR #349; that notification
does not change this worktree's selected baseline or count as executor
provider verification.

## Delivered interfaces

| Package | Version / metadata | Public operation | Instruction member | Result |
| --- | --- | --- | --- | --- |
| requirement-author | 0.1.0 / integer 3 | draft | references/authoring.md | Requirement draft, sources, acceptance, assumptions and open decisions |
| requirement-author | 0.1.0 / integer 3 | normalize | references/authoring.md | Existing requirement normalized within scope, preserving meaning/IDs and reporting material changes |
| spec-author | 0.1.0 / integer 3 | draft | references/authoring.md | Selected production/entity/adapter/formal-test draft and source/uncertainty notes |
| spec-author | 0.1.0 / integer 3 | normalize | references/authoring.md | Existing selected spec normalized while retaining source, format, meaning and scope |

Each operation declares `execution: instruction`; none declares a tool.
`configuration: null`, required/optional dependencies, artifact roles,
schemas, machine templates and tools are empty as selected. A text instruction
reader is the sole package runtime requirement. Inspecting or writing target
material still needs the target's actual permitted surface; unavailable writes
are disclosed rather than fabricated.

Packaged prose templates are ordinary declared references. They neither own a
record schema/store nor require config provisioning or a Python runtime.
`delivery_status` and `implementation_status: implemented` identify source
existence only. No invocation, package-build, installation, compatibility,
schema, code/test compliance or downstream acceptance is claimed.

## Exact membership and shared-mapping handoff

The following are the complete owned source members: requirement-author has
four; spec-author has seven. The installed column is the proposed exact mapping
for the coordinator's later shared registration, not observed installation.

| Source member | Proposed installed member |
| --- | --- |
| `src/skills/requirement-author/SKILL.md` | `.ai/core/skills/requirement-author/SKILL.md` |
| `src/skills/requirement-author/skill-package.yaml` | `.ai/core/skills/requirement-author/skill-package.yaml` |
| `src/skills/requirement-author/references/authoring.md` | `.ai/core/skills/requirement-author/references/authoring.md` |
| `src/skills/requirement-author/references/requirement-template.md` | `.ai/core/skills/requirement-author/references/requirement-template.md` |
| `src/skills/spec-author/SKILL.md` | `.ai/core/skills/spec-author/SKILL.md` |
| `src/skills/spec-author/skill-package.yaml` | `.ai/core/skills/spec-author/skill-package.yaml` |
| `src/skills/spec-author/references/authoring.md` | `.ai/core/skills/spec-author/references/authoring.md` |
| `src/skills/spec-author/references/production-template.md` | `.ai/core/skills/spec-author/references/production-template.md` |
| `src/skills/spec-author/references/entity-template.md` | `.ai/core/skills/spec-author/references/entity-template.md` |
| `src/skills/spec-author/references/adapter-template.md` | `.ai/core/skills/spec-author/references/adapter-template.md` |
| `src/skills/spec-author/references/formal-test-template.md` | `.ai/core/skills/spec-author/references/formal-test-template.md` |

No other package members are required. The coordinator owns manifest/profile
registration and generated runtime projections after actual source delivery.
Expected future generated entries are
`.agents/skills/framework-requirement-author/SKILL.md` and
`.agents/skills/framework-spec-author/SKILL.md`; neither is created here.
Each should point to its installed package entry and metadata through
`../../../.ai/core/skills/<id>/` under the shared adapter contract.
Null-config and instruction-operation support is owned by #346, not duplicated
inside either package. The packages declare no dependency on another skill.

## Useful methods retained

[Capability disposition](../capability-consolidation/capability-disposition.md)
selects independent requirement and specification responsibilities.

| Legacy source inspected at baseline | Retained method | Portable replacement |
| --- | --- | --- |
| [.ai/assets/shared/AUTHORING-BOUNDARY-CONTRACT.md](../../../../.ai/assets/shared/AUTHORING-BOUNDARY-CONTRACT.md) | Artifact-first selection; explicit choice; source bindings; no automatic pipeline; bounded handoff | Self-contained intake, source and delivery instructions in each package |
| [Requirement author references](../../../../.ai/assets/skills/requirement-author/references/authoring-playbook.md) and [source truth](../../../../.ai/assets/skills/requirement-author/references/source-truth-rules.md) | Stakeholder intent, business rules, observable acceptance, assumptions and observed-versus-intended behavior | Requirement authoring reference and populated guidance in the default prose outline |
| [Requirement guide](../../../requirement/REQUIREMENT-GUIDE.MD) | Context/goals, personas, functional/non-functional requirements, constraints, rules, acceptance and references | Optional package-owned requirement template; caller's template/path takes precedence |
| [Spec author type selection](../../../../.ai/assets/skills/spec-author/references/type-selection.md) and [output contract](../../../../.ai/assets/skills/spec-author/references/output-contract.md) | Production/entity/adapter/formal-test choice; GWT does not change owner; preserve selected schema | Four optional prose templates, explicit target-format intake and out-of-band uncertainty notes for closed schemas |
| [Spec guide](../../../specs/SPEC-GUIDE.MD) and [organization guide](../../../specs/SPEC-ORGANIZATION-GUIDE.MD) | Behavioral subject, model invariants, adapter mappings, test targets; relationship is not ownership | Useful type-specific guidance without mandatory JSON, aggregate layout, .NET defaults or source-directory conventions |

These links document source reasoning only; installed packages contain none of
these source paths. The old active source routes are preserved. No legacy
deletion, new problem-frame/compliance implementation or root cutover occurs.

## Caller choices and unresolved inputs

- Template, format, language and destination are per-operation caller inputs.
  No destination means conversation output. An authorized file write preserves
  existing content outside the selected edit scope and checks for collisions.
- Sources retain actual reference/revision/section/IDs and supported status.
  User-supplied facts, extracted observations, assumptions/proposals and open
  decisions remain distinct. No invented owner or approval fills a placeholder.
- Normalization preserves accepted semantics and separates semantic changes
  from editorial ones. Missing required target schema or authority blocks only
  the dependent claim; a provisional draft is allowed only within the request.
- Formal-test expectations and scenarios remain specifications, not test runs.
  Missing selected technology rules and inaccessible evidence remain explicit.
  No .NET or other specialist coverage is silently provided by these packages.
- No substantive new cross-contract decision is needed. Loader integration,
  exact manifest/profiles and runtime projections remain coordinator/#346 work;
  target behavior and useful consumer trials remain unverified.

## Verification boundary

See the [source report](../../../workflows/2026-09-23-portable-authoring/reports/remediation-report.md)
for actual direct checks and preserved failed attempts. Under U001 all product
CLI/help, schema validation, tests/fixtures, build/package/install, migration/
compatibility, audit/lease/effective-rule/handoff tooling and CI remain
`deferred-by-owner`, owner `program #322 coordinator / P7`, next action
`P7 selects redesigned checks after implementation`. Direct parsing and
reference inspection are not product verification.
