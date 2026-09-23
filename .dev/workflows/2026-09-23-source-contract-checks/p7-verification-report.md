# Issue 368 selected P7 verification

Status: the authorized 12-method continuation completed locally in one execution:
12 passed, zero errors/failures/skips, exit 0. The eight historical core comparisons
remain separate. No same-invocation 20-method pass or whole-P7 acceptance is claimed.

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

The separately delivered public P7 observations are recorded below; coordinator
verification/integration remains pending. Native, versioned release, provider,
CI and other unselected obligations are outside this run, deferred-by-owner under
U001 where applicable; program #322 coordinator / P7 owns subsequent selection
and integration. Local completion does not close the GitHub Issue or Project.

## Actual result and identity binding

- Coordinator-selected integrated source: `e71712b71791170c3f4946e131ce867f82dade8f`.
- Preparation / executed commit: `29b0fafbf6cb4ac0a6caa57d24b841c8204241cd`.
- Worktree/branch: `F:/framework-next/368`, `codex/2026-09-23-source-contract-checks`.
- The source tree matches the selected integrated source. Product, runner and
  helper bytes did not change; only the accepted argument test and records/docs
  changed before execution. Execution began and ended on the same clean commit.
- Actual results are delivered in a separate local records-only commit. The
  final Git read-back supplies that delivery SHA; it is not another tested head.

[Exact execution JSON](evidence/p7-selected-execution.json) contains the executable,
full argv, HEAD/runtime, execution-file hashes, all raw stdout/stderr as lossless
base64 with SHA-256, observations and complete historical before/after inventories.
The [capture script](evidence/p7-capture.py) is preserved with its verified hash.
Readable [stdout](evidence/p7-selected.stdout.txt) and [stderr](evidence/p7-selected.stderr.txt)
normalize CRLF to LF only; exact stream identities belong to the JSON bytes.
The reconciliation JSON remains the preparation snapshot, not a stale current-run
status record.

One invocation ran all 12 selected methods, with no additional attempt:
**12 passed, 0 failures/errors/skips, exit 0; unittest 12.363 s, captured runner
12.652 s, parent fixture wall 12.408 s.** Outer timeout was 90 s and did not fire.
Python 3.13.14 / PyYAML 6.0.3 / jsonschema 4.26.0 / referencing 0.37.0 ran under
`-I -B`; Git was 2.55.0.windows.3 on Windows 11 build 26200. Dependencies were not
installed or changed.

C1 observed 18 owners / 113 payload members / 8 profiles, including logical
`complete` projection. C2's selected actual-source union/null-config projection
and three negative methods passed. C3's actual tiny Git regular/missing/nonregular
member checks passed. The corrected parameter method rejected 11 illegal choices
and parsed five valid choices (including contracts), with no public/native dispatch.

C5 performed two actual development Lesson assemblies, each with 9 payload files,
1 entry and 3 metadata files. The actual reader accepted matching content identity
with distinct run/time metadata and refused all five labelled synthetic corruptions.
The restored candidate read also passed. Observed candidate identity:

```text
development:29b0fafbf6cb4ac0a6caa57d24b841c8204241cd:5225533cf4e96438d4abf018411a9d6e62b6515e1b45b6d7207bf89adc5380ad
```

This is development Lesson evidence, not versioned release, other-profile physical
assembly, installation/apply, native trial or provider acceptance.

## Accounting and residue

| Observation | Observed files / logical bytes | Retained files / bytes at measurement | Authored bytes | Visible Git launches |
| --- | ---: | ---: | ---: | ---: |
| Parent selected run | 58 / 574013 | 57 / 574002 | 26 | 103 |
| Zero-config OS-temp probe | 1 / 5 | 1 / 5 | 5 | 0 |
| Synthetic failure/identity child | 1 / 26 | 1 / 26 | 26 | 0 |
| Synthetic contracts cleanup report | 2 / 45 | 2 / 45 | 45 | 0 |
| Synthetic public cleanup report | 2 / 45 | 2 / 45 | 45 | 0 |
| Actual readonly Git child | 3 / 167 | 3 / 167 | 0 | 2 |

The two synthetic cleanup reports intentionally expose cleanup-failed / exit 2
while asserting that counts remain from before the partial deletion. Those are
successful negative assertions; neither is a real public family execution. Their
remaining child files were subsequently removed by the guarded helper after the
assertions. No new failure is hidden by the overall successful result.

The audit counts 105 actual Git launches across parent and readonly child. Add one
Python test runner for 106 known test processes. The capture adds one Python
wrapper and seven read-only Git preflight/read-back calls: 114 known processes
including capture instrumentation, not a whole-session or opaque descendant count.
Per-run file/byte observations are retained separately, not added into a fabricated
physical-write or simultaneous-peak metric. All observed caps remained satisfied.

Successful owned parent
`F:/framework-next/p7-runs/368-contracts/fn-f78fb69941c2430fa45be32b8b24dfaf`
was removed; absence was read back and no new residue remains below that parent.
The existing zero-config probe also reported successful guarded cleanup.

Full file hashes, attributes, link counts, types, sizes, mtimes and device/inode
identities match before/after for all three old #368 runs:
`fn-a9713554a15d4ca68b38842026f3a8a8`,
`fn-7ce6045a9eae47e68aa3ecb5597100cc`, and
`fn-612302fba311482d98c4d8be0ad3a1a3` beneath the explicit 368 fixture parent,
and old PR residue
`F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d`.
No historical cleanup was performed.

## Bounded completion disposition

| Required result | Disposition |
| --- | --- |
| Current legal/illegal argument contract, parse only | Passed in the selected invocation; no other layer dispatch |
| Fresh C1/actual C2/real Git C3/development C5 evidence | Passed on the executed commit identified above |
| Current selected helper and cleanup/report integration | Passed, including truthful synthetic failure reports |
| Eight historical core assertions | Retained with the limited source/unit comparison; not re-executed or promoted to a whole-run pass |
| Exact output/runtime/accounting and immutable source binding | Captured; stream hashes and all 12 method names read back |
| Successful cleanup and old failed-run preservation | Passed read-back; full historical inventories unchanged |
| Current README/design and own workflow records | Updated; fixed Issue 373 handoff attributed separately, with coordinator verification/integration pending |
| Local result handoff | Separate records-only checkpoint; coordinator owns integration |

No unresolved failure remains in this selected #368 continuation. No new public,
native, versioned-release, legacy/package matrix or provider/CI run was performed.
Online Issue/Project closure and overall P7 admission remain coordinator-owned;
unselected U001 gates remain deferred-by-owner. The original failures and all
subsequent scoped results remain in their historical records.

## Public Issue 373 handoff

After the fixed #368 execution completed, the coordinator supplied peer delivery
`07b1778f3b6cfae689c98b10326b614149e437f3`. Read its exact Git blobs, without checkout/merge or another test run:

- Report: `.dev/workflows/2026-09-23-public-skill-checks/common-source-e71712b7-report.md`.
- Report raw SHA-256: `ae13e1e8653dbd29721ebd599d79e32114401fe332e7c79852b6797eb1ff4899`.
- Source execution commit: `e71712b71791170c3f4946e131ce867f82dade8f`.
- Owner supplied `public-readme-suggestion.txt`; its content is reflected in the
  shared test README with this fixed-commit reference. A relative link to the new
  owner report awaits integration of that owner's records; they are not copied.

The owner report records seven configured families, each passed once in a separate
invocation, with all selected C4/C6 and T1-T7 phases, no skips and successful
cleanup. Across the seven: **218 public + 37 driver Git = 255 measured driver
processes; 100.585 summed fixture seconds**. This is not one aggregate invocation;
218 public launches exceed its 160 cap, and the 130 conservative nested launch
reservations would bring driver-plus-reservation budgeting to 385, exceeding 256.
Actual opaque nested launches remain unavailable. Limits were not increased.

All 14 exact runner stdout/stderr streams are retained in that owner's records.
Successful cleanup removed the full child transcripts and synthetic-provider
bodies; summaries/hashes do not restore them. No complete child-body archive is
claimed. Earlier failures remain retained at their original source identities.

This is attributed peer evidence, not a #368 public run or independent parent
admission. The coordinator stated it is still checking the evidence; delivery
integration and Issue 373 closure are pending. The #368 fixed test subject was
not changed or rerun for this message. Actual provider/native/install/adoption,
CI and whole-P7 acceptance are not inferred from the seven family results.
