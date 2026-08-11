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
- `branch`: `codex/2026-08-11-std-001-standards-simplification`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `successor-implementation`
- `artifact_root`: `.dev/workflows/2026-08-11-std-001-standards-simplification`
- `created_at`: `2026-08-11T13:31:10+08:00`
- `updated_at`: `2026-08-11T20:18:57+08:00`
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
- Current owner instruction: local implementation of Issues [#191](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/191), [#192](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/192), and [#193](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/193) is approved, in that order, with validated results returned for owner review. Project allocation, push, PR, merge, Issue closure, tag, Release, and publication remain separate decisions.
- Delivery cohesion: R2, R3, and package-candidate review share branch, reviewers, validation, v0.13 decision gate, and rollback; one workflow coordinates them without forcing unrelated authority changes into one delivery.
- Planned integration: not selected until the decision ledger identifies whether the preparation artifacts stand alone or accompany one bounded remediation delivery.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260811-003/assessment.yaml`
- Decision ledger: `.dev/workflows/2026-08-11-std-001-standards-simplification/reports/decision-ledger.md`
- Verification assessment: allocate only after a bounded remediation is selected and implemented.
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

- Last completed action: Recorded owner approval of the three-delivery split and ownership-registry placement, then created and read back Issues #191, #192, and #193. Repository automation placed each in Project #3 `Inbox`; no workflow-owned Project fields were configured.
- Current task: `STD001-003`.
- Exact next action: Start the dedicated #191 branch and workflow, implement and verify its bounded reference-routing scope, then continue #192 and #193 without combining their rollback units.
- Validation already completed: workflow/assessment validators passed the bootstrap; exact Git-blob inventory completed; v0.13 package build failed closed for missing release truth; controlled projection ZIP/tar validation passed; extracted payload navigation failed with seven genuine missing targets.
- Git state: Dedicated branch `codex/2026-08-11-std-001-standards-simplification`; bootstrap `a77db619fa48d44245845ee9f0e1d275103e1a42` and assessment checkpoint `c001cc34617396bfbde2b8138c7a65f45fc484e0` are local; this successor-intake update is pending validation and commit.
- Branch history and checkpoint handoffs: Nothing from #61 has been pushed or merged.
- Blockers or unresolved decisions: Project field allocation and transport remain pending; no governed v0.13 release record or real candidate exists yet, so the final #193 candidate gate remains future work.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local audit bootstrap | `a77db619fa48d44245845ee9f0e1d275103e1a42` | local | `2026-08-11T13:31:10+08:00` | Begin the owner-approved #61 R2/R3 investigation and preparation scope | Review the final assessment and proposed successor delivery ledger |
| 1 | `codex/2026-08-11-std-001-standards-simplification` | `main@df7012b6` | local assessment checkpoint | `c001cc34617396bfbde2b8138c7a65f45fc484e0` | local | `2026-08-11T13:45:48+08:00` | Preserve the final baseline assessment, controlled projection review, and decision ledger before owner approval | Record owner approval and successor Issue read-back |
