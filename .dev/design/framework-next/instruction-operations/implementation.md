# Instruction-operation source implementation

Issue [#346](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/346),
program #322 P5-A. Authority: [selected D342-01/D342-02](../p5-selected-contract.md),
[operation model](../capability-consolidation/operation-model.md) and the issue-owned
[workflow](../../../workflows/2026-09-23-instruction-operations/workflow.yaml).
Starting source is `842b73ca09d701d1561109255193d80439dc996b`.
This is source design evidence, not a portable package dependency.

## Delivered source contract

`src/distribution/package.py` accepts exact integer metadata 3 in addition to 1/2.
The v1/v2 operation shapes remain tool-only and still reject v3-only keys. Their
non-null configuration contract, resources, identities and meanings are retained.
V3 dispatch changes only the selected operation and configuration boundaries:

| V3 operation | Required arm | Forbidden opposite arm | Resolution |
| --- | --- | --- | --- |
| `execution: instruction` | `instructions` | `tool`, including null | Exact package-relative path in declared references; selected Git member must exist and decode as UTF-8 text. |
| `execution: tool` | `tool` | `instructions`, including null | Declared implemented tool containing that public operation. |

Both arms require id, inputs, outputs and implementation_status. Unknown fields,
missing arms or execution, unknown execution values, duplicate operation IDs and
non-implemented operations fail the metadata contract. Tool equality includes only
tool operations, so instruction operations do not require a dummy executable.
Instructions are read as text even when their reference has a non-Markdown suffix.
No instruction or package tool is executed by distribution selection or assembly.

Explicit `configuration: null` is allowed only for v3 with empty artifact_roles,
schemas and templates. References and real tools may still be present. Null does
not resolve project configuration or provision a store. Non-null v3 configuration
uses the v2 namespace/default store/default package template contract. Prose outputs
remain operation descriptions; optional prose guidance can be a reference, without
pretending it is a machine template or persistent role.

V3 retains v2 schema `(id, version)` identities, exact `read_schemas` declarations,
writable-schema inclusion and bounded same-document `#/$defs/` reference rules.
V1 keeps its existing schema identity and reference handling. All versions retain
operation-specific runtime requirements, dependency semantics, declared members,
contained paths, cross-platform collisions and selected closure checks. Delivery
and implementation statuses describe present source, not invocation or verification.

## Direct consumer changes

- `selection.select` still reads each exact declared member from the immutable Git
  tree and checks metadata/manifest equality. It passes the already-loaded
  `configuration` value explicitly to `codex.project_entry`.
- `codex.project_entry` adds a required keyword argument and one closed template
  placeholder, `configuration_guidance`. Null emits no configuration-path selection
  or store requirement. Non-null retains the existing explicit project/configuration
  guidance. Both branches remain deterministic text projections.
- The Codex template describes the operation interface, v3 instruction/tool dispatch,
  v1/v2 public tools and operation-scoped runtime requirements. It grants no execution
  or write authority. No global Python requirement is inferred from the builder's
  own implementation language.
- `assembly.assemble` consumes the selected members and metadata version without
  branching on configuration or assuming a tool per operation; it needs no change.
  P3 packages keep their existing metadata and independently owned tools unchanged.

The graph was freshly indexed at the starting checkout with persistence disabled.
It identified loader/selection/projection, but supplied no commit-SHA receipt and
its inbound loader trace was empty despite the tracked call in selection.py.
Therefore discovery completeness is not claimed. Material relationships were
confirmed against fixed Git-tracked source and explicit call-site search in `src`.
No graph-derived absence statement or schema/behavioral pass is claimed.

## Portable reviewer and future mapping

`code-reviewer@0.1.0` is exactly these three members:

| Source member under `src/skills/code-reviewer/` | Future installed destination |
| --- | --- |
| `SKILL.md` | `.ai/core/skills/code-reviewer/SKILL.md` |
| `skill-package.yaml` | `.ai/core/skills/code-reviewer/skill-package.yaml` |
| `references/review.md` | `.ai/core/skills/code-reviewer/references/review.md` |

Public operation: `review`, execution `instruction`, reference `references/review.md`.
Metadata 3; configuration null; required/optional dependencies, artifact roles,
schemas, templates and tools empty. Runtime `skill-instruction-reader` applies only
to review. A prose result needs no managed report store or mandatory Python runtime.
Target evidence, rules and permitted execution remain caller inputs.

The method is adapted from the actual legacy common guidance at the starting commit:
`.ai/assets/skills/code-reviewer/references/core-review-playbook.md`,
`references/review-routing.yaml` and `references/output-contract.md` in that same
legacy package. The new package retains subject/intent, authority, behavior and
failure reasoning, impact, test/GWT observability, findings, uncertainty, coverage,
read-only authorization and honest independent-review limits. It does not import
source assessment allocation, governance packets, role dispatch, runtime wrappers
or any hidden source path. No .NET extension is delivered; requested unavailable
specialist coverage and target-required gates remain explicit.

The future generated entry is `.agents/skills/framework-code-reviewer/SKILL.md`.
Its links resolve only to the three installed members above. No manifest/profile
mapping or wrapper generation was performed in the original source checkpoint.
The subsequent original mapping delivery is recorded below; wrappers remain unrendered.

## Deferred P7 cases

These cases are proposals for P7 selection, not executed tests or acceptance:

1. Reject bool, float, string and unknown metadata versions; retain accepted/rejected
   v1/v2 shapes, tool equality, configuration and existing five P3 packages.
2. Exercise v3 instruction-only, mixed and tool-only packages; reject missing/both
   arms, null placeholders, extra fields, unknown execution and undeclared tools.
3. Require a declared existing UTF-8 instruction reference, including non-md text;
   reject traversal, missing Git members, invalid UTF-8, duplicate/colliding paths
   and metadata/manifest mismatch. Observe that instructions/tools are never run.
4. Exercise null config with no config file and no record store; reject nonempty
   roles/schemas/templates. Include null-config tools with their own runtime needs
   and non-null mixed packages with their existing schema/template contract.
5. Retain v2/v3 schema-pair identity, read_schemas exact versions, writable inclusion,
   same-document pointer containment and rejection of remote/cyclic resolution.
6. Check installed Codex projections for null/non-null and mixed/tool/instruction
   packages, exact links, closed placeholders and truthful runtime/status language.
   Observe no invented config, store or Python requirement for the common reviewer.
7. Exercise required/optional dependency presence/version/operation selection and
   runtime absence scoped only to declared operations.
8. Try a real bounded reviewer task with supplied target intent/rules; inspect useful
   findings or honest no-findings, revision binding, missing technology coverage and
   separately authorized prose export. Source delivery alone does not cover this.

All product CLI/help, schema validation, tests/fixtures, build/package/install,
migration/compatibility, independent audit/lease/effective-rule machinery and CI
are **deferred-by-owner**, authority **U001**, owner **program #322 coordinator / P7**.
Next action: **P7 selects redesigned checks after implementation**. Direct parsing
and content inspection are syntax/source evidence only.

## First actual mapping delivery

The [first mapping handoff](../../../workflows/2026-09-23-framework-redesign-control/reports/p5-actual-mapping-scope.md)
and later direct user approval in task #346 select nine actual packages only.
At the local mapping checkpoint based on `7fab3ffd1698e2eb8ef791d6be7748f151506642`,
manifest.yaml gains the actual workflow (10), reviewer (3), requirement (4) and
specification (7) closures. Existing five rows/44 members stay byte-identical;
all nine total 68 explicit package members. Every source/destination mapping keeps
the member path under its owning package. No source design/workflow/history is mapped.

Work-management adds only software-development-orchestrator@0.1.0; collaboration
selects all nine; new engineering selects only code-reviewer, requirement-author
and spec-author@0.1.0. lesson-minimal and knowledge remain byte-identical.
Manifest/profile versions stay 1 and the Codex adapter remains selected. Declared
payload counts and expected unrendered Codex-entry counts are 9/1, 26/3, 28/3, 14/3,
68/9 for lesson-minimal, knowledge, work-management, engineering and collaboration.
A profile is a convenience selection, not a new package dependency.

This mapping does not register later engineering, structured or optional packages,
activate root routes or produce installed artifacts. Source member/profile/byte
comparisons are direct content evidence, not loader/schema/build/compatibility
verification. P7 deferrals remain under U001. Prior approval failures and the
successful later direct-user-authorized continuation remain in the issue-owned
workflow report/task; future mapping requires the next explicit coordinator handoff.

## Final actual-source mapping and complete selections

The [final mapping handoff](../../../workflows/2026-09-23-framework-redesign-control/reports/p5-final-mapping-scope.md)
adds nine delivered closures/45 members to the original nine/68, for 18 components
and 113 explicit payload members. The original nine component rows, Codex adapter
and protected lesson-minimal/knowledge/work-management profile bytes remain intact.
Source-only records are not package members. Exact source counts and preserved
Git blobs are retained in the owning workflow's final report/task.

Engineering now selects ten packages/53 members; collaboration selects sixteen/107
and excludes the two optional context-maintenance capabilities. New source-repository
implements the selected adoption proposal plus the delivered engineering methods:
fifteen packages/99 members, exactly collaboration minus local-backlog. New
context-maintenance selects only ai-context-auditor and ai-context-governance:
two packages/six members. All seven profiles remain version 1 with exact package
versions and Codex only. Profile grouping introduces no package dependency.

Each profile is a **complete selection**, not an overlay. Applying context-maintenance
after an ordinary profile does not implicitly union them and may remove previously
selected managed files. A deliberate combined profile requires a separate selection;
none is invented here. No build, rendering, application or root adoption occurred.
The profile declarations do not authorize those operations or prove compatibility.

This completes #346's bounded source/mapping assignment. P7 retains actual product,
installation and runtime verification under U001; provider closure and adoption stay
separate. Historical source-only and first-mapping checkpoints above retain their
original scoped observations rather than being rewritten as full verification.
