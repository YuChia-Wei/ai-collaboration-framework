# Validation and acceptance evidence

Scope: #452 AC01-07. Base: d334805b60b51574a94ce1634fbdf8158bbed406.
All evidence below is local Windows source evidence until stated otherwise.

## Author checks before the first immutable commit

| Check | Actual outcome |
| --- | --- |
| `python -I -B tests/run.py --suite distribution --suite schemas` | passed: 117 tests, zero failures/errors/skips, runner 10.893747 seconds |
| `python -I -B tests/run.py` | passed: 243 tests, zero failures/errors/skips, runner 67.380344 seconds |
| `git diff --check` | passed |
| Author inspection | New method/expression resources and optional BDD routing; exact dependency version closure synchronized. Corrected an overbroad manual replacement that briefly attributed BDD/Gherkin coverage to slice-implementer. No package behavior failure was observed. |

Full source stdout/stderr are retained locally under the ignored
`.dev/ai-context/local/bdd-452/` evidence root. The focused run is retained in the
conversation output. These tests do not execute installed-resource consumption
or judge agent instruction quality. No new tests that only mirror prose were added.

Initial discovery had stale graph coverage despite a current Git identity;
known current tracked paths were used as explicit fallback, and
`src/distribution` was reindexed as `bdd452-distribution` before further discovery.
Two path/PowerShell syntax lookup errors were corrected without product changes;
they are preparation errors, not failed product acceptance.

## Remaining acceptance at this checkpoint

- AC01-03: author inspection of the new resources; independent content review pending.
- AC04: fixed B1-B4 prompts and expected judgments are in workflow-plan.md; actual agent runs pending.
- AC05: source declarations pass; actual catalog/subset/install/reader checks pending.
- AC06: preserved GWT handoff and .NET rule bytes; independent immutable review pending.
- AC07: separate evidence states retained. Hosted CI, real-project adoption, release,
  parser/runner execution and token measurements are not performed.

The source-owned workflow is still in progress. No Issue completion is claimed.
