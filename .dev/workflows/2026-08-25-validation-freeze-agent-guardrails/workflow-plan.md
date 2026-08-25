# Validation Freeze And Agent Execution Guardrails

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-25-validation-freeze-agent-guardrails`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-25-validation-freeze-agent-guardrails`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `audit`
- `artifact_root`: `.dev/workflows/2026-08-25-validation-freeze-agent-guardrails`
- `created_at`: `2026-08-25T14:55:24+08:00`
- `updated_at`: `2026-08-25T14:55:24+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Current validation lifecycle evidence can self-invalidate after terminal metadata commits, while delegated and fixed-head execution lacks complete deterministic packet, lease, evidence-class, retry, and discovery-freshness enforcement.
- Authorized remediation scope: GitHub Issues #249 and #253 as one cohesive governance delivery with distinct tasks and acceptance evidence, including portable contracts, source workflow policy, software-development-orchestrator consumers, validators, regression fixtures, English canonical guidance and structurally aligned Traditional Chinese guidance.
- Exclusions: #250 product identity, #251 package Git snapshot, #252 validation route split, aggregate-runner parallelization, v0.14 or #246 historical evidence changes, provider/release mutation, CLI/registry/installer work, external repositories, push, PR, merge, Issue/Project mutation, release allocation, tag, Release, or publication.
- Completion criteria: Every #249 and #253 acceptance has a separate machine-readable evidence mapping and truthful terminal disposition; focused and selected aggregate validation pass at immutable local commits; the final clean exact head receives an independent read-only audit; only parent integration readiness is reported.

## Delivery Cohesion Decision

#249 and #253 share the validation lifecycle, software-development-orchestrator packet and evidence contracts, future-agent guidance, validators, review boundary, v0.15 release horizon, atomic rollback boundary, and final exact-head audit. They therefore use one workflow, branch, validation path, and parent integration decision. Acceptance remains independently mapped by Issue and acceptance ID; no workflow-level success field substitutes for either Issue's evidence.

## Evidence And Authority

- Live GitHub read-back on 2026-08-25: #249 and #253 are open, Project status `Inbox`, with no comments; their bodies are the scope contracts and the parent orchestration prompt records owner execution authorization.
- Completed authority/baseline read-back: #118/#119 role reachability and provider-neutral execution, #194 long-running delegation, #204 terminal runner, #212 terminal Issue closure, #243 terminal-anchor reconciliation, and #246 portable fixture acceleration.
- Base: clean `origin/main@1326f827f61de8eebeef30748dcc82ffa7dd3764` after a fresh fetch.
- Isolation: `.dev/ai-context/local/worktrees/issue-249-253` on the dedicated branch. Main, #250, #251, and all other worktrees remain read-only.
- Code graph: the original project index was stale at `599136547bd30c9bcff288a51d7dc30a4b73950c`; a full worktree index was rebuilt and verified at the exact base SHA. Graph results remain discovery only.

## Tasks And Acceptance Ownership

| Task | Issue ownership | Acceptance evidence boundary |
| --- | --- | --- |
| `GOV013-001` | #249 | Validation taxonomy, deterministic dependency/content fingerprint, reuse receipt, freeze sequencing, hosted-context and exact-head status semantics, positive/negative/unknown fail-closed regression evidence. |
| `GOV014-001` | #253 | Planned commit preflight, execution packet, worktree lease, acceptance ledger/report parity, retry fingerprint/budget, PowerShell and code-graph freshness enforcement. |
| `GOV013014-002` | #249 and #253 projections only | English canonical guidance, Traditional Chinese structural/normative parity, software-development-orchestrator consumer references, workflow/future-agent projection parity. |
| `GOV013014-VAL-001` | #249 and #253 separately | Focused validators, selected aggregate/source-governance evidence, commit validation, immutable-head audit and residual-risk closeout without provider/release mutation. |

## Stages And Checkpoints

1. Freeze live Issue, Git, authority, active-worktree, and code-graph freshness evidence.
2. Implement and validate #249 taxonomy, dependency/content fingerprint, reuse receipt, and validation-freeze lifecycle.
3. Implement and validate #253 execution packet, worktree lease, acceptance ledger/report parity, retry, host-command, and discovery freshness controls.
4. Reconcile canonical guidance and derived projections without transferring governance ownership to the software-development-orchestrator.
5. Validate planned commit messages before each durable commit, complete focused checks, and freeze an immutable local validation head.
6. Delegate any long-running selected gate through one schema-valid callback/event-wait path, then obtain a fresh exact-head independent read-only audit.
7. Reconcile each Issue acceptance separately and report only ready for parent integration decision.

## Resume Checkpoint

- Last completed action: Created the isolated worktree, refreshed live Issue/baseline evidence, loaded governance policy, and rebuilt the stale code graph at the exact base.
- Current task: `GOV013-001`
- Exact next action: Inventory current validation runner, evidence, hosted-context, and terminal lifecycle contracts, then define the smallest #249 machine-readable owner and validator surface.
- Validation already completed: clean main/worktree and base read-back; full code-graph reindex bound to `1326f827f61de8eebeef30748dcc82ffa7dd3764`.
- Git state: dedicated local branch at the exact fetched base; workflow bootstrap is uncommitted.
- Branch history and checkpoint handoffs: segment 1 started locally from `origin/main@1326f827f61de8eebeef30748dcc82ffa7dd3764`; no push, PR, merge, or provider mutation.
- Blockers or unresolved decisions: none. A change to canonical semantics, hosted required-check policy, release truth, provider state, or integration topology requires owner direction.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-25-validation-freeze-agent-guardrails` | `origin/main@1326f827f61de8eebeef30748dcc82ffa7dd3764` | local-start | pending | local only | `2026-08-25T14:55:24+08:00` | Owner-authorized cohesive #249/#253 governance delivery | Continue inventory and implementation in the isolated worktree. |
