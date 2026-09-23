# Issue 373 PR family after the helper cleanup repair

The one selected PR family run passed with exit 0 on clean source
`67788471b0556b660e4f8b30cf1449c61127ba97`. Resource setup, C4 configuration,
C6 binding, T4 Git round trip and T4 synthetic provider assertions all completed.
Cleanup succeeded, and the new unique fixture root was absent on read-back.

## Execution and observations

The existing branch `codex/2026-09-23-public-skill-checks` in
`F:/framework-next/373` was verified clean at
`fd19f252d1f6668bb6315ee67ac9528326fa2923`, then fast-forwarded using local objects
to the exact coordinator-selected source. No fetch or branch change occurred.
The unchanged capture launched this command exactly once from that clean commit:

```text
python -I -B tests/framework_next/run.py --layer public --family pr --output-root F:/framework-next/p7-runs/373-public
```

[Capture metadata](evidence/pr-cleanup-67788471-pr.json) and
[actual results, subject differences and lossless streams](evidence/pr-cleanup-rerun-result.json)
retain executable, argv, cwd, source commit, test-file hashes and stream hashes.

| Observation | Actual result |
| --- | --- |
| Exit / outcome | 0 / passed |
| Public launches | 23 |
| Measured driver processes | 23 Python + 13 Git = 36 |
| Nested launches | Actual count unavailable; conservative upper bound 73 |
| Fixture wall time | 12.7 seconds |
| Authored bytes | 21229 |
| Observed files / logical bytes | 33 / 245583 |
| Pre-cleanup retained files / bytes | 33 / 245280 |
| Cleanup / new residue | Succeeded / none |

The measurement explicitly reports `measurement_phase: before-cleanup`. The
new root was `F:/framework-next/p7-runs/373-public/fn-22a42ff045ea44c8bfa540fab6016a57`.
Measured counts stayed within the selected caps. Actual cleanup retry callback
counts are not instrumented. The last public call's expected validation-subject
conflict is a passing negative assertion. Local Git work used two commits and
one tracked UTF-8 file; all four provider failure scenarios remained synthetic
transport cases, with no live provider execution or acceptance.

Successful cleanup removed the full child transcript and synthetic-provider
fixture files. Retained runner output contains phase/call summaries and hashes,
not the deleted child output bodies. Exact runner stdout/stderr bytes are stored
in base64 to survive Git normalization. Pre-cleanup bytes are not current residue.

## Subject differences and retained attribution

Direct Git read-back from fd19f252 to 67788471 shows:

- `support.py` adds registered identity checks, one guarded retry for a known
  regular single-link Windows read-only file, and retained cleanup-failure accounting.
- `run.py` emits that accounting on failure and adds native dispatch outside
  this PR selection.
- All `src/skills`, all three public test modules and the capture are unchanged.
  `PrTests` also matches its normalized source segment from the prior PR run at c1fb1c1f.
- Distribution assembly/data/installation-state/manifest, a new complete profile,
  native/contract/versioned-candidate tests, README and build-candidate tooling
  changed upstream. The result preserves all 46 changed paths and selected object
  identities. This run does not establish their broader acceptance.

No product, helper, runner or test changes were made in this task. The five earlier
family passes remain attributed to `c1fb1c1fb07a6d246e3bcedd3cd851918f66b306`;
the workflow pass remains at `8d09ec6c5d2d41bcf4e7e3e108640545d398fea1`.
Those six families were not rerun. This fresh PR pass is not a seven-family
execution on one common subject.

The previous [PR cleanup failure](evidence/resume-c1fb1c1f-pr-cleanup.json),
[workflow failure](evidence/resume-c1fb1c1f-workflow-failure.json) and
[workflow repair result](deferred-fixture-repair-report.md) remain unchanged.
Both old failure transcript hashes were read back unchanged at these retained roots:

- `F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d`
- `F:/framework-next/p7-runs/373-public/fn-290c21edfb594765b635b8d9bda1fcb9`

No old residue cleanup or unchanged test retry occurred. Record preparation first
encountered an absent historical complete-profile object; the result retains that
error and the corrected added-file comparison. No behavioral rerun followed it.

## Local handoff

Only this workflow's result/evidence/current-pointer records changed after execution.
JSON/YAML, UTF-8, links, exact stream hashes, scope/whitespace and complete
planned-message checks are retained in
[local validation](evidence/pr-cleanup-rerun-local-validation.json).
The containing local commit is the handoff identity. Workflow remains in progress
for coordinator integration and reconciliation of the separately bound results.

No other family, C5, full suite or native execution was selected. No repair,
push/PR/provider mutation, publication, adoption or CI activation occurred.
Unselected legacy/full/history/audit/lease/hosted gates remain `deferred-by-owner`
under U001, owned by program 322 coordinator / P7 until separately selected or
adopted. Direct resource fixtures do not establish candidate installation or adoption.
