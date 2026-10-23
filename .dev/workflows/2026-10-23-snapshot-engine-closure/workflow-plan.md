# Snapshot Engine closure repair

Issue: [#492](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/492).
Template: `.dev/workflows/2026-10-22-domain-architecture-split/template.md` @ 1.0.0.

The user authorized isolated local repair, tests and a reviewable handoff. Push,
PR creation, integration, publication, source self-upgrade and Issue closure are
excluded. The parent conversation owns tracker work. One tracked writer owns this
clone; independent workers and reviewers are read-only.

## Subject and cause

Base: `a7ecb86e6b65d55e2447e43d86ad1497530135f6` (`main`, provider read-back).
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

Next: finish the bounded repair and regressions, create a clean immutable local
commit, build/verify its exact source, review that diff independently and record
actual results and any limits here. No permission for transport is implied.
