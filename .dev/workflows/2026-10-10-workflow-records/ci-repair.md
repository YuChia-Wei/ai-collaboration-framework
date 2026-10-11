# PR 447 source CI repair and integration checkpoint

## Current authority

On 2026-10-11 the owner explicitly authorized completing PR, CI and merge,
closing #439/#440, and updating their Project status and v0.20.0 target. The
owner also selected installable workflow CLI delivery for 0.20.0 and subsequent
#441/#442 inventory and design. This supersedes the earlier transport boundary
in the historical continuation record. Package implementation and release
publication are not claimed by this source PR.

PR [447](https://github.com/YuChia-Wei/ai-collaboration-framework/pull/447) binds
the first Git slice and closes #439/#440 after successful admission. T1-T4 keep
their completed historical results. T5 owns the bounded CI test repair, fixed
source checks, affected independent review and integration readiness record.
The parent remains the only tracked writer.

## Failed attempt and controlled diagnosis

The first hosted `Source change gate`, run
[38127423571](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/38127423571),
failed on `939a5de3a6e8307cea61b4bf8bc09635cc7977fc`. It executed 202 tests:
one failure, zero errors/skips. The reparse metadata test expected `unsafe_path`
but returned `ok`. Setup, dependency installation and the other assertions
passed. The bounded log remains in ignored
`.dev/ai-context/local/workflow-records-integration/ci-first-failure.txt`.

The test injected metadata by comparing an unresolved fixture path with a
provider path whose root had already been resolved. A controlled local probe
kept the same file but supplied a `..` spelling: the old test reproduced the
same `ok` result, while resolving the injection target before patching produced
`unsafe_path`, one target interception and `mutation_state=none`. The normal
path control passed and the owned fixture was removed. This demonstrates a
path-spelling defect in the test; a Windows short-name spelling on the original
hosted runner remains an inference because that runner's temp path was not
captured. No native junction or symlink acceptance is inferred.

## Repair and validation

Only `test_reparse_detection_is_applied_to_each_existing_path_component` changes
outside workflow records. It resolves the target before patching, exercises the
normal and `..` spellings, asserts rejection and checks exactly one injected
observation. Runtime and error handling remain unchanged. The focused host
test passed both subcases in 0.345 seconds; `git diff --check` passed.

Run `python -I -B tests/run.py` on the immutable repair commit and perform a
read-only affected review before the closing metadata commit. Retain both the
first CI failure and the next actual CI outcome; do not retry unchanged input.
Push only after local checks and review. Integration requires a fresh live PR
head/base, current-head successful `Source change gate`, satisfied effective
review conditions and an expected-head merge. Read Issue and Project outcomes
back independently. v0.20.0 is the delivery target, not a published version.

## Current result

The immutable repair `deb5df85c73739dd7b4198e42ab275f187ec954c` passed
`python -I -B tests/run.py`: 202 tests, zero failures/errors/skips; runner
duration 46.904919 seconds on this host. The exact output is retained in ignored
`workflow-records-integration/fixed-suites-deb5df85.txt` under the local evidence
root above. Host permissions were selected for the previously observed Windows
sandbox temp restriction; no runtime or dependency setting changed.

The independent read-only `workflow_review` agent reviewed that exact clean
commit against `939a5de3`. It verified the six-file diff, related unchanged runtime
control flow, failure excerpt, probe source, AST/JSON/YAML and whitespace, and
reported no supported actionable finding. It confirmed that both spellings
still require `unsafe_path` and exactly one interception. It did not rerun the
tests or claim native reparse acceptance. Start/end HEAD and tracked state were
identical and clean; the reviewer made no edits or provider writes.

T5 and local source integration readiness are complete. The closing change is
limited to this report, T5, the plan, locator and index. Runtime, tests, criteria
and governing source bytes remain identical to the reviewed repair; retain the
deterministic comparison and exact final-head binding in ignored integration
evidence. Hosted retry, merge and separate Issue/Project read-back follow this
commit under existing owner authorization. This record does not predeclare their
outcome; the current PR and signed provider follow-up own that later read-back.
