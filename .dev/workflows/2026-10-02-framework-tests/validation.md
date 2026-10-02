# Validation and acceptance

Issue: [#425](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/425).
Scope: local source/test delivery in one workflow, based on
`97c9c110e893ed26e4fb64d51062d07c55e794c5`. Final integrated verification is pending.

## Coverage disposition

| Acceptance | Implementation and evidence | Current disposition |
| --- | --- | --- |
| A1 | Removed native install, scan-budget, Git linked-worktree PR and complete candidate/planner/public-family trial drivers. Retained pure data checks and small loader/path simulations. | Implemented; native installation coverage intentionally withdrawn |
| A2 | Behavior names replace the three `test_rc2_*` modules/classes. Release and source tests moved from `.github/tests/` into `tests/release/` and `tests/source/`. | Implemented |
| A3 | `tests/schemas/` covers all 19 source JSON Schemas plus the custom provider YAML baseline, real validators and intentional runtime/schema differences. No provider YAML production validator exists; those assertions establish declarative consistency only. | Focused execution passed |
| A4 | `tests/tools/` exercises render contents, tokens, escaping, Unicode, provenance, configuration, record semantics, 10 real CLI requests and small native local record lifecycles. Fixed the actual Lesson v2 observation overwrite; retained v1 preservation coverage. | Focused execution passed; integrated rerun pending |
| A5 | `tests/run.py` owns explicit local selections and rejects empty, missing, failed or skipped selections. Source declarations read in place; catalog counts derive from declarations. Dormant selector now uses current declarations and the new runner protocol. | Focused execution passed |
| A6 | Updated current test docs, release guide and dormant policy references. Historical workflow/design/release evidence remains at its original source identity. | Local links, syntax and current-reference checks passed |
| A7 | Focused results and first failures are retained below. Final integrated command and current timings remain pending. | In progress |
| A8 | Local branch `codex/2026-10-02-framework-tests`; exactly one new workflow. No push, PR, merge, Issue closure or CI activation. | Local closeout pending |

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

The dormant combined source gate still leaves generic workflow JSON/YAML ownership
unresolved and retains independent scoped review for governance changes. The
new Issue #425 workflow does not get a special exception. Local suite success
does not assert that this combined gate or its admission requirements passed.
