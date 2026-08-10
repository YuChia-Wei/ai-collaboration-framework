# Terminal Validation Snapshot And Timeout Orchestration Incident

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260810-005`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-10`
- `created_at`: `2026-08-10T23:17:18+08:00`
- `updated_at`: `2026-08-10T23:17:18+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `d39712b3acb2d886dc5541ecc9c93a101f412b60`
- `previous_assessment`: `ASM-20260810-002`
- `workflow_refs`: `2026-08-10-immutable-history-validation`

## Executive Summary

- Overall assessment: The validation runner fails closed on timeout, but terminal evidence can still be produced against a moving shared checkout, and timeout cancellation does not yet prove that descendant processes have stopped. The observed timeout values are also entangled with fixture construction, repeated nested runner execution, concurrent validators, and absent inner subprocess bounds.
- Overall score: `N/A`
- Decision: `remediation-recommended`
- Primary strengths: stable per-check timing and evidence dispositions; timeout is not counted as pass; deterministic fixture assertions; handoff policy already records a fully validated subject commit.
- Primary risks: snapshot-invalid evidence may be mistaken for commit compliance; timeout may leave descendant processes writing to logs; runtime budgets are being asked to compensate for test-architecture cost; an exact packaging command can be rerun redundantly after aggregate coverage.

The key lesson is scheduling and ownership, not polling frequency. Long release or compliance validation is a terminal gate. It should run after implementation, conflict resolution, and integration are complete, against one clean committed candidate in an isolated worktree. Any later commit invalidates that evidence and requires a new terminal run.

## Scope

### Included AI Context Surfaces

- [aggregate runner](../../../.ai/scripts/check-all.sh)
- [validation profile registry](../../../.ai/scripts/validation-profile-registry.sh)
- [aggregate runner contract tests](../../../.ai/scripts/tests/test_fail_closed_validation.py)
- [immutable-history contract tests](../../../.ai/scripts/tests/test_immutable_history_validation.py)
- [immutable-history validator](../../../.ai/scripts/validate-immutable-history.py)
- [workflow handoff policy](../../standards/WORKFLOW-HANDOFF-POLICY.md)
- bounded command, timing, Git-state, and process observations from the 2026-08-10 delegated validation run

### Default Exclusions

- `src/**`
- product tests and implementation trees
- generated and dependency trees

### Additional Exclusions

- implementation of any proposed fix
- changes to timeout values
- online tracker or delivery lifecycle mutation
- rerunning long suites against an unfixed execution model

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and product tests
- Recommended skill: `not-applicable`; the inspected Python and Bash files are AI-context validation surfaces owned by the governance lifecycle

## Methodology And Evidence

### Pass A: Independent Baseline

- Reconstructed the command timeline, exact exit codes, durations, timeout boundaries, test counts, skips, and checkout reflog events.
- Distinguished assertion outcome, orchestration outcome, snapshot integrity, and evidence disposition.
- Inspected timeout process ownership and nested subprocess boundaries before considering budget changes.

### Pass B: Repository-Aware Skill Review

- Applied the assessment artifact, workflow gate, Git flow, workflow handoff, and AI-context audit/governance contracts.
- Compared the intended integration commit `769589fd5c9404f3486def95906e92957703fb1a` with current `main`; the five timeout-related implementation files are unchanged.
- Confirmed the profile registry owns the exact timeout budgets and that `package-full-matrix` already invokes the complete packaging suite.

### Delegation

- Sub-agents used: `none`
- Assigned surfaces: `not-applicable`

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory graph | indexed source checkout; revision did not match the dedicated assessment worktree | returned a mismatched function boundary for `run_command_check` | shell runner discovery only | exact commit content and shell-function boundaries | `git show`, `git diff`, and direct tracked-file reads at `main@d39712b` |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Timeout orchestration | 1 Bash runner | agent/tooling | source repository | active | owns per-check timeout and evidence classification |
| Profile budgets | 1 shell registry | agent/tooling | source repository | active | owns 300s, 60s, and 900s budgets relevant to this incident |
| Slow contract suites | 2 Python test files | maintainers | source repository | active | repeated disposable fixtures and nested processes |
| Handoff contract | 1 policy | agents/humans | repository governance | active | pins a validated commit but does not enforce stable checkout identity during command execution |

## Strengths

1. The aggregate runner classified both timeouts as failed and emitted `timed-out`; it did not convert eventual log output into a pass.
2. Per-check and total wall times made the cost visible and allowed the timeout boundary to be localized.
3. The tests use disposable repositories and verify that the real repository remains unchanged by their fixtures.
4. The handoff policy already requires a fully validated subject commit, dirty-state digest, exact command, exit code, output digest, and bounded tail.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| VALSNAP-001 | HIGH | Terminal validation is not execution-bound to an immutable checkout. An independent Codex worktree provides no isolation when the command `workdir` is redirected to a shared source checkout. | `check-all --critical` ran from 22:11:51 to 22:34:12. During that interval the source checkout committed the merge at 22:12:06, switched to `main` at 22:20:51, switched to another branch at 22:21:20, and committed again at 22:23:02. The standalone packaging run then crossed commits at 22:38:12 and 22:52:38. The handoff policy pins the fully validated subject commit at lines 39-57 but the runner does not compare that identity before and after execution. | Long-running results cannot establish compliance for one version even when every assertion passes. Repeated polling detects drift late but cannot make the evidence valid. | Define terminal validation as a final clean-commit gate in a dedicated worktree. Add preflight and postflight identity verification and stop the suite chain on drift with a distinct invalidated-evidence outcome. | `ai-context-governance` |
| VALTIME-001 | HIGH | Timeout cancellation targets a wrapper or direct PID without proving full descendant termination. | `check-all.sh:862-900` uses GNU `timeout --foreground` around either the command or `bash -c`; its fallback sends TERM/KILL only to `$!`. Both timed-out logs later reached `OK`: 40 tests in 379.975s after a 300s boundary and 19 tests in 67.767s after a 60s boundary. | Orphan validators can keep consuming resources, append after the recorded timeout, overlap later checks, and confuse operators who see eventual `OK`. | Introduce a cross-platform process supervisor that owns a process group/session on POSIX and a Job Object or equivalently bounded process tree on Windows. After timeout, wait for descendants, seal the log, and assert that no later output is possible. | `ai-context-governance` coordinating a bounded tooling implementation |
| VALTEST-001 | MEDIUM | Slow suites combine repeated fixture creation with nested subprocesses that have no local timeout. | The aggregate suite contains 40 tests, 29 `SyntheticRunnerRepo` constructions, and 10 `SyntheticShellAssetRepo` constructions. The immutable-history suite creates and commits a fresh Git repository in `setUp` for each of 19 tests. Relevant `subprocess.run` calls in both suites and the native-validator loop at `validate-immutable-history.py:744-747` have no explicit timeout. | One slow or stuck child consumes the whole outer budget. Repeated process and Git setup hides which test or operation owns the time. | Add bounded subprocess timeouts and cleanup assertions, collect per-test durations, then reduce repeated fixture/process work without weakening isolation or fail-closed behavior. | `ai-context-governance` coordinating `slice-implementer` or `local-change-implementer` |
| VALCOST-001 | MEDIUM | Expensive suite coverage and timeout budgets are not reconciled before reruns. | `validation-profile-registry.sh:232-236` proves `package-full-matrix` is exactly `python .ai/scripts/tests/test_ai_context_packaging.py -v` with a 900s budget. It passed inside the aggregate in 860.380s, then was rerun independently for 1177.187s after snapshot integrity was already lost. The aggregate and immutable budgets are 300s and 60s, below the later observed 379.975s and 67.767s completion times. | Duplicate runs add about twenty minutes and increase contention. Blindly raising budgets can conceal fixture or process-design defects, while leaving current budgets can create platform-dependent false failures. | Resolve coverage from the registry before rerunning. Re-measure isolated Windows and hosted runs after process/test optimization, then set budgets from a documented distribution and margin rather than one busy run. | `ai-context-governance` |

## Baseline And Skill Comparison

### Confirmed

- A timeout is an orchestration failure and is never a pass, even when later log text reports `OK`.
- Snapshot drift invalidates long-running compliance evidence.
- Test content and subprocess ownership must be reviewed before changing budgets.

### Added By Repository-Aware Review

- The handoff policy already carries most evidence fields needed for a snapshot contract; enforcement is missing at command execution time.
- The profile registry proves that the standalone packaging rerun duplicated `package-full-matrix` exactly.
- Material remediation would change future agent behavior and validation contracts, so it requires an online Issue and one governance workflow before implementation.

### Downgraded Or Deferred

- The observed 300s, 60s, and 900s limits are not independently declared defective constants yet; concurrent execution and moving checkouts contaminated the timing sample.
- Increasing timeout values is deferred until isolated duration evidence exists after process and fixture remediation.

### Overturned

- Frequent source updates are not a requirement of long validation. They invalidate the evidence. Long validation belongs after the candidate is fixed.
- The independent Codex worktree did not isolate commands that were deliberately run in `C:\Github\YuChia\ai-collaboration-prompts-dotnet-backend`.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | dedicated assessment worktree started clean at `main@d39712b3acb2d886dc5541ecc9c93a101f412b60` |
| Subject freshness | passed | relevant timeout files have no diff between intended merge `769589f` and assessed `main@d39712b` |
| Registry and command ownership | passed | aggregate, immutable-history, and package commands/budgets read from the tracked registry |
| Static test/process inspection | passed | fixture construction and unbounded subprocess calls counted from tracked files |
| Incident command evidence | diagnostic-only | exact commands, exits, durations, skips, timeouts, and reflog events retained; moving checkout prevents snapshot-compliance use |
| Long test rerun | not-run | remediation is not implemented; another long run would not answer the identified design questions |

### Skipped Validation

- No product code or product tests were inspected.
- No timeout budget was changed or experimentally increased.
- No online Issue, workflow, implementation, push, or integration was performed.

## Recommended Action Order

1. Create and read back one online Issue that binds the terminal-snapshot and timeout-orchestration scope; record explicit owner implementation authorization.
2. Start one `ai-context-governance` workflow because the change spans policy, runner behavior, tests, evidence schema, and independent verification.
3. Define two validation classes: development/focused checks may run on dirty work, but terminal release/compliance evidence requires a clean committed candidate in a dedicated worktree.
4. Add a snapshot identity record containing repository, full HEAD, branch/detached state, merge state, status digest, and relevant tree/input fingerprint. Verify it before and after every long command and abort remaining suites on drift.
5. Add a unique run ID and process supervisor. Test timeout cleanup by creating a child and grandchild that attempt delayed log writes, then prove both are terminated and the log remains sealed.
6. Add explicit timeout and cleanup handling to nested `subprocess.run` calls. Instrument per-test duration, fixture setup, Git operations, and child command duration.
7. Optimize repeated fixtures or split contract suites only after duration data identifies the dominant costs. Preserve test isolation and fail-closed assertions.
8. Re-measure the aggregate, immutable-history, and packaging suites on isolated Windows and hosted CI runners. Calibrate budgets from the documented measurements plus a reviewable margin.
9. Run exactly one terminal validation chain against the final commit, obtain independent `ai-context-auditor` verification, and retain only that immutable-snapshot evidence for closeout.

## Proposed Acceptance Criteria

- A terminal gate refuses a dirty, staged mid-merge, or changing checkout as closeout evidence.
- The evidence record identifies one full commit and proves the same identity at command completion.
- Injected snapshot drift stops the remaining validation chain and produces a non-passing, machine-readable invalidation outcome.
- Injected timeout terminates child and grandchild processes on Windows and POSIX; the log cannot grow after timeout is recorded.
- Each nested subprocess has an explicit bounded timeout and deterministic cleanup path.
- Per-test duration evidence identifies the slowest operations before timeout budgets are changed.
- Aggregate evidence records whether an expensive standalone suite is already covered and requires an explicit rerun reason for duplication.
- The final isolated Windows and hosted runs complete within approved budgets without skips being represented as full coverage.

## Deferred Items

- Exact timeout values remain an implementation-time decision after isolated profiling.
- Selection of Windows Job Objects, `taskkill /T`, or another process-tree mechanism requires a bounded portability spike; the assessment does not choose an implementation prematurely.
- Existing Issue #176 relationship and current provider state require online read-back before deciding whether to extend it or create a separate Issue.

## Appendix

### Commands Run

```text
C:\Program Files\Git\bin\bash.exe ./.ai/scripts/check-all.sh --critical
python .ai/scripts/tests/test_ai_context_packaging.py -v
git reflog --date=iso
git worktree list --porcelain
git diff --name-status 769589fd5c9404f3486def95906e92957703fb1a..d39712b3acb2d886dc5541ecc9c93a101f412b60 -- <timeout-related paths>
rg -n <timeout, fixture, subprocess, and handoff patterns> <scoped validation files>
```

### Incident Evidence Summary

| Command / check | Contract result | Observed duration | Bounded interpretation |
| --- | --- | ---: | --- |
| `check-all.sh --critical` | exit `1`; 52 passed and 2 timed out across 54 selected | 1344.651s | failed and snapshot-invalid |
| aggregate runner contract | timeout at 300s | later log: 379.975s | eventual assertion `OK` does not supersede timeout |
| immutable-history contract | timeout at 60s | later log: 67.767s | eventual assertion `OK` with one skip does not supersede timeout |
| complete packaging suite | exit `0`; 37 tests with one skip | 1177.187s | assertion pass, but moving checkout makes it diagnostic-only |

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260810-005/report.md`
- Stable finding references: `ASM-20260810-005#VALSNAP-001`, `ASM-20260810-005#VALTIME-001`, `ASM-20260810-005#VALTEST-001`, `ASM-20260810-005#VALCOST-001`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `not-created`
- Verification assessment: `not-created`
- Remediation intentionally not performed by this skill: `yes`
