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
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure`
- `created_at`: `2026-08-19T23:09:17+08:00`
- `updated_at`: `2026-08-19T23:18:20+08:00`
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
2. In progress: commit and obtain fresh independent exact-head review; then push and require hosted success at that exact head.
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

- Last completed action: the coherent PR A patch passed focused terminal/provider/config/workflow/shell/source-governance/entrypoint/registry/dependency/distribution/AI-context validation; sandbox Temp failures were preserved and the same affected temp-fixture suites passed on the host.
- Current task: `GOV008-001-contract-implementation`.
- Exact next action: create the durable validated implementation commit, freeze that exact head for independent audit, and do not push until the audit disposition is PASS.
- Validation already completed: terminal closure 18/18; GitHub provider 20/20; repository config 14/14; entrypoint 7/7; source entrypoint 3/3; registry 6/6; dependency 19/19; prerequisite 14/14; brand-neutral distribution 2/2; workflow artifact, shell asset, repository config, source governance, AI-context, Bash syntax, and diff checks passed.
- Git state: dedicated branch with authorized in-progress changes; no GOV-008 commit or push yet.
- Branch history and checkpoint handoffs: none yet.
- Blockers or unresolved decisions: independent fixed-head audit, hosted checks, PR A integration, and provider read-back remain pending.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | local workflow bootstrap | pending | not pushed | `2026-08-19T23:09:17+08:00` | preserve the required two-PR self-hosting boundary | complete and validate PR A |
