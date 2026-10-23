# Snapshot Engine closure repair

Current continuation: PR494 advanced `main` to `aa8bf7c934efa17e15f925befec3b12f77b58998`.
The owner explicitly requested compatibility reconciliation and affected validation.
Use branch `codex/492-snapshot-engine-closure-cont-02`; the earlier local handoff
below remains historical evidence, not a current-source build claim. See the
successor section at the end for current progress and the #491 gate relationship.

Issue: [#492](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/492).
Template: `.dev/workflows/2026-10-22-domain-architecture-split/template.md` @ 1.0.0.

The user authorized isolated local repair, tests and a reviewable handoff. Push,
PR creation, integration, publication, source self-upgrade and Issue closure are
excluded. Issue synchronization is limited to technical cause, scope and acceptance results; internal execution records remain local. One tracked writer owns this
clone; independent workers and reviewers are read-only.

## Subject and cause

Initial base: `a7ecb86e6b65d55e2447e43d86ad1497530135f6` (`main`, initial provider read-back).
Registered original checkout: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`.
It was clean, with three existing unrelated worktrees. This work uses a separate
clone at `C:/Users/h4227/Documents/Codex/2026-10-23/task/snapshot-repair`, branch
`codex/492-snapshot-engine-closure`. The original checkout remains untouched.

The two current product `ENGINE_FILES` literals agree on 29 sorted product-source
members. Both release transport checks still require exactly 23; synthetic
23-member fixtures concealed this drift. The source-project installed lock instead
pins a historical 27-member Engine and remains a separate unchanged installation.
The current README template also carries the obsolete 23-member assertion.

Hosted run 39880520986, job 120176528494 failed before invoking the catalog builder.
The complete snapshot upload was skipped and diagnostics matched no files.
This establishes no defect in published v0.20.2 assets. Earlier run 39824921822 has
the same reported failure; chronological proximity does not assign fault to PR #489.

## Plan and validation selection

Use the installed diagnostic, local implementation and orchestration instructions.
Replace cardinality assumptions with exact agreement among the selected source
declarations, pin and archived closure. Preserve path, bytes, hashes, descriptor,
source identity and archive completeness checks. Capture the release wrapper's
own stdout/stderr before invocation so early failures have diagnostics.

The one coherent repair includes immediate positive/negative release regressions,
both direct workflow callers and count-free product README wording. The release
suite is required by changed release semantics. One exact clean-head build and
bundle verification is required by Issue acceptance. A local default suite is
selected once for integration because the README is packaged product input and
the shared verifier is used by both snapshot and draft transport. No installation,
upgrade, provider write or publication test is selected. An immutable local commit
will receive scoped independent review because release packaging is affected.

This small workflow preserves unique immutable-review and cross-session handoff
state; it is one bounded outcome, not a new release lifecycle. Linear integration
would suffice when separately authorized; no provider action is selected here.

## Evidence and progress

Evidence root: sibling `../evidence` of the clone, outside package/source truth.
`job-120176528494.log` retains all 305 lines of the hosted job log.
`baseline.stdout/stderr` retain a sandbox-blocked local clone attempt (Git MSYS
could not create its process object). `baseline2.stdout/stderr` retain the same
23-file failure reproduced with Python 3.13.14 / PyYAML 6.0.3 after executing
outside that sandbox limitation. Prior attempts and external roots are preserved.

Read-only diagnosis selected `gpt-6.1-sol` / `medium` per project policy and found
the count history 23, 25, 26, 27, 29; configuration is not runtime identity proof.

The unchanged source also failed identically under Python 3.12.14 / PyYAML 6.0.3:
`baseline312.stdout/stderr` and fresh `baseline312-work`/`baseline312-assets`.
Python 3.12 uses a contained task venv based on the existing bundled interpreter;
only its pinned PyYAML dependency was installed there. No global runtime changed.

`python -I -B tests/run.py --suite release`: 44 tests, no failures/errors/skips
(`release-tests3.stdout/stderr`). Both workflow shell blocks preserve exit 0/7,
stdout/stderr and diagnostic upload inputs before any `rb` directory exists.
The prior `release-tests.stdout/stderr` attempt could not write fixtures in the
sandbox's redirected temp directory; it is retained as an environment failure.
Using task-contained TEMP/TMP resolved that limitation. Intermediate 43-case
release results preceded the diagnostic-shell test and are not relabeled.

`python -I -B tests/run.py`: all 329 default tests passed in 150.865737 seconds,
no failures/errors/skips (`default-tests.stdout/stderr`), Python 3.13.14 and pinned
test dependencies. Git Bash / nested Git tests ran outside the sandbox's MSYS
object limitation. These are local checks, not a hosted Source change gate.

Actual execution OS read-back: Microsoft Windows 10.0.26300; CPU AMD Ryzen 9 3950X.
The filesystem paths above are this desktop's local files, not inferred from a
task label. `git diff --check` and changed-record JSON/YAML parsing passed.

## Final local result and exact subject

While this work ran, provider `main` advanced to
`c9999be432b4a0e91510ec667e7d818fe495a3e7` through the unrelated #490 repair.
Its two Engine member edits and seven additional maintenance tests do not overlap
this fix. The isolated unshared repair was rebased without conflict, producing
`a9b47a5171d6de8115376cd0a2712604b8059595`. The original pre-rebase checkpoint
`28dd25d6bd6579b5cd85c6e46ed976e019e15047` remains historical local evidence;
its 329-test result is not relabeled as a test of the newer base.

On clean `a9b47a5171d6de8115376cd0a2712604b8059595`,
`python -I -B tests/run.py --suite release --suite distribution` passed all
204 tests in 94.494622 seconds, no failures/errors/skips
(`rebased-tests.stdout/stderr`). The unchanged schemas/tools/source checks retain
the earlier default-suite coverage; another full matrix was not selected merely
for a base identity change. Installed lock, selection and runtime projections have
no diff against `c9999be`.

The first repaired exact-head build reached the catalog builder but returned
`unsupported/path-budget` under the long workspace output root. Retained evidence:
`fixed.stdout/stderr`, `fixed-work/builder.stdout/stderr` and `fixed-assets`.
The existing 240 UTF-16 physical-path refusal budget was not weakened. Fresh
already-authorized shorter external roots resolved the environmental limitation:

```powershell
$repairRoot = 'C:\Users\h4227\Documents\Codex\2026-10-23\task\snapshot-repair'
$repairHead = 'a9b47a5171d6de8115376cd0a2712604b8059595'
$evidenceRoot = 'C:\Users\h4227\Documents\Codex\2026-10-23\task\evidence'
& '..\python312\Scripts\python.exe' -I -B .github/scripts/build-release.py `
  --repository $repairRoot --source-commit $repairHead `
  --tooling-commit $repairHead --workflow-commit $repairHead `
  --workflow .github/workflows/package-candidate.yml `
  --repository-name YuChia-Wei/ai-collaboration-framework `
  --run-id local-492-fixed --run-attempt 2 `
  --work-root 'C:\Users\h4227\AppData\Local\Temp\r492' `
  --output 'C:\Users\h4227\AppData\Local\Temp\a492' `
  --github-output "$evidenceRoot\short-fixed-github-output" `
  1> "$evidenceRoot\short-fixed.stdout" 2> "$evidenceRoot\short-fixed.stderr"
```

Working directory was `$repairRoot`; TEMP/TMP were the contained sibling
`task/test-temp`. Python 3.12.14 and PyYAML 6.0.3 were observed. This command exited
0, built the complete snapshot, invoked existing `verify_bundle`, extracted each
manifest member and checked its raw hash, source cleanliness and source identity.
The log stderr is empty. `r492/builder.stdout/stderr` retain the product receipt.
For a new attempt choose new external roots; do not reuse or delete prior roots.

All three output files were copied with matching SHA-256 into the durable task
evidence directory `snapshot-assets/`:

- `ai-collaboration-framework-snapshot-a9b47a5171d6de8115376cd0a2712604b8059595.zip`
- the same ZIP name plus `.sha256`
- `release-manifest.json`

ZIP: 1,082,041 bytes; 497 entries, including 29 Engine members and 29 catalog
components. SHA-256:
`3a65a58d44b8c518477e3fef8cae74e62fd455277c9a4291d740909b457847f7`.
Source, tooling and workflow commits in the manifest are all the exact repair
commit above. Publication and installation were not performed. Manifest
`tests: not-run` correctly describes the builder itself; the separately executed
local test results are recorded above, not rewritten into the manifest.

The retained copy was read back with:

```powershell
& '..\python312\Scripts\python.exe' -I -B '..\evidence\verify-snapshot.py' `
  --repository $repairRoot --assets "$evidenceRoot\snapshot-assets" `
  --commit $repairHead
```

`verification.json` records passed existing bundle integrity verification and ZIP
CRC, plus exact manifest identity, counts and hash. This is author execution.

## Independent review and limits

`fixed_head_review`, explicitly selected `gpt-6.1-sol/medium` under project policy,
reviewed clean `a9b47a5171d6de8115376cd0a2712604b8059595` against `c9999be` with
installed `code-reviewer` and the project fixed-head auditor role. It found no
actionable scoped defects and confirmed literal closure, raw bytes/hashes,
descriptor/archive guards and both diagnostic shell paths. Its initial evidence
read-back observed the retained long-root path-budget failure. The short-root
success did not change reviewed product bytes, criteria or rules.

An optional follow-up to independently read the successful artifact evidence did
not execute: the selected model was at capacity. It made no writes; this was not
a permission denial, pending operation or uncertain mutation. No substitute model
was selected. The original completed independent code review remains valid; the
artifact read-back result above is the author's, not an invented independent pass.

Both workflow shell blocks were exercised locally for early exit 7 and success 0,
including captured stdout/stderr before the product builder creates any `rb`
directory. Hosted Actions upload itself, Linux/Python 3.12.15 parity, downstream
installation/runtime behavior and publication remain unexecuted. These are not
claimed by a local snapshot or the earlier PR Source check. v0.20.2 tags, Release
and assets were not modified or assessed as damaged.

## Handoff

Local repair, selected tests, exact-source snapshot and scoped code review are
complete. The final record commit changes only this workflow's three records;
the reviewed/built product subject stays `a9b47a5171d6de8115376cd0a2712604b8059595`.
No product rerun is selected for these record-only edits.

Resume at the local clone/branch named above; do not restart from the untouched
original checkout. Inspect `git log -2`, `git status --short`, this record and
the sibling retained assets/evidence. The task evidence also receives a patch
against `c9999be` for review. Next owner action is to review the local delivery and
separately authorize any push/PR/hosted validation or integration. Issue #492 stays
open. No transport, merge, publication or closure permission is implied.

## Continuation 02: PR494 source compatibility and #491 terminal gate

Reopened explicitly for the parent's 2026-10-23 instruction after PR494, not for a
provider-only status synchronization. Provider read-back confirmed latest main
`aa8bf7c934efa17e15f925befec3b12f77b58998`, merged at 02:06 UTC. Its snapshot run
39887771375, job 120199869761 failed with the identical 23-file error before the
product builder; complete upload skipped and diagnostic upload found no files.
The full 307-line job log is retained as `job-120199869761.log` in task evidence.

The 22 changed paths relative to `c9999be` are Controller guidance, catalog hash,
component versions/references, manuals and its own workflow records. No release
helper, release workflow, Engine declaration, installed projection or governing
policy changed. No path overlaps the six-file product repair. The local fetch
requested only this exact provider-read-back commit into the isolated clone.

Original handoff branch `codex/492-snapshot-engine-closure` remains at
`999290ca1f375fd767c4b8d62545a19265d49a9b`, preserving the reviewed/built `a9b47a`
and its artifacts. A new continuation branch replays the two isolated commits
onto `aa8bf7c` without conflicts. Product code and test changes compare byte-for-byte
as the same Git patch before/after rebase (`original-product-fix.patch` and
`latest-product-fix.patch`). Previously reviewed behavior, criteria and rules are
unchanged; this is identity/input reconciliation, not another implementation.

`git diff aa8bf7c..HEAD -- src/distribution/manifest.yaml src/knowledge/dotnet-backend
src/skills docs .dev/workflows/2026-10-23-controller-example-consistency` is empty.
Installed `.ai`, `.agents`, `.codex`, `.claude` and root AGENTS also compare equal.
No Controller content, shared Preview, metadata versions or #491 records are edited.

Validation selection: current-source schemas/distribution/release tests, because
PR494 changes serialized component metadata, exact dependency versions and catalog
payload. The current-source exact snapshot is rebuilt using fresh short external
roots, then copied and read back through the existing verifier and ZIP CRC. The
previous default329 result retains its earlier subject; unchanged tools/source
tests are not repeated just for identity. Prior artifacts/failures are preserved.

#492 owns the packaging helper defect. #491 has integrated its Controller repair
and keeps its terminal gate open until an actual integrated main hosted snapshot
passes and its owner reads provider state. This local repair/build can supply
evidence for the helper fix; it cannot satisfy that hosted main condition, close
#491 or grant push/PR/merge/closure authority. Those exclusions remain in effect.

Next: run selected current-source tests, fix the source subject as a clean local
commit, build/read back the corresponding full package, then append the renewed
handoff while preserving this continuation history.


## Resumed validation checkpoint

The user resumed #492 with the contract-based approach and authorized technical
Issue synchronization, excluding approval/review chatter and internal work logs.
The implementation already removes fixed cardinality from both transport checks;
29 is an observation, never the new invariant. Exact declared set, safe sorted
unique paths, declaration agreement and byte/hash integrity remain enforced.

The aa8bf7c-based source passed `python -I -B tests/run.py --suite schemas
--suite distribution --suite release`: 248 tests, zero failures/errors/skips,
90.467891 seconds. Logs: sibling `evidence/cont02-tests.stdout` and `.stderr`.
The six-file repair patch is identical before/after replay (20,942 bytes,
SHA256 122fc6fa2c5a0c2903dfc93dc854494209f488059a690d837d3154253a8d5c20).
The independent immutable a9b47a code review remains applicable to that unchanged
patch and unchanged rules; the deterministic compatibility inventory is not a
new code review. No same-file conflict with PR494 was found.

This checkpoint fixes a clean source/tooling/workflow subject for a full snapshot
build using fresh short external roots. Complete build/readback is still pending.


## Continuation 02 final delivery

Exact build subject: `23d753542101eb16b85a87eae02ba546b85a606a`, containing
PR494 base `aa8bf7c934efa17e15f925befec3b12f77b58998`. The clean tooling checkout
was stable throughout build. Python 3.12.14/PyYAML 6.0.3 ran:

```text
python -I -B .github/scripts/build-release.py --repository <snapshot-repair>
  --source-commit 23d753542101eb16b85a87eae02ba546b85a606a
  --tooling-commit 23d753542101eb16b85a87eae02ba546b85a606a
  --workflow-commit 23d753542101eb16b85a87eae02ba546b85a606a
  --workflow .github/workflows/package-candidate.yml
  --repository-name YuChia-Wei/ai-collaboration-framework
  --run-id local-492-cont02 --run-attempt 1
  --work-root C:/Users/h4227/AppData/Local/Temp/r492b
  --output C:/Users/h4227/AppData/Local/Temp/a492b
  --github-output ../evidence/cont02-github-output.txt
```

Exit 0. Wrapper logs: `../evidence/cont02-fixed.stdout` and `.stderr`.
The three output files were copied hash-identically to
`../evidence/cont02-snapshot-assets`. Existing `verify_bundle` and ZIP CRC passed;
`../evidence/cont02-verification.json` retains read-back. ZIP has 497 entries,
29 Engine members and 29 catalog components (observed values, not gates).
ZIP SHA256: `1b935c9de0f7383f6cfe7806588526b54a5b0134201592c53e093a83d04d56f1`;
size 1,082,230 bytes. This supersedes the older-base build for current delivery;
all older artifacts and failures remain retained.

248 current-base selected tests remain valid; final edits affect only these
workflow records. No product rerun follows from record-only identity changes.
The previous six-file immutable code-review diff and current repair compare
identically; no new product finding or criteria/rule change arose.

Issue #492 body now contains technical root cause, contract-based scope,
local acceptance evidence and the still-pending hosted-main condition only.
Read-back confirmed exact body and open state. No review/approval chatter or
internal work log was posted. No push, PR, merge, publication, installed-source
upgrade or closure occurred. #491 scope remains unchanged. Hosted upload behavior,
Linux parity and downstream runtime execution are not claimed by this build.

Handoff: current continuation branch in the isolated clone; final commit only
records completion. Built source remains the exact SHA above. Reviewable patch
against aa8bf7c is `../evidence/492-snapshot-repair-cont02.patch`. Next step is
separately authorized transport/integration and actual hosted-main verification.
