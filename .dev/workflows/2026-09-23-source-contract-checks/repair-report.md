# Approved repair continuation

Latest: the single affected C5 rerun after #378 passed on
`c1fb1c1fb07a6d246e3bcedd3cd851918f66b306`; see the final section. Earlier
results and blocked observations below remain historical evidence.

The user's direct confirmation in the original Issue #368 conversation approves
GitSource/assembly path repair and PR/local-backlog alias expansion while keeping
path/link/reparse protections and original data semantics. The prior automatic
rejection and original failures remain in [the historical report](report.md).
No bypass occurred: repair resumed only after this direct user instruction and
fresh live Issue read-back. Starting local HEAD:
`070a47335ffce99d31bd83e487447942539e4a9f`.

## Bounded implementation

- Expanded only existing aliases in two metadata files. Recursive exact type,
  value, mapping-key order and list-order equality passed against the original
  committed blobs; package version/member/operation semantics are unchanged.
  The actual owner loader accepts both repaired working files. Proof and raw
  checkout hashes are in [metadata-alias-expansion.json](evidence/metadata-alias-expansion.json).
- `git_source.direct_directory` keeps strict resolution normally. Only Windows
  error 1 permits the explicit absolute spelling after lstat of every ancestor;
  each must be a plain directory without links/reparse points, have usable
  device/inode identity, and retain that identity after resolution. Traversal,
  network/device paths and ambiguous Windows names/short aliases are rejected.
  Missing, permission and other unsupported errors are not swallowed.
- GitSource compares the actual Git root path and device/inode with its admitted
  repository. Assembly retains its no-link check and rejects source containment
  both lexically and by ancestor identity, including alternate drive spellings.
  No new module, EnginePin member, format, backend guarantee or global monkeypatch.
- Three focused path methods passed (0.005 s): actual direct F: directory and
  invalid roots; output containment; labelled synthetic link/reparse/identity
  drift/error branches. Synthetic doubles do not prove native link/process
  behavior. Observed helper allocation: one file / 15 bytes, zero subprocesses;
  successful cleanup. The subsequent committed-source results appear below.

Source scope is exactly `src/distribution/git_source.py`,
`src/distribution/assembly.py`, `src/skills/pr/skill-package.yaml`, and
`src/skills/local-backlog/skill-package.yaml`; tests and issue-owned records are
updated in the original assignment. Installation state/writer/IO/coordination
remain untouched. The reader has its own strict-root check and remains a
potential independent residual; no success is forecast.

## Committed execution and remaining boundary

Repair subject: `379213a1f575aff143fb29b665c42fe5f24b219c`.
Actual command (workdir `F:/framework-next/368`):

```text
python -I -B tests/framework_next/run.py --layer contracts --output-root F:/framework-next/p7-runs/368-contracts
```

Result: **17 methods / 16 successful / one error / zero skips; exit 1**.
C1 now passes exact owner/metadata/member/version/reference/projection comparisons
for all 18 packages / 113 payload members / seven profiles. Real C3 GitSource
regular/missing/nonregular member and wrong-root/traversal checks pass. C2 and
all three path-protection regressions pass.

C5 performed **two actual Lesson assemblies** from that committed repaired
source. Both emitted exactly 13 files (9 payload + 1 entry + 3 metadata). Tests
read all emitted bytes, compared payload against actual selected Git blobs,
compared full mode/size/hash inventories, required identical selection/files
bytes, independently recalculated candidate identity inputs/hash, and observed
different run IDs/completion timestamps. Identity:
`development:379213a1f575aff143fb29b665c42fe5f24b219c:23ae30cd50a229afb8be6612e023a0eb51ad57072b13a48356f0698ad86fb220`.

The subsequent actual `installation_state.read_candidate` invocation failed at
`src/distribution/installation_state.py:208`, inside `_root`, on its separate
`Path.resolve(strict=True)` call: Windows error 1. This is now actual reader
failure evidence, rather than the earlier predicted downstream block. The
reader/mutation-refusal part of C5 remains **blocked-by-environment**; no native
admission, plan/apply/recover, or complete C5 pass is claimed. Installation files
remain outside the approved four-file repair and were not changed. Coordinator
must assign a compatible reader-root repair/decision and affected independent
review before completing acceptance; do not route candidates to another drive
or patch the reader from the caller.

Full new [stdout](evidence/contracts-repaired.stdout.txt),
[stderr](evidence/contracts-repaired.stderr.txt), and
[counts/hashes](repair-checks.json) are retained alongside original failures.
Only text line endings/trailing whitespace were normalized; original captured
hashes are recorded. No repeated selected run followed this unchanged residual.

Runtime remained Python 3.13.14 / PyYAML 6.0.3 / jsonschema 4.26.0 / referencing
0.37.0; no dependency installation. Unittest: 13.796 s; helper lifetime: 13.842 s.
Main run: 58 observed/retained files, 556829 observed/retained logical bytes,
30 helper-authored bytes, 103 actual Git subprocesses. Two cleaned helper probes
add 2 files / 31 bytes; combined observations 60 files / 556860 bytes / 61
helper-authored bytes. Add the Python runner for 104 known execution processes.
All selected caps remained within bounds. These are checkpoint logical counts,
not physical I/O, SSD wear, speed or token evidence.

Retained run: `F:\framework-next\p7-runs\368-contracts\fn-612302fba311482d98c4d8be0ad3a1a3`. It contains both real candidates and
scratch output. Preserve it until the coordinator records/authorizes inspection
and cleanup; previous failed runs also remain. Durable evidence is retained in
Git. The existing helper interface and reserved public/native failures are
unchanged. No profile beyond Lesson was physically assembled.

Changed EnginePin bytes require affected independent review; original-source
#370 cannot cover this repair. Native/root/CI/all-profile/independent/provider
acceptance remains unclaimed. Other U001 obligations remain deferred-by-owner,
owner program #322 coordinator / P7, next action separately select execution.

## Single affected C5 rerun after Issue 378

Coordinator `01a0ce78-db26-74e1-a615-2bd0599f7d0c` resumed this original
Astra/ultra task under U001. Verified clean preserved worktree
`F:/framework-next/368` on `codex/2026-09-23-source-contract-checks` at
`e71ccc989c3ae213a8e04cbe51abb80183022024`, proved the assigned target was
available locally and a descendant, then fast-forwarded that existing branch to
`c1fb1c1fb07a6d246e3bcedd3cd851918f66b306` (GitHub merge commit for PR #380).
No fetch or C: checkout edit; the worktree continues to use its existing
persistent shared Git database. No new task, agent or callback was used.

Executed exactly once, on the clean assigned source:

```text
python -I -B tests/framework_next/run.py --layer contracts --case CandidateTests.test_c5_two_real_lesson_builds_and_reader_refusals --output-root F:/framework-next/p7-runs/368-contracts
```

**One method passed, zero errors/skips, exit 0, 10.725 s**. Two actual Lesson
assemblies emitted exactly 13 files each (9 payload, 1 entry, 3 metadata).
Selection/files bytes, mode/size/hash inventory and independently recomputed
content identity agreed, with distinct run IDs/timestamps. The actual candidate
reader accepted both complete candidates. Five labelled synthetic corruptions
were refused: missing completion, changed payload, changed inventory hash,
unexpected extra file and missing payload. Final restored candidate read passed.
These reader calls are real; mutation inputs are synthetic. No plan/apply,
maintenance process, installation or native trial was invoked.

Candidate identity:
`development:c1fb1c1fb07a6d246e3bcedd3cd851918f66b306:262bede9ed874a1dbdb15b3d1f61871d4dfb4a136b600b795de192c5446ac2f6`.

[Existing repair-checks.json](repair-checks.json), field `post_378_c5`, retains
exact argv/source/attempt count, stdout/stderr and SHA-256, runtime and measured
counts; earlier fields are unchanged historical evidence. Runner runtime remains
Python 3.13.14 / PyYAML 6.0.3 / jsonschema 4.26.0 / referencing 0.37.0. The
capturing wrapper ran the exact argv with a 90-second timeout; no retry occurred.

Measured within the test: 89 Git subprocesses; 90 processes including the Python
runner. The capture wrapper plus its two read-only Git preflight calls add three
known processes, giving 93 including that instrumentation. Helper lifetime
10.832 s; captured execution 11.440 s. Observed 51 unique file paths / 573579
logical bytes, including the transient 11-byte extra-file negative. Just before
successful cleanup: 50 files / 573568 bytes. These stay within selected caps;
they are checkpoint logical counts, not cumulative physical-write or performance
evidence. No dependencies were installed.

Successful run `F:\framework-next\p7-runs\368-contracts\fn-11e0762f5bfb4ad4b485d881bc4a7769` was removed by the
existing verified-owned-run cleanup and its absence was read back. The three
older failed runs were preserved; recorded root device/inode and mtime values
match before and after execution. No old residue cleanup was performed.

The prior F: reader failure is resolved for this specific C5 case on this source.
This run does **not** establish a fresh whole-contract result, full rc.1 target
pilot, broader gates, native/install/apply acceptance, independent review,
provider/CI success, Issue/Project closure or root adoption. No source, helper,
test or runner was edited after the assigned fast-forward. Only existing
Issue-owned workflow/report records receive this handoff; coordinator owns
subsequent assignments and online integration. Unselected gates remain
**deferred-by-owner**, U001, owner program #322 coordinator / P7, next action
select the full rc.1 target pilot and subsequent broader checks separately.

## Subsequent bounded helper follow-up

The later coordinator assignment after the C5 record at `bd40c830` is documented
in [readonly cleanup repair](cleanup-repair-report.md) and
[its exact observations](cleanup-repair-checks.json). It repairs the separate
#373 fixture cleanup failure. The C5 results above remain historical; no C5 or
PR-family rerun was performed in that follow-up.
