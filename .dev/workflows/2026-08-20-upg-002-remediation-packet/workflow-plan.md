# UPG-002 Prospective Cutover And Durable Remediation Packet

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-upg-002-remediation-packet`
- `plan_id`: `development-plan-2026-08-20-upg-002-remediation-packet`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-20-upg-002-remediation-packet`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-20T09:10:41+08:00`
- `updated_at`: `2026-08-20T13:54:15+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-upg-002-remediation-packet/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-upg-002-remediation-packet/`

## Development Objective

- Product or software outcome: Implement live Issue #203 so an upgrade uses incoming validation prospectively and persists a canonical machine-readable remediation packet before any target mutation or provenance finalization.
- Current lifecycle entry point: Accepted online Issue and explicit owner authorization; implementation inventory is active.
- User constraints: Preserve rejected, interrupted, rollback, and terminal evidence; keep automatic proposals separate from owner-approved writes; do not rewrite historical commits.
- Non-goals: Project field restoration, local roadmap/backlog mutation, unrelated Issues, tag, Release, publication, nightly activation, or external-repository mutation.

## Inputs

- Requirements: Live GitHub Issue #203 and current repository-owner instructions.
- Specifications: Current upgrader contracts, schemas, templates, scripts, package boundaries, and validation fixtures.
- Architecture decisions: Prospective adoption boundary; immutable machine packet as canonical source; derived human report; durable transaction composition with #200 and package closure with #201.
- Existing implementation or tests: Current upgrade plan/apply/finalization runtime and target-effective validation suites.

## Development Stages

### Stage 1

- `stage_id`: `UPG-002`
- Goal: Deliver the complete prospective-cutover remediation packet contract and implementation.
- Capability slot: `initialized-target-upgrade`
- Owner skill: `ai-context-upgrader`
- Scope: Packet schema and persistence, incoming validator selection, mutation gate, receipt lifecycle, resume/rollback evidence, derived human output, and focused fixtures.
- Non-goals: Multi-hop route orchestration (#206) and delegation policy (#208).
- Dependencies: Integrated #200, #201, and #219 source baseline.
- Validation: Focused fixtures, package-native validation where applicable, exact-head independent audit, hosted checks, and post-merge online read-back.
- Commit checkpoint: One coherent terminal-close PR for Issue #203.

## Role Execution Coordination

Pre-#207 delegated Terra contexts are recorded only as generic bounded execution contexts. They are not claims that #207 canonical roles exist or were invoked.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| UPG-002 | pre-#207 bounded contexts / no canonical path | ai-context-upgrader | completed | Generic bounded Terra Max contexts implemented separate runtime/finalization slices and one read-only semantic gap review; these are not #207 role invocations. | root / integrated and independently revalidated focused behavior | transient agent receipts |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| Issue contract -> implementation | approved | Explicit repository-owner prompt authorizes #203 implementation, PR, review, repair, and merge. | none |

## Validation Strategy

- Requirement/spec traceability: Map every live #203 acceptance criterion and owner decision to schema, runtime gate, fixture, and terminal evidence.
- Architecture validation: Preserve source/target/provider/runtime boundaries and compose rather than duplicate #200/#201 behavior.
- Test and implementation validation: Narrow Python suites first; package-native and repository validators after coherent mutation.
- Review/compliance gates: Fresh exact-head Sol High independent audit, hosted checks, admitted-head merge, then Issue and Project read-back.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root or isolated temp fixture selected by repository tests.
- Target-owned commands: resolved from existing test modules and release-profile contracts after implementation inventory.
- Prerequisites and environment boundary: Follow `.dev/ai-context/local/cli-execution-routing.yaml`; temp-fixture tests run on the authorized host route.
- Target policy: one attempt per unchanged routed command; preserve timeouts and failures.
- Default selected levels: `unit`, `integration`

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | commit-policy 23/23; semantic lifecycle 8/8; wrapper metadata 16/16 | root / exact-head audit remains |
| integration | passed-with-retained-failures | GWT047-GWT059 each passed in bounded post-repair host groups, including retained output bytes and rollback before/after target validation; retained combined-suite timeout, obsolete-selector failure, sandbox WinError 5, and four repair-driving focused failures | root / repair review and immutable-head validation remain |

## Spec Compliance Selection

- Selected: no
- Activation source: No problem-frame compliance gate selected by the live Issue.
- Outcome: `not-applicable`
- Coverage and evidence: Focused behavioral fixtures and governed review replace spec-compliance scoring for this slice.

## Progress And Handoff

- Current stage: UPG-002 post-audit repair integrated; replacement exact-head audit and hosted admission are pending.
- Completed stages: Live Issue read; owning-skill contract read; clean source applicability packet; dedicated branch; packet/decision/receipt runtime; prospective policy cutover; candidate-authority, predecessor, package, migration, and incoming-validation identity binding; transaction-owned validation-output binding; rollback-capable pre-provenance lifecycle; rejected/historical/terminal invariants; focused validation.
- Deferred stages and reasons: None within #203.
- Open decisions: No owner-sensitive implementation decision is pending. Multi-hop pending-receipt consumption remains owned by #206, not this single-hop slice.
- Continuation instructions: Validate and commit this truthful workflow closeout, push the repaired PR head, obtain a new fresh exact-head independent audit and new hosted checks, then merge only that admitted head.
- Target policy references: `.agents/skills/ai-context-upgrader/SKILL.md`; `.ai/assets/skills/ai-context-upgrader/skill.yaml`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 branches from clean integrated main `61fbf701b064d05b91cce2ecd778ab8a09ddc57e`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-upg-002-remediation-packet` | `main@61fbf701b064d05b91cce2ecd778ab8a09ddc57e` | repair-ready | `9dfa46b928247681c58ac0978803aee203067d33` | origin / PR #224 | `2026-08-20T13:54:15+08:00` | Deliver #203 and repair the first fixed-head audit plus hosted findings. | Validate this workflow-only evidence commit, push, and replace both invalidated gates. |

## Completion Summary

- Outcome: implementation and focused repair validation complete; the first fixed-head audit and hosted PR profile failed at `66dc77d901dec3eaebf6356183f1b6f0c55f12ef`, their findings were repaired in `9dfa46b928247681c58ac0978803aee203067d33`, and replacement provider admission remains required.
- Changed artifacts: upgrader contracts/schemas/wrappers, package apply/record CLI, target finalization runtime, commit policy, focused fixtures, and this workflow evidence.
- Approved requirement/specification evidence: live Issue #203 and explicit owner instructions.
- Implementation completion evidence: canonical packet before mutation, derived report, separate exact owner decision, record-only target-validation receipt, target-prospective policy adoption, candidate authority plus sealed package/migration identity binding, retained rejected/historical evidence, and durable terminal invariant are implemented.
- Required test outcomes: focused positive/fail-closed suites passed; one combined suite timeout and one obsolete-selector failure are retained truthfully; immutable-head broad validation remains pending.
- Selected compliance evidence: not applicable.
- Review disposition: initial pre-commit semantic review found rollback, output-byte, exact-identity, recovery-boundary, and workflow-evidence gaps; repairs and focused tests are complete, and read-only current-byte repair verification found no residual blocker in those areas. Fresh exact-head Sol High audit remains pending.
- Validation evidence: focused package/finalization groups, recovery, candidate-package drift rejection, policy, semantic lifecycle, wrapper metadata, package reference integrity, AI-context/source/workflow validators, AST/YAML/import checks, and diff check passed. The sandbox temp-fixture WinError 5 was preserved; the same two-test selection passed 2/2 through the authorized host route, followed by adjacent finalization regressions 2/2.
- Workflow task state: in progress.
- Commits: `66dc77d901dec3eaebf6356183f1b6f0c55f12ef` (initial implementation) and `9dfa46b928247681c58ac0978803aee203067d33` (hosted/audit repair). The workflow-only evidence commit that contains this line is identified by the exact PR head read-back rather than a self-referential embedded SHA.
- Branch / checkpoint / handoff evidence: PR #224 was created at `66dc77d901dec3eaebf6356183f1b6f0c55f12ef`; hosted run `32335941157` and the first fresh Sol High audit both failed at that head. Repairs are committed locally at `9dfa46b928247681c58ac0978803aee203067d33` and are not admitted until pushed, rechecked, and newly audited.
- Residual risks: The active pending apply receipt remains the current single-hop validation authority; #206 must consume/archive that boundary between sequential hops without weakening current target validation. The derived human report remains less detailed than the canonical machine packet, but the machine packet is the owner-selected authority and the report is derived.
