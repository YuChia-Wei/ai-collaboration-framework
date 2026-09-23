# Knowledge lifecycle workflow

## Identity and authority

- Workflow: `2026-09-23-knowledge-lifecycle`; owner skill: `ai-context-governance`; implementation: `slice-implementer` generic slice.
- Status: `completed`; phase: local-source-complete. Verification remains deferred-by-owner.
- Issue: [#334](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/334); program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Authority: explicit coordinator continuation, [handoff](../2026-09-23-framework-redesign-control/handoffs/issue-334.yaml), [selected P3 contract](../../design/framework-next/p3-shared-contract.md), [U001](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md).
- Assigned worktree: `F:/framework-next/334`; branch: `codex/2026-09-23-knowledge-lifecycle`.
- Original source baseline: `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`; preserved design checkpoint: `99adb0762328c8f8d6cff7338f17caec99685c0a`; selected contract fast-forward: `0d0556d4c60105a28eb39cfb06efab9b069728cb`.
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version `1.2.0`; timestamps in workflow.yaml.
- Declared execution: gpt-6-astra / ultra from dispatch, not independent runtime attestation. No sub-agents, child tasks or new worktrees.

## Scope and bounded completion

Own only `src/skills/lesson/`, `src/skills/adr/`, `src/skills/standards-promotion/`,
this workflow and the knowledge-lifecycle design subtree. Ignored own commit-message
files are permitted. C: checkout, shared contracts/distribution/manifest/profiles,
root entries, runtime wrappers, coordinator records and shared indexes are protected.
All repository commands use the explicit assigned F: worktree; edits use absolute
F: paths. Coherent commits enter the existing persistent Git object database.

| Task | State | Completion boundary |
| --- | --- | --- |
| [KL-001](tasks/KL-001-contract.json) | completed | Preserved design/schema/example checkpoint and historical direct-inspection report. |
| [KL-002](tasks/KL-002-implementation.json) | completed | Three selected source packages and permitted direct inspection complete; P7 verification assigned. |

Selected packages are Lesson 0.2.0 (9 members, 11 operations), ADR 0.1.0
(8 members, 11 operations), Standards Promotion 0.1.0 (9 members, 10 operations).
Each carries a complete public contract and local script/schema/template, metadata
v2 and isolated config v2 with empty skill dependencies. Lesson keeps v1 config
compatibility and exact legacy schema bytes; old records are read-only, with
explicit derive to a new v2 identity. Promotion owns proposals only and observes
adoption/content/effect independently. Once adoption was ever observed, revision
stays blocked; conflict resolution needs a new identity and new adoption.

Bounded source completion does not close Issue #334, reconcile Project state,
verify runtime behavior, integrate shared distribution or publish a release.
No push, PR, merge, provider mutation, credential change or publication is authorized
to this executor. Coordinator owns integration and first push.

## Checks, evidence and continuation

U001 permits direct UTF-8/JSON/YAML/AST/reference/source/Git inspection and the exact
planned commit-message validator only. Product CLI (including help), tests, schema
validation, build/install/migration/compatibility/benchmark execution, independent
audits/leases, legacy gates and CI remain `deferred-by-owner`, responsible owner
program #322 coordinator / P7. Effective-rule/audit packets are not manufactured.

[Historical checkpoint report](reports/contract-checkpoint.md) preserves original
checks and initial approval-review failure. [Design entry](../../design/framework-next/knowledge-lifecycle/README.md)
provides the selected contract/inventory and synthetic examples. [Source completion report](reports/source-implementation.md)
records actual narrow checks separately from deferred behavior. A local commit is
custody, not execution evidence. Return exact HEAD/branch/worktree and member/
operation inventories to the coordinator before first push; do not self-insert the
containing commit SHA into tracked records.

Coordinator next integrates the local delivery and supplies actual package mappings
to #337. P7 selects focused behavior/schema/filesystem/compatibility/CI execution and
records real outcomes. Suggested shared workflow-index row at source completion:
`2026-09-23-knowledge-lifecycle | ADR and Lesson lifecycle | ai-context-governance |
completed | Issue #334 | local-source-complete; verification deferred-by-owner`.
