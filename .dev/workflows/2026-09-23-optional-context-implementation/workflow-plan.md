# Optional context source implementation workflow

- workflow_id: `2026-09-23-optional-context-implementation`
- owner_skill: `ai-context-governance` (existing source route)
- status: `completed`; current_phase: `completed`
- created_at: `2026-09-23T10:35:25+08:00`; updated_at: `2026-09-23T10:38:08+08:00`
- template_source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- template_version: `1.2.0`
- branch: `codex/2026-09-23-optional-context-implementation`; base_branch: `main`
- worktree: `F:/framework-next/357`; base: `59877b8d2f61e9a95615ea95d597fe35da2f44cf`
- coordinator task: `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`

## Scope and authority

[Issue #357](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/357),
read live as open during intake, implements the
[P5 final selection](../../design/framework-next/p5-final-capability-contract.md)
of D352-01..06. The assignment is source authoring with local commit handoff.
Use the [U001 override](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md).
Only the six specified package members and this issue's own design/workflow may
change. The [source design](../../design/framework-next/optional-context-implementation/README.md)
lists exact members and operation handoff. All shared integration belongs to the
coordinator; push, PR, merge and Issue/Project mutations are not executor actions.

This workflow has one substantive task, [OCM-357](tasks/OCM-357.json), because a
single bounded source assignment covers two independent instruction packages and
one coherent handoff. Workflow mode preserves source authority, U001 deferrals,
exact ownership and the cross-session local delivery; no audit task is invented.

## Completion criteria

1. Exactly three real members per package; metadata 3/package 0.1.0; null config;
   empty dependencies/roles/schemas/templates/tools; own local method reference.
2. Auditor audit/compare remains read-only toward its subject and distinguishes
   comparison from independent review. Governance propose/apply follows actual
   authority without a duplicate permission or proposal gate for direct edits.
3. Prose default, requested export and existing-format ownership remain useful;
   protected files/history/recovery and actual knowledge handoff facts are kept.
4. Direct permitted checks and their limits are recorded, with all suspended
   verification assigned to program #322 coordinator / P7 as `deferred-by-owner`.
5. Exact complete commit-message bytes are checked before a coherent local commit;
   final handoff reports immutable HEAD, scope and remaining owners.

## U001 adaptations

The existing governance templates supply identity/time/task/report structure.
Baseline/post-audit, effective-rule/acceptance packets, leases and native handoff
validation are `deferred-by-owner` under U001, owner program #322 coordinator / P7.
There is no assessment finding resolution or product behavior acceptance claim.
The source task can complete when its own content/checks are complete; deferred
framework verification, integration and Issue closure remain separate.

Declared execution provenance is the dispatched independent GPT-6 Astra / ultra
conversation (`gpt-6-astra`, `ultra`), not independent runtime attestation. No
sub-agents, executor-created conversations, product operations or fixtures are used.

## Resume and delivery

Source authoring, content inspection, direct checks and full message-file check
are complete. Actual outcomes and deferred verification are recorded in the
[delivery report](reports/source-delivery.md). No implementation decision remains
unresolved in this scope. Shared mapping/profile selection and P7 observations
remain assigned elsewhere.

Delivery is one coherent local commit in the existing persistent Git object
database. The final response supplies its actual identity and clean-status
read-back before first push; the report gives a Git locator for the same commit. Coordinator owns commit organization and
online PR integration. A linear integration is suitable for this bounded source
change; final topology remains the coordinator's integration decision.
