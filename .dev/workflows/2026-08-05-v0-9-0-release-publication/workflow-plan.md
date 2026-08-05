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
- `branch`: `codex/2026-08-05-v0-9-0-release-publication`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `candidate-preparation`
- `artifact_root`: `.dev/workflows/2026-08-05-v0-9-0-release-publication`
- `created_at`: `2026-08-05T22:26:56+08:00`
- `updated_at`: `2026-08-05T22:26:56+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: v0.9.0 has seven completed canonical outcomes and a green current-main critical gate, but it lacks the governed candidate, stable root navigation for the bundled provider, candidate package and migration evidence, and publication lifecycle records. The packaged Issue #128 correction also needs explicit release-note visibility without a local backlog backfill.
- Authorized release scope: retain the provider test projects under `tools/` as source-only verification; implement CTX-004/#98 against the stable provider landing page with English-first authoring and Luna-max Traditional Chinese translation; record the online #95/#128 relationship; create and validate the v0.9.0 governed candidate; obtain independent verification; integrate through a pull request; prepare the owner-owned tag command; then validate hosted publication and finalize the registry.
- Authorization source: owner approval in the active Codex task on 2026-08-05, including explicit CTX-004 allocation, bilingual README implementation, sub-agent use, and v0.9.0 publication after prerequisites complete.
- Work-item bindings: GitHub Issue #98 for CTX-004; Issue #128 remains online-only and must not receive a local backlog item; Issues #86, #99, #104-#107, and #118 remain the pre-existing canonical release set.
- Exclusions: no Architecture Kit cutover, no materialize-to-tools mode, no CLI/Copilot/product-source implementation, no VAL-002 profile or changed-path redesign, no local backlog backfill for Issue #128, no WSL runtime installation, and no autonomous creation/movement/deletion of the immutable release tag.
- Completion criteria: provider/test placement is coherent and validated; CTX-004 is implemented with bilingual parity and included exactly once; #128 is disclosed as an online-only packaged correction; the exact v0.9.0 candidate passes local, package, clean-install, supported-upgrade, independent, hosted, merged-main, tag, publication, asset, Project, and finalization gates; the user creates the annotated tag.

## Artifact Contract

- Baseline assessments: `.dev/assessments/ASM-20260804-001/assessment.yaml`, `.dev/assessments/ASM-20260805-003/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-05-v0-9-0-release-publication/reports/remediation-report.md`
- Verification assessment: pending allocation by `ai-context-auditor`
- Tasks: `.dev/workflows/2026-08-05-v0-9-0-release-publication/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260804-001#AIC-010` | LOW | `ai-context-governance` | resolve in v0.9.0 through stable provider navigation | `REL090-001` | bilingual structure, link, provider, and context validation |
| `ASM-20260805-003#VCR-001` | evidence | `ai-context-governance` | disclose merged packaged timing behavior without duplicating EVAL-002 | `REL090-002` | release notes, package parity, current critical gate |
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

- Last completed action: owner authorized the bounded release workflow; `main@5d9af93` passed 49/49 critical checks with zero failures and zero environment blocks.
- Current task: `REL090-001`
- Exact next action: complete the bilingual CTX-004 change, record the online #95/#128 relationship, and instantiate the release candidate contract.
- Validation already completed: current-main critical gate passed in 950 seconds; attachment parity confirmed against `ASM-20260804-001`; all seven prior Project items read back Done/v0.9.0/Not yet published.
- Git state: dedicated workflow branch created from clean `main@5d9af93`.
- Branch history and checkpoint handoffs: none.
- Blockers or unresolved decisions: publication tag remains user-owned.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-v0-9-0-release-publication` | `main@5d9af93` | active | — | local | `2026-08-05T22:26:56+08:00` | Cohesive CTX-004, provider-placement, candidate, and publication lifecycle | Continue `REL090-001` on this branch. |
| 2 | pending continuation branch | updated `main` after candidate PR | planned checkpoint continuation | — | pull-request merged main | — | Merged candidate is a checkpoint, not workflow completion | Create `codex/2026-08-05-v0-9-0-release-publication-cont-02` from updated `main`; run pre-tag gates and prepare the owner handoff. |
| 3 | pending hosted-closeout continuation branch | updated `main` after owner tag/publication | planned post-publication continuation | — | hosted release and main | — | Publication evidence and registries must be reconciled without reusing a merged segment | Create a fresh continuation branch from updated `main`; validate hosted artifacts, reconcile publication fields, and finalize through a pull request. |
