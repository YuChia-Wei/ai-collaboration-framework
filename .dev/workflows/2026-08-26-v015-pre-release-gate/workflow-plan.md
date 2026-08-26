# v0.15 Pre-Release Gate And Closeout

## Workflow Metadata

- `workflow_id`: `2026-08-26-v015-pre-release-gate`
- `plan_id`: `development-plan-2026-08-26-v015-pre-release-gate`
- `owner_skill`: `ai-context-governance`
- `coordinator_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-26-v015-pre-release-gate`
- `base_branch`: `main`
- `base_sha`: `78bfde42066e5a2d78a91969e299965f296fab17`
- `status`: `pre-release-validation-preparation`
- `created_at`: `2026-08-26T22:57:15+08:00`
- `updated_at`: `2026-08-27T07:33:23+08:00`
- `workflow_locator`: `.dev/workflows/2026-08-26-v015-pre-release-gate/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-26-v015-pre-release-gate`
- `work_items`: `GitHub Issues #250, #252, and #254`

## Objective

Prove that integrated main has the technical and governance prerequisites for a separate v0.15 release workflow and owner release decision. This workflow does not create a v0.15 tag, GitHub Release, publication record, asset upload, package publication, Project-field mutation, release option, installer, registry entry, CLI action, or external-repository change.

## Verified Entry State

- The isolated worktree started from fetched `origin/main@78bfde42066e5a2d78a91969e299965f296fab17`; the management checkout is separate and remains untouched.
- PR #255, PR #256, and PR #257 are merged, and their integrated subjects are ancestors of the verified base. PR #257's head tree is byte-identical to the merge commit tree.
- #249, #251, and #253 are closed; #250, #252, and #254 remain open at workflow entry.
- Prior branch-head lane and audit records are discovery inputs only. Every record is classified against this workflow's frozen subject before reuse.
- No formal `.dev/releases/v0.15.0` record exists or will be created by this workflow. Candidate output is synthetic and confined to declared ignored validation roots.

## Scope And Authorization

Authorized work includes tracked workflow and closeout artifacts, necessary in-scope repairs, focused validation, clean-commit long-running delegated validation, fresh independent exact-head audit, branch push, pull request, required hosted checks and review, merge after admission, integrated-main read-back, and Issue #250/#252/#254 closure after terminal gates.

Explicitly excluded are Project fields, Target release, Published in, v0.15 options, tags, Releases, asset upload, publication, registry, installer, CLI, external repositories, toolchain identity, and every mutation to v0.14.0-or-earlier public tags, releases, assets, checksums, routes, receipts, package metadata, or published bytes.

The owner explicitly requires Issues #250/#252/#254 to close while their Project fields remain unchanged. This is a task-specific owner decision that overrides the normal Project-`Done` synchronization step; it does not authorize any Project mutation. The provider state and this exception must be read back and reported at closeout.

## Acceptance Strategy

The authoritative acceptance ledger is `acceptance-map.yaml`, with the human projection in `acceptance-mapping.md`. Evidence classifications are limited to `executed`, `reused-with-proof`, `blocked`, `deferred`, and `not-applicable`. Unknown dependency or authority state fails closed. Synthetic, mock, fixture, and unit evidence cannot satisfy actual-upgrade acceptance.

Tracked mutation and focused validation finish before freeze. After freeze, read-only long validation and audit write only beneath the compact repository-admissible ignored root `.dev/ai-context/local/validation/v15/`. Required exact-head audit and provider admission are always fresh. Reused evidence requires an explicit content, dependency, command, profile, environment, and authority match.

## Stages

### Stage 1 - Integrated-Scope And Immutability Audit

- Verify #249/#250/#251/#252/#253 integration and absence of later regression.
- Bind the four public v0.15 candidate forms and all identity surfaces.
- Prove v0.14.0-and-earlier provider and tracked immutable parity without mutation.
- Reconcile the earlier #250/#252 workflow's source-stage state without projecting external evidence.

### Stage 2 - Focused Validation And Freeze

- Run workflow, source, identity, archive, lane, route, entrypoint, and diff checks.
- Record graph freshness, acceptance-to-evidence mappings, failure fingerprints, retry history, and explicit non-source-change determination.
- Commit all anticipated tracked closeout metadata, then freeze a clean immutable subject.

### Stage 3 - Owner-Deferred Rehearsal And Exact-Head Audit

- Validate an agent execution packet, exclusive tracked-writer snapshot lease, acceptance ledger, and graph record.
- Record fast, medium, trusted Windows/Linux actual-upgrade, and performance reruns as `deferred-with-owner`; retain prior results as historical integrated evidence only.
- Obtain a separate fresh read-only independent audit of the exact frozen head. Any tracked mutation invalidates this audit.

### Stage 4 - Provider Admission And Merge

- Push the dedicated branch and create one pull request.
- Require all repository-declared hosted contexts on the admitted head and a fresh exact-head review.
- Merge without bypass only after every local, delegated, audit, review, and hosted admission gate passes.
- Read back the merge commit, current main, PR state, and provider evidence.

### Stage 5 - Integrated-Main Finalization And Issue Closeout

- Reclassify branch-head evidence against the merge commit and obtain a fresh integrated-main exact-head audit when the merge identity changes.
- Close and read back Issues #250, #252, and #254 only after terminal contracts are satisfied.
- Do not modify Project fields. Report the unchanged fields and every unperformed release or publication action.

## Validation And Retry Contract

- Fast lane budget: 90 seconds. Medium lane budget: 240 seconds. Long lane budget: 1200 seconds.
- Release, full-matrix, or any observed/expected run of at least 120 seconds executes only from a clean immutable commit through the delegated read-only packet.
- One failure fingerprint may be retried only after a material state change and within its declared budget. Attempt three or later needs new owner or workflow authorization unless the attempt number was already authorized by an earlier completed workflow and is only being reused with proof.
- Required Windows and Linux actual execution cannot be substituted, downgraded, or satisfied by synthetic output.

### Owner Metadata-Only Execution Decision

On 2026-08-27 the owner classified this delivery as release-preparation metadata only and directed the workflow to finish without rerunning fast, medium, long, or full-matrix package tests. The prior branch-head fast, medium, trusted Windows actual-upgrade, trusted Linux actual-upgrade, and same-host performance records remain historical integrated evidence for Issues #250/#251/#252; they are not represented as execution or canonical `reused-with-proof` evidence for this metadata head.

The disposition record must establish that this branch changes only `.dev/workflows/**`, that the integrated PR #257 tree already contains the runtime and test bytes exercised by those records, and that no lane implementation, package implementation, identity registry, source release, legacy published artifact, route, receipt, or provider object changed. Because the repository has no authoritative input-closure resolver for the v0.15 lanes and the retained performance head has later runtime drift, those package and performance gates are `deferred-with-owner` for this head rather than `reused-with-proof`. Workflow validators, exact-head independent audit, hosted required contexts, PR review, merge read-back, and Issue read-back remain fresh because they are identity- or provider-sensitive.

### Fast-Lane Retry Record

- Attempt 1 on `c43c619cde194d4421a6d3fce43fb4d8da418759` failed before candidate construction because the sandbox denied Git for Windows signal-pipe creation (`WinError 5`; fingerprint `ccba5f15...81133`).
- Attempt 2 on the same subject ran outside that sandbox and failed before candidate construction because the nested output path made Git reject an oversized `$GIT_DIR` (`2f6411cf...e14c9`).
- A separate short-path local-clone diagnostic succeeded. The owner then explicitly authorized the material state change and fast-lane attempt 3.
- Attempt 3 on `04762d1afc8cccd2fa502f444584fc5f1c5f8d1a` failed before terminal admission because `.dev/ai-context/local/v15-gate/` did not retain the repository-required `validation` path segment. No candidate work ran. The corrected compact root is `.dev/ai-context/local/validation/v15/`.
- The owner subsequently directed metadata-only completion without additional package-lane execution. There is no attempt 4; the three failed invocations remain retained and non-passing while prior successful package evidence remains historical integrated evidence without a current-head reuse claim.
- All earlier failed invocations and terminals remain retained and non-passing.

## Completion Meaning

Completion means `READY_FOR_OWNER_V0_15_RELEASE_WORKFLOW_DECISION`. It does not mean released, tagged, published, allocated to a Project release field, or uploaded anywhere.
