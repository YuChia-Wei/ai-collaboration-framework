# LESSON-VAL-001: Terminal Validation Must Use an Immutable Snapshot

> This lesson is non-normative. It records a confirmed validation incident and
> does not authorize implementation or replace validation policy, standards,
> assessments, workflows, or runbooks.

| Field | Value |
| --- | --- |
| Lesson ID | `LESSON-VAL-001` |
| Category | `validation` |
| Lifecycle | `active` |
| Normative Authority | `none` |
| Origin Evidence | [ASM-20260810-005](../../assessments/ASM-20260810-005/report.md) |
| Evidence Subject | #175/#178 validation run `20260810T141148Z-1549` and target merge commit `769589fd5c9404f3486def95906e92957703fb1a` |
| Promotion Target | `none` |
| Supersedes | `none` |
| Superseded By | `none` |

## Origin Evidence

[ASM-20260810-005](../../assessments/ASM-20260810-005/report.md) retains the
command outcomes, checkout timeline, code-inspection findings, and proposed
remediation boundaries for this incident. The run targeted the #175/#178
integration, but its commands executed in a shared checkout that changed while
the long-running validators were active.

The initial conversational draft was transient and is intentionally not a
second source of truth. This repository packet is the durable lesson derived
from the assessment.

## Context And Symptom

A delegated validation-only task owned an independent Codex worktree, but the
validation commands explicitly used a separate shared source checkout as their
working directory. That checkout was committed, switched to `main`, switched
again, and committed again while validation was still running. The aggregate
check and standalone packaging suite therefore crossed Git states and could
only be retained as diagnostic evidence, not single-snapshot compliance
evidence.

The aggregate runner also reported two timeout failures. Their logs later
reached `OK`. This did not convert either timeout into a pass; it exposed a
separate orchestration and descendant-process-lifecycle concern.

## Confirmed Conditions And Root Cause

- `check-all.sh --critical` started before the target merge commit existed and
  remained active across subsequent branch switches.
- The standalone packaging suite also remained active across later commits.
- The aggregate profile already selected the same full packaging command, so
  the standalone rerun duplicated an expensive suite without producing valid
  terminal-snapshot evidence.
- The aggregate contract exceeded its 300-second budget and later logged 40
  tests in 379.975 seconds as `OK`.
- The immutable-history contract exceeded its 60-second budget and later
  logged 19 tests in 67.767 seconds as `OK`, with one skip.
- Static inspection found 29 `SyntheticRunnerRepo` constructions and 10
  `SyntheticShellAssetRepo` constructions in the aggregate suite. The
  immutable-history suite initialized a Git repository for each of 19 tests.
- Relevant nested `subprocess.run` calls had no explicit timeout.
- The shell runner used GNU `timeout --foreground` around a wrapper and its
  fallback signalled only the direct child PID. Continued log output after the
  timeout showed that completion and log sealing were not reliably coupled to
  the runner verdict.

The confirmed snapshot-integrity root cause was the explicit use of a mutable,
shared checkout. The exact Windows descendant-process ancestry after each
timeout was not captured, so incomplete process-tree termination remains a
strongly supported condition to verify rather than a fully reconstructed PID
history.

## Reusable Conclusion

- An independent task worktree does not isolate a command whose working
  directory points to another shared checkout.
- Long release or compliance validation is useful as terminal evidence only
  after implementation, conflict resolution, and integration are complete and
  the exact candidate is fixed as a commit.
- Repository identity before and after a long command must refer to the same
  path, full `HEAD`, merge state, index/worktree state, and untracked-file
  fingerprint. Drift makes the result diagnostic-only.
- A timeout remains a failed orchestration outcome even when an unobserved or
  surviving process later logs successful assertions.
- Timeout calibration is meaningful only after measuring isolated execution,
  bounding nested subprocesses, reducing redundant fixture work, and proving
  process-tree cleanup.
- Expensive suites should be rerun independently only when registry and prior
  evidence show that the aggregate gate did not already provide the required
  coverage or output.

## Non-Applicable Cases

- Exploratory diagnostics that are explicitly labelled mixed-revision or
  diagnostic-only do not claim terminal snapshot compliance.
- A validator intentionally designed to compare multiple commits is not made
  invalid merely because its input set contains more than one revision; its
  own execution checkout still needs stable identity when that is part of the
  evidence contract.
- An ordinary assertion failure with complete process cleanup is different
  from a timeout and should be diagnosed from the failed assertion.
- A short local check may not justify the full cost of a terminal suite, but
  its reported evidence still needs an honest subject identity.

## Remediation Example

A candidate remediation sequence is:

1. Finish implementation and integration, then record the candidate's full
   commit SHA.
2. Create a dedicated, short-path worktree at that commit and keep it detached
   or otherwise protected from concurrent branch operations.
3. Record preflight repository identity, selected runtime, validation profile,
   unique run ID, and existing validator processes.
4. Run the aggregate terminal gate once. Re-read repository identity after
   each long command and stop the chain on any drift.
5. On timeout, terminate and wait for the complete process tree, seal the log,
   and verify that neither descendants nor output continue.
6. Measure test and subprocess durations, remove repeated setup where safe,
   add local subprocess bounds, and only then recalibrate profile budgets from
   isolated Windows and hosted-runner evidence.

This sequence is a remediation proposal from the assessment. The full
process-tree implementation and terminal-suite rerun remain separately
authorized work.

## Verification

| Command or contract | Exit / runner outcome | Duration and bounded result |
| --- | --- | --- |
| `bash ./.ai/scripts/check-all.sh --critical` | exit `1` | 1344.651 seconds; 54 checks; two required timeouts |
| `aggregate-runner-contract` | timeout at 300 seconds | later log: 40 tests in 379.975 seconds, `OK` |
| `immutable-history-validation-contract` | timeout at 60 seconds | later log: 19 tests in 67.767 seconds, `OK`, one skip |
| `python .ai/scripts/tests/test_ai_context_packaging.py -v` | exit `0` | 1177.187 seconds; 37 tests; one skip; checkout drift made the result diagnostic-only |

No individual unittest assertion was identified as the aggregate gate's
failing result. The exact failing check names were
`aggregate-runner-contract` and `immutable-history-validation-contract`, and
their timeout outcomes remain failures.

## Promotion And Supersession

The lesson remains `active` with no promotion target, predecessor, or
successor. Any future standard, runbook, validator, or process-supervisor
change requires separately authorized implementation and verification.

## Security And Portability Boundary

The reusable conclusions concern Git snapshot identity, validation sequencing,
bounded subprocesses, and evidence classification. Local usernames, hostnames,
temporary paths, credentials, private endpoints, and mutable machine state are
excluded. Windows/Git Bash behavior is part of the observed environment and
must not be generalized to every POSIX host without platform-specific
verification.
