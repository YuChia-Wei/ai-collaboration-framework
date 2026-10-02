# Validation and acceptance

Issue: [#425](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/425).
Scope: local source/test delivery in one workflow, based on
`97c9c110e893ed26e4fb64d51062d07c55e794c5`. Local implementation and selected validation are complete. This record does not claim
that the dormant combined admission gate passed.

## Coverage disposition

| Acceptance | Implementation and evidence | Current disposition |
| --- | --- | --- |
| A1 | Removed native install, scan-budget, Git linked-worktree PR and complete candidate/planner/public-family trial drivers. Retained pure data checks and small loader/path simulations. | Implemented; native installation coverage intentionally withdrawn |
| A2 | Behavior names replace the three `test_rc2_*` modules/classes. Release and source tests moved from `.github/tests/` into `tests/release/` and `tests/source/`. | Implemented |
| A3 | `tests/schemas/` covers all 19 source JSON Schemas plus the custom provider YAML baseline, real validators and intentional runtime/schema differences. No provider YAML production validator exists; those assertions establish declarative consistency only. | Focused execution passed |
| A4 | `tests/tools/` exercises render contents, tokens, escaping, Unicode, provenance, configuration, record semantics, 10 real CLI requests and small native local record lifecycles. Fixed the actual Lesson v2 observation overwrite; retained v1 preservation coverage. | Passed on the integrated implementation |
| A5 | `tests/run.py` owns explicit local selections and rejects empty, missing, failed or skipped selections. Source declarations read in place; catalog counts derive from declarations. Dormant selector now uses current declarations and the new runner protocol. | Focused execution passed |
| A6 | Updated current test docs, release guide and dormant policy references. Historical workflow/design/release evidence remains at its original source identity. | Local links, syntax and current-reference checks passed |
| A7 | Integrated and affected-suite results, exact subjects and first failures are retained below. | Passed for selected local suites |
| A8 | Local branch `codex/2026-10-02-framework-tests`; exactly one new workflow. No push, PR, merge, Issue closure or CI activation. | Completed locally; integration remains separately authorized |

## Integrated execution and content binding

Environment: Windows, Python 3.13.14, PyYAML 6.0.3, jsonschema 4.26.0 and
referencing 0.37.0. Commands ran from the clean integration worktree. The first
full default and optional invocations ran concurrently with separate temporary
fixtures. No tracked mutation occurred during execution.

| Command | Immutable source commit | Tests | Runner seconds | Outcome |
| --- | --- | --- | --- | --- |
| `python -I -B tests/run.py` | `da1e481b4e4a72269be99b0d26b21d006ba24cb7` | 178 | 38.514091 | Passed; zero failures/errors/skips |
| `python -I -B tests/run.py --suite loader --suite platform` | `da1e481b4e4a72269be99b0d26b21d006ba24cb7` | 36 | 1.681945 | Passed; zero failures/errors/skips |
| `python -I -B tests/run.py --suite source` | `8b4d15e1fd3a3a7888a0a1e51d850dcab433e56c` | 38 | 2.237030 | Passed after padded-rename correction; zero failures/errors/skips |

The final source retry follows the actual selector's `R095` failure. Git's
zero-padded similarity score was rejected by the old parser. The repair accepts
`R000` through `R100`, retains existing short scores, and rejects invalid larger
or malformed scores. One new regression preserves both renamed paths and the
following diff record. Worker focused source execution passed 34 methods before
root ran those methods together with the four runner tests.

Between the full execution and the source retry, `git diff --name-only` contains
only `.github/scripts/check-source-change.py` and
`tests/source/test_source_gates.py`. The real product sources, schemas, templates,
distribution/loader/platform/tool/release tests, runner and workflow callers have
identical tracked bytes. Affected source tests were rerun; the other results are
reused on the same host, dependencies, commands and authority. The final closeout
commit changes only this workflow's status and evidence records; final Git
read-back checks that source and test bytes still match the recorded subjects.

Raw stdout report SHA-256 (captured before closeout; values are embedded here so
this record does not depend on temporary log storage):

- `default`: `4fd2103b438ccfef4be3792cc1860aa3104ddf0b219eb98d281af6d23c996033`
- `optional`: `d1ce020434a08ad6fc2a06403d2774449ffe921eefb4b4cf559c4b4644eaece3`
- `source-final`: `140831e91290ae46a2d8e5f251e5ebbe92167565b9ea978c22a21788cc4fa813`
- `selector`: `09748e0871020b51ceb6e275ff54241061382b7c5c93e9e1b8913b239a2a80d4`
- `selector-final`: `1dc2b0a138a5199cde9c89ff38a5770c9afe445f8263c057848b11623c78c39e`

Additional checks: changed local Markdown references, retained Python syntax,
whole-change whitespace, exact planned commit messages and workflow branch
commit-range grammar passed. Workflow locator/task identity, timestamps,
references and completed-state consistency are checked directly against
WORKFLOW-ARTIFACT-POLICY.md. Original `main` remains clean at
`97c9c110e893ed26e4fb64d51062d07c55e794c5`.

## Preserved attempts and corrections

| Attempt | Observed result | Correction and follow-up |
| --- | --- | --- |
| Schema first run | 41 methods; 7 failures and 26 subtest errors; zero skips; 0.687 s unittest, 1.237 s command | Fixture container aliasing, integral-float exception expectations and optional date-format assumptions corrected. One retry: 42 passed, zero skips; 0.599 s unittest, 0.961 s command. |
| Tools first run | 37 methods; 4 assertions failed across 3 methods; zero skips; 32.242 s unittest, 32.509 s command; 10 CLI subprocesses | Three expected-output mistakes corrected (Markdown backslash escaping and canonical persisted-key order). Two affected methods passed in 1.726 s. Fourth assertion identified the genuine Lesson observation bug; source fix belongs to root integration. |
| Root distribution + loader + platform first run | 71 methods; 8 failures; zero errors/skips; 4.958 s unittest | Two version-rejection message expectations were too narrow. Six loader failures were host-precondition failures because the command omitted `-I`; isolation was not simulated. Corrected expectation and actual isolated invocation. |
| Root isolated corrected run | `python -I -B tests/run.py --suite distribution --suite loader --suite platform`: 71 passed, zero skips; 3.511 s unittest, 3.837 s runner | Product loader/path tests remain synthetic unit evidence; this is not installation acceptance. |
| Root tools + release after Lesson fix | `python -I -B tests/run.py --suite tools --suite release`: 63 passed, zero skips; 32.824 s unittest, 33.063 s runner | Real tool calls and native local record operations, with offline release/provider transports. The later v1 preservation method separately passed in 0.646 s. |
| Root integrated source suite | `python -I -B tests/run.py --suite source`: 37 passed, zero skips; 2.040 s unittest, 2.155 s runner. Worker first 32 and final 33 selector methods also passed. | Real runner integration plus in-memory source/transport fixtures. |
| Root distribution after small cleanup | `python -I -B tests/run.py --suite distribution`: 35 passed, zero skips; 2.231 s unittest, 2.439 s runner | No candidate or installed target produced. |

These timings describe the measured commands on this Windows host. There is no
same-host before/after baseline, so no comparative speedup is claimed. Helper
write counters cover only explicit fixture writes, not total filesystem I/O.

## Boundaries

Source/template/schema consistency is not skill-instruction or agent-output
quality. Native local record publication is not framework installation. Mocked
provider responses are not live provider evidence. Loader and Windows API
simulations are not native apply, locking, interruption or recovery acceptance.
The experimental standards-promotion source remains excluded from distribution.
Existing CI suspension and dormant source policy remain unchanged.

Root performs integration and direct diff review. Delegated implementations are
supporting evidence, not independent review. No independent fixed-head audit or
hosted/release admission is claimed. Workflow metadata is validated directly
against the source policy because its historical validator route is unavailable.
An optional availability check of
`python -I -B tools/maintenance/validate-agent-execution-guardrails.py --help`
failed before argument parsing because the removed `artifact_core` module could
not be imported. This is a preparation/tooling failure, not an executed behavioral
review. No independent reviewer was dispatched and no legacy route was restored.

The actual combined gate was executed twice against clean fixed commits using
`python -I -B .github/scripts/check-source-change.py --base
97c9c110e893ed26e4fb64d51062d07c55e794c5 --head <subject>`.
The first attempt on `da1e481b4e4a72269be99b0d26b21d006ba24cb7` failed before
selection on `R095` (0.255 s). After the parser repair, the attempt on
`8b4d15e1fd3a3a7888a0a1e51d850dcab433e56c` failed closed in 19.181 s with exactly
three unresolved ownership paths: this workflow's `tasks/T1.json`,
`tasks/T2.json` and `workflow.yaml`. It selected the expected seven test suites,
retained `independent-scoped-review`, and executed none of those selected checks
inside the combined gate (`results: []`). The explicit runner commands above
were executed separately under the owner's local scope.

Generic workflow JSON/YAML ownership and governance admission remain outside
this test-refocus change. No special Issue #425 exception, legacy guardrail
restoration, CI activation, push, PR, merge, provider mutation or Issue closure
was performed during closeout. These blocked/unexecuted gate results are not
converted to passed by the successful local suites.
