# GOV-008 Terminal And Deferred GitHub Issue Closure

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-19-gov-008-terminal-issue-closure`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-19-gov-008-terminal-issue-closure`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure`
- `created_at`: `2026-08-19T23:09:17+08:00`
- `updated_at`: `2026-08-19T23:28:39+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the source GitHub provider prevents premature Issue closure but has no symmetric terminal gate, so an accepted final delivery can integrate while its authoritative Issue and Project state remain open.
- Authorized remediation scope: Issue #212; the source GitHub provider contract, PR template, deterministic validator and focused GWT fixtures, source-governance check registration, downstream exclusion, and directly affected Git/workflow closeout guidance.
- Authorization source: the repository owner explicitly authorized implementation, validation, push, independent review, merge, and terminal continuation for #212, then explicitly approved the multi-surface governance and packaging patch after its risk was disclosed.
- Exclusions: downstream GitHub keyword requirements; historical Issue/PR/workflow rewrites; releases, tags, publication, nightly activation, and implementation of Issues #203 or #205-#208/#213.
- Completion criteria: PR A integrates the two-mode contract using deferred self-hosting semantics and #212 remains open; a continuation PR then validates terminal-close for #212 and #204, integrates at an independently reviewed exact head, and provider read-back proves both Issues completed and Project cards Done.
- Workflow justification: the two-PR self-hosting boundary preserves an independently resumable integration checkpoint that no Issue, single commit, or conversation can represent alone.

## Artifact Contract

- Remediation report: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/reports/remediation-report.md`
- Closure evidence: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/evidence/terminal-issue-closure-pr-a.yaml`
- Tasks: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `GOV-008-CLOSURE-ASYMMETRY` | HIGH | `ai-context-governance` | implement exactly `terminal-close` and `deferred`, then self-host through two sequential PRs | `GOV008-001-contract-implementation`, `GOV008-002-terminal-continuation` | focused GWT, source governance, downstream exclusion, exact-head audit, hosted checks, provider read-back |

## Stages And Checkpoints

1. Completed locally: implement the canonical source-only contract, template, validator, fixtures, guidance, distribution boundary, and PR A deferred evidence.
2. In progress: remediate the failed exact-head audit of `4fe042f8a1d0483b311b327a22fa0b7e320300c4`, then create a corrective commit and obtain a fresh audit.
3. Pending: merge PR A and read back that #212 remains open by design.
4. Pending: continue from refreshed `main`, terminally reconcile #212 and #204, and complete provider read-back.

## Self-Hosting PR A Disposition

- Issue: `#212`
- Mode: `deferred`
- Reference: `Refs #212`
- `closure_deferred_reason`: `self-hosting contract must integrate before it can govern its own terminal closeout`
- Next terminal gate: `continuation closeout PR after PR A merges`
- Closing keyword: forbidden for PR A.

## Validation Strategy

- Run the terminal/deferred validator and all focused positive/negative GWT fixtures.
- Run GitHub provider, repository configuration, entrypoint, shell-asset, workflow-artifact, source-governance, AI-context, and distribution/package boundary validation selected by the changed surfaces.
- Bind independent review and hosted checks to one clean immutable commit. Any mutation invalidates the prior audit.
- Treat failure, cancellation, timeout, head drift, review block, or missing/mismatched provider read-back as nonterminal.

## Resume Checkpoint

- Last completed action: independent audit of `4fe042f8a1d0483b311b327a22fa0b7e320300c4` returned FAIL for current-PR binding, inline closing-keyword detection, head-bound review/check completeness, and stale workflow truth; the bounded repair now separates declaration, merge admission, and reconciliation while keeping exactly two closure modes.
- Current task: `GOV008-001-contract-implementation`.
- Exact next action: finish repair validation, create a corrective commit, then push only far enough to open PR A and bind its assigned PR number before the fresh final audit.
- Validation already completed: original focused suites passed; repaired closure suite passes 23/23 and provider 20/20, including inline/qualified closing keywords, PR/head mismatch, review/check head drift, and required-context completeness.
- Git state: dedicated branch at failed audited commit `4fe042f8a1d0483b311b327a22fa0b7e320300c4` with bounded uncommitted audit repairs; nothing pushed.
- Branch history and checkpoint handoffs: none yet.
- Blockers or unresolved decisions: independent fixed-head audit, hosted checks, PR A integration, and provider read-back remain pending.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed exact-head audit | `4fe042f8a1d0483b311b327a22fa0b7e320300c4` | not pushed | `2026-08-19T23:28:39+08:00` | preserve four blocking validator/workflow findings before any transport | complete bounded repair, commit, then open draft PR for number binding |
