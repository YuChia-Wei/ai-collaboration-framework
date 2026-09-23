# Knowledge lifecycle workflow

## Identity and authority

- Workflow: `2026-09-23-knowledge-lifecycle`; skill: `ai-context-governance`.
- Status: `in_progress`; phase: contract-reconciliation. Only KL-001 completes at this checkpoint.
- Issue: [#334](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/334), program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Authority: explicit coordinator dispatch, [handoff](../2026-09-23-framework-redesign-control/handoffs/issue-334.yaml), [U001 override](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md).
- Worktree: `F:/framework-next/334`; branch: `codex/2026-09-23-knowledge-lifecycle`; base: `main`; starting HEAD: `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`.
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version `1.2.0`. Created/updated timestamps are in workflow.yaml.
- U001 adaptation: design/source stages replace baseline/audit ceremony; no audit/lease/handoff-validation machinery, legacy checks, product runs or CI. Declared model/effort: gpt-6-astra / ultra, not separately attested. No sub-agents or child-created tasks/worktrees.

## Scope and completion criteria

This first checkpoint owns only `.dev/design/framework-next/knowledge-lifecycle/`
and this workflow. It defines implementable lifecycle, version/preservation,
config/coexistence, authority and promotion boundaries, schemas/examples and exact
package members. It must compare actual P2 source with proposed reuse. It does not
implement the product, edit shared contracts, install a runtime or complete #334.
Source, tools, .ai/.agents/.github, coordinator records and shared indexes remain
protected. An ignored own commit-message file is permitted by the handoff.

| Task | State | Completion boundary |
| --- | --- | --- |
| [KL-001](tasks/KL-001-contract.json) | completed | Bounded design/schema/example contract; direct content/data inspection; local checkpoint commit. |
| [KL-002](tasks/KL-002-implementation.json) | in_progress | Coordinator reconciles C334-01..04; same task then implements explicitly assigned source. Source implementation has not begun. |

Overall completion requires actual Lesson/ADR/promotion source and truthful P7
verification disposition. Online integration/Issue/Project states belong to the
coordinator and remain distinct. No push, PR, merge, provider mutation, credential
change or release is authorized to this executor.

## Evidence and next action

[Checkpoint report](reports/contract-checkpoint.md) contains inspected sources,
actual checks, initial failed approval review and verification deferrals.
[Design entry](../../design/framework-next/knowledge-lifecycle/README.md) points to
the contract, three draft schemas, synthetic examples and member proposal.

Coordinator reconciles config v2 with #335, metadata v2 multi-version schema
loading and explicit read_schemas, the standards-promotion owner and its local
evidence trust boundary. Then resume this SAME Codex task with exact source
ownership. This is internal reconciliation of authorized work, not a new owner
permission request. Proposed source roots are lesson, adr and standards-promotion;
none is writable under this first-turn checkpoint.

The containing checkpoint commit identifies the design bytes; do not self-insert
its SHA into tracked content. Return its exact HEAD, branch, paths, checks and
remaining work before first push. Shared index row proposed for coordinator:
`2026-09-23-knowledge-lifecycle | ADR and Lesson lifecycle | ai-context-governance |
in_progress | Issue #334 | contract-reconciliation`.
