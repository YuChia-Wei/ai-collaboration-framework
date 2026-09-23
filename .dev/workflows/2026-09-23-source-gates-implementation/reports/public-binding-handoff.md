# Issue #369 public caller binding

Status: **caller binding complete; product acceptance and overall Issue partial**.
Starting checkpoint: `6c5f4a298bc3ffdbea47348ae6ef8c9f4584b41d`.
Worktree: `F:/framework-next/369`; branch: `codex/2026-09-23-source-gates`.
Actual public interface inspected with read-only `git show` at
`7996b32d3d4f70553b203299e25dc69d9413ff9d`: `run.py`, `test_knowledge.py`,
`test_work.py`, `test_cbf.py`, `README.md` and #373's report. No runner/helper,
product source or public test file was copied, imported, merged or executed.

## Caller and admission

Each known `public:<family>` now selects exactly:

```text
python -I -B tests/framework_next/run.py --layer public --family <family>
```

The seven package IDs are unchanged. No aggregate, `--case` or
`--public-read-only` is selected. The existing exact HEAD/clean tracked-source
checks and pinned entry-byte/link checks remain. The parser receives the subject
from that Git tree, never from the output's self-declaration. Missing runner
files still fail before launch; coordinator integration owns their delivery.

Only public calls request separate stdout/stderr capture, within the same 64 KiB
combined output cap and 120-second child timeout. Source-tests/contracts retain
their previous combined-stream behavior. No dormant workflow argument/dependency
change is necessary; its dependencies already match the delivered public runner.
Native remains the unchanged blocked Windows-only route, with no implementation.

Public stdout must contain the actual three JSONL observations in order: runtime,
one public_family, then final public_selection/outcome/exit/unexecuted_families.
Require the requested family and source commit, passed outcomes, true integer exit
0, every selected phase exactly once in declared order, no failed/current phase,
no blocked-before-write or unexecuted phase/family, and one no-skip unittest success
on stderr. `PublicCase.finish()` clears current and observation emits
`failed_phase:null`; the caller does not invent an output `complete` field.

Calls receive only basic structure and launch-count consistency checks. Expected
negative child exits remain valid observations; original PublicCase assertions
own request/response, operation and protocol semantics. Necessary fixture counters
must be consistent and cleanup must report no residue/next action. The accounting
snapshot precedes successful cleanup, so retained file counts need not be zero.
Missing, malformed, contradictory, partial, failed, skipped or cleanup-failed
output is non-passing. No new receipt, operation matrix or acceptance platform
was introduced. Future phase/interface changes require updating this small caller.

## Actual focused evidence

Only this command ran:

```text
python -I -B F:/framework-next/369/.github/tests/test_source_gates.py --output-root F:/framework-next/p7-runs/369-source-gates
```

Final result: **37/37 passed**, no failures/errors/skips; unittest 1.540 s,
harness 1.541 s. The initial public-binding version passed 37 in 3.971 s, then the
coordinator explicitly requested proportional admission rather than per-operation
revalidation. Those redundant checks were removed and the final run above covers
the changed implementation. This is not a performance comparison. Earlier 24/28
passes and the original F: WinError 1 failure remain in prior checkpoint reports.

Every complete public success response in the tests is explicitly **synthetic**;
#373 has no full family pass. Cases cover all seven exact argv, subject/family
mismatch, missing/reordered phases, partial/skip/unexecuted state, missing/duplicate/
malformed JSONL, wrong process exit, contradictory stderr, cleanup/accounting
failure, missing runner and pinned subject forwarding. Tiny actual child programs
verify separate streams and the combined output limit; they are not public tools.
The existing tiny Git selector fixture was cleaned; the supplied parent is empty.

Independent direct checks, without importing upstream modules:

- AST extraction from the three fixed public test source files matched all seven
  `prepare(..., phases)` lists exactly, including resource-setup.
- Read-only parsing of retained `adr-read-only.stdout/.stderr` (partial, exit 1)
  and `pr-read-only.stdout/.stderr` (failed, exit 1) rejected both. These are retained
  observations, not fresh runs or final-byte product acceptance.
- Changed Python/JSON/YAML syntax, local references, UTF-8/whitespace, diff scope
  and full planned-message validation are required before the local commit.

## Preserved blockers and next owner

No complete T1-T7 family round-trip succeeded in #373. Actual Lesson create refused
the filesystem/volume predicate; PR explain failed `yaml-token`; backlog was not
executed because its shared metadata/parser incompatibility was source-verified.
Read-only C4/C6 successes do not establish writing, installation or native behavior.
P7's F: path/backend problem and #368 metadata repair remain unresolved. #368's
retained result is still 14 methods / 11 successful / 3 affected / 7 errors, with
zero successful candidate builds. This caller change repairs none of them.

Coordinator owns integration, separately authorized repairs and actual selected
runs, high-risk scoped review, native binding, root adoption and CI restoration.
Original policy/AGENTS/PR-template writes remain stopped pending direct user
confirmation; none were retried. No workflow/provider setting, credential, old
workflow, shared index or canonical policy changed. No push, PR, merge, Issue
closure, sub-agent or callback occurred. Keep #369 open.

Containing commit identifies this follow-up; final handoff supplies exact SHA and
clean state. U001 leaves unselected legacy matrices/packet machinery and hosted
validation `deferred-by-owner`, owner program #322 coordinator / P7.
