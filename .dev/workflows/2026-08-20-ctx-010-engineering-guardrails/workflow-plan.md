# CTX-010 Optional Engineering Guardrails Provider Contract

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-ctx-010-engineering-guardrails`
- `plan_id`: `development-plan-2026-08-20-ctx-010-engineering-guardrails`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-20-ctx-010-engineering-guardrails`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-20T14:45:44+08:00`
- `updated_at`: `2026-08-20T16:15:04+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-ctx-010-engineering-guardrails/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-ctx-010-engineering-guardrails/`

## Development Objective

- Product or software outcome: Implement live Issue #205 so the .NET technology binding can recommend Engineering Guardrails without selecting, installing, or claiming execution for an unavailable provider, while retaining an SDK-free framework package and bounded target-owned analyzer starting templates.
- Current lifecycle entry point: Live Issue contract and exact external-provider state have been read; owner authorization in the v0.14 delivery prompt supersedes the Issue body's earlier no-implementation boundary.
- User constraints: Keep recommendation, selection, readiness, compatibility, and execution evidence distinct; do not modify the external repository or invent a package identity, version, feed, publication contract, or readiness result.
- Non-goals: Contracts adoption (#179), external provider publication, Project-field restoration, local roadmap/backlog mutation, tag, Release, package publication, or nightly activation.

## Inputs

- Requirements: Live GitHub Issue #205 and the current repository-owner v0.14 instructions.
- Specifications: Current provider-neutral semantic rule layer, .NET technology bindings, upgrade/reporting schemas, recipe manifests, and package boundaries.
- Architecture decisions: `official-recommended` is independent of selection; provider capability identity is stable without a package ID; exact readiness evidence is required before execution claims; source/test templates are bounded target-owned starting points.
- Existing implementation or tests: Current SDK-free .NET profile, reference-only analyzer recipe, package-native validation, and upgrade/provider fixtures.

## Development Stages

### Stage 1

- `stage_id`: `CTX-010`
- Goal: Deliver the complete optional Engineering Guardrails provider contract and target-owned fallback templates.
- Capability slot: `ai-context-governance`
- Owner skill: `ai-context-governance`
- Scope: Provider capability identity and state schema, .NET recommendation binding, readiness/compatibility/execution evidence gates, capability-gap reporting, terminology correction, bounded analyzer and analyzer-test templates, and portable package-native fixtures.
- Non-goals: Provider installation or selection, Engineering Guardrails repository changes, Contracts adoption, and a required .NET SDK release gate.
- Dependencies: Integrated GOV-010 framework-source applicability and UPG-002 remediation evidence baseline.
- Validation: Focused positive and fail-closed fixtures; package-native validation; SDK-free structural template validation; source governance; exact-head independent audit; hosted checks; and post-merge Issue/Project read-back.
- Commit checkpoint: One terminal-close PR for Issue #205.

## Role Execution Coordination

Before #207 integration, delegated contexts are recorded only as generic bounded execution contexts. They are not claims that #207 canonical roles exist or were invoked.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| CTX-010 | pre-#207 bounded context / no canonical path | ai-context-governance | completed | Terra Max contexts completed inventory, implementation, three immutable smokes, and three bounded audit repairs. Fresh Sol High contexts independently failed `09aa506f`, `91d4025c`, and `e93f5847` without repair. None is a #207 role claim. | root / all findings accepted and repaired; fourth audit pending | transient receipts; versioned baseline repair `e68c0186128bb039f347846eddfc4938fd0cdfce` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| Issue contract -> implementation | approved | Explicit repository-owner v0.14 prompt authorizes #205 implementation, PR, review, repair, and merge; the live Issue alone is not treated as authorization. | none |

## Validation Strategy

- Requirement/spec traceability: Map each live #205 acceptance criterion and owner decision to a schema, binding, diagnostic, fixture, template, or package assertion.
- Architecture validation: Preserve source-framework, downstream-target, provider, package, and runtime-session truth as separate evidence layers.
- Test and implementation validation: Run narrow schema/fixture/template tests first, then clean immutable package-native and hosted validation.
- Review/compliance gates: Fresh exact-head Sol High independent audit, hosted checks, admitted-head merge, then Issue and Project read-back.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root or isolated package fixture selected by repository tests.
- Target-owned commands: resolved from current focused tests and package validation contracts after inventory.
- Prerequisites and environment boundary: Follow `.dev/ai-context/local/cli-execution-routing.yaml` when a selected command crosses the sandbox or requires host tooling.
- Target policy: Preserve first failures and timeouts; full or release-profile validation requires a clean immutable commit and external read-only execution.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: SDK-based execution remains unselected because #205 requires SDK-free release validation.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed-with-retained-failures | Provider contract 9/9, SDK-free 5/5, and registry 6/6 passed. Retained pycache, initial fixture, local extract, isolated object-store, and sandbox Git Bash failures remain. | root / no focused unit work remains |
| integration | in-progress | Package projection passed 1/1. Smokes passed at `09aa506f`, `91d4025c`, and `e93f5847`, but each head was invalidated by a later audit repair. A fourth smoke/audit and hosted checks remain at the versioned-baseline head. | root / clean immutable revalidation and provider admission |

## Spec Compliance Selection

- Selected: no
- Activation source: No problem-frame compliance gate is selected by the live Issue or owner prompt.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance-traceable fixtures and governed independent audit are the selected gates.

## Progress And Handoff

- Current stage: CTX-010 post-audit repair revalidation and independent provider admission.
- Completed stages: Live Issue/provider read-back; workflow/packet/inventory; implementation/focused validation; three immutable smokes; three independent audit FAIL cycles; fail-closed claim sealing; versioned Issue #205 baseline with canonical schema/contract/template digests and fourteen coordinated-mutation categories.
- Deferred stages and reasons: None within #205.
- Open decisions: No owner-sensitive decision is pending; unavailable provider identity/readiness must remain explicitly unknown or unproven.
- Continuation instructions: Commit the third-audit and versioned-baseline repair evidence, rerun immutable package smoke at the new head, obtain a fourth fresh Sol High exact-head audit, then push and prepare the terminal-close PR with hosted admission.
- Target policy references: `.agents/skills/ai-context-governance/SKILL.md`; `.ai/assets/skills/ai-context-governance/skill.yaml`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 branches from clean integrated main `8bcb26f1440b49f357cc494217eabd67d400e64f`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-ctx-010-engineering-guardrails` | `main@8bcb26f1440b49f357cc494217eabd67d400e64f` | audit-repair-03 | `e68c0186128bb039f347846eddfc4938fd0cdfce` | local | `2026-08-20T16:15:04+08:00` | Third audit proved coordinated schema plus artifact weakening stayed green. | Commit evidence and replace the third invalidated smoke/audit at the versioned-baseline head. |

## Completion Summary

- Outcome: Implementation and three audit repairs complete. All three exact-head failures are retained; fourth package smoke, fourth audit, and hosted admission are pending.
- Changed artifacts: Provider-local contract/schema, target-owned analyzer and test starting templates, recipe documentation, focused GWTs, SDK-free/package assertions, and validation registry membership.
- Approved requirement/specification evidence: Live Issue #205 plus explicit repository-owner v0.14 authorization.
- Implementation completion evidence: Stable capability identity; official-recommended and not-selected coexistence; explicit declined, selected-unavailable, and synthetic readiness semantics; separately typed/digested readiness, compatibility, and execution receipts; no real provider identity or execution claim; SDK-free target-owned templates.
- Required test outcomes: Provider 9/9, SDK-free 5/5, registry 6/6, and package projection 1/1 passed. Three package smokes passed only at invalidated pre-repair heads; replacement smoke and hosted checks remain.
- Selected compliance evidence: Not applicable.
- Review disposition: Three Sol High FAILs progressively found one-sided fabricated claims, additional claim-invariant drift, then coordinated schema/artifact weakening. Repair `e68c0186` adds a versioned Issue #205 authority baseline with independent canonical digests and coordinated mutation protection; fourth audit remains mandatory.
- Validation evidence: Framework-source packet `09b7c4c770c5a6d5f79f5b48cc0d1d353d65a5260df9bb489351cc44ddc660ae`; validate-ai-context, validate-source-governance, validate-shell-assets, YAML/static checks, and focused GWTs passed; first failures remain retained in the task record.
- Workflow task state: in progress.
- Commits: `ea6bf4e5` bootstrap; `16584c99` implementation; `09aa506f`, `91d4025c`, and `e93f5847` evidence heads; `b3425f56`, `3c222110`, and `e68c0186` audit repairs.
- Branch / checkpoint / handoff evidence: dedicated branch created from `8bcb26f1440b49f357cc494217eabd67d400e64f`; implementation commit is clean and package-visible.
- Residual risks: The provider has analyzers and tests in source but no approved packable distribution identity or hosted release; all real-provider execution claims must remain unavailable until external evidence changes.
