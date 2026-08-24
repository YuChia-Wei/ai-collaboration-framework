# Retire Repository Backlog And Roadmap Authority

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-24-retire-repository-backlog-authority`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-24-retire-repository-backlog-authority`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-08-24-retire-repository-backlog-authority`
- `created_at`: `2026-08-24T20:11:36+08:00`
- `updated_at`: `2026-08-24T22:22:35+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`
- `work_item`: `https://github.com/YuChia-Wei/ai-collaboration-framework/issues/245`
- `subject_base`: `origin/main@4be33ff90de061dc1db221f60e57ff6130cab54a`
- `base_drift_from_handoff`: `none`

## Objective And Scope

- Problem statement: Current tracked guidance, configuration, snapshots, validators, and source dispositions still describe `.dev/backlog` and `ROADMAP.md` as current source-repository work-management or planning authority after GitHub Issues and Project #3 became authoritative.
- Authorized remediation scope: Implement Issue #245's authority boundary; freeze local backlog and roadmap as historical or legacy-compatibility evidence; relocate active source GitHub provider policy to one non-backlog canonical owner; retire mutable current-snapshot claims; update active consumers, validators, tests, routing, documentation, and source dispositions; preserve v0.5.0-v0.9.0 `planning.backlog_refs`; preserve v0.10.0+ online-Issue release scope.
- Exclusions: No physical deletion or bulk move of legacy items, roadmap history, workflows, assessments, or release records; no portable downstream work-item binding redesign; no provider bulk mutation, push, pull request, merge, Issue closure, Project completion, release allocation, tag, Release, asset, package-byte, or archive-name mutation.
- Completion criteria: Every Issue #245 acceptance criterion is directly verified at an immutable exact head; long-running aggregate validation is delivered by one schema-valid delegated terminal report; an independent exact-head audit has no unresolved P1-P3 finding; workflow and commit evidence are durable and the branch is clean.

## Authority Baseline

- Live GitHub Issues own source-repository candidate, approved, authorized, in-progress, and completed work-item state.
- Live GitHub Project #3 owns current priority, status, owner-review, target-release, and published-in views.
- Repository workflows own execution and validation evidence; provider state does not authorize execution.
- Integrated `main` owns repository-integrated truth; branch work is not yet integrated truth.
- Repository backlog, roadmap, planning files, and point-in-time provider receipts are historical or legacy-compatibility evidence only.
- Ordinary deterministic validation must not require ambient GitHub credentials; current-provider-state claims require explicit live read-back.

## Artifact Contract

- Baseline evidence: live Issue #245 read-back at `2026-08-24T20:00:00+08:00`, `origin/main@4be33ff90de061dc1db221f60e57ff6130cab54a`, and current tracked files reopened during inventory.
- Remediation report: `.dev/workflows/2026-08-24-retire-repository-backlog-authority/reports/remediation-report.md`
- Verification assessment: allocated under `.dev/assessments/` by the independent `ai-context-auditor` at the immutable implementation head.
- Tasks: `.dev/workflows/2026-08-24-retire-repository-backlog-authority/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| GOV012-F001 active local backlog/roadmap authority claims | P1 | ai-context-governance | remediate | GOV012-001 | active-surface scan plus source-governance tests |
| GOV012-F002 active GitHub policy is owned below retired backlog boundary | P1 | ai-context-governance | relocate with one canonical owner | GOV012-001 | consumer parity and retired-path fail-closed tests |
| GOV012-F003 mutable Project snapshot is presented as current truth | P2 | ai-context-governance | retire current claim; retain point-in-time evidence where valid | GOV012-001 | snapshot/disposition validation |
| GOV012-F004 prospective freeze can conflict with legacy v0.5.0-v0.9.0 backlog references | P1 | ai-context-governance | split prospective enforcement from legacy compatibility | GOV012-001 | legacy and new-work suites run separately |
| GOV012-F005 exact-head aggregate and independent verification are required | P1 | ai-context-governance / ai-context-auditor | validate and audit | GOV012-VAL-001 | delegated matrix report plus verification assessment |

## Stages And Checkpoints

1. Bootstrap and direct-evidence inventory on the dedicated branch.
2. Implement the authority freeze, canonical provider-policy relocation, active-consumer updates, and prospective/legacy validation split.
3. Run focused validation and create an immutable implementation commit with a clean worktree.
4. Delegate any aggregate/full matrix meeting the long-running gate through one validated dispatch/completion envelope and one completion route.
5. Obtain an independent exact-head read-only audit; repair and repeat against a new immutable head if required.
6. Reconcile evidence, complete workflow/task state, validate commit range, and create the final durable local commit.

## Low-Task Proportionality

Two substantive tasks are retained because the implementation boundary and the immutable-head validation/audit boundary have different mutation permissions, recovery semantics, and evidence owners. The workflow uniquely preserves source-of-truth relocation, legacy release compatibility, external validation transport, independent verification, and cross-conversation resume state that Issue and commit metadata alone cannot safely reconstruct.

## Resume Checkpoint

- Last completed action: The fresh audit of pushed PR head `0e4e0c0859f639c4c10cf28bcd218f43625cb833` failed on stale terminal-evidence counts and a superseded handoff exclusion; implementation and authority surfaces were unchanged.
- Current task: complete
- Exact next action: Commit and push the terminal-evidence-only correction, update the live PR body to exact declaration parity, then obtain a new exact-head independent audit, required hosted checks, source audit receipt, and live merge admission before integration.
- Validation already completed: focused authority/legacy/prospective gates, source/workflow/assessment governance, terminal closure, release compatibility, packaging boundary, a retained failed sandbox aggregate, the passing host-context aggregate, and a passing independent exact-head audit.
- Git state: the terminal-evidence correction is uncommitted on `codex/2026-08-24-retire-repository-backlog-authority`; the failed audit of `0e4e0c0859f639c4c10cf28bcd218f43625cb833` cannot admit the corrected head.
- Branch history and checkpoint handoffs: segment 1 is pushed through `0e4e0c0859f639c4c10cf28bcd218f43625cb833`; draft PR #247 targets unchanged `main@4be33ff90de061dc1db221f60e57ff6130cab54a`.
- Blockers or unresolved decisions: none; `.dev/standards/` is the selected single active source policy owner and `.dev/backlog/` is frozen historical evidence.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-24-retire-repository-backlog-authority` | `main@4be33ff90de061dc1db221f60e57ff6130cab54a` | audited implementation | `ba7c159a2d8fd58291ddc1e92036cb82acd23fb6` | local only | `2026-08-25T00:35:25+08:00` | Exact-head aggregate and independent audit passed; terminal evidence-only closeout follows. | Hand the local branch to the owner; do not infer push, PR, merge, Issue, Project, or release action. |
| 1 | `codex/2026-08-24-retire-repository-backlog-authority` | `main@4be33ff90de061dc1db221f60e57ff6130cab54a` | push and PR declaration | `01f90ab4b75b19d95b234ef1d0a767dcf45f81e6` | `origin/codex/2026-08-24-retire-repository-backlog-authority`, PR #247 | `2026-08-25T07:09:47+08:00` | Owner authorized terminal delivery; the declaration intentionally advances the head after initial push. | Push the declaration commit, audit that exact head, pass hosted checks, capture admission, then merge with merge-commit topology. |
| 1 | `codex/2026-08-24-retire-repository-backlog-authority` | `main@4be33ff90de061dc1db221f60e57ff6130cab54a` | terminal evidence audit reroute | `0e4e0c0859f639c4c10cf28bcd218f43625cb833` | PR #247 | `2026-08-25T07:18:10+08:00` | Fresh audit found stale counts and a superseded handoff exclusion; implementation surfaces were unchanged. | Commit and push the terminal-evidence-only correction, update the live PR body, then audit the new exact head. |
