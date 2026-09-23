# Issue 373 deferred workflow fixture repair

The single fresh `software-development-orchestrator` public family execution
passed with exit 0 on clean repair commit
`8d09ec6c5d2d41bcf4e7e3e108640545d398fea1`. It completed both `T6-round-trip`
and `T6-with-deferrals`, along with resource setup, C4 configuration and C6 binding.
There were no skipped or unexecuted phases, and fixture cleanup succeeded.

## Change and authority

The coordinator selected this repair inside the original Issue 373 test ownership
under U001 and the owner-selected repair-before-pilot sequence. The task resumed
from clean local HEAD `8b151f0aa31ec91277c5399251171ebc12902f35` on
`codex/2026-09-23-public-skill-checks` in `F:/framework-next/373`.
Only `WorkflowTests` in `tests/framework_next/test_work.py` changed: the deferred
task now has the truthful result `Not executed; deferred in synthetic fixture.`
The existing product contract and synthetic authority semantics were preserved.

Before behavioral execution, the correction and its
[preflight evidence](evidence/deferred-fixture-repair-preflight.json) were committed.
AST/UTF-8 inspection, exact minimal diff, Git whitespace and complete planned-message
validation passed. Direct source-segment comparisons proved `PrTests` and
`BacklogTests` unchanged. Git object comparisons with prior source
`c1fb1c1fb07a6d246e3bcedd3cd851918f66b306` proved all `src`, helper, runner,
knowledge tests and CBF tests unchanged. Their captured file hashes also matched.
The single changed fixture does not invalidate attribution of the earlier
bounded observations to their original source; no fresh all-family pass is claimed.

## Actual selected run

```text
python -I -B tests/framework_next/run.py --layer public --family software-development-orchestrator --output-root F:/framework-next/p7-runs/373-public
```

The unchanged issue-local capture command launched that runner exactly once,
from the clean repair commit. Exact executable/argv/cwd, file hashes and stream
hashes are in [the capture](evidence/deferred-fixture-8d09ec6c-workflow.json).
[The result](evidence/deferred-fixture-repair-result.json) preserves actual phase
outcomes, all 37 call summaries and lossless base64 runner stdout/stderr.

| Observation | Actual result |
| --- | --- |
| Runner exit / family outcome | 0 / passed |
| Public launches | 37 |
| Measured fixture processes | 37 Python + 4 Git = 41 |
| Nested launches | Actual count unavailable; conservative upper bound 9 |
| Fixture wall time | 22.666 seconds |
| Authored bytes | 31440 |
| Observed files / logical bytes | 19 / 420994 |
| Pre-cleanup retained files / bytes | 19 / 418482 |
| Cleanup | Succeeded; unique run root absent on read-back |

The successful root was
`F:/framework-next/p7-runs/373-public/fn-0cd8a10a1e064a669d8fcd24adc8a725`.
The unchanged helper deleted its full child transcript. The retained runner
streams contain call summaries and hashes, not the deleted child stdout bodies.
Pre-cleanup byte counts are not current residue. All measured bounds stayed
within the selected limits; no new boundary exception was introduced.

## Preserved failures and handoff

The prior [seven-family report](resume-c1fb1c1f-report.md) and exact
[failed workflow request/response](evidence/resume-c1fb1c1f-workflow-failure.json)
remain unchanged. The original failed workflow transcript hash was rechecked,
and both workflow and PR failure roots remain retained:

- `F:/framework-next/p7-runs/373-public/fn-290c21edfb594765b635b8d9bda1fcb9`
- `F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d`

The five prior passing families were not rerun. Their observations remain bound
to c1fb1c1f. PR was not rerun or repaired; its cleanup failure remains separate
and is assigned to the helper owner by the coordinator. This local result resolves
the selected workflow fixture failure, not the complete public suite or rc.1 pilot.
No other repair was attempted and no residue was removed by this task.

The final records-only commit contains the actual result and current task pointer.
Record parsing, links, stream integrity, scope/whitespace and exact planned-message
checks are retained in the local validation record. The containing commit is the
handoff identity; workflow remains in progress for coordinator integration and
separate PR cleanup disposition. No push, PR/provider mutation, native execution,
publication, adoption or CI activation occurred. Unselected legacy/full/history/
audit/lease/hosted gates remain `deferred-by-owner` under U001, owned by the
program 322 coordinator / P7 until separately selected or adopted.
