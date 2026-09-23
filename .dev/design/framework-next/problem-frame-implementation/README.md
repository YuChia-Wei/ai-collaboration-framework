# Issue #356 source handoff

Selected by [P5 final contract](../p5-final-capability-contract.md), implementing
D351-01..05 from [the frame/compliance design](../problem-frame-compliance/README.md).
Authority: program #322 / U001 and Issue #356 coordinator assignment. This is
source implementation; runtime/schema/package/backend verification is
**deferred-by-owner**, owner **program #322 coordinator / P7**.

## Actual source closure

| Package | Exact members |
| --- | --- |
| problem-frame-author | SKILL.md; skill-package.yaml; references/authoring.md; references/format.md; references/operations.md; references/configuration.md; references/example.md; schemas/cbf-record-v1.schema.json; templates/cbf.md; scripts/problem_frame.py |
| spec-compliance-validator | SKILL.md; skill-package.yaml; references/compliance.md; references/report-template.md; references/legacy-intake.md; profiles/dotnet.md |

Both are metadata 3 / package 0.1.0 with empty required/optional selectable
dependencies. Exact source-to-installed suffix mapping remains
`src/skills/<id>/<member>` -> `.ai/core/skills/<id>/<member>`. A separate shared
writer must map these 16 actual members and coordinator-selected profiles;
this assignment changes no manifest/profile/loader/adapter/root/index.

## Actual public interfaces

Frame instruction operations: draft, review-draft through authoring.md. Tool
problem-frame-author.fs: explain/create/inspect/validate/render through one
scripts/problem_frame.py. Every closed request requires operation, project_root,
package_root. Create adds reference/record; read operations add reference and
optional expected_sha256. No help, migration, revise or execution operation.

The package owns exact problem-frame.cbf@1.0.0, Draft 2020-12 schema, canonical
producer, strict reader, structural validator and version/unsupported responses.
Project role problem-frame.cbf has that exact write/read schema, store binding
problem-frame-author.store and <id>.cbf.json filename; derived
problem-frame.cbf-view is result-only Markdown. Configuration is nonnull namespace
problem-frame-author, exact integer config 2, default specs/problem-frames with
tracked intent and templates/cbf.md. Explicit flat store-relative filenames make
identity/path collision equivalent without a collection scan; caller selects a
new store for a different collection. Ancestors already exist; no mkdir.

Source implements 4 MiB/32 depth/1024 array/16384 text/96 ID limits, duplicate-key
and exact shape/version handling, typed source/statement/related references,
combined claim ID uniqueness, and mandatory question links for every unresolved
statement or assertion. Staging is exclusive sibling, file-flushed/fsynced, then
no-clobber hard-link publication and exact owner read-back. Equal bytes still
conflict. NTFS ancestor pinning and Linux directory descriptors select bounded
local backends; unknown backend is unavailable. None/published/uncertain plus
residue preserve partial failures. No power-loss or cross-file promise.

Public structure contract is problem-frame.cbf.structural-result@1.0.0 with
exact fields contract/status/family/schema_version/id/subject_sha256,
criterion_inventory/counts/unresolved_ids/source_ids/question_ids. Inventory
rows are id/kind/pointer/scenario_id for EVERY statement, scenario and assertion.
All four record operations consume the same owner result. Detailed authoritative
package interface: [operations](../../../../src/skills/problem-frame-author/references/operations.md).

Compliance is instruction-only with configuration:null, no artifact roles,
schemas/templates/tools and no Python prerequisite. Operations plan-validation,
review-semantics, assess-runtime point to compliance.md. It consumes actual owner
results and exact bytes, retaining the complete inventory without another parser.
Outcome precedence: required contradiction -> not-compliant; missing required
evidence/authority/binding or empty scope -> unavailable; full required coverage
-> compliant-within-scope. dotnet@0.1.0 is explicitly selected instructions and
imposes no ORM/testing/architecture defaults. Legacy CBF/SWF machine support is
unsupported and originals remain unchanged; selected semantic intake retains
complete criteria and per-field loss/uncertainty notes.

## Integration and verification handoff

The [workflow report](../../../workflows/2026-09-23-problem-frame-implementation/reports/remediation-report.md)
retains actual checks, initial provider failure/recovery, static repairs and
unexecuted P7 obligations. Coordinator reads the local commit/branch/worktree
before first push; no executor callback, push, PR, merge or provider mutation.
No unresolved shared-contract decision currently requires another design.

Suggested coordinator row: `P5-F / #356: 10-member CBF owner + 6-member scoped
compliance source delivered locally; exact shared mapping pending; all behavioral
and compatibility verification deferred-by-owner under U001 to coordinator/P7`.
Do not interpret this suggested row as a mutation of a shared index or provider.
