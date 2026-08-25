# PERF-002 Package-Apply Git Snapshot Workflow

## Workflow Metadata

- `workflow_id`: `2026-08-25-package-apply-git-snapshot`
- `plan_id`: `development-plan-2026-08-25-package-apply-git-snapshot`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-25-package-apply-git-snapshot`
- `base_branch`: `main@1326f827f61de8eebeef30748dcc82ffa7dd3764`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-25T14:52:56+08:00`
- `updated_at`: `2026-08-25T22:14:14+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-25-package-apply-git-snapshot/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-25-package-apply-git-snapshot/`

## Development Objective

- Outcome: satisfy GitHub Issue #251 by replacing per-path target Git subprocess inspection with phase-bounded snapshots while preserving fail-closed package-apply and journal-v5 semantics.
- Lifecycle entry: approved implementation, focused validation, immutable local commit, long-running delegation when applicable, exact-head independent audit, and parent integration-decision handoff.
- Authorization: owner instruction relayed by parent orchestration thread on 2026-08-25 authorizes local implementation, workflow artifacts, focused validation, long-running delegation, exact-head audit, and durable local commits.
- Provider boundary: push, PR, merge, Issue/Project mutation, release allocation, tag, Release, and publication are not authorized.
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

- Current stage: implementation and same-commit aggregate validation are complete. Exact-head audits correctly rejected repository-local policy drift at `7a6f20a0`, config-selection drift at `ee55880b`, and dormant include-target drift at `ad0b38a0`. The current repair binds every file-backed effective config origin, dormant include target, and selected/default ignore and attribute file; focused process/config-drift tests and real two-hop validation pass, and a fresh exact-head audit remains.
- Current bounded counts: direct and real later-hop plan `22` Git subprocesses (early admission plus full path snapshot), apply `11`; both are payload-independent. Successful apply performs `4` full worktree inventory scans independent of operation count, while per-operation checks inspect only snapshotted candidate paths.
- Long-running gate: the terminal task bound to `13a33cc44825f8da10674e0294b38edbf7159053` passed package-apply 104 tests (1 Windows symlink-privilege skip), multi-hop 31 tests, and the retained 631-record cold-first plus three-warm-run benchmark in 4865.614824 seconds. Later repairs change only the constant-size Git policy identity set, reuse the existing config/admin subprocesses, and are covered by the deterministic 22/11 process-count matrix plus focused semantic tests; the expensive legacy baseline is retained rather than repeated. Earlier blocked, failed, passed-on-superseded-head, and interrupted receipts remain retained without rewriting.
- Durable lessons: [`reports/execution-retrospective.md`](reports/execution-retrospective.md) preserves the execution history, audit failures, benchmark-reuse recommendation, and the explicit reason this local validation record is not an ADR.
- Parent integration owner: source orchestration thread `01a036af-3b1f-7283-97ab-eb6b7caabf93`.
- Required final handoff: worktree/branch/base/final SHA, clean state, changed files, process counts/timings/benchmarks, test commands/durations/digests, delegated receipt if applicable, exact-head audit, compatibility evidence, residual risks, and excluded provider/release actions.
- Completion claim boundary: report only ready for parent integration decision; do not claim merged or release-ready.
