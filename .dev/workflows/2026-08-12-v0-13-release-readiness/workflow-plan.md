# v0.13 Terminal Release Readiness

## Workflow Metadata

- `workflow_id`: `2026-08-12-v0-13-release-readiness`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-12-v0-13-release-readiness`
- `base_branch`: `main`
- `status`: `in_progress`
- `current_phase`: `integration-validation`
- `artifact_root`: `.dev/workflows/2026-08-12-v0-13-release-readiness`
- `created_at`: `2026-08-12T07:20:06+08:00`
- `updated_at`: `2026-08-12T08:10:31+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the integrated v0.13 implementation has no governed release record, Issue #194's real hosted-check callback did not satisfy the canonical completion schema, and Issues #193 and #61 intentionally remain open until a real candidate archive receives user-view review.
- Authorized outcome: complete all repository and provider work through an exact clean-main pre-tag preparation for `v0.13.0`, leaving only the repository owner's creation and push of the printed annotated tag command.
- Included work: reconcile the already integrated and independently verified #187 SDK-free baseline; harden #194 with mandatory pre-send completion validation and a real schema-valid callback; author and validate the v0.13 release record, notes, migration guide, and phase contract; perform #193 archive/payload review; reconcile #61 and included Issues; pass focused, hosted, candidate, provider-preflight, and merged-main pre-tag gates.
- Exclusions: creating, moving, deleting, recreating, or pushing `v0.13.0`; creating a GitHub Release or publishing assets; changing `EngineeringGuardrails.Contracts.*` under #179; rewriting historical release or assessment evidence.
- Completion criteria: all included Issues satisfy prepublication provider state; the real candidate passes its version-owned candidate contract and user-view review; the accepted branch passes hosted checks and is integrated; final clean `main` passes provider preflight and `prepare-ai-context-release.py --version v0.13.0`; the generated tag command is reported without execution.

## Authorization And Delivery

- Owner instruction: `OK，那完成到可以發布 0.13` on 2026-08-12 authorizes implementation, validation, GitHub transport, integration, and pre-tag readiness. Tag creation and hosted publication remain owner actions under the source release policy.
- Work items: [#187](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/187), [#193](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193), [#194](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/194), and coordination [#61](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/61). Issues #191 and #192 are completed included work already integrated by PR #195.
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
| v0.13 candidate and tag handoff | #187, #193, #61 | `ai-context-governance` | `REL013-001` | candidate archive review, hosted PR checks, provider preflight, clean-main preparation |

## Stages And Checkpoints

1. Freeze `main@afd54f63db51d88bb573e758535ae9692f8aa61a`, live Issue/Project state, and the completed #187/#191/#192/#193 implementation evidence. `completed`
2. Require delegated tasks to validate the complete terminal envelope before source-task delivery, then prove it with a real callback. `completed`
3. Reconcile and close #187/#194 when their integration acceptance is satisfied. `completed`
4. Instantiate and validate the exact v0.13 candidate, including notes, one-source upgrade policy, provider reconciliation, and real archive user-view evidence. `completed`
5. Close #193, retain #61 as release coordination, push the branch, pass hosted checks, and merge with the selected topology. `in_progress`
6. On the final clean integrated `main`, pass provider preflight and pre-tag preparation, then hand the printed annotated-tag command to the owner without executing it. `pending`

## Resume Checkpoint

- Last completed action: `python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version v0.13.0` passed at clean commit `ee348d79986279a9696609613855d77f63473fea` with live read-only provider state.
- Current task: `REL013-001`.
- Exact next action: commit this candidate-gate receipt and delegate `bash .ai/scripts/check-all.sh --critical` from the resulting clean immutable commit using one schema-valid terminal callback.
- Validation already available: PR #195 passed five hosted checks; `ASM-20260811-002` found all #187 findings addressed; `ASM-20260811-006` found no new #193 blocking finding but correctly deferred the real candidate review.
- Blockers: none at the candidate-review boundary. Tag creation and publication are intentionally excluded owner actions.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | workflow bootstrap | `fed4f2eaa42851fd8a9151586fbdc0c1c86332c7` | local | `2026-08-12T07:20:06+08:00` | Complete #194 hardening and exact v0.13 pre-tag readiness in one release-boundary delivery | Implement `VAL005-002`, then author the candidate |
| 2 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | validated #194 checkpoint | `14911780b0b78364ba454c9999e237ed9038f5a9` | local callback regression | `2026-08-12T07:31:00+08:00` | Pin the pre-send contract before the real source-task callback | Reconcile #194 and continue `REL013-001` |
| 3 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | candidate retry authorization | `5ee9b2f5c6307795dd75627992e683144d56f391` | local real candidate | `2026-08-12T07:54:30+08:00` | Preserve attempts 1/2 and authorize the bounded writable-output retry | Await #193 owner read-back of the passing candidate |
| 4 | `codex/2026-08-12-v0-13-release-readiness` | `main@afd54f63db51d88bb573e758535ae9692f8aa61a` | candidate provider gate | `ee348d79986279a9696609613855d77f63473fea` | live read-only provider reconciliation | `2026-08-12T08:10:31+08:00` | Prove every included Issue and Project field satisfies candidate policy | Commit receipt, then delegate the critical gate |
