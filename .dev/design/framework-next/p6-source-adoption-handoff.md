# P6 source-repository adoption design assignment

[Issue #361](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/361) supplies a concrete source-repository adoption plan while #359 implements managed maintenance. This is a design-only task under [U001](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md). It does not activate the product, replace blocked #346/#347 writes, or start P7 execution.

## Inputs and ownership

Use the assigned fixed source, [assessment and execution plan](../../assessments/ASM-20260923-00-6oq/execution-plan.md), selected [P6 contract](p6-selected-contract.md), [writer handoff](p6-writer-handoff.md), source-layout and portable-contracts designs, the #342 capability/schema inventory, and actual delivered package handoffs. Read selected current root entries/routes/configuration/attributes/ignore files where necessary. Reuse existing inventories instead of scanning historical workflows, assessments, tests or all legacy implementation.

Own only `.dev/design/framework-next/source-adoption/` and `.dev/workflows/2026-09-23-source-adoption-design/`. Do not modify root entries, skills, mapping, installer, configuration, CI, source indexes or historical records. No new schemas, tools or report machinery solely to support this design.

## Required decisions

1. Produce an exact path/owner/disposition matrix. `src/` remains the sole editable product source; the repository root consumes the framework and retains project/source-maintenance policy. Preserve project `.dev`, `.ai/custom`, release/governance/CI duties, frozen records and any active legacy recovery. Identify each actual predecessor route and the selected successor prerequisite before retiring it; avoid duplicate active owners and wholesale deletion.
2. Keep the first P7 pilot **lesson-minimal / Lesson 0.2 / Codex**. Separately describe the broader root capabilities/profile selection needed for this repository from actual delivered source. Optional context maintenance remains optional. State exactly what the pilot can establish, which legacy routes remain active, and what is required for whole-repository adoption. A partial pilot is not completed adoption.
3. Give concrete, reviewable proposals for root pointers, generated versus project ownership, byte-preserving Git attributes/tracking/ignore, explicit configuration/template/store bindings, and legacy status. Map current meaning to successor binding; do not perform mass moves, semantic rewrites, new migration implementation or actual configuration changes. Select exact paths only when current evidence supports them; otherwise name the precise unresolved input. Do not guess flags, backend guarantees or release state.
4. M01 remains unassigned unless an actual P2 config-version-1 input needs the narrowly selected version-2 conversion. Bound any absence conclusion to inspected paths. Source, project configuration and project-data backups/rollback remain separate from the managed installer's snapshot. Specify quiescence and activation sequencing; installer `project_readiness` stays `not-assessed`.
5. Identify later public-reader observations and acceptance questions without executing them. Map dependencies on #359, blocked source/mapping, the later adoption action and P7 verification/pipeline review. P8 CLI/provider work remains optional. The plan must allow continuation without hidden conversation state.

## Delivery and limits

One independent GPT-6 Astra / ultra task uses only `F:/framework-next/361`, its assigned branch and absolute edit paths. No sub-agents, executor-created conversations, callbacks or provider mutation. Preserve `F:/ai-context-tests` and all other worktrees. The coordinator receives a coherent local design checkpoint before first push and owns online integration.

Use the owning governance skill/templates proportionally for issue workflow and a bounded final report. Direct UTF-8/JSON/YAML reading, references, fixed-source/Git inspection, `git diff --check` and the exact complete commit-message validator are allowed. No product CLI/help/import, schema validation, tests/fixtures/build/package/install/migration/probes, audits/leases/acceptance packets or CI. These are **deferred-by-owner**, authority U001, owner program #322 coordinator / P7; next action is later selected implementation and verification. Design completion does not claim behavior, migration safety, adoption or framework completion.
