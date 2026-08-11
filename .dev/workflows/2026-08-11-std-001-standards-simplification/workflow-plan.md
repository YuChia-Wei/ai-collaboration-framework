# v0.13 Standards Simplification Round 2 And Round 3

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-11-std-001-standards-simplification`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-11-std-001-pkg-navigation-closure`
- `base_branch`: `main`
- `branch_segment`: `4`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-standards-simplification`
- `created_at`: `2026-08-11T13:31:10+08:00`
- `updated_at`: `2026-08-12T01:14:01+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #61 requires a v0.13 Round 2/3 simplification baseline that measures code-review reference loading, establishes canonical governance terminology ownership, and reviews the actual package candidate from a downstream user's perspective before any broad standards rewrite.
- Authorized scope: Execute #61's approved investigation, decision evidence, and implementation preparation on one cohesive branch. Produce R2/R3 source, routing, terminology, validator-impact, and package-view inventories; preserve doctrine, checklists, severity, and output contracts; define bounded delivery scopes from stable findings.
- Exclusions: Round 1/#86 is completed historical evidence; #167 release lifecycle work is a related terminology source, not reopened scope; OBS-001 remains a consumer; CAP-001's no-dedicated-terminology-skill decision is retained; no unreviewed canonical standards or validator rewrite, successor-Issue implementation, v0.13 tag, Release, or publication is authorized by workflow bootstrap.
- Completion criteria for the approved preparation phase: `ASM-20260811-003` is final with stable R2/R3/package findings; every candidate move/delete has a proposed owner, replacement entry, compatibility, migration, and equivalence test; a governance decision ledger partitions changes into bounded delivery scopes and identifies any required successor Issues or owner decisions.

## Authorization And Delivery

- Work item: [GitHub Issue #61](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/61), read as OPEN on 2026-08-11.
- Project read-back: Project #3 records `Status=Planned`, `Priority=P1 High`, `Owner review=Approved`, `Target release=v0.13.0`, and `Published in=Not yet published`.
- Current owner instruction: local implementations of Issues [#191](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/191), [#192](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/192), and [#193](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193) are accepted for repository integration. On 2026-08-11 the owner explicitly requested merge to `main`, followed by evidence-based branch reconciliation and deletion of branches with no unique delivery. Issue closure, Project mutation, v0.13 tag, Release, and publication remain separate decisions.
- Long-running validation instruction: on 2026-08-12 the owner required long-running repository validation to execute only after local mutations and focused checks are complete, in a low-cost external task that reports once without polling by the primary conversation. After the first hosted run exposed a missing source-task callback contract, the owner authorized a schema-bound dispatch/completion format, one callback or parent event wait, focused cross-task regression, push, and merge after all hosted checks pass. [Issue #194](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/194) is the online implementation authority; aggregate-runner parallelization remains prohibited until dependency and artifact-isolation safety is proven.
- Composite integration-gate authorization: after reviewing the 51/54 aggregate receipt and the three exact timed-out commands passing independently, the owner explicitly accepted the combined evidence as sufficient for this integration. The aggregate receipt remains recorded as timed out rather than relabeled 54/54. The owner also deferred v0.13 packaging and authorized merge plus closure only for Issues whose own acceptance conditions are satisfied after integration read-back.
- Upgrade-test direction: active upgrade testing begins at v0.6.0; routine later releases keep only the immediate-predecessor route; every breaking release establishes a predecessor-only migration checkpoint so historical Cartesian matrices do not become a standing gate.
- Delivery cohesion: R2, R3, and package-candidate review share branch, reviewers, validation, v0.13 decision gate, and rollback; one workflow coordinates them without forcing unrelated authority changes into one delivery.
- Planned integration: one pull request from `codex/2026-08-11-std-001-pkg-navigation-closure` to `main`, using a merge commit because the grouped #191/#192/#193 rollback units, four independent assessments, and this incomplete-workflow handoff boundary carry durable information. Direct main mutation remains forbidden; hosted checks and PR review must pass first.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-003/assessment.yaml`
- Decision ledger: `.dev/workflows/2026-08-11-std-001-standards-simplification/reports/decision-ledger.md`
- Verification assessments: `ASM-20260811-004`, `ASM-20260811-005`, and `ASM-20260811-006` independently fix and reconcile the three successor implementation subjects.
- Tasks: `.dev/workflows/2026-08-11-std-001-standards-simplification/tasks/`

## Workstream Triage

| Workstream | Authority | Owner | Disposition | Task | Required evidence |
| --- | --- | --- | --- | --- | --- |
| R2 code-review progressive disclosure | #61 owner decision | `ai-context-auditor` -> `ai-context-governance` | measure current loading and propose file-type/finding routing | `STD001-001` | entry graph, reference set, checklist/severity/output-contract preservation |
| R3 governance terminology | #61 owner decision | `ai-context-auditor` -> `ai-context-governance` | inventory definitions and propose one canonical owner plus contextual links | `STD001-002` | term/definition/consumer matrix, conflict and duplication evidence, validator/migration impact |
| Package candidate user view | #61 owner decision | `ai-context-governance` | inspect actual payload and record delivery partitions | `STD001-003` | package projection, downstream navigation review, decision ledger, successor-Issue boundaries |
| Long-running validation execution | #194 owner instruction | `ai-context-governance` | require fixed-commit external execution with no primary-conversation polling | `VAL005-001` | canonical policy, machine-readable contract, focused tests, external final report |

## Stages And Checkpoints

1. Freeze merged `main`, Issue/Project authority, workflow branch, and draft assessment. `completed`
2. Complete R2 reference-loading inventory and doctrine-equivalence baseline. `completed`
3. Complete R3 terminology ownership and definition-placement inventory. `completed`
4. Build and review the controlled current-tree package projection, then finalize the decision ledger. `completed-with-v0.13-fail-closed-limitation`
5. Present bounded delivery scopes for owner confirmation and create the approved successor Issues. `completed`
6. Coordinate separately authorized successor deliveries and the final governed v0.13 package-candidate review. `completed-with-v0.13-owner-deferral`
7. Codify #194, finish focused validation, and adopt schema-bound non-polling external execution for future long-running gates. `completed`

## Resume Checkpoint

- Last completed action: Pinned commit `1a5fa40378594c3622eaabb7f7bd57a30fcf416b` passed the live schema-only regression in external task `019ff1cb-fd3f-7f92-8c75-eaebda9bc91c` and delivered exactly one schema-valid terminal callback to source task `019fee2e-80d3-72b1-9f34-f368c06126bc`; the dispatch and completion records are retained under `evidence/`.
- Current task: none; all workflow-owned tasks are terminal, with the real v0.13 candidate review explicitly deferred to its owner condition.
- Exact next action: the source owner pushes PR #195, delegates the hosted-check wait without polling this task, and merges only if the final remote head is fully green. Workflow completion does not claim PR integration, Issue closure, a v0.13 candidate, release, or publication.
- Validation already completed: #191 is independently verified by `ASM-20260811-004`; #192 by `ASM-20260811-005`; #193 selected-payload, version, packaging, archive/apply, routing, and aggregate gates passed and `ASM-20260811-006` found no new blocking finding. Integration-gate attempts at `ccca869` preserved the earlier 52/54 regression receipt and the later 51/54 timeout receipt; all three timed-out commands pass independently, `ac54e78` raises only those registry budgets from 30 to 60 seconds, and the owner accepted that composite evidence for this integration. #194 focused capability tests passed 14/14 and deterministic acceptance passed 3/3.
- Git state: current branch contains fix checkpoint `1a5fa40378594c3622eaabb7f7bd57a30fcf416b` plus the containing workflow completion commit; PR #195 remains open and requires a new push so hosted checks evaluate the fixed head.
- Branch history and checkpoint handoffs: integration is authorized but not yet transported. The normal handoff schema can represent only one exact passing `check-all.sh --critical` execution, so it cannot truthfully encode this owner-approved composite evidence. Under the owner's explicit higher-priority instruction, this workflow plan records the transport exception instead of fabricating a 54/54 command receipt. Hosted PR checks remain mandatory external evidence.
- Blockers or unresolved decisions: the critical handoff checkpoint and hosted PR checks must pass before integration. No governed v0.13 release record or real candidate exists yet; #193/#61 closeout, Project state, tag, Release, and publication remain separately gated.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local audit bootstrap | `a77db619fa48d44245845ee9f0e1d275103e1a42` | local | `2026-08-11T13:31:10+08:00` | Begin the owner-approved #61 R2/R3 investigation and preparation scope | Review the final assessment and proposed successor delivery ledger |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local assessment checkpoint | `c001cc34617396bfbde2b8138c7a65f45fc484e0` | local | `2026-08-11T13:45:48+08:00` | Preserve the final baseline assessment, controlled projection review, and decision ledger before owner approval | Record owner approval and successor Issue read-back |
| 2 | `codex/2026-08-11-std-001-r2-review-routing` | `codex/2026-08-11-std-001-standards-simplification@73b12c6` | local verified implementation | `f62f110` | local | `2026-08-11T20:56:40+08:00` | Preserve the completed #191 routing delivery and independent `ASM-20260811-004` evidence without merging its rollback unit | Start #192 from the updated coordination branch; retain #191 for owner review |
| 3 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | local verified implementation | `92e7383` | local | `2026-08-11T21:40:15+08:00` | Preserve the completed #192 governance-term delivery and independent `ASM-20260811-005` evidence without merging its rollback unit | Start #193 from the updated coordination branch; use a validation-only combined view for #191/#192 package closure |
| 4 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `codex/2026-08-11-std-001-combined-validation@b1aacf8` | local verified implementation | `ff80d590`, `cef711a`, `fe969d3` | local | `2026-08-11T22:45:54+08:00` | Preserve selected-payload/component closure, bounded upgrade-test policy, and independent `ASM-20260811-006` evidence without claiming integration | Create the required incomplete-workflow handoff, then open the owner-authorized integration PR to `main` |
| 4 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `main@df7012b6` | owner-approved composite integration transport | `ccca869`, `ac54e78`, `735ed82` | local, PR pending | `2026-08-12T00:22:08+08:00` | Preserve the 51/54 aggregate timeout receipt, three independent passing commands, timeout calibration, and #194 no-polling rule without falsely claiming one 54/54 command | Push and open one PR; external hosted checks gate merge, eligible Issue closure, and branch cleanup |
| 4 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `main@df7012b6` | external-task contract and live callback checkpoint | `1a5fa40378594c3622eaabb7f7bd57a30fcf416b`, plus containing workflow completion commit | local, PR pending | `2026-08-12T01:14:01+08:00` | Repair capability-profile 1.4 validation, bind dispatch/completion envelopes, and preserve the successful source-task callback receipt | Push the final head; delegate one terminal hosted-check report; merge only after all checks pass |
