# Issue 373 selected public checks after the c1fb1c1f fast-forward

The seven existing public families each ran once, sequentially, without test,
runner, helper or product changes. Five passed. PR completed its assertions but
failed cleanup (exit 2). Workflow completed its main round trip but failed the
separate deferred-task fixture (exit 1). Full selected public acceptance remains
incomplete; neither failure was repaired or retried here.

## Authority and subject

- Executor task: `01a0cd49-7805-7202-9176-e8f7b4cf4285`; resumed coordinator:
  `01a0ce78-db26-74e1-a615-2bd0599f7d0c`.
- Worktree: `F:/framework-next/373`; branch:
  `codex/2026-09-23-public-skill-checks`.
- Clean prior local checkpoint: `7996b32d3d4f70553b203299e25dc69d9413ff9d`.
  Locally available source was fast-forwarded to exactly
  `c1fb1c1fb07a6d246e3bcedd3cd851918f66b306`; no fetch was used.
- Owner-authorized scope: seven unchanged family executions and only this
  workflow's records/local commit. U001 remains effective. The declared
  GPT-6 Astra / ultra dispatch is provenance, not independent runtime attestation.
- Prior [report](report.md), [observations](evidence/observations.json),
  failure evidence and retained fixtures remain historical evidence. The new
  source/run does not erase earlier failures or relabel earlier partial checks.

## Actual execution

Each command ran from `F:/framework-next/373`:

```text
python -I -B tests/framework_next/run.py --layer public --family <family> --output-root F:/framework-next/p7-runs/373-public
```

The existing `capture-family.py` launched each real runner once. The exact Python
executable, argv, cwd, source pin, test-file hashes and stream hashes are retained
in each linked capture. Python was 3.13.14, PyYAML 6.0.3, jsonschema 4.26.0 and
referencing 0.37.0. No read-only-mode or aggregate invocation was substituted.

| Family / capture | Exit and disposition | Public launches | Measured driver Git / process total | Nested launch upper bound | Fixture wall seconds |
| --- | --- | ---: | --- | ---: | ---: |
| [lesson](evidence/resume-c1fb1c1f-lesson.json) | 0 passed | 43 | 4 / 47 | 12 | 24.814 |
| [adr](evidence/resume-c1fb1c1f-adr.json) | 0 passed | 31 | 4 / 35 | 9 | 17.929 |
| [standards-promotion](evidence/resume-c1fb1c1f-promotion.json) | 0 passed | 26 | 4 / 30 | 9 | 14.564 |
| [pr](evidence/resume-c1fb1c1f-pr.json) | 2 cleanup-failed | 23 | unavailable / unavailable | 73 | unavailable |
| [local-backlog](evidence/resume-c1fb1c1f-backlog.json) | 0 passed | 29 | 4 / 33 | 9 | 12.927 |
| [software-development-orchestrator](evidence/resume-c1fb1c1f-workflow.json) | 1 failed, T6-with-deferrals | 34 | 4 / 38 | 9 | 20.467 |
| [problem-frame-author](evidence/resume-c1fb1c1f-cbf.json) | 0 passed | 29 | 4 / 33 | 9 | 13.756 |

There were 215 public launches across seven separate selected invocations; each
was below its 160 public-launch cap. This is not an aggregate run against that
cap. Actual nested child launches are unavailable: bounds above are conservative
source accounting, not measured process counts. Each capture adds one outer
runner subprocess, excluded from the fixture's process audit. PR cleanup raised
before returning its accounting, so no complete seven-family process total is
claimed. Its unittest duration was 16.810 seconds, not a complete fixture duration.

All five passing families completed their selected C4/C6 and T1/T2/T3/T5/T7
phases, including their expected negative outcomes. Lesson also completed the
selected 4 MiB + 1 byte stdin boundary. Expected invalid-input, blocked, conflict
and unsupported outcomes are successful negative assertions, not family failures.
The [observations](evidence/resume-c1fb1c1f-observations.json) retain phase-level
results and exact per-run accounting.

## New failure fingerprints and repair requests

**PR cleanup:** assertions completed through `T4-git-round-trip` and
`T4-synthetic-provider`; unittest reported OK. `support.FixtureRun.close`
then raised `PermissionError / WinError 5` at `shutil.rmtree`, on:

```text
F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d/pr/project/git-fixture/.git/objects/0d/23fa530318e9f5d15bea5f49dc23ec095ffa18
```

Scoped read-back found a regular 134-byte file, Windows attributes 33
(read-only + archive), and no reparse attribute. No chmod or cleanup retry was
performed. The initial sandbox lstat refusal and successful scoped read remain
separate in the [cleanup evidence](evidence/resume-c1fb1c1f-pr-cleanup.json).
The helper measures before deletion, but its exception prevents that observation
from being returned. Current residue is only the partially deleted remainder:
21 files / 117172 logical bytes; it is not the run's high-water accounting.

Smallest requested repair: the helper owner handles read-only Git objects inside
the verified unique fixture without weakening root identity, containment or
reparse checks, and preserves measured accounting when cleanup fails. Keep
cleanup failure nonzero. This is a request, not an implementation in this commit.

Only the PR test creates Git objects in its fixture. The remaining backlog,
workflow and CBF tests have no `support.git` fixture calls; their common Git
operations only read source. They were independent of this cleanup failure and
continued in the selected order. No dependent PR case was dispatched afterward.

**Workflow fixture:** `resource-setup`, `C4-config`, `C6-binding` and
`T6-round-trip` completed. In the separate `T6-with-deferrals` case, the checkpoint
request changed T001 to deferred but kept `result: ""`. The product returned:

```json
{"diagnostics":[{"code":"type","message":"task result must be a nonempty string."}],"directories_created":[],"mutation_state":"none","operation":"checkpoint","outcome":"invalid-input"}
```

The response SHA-256 is
`8b924b6e2befaa9f4350f13f6e3e2689f22908bba36f18f1a681511aeab71db1`.
The [failure evidence](evidence/resume-c1fb1c1f-workflow-failure.json) contains the
exact request/response, full retained transcript and source-bound excerpts:
`test_work.py:222-224`, `workflow.py:923-925`, and `operations.md:131`.
The contract permits empty reason/result only for initial pending/active tasks;
the validator requires both for other states. This identifies a test fixture
defect against the existing product contract.

Smallest requested repair: populate a truthful nonempty deferred-task result in
`tests/framework_next/test_work.py`, preserving the product invariant and the
synthetic attribution boundary. No test or product repair was made. The second
workflow's retrospect, completed transition, resume and with-deferrals assertions
were not executed. The emitted `unexecuted_phases: []` only means there was no
later named phase; it does not establish completion of the failing phase.

## Bounds, custody and retained fixtures

Measured non-boundary authored bytes ranged from 18234 to 31191 per accounted
family, below 1 MiB. Observed file counts ranged from 16 to 21, below 256. The
unchanged 16 KiB normal-input bound and 256 helper/nested-launch bound stayed in
force; the single 4194305-byte Lesson stdin case is the selected exception.
PR's missing pre-cleanup accounting remains unavailable, not inferred compliant
from its smaller surviving residue. All fixtures used committed raw resources
with their relative layout; they did not assemble or install a package.

Five successful unique fixtures were removed by unchanged cleanup and absence
was read back. Their `retained_bytes` fields describe the measurement immediately
before deletion. Their advertised child transcript paths no longer exist;
runner output preserves call summaries/hashes, not the deleted full child streams.
Exact runner stdout/stderr bytes for all seven runs are retained in
[the base64 stream bundle](evidence/resume-c1fb1c1f-raw-streams.json), preventing
Git newline conversion from altering the recorded byte evidence.

New retained failures, preserved without cleanup:

- PR: `F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d`.
  Its surviving child transcript and synthetic-provider results are also stored
  losslessly in the cleanup evidence.
- Workflow: `F:/framework-next/p7-runs/373-public/fn-290c21edfb594765b635b8d9bda1fcb9`;
  19 retained files / 395594 logical bytes. Its child transcript is stored
  losslessly in the workflow failure evidence.

PR used actual tiny local Git history with two commits and one tracked UTF-8
file. Its four provider failure scenarios replaced transport only and remained
synthetic: unavailable executable, preflight conflict, post-write read failure
and lost write response. No live provider operation or provider acceptance was
performed. Synthetic decisions and deferrals never authorize source adoption.

## Local handoff

Only this existing workflow's records changed after source c1fb1c1f. Exact-byte
capture integrity, JSON/YAML parsing, local Markdown links, Git whitespace/scope
checks and the complete planned commit-message validation are the selected
record checks; their actual outcomes are retained in the local validation record.
The delivery commit is the containing local commit, avoiding a self-referential
SHA inside tracked evidence. Workflow status stays in progress.

The coordinator's next action is to select the two bounded repairs and then
separately authorize affected-family execution. There is no unchanged retry or
automatic wider run. Full rc.1 assembly and existing-target customization pilot,
apply/install/native acceptance, CI restoration, legacy/full/history/audit/lease
or hosted gates, publication and adoption remain separately selected or
`deferred-by-owner` under U001. This handoff does not push, open a PR, mutate
Issue/Project state, or change credentials.
