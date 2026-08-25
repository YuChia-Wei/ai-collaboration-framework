# PERF-002 Package-Apply Git Snapshot Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-25-package-apply-git-snapshot`
- `plan_id`: `development-plan-2026-08-25-package-apply-git-snapshot`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-25-package-apply-git-snapshot`
- `base_branch`: `main@1326f827f61de8eebeef30748dcc82ffa7dd3764`
- `branch_segment`: `1`
- `status`: `completed`
- `created_at`: `2026-08-25T14:52:56+08:00`
- `updated_at`: `2026-08-26T00:10:35+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-25-package-apply-git-snapshot/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-25-package-apply-git-snapshot/`

## Development Objective

- Outcome: satisfy GitHub Issue #251 by replacing per-path target Git subprocess inspection with phase-bounded snapshots while preserving fail-closed package-apply and journal-v5 semantics.
- Lifecycle entry: approved implementation, focused validation, immutable local commit, long-running delegation when applicable, exact-head independent audit, and parent integration-decision handoff.
- Authorization: owner instruction relayed by parent orchestration thread on 2026-08-25 authorized local implementation, workflow artifacts, focused validation, long-running delegation, exact-head audit, and durable local commits. On 2026-08-25 the owner separately authorized push, PR, merge, and Issue #251 closure.
- Provider boundary: manual Project-field mutation, release allocation, tag, Release, and publication remain unauthorized. Terminal-close relies on provider automation plus read-back for Project `Done`; stop if reconciliation does not prove it.
- Non-goals: #250 identity migration, #252 lane split, #249 evidence reuse policy, #253 agent guardrails, CLI/registry/installer work, and any v0.14.0-or-earlier published mutation.

## Authority And Preflight

- Live Issue #251: OPEN, labels `bug`, `scope:framework`, `created-by:codex`, no comments, Project #3 status `Inbox`; Issue body is the scope contract.
- Related live state: #239 is CLOSED/Done and owns journal-v5 durability; #246 owns only explicit disposable-fixture acceleration and excludes durability/platform semantics.
- Fresh base: successful `git fetch origin main --prune` retained `origin/main@1326f827f61de8eebeef30748dcc82ffa7dd3764`; management checkout was clean `main` before worktree creation.
- Stable preflight fingerprint `remote-ref-not-found:codex/2026-08-25-v015-public-identity`: two equivalent fetch command failures were deduplicated, parent clarified the branch is intentionally local-only, and no further retry is allowed. Read-only evidence is taken from local branch/worktree `issue-250@2497597b17a00a7bebcee36c4ae0fb3a97a977a2`.
- Effective rules: framework-source packet resolved at the base commit with `loaded_rule_ids=[AICTX-EVIDENCE-001]`, packet digest `46b000d161c18ee99c76047cc7c8304d5d46bcd4b291840904733fcaae991722`.
- Code discovery: a full worktree-bound Codebase Memory index is used only as an accelerator; tracked files, Git, and repository validators remain authoritative.

## Development Stages

### PERF-002 implementation and verification

- Capability: `implementation`
- Owner skill: `slice-implementer`
- Intent/mode: behavior-preserving performance refactor, `generic`, no remediation overlay.
- Scope: target Git snapshot lifecycle, consumers, deterministic process/byte/duration instrumentation, regression fixtures, benchmarks, and compatible workflow evidence.
- Validation: focused planner/apply/journal/resume/rollback/crash/retained-origin tests; same-commit three-run benchmark with cold/warm conditions separated; independent read-only exact-head audit.
- Commit checkpoint: one coherent validated implementation commit, followed only by evidence/workflow commit if required; every final mutation invalidates prior exact-head audit.

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | approved | Parent delegation records owner authorization on 2026-08-25; GitHub Issue #251 body supplies scope | none |

## Test Execution Contract

- Provider: target-owned Python test entrypoints and repository validators.
- Working directory: isolated Issue #251 worktree.
- Default selected levels: unit and integration.
- Long-running commands: delegate after a clean immutable commit when expected or observed duration is at least 120 seconds.
- Durability/platform suites remain on real storage and must not consume `AI_CONTEXT_TEST_TMP_ROOT`.

## Spec Compliance Selection

- Selected: no.
- Outcome: not-applicable; no problem-frame compliance contract was selected.

## Progress And Handoff

- Current stage: source implementation, workflow task, retained validation, retrospective, and PR #255 terminal-close declaration are complete. The first PR-bound source-closeout head `edb50e36154ac53391ff0d7a773126a2d8b56a53` was rejected by the fresh independent audit because the live PR body carried two trailing LF bytes that the `|-` declaration omitted; the declaration now preserves those bytes exactly. The same hosted head passed Windows prerequisite, Ubuntu prerequisite, read-only governance, and candidate-build checks, but its Ubuntu PR profile exposed one Linux-only package-apply regression: Git interpreted a pathspec below a symlink before the framework emitted its canonical symlink-boundary failure. Snapshot admission now rejects symlink/reparse boundaries before any Git pathspec interpretation. A new exact-head audit and hosted rerun are required; the retained multi-hour benchmark is not repeated because the repair adds only O(paths) filesystem boundary checks and no Git subprocess.
- Current bounded counts: direct and real later-hop plan `24` Git subprocesses (two complete 12-process admissions), apply `12`; both are payload-independent. The increase from the retained benchmark's `22/11/22` is one closing config read-back per snapshot, a constant safety cost. Successful apply performs `4` full worktree inventory scans independent of operation count, while per-operation checks inspect only snapshotted candidate paths.
- Long-running gate: the terminal task bound to `13a33cc44825f8da10674e0294b38edbf7159053` passed package-apply 104 tests (1 Windows symlink-privilege skip), multi-hop 31 tests, and the retained 631-record cold-first plus three-warm-run benchmark in 4865.614824 seconds. The historical benchmark remains valid evidence for eliminating per-path amplification (`22/11` at that exact head). Later safety repairs are covered by deterministic current-head `24/12/24` process-count and focused semantic tests; the expensive legacy baseline is retained rather than repeated because neither the legacy emulation, fixture/profile, host/storage, payload, nor claimed performance path changed. Earlier blocked, failed, passed-on-superseded-head, and interrupted receipts remain retained without rewriting.
- Durable lessons: [`reports/execution-retrospective.md`](reports/execution-retrospective.md) preserves the execution history, audit failures, benchmark-reuse recommendation, and the explicit reason this local validation record is not an ADR.
- Delivery PR: draft PR #255, with exact body declared by `evidence/terminal-issue-closure-pr-255.yaml`; selected topology is merge commit because the branch is a durable multi-commit validation/audit/repair unit.
- External terminal gates: final exact-head audit of the immutable repaired source-closeout head, fresh hosted Ubuntu/Windows checks including Linux package-apply and multi-hop execution, strict source audit receipt, live merge admission, integration, and post-merge Issue/Project read-back.
- Completion claim boundary: `completed` means source workflow completion only. PR #255 remains unmerged and Issue #251 remains open until the external terminal gates pass.
