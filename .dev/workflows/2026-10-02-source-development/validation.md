# Source cutover validation

Base: `4f231fe7f08eaa9ae296ec243be524658f8d3849`.
This record covers the proposed ordinary-source transition. It is not owner
adoption, independent review, native acceptance or hosted success.

## Focused implementation checks

- `python -I -B tests/run.py --suite source`: 44 passed, zero failures/errors/skips,
  2.273 s runner after locator ownership, runtime mapping and CI changes.
- Added two source-configuration tests, then observed the explicit runner still
  selected only 44 tests. Registered the new module before counting that coverage.
  Final focused run: 46 passed, zero failures/errors/skips, 2.246 s runner.
- `git diff --check`: passed. Actual YAML policies and workflow definitions parse;
  source tests check exact one-context selection, review risk domains and named
  policy paths, plus CI permission/event invariants. These are structural checks.
- Both retained checkout/setup-python immutable revisions were independently
  resolved through the GitHub API. This proves revision existence, not execution.

No installation/build/product/native/agent scenario was run. The owner removed
the fourth-stage agent scenarios from scope. The init/AGENTS assessment is
read-only against the unchanged integrated main and does not mutate installer
or target templates.

## Remaining acceptance

1. Run the complete affected gate on the clean immutable candidate.
2. Record the explicit owner bootstrap decision for independent review without
   unavailable legacy packet tooling; conduct that read-only fixed-diff review.
3. Adopt only the concrete scope, enable only Source checks and observe its exact
   hosted head. Local results cannot satisfy that provider observation.
4. Apply authorized backlog dispositions and read Issue/Project state separately.
