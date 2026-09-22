# Standalone Lesson Example

Every value here is a design illustration. The example ID/time/evidence are synthetic, not tool execution. No script or installer is supplied, runtime availability is not asserted, and the sequence below has not run. It describes intended P2 behavior.

## Complete selected inputs

Treat `examples/project/` as project root and `lesson/` as package root. The caller supplies their absolute locations after copying them anywhere; no parent source checkout is required.

- Package entry/declaration: `lesson/SKILL.md`, `lesson/skill-package.yaml`.
- Required/optional skills: both empty; complete skill closure `lesson@0.1.0`.
- Runtime: instruction reader, Python `>=3.11,<4`, PyYAML `>=6,<7`, jsonschema `>=4.18,<5`, and declared filesystem semantics. These are design requirements, not tested compatibility. No network, Git, tracker or workflow skill is required.
- Owned resources: `references/configuration.md`, `references/operations.md`, `schemas/lesson-record.schema.json`, `templates/lesson.md`; tool `lesson.fs` remains planned, `entrypoint: null`.
- Project config argument: `team/lesson.config.json`, relative to project root.
- Local config and invocation overrides: omitted.
- Project template: `team/templates/lesson.md`.
- Example record: `knowledge/lessons/lesson-11112222333344445555666677778888.lesson.json`.

The JSON candidate is authoritative. The template changes presentation without creating another editable record. P1-B may install at `.ai/core/skills/lesson` and generate runtime projections; those paths never enter Lesson record metadata.

## Intended standalone sequence

1. `explain` resolves store `<project_root>/knowledge/lessons` and template `<project_root>/team/templates/lesson.md`. Both are project values. Allowed write roots are `knowledge/lessons` and `knowledge/review-candidates`; tracking/template are locked.
2. `query` with `output locations` finds the synthetic candidate. It reports `partial: false` only if every selected file actually parses; it never searches workflows or other skills.
3. `inspect` by logical role/ID returns the record and an actual execution-computed SHA-256. No digest is supplied here.
4. `render` returns Markdown beginning `# Team learning: Resolve output locations from an explicit project root`, with ID/schema, evidence and limits. It does not write a Markdown file implicitly.
5. A new Lesson takes authored content, a prior similar-candidate query and `create`. Generate fresh ID/time and one record below the frozen store; never reuse the synthetic identity or create a workflow.
6. `revise` takes a real expected digest and replacement content; stale digest means conflict. Preserve extensions/creation time. Promotion/standard editing remain separate unsupported operations.

## Precedence and constraint examples

These are expected design outcomes, not execution observations. A local config is explicitly selected and ignored before use. Changing a store selects a different collection; it does not relocate the example record.

| Inputs over the project config | Effective behavior |
| --- | --- |
| No local/override | `knowledge/lessons`, project template. |
| Local `skills.lesson.store.root = knowledge/review-candidates` | Local wins, permitted by the second allowed root. |
| Same local, invocation `store.root = knowledge/lessons` | Invocation wins, still project-root based when shell cwd changes. |
| Invocation root `unrelated/output` | Rejected, outside allowed roots. |
| Invocation tracking `ignored` | Rejected, project-locked field. |
| Different local/invocation template | Rejected, locked object. |
| Partial template or explicit null | Invalid input, not inheritance/reset. |
| Unknown config version or missing named config | Unsupported/invalid input before mutation, no fallback. |
| Missing runtime/library/filesystem capability | Unavailable, no record fabrication/manual mutation. |
| Missing optional collaborator | No effect on this Lesson's empty closure; future composition declares its own contract. |

External storage needs an absolute store root, an explicit project constraint covering it and actual runtime permission. This example neither creates external directories nor promises durability. Omitting all config arguments selects package defaults: `notes/lessons` under project root and the package template. Defaults create nothing until an authorized operation runs.

## Output and migration limits

Create/revise write only `lesson.record`; inspect/query/validate/explain write nothing; render returns `lesson.view`. No staging, PR, other skill invocation, standard adoption or receipt for unperformed checks. Historical Markdown/YAML import and schema conversion are unsupported; original input bytes remain intact.

P2 implements this interface, P3-A adds accepted lifecycle behavior, P7 designs/runs validation. P1-A delivers readable design, not standalone execution acceptance.
