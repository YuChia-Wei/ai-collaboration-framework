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

The runner imports only `test_contracts.py` by exact path. Exit 0 requires all
selected tests successful with no skips and successful cleanup; 1 means test
failure; 2 means argument, dependency, setup or cleanup failure. Unexpected
exceptions also remain nonzero. Failed output is retained and its exact run path
and next action are printed; no auto retry. Results are unittest output plus
small JSON observations on stdout, not a universal acceptance receipt.

Reserved invocations (currently **exit 2 before allocation**, no green stubs):

```text
python -I -B tests/framework_next/run.py --layer public --family lesson
python -I -B tests/framework_next/run.py --layer public
python -I -B tests/framework_next/run.py --layer native-windows --native-root EXPLICIT_ROOT
```

The seven future family IDs are `lesson`, `adr`, `standards-promotion`, `pr`,
`local-backlog`, `software-development-orchestrator`, `problem-frame-author`.
Unknown layers/families fail. `--family` belongs only to public; `--native-root`
belongs only to native-windows and is mandatory there. No disposable setting
selects a native root. Later workers must implement those paths explicitly;
registration/presence cannot count as execution.

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
fail. The actual installation reader retains its separate strict-root check
and currently refuses the assigned F: backend.

The audit hook counts all subprocess launches made in this interpreter (including
GitSource's nested Git) and stops before launch 257. It cannot observe opaque
child-process grandchildren; future public/native workers must report those
separately or as unavailable. Builder tests currently invoke the actual owner
in-process, with its real Git subprocesses, not the CLI. Public builder/installer
entry acceptance remains distinct.

Accounting records maximum observed size per unique relative file at checkpoints,
current retained bytes/files, helper-authored bytes, processes by executable and
wall time. It is not cumulative physical I/O or a complete transient-write meter.
Tiny helper probes print separate counts before cleanup; combine those explicitly,
never hide them in the parent total. Fixed tiny fixtures are measured after each
material phase; file/byte checks are checkpoint limits, not filesystem quotas.
No giant 4 MiB boundary is selected here. No speed/wear/token claim is made.

## Selected scope and current limitations

C1 asserts exact 18 owners / 113 declared members / seven profile selections,
versions, destinations, Git bytes/modes, owner references and installed entry
links. C2 asserts v1/v2/v3 union, schema identities and null configuration without
invented stores/probes. Two implementation packages legitimately need an
authorized target editor. C3 covers synthetic selection negatives and one tiny
real Git fixture. C5 calls actual Lesson assembly twice and actual candidate
reader, with five labelled synthetic candidate corruptions; no apply/recovery.

The directly approved four-file repair preserves metadata semantics while
expanding PR/backlog aliases and handles the observed F: error in GitSource/
assembly. Committed-source execution now passes C1-C3 and completes two real
Lesson builds; the subsequent installation reader still refuses F: strict root
resolution, so C5 aggregate remains failing. Exact original and repaired
observations are retained in the
[repair report](../../.dev/workflows/2026-09-23-source-contract-checks/repair-report.md).
C4/C6, public families, native Windows, root adoption, independent review,
all-profile build acceptance, CI and publication remain separately assigned.
