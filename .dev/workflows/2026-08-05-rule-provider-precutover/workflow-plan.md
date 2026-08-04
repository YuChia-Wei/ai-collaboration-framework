# AI Context Maintenance Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-05-rule-provider-precutover`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-05-rule-provider-precutover`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-05-rule-provider-precutover`
- `created_at`: `2026-08-05T01:29:39+08:00`
- `updated_at`: `2026-08-05T06:46:31+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Engineering-rule semantics, target-effective state, and the bundled .NET mechanical-validation provider are split across `.dev/standards/**`, `.ai/assets/**`, and root `tools/**`. Without explicit identities, a file-level migration plan, one target-effective resolver, and an inactive-by-default provider contract, agents can use stale defaults or confuse delivered source with active validation.
- Authorized remediation scope: Implement the owner-approved #92 pre-cutover contract through bounded Issues #109 through #117: stable engineering identities and owners; an exhaustive migration matrix; portable .NET asset migration; target-effective state; deterministic task-scoped packets; action-skill consumption; bundled-provider relocation and reference-in-place activation; and an Architecture Kit readiness gate that currently returns `unsupported/unavailable`.
- Authorization: The owner completed the #92 discussion and explicitly authorized workflow creation, bounded implementation, low-cost Terra sub-agent execution under root orchestration, and merge-commit / `--no-ff` integration on 2026-08-05. Issue state is traceability, not independent authority.
- Exclusions: v0.9.0 packaging, release preparation, publication, tag, or ROADMAP pre-allocation; actual Architecture Kit provider implementation, package publication, Diagnostic parity proof production, real-target proof, or cutover; materialize-to-tools implementation without target limitation evidence and separate authorization; target-owned `.slnx`, `Directory.Build.props`, `.editorconfig`, package/reference, severity, or warnings-as-errors mutations; #93/#99; #94; #98 implementation; product source/test trees.
- Completion criteria: Every child issue has durable accepted evidence; the ownership/migration contract has one canonical owner per semantic; target-effective resolution is deterministic and fail closed; bundled source is profile-owned and inactive until explicit reference-in-place activation; Architecture Kit remains unavailable; an independent read-only audit reconciles `AIC-001` and `AIC-002`; a PR is integrated by merge commit and merged main is read back. Release packaging remains a separate future workflow.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260804-002/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-05-rule-provider-precutover/reports/remediation-report.md`
- Verification assessment: allocate only after checking all local and remote refs for the next unused assessment ID.
- Tasks: `.dev/workflows/2026-08-05-rule-provider-precutover/tasks/`
- Migration matrix: `.dev/workflows/2026-08-05-rule-provider-precutover/evidence/migration-matrix.yaml`

## Work-Item Topology

| Umbrella | Bounded children | Workflow task |
| --- | --- | --- |
| #104 | #109 identity; #110 migration matrix; #111 portable .NET asset migration | `RPB-001`, `RPB-002`, `RPB-004` |
| #105 | #112 target-effective state; #113 resolver/packets; #114 action-skill consumption | `RPB-003`, `RPB-006` |
| #106 | #115 provider relocation/manifest; #116 reference-in-place activation | `RPB-005` |
| #107 | #117 readiness record and unavailable gate | `RPB-007` |

The four parents remain umbrella Enablers. The nine children record deliverable and rollback boundaries. They do not create nine workflows or nine releases.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260804-002#AIC-001` | HIGH | `ai-context-governance` | authorized remediation | `RPB-001` through `RPB-006` as applicable | matrix completeness, canonical-owner read-back, distribution/navigation evidence, independent audit |
| `ASM-20260804-002#AIC-002` | HIGH | `ai-context-governance` | authorized pre-cutover remediation | `RPB-003`, `RPB-005`, `RPB-006`, `RPB-007` | manifest/state read-back, reference-in-place evidence, unavailable gate, independent audit |
| `ASM-20260804-002#AIC-004` | HIGH | `ai-context-auditor` | retained evidence; no byte migration required | all tasks cite retained evidence | traceability read-back |

## Dependency-Ordered Tasks

1. `RPB-001` / #109 — stable engineering identities and ownership foundation.
2. `RPB-002` / #110 — exhaustive file-by-file migration matrix; starts after `RPB-001`.
3. `RPB-004` / #111 — apply non-provider portable .NET migration rows and derive machine-readable shared/profile rule catalogs; starts after `RPB-002`.
4. `RPB-003` / #112 and #113 — target-effective schema, index, deterministic resolver, and packets. The #112 schema depends on `RPB-001`; the #113 runtime follows `RPB-004` and consumes its catalogs rather than parsing Markdown or the flat registry.
5. `RPB-005` / #115 and #116 — relocate the bundled provider and implement reference-in-place activation; starts after `RPB-002` and uses the exact canonical root recorded by the matrix.
6. `RPB-006` / #114 — migrate action skills to effective-rule consumption; starts after `RPB-003` and must coordinate shared-file ownership with the independent #94 workflow.
7. `RPB-007` / #117 — implement the Architecture Kit readiness record and current unavailable gate; starts after `RPB-003` and `RPB-005`.

Only one task is marked `in_progress` in durable workflow state. The orchestrator may delegate non-overlapping bounded file ownership in parallel after its dependencies are complete.

## Cross-Workflow Coordination

- #94 exclusively owns `.ai/SUB-AGENT-SYSTEM.MD`, skill `role_bindings` and `role_execution`, direct/delegated/unavailable/not-applicable semantics, test-design-to-slice-implementation role mapping, no-delegation inline parity, and their fixtures.
- #92 owns engineering-rule/provider identities, the migration matrix, target-effective semantics, bundled-provider relocation/activation, and Architecture Kit readiness.
- `.ai/assets/CANONICAL-SCHEMA.MD` and applicable action-skill `skill.yaml` files are shared surfaces. Before an essential #92 edit, the orchestrator must name the exact section to the #94 workflow and select one writer for sequential integration.
- `RPB-006` must not edit #94-owned sub-agent sections. It may only add effective-rule packet consumption and rule-resolution evidence after shared ownership is coordinated.

## Validation And Evidence Policy

- Per explicit owner direction, do not execute `check-all`, `validate-*` repository scripts, or other repository validation scripts in this workflow.
- Do not classify skipped scripts as passed. Record them as `not-run-owner-directed` or `deferred-with-owner`.
- Use scoped read-back, structured diff inspection, deterministic fixture review, and `git diff --check` where useful. Hosted PR checks may run, but a failure is reported without local reproduction unless the owner changes direction.
- Final orchestration includes an independent read-only AI-context audit. Any mechanical checks assigned separately must also respect the owner prohibition on repository validation scripts.

## Stages And Checkpoints

1. Baseline evidence and owner decisions — completed from `ASM-20260804-002`, #92 discussion, and live Issue read-back at `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019`.
2. Workflow and bounded work-item binding — completed by creating #109 through #117 and formal sub-issue relationships under #104 through #107.
3. Dependency-ordered remediation — in progress; `RPB-001` through `RPB-005` completed. `RPB-006` is active.
4. Independent post-remediation audit — pending.
5. PR review, merge-commit integration, merged-main read-back, and closure — pending; release packaging remains excluded.

## Delivery And Merge Decisions

- Delivery grouping: one AI-context governance workflow because all tasks share the same owner decision, branch family, semantic outcome, reviewers, integration gate, release horizon, and rollback boundary.
- Phase representation: phases are substantive tasks in this workflow, not separate workflow directories. A checkpoint merge may create a continuation branch while preserving the same workflow ID if integration risk requires it.
- Integration gate: pull request to `main` under `.dev/TEAM-GIT-FLOW-RULES.MD`.
- Selected topology: merge-commit integration. The owner explicitly selected no-rebase `--no-ff` integration.
- Release boundary: completing this workflow does not package or publish v0.9.0. Completed work may be allocated to a later release workflow under the repository's release policy.

## Resume Checkpoint

- Last completed action: Completed `RPB-005` provider relocation, stable manifest/capability identity, source-only distribution, physical canonical-root binding, and inactive-by-default reference-in-place evidence contract for #115/#116.
- Current task: `RPB-006` is in progress.
- Exact next action: Add only the coordinated `effective_rule_consumption` sibling sections, canonical-schema documentation, and #92 resolver-consumer tests across the exact ten action skills.
- Validation already completed: prior migration/catalog and resolver read-back plus production blob parity, relocation/distribution scans, typed evidence and digest read-back, two independent provider review rounds with post-fix blocker confirmation, path/symlink/canonical-root source inspection, and `git diff --check`. No tests, builds, check-all, or repository validation scripts have run.
- Git state: branch `codex/2026-08-05-rule-provider-precutover` starts from `origin/main@d8580df4516155ff7b1a139d9a064a8b0d4b2019`.
- Branch history and checkpoint handoffs: segment 1 only; local durable checkpoints through `ec55b91`, with the RPB-005 checkpoint pending this commit; no push or merge handoff yet.
- Blockers or unresolved decisions: none. Shared-file sequencing with #94 is a coordination constraint, not an owner-decision blocker.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-05-rule-provider-precutover` | `main@d8580df4516155ff7b1a139d9a064a8b0d4b2019` | active remediation | pending | `origin/main` | `2026-08-05T01:29:39+08:00` | owner-authorized grouped pre-cutover remediation | execute `RPB-006` |
