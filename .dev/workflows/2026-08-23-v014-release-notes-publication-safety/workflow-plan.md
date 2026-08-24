# v0.14.0 Release Notes Publication-Safety Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-23-v014-release-notes-publication-safety`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-23-v014-release-notes-publication-safety-delivery`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `in_progress`
- `current_phase`: `delivery-continuation-preparation`
- `artifact_root`: `.dev/workflows/2026-08-23-v014-release-notes-publication-safety`
- `created_at`: `2026-08-23T23:09:27+08:00`
- `updated_at`: `2026-08-24T08:14:48+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: GitHub Issue #241 records that the published v0.14.0 body and its authored source retain candidate, pending-publication, transient execution-history, and open/unmerged-state narration.
- Authorized remediation scope: make `.dev/releases/v0.14.0/release-notes.md` consumer-facing; strengthen the effective v0.13.0+ tag-triggered renderer boundary; add focused GWT regression tests; render and validate the exact hosted body; remediate the directly related v0.14.0 retained-origin route evidence without changing the retained source set or another version's published semantics; make exactly one body-only GitHub Release update from a clean immutable reviewed commit; retain mechanical before/after parity evidence.
- Exclusions after the latest owner continuation: Project mutation beyond required terminal read-back, release allocation, tag mutation, Release recreation or non-body user-controlled mutation, asset mutation, new publication, downstream mutation, package/archive rename, and ID-002 creation. Push, pull request, merge, and Issue #241 terminal close are now separately authorized when their gates pass.
- Completion criteria: source and focused tests pass; a clean immutable commit receives independent read-only review; the hosted body is updated once from exact validated bytes; provider receipts prove every non-body Release, tag, peeled-commit, and asset field is unchanged; workflow evidence remains truthful.

## Governing Contracts

- `.dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md`
- `.dev/standards/WORKFLOW-GATE-POLICY.md`
- `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`
- `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`
- `.dev/TEAM-GIT-FLOW-RULES.MD`
- `.dev/standards/GIT-COMMIT-POLICY.md`
- `.dev/releases/v0.14.0/release-phase-checks.yaml`
- `.github/workflows/publish-release.yml`

## Artifact Contract

- Baseline authority: live GitHub Issue #241 plus live v0.14.0 Release/tag/asset read-back; no standalone assessment is selected.
- Remediation report: `.dev/workflows/2026-08-23-v014-release-notes-publication-safety/reports/remediation-report.md`
- Independent verification: exact-commit read-only reviewer receipt recorded in the remediation report and task result.
- Task: `.dev/workflows/2026-08-23-v014-release-notes-publication-safety/tasks/REL016-001.json`
- Provider evidence: `.dev/workflows/2026-08-23-v014-release-notes-publication-safety/evidence/`

## Finding Triage And GWT Design

| Finding / Scenario | Severity | Given | When | Then | Level | Task |
| --- | --- | --- | --- | --- | --- | --- |
| REL016-F001 absent-publication claim | high | v0.13.0+ notes say an existing body is not a tag, GitHub Release, or publication record | publication rendering validates the notes | fail closed before body output | focused renderer unit | REL016-001 |
| REL016-F002 pending/open state | high | notes describe pending tag/publication/admission or open/unmerged PR state | publication rendering validates the notes | fail closed before body output | focused renderer unit | REL016-001 |
| REL016-F003 transient execution history | high | notes narrate checkpoint SHA, run/job IDs, or failed-attempt chronology | publication rendering validates the notes | fail closed before body output | focused renderer unit | REL016-001 |
| REL016-F004 durable status counterexamples | high | notes contain deprecated, withdrawn, support limitation, and concise validation outcome content | publication rendering validates the notes | remain valid and render unchanged | focused renderer unit | REL016-001 |
| REL016-F005 deterministic hosted body | high | corrected v0.14.0 source notes and immutable tag commit are selected | renderer runs twice and repository release-state validation consumes the body | outputs are byte-identical and publication-safe | renderer plus source-release validation | REL016-001 |
| REL016-F006 retained-origin evidence drift | high | the schema-1.0 route inventory points to the superseded route archive and validator digest while the unchanged hosted v0.14.0 ZIP validates all three declared origins | schema-1.1/v2 evidence is generated from the exact hosted ZIP bytes | all existing origins resolve direct without changing `automatic_upgrade_sources` | direct-edge, resolver, and publication-phase validation | REL016-002 |

## Execution Stages And Checkpoints

1. Freeze live Issue, hosted Release, tag, peeled commit, and asset baseline.
2. Implement bounded notes, renderer contract, and GWT tests.
3. Run focused renderer/release-state tests and proportionate source-governance checks.
4. Commit a clean immutable head and obtain independent read-only exact-head review.
5. Bind schema-1.1/v2 retained-origin evidence to the exact existing hosted ZIP while preserving the three-source set, then validate the publication phase.
6. Re-read provider state, stop on drift, otherwise execute exactly one body-only update and immediately compare all fields.
7. Finalize task/report receipts, obtain fresh exact-head review, then perform the authorized push, pull request, gated merge, and Issue #241 terminal close with provider read-back.

## Provider Mutation Guard

- The update payload must contain exactly one key: `body`.
- The body bytes must equal the deterministic rendered evidence file.
- Release numeric ID, node/name/tag/target, peeled commit, draft/prerelease flags, publication timestamp, and the complete asset identity/state/size/digest/download-URL set must be captured immediately before mutation.
- Any drift, incomplete validation, unclean head, missing credential, or uncertain write outcome stops the mutation; no retry is authorized.

## Resume Checkpoint

- Last completed action: Provider receipts were committed at clean evidence head `d988359acd6a79fce71ee2949996828fa36e4768`, independently reviewed with no findings, and pushed without rewriting any reviewed or provider-bound SHA. Segment 2 now contains a squash of that exact evidence tree on `main@6f690440d59f5569e19c3e2ceb219f964c2fa6f6`.
- Current task: `REL016-001`
- Exact next action: commit the delivery continuation with compliant metadata, prove source and receipt byte equivalence to `d988359acd6a79fce71ee2949996828fa36e4768`, validate the exact head, and obtain fresh independent review. PR creation and merge remain gated by terminal-close handling for Issue #241, whose Project status is currently `Inbox`.
- Validation already completed: renderer GWT 25/25, route GWT 31/31, and release-state GWT 37/37 passed again on segment 2 outside the sandbox after the sandbox Temp ACL block was preserved; source and receipt paths are byte-equivalent to `d988359acd6a79fce71ee2949996828fa36e4768`; AI-context and workflow checks passed; deterministic hosted body SHA-256 remains `07b17d1f47e5ee1489b2f4049da89f52e4acf50efedbf549e39a25582603737e`; publication and finalization phases passed again at tagged commit `412bb14a16fe75ee65a020b16680def0acc0ff1b`.
- Git state: bootstrap `b12747531feb2249217935fbe8549e0a7671dc25`, initial implementation `d29d75e1f5bd7d22635dce3a95c6e730081264b5`, migration-input repair `b3a4d200706c099065274099685b1dcc2bd25acf`, heading-adjacent repair `855e101d61fdf38682a348400250b89e5dbe4dcf`, blocked receipt `d102fa534a86affe1ab7296219da295150854e0b`, migration-heading repair `915959a7f9f9aacac646276373e2764fc6016ed6`, final renderer receipt `a3a77a3a15156046e93acfe8e190aa4a884ccd08`, and test-count receipt `4086a6d024f7c683ab493fdb33cdf1592abc9620` are committed locally; no unrelated tracked changes observed.
- Provider correction completed exactly once under the owner's later 2026-08-24 authorization. No further Release mutation is authorized.
- Branch history and checkpoint handoffs: segment 1 is preserved at pushed clean head `d988359acd6a79fce71ee2949996828fa36e4768`; segment 2 is the main-based compliant delivery continuation. The latest owner continuation authorizes push, PR, merge, and Issue close after the remaining gates pass.
- Blockers or unresolved decisions: Issue #241 is currently open with Project #3 status `Inbox`, while terminal closeout requires post-integration `Done`. Direct Project mutation remains excluded and recent Issue #239 being `Done` does not prove automation for #241. Do not merge until automatic disposition is proven or the owner authorizes a bounded Project status correction. Package/archive naming remains explicitly deferred and excluded.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-23-v014-release-notes-publication-safety` | `main@6f690440d59f5569e19c3e2ceb219f964c2fa6f6` | provider/evidence checkpoint | `d988359acd6a79fce71ee2949996828fa36e4768` | `origin/codex/2026-08-23-v014-release-notes-publication-safety` | `2026-08-24T08:08:00+08:00` | Preserve reviewed and provider-bound SHAs without rewrite; commit receipts and the non-rewriting delivery decision. | Continue from current `main` on segment 2 and squash the final evidence tree into compliant PR history. |
| 2 | `codex/2026-08-23-v014-release-notes-publication-safety-delivery` | `main@6f690440d59f5569e19c3e2ceb219f964c2fa6f6` | squashed delivery continuation | pending | local; target `origin` after exact-head validation | `2026-08-24T08:12:08+08:00` | Create policy-compliant PR history without invalidating exact-SHA reviews or the provider receipt. | Commit, prove bounded tree equivalence, validate, obtain fresh review, then resolve the Project terminal-close boundary before PR merge. |
