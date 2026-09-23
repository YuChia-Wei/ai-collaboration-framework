# P4 portable workflow orchestration

Workflow: 2026-09-23-workflow-orchestration. Owner: ai-context-governance.
Issue: [#341](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/341), program #322 / P4.
Status: in_progress; contract-reconciliation. Created/updated: 2026-09-23T09:09:21+08:00.
Template: .ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md, version 1.2.0.

## Authorized scope and durable state

This workflow preserves the two-stage same-task boundary: a local design checkpoint, coordinator contract reconciliation, then separately handed-off product implementation. That state is not adequately represented by a single Issue status. The current deliverable is [contract.md](../../design/framework-next/workflow-orchestration/contract.md), its record shapes, exact interface proposal, examples and Traditional Chinese explanation.

Assigned worktree F:/framework-next/341; branch codex/2026-09-23-workflow-orchestration; base main; exact starting commit 3a82b3654976fb26da7618a4404f49d7868d813a. Git common directory C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git. Initial direct read-back matched all four and clean porcelain. Runtime/model provenance: coordinator-declared and coordinator-reported runtime read-back gpt-6-astra / ultra; this executor has not independently attested runtime metadata. No sub-agents or new tasks.

Current write roots: .dev/design/framework-next/workflow-orchestration/ and this workflow directory. Later proposed source root: src/skills/software-development-orchestrator/. No shared index/coordinator/manifest/profile/root runtime/settings edits. No first push, PR, merge, Issue/Project change, credentials or release.

## Tasks and completion criteria

| Stable task | Status | Owned result |
| --- | --- | --- |
| P4-CONTRACT | completed | Implementable record/lifecycle/config-v2/metadata-v2 contract, ten expected members/operations, synthetic examples, retention and composition boundaries, C341-01..05. |
| P4-SOURCE | in_progress | Current action is coordinator reconciliation; source implementation has NOT started and is not yet authorized by this checkpoint. Continue in the same task after explicit selection. |

[Task records](tasks/P4-CONTRACT.json) and [P4-SOURCE](tasks/P4-SOURCE.json) retain scope and next action. No placeholder audit/test task is manufactured. Completing P4-CONTRACT does not complete #341 or the full workflow.

Observable design criteria: minimal semantic create; stable tasks/dependencies; visible actual caller-attributed evidence/failure/deferral; bounded resumable next action; config-v2 isolation; closed metadata-v2 and version dispositions; selectable store/tracking/retention/inert templates; safe preview semantics; specialist independence; exact members/operations; explicit limitations/decisions. Source criteria remain pending coordinator reconciliation and later source delivery.

## Authority, inputs and U001 adaptations

- Root AGENTS.md, temporary redesign override, execution-plan.md U001 and coordinator p4-orchestration-scope.md / ISSUE-341.json.
- Live Issue #341 read as OPEN on 2026-09-23. Initial sandbox read failed because the proxy connection was refused; the same read-only command succeeded with scoped network permission. This is no provider mutation.
- Runtime governance wrapper resolves canonical .ai/assets/skills/ai-context-governance/skill.yaml. Dispatch's nonexistent canonical SKILL.md was corrected by the coordinator; no substitute skill invoked.
- P1 portable/source-layout contracts and P3 selected contract; actual PR/backlog metadata/public references. #334 knowledge shapes are selected design inputs, not proof of delivered packages.
- Narrow graph index only for src/distribution, persistence=false. load_package discovery showed defaults closed to store/template. No index SHA was reported; direct Git HEAD plus matching tracked/blob bytes verified the material finding. Known-path .ai/scripts/validate-git-commits.py read directly; no archive indexing or product imports.

Owning skill templates are adapted under U001. Shared index edits are coordinator-owned; handoff is a small owned JSON plus report. Legacy validator, independent audit, lease and native handoff compliance is not claimed. Source policies above are not future product dependencies.

## Resume checkpoint

Last completed action: design authored; actual limited check status is in [checkpoint-report.md](reports/checkpoint-report.md).
Current task: P4-SOURCE.
Next action: coordinator reconciles C341-01..05 with actual #334 packages and metadata default ownership, then sends the exact accepted source scope to this SAME task. Until then stop after local commit/callback; do not edit src.
Expected checkpoint identity: containing commit of [handoff.json](handoff.json); resolve with Git history. No fabricated self-referential SHA.
Unresolved choices: exact identity/surface; candidate-only composition; preview-only cleanup; completion with attributed deferrals; metadata-v2-compatible operational defaults.
Source dependency: #334 actual source return and coordinator selection. #337/shared mappings remain coordinator-owned.
#316 remains separate/open according to the current scope record; no closure claim.

## Verification and integration

Only direct UTF-8/JSON/YAML syntax, selected source/reference/Git inspection, diff whitespace and exact planned message format run under U001. Product CLI/help, schema validators, tests, fixtures, build/package/install/migration, audit/lease machinery and CI remain deferred-by-owner to program #322 coordinator / P7. P7 selects and executes replacement verification; syntax is not acceptance.

Local coherent commit only. Coordinator owns first push and online PR integration. Preserve the referenced checkpoint. Proposed integration is a checkpoint with in_progress state; coordinator selects actual topology. No downstream adoption follows from source integration.
