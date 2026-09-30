# Sub-Agent Runtime Integration Planning

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-18-sub-agent-runtime-integration-planning`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-18-sub-agent-runtime-integration-planning`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-07-18-sub-agent-runtime-integration-planning`
- `created_at`: `2026-07-18T20:15:59+08:00`
- `updated_at`: `2026-07-18T20:15:59+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the repository has 18 canonical delegated sub-agent role prompts, but only `context-translator` declares and ships runtime-native adapters. The current routing and validator surfaces do not clearly distinguish intentional dynamic prompt loading from missing adapter integration.
- Authorized scope: analyze canonical role consumption and adapter coverage, classify the governance gap, create one durable backlog item, and place the work on the active release roadmap.
- Exclusions: do not generate adapters for every role, change model selections, modify runtime permissions, alter canonical role behavior, implement validator changes, or remediate the existing routing table in this planning workflow.
- Completion criteria: record file-backed role and adapter evidence; define dynamic versus runtime-native integration modes; create a traceable backlog item; separate patch-safe discovery correction from minor-version governance work; and make the `v0.6.0` taxonomy horizon depend on the stabilized contract.

## Artifact Contract

- Baseline assessment: not created; this is a bounded governance inventory and release-planning decision, not a formal persisted audit.
- Remediation report: not created; implementation is deferred to `SAG-001`.
- Verification assessment: required only if the future implementation workflow changes canonical behavior or runtime routing.
- Tasks: `.dev/workflows/2026-07-18-sub-agent-runtime-integration-planning/tasks/`

## Evidence Inventory

| Surface | Observed State | Evidence |
| --- | --- | --- |
| Canonical roles | 18 active `sub-agent.yaml` manifests | `.dev/agents/*/sub-agent.yaml` |
| Dynamic roles | 17 roles declare `wrapper_targets: []` and have at least one active external consumer | canonical manifests, `.ai/SUB-AGENT-SYSTEM.MD`, owning skill references, and active guides |
| Runtime-native role | `context-translator` declares `codex`, `claude`, and `copilot` targets | `.dev/agents/context-translator/sub-agent.yaml` |
| Runtime adapters | one adapter exists in each declared runtime root | `.codex/agents/context-translator.toml`, `.claude/agents/context-translator.md`, `.github/agents/context-translator.agent.md` |
| Packaging | canonical roles and all three adapter roots are framework-managed package entries | `.ai/distribution/profiles/dotnet-backend.yaml` |
| Routing | the active routing table lists 17 roles but omits `context-translator` | `.ai/SUB-AGENT-SYSTEM.MD`; the independent post-v0.4.0 plan also records `#AIC-010` |
| Validation | common sub-agent manifest fields are validated, but adapter metadata and target-to-path parity are validated only for `skill.yaml` | `.ai/assets/CANONICAL-SCHEMA.MD` and `.ai/scripts/validate-ai-context.py` |
| History | canonical translator plus all three adapters were introduced together | commit `0a7ac646e3d5d48c77fc45ebdac7b1fdeeb2176d` |

## Analysis

### Independent Baseline

A portable canonical role library does not require one runtime-native adapter per
role. A main agent can load a canonical role prompt and pass it to a generic
worker when the role has no runtime-specific model, tool, permission, or
invocation requirement. Native adapters are justified when the runtime must
select a specialized model or expose a stable named agent entry.

The repository should therefore avoid bulk wrapper generation. It needs an
explicit promotion contract that makes intentional dynamic roles
distinguishable from missing native adapters.

### Repository-Aware Pass

The existing metadata already expresses most of the intended distinction:

- `wrapper_targets: []` means the role remains canonical and dynamically loaded;
- non-empty `wrapper_targets` means runtime-native adapters are expected.

However, the sub-agent schema does not define `wrapper_metadata`, and
`validate_canonical_assets` calls wrapper-path validation only for `skill.yaml`.
The repository can therefore lose or misplace a declared sub-agent adapter while
the main AI-context validator still passes. The active routing table also omits
the one role that has already been promoted.

### Findings

| Finding | Severity | Disposition |
| --- | --- | --- |
| `SAG-F-001` — Declared sub-agent adapter targets have no deterministic target-to-path parity contract or validator coverage. | MEDIUM | Plan for `v0.5.0` under `SAG-001`; this adds governance and validation semantics. |
| `SAG-F-002` — `context-translator` is canonical and packaged with three adapters but is absent from active role routing. | LOW | Treat the routing/catalog-only correction as a `v0.4.1` patch candidate. |
| `SAG-F-003` — The repository does not document criteria for promoting a dynamic role to a runtime-native adapter. | MEDIUM | Define selective promotion criteria in `v0.5.0`; do not pre-authorize adapters for all roles. |

## Integration Mode Decision

| Mode | Canonical Signal | Runtime Projection | Default |
| --- | --- | --- | --- |
| Dynamic canonical role | `wrapper_targets: []` | The owning skill or main agent reads `sub-agent.yaml` and delegates to a generic worker. | Default for the 17 existing domain, implementation, test, and review roles. |
| Runtime-native role | non-empty `wrapper_targets` plus exact adapter metadata | One thin adapter per declared target selects runtime-specific model, tools, permissions, or invocation behavior while importing canonical rules. | Exception justified by runtime-specific behavior; currently `context-translator` only. |

Runtime-native promotion requires a concrete runtime need, exact adapter paths,
packaging coverage, deterministic parity validation, and a compatibility plan.
Convenience or visual symmetry alone is not sufficient.

## Roadmap Timing

| Version | Decision |
| --- | --- |
| `v0.4.1` | Correct the existing `context-translator` routing/catalog omission only. This is a contract-preserving documentation correction and must not add adapter semantics or bulk-generate wrappers. |
| `v0.5.0` | Execute `SAG-001`: define the two integration modes, add sub-agent adapter metadata and parity validation with GWT coverage, verify packaging, and make explicit promotion decisions role by role. |
| `v0.6.0` | Consume the stabilized contract during skill-family taxonomy work. Do not make adapter generation an automatic consequence of taxonomy grouping or renaming. |

## Task Plan

| Task | Purpose | Status |
| --- | --- | --- |
| `SAGPLAN-001` | Inventory canonical roles, consumers, runtime adapters, packaging, validation, and Git provenance. | `completed` |
| `SAGPLAN-002` | Persist `SAG-001` and update the active roadmap and discovery indexes. | `completed` |

## Resume Checkpoint

- Last completed action: created `SAG-001`, assigned the governance contract to `v0.5.0`, identified the existing routing omission as a `v0.4.1` patch candidate, and made `v0.6.0` taxonomy depend on the stabilized contract.
- Current task: none; planning workflow completed.
- Exact next action: during `v0.4.1` candidate selection, include only the routing/catalog correction if it remains current; activate the full `SAG-001` workflow when the roadmap reaches `v0.5.0`.
- Validation already completed: direct manifest and adapter inventory; active external reference inventory for all 18 roles; Git provenance inspection; canonical schema and validator control-flow review; workflow/backlog, AI-context, JSON, YAML, and whitespace validation.
- Git state: changes committed on the dedicated workflow branch.
- Branch history and checkpoint handoffs: segment 1 started from `main`; no push, merge, tag, release, or publication action was authorized.
- Blockers or unresolved decisions: the future `v0.5.0` workflow must verify each runtime's then-current adapter schema and decide whether any role beyond `context-translator` has a concrete native-adapter need.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-18-sub-agent-runtime-integration-planning` | `main` | planning | recorded by workflow commit | local | `2026-07-18T20:15:59+08:00` | Analyze sub-agent integration and create a durable roadmap handoff. | Planning complete; activate future work from the roadmap and `SAG-001`. |
