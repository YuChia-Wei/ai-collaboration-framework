# VAL-007 Terminal Validation Supervision And Evidence Remediation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-15-val-007-terminal-validation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-15-val-007-terminal-validation`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `hosted-ci-gate`
- `artifact_root`: `.dev/workflows/2026-08-15-val-007-terminal-validation`
- `created_at`: `2026-08-15T13:39:00+08:00`
- `updated_at`: `2026-08-15T18:55:09+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: terminal validation currently supervises only the direct process, does not bind an immutable repository identity before and after execution, leaves nested subprocesses unbounded, and cannot prove that retained logs and evidence remain sealed after timeout or cancellation. A moving checkout or surviving descendant can therefore invalidate an apparently terminal result.
- Authorized remediation scope: GitHub Issue #204, `ASM-20260810-005#VALSNAP-001`, `#VALTIME-001`, `#VALTEST-001`, `#VALCOST-001`, `ASM-20260813-001#VALRUN-001`, DS-16, and the owner-approved delivery table from 2026-08-15. Implement complete process-tree supervision, immutable pre/post snapshot admission, bounded nested validation and cleanup, sealed command/evidence artifacts, and nightly-full readiness without executing nightly-full.
- Authorization source: the owner confirmed the eight-step plan and authorized starting #204 as an independent PR. Repository implementation and focused validation are authorized; Project/milestone mutation, Issue closure, push, PR creation, merge, tag, release, and publication remain separate decisions.
- Normative truth: live Issue #204 acceptance criteria, the two baseline assessments, the long-running validation gate in `AGENTS.md`, the validation profile registry, and the existing external-task terminal receipt contract.
- Exclusions: Issue #215 registry-count improvements; Issues #203 and #205-#208; Issue #149 runtime/model comparison; changes to #194 external-task delegation semantics; an actual `release`, `nightly-full`, full-matrix, or at-least-120-second validation run; downstream repositories; hosted publication.
- Completion criteria: the repository-relative snapshot defect exposed at hosted branch head `a60dcac687b07c8f1df95b43162474e05dd4f29d` is locally remediated and independently reviewed. The original process-tree, drift, evidence, cleanup, focused fixture, and hard-disabled nightly-readiness criteria remain satisfied. Workflow completion remains gated on a durable corrective commit and passing required hosted checks at that exact pushed head.

## Artifact Contract

- Baseline assessments: `.dev/assessments/ASM-20260810-005/assessment.yaml` and `.dev/assessments/ASM-20260813-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-15-val-007-terminal-validation/reports/remediation-report.md`
- Pre-remediation coverage inventory: `.dev/workflows/2026-08-15-val-007-terminal-validation/reports/coverage-inventory.md`
- Verification evidence: independent fixed-head review of clean `59dae454bcfe55fed9873eac834449583750c4a5` found no P0/P1 issue; no standalone assessment was required for this bounded workflow
- Tasks: `.dev/workflows/2026-08-15-val-007-terminal-validation/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260810-005#VALSNAP-001`, `ASM-20260813-001#VALRUN-001` | HIGH | `ai-context-governance` | bind clean terminal admission and exact pre/post identity to the runner and evidence | `VAL007-001-supervision-snapshot` | snapshot drift, remaining-check abort, exact identity assertions |
| `ASM-20260810-005#VALTIME-001` | HIGH | `ai-context-governance` | supervise and prove termination of the complete process tree before sealing output | `VAL007-001-supervision-snapshot` | Windows/POSIX child-grandchild delayed-writer fixtures, timeout and cancellation |
| `ASM-20260810-005#VALTEST-001`, DS-16 | MEDIUM | `ai-context-governance` | bound nested validators, surface cleanup failure, and measure duplicate fixture coverage before removal | `VAL007-002-evidence-cleanup` | deterministic nested timeout, cleanup diagnostics, inventory evidence |
| `ASM-20260810-005#VALCOST-001` and nightly cluster | MEDIUM | `ai-context-governance` | retain one terminal chain and establish scheduled-runner readiness without executing it | `VAL007-003-nightly-readiness` | workflow contract checks only; nightly-full remains prohibited |

## Source-Repository Action Routing

- `bdd-gwt-test-designer`: evaluated but not selected for execution. Its action requires a freshness-verified live target effective-rule packet; this framework source repository is prohibited from creating one. The acceptance scenarios below are maintained directly by the governance owner and no resolver success is fabricated.
- `slice-implementer`: a delegated follow-up attempted its required effective-rule resolution and stopped without mutation because `.dev/ai-context/provenance.yaml` is intentionally absent in this source repository. Existing Issue #204 governance authority then owned the bounded direct remediation; no framework-default rule packet was fabricated.
- `software-development-orchestrator`: coordinates focused test execution, independent review, durable commit checkpoints, and the later immutable external-task gate without taking governance ownership.
- Runtime evidence: task records persist `gpt-5.6-sol` with `max` reasoning effort. The user-selected Ultra execution mode is a runtime orchestration mode and is not substituted for those schema fields.
- `role_execution`: not applicable because no action-skill execution is selected; the read-only explorer tasks provide inventory evidence only and do not transfer implementation ownership.

## Governed GWT Acceptance Matrix

| Scenario | Given | When | Then | Level |
| --- | --- | --- | --- | --- |
| `VAL007-GWT-001` | a POSIX validator starts a child and delayed-writing grandchild | the check times out | the entire process group terminates before return and the sealed log never changes afterward | focused integration |
| `VAL007-GWT-002` | a Windows validator starts a child and delayed-writing grandchild | the check times out or is cancelled | the supervised process tree terminates before return and later writes are impossible | focused integration |
| `VAL007-GWT-003` | terminal-profile admission records a clean immutable snapshot | HEAD, tree, branch/detached state, merge state, or status changes before finalization | the current check and remaining chain fail closed with explicit drift evidence | focused integration |
| `VAL007-GWT-004` | one supervised check completes or is terminated | evidence is finalized | exact argv, cwd, commit, duration, outcome, cleanup result, log digest, and retained artifact references are bound atomically | unit plus focused integration |
| `VAL007-GWT-005` | a supervised process cannot be fully cleaned up | the timeout or cancellation path returns | cleanup failure is visible and the check cannot be classified as passed | focused integration |
| `VAL007-GWT-006` | immutable-history validators invoke nested processes | a nested command exceeds its bound | the nested process is terminated and the outer validator reports a bounded non-pass | unit plus focused integration |
| `VAL007-GWT-007` | synthetic repositories and cleanup helpers are instrumented | duplicate coverage and cleanup behavior are reviewed | unique coverage is retained, redundancy is recorded before removal, and cleanup errors are deterministic | contract test |
| `VAL007-GWT-008` | nightly readiness is declared | workflow contracts are validated | concurrency is bounded, artifact paths are deterministic, cancellation is fail-closed, ownership is explicit, and nightly-full is not run | workflow contract |
| `VAL007-GWT-009` | timeout, interruption, missing terminal evidence, or blocked execution occurs | summary/evidence is produced | none of those states is reported or cached as passed | unit plus contract test |

## Stages And Checkpoints

1. Completed: baseline/live-state read-back, branch isolation, runner/test/nightly inventory, and workflow bootstrap.
2. Completed: process-tree supervisor, immutable admission, sealed result/log artifacts, and Windows/POSIX focused fixtures.
3. Completed: nested timeout, deterministic cleanup, evidence schema/finalization, and duplicate-coverage disposition.
4. Completed: hard-disabled nightly readiness contract and focused repository validation; nightly-full was not executed.
5. Completed locally: durable clean implementation commit `59dae454bcfe55fed9873eac834449583750c4a5`, independent fixed-head review with no P0/P1, and finding reconciliation.
6. Local remediation completed: resolve the repo-relative snapshot through the repository artifact boundary; execute GWT-035 on Windows and Ubuntu; retain event-relative log/result semantics; obtain an independent P0=0/P1=0 review. In progress: create and push the durable correction, then require one exact-head hosted-check watch before merge.

## Validation Strategy

- Run only directly affected unit, contract, shell-syntax, workflow-artifact, and deterministic process-tree fixtures during implementation.
- Do not execute `release`, `nightly-full`, any full matrix, or any command expected or observed to run at least 120 seconds before the owner-approved cumulative #200-#208 validation stage.
- Bind any later long-running command to one clean immutable commit and delegate it through exactly one external task with one validated terminal receipt and an exact callback or single event wait; no polling and no repair.
- Treat timeout, cancellation, interruption, missing evidence, cleanup failure, snapshot drift, and blocked execution as non-passing outcomes.

## Resume Checkpoint

- Last completed action: changed `build_record` to admit `--snapshot` through the repository-root artifact boundary, added supervised GWT-035 using the runner's repo-relative argv, passed Windows GWT-035/009/019 3/3 in 6.942 seconds and Ubuntu-24.04 GWT-035 1/1 in 1.228 seconds, and received an independent P0=0/P1=0 review.
- Current task: `VAL007-001-supervision-snapshot` remains in progress only for durable commit and exact-head hosted-gate evidence.
- Exact next action: commit and push the bounded #204 correction, then use one exact-head hosted-check watch. Stop on any required-check failure or head drift; merge only after every required gate passes.
- Validation already completed: Windows and WSL supervisor modules; bounded evidence GWT groups; selected fail-closed runner batches; workflow and registry contract modules; AST, Bash syntax, YAML/workflow, and diff checks; independent current-diff and fixed-head reviews. The historical GWT-019 stale-message failure and sandbox-blocked attempts remain retained rather than relabeled.
- Git state: branch `codex/2026-08-15-val-007-terminal-validation`; PR #216 is open as draft at `a60dcac687b07c8f1df95b43162474e05dd4f29d`. The first hosted attempt exposed the fixed Ubuntu startup failure; the second exposed the repo-relative finalization defect after every selected validator completed.
- Branch history and checkpoint handoffs: durable implementation boundaries are `254d0d7`, `910944f`, `59dae45`, and CI portability fix `7b4be71`; workflow bootstrap is `0965a2c`, initial closeout is `94f7d9e`.
- Blockers or unresolved decisions: local remediation has no P0/P1 blocker; required hosted gates must still re-observe the fix at the exact pushed head. Issue closure, cumulative external validation, nightly activation, and release remain separate decisions.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-15-val-007-terminal-validation` | `main@76c51574c7b2fdf59e8648eb105570589053ecf0` | local workflow bootstrap | `0965a2cf288c79fe91df3e291806d1bf66e9f8c9` | not pushed | `2026-08-15T13:39:00+08:00` | isolate #204 as its owner-approved independent delivery | implement and validate focused VAL-007 remediation |
| 1 | `codex/2026-08-15-val-007-terminal-validation` | `0965a2cf288c79fe91df3e291806d1bf66e9f8c9` | clean fixed-head implementation review | `59dae454bcfe55fed9873eac834449583750c4a5` | not pushed | `2026-08-15T17:52:54+08:00` | preserve reviewed process-tree, evidence, and disabled-readiness implementation | commit closeout records, then return push/PR decision to owner |
| 1 | `codex/2026-08-15-val-007-terminal-validation` | `94f7d9e911e0f85d5330bc09c6b6c2b110d598a2` | hosted CI portability remediation | `7b4be71e00ef09289b2d17b77c00b23ddcbc3c9c` | PR #216 update pending | `2026-08-15T18:10:52+08:00` | split portable artifact-path declaration from ordered assignment after identical Ubuntu startup failures | commit closeout sync, push, and watch exact-head hosted checks once |
| 1 | `codex/2026-08-15-val-007-terminal-validation` | `a60dcac687b07c8f1df95b43162474e05dd4f29d` | hosted CI finalization remediation | current corrective commit | PR #216 remains draft | `2026-08-15T18:55:09+08:00` | both Ubuntu jobs reached finalization and exposed duplicate evidence-directory prefixing of a repo-relative snapshot ref | local fix and review complete; commit, push, and run one exact-head hosted watch |
