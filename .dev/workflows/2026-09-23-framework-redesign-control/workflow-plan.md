# Framework redesign coordination

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-23-framework-p3-dispatch`; base: `main`; status: `in_progress`.
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
| #334 | P3-A knowledge lifecycle | knowledge-lifecycle design, own workflow; source scope follows contract reconciliation | independent Astra Ultra contract checkpoint active |
| #335 | P3-B work management | work-management design, own workflow; source scope follows contract reconciliation | independent Astra Ultra contract checkpoint active |

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

Current action: P2 merged through PR #333 at `ba36554b418977a2c8a12d51152c7b625bf48124`; #330/#331 are CLOSED/COMPLETED and Project Done. Independent #334/#335 tasks are active from checkpoint `a34ecd3c9423b17b6bb745f598ef22fd7437dd24`; model and assigned F: execution identity were read back in [dispatch evidence](evidence/p3-task-dispatch.json). Receive their early local contract checkpoints. They must settle lifecycle/authority, selected config namespace coexistence, owned schema/version and package member changes before concurrent product edits. The coordinator reviews both, chooses any common contract changes and resumes each same task with exclusive source ownership. These checkpoints do not close the Issues and do not require another user approval for already delegated routine design decisions. All product/tool/build/install trials stay deferred to P7.

## Remaining work and verification

P3-P6 implementation and P7 redesigned validation/pipeline review remain open. Final independent review, tool trials and I/O tests have not run. Pipeline restoration is not scheduled automatically. [Remediation report](reports/remediation-report.md) maps current evidence without claiming final closure.
