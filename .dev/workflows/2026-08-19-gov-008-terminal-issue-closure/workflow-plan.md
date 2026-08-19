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
- `branch`: `codex/2026-08-19-gov-008-terminal-issue-closure-cont-02`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure`
- `created_at`: `2026-08-19T23:09:17+08:00`
- `updated_at`: `2026-08-20T03:34:43+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: the source GitHub provider prevents premature Issue closure but has no symmetric terminal gate, so an accepted final delivery can integrate while its authoritative Issue and Project state remain open.
- Authorized remediation scope: Issue #212; the source GitHub provider contract, PR template, deterministic validator and focused GWT fixtures, source-governance check registration, downstream exclusion, and directly affected Git/workflow closeout guidance.
- Authorization source: the repository owner explicitly authorized implementation, validation, push, independent review, merge, and terminal continuation for #212, then explicitly approved the multi-surface governance and packaging patch after its risk was disclosed.
- Exclusions: downstream GitHub keyword requirements; historical Issue/PR/workflow rewrites; releases, tags, publication, nightly activation, and implementation of Issues #203 or #205-#208/#213.
- Completion criteria: PR A integrates the two-mode contract using deferred self-hosting semantics and #212 remains open; a continuation PR then validates terminal-close for #212 and #204, binds audit/check evidence to its admitted head, permits any supported integration topology, and provider read-back proves both Issues completed and Project cards Done without a post-merge source repair commit.
- Workflow justification: the two-PR self-hosting boundary preserves an independently resumable integration checkpoint that no Issue, single commit, or conversation can represent alone.

## Artifact Contract

- Remediation report: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/reports/remediation-report.md`
- Closure evidence: PR A bootstrap read-back and the continuation declaration under `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/evidence/`
- Tasks: `.dev/workflows/2026-08-19-gov-008-terminal-issue-closure/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `GOV-008-CLOSURE-ASYMMETRY` | HIGH | `ai-context-governance` | implement exactly `terminal-close` and `deferred`, then self-host through two sequential PRs | `GOV008-001-contract-implementation`, `GOV008-002-terminal-continuation` | focused GWT, source governance, downstream exclusion, exact-head audit, hosted checks, provider read-back |

## Stages And Checkpoints

1. Completed locally: implement the canonical source-only contract, template, validator, fixtures, guidance, distribution boundary, and PR A deferred evidence.
2. Completed: remediate all nine failed audits; fresh audit of final PR A head `f8cffd33af799b6b92f748c99e82ff9bd344fbb7` passed and five required hosted checks succeeded.
3. Completed: PR #220 merged with `--no-ff` as `6a878d65565920271047f42b25b39f05afe68592`; provider read-back kept #212 open and its Project status `Inbox` by design.
4. In progress: on refreshed continuation branch, encode the owner's single-maintainer source decision, preserve target-owned downstream policy, separate admitted head from integration commit, and terminally reconcile #212 and #204.

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
- Bind independent review and hosted checks to one admitted PR head. Any pre-integration mutation invalidates the prior audit, but fast-forward, rebase, squash, and merge-commit integration remain valid and record their actual provider integration commit separately.
- Treat failure, cancellation, timeout, head drift, review block, or missing/mismatched provider read-back as nonterminal.

## Resume Checkpoint

- Last completed action: bound PR #221 in `06f32f785cad287e838d1cd93840a3ab20942b9d`; the fresh exact-head audit failed only because this resume checkpoint still described that completed binding as pending.
- Current task: `GOV008-002-terminal-continuation`, with the remaining prospective contract refinement retained in `GOV008-001` until fresh verification.
- Exact next action: ensure the commit containing this reconciliation is pushed, resolve that exact PR #221 head from the provider, and request a new read-only independent audit before any receipt or admission.
- Validation already completed: continuation terminal closure 54/54, GitHub provider 20/20, repository configuration fixtures 14/14, and all affected workflow/source/distribution validators; the failed `06f32f78` audit independently reran closure 54/54, provider 20/20, static records, and workflow artifacts.
- Git state: branch `codex/2026-08-19-gov-008-terminal-issue-closure-cont-02` starts from merge commit `6a878d65`; draft PR #221 is open and provider head `06f32f78` was the failed audit subject. The commit containing this checkpoint intentionally does not self-embed its own SHA; provider read-back selects the next exact audit subject after push.
- Branch history and checkpoint handoffs: PR A is the retained merge checkpoint; segment 2 is the terminal continuation.
- Blockers or unresolved decisions: the failed `06f32f78` audit is non-passing; a new exact-head audit receipt, hosted read-back for that new head, live admission, owner-selected integration topology, and post-merge provider read-back remain pending. No second GitHub identity is required.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | draft PR bootstrap | `8ae7ec75cbaf43c5b22b574006f182a2586bc33f` | PR #220 | `2026-08-19T23:31:54+08:00` | obtain the provider-assigned PR number required for exact event binding; this is not review or hosted success | bind #220, push the new head, and obtain fresh audit |
| 2 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `40f0821b3443b79a5e9f4400dc77afc8e509f012` | PR #220 | `2026-08-19T23:39:59+08:00` | preserve the optional/self-referential merge-admission finding and stale checkpoint evidence | implement non-mutating provider admission overlay, validate, commit, push, and re-audit |
| 3 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `1a54e94a3b07fcc1771b38484b594b457de904d8` | PR #220 | `2026-08-19T23:53:01+08:00` | preserve stage-downgrade and self-authenticating provider snapshot findings plus hosted failures | require declaration-only overlays and live GitHub verification against provider-owned contexts, validate, commit, push, and re-audit |
| 4 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `5dca98d3da1a29b6d088c4bd44ce7161d5e901f2` | PR #220 | `2026-08-20T00:04:39+08:00` | preserve effective-review, pagination-completeness, and capture-path safety findings plus hosted failures | enforce decisive review state, complete safe pagination, and stdout-only capture, then validate, commit, push, and re-audit |
| 5 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `2f93ecb18aaa5e823f0b40ab2f1ccdcf472e8ac1` | PR #220 | `2026-08-20T00:10:45+08:00` | preserve malformed/short pagination and non-replayable capture findings | fail closed on Link/total mismatches, separate YAML/status streams, validate, commit, push, and re-audit |
| 6 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `11f0914d3125e9c275b21a7bf3ecbd0209e62ff7` | PR #220 | `2026-08-20T00:15:27+08:00` | preserve duplicate-next page-skipping finding | reject duplicate relations, validate, commit, push, and re-audit |
| 7 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `7bdca9da523e39ae77af2d108541c2ae539be8d4` | PR #220 | `2026-08-20T00:25:30+08:00` | preserve Issue partition, commit-message, hosted checkout/test, and relation-token findings | implement bounded repair, validate, commit, push, and re-audit |
| 8 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `91826703df14d45eae6a8bcaf2d506f3c6f1c86a` | PR #220 | `2026-08-20T00:34:55+08:00` | preserve stale/fabricated event metadata admission finding while retaining all earlier repairs | live-read and bind PR number/base/head/body, rerun edited-body checks, validate, commit, push, and re-audit |
| 9 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | failed fresh exact-head audit | `11ec97d13718d999b11a05cae281603263876c01` | PR #220 | `2026-08-20T00:42:58+08:00` | preserve omitted event-repository binding finding while retaining live PR metadata and all earlier repairs | bind event top-level/base repository to live governed repository, validate, commit, push, and re-audit |
| 10 | `codex/2026-08-19-gov-008-terminal-issue-closure` | `main@174eb835058dff40f67624df682d7d531ee9949b` | merged self-hosting checkpoint | `f8cffd33af799b6b92f748c99e82ff9bd344fbb7` | PR #220 / `main@6a878d65565920271047f42b25b39f05afe68592` | `2026-08-20T03:09:54+08:00` | final audit passed, five checks succeeded, and owner used `--no-ff`; #212 remained open/Inbox | create segment 2 from refreshed main and terminally reconcile #212/#204 |
| 11 | `codex/2026-08-19-gov-008-terminal-issue-closure-cont-02` | `main@6a878d65565920271047f42b25b39f05afe68592` | draft PR bootstrap | `0b6e797a2e55f5be4e5db234a3dbe15d2b7f8b26` | PR #221 | `2026-08-20T03:45:44+08:00` | obtain the provider-assigned continuation PR number while preserving topology-neutral SHA evidence | bind #221, push the provider-bound head, then audit and admit that exact head |
| 12 | `codex/2026-08-19-gov-008-terminal-issue-closure-cont-02` | `main@6a878d65565920271047f42b25b39f05afe68592` | failed fresh exact-head audit | `06f32f785cad287e838d1cd93840a3ab20942b9d` | PR #221 | `2026-08-20T03:52:04+08:00` | preserve the stale resume-checkpoint finding; receipt safety, Issue partition, topology separation, tests, and five hosted contexts otherwise passed | reconcile durable checkpoint truth, push, provider-read the containing head, and re-audit without self-embedding that commit SHA |
