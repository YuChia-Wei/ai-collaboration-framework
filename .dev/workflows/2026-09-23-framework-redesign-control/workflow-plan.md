# Framework redesign coordination

## Current action: start rc.2 in a fresh coordinator task

The owner directly instructed rc.2 execution on 2026-09-24 and allowed a fresh
continuation task after preparation. The [compact transfer](handoffs/rc2-coordinator-transfer.md)
owns current start instructions. S1 fixes shared formats and migration scope;
S2-S6 then proceed under their exclusive owners. The selected scope does not need
another overall approval merely because this task is transferred.
The sender retains write ownership until receiver acceptance and explicit release.

Receiving coordinator: `01a0d226-d1f7-7d43-ad20-8b7b9f8e0e00`, requested Astra/ultra, assigned
`F:/framework-next/rc2-coordinator`. Its first turn accepted the clean prepared
checkpoint `2a2f1244` read-only. The sender's remaining work is online handoff
integration and explicit exclusive-writer release; then the receiver starts S1.

## Current direction: rc.2 planning; stable is not ready

On 2026-09-24 the owner selected further iteration: preserve skill IDs, prefer
`aicf-` generated entry names, restore Claude, move reusable engineering knowledge
into `src`, and make installation selective. Source self-adoption must not force
engineering knowledge/.NET installation. These directions supersede the earlier
inspection-only sequencing below, while preserving historical results.

Read the [concrete rc.2 proposal](../../design/framework-next/rc2-installation-selection.md)
and `latest_checkpoint.rc2_planning` in the machine handoff. The proposed layout,
selection format and six implementation units are for review; no implementation
task is dispatched and no product/target files are changed by this checkpoint.
R1-R7 remain explicit, with R8 added for selectable installation and engineering
knowledge productization. Stable readiness is `not-ready-by-owner`.
#369 native expansion remains deferred-by-owner; U001, CI suspension and the
separate publication/adoption boundaries remain in force.

## Online-main completeness and known release-scope inventory

The owner evaluates online main across computers before choosing stable contents.
Read the [complete current inventory](reports/successor-acceptance-and-repair-scope.md#online-main-completeness-and-known-release-scope-inventory)
and coordinator-transfer.json latest_checkpoint.online_main_inventory.

At source d6a725ef / target cc0e3453, no delivered product merge backlog was found:
43 source commit ancestors, 33 scoped Issue states, retained experimental blobs,
the RC-to-main source delta and target tracked installation were checked.
Old experimental snapshots must not be merged over their accepted successors.

Before stable scope is final, explicitly disposition source self-adoption, actual
new-format publication/delivery, stable update/rollback, cross-computer admission
and recovery, the owner's deferred native/CI/policy work, runtime/target decision
configuration boundaries, and input-specific stable verification (R1-R7).
The main product is newer than the immutable installed RC baseline by the CR-002
GitSource repair. Source root routing remains legacy; inspect src/skills for the
new source and target .ai/core/skills for the installed product.

The C: analysis archive is local/uncommitted with no configured remote; online
Git does not include its raw admission/recovery evidence. This online inventory
is the portable handoff, not a new test pass, adoption or authorization to expand
#369. Known existing residuals must not be presented later as newly discovered work.

Observed: 2026-09-24T08:07:21.645747+08:00.

## Current checkpoint: ready for owner inspection and task archival

The owner will archive the work tasks and inspect the framework and mq lab
before opening a new task for 0.19.0. No automatic continuation, native expansion
or CI restoration is selected. Program #322 and Issue #369 remain open.

Direct owner authorization created and pushed annotated tag v0.19.0-rc.1
at installed candidate source 1ce41a4f03f61e83bf9b99de3ce196887547e922.
Tag object: 40e41e7b4f33cb07ca84d789b768e40bcbe6f13f. Remote peeled commit
matched. This names the existing Codex pilot baseline; no GitHub Release or
assets were published. It does not retroactively validate release-source records
or change the installed engine pin 3afb4ff4207acb3e12e3953018736305a439ed21.

Target PR16 remains integrated at cc0e345367a1d24f49bf8fa68e0eb668df9e5e55.
Both C: target checkouts are clean at that commit. Keep the pilot checkout:
the historical review descriptor includes its absolute root. Inspecting the same
tree in original main does not claim relocated admission. The old source main
9338a85 was only a historical one-shot bootstrap; its seven exact files were
archived before updating that checkout. Do not rerun the historical preflight.

Cleanup removed eight clean merged worktrees, eleven merged local branches and
nine merged remote branches before this checkpoint integration. Each removed
worktree's ignored evidence was archived and hash-checked first. A stale upstream
caused one safe branch deletion refusal; the failure is retained, then merged
HEAD/main ancestry was confirmed and that obsolete upstream was cleared.

External reports, raw evidence and restart guidance are stored in:
C:/Github/YuChia/ai-collaboration-framework-analysis/codex/framework-rc1-closeout-20260924/README.md.
baseline.json preserves source/candidate/engine/target identities;
cleanup-results.json is the operation ledger; per-root manifests bind copied
bytes. The analysis repository's pre-existing changes were left untouched.

Preserved: unfinished F369; pinned F386 engine; coordinator checkout; all
p7-runs/failed fixtures and F:/ai-context-tests; target pilot/recovery data;
three dirty F:/codex-v018-evaluation worktrees; unmerged design/Luna branches
and Luna checkout; the historical v016 projection with an unreleased lease.
The three dirty F: worktrees include independent raw-file, index and working
diff backups on C:. All 1623 p7-runs files also have verified C: byte copies.
Byte archives preserve evidence, not original filesystem identities or runtime
leases. RAM-disk roots must be reconstructed and rechecked if lost.

Future 0.19.0 work starts from this checkpoint, the external README and current
provider/Git readback. Preserve the owner's #369 deferral. Select any new
native/CI/policy adoption and publication contract explicitly; do not restore
legacy full matrices automatically. New-framework Claude adapters remain
unsupported. Historical sections below retain earlier observations; this
checkpoint and latest_checkpoint control current navigation.

Observed: 2026-09-24T07:34:15.344638+08:00.

## Current affected-review result and repair assignment

Observed at 2026-09-23T17:58:21.695505+00:00. Original #370 completed immutable review
6d9184e8e01d826131d03dd603422b5a3a1a7e4a against ae40e6cb0d49cdfb8e2174c732d74e1d918d0c2f.
Parent verified ten engine raw/Git/prior/installed comparisons, direct producer
hash, both preserved historical reports and its exact four-record delivery.
[Current-engine report](../2026-09-23-installation-source-review/current-engine-review.md)
finds one P2 source defect, CR-002: Windows error-1 direct_directory fallback can
admit a DOS-drive alias to a source descendant, evading the candidate producer's
lexical/visible-ancestor output isolation. This is concrete source-predicate
reasoning without a native mapping reproduction, not a maintenance apply/recover
escape or existing-file overwrite.

C-001 is a separate unverified protected-path casing/API premise. It is not a
substantiated defect and does not select a source repair. The earlier CR-001
loader disposition remains resolved; changed/unchanged source and attributed
execution evidence are explicitly separated. Review completion is not blanket
engine, native, target, policy/CI or publication acceptance.

Original #368 task 01a0cd11-1dc9-7842-abba-65b8fac0edb8 now continues under its
existing GitSource/assembly defect scope and Issue comment 5800095738. Its same
F:/framework-next/368 branch was clean and fast-forwarded to the review delivery.
The explicit Astra/ultra dispatch is active in app readback. Only direct_directory,
its necessary existing-module private helper, immediate output_parent call if
needed, test_contracts regressions and own records are selected. No actual SUBST
mapping or host setting change is allowed. Only affected focused checks and one
actual C5 selection may run after a clean repair checkpoint, with prior caps/raw
output/failure preservation. No repair pass or handoff exists at this checkpoint.

#368 and #370 stay OPEN; original #370 owns the affected re-review after repair.
#369 native-extension and target-provider decisions remain pending. No source
sub-agent, replacement task, C-001 repair, native trial, target mutation, policy
adoption or CI restoration is created by this continuation.

## Prior integration and independent review continuation

Observed at 2026-09-23T17:44:32.050285+00:00. PR392 is MERGED at
ae40e6cb0d49cdfb8e2174c732d74e1d918d0c2f; exact remote head, all 29 changed
paths and the three original delivery ancestors were verified. Empty hosted
checks remain deferred-by-owner, not passed. #368 and #369 stay OPEN; #373 stays
CLOSED/COMPLETED and Project Done.

The original #370 independent Astra/ultra task
01a0cd16-e671-7ae0-9f31-9ac1fd1e9b2a resumed in recreated F:/framework-next/370,
branch codex/2026-09-24-current-engine-review, at that immutable merged source.
Issue comment 5799832277 assigns the same ten-file EnginePin closure, focused on
six changed files since reviewed source 0d29b9abf36804cb2587732232d807a1b754c3a0.
All ten files equal the actual installed engine 3afb4ff4. Only its existing
review-workflow records may change; original reports remain. Product/native
execution, repairs and source sub-agents are excluded. Actual app readback showed
active execution; explicit dispatch selects gpt-6-astra / ultra, without inventing
new runtime attestation. Issue370 is OPEN and existing Project Status Verification;
only Status changed. The review result is pending, not passed.

F:/framework-next/373 and its local branch were removed after exact merged/clean,
closed-Issue and idle-task checks. Seven ignored files (7483 bytes) are hash-checked
in the persistent completed-worktree-archive/373 under the source bootstrap's
ignored framework-next-control directory. The remote branch pointed to already
merged 07b1778f; deletion used an exact-head lease and absence was read back.
The first preflight stopped on its remote-absence assumption, and the second on
PowerShell OrderedDictionary property projection; both stopped before archive or
deletion and are retained. Explicit integer accumulation confirmed unchanged file
bytes before the successful bounded attempt. All p7-runs and failed fixtures,
F:/ai-context-tests, current F368/F369/F370 and installed F386 engine remain.

Target a17cc80 remains locally admitted without provider integration. The two
pending direct owner questions still govern target push/PR/merge and the #369
native extension. CI/policy adoption, source-root adoption and stable release/
actual target update remain incomplete. No dependent action follows elapsed time.

## Prior selected P7 integration checkpoint

Observed at 2026-09-23T17:34:57.980273+00:00. The three original Issue tasks returned clean local
deliveries: #368 edfae7a868c54a35deb871d179caf5acd40c2c00, #369
5440a9f410c9a8dd5ae7895195c9ba2a1a4a5b64, and #373
4ab8c0ca0b24e8921d17482c596458f4d7685c94. This containing commit preserves all three
histories and the bounded coordinator review; online integration is the next
provider action, not a result asserted by this commit.

- #368 ran the selected 12 methods once at 29b0fafbf6cb4ac0a6caa57d24b841c8204241cd:
  passed, zero skips/errors, two actual Lesson candidate builds/readers. Its eight
  historical core comparisons remain separate from that invocation. Parent
  verified raw streams, all eleven executable inputs and unchanged historical
  failure inventories (240 entries, 93 file hashes, 674869 bytes). The only
  executable change corrects parse-only valid public/native argument expectations.
  Issue closure remains pending the required affected EnginePin independent review
  and online integration. Earlier #370 reviewed the prior loader repair, not all
  subsequent engine changes; current coordinator review does not replace it.
- #373's seven separately invoked public families passed on
  e71712b71791170c3f4946e131ce867f82dade8f. PR391 merged delivery 07b1778f at
  d4db3fb8e83e74acbe3bdfd5acf03dbd18bae8b7; live Issue state is CLOSED/COMPLETED
  and Project Done. The returned four-record closeout is included here. Totals
  span separate runs: 218 public plus 37 driver Git launches; opaque nested
  launches are unavailable. All 14 runner streams remain; successful child
  transcripts were removed by existing cleanup. No aggregate or hosted pass.
- #369's bounded original-scope selector/test change passed 44 focused methods
  once, zero skips. The tested working-tree bytes match code commit 76b2c013;
  the final records-only commit does not change those bytes. Its existing V2
  parser accepted all seven actual #373 captured results, with nine immutable
  receipt blob identities, 14 stream hashes and five test-source hashes checked.
  Replay launched no product runner. Only finite ownership maps/provenance
  constants and classification changed; parsers, caps and native caller remain.
  #369 stays OPEN / In progress for the separate native/policy/CI obligations.

Coordinator common-route bounded source review found no actionable finding.
This is not formal independent P7/policy-adoption review. Original failures,
read-preparation errors and the limits of every evidence reuse remain visible.
No product suite was repeated solely for integration.

Completed worktrees F:/framework-next/381, /382 and /383 and their local branches
were removed only after clean merged-ancestor/closed-Issue checks and exact
persistent archive verification: ten ignored files, 10805 bytes in total, under
C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/
framework-next-control/completed-worktree-archive/{381,382,383}.
Their remote branches were already absent; none was deleted by this cleanup.
The initial remote-existence preflight stopped before deletion and is retained.
All p7-runs, failed fixtures, F:/ai-context-tests and the F386 installed engine
remain. F368/F369/F373 are retained at this checkpoint.

The target pilot remains locally admitted and unchanged at
a17cc80ef112368ff47109926aad22915a654b35. Two direct owner questions remain pending:
target push/PR/online merge of those seven reviewed commits; and the exact #369
native-driver/caller extension and explicit roots proposed in Issue comment
5799329517. No dependent action is authorized by elapsed time. Source Actions
and all nine workflows remain disabled at the last live readback, policies are
dormant, and U001 applies. Root adoption, independent source adoption review,
effective-policy/CI adoption, stable release/publication and actual stable target
update remain incomplete and separately governed.

## Prior admitted target checkpoint

The complete target pilot is locally admitted at
a17cc80ef112368ff47109926aad22915a654b35, unchanged full tree
1f1bac4fcc564657ae8eddb4ee1c704cc85c7284. Independent reviewer
/root/target_rc1_audit returned no reportable findings for content subject
eb9b599369c9492024d33b5a2cc8327a7d0316ccc2655d46ee7fc650c080f621.
Its one current target gate passed in 25.923705 seconds; fourteen focused
regressions were reused with exact-input proof. Parent compared all 316 authority
files with raw and Git bytes, accepted the genuine receipt, passed --admit,
validated released lease, and removed only the exact owned review lock. Target
tracked bytes remain unchanged and clean.

Durable target proof is under
C:/Github/YuChia/dotnet-mq-arch-lab-rc1-pilot/.dev/ai-context/local/rc1-independent-review/attempt-01:
report.md, receipt.json, role-execution.json, parent-admission.execution.json,
parent-closeout.json and parent-final-manifest.json. Runtime preflight preparation,
the reviewer timestamp serialization failure, and the parent full-stat lock
comparison failure remain retained. The latter stopped before unlink; stable
identity plus exact owned-lock bytes admitted the later release. No behavioral
gate rerun or retrospective success claim erased these failures.

Target remote main remains cb122285af09e46b24102f22a0ad9d713219c1f2.
The seven local commits are reviewable in the ignored rc1-integration-proposal.md;
target push/PR/merge requires the pending separate direct owner decision. Issue 15
remains open. Stable publication and actual rc.1-to-stable update are incomplete.

Original #368/#369/#373 tasks were resumed for read-only evidence reconciliation,
not replacement tasks or sub-agents. #369 identifies compatible V1/V2 command
interfaces, missing generic native caller/hosted binding, changed engine bytes,
owned-process termination and durable evidence retention gaps. Caller/driver
changes, their selected executions, effective-policy cutover and CI adoption are
not represented as done. #368/#373 current-input reuse decisions remain pending.

Live source read-back: Actions enabled=false; all nine workflows
disabled_manually; rulesets including inherited returned []; main/protection
returned 404 with explicit Branch not protected. No setting was changed and no
hosted pass is inferred. Source root adoption, remaining P7 acceptance, release
delivery review and stable upgrade remain separate work. U001 and unselected
legacy/full/formal/hosted deferrals remain effective.


## Historical repair and review dispatch checkpoint

PR #388 merged the original #335 linked-worktree repair at eca7c971; its selected
real Git regression and installed target retry passed. #335 is closed / Project
Done after bounded coordinator review and live readback. The new complete rc.1
candidate was built/read from 1ce41a4f and delta-installed with two changed files.
Target is clean at a17cc80ef112368ff47109926aad22915a654b35, pilot-review, with
131 managed hashes and 132 Git/index/checkout byte/mode comparisons passed.
Independent target review P15-rc1-a17cc80-01 is dispatched; admission is pending.
See handoffs/coordinator-transfer.json latest_checkpoint and the successor report.
All earlier states below are preserved historical snapshots. Broader P7, target
provider integration, CI adoption, stable upgrade and publication remain distinct.

## Workflow metadata

- Workflow: `2026-09-23-framework-redesign-control`; owner: `ai-context-governance`.
- Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: [assessment](../../assessments/ASM-20260923-00-6oq/report.md), [authorized execution plan and U001](../../assessments/ASM-20260923-00-6oq/execution-plan.md).
- Planning checkpoint: `cee653cedd922e39c5b6dd2c64be7b2b5fad5b98`; merged through PR #323 as `a4865f355c71aa5c80d1a2c50b7a30ddb6ab5e66`.
- Branch: `codex/2026-09-24-rc1-pilot-continuation`; base: `main`; status: `in_progress`.
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version 1.2.0, adapted for U001.

## Authority and completion

U001 is the current owner-selected execution boundary. Follow repository skills, work-item/branch/workflow/commit discipline and online PR integration. Do not run or recreate legacy validators, test matrices, critical gates or hosted PR checks during early development. Final verification is deferred to P7; no waived/deferred check becomes passed. The owner's 2026-09-24 amendment permits short, clearly bounded work through coordinator-dispatched sub-agents with capable lower-cost profiles; larger or multi-stage work retains independent gpt-6-astra / ultra conversations. Executors do not create further tasks or delegate without a coordinator assignment.

This coordinator owns dependencies, task/branch/PR mapping and integration. Issue workers own only their assigned files and issue workflow. The root index is coordinator-owned to avoid parallel edits. Every PR declares which Issue is complete versus still waiting for later delivery or verification.

## Historical continuation handoff snapshot (owner update, 2026-09-23)

The owner requested a fresh Astra/Ultra coordinator and selected: repair known
problems first, then a versioned dotnet-mq-arch-lab pilot, then overall validators,
release path and pipeline review. Trial version: 0.19.0-rc.1; stable target: 0.19.0.
Neither version is released by this selection. The rc.1 installation must retain
a concrete path to the later stable version, not merely a changed version string.
Only repair/pilot-required focused checks precede the pilot; CI remains disabled.

The [current coordinator handoff](handoffs/coordinator-transfer.md) supersedes
historical active-task/approval wording below. #368/#369/#373 are open with their
returned checkpoints integrated; their latest turns are complete. Previous owner
confirmations are resolved. Root adoption and target installation remain undone.
The successor accepts shared-record ownership before updating the coordinator ID.

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
| #368 | P7-V1 source contracts | runner/helper/contract tests and selected observed distribution repairs | approved repair received; two actual assemblies; C5 reader and affected review incomplete |
| #369 | P7-P1 dormant source gates | .github source gates/tests and prospective source policy | approved dormant rules received; native binding and scoped review remain |
| #370 | P7 installation source review | own review workflow only; fixed ten-file source read-only | affected review online PR #374; Issue/Project complete within source-review scope |
| #371 | P7 source pin repair | maintenance source loading and focused cache tests | source/test checkpoint online PR #374; Issue/Project complete; public/native gaps retained |
| #373 | P7-V2 public skill checks | public test families/dispatch and own records | local partial checkpoint received; no complete family acceptance |

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

Current action: integrate the [directly approved returns and completion-based cleanup](reports/p7-approved-returns-and-cleanup.md). Both original authorization replies were received and the assigned edits completed. C5 now reaches two real builds and then the separate installation reader's F: strict-root failure; public writer-volume, affected independent review, V3/native binding, root adoption and CI adoption remain outstanding. No unchanged failing run or new implementation scope is selected merely to clean worktrees. Issues 368/369/373 remain open; 25 earlier completed worktrees were removed after live closure and exact merged/clean proof.

## P3 shared implementation continuation

Both contract checkpoints are received. [Reconciliation](reports/p3-contract-reconciliation.md) and [selected contract](../../design/framework-next/p3-shared-contract.md) authorize owned source continuation in the same #334/#335 tasks. #337 supplies shared metadata-v2 distribution support in another independent Astra Ultra task; actual manifest/profile mapping follows package delivery. Original bootstrap/contract commits remain retained.

## Remaining work and verification

P4-P6 source/design checkpoints are online. P7 selected source contracts and public checks have partial/failed evidence; the bounded source-pin repair and affected review are complete. Native installation, source adoption, effective policy transition and CI restoration remain open. Pipeline restoration is not scheduled automatically. Historical phase paragraphs below retain their observation-time statements; this resume checkpoint and current task records govern continuation.

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

PR #372 is MERGED at `3a21b0eb58e80752df010e7277aec55725b3061e`; all four P7 execution/review Issues remain open. The provider auto-close of #368 was corrected and both newly registered workflows explicitly disabled; all nine are now disabled_manually. [The retained checkpoint report](reports/p7-implementation-checkpoint.md) records exact transitions and the next source-pin repair/review.

[Source-pin repair handoff](reports/p7-source-pin-repair.md) receives #371 at `0d29b9abf36804cb2587732232d807a1b754c3a0`: nine focused loader tests passed; one unmodified public-entry attempt refused before dispatch. The original #370 task reviews only that fixed source delta and evidence limits. Blocked path/policy writes and public/native obligations remain separate.

The source-pin repair and affected source review are locally complete (#370/#371); the test-only follow-up passed 10/10 with product bytes unchanged. Their bounded online closure keeps public/native obligations in #322 / V3. #373 is selected for independent public-family tests using the already delivered helper, without installer activation or takeover of blocked writes.

#373 is active in `01a0cd49-7805-7202-9176-e8f7b4cf4285` at `F:/framework-next/373`, starting from `f8f0d073e6442df8a280c5941a2c7a1d6ed7060b`. Runtime Astra Ultra, actual first F: command and live Project In progress are verified in the dispatch record. No public-family passing result is implied.

PR #374 is online at `c10d874dc658d86ba9e3cf064271ffcfe4a25a14`, with bounded #370/#371 closure and Project Done verified. #368/#369/#373 remain OPEN / In progress; all nine workflows and repository Actions remain disabled. Completed branch cleanup preserved all F: worktree and failed-fixture files.

## Successor acceptance and first repair

[Acceptance and bounded repair scope](reports/successor-acceptance-and-repair-scope.md)
records the new coordinator, live provider state and #378 ownership. The owner order
remains repair, rc.1 pilot, then overall validator/release/pipeline review.

## Repair integrated and complete rc.1 preparation

PR #380 is merged at c1fb1c1fb07a6d246e3bcedd3cd851918f66b306. #378 is
CLOSED/COMPLETED and Project Done after the owner directly authorized closure
only for reviewed, accepted and online-integrated implementation Issues.
#322/#368/#369/#373 stay open. The full-framework pilot choice supersedes the
earlier Lesson-only target selection; source-root adoption remains separate.

The original #368 and #373 tasks were restored from archive and resumed on the
exact merged repair commit. #368 selects only C5 candidate/reader checks; #373
selects its seven existing public families once each, with dependent stop on a
new shared failure. Only their existing records may change in this continuation.
No whole P7 admission, native or downstream success is inferred.

Issue #381 prepares the missing versioned candidate identity, complete explicit
18-component profile and rc.1-to-stable candidate/lock planning input contract.
Its Issue records exact source/test ownership and bounded actual build/read
acceptance. Publication, actual stable output and target installation are separate.
The actual independent Astra/ultra #381 task is 01a0cea5-3b1a-7312-ab81-3e5edd32d651 in F:/framework-next/381.

Issue #382 supplies bounded real Windows maintenance observations before target
mutation. Its independent Astra/ultra task 01a0cea9-e5fe-72c1-8f95-ce82d01927c2
uses F:/framework-next/382, an isolated tiny native fixture, and explicit durable
C: recovery/observation parents. Product files stay read-only. Its development
fixture does not establish #381 versioned-candidate or complete target acceptance.
Both actual dispatches started clean at 031233202f21e0793c9667cac872375d65e52be0.

#368 returned bd40c830: the single selected C5 method passed once on c1fb1c1f,
including two real Lesson builds, reader acceptance and five synthetic refusals.
The record-only handoff is locally inspected/integrated; prior failed whole runs
remain visible. #368 stays open for its remaining reconciliation/review.


## Complete rc.1 and native continuation

The fixed #381 candidate implementation is reviewed for local integration.
The latest coordinator report retains its actual build/read identity, the owner
Codex-first Claude disposition, #373 workflow-only pass, and #382 native plan
failure. #383 owns only the observed protected-input Windows path repair.
Native acceptance and target installation remain pending.


## Candidate online; repaired native continuation

PR #384 merged at 9e114574; #381 closed/Done. Current branch is
codex/2026-09-23-native-pilot-continuation from that main. The latest report
records reviewed #383 protected-path repair and #373 PR-only pass. Resume the
original #382 native driver on the integrated fixed repair; keep source checks
and target activation separate. Target #15 has an isolated persistent worktree
and planning-only records, with target-owned gate coupling under analysis.


## Native prerequisite complete; target adoption underway

Reviewed #382 local delivery 96386941 supplies all selected native cases across
the truthful two-source continuation. Integrate #382/#383 online, then apply the
complete #381 rc.1 candidate in target Issue 15 with its newly adopted current
gate. Retain all failures and target independent review before readiness claims.


## Complete pilot capture repair

PR385 is merged; #382/#383 complete. Target complete rc.1 plan passed but actual
apply hit scan-limit before managed writes. Preserve all target failure evidence.
Directly confirmed #386 owns bounded IO/Reader repair and one full-candidate fixture
trial; task 01a0cedd-9907-78a3-b94b-37192978d04c in F:/framework-next/386.
Target gate development proceeds separately under its direct owner decision.


#386 final 3afb4ff4 is reviewed; actual full-candidate fixture apply passed at
64bf9f6e with all 131 members. Integrate online, then use a fresh engine pin/plan
for target Issue 15 while preserving its prior capture failure. Current target
gate is prepared at 1269a5fa and intentionally rejects incomplete admission.

## Installed pilot and PR Git worktree defect

Target local checkpoint 24998b88 holds the actual complete installation,
reconciled Codex/legacy routes and five local record lifecycles. It remains
pilot-blocked by actual PR Git worktree inspection failure. Original #335/task
resumed for a bounded source repair; see the latest successor report and live
Issue. Current branch is codex/2026-09-24-rc1-pilot-continuation from ff57a09b.
Preserve all old candidates/recovery/failed evidence. Independent target review
follows a newly built immutable candidate and explicit target delta update.


## Current CR-002 affected review and P7 coverage gap

Source PR393 is online at 3185c0f6f9546145a9ef93e486a9232b0e90b4b4.
Original #368 returned af5c4e39e193ef9cd161f203a5da211cfd95f7bf: six affected
methods passed once on 698654d7, including two actual Lesson builds/readers;
Win32 alias cases are simulated. Parent verified exact inputs and raw outputs;
the original #370 now reviews that fixed repair without product execution.

The original #369 read-only inventory identifies missing named-regression
bindings for implementation-only changes and unresolved enforcement of manual
admission requirements. Retain these as P7 adoption gaps. Target seven-commit
provider integration and the #369 native extension still await direct decisions.
No policy, CI, release or target provider action is inferred. See the latest
successor report and machine-readable handoff for evidence and boundaries.


Original #370 completed affected review at 67da0e4b9bf4b7e067f36cf8fd7d35c4e664c788:
CR-002 resolved in reviewed source, no new substantiated finding. Parent verified
17 raw/Git bindings and four preserved historical reports/inventories. #368 and
#370 meet their bounded criteria; online integration remains required before
conditional Issue closure and Project Done. C-001 remains unverified, with no
new native or target acceptance claimed.


## Verified CR-002 closeout; remaining owner decisions

PR394 merged at 63263834e334d094971719302a6da81e90765f0c. Exact head, 21
paths and all repair/review ancestors were read back. #368/#370 are now
CLOSED/COMPLETED and their existing Project Status is Done; other fields stayed
unchanged. #322/#369 remain open. No target provider action or native extension
was executed. The current target remains locally admitted at a17cc80ef112368ff47109926aad22915a654b35.

Completed #368/#370 worktrees and local branches were removed only after clean
state, merged ancestry, idle original tasks and durable archive/hash checks.
Twenty ignored files (440214 bytes) are preserved at the persistent source
control archive in 368-af5c4e39 and 370-67da0e4b. Remote branches were already
absent. The first cleanup preflight stopped before any copy/removal because
the historical 370 archive already existed; that failure and the old archive
remain, and the corrected unique destinations were verified after cleanup.
All p7-runs/failed fixtures, F:/ai-context-tests, unfinished #369, the actual F386
engine and all target candidate/recovery/admission evidence remain.

Await the existing direct owner decisions for target seven-commit push/PR/merge
and Issue369 native scope/roots. Before P7 adoption, reconcile the recorded
selector-to-regression and manual-admission gaps. Stable publication also needs
a separately selected/adopted new-format contract; no release, tag, policy or
CI restoration is implied by this closeout. C-001 remains unverified.


## Target integrated; native expansion deferred by owner

The user directly authorized dotnet-mq-arch-lab push/PR/online merge. Target PR16
merged at cc0e345367a1d24f49bf8fa68e0eb668df9e5e55 from reviewed a17cc80.
The seven commits and 222 diff paths were verified through three REST pages;
the initial truncated 100-file read stopped before merge and remains recorded.
The full tree is still 1f1bac4fcc564657ae8eddb4ee1c704cc85c7284. Current
admission passed before push (21.335462 s) and after merge (32.807636 s). All
48 original review artifacts / 346497 bytes matched; no tracked target bytes
or review evidence changed. The target pilot checkout is clean. Issue15 stays
open for later stable-version/update and rollback work; no release is claimed.

The owner then explicitly deferred the proposed Issue369 native additions,
concerned about later development interruptions and errors. The proposed
native driver/runner/caller expansion and new native run remain unimplemented.
The 44 focused tests and seven actual public-family results remain separate
from historical source-bound Issue382 native results; they do not establish a
current full native pipeline pass or sustained stability. Keep CI and policy
inactive. Any later blocking gate set needs a concrete owner adoption decision.
The selector/regression and manual-admission gaps stay recorded without a new
implementation selection. No approval question remains pending for this
deferred expansion. Decision: Issue369 comment 5804473245.

## RC.2 exclusive coordinator release and S1 dispatch preparation

The predecessor released exclusive source/Issue coordinator ownership after
online PR #400 merged at 6f5a13046f1978ba4b8701e4ae772faecde2c2ff. The receiving
task 01a0d226-d1f7-7d43-ad20-8b7b9f8e0e00 fast-forwarded its assigned
F:/framework-next/rc2-coordinator, confirmed clean Git state and matching
current-coordinator bindings in U001, workflow.yaml and the rc.2 handoff JSON.
Live GitHub main matched and #322 remained OPEN. The handoff is accepted and
write ownership is now with the receiver; this is not rc.2 completion.

S1 is prepared as a bounded contract and migration-inventory Issue with six
acceptance criteria. Its executor will own only
.dev/design/framework-next/rc2-contracts/ and
.dev/workflows/2026-09-24-rc2-selection-contract/. Shared distribution, manifest
and profile implementation remains S3-owned after S1 integration.

The actual gh issue create attempt was rejected by automatic approval review.
The stated reason was absence of trusted direct authorization for publishing
the exact payload, including task identifiers/design details, to the specified
GitHub repository. The target was YuChia-Wei/ai-collaboration-framework; the
5036-byte prepared body has SHA-256
12c086e03741c49c570ce2ff0fe70850e68c894f346a4cb73942e5673b47a4b8.
No Issue was created and no implementation task/worktree was dispatched.
The receiver requested concrete direct confirmation and did not retry or use
an alternate publishing route. The prepared body remains an ignored local
artifact until that decision; this progress record does not publish it.

Next: after confirmation, create S1, assign its F: worktree and independent
Astra/ultra task, then continue S1-S6. Preserve R1-R8 and fixed rc.1 identities.
Legacy/formal/critical verification, CI, #369 native expansion, dormant policy
adoption and new tag/Release publication retain their prior dispositions.
Direct JSON/YAML/content/Git and exact-message checks are separate from all
U001-deferred verification.

## RC.2 S1 dispatched after direct confirmation

The owner directly replied in receiving task
01a0d226-d1f7-7d43-ad20-8b7b9f8e0e00: "同意開立 issue 並接續工作".
The unchanged S1 draft was then successfully published as
[Issue #401](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/401).
The earlier automatic approval-review rejection remains historical evidence;
it is no longer the current dispatch blocker. No alternate publication route
was used and no Project item was added.

S1 was assigned an independent task under U001 from clean integrated main
6f5a13046f1978ba4b8701e4ae772faecde2c2ff. The task owns rc2-contracts
design and its 2026-09-24-rc2-selection-contract workflow only. It returns
local commits before first push. Exact runtime task/worktree/provenance
details remain in ignored local coordination evidence: a proposed Issue
comment containing those new details was rejected by automatic approval
review. The replacement public update contains product scope and progress
only; rejected details are not published via another route.

[evidence/rc2-task-dispatch.json](evidence/rc2-task-dispatch.json) records exact
ownership, acceptance IDs, dependencies and outstanding units. S1 is running;
S2-S6 remain undispatched pending their inputs. The coordinator will review
S1's complete contract and inventory before integration or dependent shared
distribution work. This dispatch is not implementation, behavioral verification
or rc.2 completion. Stable readiness and R1-R8 remain unchanged.

The [rc.2 acceptance status](reports/rc2-acceptance-status.md) maps the seven
selected completion criteria and R1-R8 to pending delivery/consumption evidence.
It is a progress projection, not a new approval or verification pipeline.

## S1 contract accepted for online integration

Issue #401 returned original document commit e27ff21cf06c91abdf5fde4f70c1bddb632b1898
and correction 32a2b59dd38f9335f60cf2edd8eac4d6d95f95cf. The coordinator reviewed
the fixed content and accepted the bounded S1 contract/inventory delivery after
separating legacy Codex projection from the new v2 adapter seam and correcting
the completed workflow phase. See [content review](reports/rc2-s1-contract-review.md).

The local integration retains both implementation commits and coordinator
checkpoints as a resumable branch boundary; online merge-commit PR integration
is selected. #401 is intended terminal-close after this accepted document
delivery reaches main; #322 is deferred/open for S2-S6 and the retained residuals.
No Project item is selected or created. Required legacy/formal/hosted machinery
remains deferred-by-owner under U001; no CI success is inferred.

After online integration, S2 owns exactly the two content package roots and S4
owns only its adapter roots plus the reserved Codex/Claude renderer files. Their
work can proceed independently. S3 starts shared distribution/manifest/profile
integration after their exact inputs are accepted, avoiding simultaneous shared
writers. S5 consumer/adoption and S6 actual verification remain pending.

## S1 online integration and bounded execution amendment (2026-09-24)

The owner explicitly authorized the prepared branch push, S1 PR/merge, #401
closure and continuation of S2/S4. The earlier push approval-review rejection
remains historical; the new direct authorization resolved it. PR #402 merged at
`173b2523767aece5004bc57c6e0cbba12898039a`; provider read-back confirmed #401
CLOSED / Project Done and #322 OPEN / In progress. Hosted checks were absent and
remain deferred-by-owner under U001/P7, not passed.

The owner then changed execution sizing: short, clearly bounded work may use
sub-agents and need not use Astra or a new task conversation. This source-only
amendment is effective for current dispatch and recorded in U001 plus both root
entries. It changes neither acceptance nor source/target/external-write authority.
S2 remains a substantial independent migration over 235 members; S4 has fixed
renderer/template seams and uses one bounded sub-agent with an appropriate
lower-cost profile. Each assigned worktree has one tracked writer; shared S3
callers/manifest/selection/ownership transitions remain reserved.

S2 Issue #403 and S4 Issue #404 were created and their complete acceptance and
ownership text read back. Dispatch starts from this coordinator checkpoint; the
accepted S1 contract remains bound to PR #402. S4 owns only the additional
`tests/framework_next/test_rc2_adapters.py` case module, not the shared runner.

Both assignments were dispatched from `9247f444eb14a86849c66078cd7fa366dc098379`.
S2 uses the retained independent-task route; S4 uses one bounded sub-agent.
Invocation references and selected runtime profiles are retained in ignored local
coordination evidence. Implementation, behavioral verification and integration
remain pending; dispatch is not delivery evidence.

## S4 bounded local delivery accepted (2026-09-24)

Issue #404 returned source 6d5c0df1 and acceptance-ID correction ece36743.
[Coordinator content review](reports/rc2-s4-content-review.md) accepts the bounded
implementation and exact S3 handoff. The correction did not change any reviewed
code/template/test/handoff blob. S2 remains in progress; S3 shared integration
waits for both accepted inputs. Existing #403/#404 Project Status was updated to
In progress and read back, without adding items or changing other fields.

## S2 bounded local content accepted (2026-09-24)

Issue #403 returned f22674e2 with all 235 members and exact S3 rows.
[Receiving review](reports/rc2-s2-content-review.md) records direct source/member/
metadata comparisons, the bounded semantic review and incomplete helper attempts.
The parent completed the remaining mechanical checks using a corrected independent
Git-blob comparison; no failed helper result was upgraded to success. S2 and S4
are ready for online integration. S3 remains the sole shared implementation owner
and starts only after that integrated input checkpoint.

## S2/S4 online integration and S3 preparation (2026-09-24)

PR #405 merged at `81c9603b6b5ceae7b0e33a541bc12e28118bc6be`. The pushed
head was read back and all 267 provider changed paths matched the local diff.
Fresh provider read-back confirmed #403 and #404 CLOSED / Project Done, with
#322 OPEN / In progress. The owner execution-sizing amendment is now online.
No hosted or behavioral pass is inferred; U001 deferrals remain.

S3 Issue #406 was created with S3-A1 through S3-A10, exact S2/S4 input pins,
sole shared implementation ownership and the before-first-push return boundary.
The full online body equals the prepared local draft. S3 is a substantial connected
distribution/maintenance change and uses an independent task; a short read-only
S5 consumer/retained-duty preparation uses a bounded sub-agent concurrently.
S3 must publish the exact operation/journal contract before any S5/S6 adoption use.

S3 was dispatched from clean `238f58bede46a8466699b5f9cd2307acb7155ac0`.
Its existing Project item was updated to In progress and read back. Actual
invocation provenance is retained in ignored coordination evidence. A bounded
read-only S5 analysis at 81c9603 identified the five direct consumers; S3 received
the precise verified-resource/binding interface requirement.

S5 consumer Issue #407 now has the accepted instruction-only scope S5C-A1 through
S5C-A6 and exact body read-back. Its five skill roots are disjoint from S3. Final
consumer instructions must bind to S3's concrete reading seam before acceptance;
the coordinator will serially return changed component rows to S3. This is separate
from source and mq-lab adoption and does not retire any retained legacy owner.
