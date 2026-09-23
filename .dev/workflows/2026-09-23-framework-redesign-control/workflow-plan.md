# Framework redesign coordination

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-23-p4-orchestration-dispatch`; base: `main`; status: `in_progress`.
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version 1.2.0, adapted for U001.

## Authority and completion

U001 is the current owner-selected execution boundary. Follow repository skills, work-item/branch/workflow/commit discipline and online PR integration. Do not run or recreate legacy validators, test matrices, critical gates or hosted PR checks during early development. Final verification is deferred to P7; no waived/deferred check becomes passed. No sub-agents or child-created tasks. All implementation tasks use independent gpt-6-astra / ultra conversations.

This coordinator owns dependencies, task/branch/PR mapping and integration. Issue workers own only their assigned files and issue workflow. The root index is coordinator-owned to avoid parallel edits. Every PR declares which Issue is complete versus still waiting for later delivery or verification.

## Initial work allocation

| Issue | Phase | Owner paths | State |
| --- | --- | --- | --- |
| #324 | P0 transition control | scoped override, root/source pointers, one exact source-only distribution exclusion, own workflow | integrated PR #328; Issue/Project complete; P7 verification deferred |
| #325 | P1-A portable contracts | `.dev/design/framework-next/portable-contracts/`, own workflow | integrated PR #329; Issue/Project complete |
| #326 | P1-B source/consumer layout | `.dev/design/framework-next/source-layout/`, own workflow | integrated PR #329; Issue/Project complete |
| #330 | P2-A Lesson implementation | `src/skills/lesson/`, own workflow | integrated PR #333; Issue/Project complete; verification deferred |
| #331 | P2-B candidate assembly | selected distribution/profile/adapter/tool paths, own workflow | integrated PR #333; Issue/Project complete; verification deferred |
| #334 | P3-A knowledge lifecycle | Lesson/ADR/promotion source and own design/workflow | source inspected and locally integrated; online PR pending |
| #335 | P3-B work management | PR/local-backlog source and own design/workflow | integrated PR #340; Issue/Project complete; P7 verification deferred |
| #337 | P3-C distribution support | metadata loader/direct call sites and own design/workflow; exact mappings follow actual source | loader merged PR #339; final mapping inspected and locally integrated |
| #341 | P4 workflow orchestration | own contract/workflow first; source follows reconciliation | independent design checkpoint task active |
| #342 | P5 capability/schema design | own design/workflow only; implementation slices follow selection | independent design/inventory task active |

The two P1 design issues may proceed in parallel with P0 because each receives U001 directly and owns separate files. Integrate the transition control first, reconcile the P1 contracts together, then open P2 implementation against the integrated design. Do not start mass migration or validator rewrites early. Later stages remain in execution-plan.md until their input contracts are ready; do not create many speculative implementation issues now.

## Completed preparation

- Complete planning checkpoint retained and merged online; no direct main push.
- Deleted 25 local and 18 remote merged branches. Two squash-merged branches were proven with exact PR head/merge SHAs. Two unmerged experimental branches remain. Three existing worktrees were detached with all files preserved.
- Repository Actions disabled; all seven workflows disabled_manually; no active/queued jobs required cancellation.
- F: capacity read back as approximately 16 GiB; `F:/ai-context-tests` preserved. New checkouts use `F:/framework-next/<issue>/`.
- See evidence/ci-suspension.json and evidence/branch-cleanup.json. These read-backs establish administrative state, not product validation.

## Integration sequence

Workers return local commits before push. Coordinator inspects exact scope and organizes unshared commits into coherent units without erasing the expressly retained assessment or referenced handoffs. Push only the selected branch, read back remote SHA, create a PR, inspect content and actual deferred checks, merge through GitHub, then read back main and work-item state. No credentials, release, tags or downstream adoption are included.

## Resume checkpoint

Current action: #334 knowledge source and #337 final 44-member/four-profile mapping are inspected and locally integrated; complete their combined online PR and Issue/Project read-back. See [knowledge inspection](reports/p3-knowledge-integration.md) and [mapping inspection](reports/p3-mapping-integration.md). #335 is merged/closed through PR #340. #341 workflow design runs in task `01a0cbc8-448d-7270-b27b-295295914afb`; #342 capability/schema design runs in task `01a0cbd1-789e-7c72-9852-ba5edd3a6998`. Both have verified Astra Ultra and assigned F: execution, and neither may change product/shared source before coordinator selection. Product execution remains deferred to P7.

## P3 shared implementation continuation

Both contract checkpoints are received. [Reconciliation](reports/p3-contract-reconciliation.md) and [selected contract](../../design/framework-next/p3-shared-contract.md) authorize owned source continuation in the same #334/#335 tasks. #337 supplies shared metadata-v2 distribution support in another independent Astra Ultra task; actual manifest/profile mapping follows package delivery. Original bootstrap/contract commits remain retained.

## Remaining work and verification

P3-P6 implementation and P7 redesigned validation/pipeline review remain open. Final independent review, tool trials and I/O tests have not run. Pipeline restoration is not scheduled automatically. [Remediation report](reports/remediation-report.md) maps current evidence without claiming final closure.
