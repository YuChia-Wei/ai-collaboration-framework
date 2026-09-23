# Issue 373 public families on one selected source

All seven selected public families passed on the same unchanged clean tracked
source `e71712b71791170c3f4946e131ce867f82dade8f`. Each ran exactly once in a
separate runner process and unique owned fixture. Every selected phase completed,
with no skips, partial outcomes, cleanup failures, missing captures or source drift.
This establishes the bounded C4/C6 and T1-T7 public selection on that source.

## Identity, selection and authority

The original `F:/framework-next/373` worktree and
`codex/2026-09-23-public-skill-checks` branch were verified clean at
`085fb3758d0550959d58bd20e91a41ac5903b096`, then fast-forwarded using local
objects to the exact selected source. No fetch or branch change occurred.
The coordinator selected this batch after the read-only reconciliation under
original Issue 373 / U001 authority. Declared executor remains GPT-6 Astra / ultra;
that dispatch provenance is not independent runtime attestation. No agents,
new tasks, formal packets or callback messages were created.

The existing capture was used in this exact order: PR, Lesson, ADR,
standards-promotion, local-backlog, software-development-orchestrator,
problem-frame-author. Each capture invoked:

```text
python -I -B tests/framework_next/run.py --layer public --family <selected-family> --output-root F:/framework-next/p7-runs/373-public
```

The source SHA, tracked diff, prior capture hashes/outcomes, fixture absence and
current test-file hashes were checked before every next family and after the last.
The runner/helper/public tests/product were not edited. README remains untouched
for its separate owner. The exact executable, argv, cwd, source/runtime, phase/call
observations and accounting are in [the result](evidence/reconcile-e71712b7-results.json)
and each `reconcile-e71712b7-<family>.json` capture.

## Actual results

| Family | Exit / outcome | Public | Driver Git | Driver total | Fixture seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| pr | 0 / passed | 23 | 13 | 36 | 10.630 |
| lesson | 0 / passed | 43 | 4 | 47 | 20.328 |
| adr | 0 / passed | 31 | 4 | 35 | 14.337 |
| standards-promotion | 0 / passed | 26 | 4 | 30 | 11.698 |
| local-backlog | 0 / passed | 29 | 4 | 33 | 10.843 |
| software-development-orchestrator | 0 / passed | 37 | 4 | 41 | 20.451 |
| problem-frame-author | 0 / passed | 29 | 4 | 33 | 12.298 |

Totals across the seven independent invocations: 218 public, 37 driver Git,
255 measured driver processes and 100.585 reported fixture seconds. Outer captures
each launch one runner outside the fixture audit. The sum of conservative nested
launch reservations is 130; actual opaque nested launches remain unavailable.
Timing excludes capture/guard/task overhead and is not a performance comparison.
Runtime: Python 3.13.14, PyYAML 6.0.3, jsonschema 4.26.0, referencing 0.37.0.

All families completed their selected C4/C6 setup and family phases. Lesson
completed the one 4194305-byte stdin boundary; Workflow completed the separate
with-deferrals case; PR completed actual two-commit/one-file local Git work and
four synthetic provider failure scenarios. Expected conflicts/invalid-input/
unsupported outcomes are passing negative assertions, not family failures.
Synthetic provider and decision/deferral inputs do not prove actual provider
acceptance, owner authority or adoption.

## Caps and evidence custody

The unchanged per-invocation caps remained 160 public launches, 256 combined
helper/nested reservation budget, 256 observed files, 16 MiB retained logical
bytes, 1 MiB authored fixture bytes and 16 KiB normal input, with the selected
single Lesson stdin exception. No aggregate command was run or cap increased.
All seven would require 218 public and 385 measured-driver-plus-reserved-nested
budget on the historical success path, exceeding the aggregate 160/256 limits.
The separate-family selection is explicit; it does not establish aggregate success.

All 14 exact runner stdout/stderr streams are retained alongside captures and in
[the lossless bundle](evidence/reconcile-e71712b7-raw-streams.json); all hashes
match capture metadata. Successful cleanup removed all seven new fixture roots,
with absence read back. Accounting explicitly reports `before-cleanup`; retained
bytes are pre-deletion measurements, not current residue. The unchanged helper
also removed full child transcripts and synthetic-provider fixture files. Runner
streams retain phase/call summaries and hashes, not those deleted child bodies.
There was no timeout, so the existing capture's timeout evidence limitation was
not exercised.

Old failures and earlier successes remain at their original source identities.
No old observations were relabelled as this batch. Both recent failed-run roots
remain present with the original transcript hashes:

- `F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d`
- `F:/framework-next/p7-runs/373-public/fn-290c21edfb594765b635b8d9bda1fcb9`

Earlier retained runs were not targeted. No manual cleanup or unchanged retry
occurred. The prior [PR result](pr-cleanup-rerun-report.md) and
[workflow repair result](deferred-fixture-repair-report.md) remain historical.

## Completion and handoff

The selected execution completion criteria are all met: seven exact selected
families; one shared execution SHA; all declared phases/no skips; independent
unchanged caps; exit 0 and successful cleanup; complete runner captures with
verified hashes/runtime/accounting; preserved prior evidence; no source/test edits.
Record readability, JSON/YAML, links, Git scope/whitespace and complete planned
message validation are retained in the local validation record. The execution
SHA is e71712b7; the containing records-only commit is the separate delivery SHA.

Technical public selection is complete and ready for coordinator closeout.
The workflow stays in progress for delivery integration and coordinator-owned
Issue/Project disposition; this task performs neither. README wording is supplied
in [the proposed public paragraph](public-readme-suggestion.txt) for the #368 owner;
no README write is included here.

C5, native, installation/target adoption, all-public aggregate, actual provider,
CI and whole-P7 completion are not established by these tests. Unselected legacy/
full/history/audit/lease/hosted gates remain `deferred-by-owner` under U001,
owned by program 322 coordinator / P7. No push, PR, provider mutation, publication
or adoption was performed. Only this existing workflow's records are delivered.
