# Implementation selection and P7 handoff

This design is complete for selection, not authority to implement source.
Coordinator owns these decisions, shared mappings and future assignments.

## Decisions to record before source work

| ID | Recommended selection | Consequence / unresolved choice |
| --- | --- | --- |
| D351-01 | problem-frame.cbf@1.0.0 single JSON snapshot as specified | New format, no legacy compatibility. Coordinator may choose prose-only instead; then omit all machine roles/schema/tools and explicitly defer structured support. |
| D351-02 | One owner, create-only snapshots and no migration edge | Adopt identity/path/config and publication contract together. If in-place edits or multi-file fidelity are necessary, request a new bounded design rather than append a hidden updater. |
| D351-03 | Distinct instruction-only compliance package and scoped conclusions | No universal 100% or source helper as runtime proof. Target retains gate/evidence authority. |
| D351-04 | Bundle explicit opt-in dotnet@0.1.0 instructions | Choose whether to include this reference in first source batch; no global .NET rule/profile change. If omitted, report .NET coverage unavailable until separately implemented. |
| D351-05 | Preserve SWF/legacy YAML as unsupported machine inputs | Assign a later family owner only when real SWF/legacy fidelity demand is supplied; preserve workpiece/AC/entity-contract responsibility and all current roots/history. |

No missing target example, SDK, normative rules, authoritative approval or
execution evidence is invented. No substantive question prevents retaining this
design. These choices gate source implementation, not this design checkpoint.
No selected target proves that the minimal snapshot captures every downstream
frame; P7 and later target use must expose that limitation.

## Exact source slices and dependencies

The assigned paths below are **future proposals**, not current source presence.
Source to installed mapping is exact suffix preservation:
`src/skills/<id>/<member>` -> `.ai/core/skills/<id>/<member>`.
No installed package references this design, .dev policies, legacy .ai/assets,
source workflow or U001.

### S351-A: bounded frame owner

One future writer owns only `src/skills/problem-frame-author/` plus its own
assigned design/workflow. Package version 0.1.0, metadata integer 3.
Ten exact members:

1. SKILL.md
2. skill-package.yaml
3. references/authoring.md
4. references/format.md
5. references/operations.md
6. references/configuration.md
7. references/example.md
8. schemas/cbf-record-v1.schema.json
9. templates/cbf.md
10. scripts/problem_frame.py

Operations and fields are completely specified by this design. SKILL and
authoring retain extraction, family selection, bounded external-system
reasoning, source authority and uncertainty. format owns the selected record
contract. operations/configuration own concrete request/error/path behavior.
example includes a fictional draft plus expected unavailable runtime coverage.
The schema and sole script implement producer/reader/validator/version handling
together; schema-only delivery is incomplete. No import of legacy validators,
P3 scripts, source-only helpers or common runtime.

Metadata declares the instruction operations draft/review-draft and the five
tool operations explain/create/inspect/validate/render, all linked to actual
contained members. `problem-frame.cbf` project role has writable schema and
read_schemas exactly `problem-frame.cbf@1.0.0`, store binding
`problem-frame-author.store`, identity `cbf-<32 lowercase hex digits>`,
filename `<id>.cbf.json`; read operations inspect/validate/render, write create.
Derived role `problem-frame.cbf-view` has source_role problem-frame.cbf,
result-only Markdown output, produce render; no persisted report schema.
The template binds those two roles. Schema owner and tool owner are
problem-frame-author. Migration is unsupported; preserve original.
Schema resources declare the exact pair; JSON Schema uses Draft 2020-12 and
contained #/$defs only. Dependencies required/optional remain empty.

Use selected metadata-v3 support delivered under #346, and package-local
non-null config 2 semantics. This is a new namespace in optional target config,
not a required target config migration or a shared config edit. No package
metadata/config version change is required elsewhere.

### S351-B: bounded compliance owner

Depends on selected D351-01/03/04 and stable S351-A public structure-result
contract for new CBF input; does not own or copy its parser. One future writer
owns only `src/skills/spec-compliance-validator/` plus own assigned records.
Package version 0.1.0, metadata integer 3. Six exact members if .NET is selected:

1. SKILL.md
2. skill-package.yaml
3. references/compliance.md
4. references/report-template.md
5. references/legacy-intake.md
6. profiles/dotnet.md

All non-entry prose members are declared references. Three public instruction
operations plan-validation/review-semantics/assess-runtime point to
references/compliance.md. configuration:null; empty artifact roles, schemas,
machine templates, tools and dependency arrays. Runtime declares an instruction
reader; operation inputs identify the actual format reader and target execution
surface when required. No Python is required merely to read these instructions.

compliance contains complete criteria extraction, subject/authority/evidence
checks and outcome precedence. report-template carries all four stages, matrix,
exclusions and limits. legacy-intake contains explicit CBF and SWF selected-file
lists, original version uncertainty and preservation rules. dotnet is optional
intake/mapping, not an automatic executable or target rule registry.
If D351-04 is omitted, membership is five and references must truthfully
describe missing .NET coverage; never leave a dangling profile path.

### S351-C: coordinator-owned integration

Only after actual packages return, assign one shared writer to exact manifest
member mappings and coordinator-selected profile rows. Do not add a speculative
distribution profile, adapter change, root switch or global registry in A/B.
Existing v3 adapter should handle mixed instruction/tool operations; if source
inspection identifies an actual gap, return it to that owner before widening
the package task. P6 owns root/runtime projections and installation/update
selection. P7 owns verification/restoration. No self-rebase or shared-index edit
by these workers.

Sequence: decision record -> S351-A source contract -> S351-B consumes actual
interface (its independent prose drafting may overlap A) -> C maps real members
-> P7 selected executions -> separately authorized target adoption/root cutover.
Do not claim this order has run.

## P7 observations to require, not current passes

All rows below are unexecuted, **deferred-by-owner**, U001, owner
**program #322 coordinator / P7**. The next action is to select and run the
smallest tests/trials needed after source implementation and restoration
authority. No full legacy suite or CI restoration is implied.

| ID | Real observation needed | Limit established |
| --- | --- | --- |
| P7-351-01 | Execute new snapshot create, inspect, validate and render on exact source/installed package identities and explicit non-.dev paths; compare raw persisted bytes/digest and complete render | Real tool implementation, no source checkout or hidden common runtime |
| P7-351-02 | Exercise unknown family/version, malformed/duplicate JSON, wrong types, unknown fields, missing actor/command/domain, duplicate IDs and typed dangling refs; keep original bytes unchanged | Structural fail-closed behavior; no runtime compliance inference |
| P7-351-03 | Exercise inferred/unresolved sources, missing intent, absent test anchors, unresolved question links and false normative labels | Structure can accept a representation without semantically approving it; semantic report remains uncertain/unavailable |
| P7-351-04 | Exercise project/local/invocation precedence, missing explicit configs, locks/write roots, path escape/aliases/reparse points and external/custom templates | No implicit .dev, config write, template fallback, external execution or authority expansion |
| P7-351-05 | On selected Windows and Linux filesystems observe concurrent create collision, interruption before/after publication, read-back/cleanup failure and retained residue | No truncation/overwrite, truthful published/uncertain states; unsupported filesystems unavailable; no untested durability claim |
| P7-351-06 | Supply actual representative old CBF and SWF documents; observe machine unsupported outcome plus useful bounded semantic reading and loss/uncertainty report | Preserve families/IDs/bytes; no silent migration or conversion pass |
| P7-351-07 | Run package selection/build/install under P7 authority for exact A/B members and v3 operations, null versus non-null config and source-link containment | Real distribution compatibility; mere metadata parse is insufficient |
| P7-351-08 | Observe a selected real .NET target with known source/criteria/SDK/runner; deliberately omit runtime, intent or evidence in separate cases; retain actual failure/skipped runs | Missing prerequisites become unavailable, contradictions not-compliant; no global testing/ORM defaults |
| P7-351-09 | Observe all then conditions, event attributes and selected PRE/POST/INV/constraints mapped to actual assertions/runs, including an unasserted condition and changed subject | Complete denominator, stale evidence rejection, failure precedence and scoped successful conclusion |
| P7-351-10 | For a criterion requiring real transaction/message/external behavior, use actual required environment; compare supplied unit-only evidence | Synthetic/unit evidence cannot satisfy required real integration acceptance |
| P7-351-11 | Read both capabilities in an ordinary target task without source governance, another authoring skill or .NET selection | Independently useful methods and visible unavailable specialist coverage |

P7 may select a narrower set only with recorded reasons/remaining limitations.
Not every target must use .NET/infrastructure; unavailable means the unobserved
capability cannot be claimed. Design examples are not substitute executions.

## Related Issue scope only

Live read-only observations on 2026-09-23: #351 OPEN, #342 CLOSED,
#316/#318/#317 OPEN. Their recorded states are observations, not closure
recommendations. Bodies are retained with observation time.

| Issue | Actual overlap | Kept separate |
| --- | --- | --- |
| #316 | Explicit version support, immutable identity, stale-input/path protections and honest completion evidence inform the future writer | Its workflow/assessment multi-file/index/finalization acceptance is not implemented by CBF snapshot creation; no replacement or closure |
| #317 | Strict JSON parsing/digest mechanics are conceptually similar | Its existing authoring/execution producers, YAML scalar/comment compatibility and shared legacy module remain its own work; no new dependency or second migration of that module |
| #318 | Preserve original unsupported versions and identity | Dynamic role metadata 1.0 -> 1.1 and guarded updates are unrelated to CBF/SWF contracts; no conversion or closure here |

## Coordinator integration handoff

Receive the local design commit and exact final Git identity from this task.
Select D351-01..05 in coordinator-owned records; assign A/B and one shared
mapping writer only after that decision. Keep SWF, historical conversion,
runtime evidence and all P7 checks visible. The suggested shared row is:
`P5-D / #351: design delivered; CBF 1.0.0 + bounded owner tools and separate
compliance recommended; source selection pending; verification deferred-by-owner`.

No coordinator record/index, src, manifest/profile, root/custom/CI file or
external provider state is changed by this delivery.
