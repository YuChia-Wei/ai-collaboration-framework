# Framework redesign coordination

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-23-p6-adoption-plan`; base: `main`; status: `in_progress`.
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
| #334 | P3-A knowledge lifecycle | Lesson/ADR/promotion source and own design/workflow | integrated PR #343; Issue/Project complete; P7 verification deferred |
| #335 | P3-B work management | PR/local-backlog source and own design/workflow | integrated PR #340; Issue/Project complete; P7 verification deferred |
| #337 | P3-C distribution support | metadata loader/direct call sites and own design/workflow; exact mappings follow actual source | loader PR #339 and final mapping PR #343 integrated; Issue/Project complete |
| #341 | P4 workflow orchestration | own contract/workflow first; source follows reconciliation | source online in PR #350; actual shared mapping pending |
| #342 | P5 capability/schema design | own design/workflow only; implementation slices follow selection | design integrated PR #349; Issue/Project complete |
| #345 | P6-A installation/update design | own design/workflow only; implementation follows selection | design online PR #355; Issue/Project complete |
| #346 | P5-A instruction support/reviewer | shared loader/adapter plus own reviewer package; mapping follows actual delivery | source online; mapping blocked by automatic approval review |
| #347 | P5-B engineering methods | five own instruction packages/design/workflow | write blocked by automatic approval review; awaiting direct confirmation |
| #348 | P5-C portable authoring | two own instruction packages/design/workflow | source online PR #353; Issue/Project complete |
| #351 | P5-D frame/compliance design | own design/workflow only | design online PR #358; Issue/Project complete |
| #352 | P5-E optional maintenance design | own design/workflow only | design online PR #358; Issue/Project complete |
| #354 | P6-B state/planning | own reader/plan modules and design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #356 | P5-F frame/compliance source | two own packages/design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #357 | P5-G optional maintenance source | two own packages/design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #359 | P6-C maintenance writer | coordination/bootstrap/apply/recover and direct state/plan integration | source inspected and locally integrated; online PR pending |
| #361 | P6-D source adoption design | own concrete path/route/configuration adoption plan and workflow | design selected and locally integrated; online PR pending |

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

Current action: integrate #359 source and #361 design online, then read back the provider receipt. After that checkpoint, resume #346/#347 only on the pending direct confirmation required by automatic approval review; complete actual mappings and remaining source before P7. #354/#356/#357 source is online in PR #360, with CLOSED/COMPLETED and Project Done read back. #359 is active under [the writer handoff](../../design/framework-next/p6-writer-handoff.md). #346 mapping and #347 engineering writes await the consolidated direct confirmation required by automatic approval review; no substituted writes. #351/#352 design is online PR #358 and CLOSED/Done. Product verification and CI remain deferred to P7.

## P3 shared implementation continuation

Both contract checkpoints are received. [Reconciliation](reports/p3-contract-reconciliation.md) and [selected contract](../../design/framework-next/p3-shared-contract.md) authorize owned source continuation in the same #334/#335 tasks. #337 supplies shared metadata-v2 distribution support in another independent Astra Ultra task; actual manifest/profile mapping follows package delivery. Original bootstrap/contract commits remain retained.

## Remaining work and verification

P4-P6 implementation and P7 redesigned validation/pipeline review remain open. Final independent review, tool trials and I/O tests have not run. Pipeline restoration is not scheduled automatically. [Remediation report](reports/remediation-report.md) maps current evidence without claiming final closure.

## Remaining P5 design dispatch

Both tasks are active from shared checkpoint `731d658b6004110fd59224ca39aa3a5d63891d91`. [Runtime and first-command read-back](evidence/p5-remaining-design-dispatch.json) confirms gpt-6-astra / ultra and assigned F: worktrees. No source/design completion or verification is implied.

## P6 source and P5 mapping dispatch

[Actual dispatch evidence](evidence/p6-planning-dispatch.json) records #354 runtime/F: identity and #346 explicit fast-forward to `5986b2146bb4559609acb0d5c7d09e8570375ea8`. They own different source paths. Neither implementation completion nor execution is inferred.

## Final P5 source dispatch

[Runtime and first-command evidence](evidence/p5-final-source-dispatch.json) records #356 and #357 on the preserved design checkpoint `59877b8d2f61e9a95615ea95d597fe35da2f44cf`. Both use independent Astra Ultra tasks and distinct F: worktrees. No package mapping, product execution or acceptance is implied.

## P6 writer dispatch

[Runtime and first-command evidence](evidence/p6-writer-dispatch.json) records #359 on preserved checkpoint `f7fd09faeb52860fde9cde83ea6cf395df883f66`, with one owner for complete maintenance source. It has not executed or installed the product; P7 evidence remains deferred.

## Source integration and adoption planning

PR #360 merged as `4b28710c39fed90acfd568cadbe3639ecb0ed722`; source Issues #354/#356/#357 and Project state were read back at `2026-09-23T10:58:13.4943619+08:00`. All four completed source/integration branches were deleted only after clean worktree and merged-ancestry checks; F: worktree files remain detached at their handoff commits. Active #359 and blocked #346/#347 branches remain. The ignored provider read-back is `.dev/ai-context/local/framework-next-control/p5-p6-source-integration-readback.json`; retained source integration reports distinguish limited checks from deferred execution.

[The #361 assignment](../../design/framework-next/p6-source-adoption-handoff.md) selects concrete adoption design only. It preserves the first Lesson pilot and explicitly separates broader root adoption, missing mappings/source, legacy recovery and later P7 observations.

[Actual #361 dispatch](evidence/p6-adoption-dispatch.json) binds the independent Astra Ultra task to `b4a147c1bc8ec00fcdb92a7006c142209c61a29f` and the assigned F: checkout. No source activation or design completion is inferred.

## P6 maintenance and adoption return

[Fixed-subject inspection and selection](reports/p6-maintenance-and-adoption-integration.md) records #359 source and #361 design. Both local worktrees were clean and tasks idle at handoff. The limited source/design checks passed; product behavior, root adoption and all final findings remain unverified. The live online receipt will be `.dev/ai-context/local/framework-next-control/p6-maintenance-adoption-readback.json`; no receipt exists merely because this locator is named. Source completion does not restore pipelines or begin P7.
