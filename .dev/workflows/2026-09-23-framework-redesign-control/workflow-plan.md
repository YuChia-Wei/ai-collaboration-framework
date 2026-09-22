# Framework redesign coordination

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-23-framework-redesign-control-cont-02`; base: `main`; status: `in_progress`.
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version 1.2.0, adapted for U001.

## Authority and completion

U001 is the current owner-selected execution boundary. Follow repository skills, work-item/branch/workflow/commit discipline and online PR integration. Do not run or recreate legacy validators, test matrices, critical gates or hosted PR checks during early development. Final verification is deferred to P7; no waived/deferred check becomes passed. No sub-agents or child-created tasks. All implementation tasks use independent gpt-6-astra / ultra conversations.

This coordinator owns dependencies, task/branch/PR mapping and integration. Issue workers own only their assigned files and issue workflow. The root index is coordinator-owned to avoid parallel edits. Every PR declares which Issue is complete versus still waiting for later delivery or verification.

## Initial work allocation

| Issue | Phase | Owner paths | State |
| --- | --- | --- | --- |
| #324 | P0 transition control | scoped override, root/source pointers, one exact source-only distribution exclusion, own workflow | local implementation complete; online integration pending |
| #325 | P1-A portable contracts | `.dev/design/framework-next/portable-contracts/`, own workflow | active independent task |
| #326 | P1-B source/consumer layout | `.dev/design/framework-next/source-layout/`, own workflow | local delivery received; cross-contract review pending |

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

Current action: integrate #324 delivery `ee8aadbbfc363ac9a206535134d0bdcd73e72203` through the online PR path. Coordinator review found the original source-only prose did not exclude the new override from `.dev/standards/**` package selection; CORR-001 adds the exact exclusion to the existing source-only group. Bootstrap and original delivery commits are preserved because handoff records reference them. #326 delivery `42601292b9fa1d4fbd190c0d03f570c25e991624` is available for cross-contract review with #325; no P2 implementation has started. Exact task IDs and worktrees remain in tasks/ISSUE-*.json. Full verification remains deferred to P7.

## Remaining work and verification

P2-P6 implementation and P7 redesigned validation/pipeline review remain open. Final independent review, tool trials and I/O tests have not run. Pipeline restoration is not scheduled automatically. [Remediation report](reports/remediation-report.md) maps current evidence without claiming final closure.
