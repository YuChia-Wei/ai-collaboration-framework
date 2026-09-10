# Focused Validation Before Model Evaluation

The canonical handoff, .NET step contract, existing receiving roles/reviewer,
paired original examples and evaluation inputs are implemented. Source checks
passed on the working content. Independent model evaluation and final admission
are pending; this record does not claim those outcomes.

## Observed Execution

- Default BDDfy: build passed (10.083 seconds), 5 tests passed (2.998 seconds).
- Plain xUnit initial build failed with CS0029: the pinned xUnit exception
  capture returns ValueTask, while the helper declared Task. The corrected
  async helper awaits capture. Its build passed (1.851 seconds) and all 5 tests
  passed (2.663 seconds), with no skipped tests or build warnings.
- AI context validation passed; 115 workflows validated; diff whitespace passed.
- Code-review routing suite: 9 tests passed in 80.468 seconds. Its package tests
  select Git HEAD, which still held the prior source, so that result is baseline
  evidence only. Package closure must be repeated after this source is committed.
- Effective action/skill contract: 3 tests passed in 0.226 seconds.
- The catalog source section, complete source file hashes and preservation of
  unrelated catalog records were checked deterministically.

Raw commands, durations, TRX, initial failure and source hashes are under the
declared ignored root `.dev/ai-context/local/2026-09-10-bdd-test-implementation/`:
`examples-initial/`, `examples-plain-correction/`, and `example-evidence.json`.
The separate `generation-cases.yaml`, `review-cases.yaml` and `review-oracle.yaml`
were fixed before model dispatch. Review workers must not read the oracle.

## Limits

Passing the examples is executable fixture evidence. It does not establish
model compliance. A small controlled generation exercise and ten curated review
cases cannot prove universal reliability, statistical improvement, downstream
adoption or cost savings. Existing external MSTest examples remain unchanged.

## Fresh Preflight Correction

The first source effective-rule preflight on the committed payload rejected a
stale whole-catalog digest before any model invocation. Per-rule projections
were correct; the derived catalog digest was recomputed using the canonical
resolver function. Preserve this failed preflight in
`catalog-preflight-failure.json`; the next clean commit requires fresh resolution.
