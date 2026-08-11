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
- `status`: `in_progress`
- `current_phase`: `integration-checkpoint`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-standards-simplification`
- `created_at`: `2026-08-11T13:31:10+08:00`
- `updated_at`: `2026-08-11T23:30:58+08:00`
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

## Stages And Checkpoints

1. Freeze merged `main`, Issue/Project authority, workflow branch, and draft assessment. `completed`
2. Complete R2 reference-loading inventory and doctrine-equivalence baseline. `completed`
3. Complete R3 terminology ownership and definition-placement inventory. `completed`
4. Build and review the controlled current-tree package projection, then finalize the decision ledger. `completed-with-v0.13-fail-closed-limitation`
5. Present bounded delivery scopes for owner confirmation and create the approved successor Issues. `completed`
6. Coordinate separately authorized successor deliveries and the final governed v0.13 package-candidate review. `in_progress`

## Resume Checkpoint

- Last completed action: Read back the owner's main-integration and branch-cleanup instruction, refreshed `origin/main@df7012b6`, and proved the current branch contains the complete #191/#192/#193 delivery while the older local branches are ancestors or content-equivalent predecessors.
- Current task: `STD001-003`.
- Exact next action: commit this integration authorization, run the repository critical gate, create and validate the incomplete-workflow handoff checkpoint, then push the current branch and open the single PR to `main`.
- Validation already completed: #191 is independently verified by `ASM-20260811-004`; #192 by `ASM-20260811-005`; #193 selected-payload, version, packaging, archive/apply, routing, and aggregate gates passed and `ASM-20260811-006` found no new blocking finding. Earlier package, sandbox, source-governance, and WSL timeout receipts remain recorded rather than relabeled.
- Git state: clean current branch `codex/2026-08-11-std-001-pkg-navigation-closure@fe969d3`; refreshed `origin/main@df7012b6`; no overlapping open pull request exists.
- Branch history and checkpoint handoffs: integration is now authorized but not yet transported. Because the parent workflow remains active for the real v0.13 candidate review, the PR merge is an incomplete-workflow checkpoint and requires a registered machine-readable handoff.
- Blockers or unresolved decisions: the critical handoff gate and hosted PR checks must pass before integration. No governed v0.13 release record or real candidate exists yet; Issue close, Project state, tag, Release, and publication remain separately gated.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local audit bootstrap | `a77db619fa48d44245845ee9f0e1d275103e1a42` | local | `2026-08-11T13:31:10+08:00` | Begin the owner-approved #61 R2/R3 investigation and preparation scope | Review the final assessment and proposed successor delivery ledger |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local assessment checkpoint | `c001cc34617396bfbde2b8138c7a65f45fc484e0` | local | `2026-08-11T13:45:48+08:00` | Preserve the final baseline assessment, controlled projection review, and decision ledger before owner approval | Record owner approval and successor Issue read-back |
| 2 | `codex/2026-08-11-std-001-r2-review-routing` | `codex/2026-08-11-std-001-standards-simplification@73b12c6` | local verified implementation | `f62f110` | local | `2026-08-11T20:56:40+08:00` | Preserve the completed #191 routing delivery and independent `ASM-20260811-004` evidence without merging its rollback unit | Start #192 from the updated coordination branch; retain #191 for owner review |
| 3 | `codex/2026-08-11-std-001-r3-governance-terms` | `codex/2026-08-11-std-001-standards-simplification@088fee7` | local verified implementation | `92e7383` | local | `2026-08-11T21:40:15+08:00` | Preserve the completed #192 governance-term delivery and independent `ASM-20260811-005` evidence without merging its rollback unit | Start #193 from the updated coordination branch; use a validation-only combined view for #191/#192 package closure |
| 4 | `codex/2026-08-11-std-001-pkg-navigation-closure` | `codex/2026-08-11-std-001-combined-validation@b1aacf8` | local verified implementation | `ff80d590`, `cef711a`, `fe969d3` | local | `2026-08-11T22:45:54+08:00` | Preserve selected-payload/component closure, bounded upgrade-test policy, and independent `ASM-20260811-006` evidence without claiming integration | Create the required incomplete-workflow handoff, then open the owner-authorized integration PR to `main` |
