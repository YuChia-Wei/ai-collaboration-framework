# Compact Effective-Rule Packet Filenames With Deterministic Base32 Keys

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-30-effective-rule-packet-base32`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-30-effective-rule-packet-base32`
- `base_branch`: `main@f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `validation`
- `artifact_root`: `.dev/workflows/2026-08-30-effective-rule-packet-base32`
- `created_at`: `2026-08-30T18:35:25+08:00`
- `updated_at`: `2026-08-30T19:27:39+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `work_item`: `https://github.com/YuChia-Wei/ai-collaboration-framework/issues/265`

## Objective And Scope

- Problem statement: full `ROUTE-<SHA256>.yaml` packet filenames consume 114 repository-relative characters and can block downstream Windows operations under legacy path limits.
- Authorized remediation scope: implement the owner-approved `route-base32-60-v1` persisted layout, legacy compatibility, path-budget preflight, migration safety, tests, durable local commits, and fresh exact-head independent audit.
- Exclusions: numeric filenames, a second authoritative index, weakened full identities, silent package-apply migration, push, pull request, merge, Issue or Project terminal mutation, tag, Release, and publication.
- Completion criteria: every Issue #265 acceptance is backed by direct evidence; focused validation and workflow gates pass; a clean immutable commit receives a fresh independent read-only audit.

## Workflow Value And Delivery

- Mode: workflow, because the change alters canonical target-effective state, persisted routing paths, compatibility behavior, and migration/recovery truth across `.ai` and `.dev`.
- Unique state: the Issue cannot by itself preserve migration-stage progress, validation outcomes, exact-head audit binding, and truthful recovery state.
- Delivery cohesion: one Issue, branch, persisted-layout boundary, validation set, reviewer boundary, and atomic rollback unit.
- Integration gate: pull request required if later authorized; none is currently authorized.
- Proposed topology: linear, because this is one cohesive compatibility delivery and no external checkpoint boundary currently needs a merge node.

## Acceptance-To-Evidence Human Projection

The machine-readable authority is `acceptance-ledger.yaml`.

| Acceptance | Status | Required evidence |
| --- | --- | --- |
| GOV016-A1 | verified | exact 12-character lowercase RFC 4648 Base32 derivation and 58-character relative path |
| GOV016-A2 | verified | full route and packet identities retained; state remains the single mapping authority |
| GOV016-A3 | verified | complete-set collision and path mismatch rejection before writes |
| GOV016-A4 | verified | privacy-safe legacy-path-budget preflight before mutation |
| GOV016-A5 | verified | legacy reads plus explicit, rollback-safe compact regeneration without silent package apply |
| GOV016-A6 | verified | mixed/orphan/malformed final layouts fail closed |
| GOV016-A7 | verified | focused effective-rule, provenance, package, upgrade, workflow, and AI-context validation |
| GOV016-A8 | pending | clean immutable commit and fresh independent exact-head audit |

## Stages And Checkpoints

1. Implement compact identity/path helpers, schema contract, preflight, compatibility, and regression tests.
2. Validate focused behavior and update acceptance evidence.
3. Create a policy-valid local commit and freeze the exact subject.
4. Run fresh independent read-only post-remediation audit.
5. Reconcile findings and leave a truthful local handoff without external mutation.

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| design to implementation | approved | Owner decision in this conversation and live Issue #265 | none within local scope |

## Test And Compliance Selection

- Selected levels: unit and integration through repository-owned focused commands.
- Long-running aggregate execution: only after clean immutable commit under the external-task contract if selected by repository policy.
- Spec compliance: not selected; outcome `not-applicable` unless later activated by explicit target evidence.
- Independent verification: required through `ai-context-auditor` after the implementation commit is clean and immutable.

## Resume Checkpoint

- Last completed action: fixed-head audit attempt 1 was blocked by sandbox temp access; attempt 2 passed 113 package-apply tests but found that init/finalize preflight occurred after authority mutation. Governance added a pure preflight before any destination mutation, and 32 effective-rule plus 10 lifecycle tests now pass.
- Current task: `implement-compact-packet-paths`.
- Exact next action: run fresh local validators, commit the audit remediation, then repeat immutable-head package validation and independent audit without reusing the superseded result.
- Validation already completed: post-remediation 32 effective-rule tests (2 skipped) and 10 semantic lifecycle tests passed. The earlier 113-test package result and audit remain evidence for superseded commit `5a885cb7`, not the new subject.
- Git state: dedicated local branch with authorized post-audit remediation pending commit.
- Branch history and checkpoint handoffs: implementation checkpoint `5a885cb748f8c1c96afd67e66fa85a4c4f698e39`; fixed-head audit rejected it for preflight ordering.
- Blockers or unresolved decisions: none.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-30-effective-rule-packet-base32` | `main@f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af` | implementation checkpoint rejected by fixed-head audit | `5a885cb748f8c1c96afd67e66fa85a4c4f698e39` | local only | `2026-08-30T19:18:25+08:00` | audit found preflight occurred after authority mutation | commit audit remediation, then re-freeze and re-audit |
