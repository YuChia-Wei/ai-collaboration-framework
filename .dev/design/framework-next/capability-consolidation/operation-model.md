# Instruction operations and mechanical tools

Status: proposed D342-01/D342-02, not adopted metadata semantics. [Source observation](../../../workflows/2026-09-23-capability-consolidation/evidence/source-observation.json) pins exact Git blobs. Current src/distribution/package.py:load_package accepts exact integer metadata 1/2, nonempty operations with implementation_status=implemented, a string tool, a declared implemented executable and exact tool-operation equality. It also requires configuration store/template defaults. A project role requires schema; every template binds roles. Empty tools alone cannot represent a store-free reasoning package.

## D342-01: minimal explicit metadata version 3

Keep v1/v2 accepted/rejected shapes and meanings unchanged; old loaders reject 3. Version dispatch precedes field validation. Exact integer 3 rejects booleans, floats and strings. Preserve v2 schema-pair/read_schemas rules, closed fields, contained paths, collisions, ownership, exact members, dependency absence and operation-scoped runtime requirements.

Only two boundaries change:

1. Public operations become a closed discriminated union. Common fields remain id, inputs, outputs, implementation_status. Add required execution with exact value instruction or tool. An instruction arm adds only instructions, a package-relative path already in resources.references, and forbids tool. A tool arm adds only tool, preserving implemented executable mapping, and forbids instructions. No nullable tool, implicit fallback, executable string or generic engine.
2. configuration may be explicit null for a package with **empty artifact_roles, schemas and templates**. Non-null configuration keeps the exact v2 namespace/default store/default template contract. Null triggers no lookup, config creation or directory provisioning. A tool without owned records could use null under the same constraints; authorized edits to target source are operation inputs, not a framework-managed record store.

For instruction operations, delivery_status=implemented and implementation_status=implemented mean the named instruction deliverable exists in source. For tool operations they still mean an actual executable exists. Neither means invoked, tested, installed, compliant or approved. This design specimen is not an implemented source package and is not eligible for manifest registration just because its illustrative value says implemented.

Tool-operation equality compares only tool arms. Instruction references must be real declared members, read as text and never executed by the builder. resources arrays may be empty. Schema-free outputs remain prose descriptions in outputs, not fake artifact roles. Runtime needs are operation-scoped: an instruction reader suffices for prose review; target inspection/experiments still require the actual permitted environment. Optional prose templates can be declared instruction references; do not weaken machine-template role bindings for them.

A mixed package may offer an instruction-driven draft and a useful real validate/create operation over an owned schema. Semantic content comes from the author; mechanical tooling checks structure/identity/concurrency. Approval and actual execution observations remain external inputs. Do not create a writer just to relabel a manual artifact kind as executable.

## Reasoning example: code-reviewer@0.1.0

[Complete proposed metadata](examples/code-reviewer-metadata-v3.yaml). Exactly three expected future members (not current source availability):

| Source | Installed |
| --- | --- |
| src/skills/code-reviewer/SKILL.md | .ai/core/skills/code-reviewer/SKILL.md |
| src/skills/code-reviewer/skill-package.yaml | .ai/core/skills/code-reviewer/skill-package.yaml |
| src/skills/code-reviewer/references/review.md | .ai/core/skills/code-reviewer/references/review.md |

SKILL.md uses the existing accepted name/description frontmatter and links to references/review.md. Its instructions obtain scope, intended behavior and applicable target rules; inspect evidence; return findings with impact/location/uncertainty and coverage. No findings means no supported findings in the inspected scope, not acceptance. The instruction reference is an agent method, not a shell command. There is no tool, schema, persistent role, store, template, dependency or mandatory Python runtime.

Operation review returns ordinary prose. Caller-selected export is a separately authorized file write, not a persisted machine-report family. If dotnet specialist coverage is requested but unavailable, report it missing. This first common-only package does not pretend to contain the legacy dotnet extension.

Future generated entry: .agents/skills/framework-code-reviewer/SKILL.md. Exact expected links from it are:

```text
../../../.ai/core/skills/code-reviewer/SKILL.md
../../../.ai/core/skills/code-reviewer/skill-package.yaml
../../../.ai/core/skills/code-reviewer/references/review.md
```

Installed entry links references/review.md relative to its own package. No link points to src, .dev or this design. Current adapter text says declared tool interface and requires configuration. The shared owner must change it to declared operation interface, describe instruction execution, and skip config for null packages. project_entry placeholders need not expand. Wrapper generation cannot claim an instruction was executed.

## Schema-owned authoring example: actual adr@0.1.0

[Metadata specimen](examples/adr-metadata-v2.yaml) copies current src/skills/adr/skill-package.yaml bytes; [source inventory](current-src-formats.json) binds its blob. Keep metadata v2. Exactly eight members:

```text
SKILL.md
skill-package.yaml
references/configuration.md
references/operations.md
references/example.md
schemas/adr-record.schema.json
templates/adr.md
scripts/adr.py
```

Each maps from src/skills/adr/<member> to .ai/core/skills/adr/<member>. Generated .agents/skills/framework-adr/SKILL.md would link to ../../../.ai/core/skills/adr/SKILL.md and corresponding metadata, schema and script paths. Installed SKILL.md links references/configuration.md and references/operations.md within the package. The actual installed script uses its declared interface and explicit absolute project_root/package_root, without a source checkout dependency.

adr.fs owns 11 actual source operations: explain, create, inspect, query, validate, revise, render, derive, decide, retire, supersede. Reader/writer/validator logic is scripts/adr.py; structure is adr.record@1.0.0. The project-owned store defaults to notes/adrs; adr.view is result-only Markdown. Project/local config 2 is explicit. Package schemas/tools/default template are managed; config/custom templates/records are project-owned. decide consumes project-mapped decision evidence and cannot create its own authorization. derive makes a new identity, not migration. Schema conversion is unsupported.

Real source is not runtime verification. Current manifest at this subject does not yet map ADR; #337 owns that work. No ADR metadata upgrade is needed to coexist with a future reasoning package.

## Future checks, not executions

P7 selects exact-type/version rejection, unchanged v1/v2 behavior, both/neither operation-arm fields, missing instruction resource, null config with owned record/schema/template, tool equality, member/path collisions, source-link leakage and mixed package selection. Package source, wrapper generation and instruction invocation remain separate observations. This list grants no execution now or adoption of v3.

Subsequent dependency state: [P3 integrated mapping and P4 selected contract](dependency-update.md). Baseline inventory remains pinned; P4 source is not yet delivered.
