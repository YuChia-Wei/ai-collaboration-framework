# v0.11.0 Product Boundary, Delivery Contract, And Evidence Completion

## Workflow Metadata

- `workflow_id`: `2026-08-09-v0-11-product-boundary-delivery-evidence`
- `plan_id`: `development-plan-2026-08-09-v0-11-product-boundary-delivery-evidence`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-09-v0-11-product-boundary-delivery-evidence`
- `base_branch`: `main`
- `status`: `active`
- `created_at`: `2026-08-09T00:44:44+08:00`
- `updated_at`: `2026-08-09T00:44:44+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/workflow.yaml`

## Objective And Authority

Deliver, publish, and terminally close `v0.11.0` under online Issue #151 and the owner-supplied R2 work package. Online GitHub Issues are work-management authority; this plan is execution evidence. The owner explicitly waived validation execution for this bounded delivery, so no unexecuted gate is recorded as passed.

## Runtime Worker Preflight

- `bounded-general-worker`: present, `gpt-5.6-terra`, `xhigh`, source-only runtime execution profile.
- `bounded-routine-worker`: present, `gpt-5.6-luna`, `high`, read-only source runtime execution profile.
- `context-translator`: unchanged canonical runtime-native role adapter.
- Canonical role inventory remains 18; the two generic profiles are not canonical roles and remain excluded from downstream distribution.

## Delivery Cohesion And Stages

The approved Issues share one release identity, candidate, rollback, and publication boundary. They use one workflow with coherent stages: `V011-BASELINE` (#151), `V011-TERM` (#148), `V011-VAL` (#96/#144), `V011-EVAL` (#95/#143), `V011-READY` (#147), `V011-PRODUCT` (#145), `V011-CLI` (#146), `V011-CANDIDATE` (#151), `V011-PUBLISH` (#151/#152), and `V011-CLOSEOUT` (#148).

## Constraints

- Preserve all existing immutable tags and Release assets.
- Do not implement #149 native language/runtime work, #150 repository rename, or #153 Copilot support.
- Do not infer token usage or collect prompts, secrets, credentials, or private host identity.
- Use `gh` and WSL only outside the sandbox.
- Do not run validators or tests in this owner-directed fast path; record them as `deferred-with-owner`, never passed.

## Worker Coordination

| Task | Execution Profile | Owning Skill | Canonical Role | Scope | Status |
| --- | --- | --- | --- | --- | --- |
| V011-VAL / V011-EVAL | `bounded-general-worker` | `ai-context-governance` | not applicable; the skill has no role binding for this source-governance unit | `.ai/scripts/**`, `.github/workflows/**` | in progress |
| V011-READY / V011-PRODUCT / V011-CLI | `bounded-general-worker` | `ai-context-governance` | not applicable; the skill has no role binding for this contract unit | `.ai/assets/shared/**`, `.ai/distribution/**`, environment policy and bounded ADRs | in progress |

Nested workers are prohibited. The parent owns GitHub state, integration, release identity, and final acceptance.

## Validation Selection

Spec compliance is not selected. All test and validator execution is `deferred-with-owner` by the current explicit instruction. Provider read-back used for identity and publication is operational evidence, not a validation pass.

## Publication And Closeout

Candidate source must be merged to current `main`; the new annotated `v0.11.0` tag may be created only if absent and targeted at that exact main. Publish governed ZIP, tar.gz, checksum sidecars, and release notes; then persist one records-only terminal update without rebuilding package bytes. Deferred Issues #149, #150, and #153 remain open.
