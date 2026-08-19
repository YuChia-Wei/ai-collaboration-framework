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
- `updated_at`: `2026-08-20T00:04:39+08:00`
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

- Last completed action: fresh independent audit of `5dca98d3da1a29b6d088c4bd44ce7161d5e901f2` returned FAIL for comment-masked change requests, incomplete provider pagination, and unsafe filesystem capture; earlier provider ownership/live verification and closure protections remained fixed.
- Current task: `GOV008-001-contract-implementation`.
- Exact next action: commit and push the decisive-review/pagination/stdout-capture repair, then obtain another fresh independent exact-head audit before hosted admission or merge.
- Validation already completed: current repair passes closure 38/38 and provider 20/20 plus repository/workflow/source-governance/AI-context and diff checks; the preceding head's two hosted failures remain preserved.
- Git state: draft PR #220 exists at pushed head `5dca98d3da1a29b6d088c4bd44ce7161d5e901f2`; four failed audits are preserved and the bounded fourth repair is uncommitted.
- Branch history and checkpoint handoffs: none yet.
- Blockers or unresolved decisions: independent fixed-head audit, hosted checks, PR A integration, and provider read-back remain pending.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | draft PR bootstrap | `8ae7ec75cbaf43c5b22b574006f182a2586bc33f` | PR #220 | `2026-08-19T23:31:54+08:00` | obtain the provider-assigned PR number required for exact event binding; this is not review or hosted success | bind #220, push the new head, and obtain fresh audit |
| 2 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `40f0821b3443b79a5e9f4400dc77afc8e509f012` | PR #220 | `2026-08-19T23:39:59+08:00` | preserve the optional/self-referential merge-admission finding and stale checkpoint evidence | implement non-mutating provider admission overlay, validate, commit, push, and re-audit |
| 3 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `1a54e94a3b07fcc1771b38484b594b457de904d8` | PR #220 | `2026-08-19T23:53:01+08:00` | preserve stage-downgrade and self-authenticating provider snapshot findings plus hosted failures | require declaration-only overlays and live GitHub verification against provider-owned contexts, validate, commit, push, and re-audit |
| 4 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `5dca98d3da1a29b6d088c4bd44ce7161d5e901f2` | PR #220 | `2026-08-20T00:04:39+08:00` | preserve effective-review, pagination-completeness, and capture-path safety findings plus hosted failures | enforce decisive review state, complete safe pagination, and stdout-only capture, then validate, commit, push, and re-audit |
