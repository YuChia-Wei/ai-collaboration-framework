# Framework redesign coordination

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-23-p5-authorized-continuation`; base: `main`; status: `in_progress`.
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
| #341 | P4 workflow orchestration | own contract/workflow first; source follows reconciliation | source online PR #350; mapping online PR #366; Issue/Project complete |
| #342 | P5 capability/schema design | own design/workflow only; implementation slices follow selection | design integrated PR #349; Issue/Project complete |
| #345 | P6-A installation/update design | own design/workflow only; implementation follows selection | design online PR #355; Issue/Project complete |
| #346 | P5-A instruction support/reviewer | shared loader/adapter plus own reviewer package; mapping follows actual delivery | complete source/mapping online PR #366; Issue/Project complete |
| #347 | P5-B engineering methods | five own instruction packages/design/workflow | source online PR #363; Issue/Project complete; final mapping assigned to #346 |
| #348 | P5-C portable authoring | two own instruction packages/design/workflow | source online PR #353; Issue/Project complete |
| #351 | P5-D frame/compliance design | own design/workflow only | design online PR #358; Issue/Project complete |
| #352 | P5-E optional maintenance design | own design/workflow only | design online PR #358; Issue/Project complete |
| #354 | P6-B state/planning | own reader/plan modules and design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #356 | P5-F frame/compliance source | two own packages/design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #357 | P5-G optional maintenance source | two own packages/design/workflow | source online PR #360; Issue/Project complete; verification deferred |
| #359 | P6-C maintenance writer | coordination/bootstrap/apply/recover and direct state/plan integration | source online PR #362; Issue/Project complete; execution deferred |
| #361 | P6-D source adoption design | own concrete path/route/configuration adoption plan and workflow | design online PR #362; Issue/Project complete; adoption unperformed |
| #364 | P7-A focused verification design | own design/workflow only | design online PR #367; Issue/Project complete |
| #365 | P7-B pipeline/policy design | own design/workflow only | design online PR #367; Issue/Project complete |
| #368 | P7-V1 source contracts | runner/helper/contract tests and selected observed distribution repairs | independent Astra Ultra task active; actual F: identity verified |
| #369 | P7-P1 dormant source gates | .github source gates/tests and prospective source policy | independent Astra Ultra task active; native continuation awaits actual V3 interface |
| #370 | P7 installation source review | own review workflow only; fixed ten-file source read-only | independent Astra Ultra review active; fixed product subject |

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

Current action: receive #368/#369 implementation outcomes, receive the independent fixed-source #370 review, then arrange V2/V3 from the actual helper interface. [Dispatch observations](evidence/p7-implementation-dispatch.json) verify the two active tasks. Only assigned narrow execution is authorized; native/root/CI outcomes remain outstanding.

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

## Direct owner confirmation

The owner directly confirmed “確認 #346、#347 原定寫入範圍”. [Scope and retained rejection history](reports/p5-owner-confirmed-resume.md) bind the reply to the same two tasks at resumed checkpoint `4cda6689bf469a2273e14e237a0c3bf7ad4b6eed`. #346 returned record-only checkpoint `7fab3ffd1698e2eb8ef791d6be7748f151506642` after automatic review again required direct user input in that executor task. #347 returned source `814fd12822bb270f17edbfe91d0864ba07c1aacb`; [bounded inspection](reports/p5-engineering-source-integration.md) selects it for online integration. No replacement writer or scope expansion is introduced.

## Final mapping continuation

The user reported “P5 A 已完成，可繼續”. Fixed first mapping `444327034aa14d9a9364c72e33e77ac879e9e5df` is inspected and locally integrated; its earlier approval refusals remain historical. [The final handoff](reports/p5-final-mapping-scope.md) selects all 18 actual components/113 members, ordinary engineering/collaboration, the complete source-repository selection and a separate optional context-maintenance profile. No product execution or root activation is assigned.

## Complete source selection and P7 entry

Final #346 source/mapping `4ffa3881484783a2e35152ad426bec359d2d9252` is locally integrated. [Inspection and retained preparation outcomes](reports/p5-final-mapping-integration.md) record exact selection and the narrowed Project update after automatic review refusal. #364/#365 are design-only work items with disjoint ownership; they start only after this batch is online. Their proposed checks and replacement rules require coordinator reconciliation before bounded implementation/trials, with final owner adoption still required for CI restoration.

## P7 design dispatch

[Runtime and first-command read-back](evidence/p7-design-dispatch.json) binds both independent Astra Ultra tasks to `171f33474f88888fbe853600de04bfe9c5716b25` and their distinct F: worktrees. Project Status is In progress; no release or owner-review field was changed. PR #366 and #341/#346 closure/Project Done were read back at `2026-09-23T14:28:27.3418807+08:00`. Completed P5 branches were deleted only after merged-ancestry and clean-state proof; F:/framework-next/346 remains detached with all files preserved.

## P7 design reconciliation

[Fixed design inspection](reports/p7-design-reconciliation.md) selects the bounded source checks and dormant pipeline/source-policy work. [Original-request coverage](reports/request-coverage-at-p7-entry.md) keeps actual use, root adoption and conditional future capabilities distinct. No product trial has yet run.

## First selected P7 implementation

PR #367 merged at `01aeb8ae4f18132dfdd7ad3479346c78b9f5f913`; design Issues are CLOSED/COMPLETED and Project Done. #368 owns shared source checks; #369 owns dormant source gates and prospective rules, with native continuation kept open until actual V3 binding exists. New task Project Status is Planned only; release/owner-review fields were not changed. Completed design branches were removed after clean/merged proof; all RAM worktree files remain.

#370 also started with verified Astra Ultra runtime and actual F: identity. Project is In progress by live read-back; the reviewed product subject remains `38e6458f8d3e81dc2568daf1fa467571fb529fee`. No review result is implied.

## First actual checks and narrow repair

[#368 observations and scope reconciliation](reports/p7-first-observed-repairs.md) retain initial F: preparation failure, the later actual selected run, two metadata alias repairs, an incorrect test assumption and the bounded GitSource path repair. There is no passing layer result yet. The original #370 subject remains fixed; any engine change receives affected later review.

## First P7 returned checkpoint

[Fixed-return reconciliation](reports/p7-implementation-checkpoint.md) records actual failed source contracts, passing selector tests, two automatic approval stops and the independent CR-001 finding. #368/#369 remain partial; #370 awaits affected re-review after repair #371. Unaffected real-runner binding continues only in the original #369 task. No product repair, CI restoration, native or root acceptance is implied.

The #369 real contracts binding returned at `6c5f4a298bc3ffdbea47348ae6ef8c9f4584b41d`; 28 focused tests passed using synthetic runner results. Policy/public/native remain incomplete. #371 is active in its verified independent task and F: checkout; it does not take over the stopped path/policy writes.
