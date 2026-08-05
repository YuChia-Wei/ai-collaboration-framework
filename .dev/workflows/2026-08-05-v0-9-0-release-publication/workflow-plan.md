# v0.9.0 AI Context Release Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-05-v0-9-0-release-publication`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-05-v0-9-0-release-publication-cont-03`
- `base_branch`: `main`
- `branch_segment`: `3`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-08-05-v0-9-0-release-publication`
- `created_at`: `2026-08-05T22:26:56+08:00`
- `updated_at`: `2026-08-06T07:05:42+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: v0.9.0 has eight completed canonical outcomes, stable bilingual bundled-provider navigation, deterministic candidate packages, clean-install and exact-v0.8.0 upgrade evidence, and a green final-code critical gate. Independent candidate verification, integration, the owner-controlled tag, hosted publication, and terminal reconciliation remain separate lifecycle stages. The packaged Issue #128 correction is disclosed without a local backlog backfill.
- Authorized release scope: retain the provider test projects under `tools/` as source-only verification; implement CTX-004/#98 against the stable provider landing page with English-first authoring and Luna-max Traditional Chinese translation; record the online #95/#128 relationship; create and validate the v0.9.0 governed candidate; obtain independent verification; integrate through a pull request; prepare the owner-owned tag command; then validate hosted publication and finalize the registry.
- Authorization source: owner approval in the active Codex task on 2026-08-05, including explicit CTX-004 allocation, bilingual README implementation, sub-agent use, and v0.9.0 publication after prerequisites complete.
- Work-item bindings: GitHub Issue #98 for CTX-004; Issue #128 remains online-only and must not receive a local backlog item; Issues #86, #99, #104-#107, and #118 remain the pre-existing canonical release set.
- Exclusions: no Architecture Kit cutover, no materialize-to-tools mode, no CLI/Copilot/product-source implementation, no VAL-002 profile or changed-path redesign, no local backlog backfill for Issue #128, no WSL runtime installation, and no autonomous creation/movement/deletion of the immutable release tag.
- Completion criteria: provider/test placement is coherent and validated; CTX-004 is implemented with bilingual parity and included exactly once; #128 is disclosed as an online-only packaged correction; the exact v0.9.0 candidate passes local, package, clean-install, supported-upgrade, independent, hosted, merged-main, tag, publication, asset, Project, and finalization gates; the user creates the annotated tag.

## Artifact Contract

- Baseline assessments: `.dev/assessments/ASM-20260804-001/assessment.yaml`, `.dev/assessments/ASM-20260805-003/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-05-v0-9-0-release-publication/reports/remediation-report.md`
- Verification assessment: `.dev/assessments/ASM-20260805-004/assessment.yaml` (`healthy-with-followups`; no active finding)
- Tasks: `.dev/workflows/2026-08-05-v0-9-0-release-publication/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260804-001#AIC-010` | LOW | `ai-context-governance` | resolve in v0.9.0 through stable provider navigation | `REL090-001` | bilingual structure, link, provider, and context validation |
| `ASM-20260805-003#VCR-001` | evidence | `ai-context-governance` | disclose merged packaged timing behavior without duplicating EVAL-002 | `REL090-001` | release notes, package parity, current critical gate |
| Bundled provider test-location coherence | owner-raised | `ai-context-governance` | decide from provider/package/project evidence and move only if ownership is coherent | `REL090-001` | project-reference, dependency, package, and .NET test gates |

## Stages And Checkpoints

1. `REL090-001`: implement English CTX-004, obtain Luna-max zh-TW parity, retain source-only tests under `tools/`, and reconcile #95/#128 online traceability.
2. `REL090-001`: create the eight-item governed candidate, author compatibility and migration guidance, build and validate immutable package candidates, and prove clean install plus v0.8.0 upgrade.
3. `REL090-001`: obtain independent verification, integrate one release PR with an explicit merge commit, then create a continuation branch from updated `main` for merged-main gates and the owner-owned annotated-tag handoff.
4. `REL090-001`: after the owner creates and pushes the annotated tag, validate publication and complete hosted closeout from a fresh continuation branch based on updated `main`.

## Validation Policy

- Routine source gate: `bash .ai/scripts/check-all.sh --critical` through Git for Windows Bash on this host; WSL is not a valid runtime on the current machine.
- Candidate and later release phases must use `.dev/releases/v0.9.0/release-phase-checks.yaml` verbatim.
- Unit/integration coverage: provider evaluator suites, analyzer/runtime/building-blocks .NET tests, package/apply/release-state tests, and clean-install plus supported-upgrade fixtures.
- Independent verification: `ai-context-auditor` post-remediation assessment on the release workflow branch before integration.
- Spec compliance: not selected; `not-applicable`.
- Integration gate: pull request with required hosted checks.
- Topology: merge commit because the release, sub-agent, approval, package, tag handoff, and hosted publication lifecycle form one durable boundary.

## Resume Checkpoint

- Last completed action: immutable tag `v0.9.0`, successful hosted publication run `31027306074`, four public assets, checksums, archive parity, published registry, and eight-item Project publication fields were read back and reconciled. The owner accepted the documented HIGH pre-tag ordering deviation and directed completion without tag mutation.
- Current task: `REL090-001` completed.
- Exact next action: none for v0.9.0; merge the terminal closeout PR and preserve the immutable tag and Release.
- Validation already completed: current-main critical gate passed before preparation; final-code critical passed 49/49; deterministic packages, fresh clean install, and exact v0.8.0 upgrade passed; `ASM-20260805-004` had no active candidate finding; PR #130 and PR #131 each passed five hosted checks; the merged-main pre-tag gate passed; tag and publication phases passed; public ZIP/tar matched sidecars and passed parity; all eight Project items read published in v0.9.0. The owner-waived duplicate post-rewrite fixture run remains explicitly not executed.
- Git state: terminal closeout branch created from clean `main@e4965cb`.
- Branch history and checkpoint handoffs: segments 1 and 2 merged through PR #130 and PR #131; segment 3 owns terminal registry and workflow closeout.
- Blockers or unresolved decisions: none. The accepted procedural deviation remains durable evidence, not a passing check.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-v0-9-0-release-publication` | `main@5d9af93` | merged checkpoint | `c14a3260cba7d0a9e2b67b73df9e221280d2d2ef` | PR #130 / `main` | `2026-08-06T00:27:06+08:00` | Cohesive CTX-004, provider-placement, candidate, and publication lifecycle | Completed; do not reuse the merged branch. |
| 2 | `codex/2026-08-05-v0-9-0-release-publication-cont-02` | `main@c14a326` | merged checkpoint | `e4965cb232323affe3339747b0405b79b868cf75` | PR #131 / `main` | `2026-08-06T00:51:20+08:00` | Persist merged-main pre-tag evidence and owner handoff | Completed; its post-gate merge is retained as the accepted sequence deviation. |
| 3 | `codex/2026-08-05-v0-9-0-release-publication-cont-03` | `main@e4965cb` | terminal closeout | pending closeout PR | hosted release and `main` | `2026-08-06T07:05:42+08:00` | Reconcile immutable publication, registry, Project fields, and workflow closure | Merge the terminal closeout PR; no further v0.9.0 action remains. |
