# v0.13 Terminal Release Readiness

## Workflow Metadata

- `workflow_id`: `2026-08-12-v0-13-release-readiness`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-12-v0-13-release-readiness`
- `base_branch`: `main`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-12-v0-13-release-readiness`
- `created_at`: `2026-08-12T07:20:06+08:00`
- `updated_at`: `2026-08-24T10:36:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Historical problem statement at the 2026-08-12 checkpoint: the v0.13 implementation and candidate were complete, but PR candidate packaging still scanned the accumulated release registry and therefore treated terminal `v0.12.0: validated` plus `v0.13.0: validated` as an ambiguous pair. The owner's clean branch rewrite also removed the former preservation merge from ancestry while the workflow evidence still claimed it remained present.
- Terminal reconciliation: Issue #243 recorded a live 2026-08-24 read-back showing hosted Release `v0.13.0` published at `2026-08-12T10:27:15Z` and coordination Issue #61 closed/completed at `2026-08-12T10:27:44Z`. The declared terminal anchor therefore supersedes the obsolete resume projection without changing the terminal source record or rewriting intermediate evidence.
- Authorized outcome: complete all repository and provider work through an exact clean-main pre-tag preparation for `v0.13.0`, leaving only the repository owner's creation and push of the printed annotated tag command.
- Included work: reconcile the already integrated and independently verified #187 SDK-free baseline; harden #194 with mandatory pre-send completion validation and a real schema-valid callback; author and validate the v0.13 release record, notes, migration guide, and phase contract; perform #193 archive/payload review; bind PR candidate selection to changed governed release records under #197; reconcile the owner's clean corrected branch topology; reconcile #61 and included Issues; pass focused, hosted, candidate, provider-preflight, and merged-main pre-tag gates.
- Exclusions: creating, moving, deleting, recreating, or pushing `v0.13.0`; creating a GitHub Release or publishing assets; changing `EngineeringGuardrails.Contracts.*` under #179; rewriting historical release or assessment evidence.
- Completion criteria: all included Issues satisfy prepublication provider state; PR candidate selection resolves exactly one changed governed candidate, treats zero as not applicable, and fails closed on multiple candidates; the real candidate passes its version-owned candidate contract and user-view review; the accepted branch passes hosted checks and is integrated; final clean `main` passes provider preflight and `prepare-ai-context-release.py --version v0.13.0`; the generated tag command is reported without execution.

## Authorization And Delivery

- Owner instruction: `OK，那完成到可以發布 0.13` on 2026-08-12 authorizes implementation, validation, GitHub transport, integration, and pre-tag readiness. Tag creation and hosted publication remain owner actions under the source release policy.
- Work items: [#187](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/187), [#193](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193), [#194](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/194), [#197](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/197), and coordination [#61](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/61). Issues #191 and #192 are completed included work already integrated by PR #195.
- Delivery cohesion: completion-envelope hardening and the release candidate share the exact release gate, branch, hosted validation, provider reconciliation, rollback, and final frozen-main handoff. One workflow avoids an unvalidated release snapshot between them.
- Planned topology: merge commit. The branch groups a release record, provider state, candidate review, external-task evidence, and immutable tag handoff as one durable integration event.

## Artifact Contract

- Release record: `.dev/releases/v0.13.0/release.yaml`
- Release notes: `.dev/releases/v0.13.0/release-notes.md`
- Migration guide: `.dev/releases/v0.13.0/migration-guide.md`
- Phase contract: `.dev/releases/v0.13.0/release-phase-checks.yaml`
- Remediation report: `.dev/workflows/2026-08-12-v0-13-release-readiness/reports/remediation-report.md`
- Tasks: `.dev/workflows/2026-08-12-v0-13-release-readiness/tasks/`

## Workstream Triage

| Workstream | Authority | Owner | Task | Terminal evidence |
| --- | --- | --- | --- | --- |
| External completion envelope | #194 | `ai-context-governance` | `VAL005-002` | pre-send schema validator plus real source-task callback |
| v0.13 candidate and tag handoff | #187, #193, #197, #61 | `ai-context-governance` | `REL013-001` | changed-release binding, candidate archive review, hosted PR checks, provider preflight, clean-main preparation |

## Historical Stages And Checkpoints (retained)

The stage states below are the last durable 2026-08-12 intermediate snapshot.
They remain evidence and are not the current resume projection after the
declared terminal-anchor reconciliation.

1. Freeze `main@afd54f63db51d88bb573e758535ae9692f8aa61a`, live Issue/Project state, and the completed #187/#191/#192/#193 implementation evidence. `completed`
2. Require delegated tasks to validate the complete terminal envelope before source-task delivery, then prove it with a real callback. `completed`
3. Reconcile and close #187/#194 when their integration acceptance is satisfied. `completed`
4. Instantiate and validate the exact v0.13 candidate, including notes, one-source upgrade policy, provider reconciliation, and real archive user-view evidence. `completed`
5. Close #193/#197, retain #61 as release coordination, reconcile the owner-rewritten clean branch, push without history rewriting, pass hosted checks, and merge with the selected topology. `in_progress`
6. On the final clean integrated `main`, pass provider preflight and pre-tag preparation, then hand the printed annotated-tag command to the owner without executing it. `pending`

## Current Reconciliation Checkpoint

- Last completed action: reconciled the v0.13 workflow and `REL013-001` to `completed` from the declared tracked terminal anchor under Issue #243.
- Current task: none; all workflow-owned tasks are terminal.
- Exact next action: none inside this historical workflow. Integration of the #243 governance change remains a separate pull-request/provider action.
- Validation already available: tracked terminal-anchor evidence, focused positive/negative fixture coverage, and repository workflow validation recorded by the #243 workflow.
- Blockers: none for workflow completion. Provider refresh is intentionally outside ordinary offline validation.

## Superseded Resume Checkpoint (retained 2026-08-12)

- Last completed action: the owner rewrote the remote branch to clean corrected head `ff70dc38ab97d287dde9b5a3fe9f364a26b4c947`; local and remote matched, the old evidence chain and preservation merge were no longer ancestors, and all nine original/corrected pairs remained tree-equivalent. #197 then added PR base/head changed-release binding, passed focused Git-backed regression coverage, and reached closed/completed provider state with `Done / Approved / P1 High / v0.13.0 / Not yet published`.
- Current task: `REL013-001`.
- Exact next action: commit the validated #197 delivery, perform a normal non-force push to PR #196, and require every hosted check to pass at that exact head before merge.
- Validation already available: PR #195 passed five hosted checks; `ASM-20260811-002` found all #187 findings addressed; `ASM-20260811-006` found no new #193 blocking finding but correctly deferred the real candidate review.
- Blockers: none for the PR checkpoint. Any future need to rewrite the shared branch must be explained and separately authorized, or handed back as a prepared branch plus exact owner commands. The callback/dedup defect remains residual risk and is not marked repaired. Tag creation and publication are intentionally excluded owner actions.

## Critical Gate And Callback Disposition

- Release gate execution: `passed` at `a9a00dc29063fd5ed5ca86b15d62add11e02e798`; the release runner executed 9 selected checks, passed all 9, and recorded 0 failed or blocked outcomes.
- Profile selection: 52 registry checks were not selected by the release profile and are retained as `not-applicable`, not failures. The terminal compatibility summary separately called out Selected Git Commit Messages because `COMMIT_RANGE` was unset.
- Callback transport: `failed`. The successful task's terminal payload did not exactly match its reported validated completion, and a delayed duplicate task overwrote the shared ignored completion path with a non-valid pending record.
- Owner disposition: accept the independently retained release-runner evidence, retain callback/dedup as failed, stop local reruns, and proceed to exact-head hosted PR validation.
- Durable evidence: `evidence/REL013-001-critical-gate-execution.yaml` and `evidence/REL013-001-critical-gate-transport.yaml`.

## AI Attribution Reconciliation

- Primary session metadata records `OpenAI Codex (gpt-5.6-sol, max)` for the v0.13 workflow commits; earlier `sol/high` trailers and task metadata were incorrect.
- Delegated callback, candidate-build, and critical-gate evidence was produced by `OpenAI Codex Sub-Agent (gpt-5.6-luna, high)` and is represented only on commits that retain that material evidence.
- Nine workflow commits were replayed in order with corrected trailers. Their original SHAs remain historical execution references, and all nine original/corrected pairs are tree-equivalent.
- The repository owner subsequently rewrote the remote branch to the clean linear corrected chain at `ff70dc38ab97d287dde9b5a3fe9f364a26b4c947`. Original evidence head `4dcf2c94a2fa2a625c8e6e35d592af2bbe0c024a` and abandoned preservation merge `9782bda97f6af354edcc3c14482b738a5f62103e` are not ancestors of the current branch.
- Agents must not perform a future force-push without first explaining the need and impact and receiving explicit authorization; the safe alternative is to prepare a separate clean branch and return exact owner commands.
- Durable mapping: `evidence/REL013-001-ai-attribution-reconciliation.yaml`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | workflow bootstrap | `fed4f2eaa42851fd8a9151586fbdc0c1c86332c7` | local | `2026-08-12T07:20:06+08:00` | Complete #194 hardening and exact v0.13 pre-tag readiness in one release-boundary delivery | Implement `VAL005-002`, then author the candidate |
| 2 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | validated #194 checkpoint | `14911780b0b78364ba454c9999e237ed9038f5a9` | local callback regression | `2026-08-12T07:31:00+08:00` | Pin the pre-send contract before the real source-task callback | Reconcile #194 and continue `REL013-001` |
| 3 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | candidate retry authorization | `5ee9b2f5c6307795dd75627992e683144d56f391` | local real candidate | `2026-08-12T07:54:30+08:00` | Preserve attempts 1/2 and authorize the bounded writable-output retry | Await #193 owner read-back of the passing candidate |
| 4 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | candidate provider gate | `ee348d79986279a9696609613855d77f63473fea` | live read-only provider reconciliation | `2026-08-12T08:10:31+08:00` | Prove every included Issue and Project field satisfies candidate policy | Commit receipt, then delegate the critical gate |
| 5 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | critical release gate subject | `a9a00dc29063fd5ed5ca86b15d62add11e02e798` | local owner-authorized host execution | `2026-08-12T10:05:34+08:00` | Preserve the 9/9 passing runner independently from the failed callback/dedup transport | Commit split evidence, push, open ready PR, and require exact-head hosted checks |
| 6 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | AI attribution reconciliation | `82ba7e73c1b389d492f3c24fe24aaafb80479222` | local corrected first-parent chain | `2026-08-12T16:56:34+08:00` | Correct primary and sub-agent attribution while preserving every evidence-bound original SHA | Create the evidence-preserving second-parent merge and validate the exact first-parent range |
| 7 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | abandoned preservation merge | `9782bda97f6af354edcc3c14482b738a5f62103e` | superseded; not in current ancestry | `2026-08-12T16:59:27+08:00` | The proposed merge retained the erroneous chain and did not match the owner's desired clean topology | Preserve as historical evidence only; do not merge it back |
| 8 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | owner clean-history rewrite checkpoint | `ff70dc38ab97d287dde9b5a3fe9f364a26b4c947` | local and remote exact match | `2026-08-12T17:41:57+08:00` | Retain only the corrected linear commit chain while keeping old SHAs as historical execution references | Implement #197, normal-push the next exact head, and run hosted PR checks |
