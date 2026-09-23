# Issue 368 selected P7 verification

Status: source prepared; the selected execution is pending. No prospective pass.

## Authority and source

Original #368 Astra/ultra task under program #322 U001. The coordinator accepted
the read-only reconciliation and authorized this bounded continuation after its
reported target-pilot admission. That parent status is attributed to coordinator
`01a0ce78-db26-74e1-a615-2bd0599f7d0c`, not independently verified here.

Verified clean `eb28d0b6290e257f9da187318efb3efe76a9cb9c` on the original
`F:/framework-next/368`, branch `codex/2026-09-23-source-contract-checks`, and
fast-forwarded only to selected `e71712b71791170c3f4946e131ce867f82dade8f`.
The later coordinator-only main commit is not substituted. No agent, new task,
push, provider mutation or C: checkout edits are selected.

The only executable change corrects the old argument-test expectation: valid
public/native choices are parsed without calling main, dispatching another layer
or allocating a native root. All previously invalid cases stay rejected; illegal
public case/native-root and native case/output-root combinations are explicit.
Runner, helper, product files and profile expectations retain integrated bytes.

## Evidence reconciliation

[p7-reconciliation.json](p7-reconciliation.json) records exact selectors, 32
unchanged source/unit bindings, helper proof, source tree, caps and scope limits.
Eight historical core assertions have identical selected input/definition bytes:
two synthetic metadata methods, two synthetic selection methods, three path
admission methods, and the 17-scenario readonly refusal method. This is a limited
core assertion comparison, not complete runner/environment reuse and not eight
new test executions. The helper and package path/link/reparse guards are retained.

C1/actual-source C2 need fresh observation of eight profiles and changed resource
bytes. C5 crosses changed assembly/versioned identity and reader directory
observation code. The existing runner integrations and actual Git fixtures also
need fresh evidence; original Git binary/environment identity is unavailable.
The historical 16/17 run and single later C5 pass remain distinct in
[repair-checks.json](repair-checks.json). [Cleanup evidence](cleanup-repair-checks.json)
remains historical and unchanged.

## Selected execution contract

Commit the preparation before execution; bind the call to that clean immutable
commit and preserve its actual HEAD/runtime, complete stdout/stderr and hashes.
Execute the exact 11 selectors (12 methods) in the JSON once from this worktree,
using `python -I -B tests/framework_next/run.py --layer contracts` and explicit
`--output-root F:/framework-next/p7-runs/368-contracts`. Outer timeout is 90 seconds;
15-25 seconds is an estimate from prior observations, not a performance result.

Keep the existing per-run caps: 256 observed files, 16 MiB retained bytes,
16 KiB per normal authored file, 1 MiB authored total, 256 visible subprocesses
per active run; Git calls time out after 30 seconds. Output checks are bounded
post-capture checks, not streaming or filesystem quotas. Tiny nested helper probes
report separately; never silently hide them in the parent accounting. The
zero-configuration test includes its existing one tiny OS-temp allocation.

Preserve all existing failed fixtures. Failure, timeout or missing evidence stops
this selected attempt and returns to the coordinator; no repair/retry or expanded
public/native/legacy/package matrix follows it automatically. Capture errors and
partial output remain evidence, never a pass.

## Completion conditions

- Correct parser-only expectations and preserve every illegal-combination guard.
- Retain path/link/reparse protection and original metadata semantics.
- Observe the selected 12 methods on one clean committed source, with no skips,
  complete raw output and accounting, or report the exact stopped outcome.
- Keep the eight historical core comparisons separate from the actual execution.
  Do not claim a same-invocation 20-method pass.
- Read back successful cleanup or retain failed residue; compare historical runs.
- Update own records and current README/design wording, commit actual results
  separately, and return selected-source, executed and delivery commit identities.

Public P7 results remain pending Issue 373. Native, versioned release, provider,
CI and other unselected obligations are outside this run, deferred-by-owner under
U001 where applicable; program #322 coordinator / P7 owns subsequent selection
and integration. Local completion does not close the GitHub Issue or Project.
