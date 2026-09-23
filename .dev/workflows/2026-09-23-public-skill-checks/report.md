# Public checks: local checkpoint, acceptance incomplete

Issue 373 delivers the public dispatch arm and seven selected family test bodies.
There is **no complete T1-T7 round-trip pass**. Five families completed independent
C4/configuration and C6/executable-binding assertions; these are partial results,
not family acceptance. Source/helper/schema/metadata remain unchanged at
`f8f0d073e6442df8a280c5941a2c7a1d6ed7060b`. No assembly, installation, native trial,
provider call, CI, root adoption or publication was performed.

## Caller interface for Issue 369

From the explicit assigned source workdir:

```text
python -I -B tests/framework_next/run.py --layer public --family <id> --output-root F:/framework-next/p7-runs/373-public
python -I -B tests/framework_next/run.py --layer public --family <id> --public-read-only --output-root F:/framework-next/p7-runs/373-public
```

IDs: `lesson`, `adr`, `standards-promotion`, `pr`, `local-backlog`,
`software-development-orchestrator`, `problem-frame-author`. Omitted family means
explicit aggregate; it stops at the first failure/partial result or resource cap
and lists `unexecuted_families`. No aggregate was executed here. Prefer affected
family selections; a cumulative cap stop is not passing aggregate evidence.

Stdout contains JSON lines: `runtime`, `public_family`, then `public_selection`,
`outcome`, `exit`, `unexecuted_families`. Family rows retain phase dispositions,
calls/actual diagnostics, raw-stream transcript, source commit and accounting.
Stderr is unittest detail, including original exceptions/tracebacks. Exit 0 needs
all selected phases, no skips and successful cleanup; exit 1 is failed/partial;
exit 2 is argument/dependency/import/setup/cleanup failure. Explicit read-only
selection always returns nonzero, including unittest's `OK (skipped=1)`. A missing
selected module or unexecuted phase cannot be admitted as passed. Contracts and
reserved native semantics remain separate. No invented validation command exists.

`capture-family.py` is an Issue-local stream capture command, not a fixture
framework or gate. Its saved `.json` records exact argv/cwd, child exit and test
file hashes. All fixtures use the unchanged `support.py`, raw committed Git blobs,
their actual relative layouts and a source manifest. They are direct package
resource fixtures, not assembled or installed packages.

## Actual executions

All commands use the explicit output parent above. `RO` adds
`--public-read-only`; `full` omits it. Every allocated run is retained.

| Family / selection | Public calls | Driver Git | Files | Retained logical bytes | Outcome / runner exit |
| --- | ---: | ---: | ---: | ---: | --- |
| Lesson full | 3 | 4 | 12 | 129027 | explain/query succeeded; create unsupported; 1 |
| ADR first full | 6 | 4 | 14 | 131740 | C4 test expected wrong version outcome; 1 |
| ADR RO corrected | 16 | 4 | 15 | 218992 | C4/C6 complete; round-trip unexecuted; 1 |
| Promotion RO | 16 | 4 | 16 | 248796 | C4/C6 complete; round-trip unexecuted; 1 |
| PR RO | 1 | 4 | 13 | 126915 | explain rejected committed YAML anchors; 1 |
| Workflow RO | 16 | 4 | 17 | 256880 | C4/C6 complete; round-trip unexecuted; 1 |
| CBF first RO | 6 | 4 | 16 | 105012 | C4 test expected wrong version outcome; 1 |
| CBF RO corrected | 16 | 4 | 17 | 163442 | C4/C6 complete; round-trip unexecuted; 1 |
| Lesson RO | 18 | 4 | 16 | 224910 | C4/C6 including v1/v2 config distinction complete; round-trip unexecuted; 1 |
| Backlog | 0 | 0 | 0 | 0 | not executed: verified shared metadata/parser failure |

An earlier sandbox allocation refusal had zero public calls and no run child;
the same F: selection proceeded only after scoped sandbox escalation. A workflow
directory creation refusal was similarly resolved with scoped permission; no
public tool ran during that preparation failure. Initial evidence is retained in
[initial-attempts.json](evidence/initial-attempts.json).

The two harness expectation failures are retained beside corrections. Ordinary
record tools reject boolean/float config versions with `unsupported`; CBF uses
`unsupported-version`/2. This was a test correction, not product remediation.
No failed Lesson create or shared writer setup was retried. Coordinator explicitly
allowed independent read-only cases and accepted T5's actual public sequence
`draft -> planned -> in_progress -> completed` in place of the design's conceptual
active wording. Backlog source transition requirements were not changed.

Across nine allocated runs: **98 public Python launches + 36 helper Git launches**,
136 observed files, 1,610,634 maximum-observed logical bytes, 1,605,714 retained
bytes and 78,672 helper-authored bytes. Every individual normal authored input
stayed <=16 KiB; source-derived scripts/resources are separately copied bytes.
No public record was published; no PR Git fixture or provider simulation reached
execution; the selected transient 4 MiB+1 input remains unexecuted. Capture
drivers launch one runner each outside helper accounting (eight captures,
including the first ADR inline capture); the initial Lesson runner was direct.
These counts exclude interactive discovery/commit tools and are not physical I/O.
Opaque grandchildren are **unavailable as measured counts**. Conservative
source-derived nested ceilings are separately recorded; they are not observations.
No physical-write, speed, wear or token inference is made.

Exact per-run argv, hashes, times, calls and residue are in
[observations.json](evidence/observations.json) and the corresponding `.stdout`,
`.stderr`, `.json` captures. [raw-streams.json](evidence/raw-streams.json) retains
lossless base64 of captured streams and all nine public transcripts, independently
of Git text newline conversion. Failed/partial cleanup is intentionally not attempted.
The F: fixture copies remain volatile; coordinator must inspect before any
separately authorized cleanup. The source predicate record and minimal exact
refusal streams are tracked durably here.

## Product and environment findings

1. **Observed Lesson volume-query refusal.** Actual public `create` returned
   `unsupported`, code `filesystem`, `mutation_state: none`, no directories created.
   [Exact response bytes](evidence/lesson-create.response.bin) have SHA-256
   `f04781a4012bc54c45c8bbba635098bd257f1f5a763688bc038b667fac0d2f28`.
   The predicate at `src/skills/lesson/scripts/lesson.py:354` is
   `not GetVolumeInformationW(root.value, None, 0, None, None, None, filesystem, len(filesystem)) or filesystem.value != "NTFS"`.
   `root.value` is populated by `GetVolumePathNameW(str(existing_store_ancestor), ...)`;
   the code separately checks drive type 3 or 6. The response alone does not
   distinguish query failure from a non-NTFS string. No extra native probe was run.
2. **Verified shared writer source.** Lesson, ADR, promotion, PR, backlog and
   workflow `local_write_backend` have identical function-source SHA-256
   `3f9fb0edbf32c0d3f8099d6be240d62c6a51821415d0ef5c51f8d7ef6a811e35`.
   CBF has a distinct `local_backend`, with the same Windows volume-query inputs
   and successful-query-plus-NTFS predicate. Its native behavior remains
   unobserved. Shared source is grounds to leave affected writes unexecuted, not
   to claim six/seven observed writer failures.
3. **Observed PR metadata incompatibility; backlog source-bound impact.** PR
   `explain` returned `invalid-input / yaml-token` before any Git/provider action.
   [Exact response bytes](evidence/pr-explain.response.bin) have SHA-256
   `592fbcb37e6c113808d6632e319bc8239cb651a8df2b019f13ba488f6811a924`.
   Both committed metadata files contain AnchorToken/AliasToken; their `parse_yaml`
   function sources are identical and reject those tokens. Backlog was not invoked.
   Small repair targets remain those two metadata resources in their original
   owning task, not this executor.

[source-predicates.json](evidence/source-predicates.json) binds exact source
locations, function digests, Windows call source and metadata token locations.
The smallest writer repair investigation belongs to these owner functions and
their root input construction; source evidence does not establish a driver cause
or authorize relaxing the NTFS guard.

Coordinator separately reported read-only OS inventory at 16:12:33 +08:00:
DriveInfo(F:/) NTFS/Fixed/Ready; CIM access denied; a later scoped native inventory
returned `F:\framework-next\` from GetVolumePathNameW, then GetVolumeInformationW
failed with last-error 144; strict Path.resolve still failed WinError1. These are
**coordinator-attributed inventory**, not this task's product run, independent
diagnosis or native acceptance. No settings/root/guard changes follow from them.

## Remaining work and handoff

Direct Python AST, JSON/YAML parsing, changed Markdown references and diff checks
passed. Removing only the new public dispatch branch leaves the contracts `main`
AST identical to the starting commit; excluded helper/contracts/engine test files
remain unchanged. Four bounded CLI checks returned 2 before public invocation:
invalid explicit output root, native still reserved, unknown family and public
`--case` rejection. [direct-checks.json](evidence/direct-checks.json) records the
actual commands and output. No legacy validation suite was run.

All seven minimal round-trips and selected dependent negatives have test bodies,
but remain behaviorally unestablished. This includes decisions/derive/supersession,
promotion reconciliation, PR real Git plus synthetic transport, backlog lifecycle,
workflow failure/deferral history and CBF exact inventory/negative cases. Later
test-only additions (boundary input, malformed sibling, stale ADR decision and
aggregate accounting/fail-fast) received direct syntax/source inspection only;
earlier captured test hashes are preserved, not relabelled as final-byte passes.

Next owner: program 322 coordinator. Inspect this checkpoint, decide the separately
owned metadata/volume-query repairs, then select only affected fresh family runs
on a containing source checkpoint. Do not restart the full matrix unchanged or
claim RO exit 1 as acceptance. Issue 369 may bind only the actual interface above.
This handoff grants no push, PR, merge, Issue/Project mutation, CI restoration,
native installation, root adoption, release or downstream adoption.

U001 keeps all unselected legacy/full/history/upgrade checks, formal audit/lease
machinery and hosted validation **deferred-by-owner**, responsible owner program
322 coordinator / P7; next action is separate selection/adoption. Workflow stays
in progress with truthful partial execution, not completed acceptance.
