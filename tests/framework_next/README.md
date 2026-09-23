# Selected framework source checks

Run from this source worktree with already provisioned Python >=3.11,<4,
PyYAML >=6,<7, jsonschema >=4.18,<5 and referencing. Nothing is installed.

```text
python -I -B tests/framework_next/run.py --layer contracts --output-root F:/framework-next/p7-runs/368-contracts
python -I -B tests/framework_next/run.py --layer contracts --case MetadataTests.test_c2_reject_version_types_and_duplicate_schema --output-root F:/framework-next/p7-runs/368-contracts
```

`--case Class.method` is repeatable; missing/unknown cases fail. Omit it for all
selected C1-C3/C5 and helper cases. No discovery of other tests, legacy validators,
profile build matrix or installed skill execution. Source blobs come from HEAD;
the executing assembly requires its source implementation to match that commit.
Fixture metadata is synthetic only where the test name/description says so.
The current contracts module contains 20 methods. The coordinator-selected P7
continuation executes only 12 methods once; eight historical core assertions
have a separate, limited byte-comparison record. See the
[P7 reconciliation and execution record](../../.dev/workflows/2026-09-23-source-contract-checks/p7-verification-report.md).
That combination is not a claim that all 20 methods passed in one invocation.

The contracts arm imports only `test_contracts.py` by exact path. Exit 0 requires all
selected tests successful with no skips and successful cleanup; 1 means test
failure; 2 means argument, dependency, setup or cleanup failure. Unexpected
exceptions also remain nonzero. Failed output is retained and its exact run path
and next action are printed; no auto retry. Results are unittest output plus
small JSON observations on stdout, not a universal acceptance receipt.

The bounded Issue 382 native selection uses its exact provisioned roots:

```text
python -I -B tests/framework_next/run.py --layer native-windows --native-root F:/framework-next/p7-runs/native-w01/382
```

The seven public family IDs are `lesson`, `adr`, `standards-promotion`, `pr`,
`local-backlog`, `software-development-orchestrator`, `problem-frame-author`.
Unknown layers/families fail. `--family` belongs only to public; `--native-root`
belongs only to native-windows and is mandatory there. No disposable setting
selects a native root. Registration/presence cannot count as execution.

## Public caller interface

```text
python -I -B tests/framework_next/run.py --layer public --family lesson --output-root F:/framework-next/p7-runs/373-public
python -I -B tests/framework_next/run.py --layer public --family lesson --public-read-only --output-root F:/framework-next/p7-runs/373-public
```

Select one family during development. Omitted `--family` explicitly selects all
seven, sequentially, with a separate verified child per family and shared public/
process ceilings. Aggregate stops on the first non-pass and names the remaining
unexecuted families; it may stop at a cap. `--case` remains
contracts-only. The public arm loads only its named family and shared public
assertions. It copies exact committed package resources through `git_blobs`,
retaining their relative paths and source manifest. These are **direct resource
fixtures**, not assembled or installed packages. Source-derived resource bytes
are separate from bounded authored request/config fixtures.

Stdout is JSON lines: `runtime`, one `public_family` per attempted family, then
`public_selection` / `outcome` / `exit`. Unittest details are stderr. Family rows
include completed/failed/unexecuted phases, public launch results, source commit,
raw transcript location and existing helper accounting. Transcript stdout/stderr
are losslessly base64 encoded. Public protocol success is `succeeded`/0 except
CBF `ok`/0; negative CBF exits retain their actual 2/3/4 meanings.

Runner exit **0** requires every selected phase, no skips and successful cleanup;
**1** means failed or partial selected work; **2** means argument, dependency,
import, setup or cleanup failure. A missing module cannot pass. Explicit
`--public-read-only` executes independent C4/C6 assertions and stops before the
write-dependent round-trip; it **always remains partial/nonzero**, even if unittest
prints `OK (skipped=1)`. It does not satisfy a full family gate. Invalid explicit
output roots never fall back. All failed/partial residue remains owned by its run.

One sequential family test stops its dependent cases at the first failure.
The PR fixture has two commits/one tracked UTF-8 file. Its provider cases use the
unchanged adapter with a bounded synthetic `run_bounded` transport and an extra
subprocess denial guard; they cannot establish live provider acceptance. No tool
fabricates a validate operation for PR/backlog/workflow. Backlog follows actual
`draft -> planned -> in_progress -> completed` states.

The helper counts driver subprocesses. Opaque child launches are reported
unavailable; the public assertions reserve conservative source-derived nested
launch ceilings, separately labelled as bounds, not measurements. The one selected
4 MiB+1 Lesson input is transient stdin and separately counted when executed.
No physical-I/O, performance or token inference is made.

Public evidence belongs to Issue 373. Its [initial report](../../.dev/workflows/2026-09-23-public-skill-checks/report.md),
[later family observations](../../.dev/workflows/2026-09-23-public-skill-checks/resume-c1fb1c1f-report.md),
and [focused PR cleanup rerun](../../.dev/workflows/2026-09-23-public-skill-checks/pr-cleanup-rerun-report.md)
retain their own source identities, failures and scoped passes. The original
writer/root and metadata failures are historical observations, not current
universal blockers. Fresh public results for the selected P7 source are
**pending Issue 373**. Source-contract or parser success does not establish
public family, installation, live-provider or hosted CI acceptance.

## Small helper interface

`support.REPOSITORY` is this checkout, `PYTHON` is the executing interpreter.
The runner adds this checkout's `src` and test directory for imports under `-I`.

- `FixtureRun(output_root=None, *, environment=None)`: CLI root overrides
  `FRAMEWORK_TEST_OUTPUT_ROOT`; otherwise OS temp. Ignores
  `AI_CONTEXT_TEST_TMP_ROOT`, never scans drives or changes TEMP/TMP. An explicit
  parent may be created only as one new leaf under existing direct ancestors.
- `run.root`, `run.case(simple_name) -> Path`: one exclusive `fn-<uuid>` run,
  exclusive named case directories. Duplicate case names fail.
- `run.write(absolute_path, bytes) -> Path`: exclusive tiny file under an existing
  owned parent, <=16 KiB each / <=1 MiB authored total. Source-derived builder
  output is accounted separately by observation; never treat it as authored data.
- `run.measure() -> dict`, `run.close(success) -> dict`: direct-ancestor and
  identity checks, <=256 observed files / <=16 MiB retained bytes. Success cleans
  only the unique verified run. Failure retains it; the caller must record and
  inspect it before separately authorizing cleanup. Parent is never deleted.
  A registered regular single-link readonly file may be retried once after fresh
  path/ancestor/identity/attribute checks. Other errors and link/reparse/drift
  observations remain failures. `FixtureCleanupError.accounting` retains the
  measured `before-cleanup` counts even after partial deletion; both contracts
  and public reports keep a cleanup failure nonzero.
- `use_run(run)` / `active_run()`: narrow context used by runner and tests.
- `run_process(argv, *, cwd, input=None, timeout=30) -> CompletedProcess[bytes]`:
  no shell, bytes I/O, <=8 MiB post-capture output check. This is for bounded
  trusted tools, **not** a streaming output limiter or process sandbox.
- `git(*args, cwd=REPOSITORY, input=None) -> bytes`: no replace/lazy fetch/prompt,
  30-second timeout, explicit `-C`; environment is sanitized of inherited GIT
  variables. Shell cwd remains the source checkout. No fetch, copy or hooks.
- `git_blobs(full_commit, exact_src_paths) -> dict[str, Blob]`: two batch Git
  reads with mode, name, size and Git-object digest checks; no production format
  parser. Tests pass those actual immutable blobs to the sole owner readers.
- `runtime_versions() -> dict`: reports and checks existing dependencies.

Fixture ancestry uses lstat, refuses links/reparse points, ambiguous paths,
source containment and drive roots, then uses an absolute direct path. It does
not require Windows' optional final-path API. The approved GitSource/assembly repair uses a narrow Windows error-1 fallback
only after direct ancestor and stable device/inode checks; other errors still
fail. The installation reader has its own guarded Windows error-1 fallback,
including stable ancestry and independent canonical-name/drive checks. The
previous F: reader blocker was resolved for the historical C5 case on
`c1fb1c1fb07a6d246e3bcedd3cd851918f66b306`. Later versioned-candidate and directory
observation changes require the separately selected P7 C5 execution; no fallback
permits aliases, links/reparse points or a silent change of root.

The audit hook counts all subprocess launches made in this interpreter (including
GitSource's nested Git) and stops before launch 257 per active run. It cannot observe opaque
child-process grandchildren; public/native workers report those
separately or as unavailable. Builder tests currently invoke the actual owner
in-process, with its real Git subprocesses, not the CLI. Public builder/installer
entry acceptance remains distinct.

Accounting records maximum observed size per unique relative file at checkpoints,
retained bytes/files at measurement, helper-authored bytes, processes by executable
and wall time. Close observations are labelled `before-cleanup`, including when
cleanup later fails; they are not a count of the partial residue left afterward. It is not cumulative physical I/O or a complete transient-write meter.
Tiny helper probes print separate counts before cleanup; combine those explicitly,
never hide them in the parent total. Fixed tiny fixtures are measured after each
material phase; file/byte checks are checkpoint limits, not filesystem quotas.
No giant 4 MiB boundary is selected here. No speed/wear/token claim is made.

## Selected scope and current limitations

C1 asserts exact 18 owners / 113 declared members / eight profile selections,
versions, destinations, Git bytes/modes, owner references and installed entry
links. C2 asserts v1/v2/v3 union, schema identities and null configuration without
invented stores/probes. Two implementation packages legitimately need an
authorized target editor. C3 covers synthetic selection negatives and one tiny
real Git fixture. C5 calls actual Lesson assembly twice and actual candidate
reader, with five labelled synthetic candidate corruptions; no apply/recovery.

The directly approved four-file repair preserves metadata semantics while
expanding PR/backlog aliases and handles the observed F: error in GitSource/
assembly. The historical repaired run passed 16 of 17 methods; its reader failure
was later followed by one successful C5-only run. Read both outcomes in the
[repair report](../../.dev/workflows/2026-09-23-source-contract-checks/repair-report.md).
The added `complete` profile selects all 18 owners / 113 payload members; logical
projection is distinct from physical assembly of that profile. C5 remains the
two-build development Lesson case, not a versioned-release or all-profile matrix.

The [P7 record](../../.dev/workflows/2026-09-23-source-contract-checks/p7-verification-report.md)
tracks the newly selected 12-method execution and the separate eight-assertion
historical comparison. Do not relabel the older 16/17 or C5-only result as a
current all-contract pass. Public results remain pending Issue 373; native,
versioned distribution, target adoption, independent review, CI and publication
retain their respective owners and evidence boundaries.

## Native Windows caller interface (Issue 382)

This selection is bound to the clean committed `F:/framework-next/382` source,
`lesson-minimal` development candidate, and the exact native parent above. Before
calling, explicitly provision that parent and these two ignored/untracked parents:

- `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n382/recovery`
- `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n382/observations`

No environment fallback, global temp changes, dependency install or drive discovery.
Each call exclusively allocates one short child under each parent. The engine stays
outside fixtures. Only process termination with OS/storage available is selected.
A future caller must reconcile these fixed bindings; this is not a generic hosted
Windows acceptance route. `--case` and `--output-root` are rejected for native.

The driver builds once with the real builder, then invokes the unmodified public
`maintain_framework.py` using `-I -B` and the complete raw EnginePin. Six result rows
cover inspect/plan/pin refusal, fresh apply, same-content no-op, drift/collision
refusal, a second process holding the real native guard, and one notification-based
public interruption attempt with exact same-engine finish when attributable. The
small copied drift setup is labelled synthetic; its public refusal is real. There
are no product hooks, inserted delays, simulated successful applies or retry loop.

Stdout is one JSON object with `native_windows`, interface `native-windows/382-v1`,
source/pin/command, fixed selection, per-case outcomes, unexecuted cases, launches,
counts, residual paths and cleanup ownership. Exit 0 requires all six rows passed;
1 means failed or partial (including `not-observed` interruption); 2 means setup or
accounting/cleanup failure. Product failure stops dependent cases. Raw requests and
base64 stdout/stderr stay in durable `calls.jsonl`; `result.json` is the observation.
The isolated command/pin and unchanged cache inventory are native observations;
adversarial cache-loader tests are separate synthetic evidence. No project readiness,
whole-P7, versioned candidate, stable upgrade, CI or target adoption is inferred.

Caps are two simultaneous owned children, 30 public/helper launches, three durable
operation roots, 256 observed created file names and 16 MiB retained logical output.
Driver Git launches are counted separately; opaque product grandchildren and total
transient creations are explicitly unavailable. Counts are not performance claims.
All successful and failed fixture/recovery/observation outputs are retained.
The coordinator owns later disposition; no prior run or recovery cleanup is done.

Native evidence: [Issue 382 original report](../../.dev/workflows/2026-09-23-native-maintenance-checks/report.md)
and [resumed observations](../../.dev/workflows/2026-09-23-native-maintenance-checks/resume-report.md).
Those results retain their exact source pins and residual dispositions; the
current #368 contracts selection does not execute native maintenance.
