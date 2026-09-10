# BDD Scenario-To-Test Strengthening — Local Delivery

Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/293
Workflow: `2026-09-10-bdd-test-implementation`. Integrated baseline: `f3127a733b5644902e76b74b3b621cc9f920cd01`.
Tested/reviewed source: `ef8b63d7650e640feb8de7730b0f88e557f5dc88`. Root owns local acceptance.

## Delivered Behavior

The shared GWT handoff now binds each source scenario/data row to concrete
Given data, the primary When, every observable Then, test identity, assertions
and execution status. It uses existing target artifacts and preserves target
schemas. The BDD designer supplies design/review; the existing slice/test roles
implement tests; the code reviewer follows step bodies and checks semantics.
No new top-level skill or mandatory upstream document stage was added.

The .NET standard clarifies business-readable step methods, visible material
data, a real primary action, independently sourced expectations and isolated
per-test state. Task completion and exception capture/assertion responsibilities
are explicit. xUnit + BDDfy remains the default; an explicit target opt-out
permits plain xUnit GWT. NSubstitute/target choices, optional feature files and
the permitted compact exception-contract form retain their boundaries.

Two original standalone projects implement the same five cases. Earlier
incomplete example directories retain their reference-only classifications.
The original external MSTest projects were not modified.

## Observed Results

| Evidence | Actual observation | What it establishes |
| --- | --- | --- |
| Original default BDDfy example | Build succeeded; 5/5 passed, no skips | Executable bounded fixture |
| Original plain-xUnit example | Build succeeded; 5/5 passed, no skips | Explicit opt-out remains runnable |
| First model-generated default profile | Build succeeded; 5/5 passed | Five new input scenarios implemented and executed |
| First model-generated plain profile | Build succeeded; 5/5 passed | Same five scenarios under the selected opt-out |
| Independent generated-code review | Passed, zero actionable findings | Step semantics and every expected assertion inspected |
| Ten precommitted review cards | 10/10 matched the hidden oracle: 7 defects, 3 valid alternatives | Bounded reviewer discrimination |
| Actual deceptive-pass control | Fabricated-zero When still produced one passing zero-result test | Green output alone cannot establish scenario fidelity |
| Committed package reference closure | Passed, 43.996 seconds | Real selected/core reference integrity at tested source |
| AI context / workflows / whitespace | Passed, including 115 workflows | Applicable source structure and metadata checks |
| Effective rule resolution | Three fresh source packets resolved the exact selected rules | Canonical catalog semantics available to actual roles |

Model generation used the existing Luna max test role with fixed scenario data,
approved fixture API/configuration and strengthened guidance. It did not read
the canonical complete golden test files. No generated source repair or second
model generation attempt occurred. The source and generated-code reviews used
Terra xhigh; a separate Luna max reviewed cards without reading the oracle.
All four operations returned schema-validated actual execution records and
released their read-only leases. Parent verification checked input/output hashes,
case identities, all TRX results and separate semantic dispositions.

Retained generated outputs are under `evidence/generated-tests/`; source bytes
equal the executed ignored files. `observed-results.json` contains profile/case
results, exact commands, source/result hashes and execution record references.
`evidence/acceptance-ledger.json` retains separate evidence entries and a
validated human projection; `acceptance-index.json` maps all eight criteria.
Raw logs/TRX, packets, leases, original stage reports and receipts remain under
the declared ignored root `.dev/ai-context/local/2026-09-10-bdd-test-implementation/`.

## Acceptance

| Criterion | Required outcome | Local disposition |
| --- | --- | --- |
| AC1 | Source/scenario identity, concrete data and parameterized traceability | passed |
| AC2 | Readable GWT step responsibilities, async/exception behavior and isolation | passed |
| AC3 | Paired runnable default BDDfy and explicit plain-xUnit examples | passed |
| AC4 | Existing design, implementation and review owners consume one contract | passed |
| AC5 | Meaningful positive/negative review and deceptive-pass control | passed |
| AC6 | Actual generated code, compilation, discovery, execution and independent review | passed |
| AC7 | Source, catalog, package-reference and workflow checks | passed |
| AC8 | Separate evidence classes, preserved failures and limited claims | passed |

This table projects the eight IDs in `acceptance-index.json`; it is not an
aggregate substitute for the separate evidence entries.

## Preserved Failures And Limits

1. The original plain example first failed CS0029 because the pinned xUnit
   exception API returns ValueTask. Awaiting it inside an async Task helper
   corrected the example; the initial log and successful rerun are retained.
2. Fresh post-commit rule preflight rejected a stale whole-catalog digest.
   Per-rule text/source hashes were correct; the canonical digest function
   refreshed the derived catalog field before any worker invocation.
3. The sandbox denied NuGet temporary-lock access for one repeat example build
   and the first negative-control attempt. Normal host execution was approved
   and succeeded with the same source/configuration. No lock deletion or global
   TEMP/TMP change was made; those blocked attempts remain separate from passes.
4. The earlier nine-test routing pass read the prior Git HEAD for package tests.
   It is baseline evidence only. The 43.996-second committed-payload reference
   check above supplies current package evidence.

5. The first closeout workflow check rejected an outdated derived index timestamp.
   Synchronizing it with the locator corrected the projection; the focused
   failure fingerprint remains in `metadata-projection-failure.json`.

This is one controlled generation exercise and ten curated static review cards,
with one separately executed deceptive-pass control. It is not a blind baseline
comparison, repeated-trial study, full mutation matrix, downstream integration,
or proof of universal generation reliability, stability improvement or savings.
The tests exercise only the stated unit-fixture behavior; repository substitutes
return completed Tasks, so delayed external-I/O behavior was not demonstrated.
Formal spec compliance,
full release/history matrices, hosted checks and downstream adoption are
not-applicable to this bounded local change.

## Completion And Subsequent Admission

All workflow-owned implementation, model execution, semantic review and local
acceptance tasks are complete. The next clean commit contains only retained
evidence and workflow closeout after the tested source. Source/input byte
preservation must be verified before any evidence reuse.

A fresh independent terminal admission is declared at ignored `final_admission/`.
It inspects the final report, preservation proof and all eight criteria without
repeating package/model/test executions. This tracked document does not assert
that later result. A failed or missing terminal admission blocks delivery; its
schema-valid result and parent acceptance remain ignored terminal artifacts.

Authorization covers local implementation/validation and Issue creation only.
No push, PR, merge, Issue/Project closure, tag, release or publication was
performed. The branch remains `codex/2026-09-10-bdd-test-implementation`; later integration uses the source
repository's PR gate, with merge-commit topology if the cohesive branch boundary
is retained. There is no remaining owner-sensitive local decision.
