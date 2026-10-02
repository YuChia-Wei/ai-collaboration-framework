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
the fourth-stage agent scenarios from scope. The initial init/AGENTS assessment
was read-only; the later request authorized T5 source templates separately.

The full affected gate on clean candidate
`a6832ca1e0c59a9eaf6f49e8c4ed6cec2b81fb7d`, against base above, passed in 60.543 s:
223 tests across schemas 42, tools 38, distribution 35, release 26, source 46,
loader 10 and platform 26; zero failures/errors/skips. Content and whitespace
passed. Independent review remained required and admission was not evaluated.
This evidence belongs to that candidate; it is not automatically a pass for T5.

## T5 initialization source checks

- `python -I -B tests/run.py --suite distribution`: 35 passed in 2.415 s,
  zero failures/errors/skips. This reads the new actual metadata, declaration
  members, package references and optional preset in place.
- `python -I -B tests/run.py --suite schemas --suite source`: 88 passed in
  3.150 s, zero failures/errors/skips.
- Skill creator `quick_validate.py src/skills/ai-context-init`: passed. This
  verifies the entry/frontmatter, not skill behavior or every seed's semantics.
- Real `project_members` in-memory projection of new source bytes: 12 payload
  members and two original-name runtime entries; no root AGENTS/CLAUDE management.
  The selection pin was synthetic and no catalog artifact or target was created.
  First preparation attempt omitted required selection fields and failed with
  `Selection: invalid union`; after supplying the documented closed selection
  shape, the second attempt passed. Product validation was not weakened.
- All 12 local Markdown links in the package resolved within its declared source,
  including uppercase `.MD` files. All eight prior presets were byte-identical
  to the pre-T5 candidate; managed `.ai`, `.agents` and `.claude` had no diff.
- `git diff --check` passed. Both the main checkout and MQ lab remained clean.

The first fixed-head incremental gate at `cb1029772b86e77b6ccffd75ad8c152c56f2536c`
failed before test dispatch in 18.643 s: completed T5 used `result` instead of
the required `result_summary`. The record key was corrected; no gate or product
behavior changed. A second attempt is warranted by that material input repair.

These checks establish source/declaration/projection properties. They do not
establish instruction quality, actual preservation by an agent, runtime client
discovery, successful initialization in a consumer, or hosted/release acceptance.

## Adoption and hosted validation

The owner subsequently adopted the concrete transition. On clean immutable
`3ca6756cc088241b668378460aa827c9b24cf0f1`, the full base-to-head affected gate
passed in 83.394 s: schemas 42, tools 38, distribution 35, release 26, source 46,
loader 10 and platform 26 (223 total, zero failures/errors/skips), plus content
and whitespace. This is local execution. Independent scoped review of that same
subject returned no supported actionable findings; see [review.md](review.md).
The initial online Issue read-back differed only in trailing newline handling;
normalized content and title matched without a duplicate write.

Source checks was enabled through the authorized workflow endpoint and read back
as active. PR #428 was created as a draft at `c82b0c32`; its first actual
[hosted run](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/36971267170)
failed on `c82b0c32188d0d1fa03699f33b33dff9615a9fec` before test dispatch.
Windows/Python 3.13.15 setup, exact checkout/base fetch and dependency install
passed. The gate rejected the incidental snapshot workflow comment change as
`unselected source/legacy pipeline owner` (both diff sides), matching the
independent follow-up finding. Gate duration was 17.473 s; the job failed rather
than reporting a skipped or passing test result. The always-run summary completed.
The comment was restored to the previously reviewed bytes; only then is a new
head/run warranted. The failed run remains retained and is not a hosted pass.

The correction was committed as `cc4b42d9070d952370abd3ffa03b6c88381fd482`.
Actual production selector/content/whitespace preflight passed with no ownership
errors; no local suite rerun was attributed to that preflight. Independent
affected review confirmed the blocker removed and substantive implementation and
policy unchanged. The reviewer identified a stale remaining-enable sentence in
this record; it is corrected here. The retained snapshot comment is historical
#418 wording, not the current provider-state source of truth.

[Hosted run 36971496887](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/36971496887)
completed successfully on that exact head, base
`4f231fe7f08eaa9ae296ec243be524658f8d3849`, on Windows/Python 3.13.15. Its actual
selector report passed 223 tests (42 schemas, 38 tools, 35 distribution, 26
release, 46 source, 10 loader, 26 platform), zero failures/errors/skips, plus
content/whitespace. Gate duration: 65.022 s; hosted job: 96 s. Setup, fixed
checkout/fetch, dependencies, gate, summary and post steps succeeded.

Provider read-back showed only Source checks, Build framework snapshot and Prepare
framework draft active; the other six workflows remained disabled. Repository
permissions, rulesets and protection were not changed. Source adoption supplies
maintainer admission rules, not a claim of server-enforced branch protection.

## Final integration conditions

All source tasks and the prior backlog disposition are complete, but that does
not pre-approve a later head or merge. Evidence-only closeout changes receive
affected independent review and their own current-head hosted check. Record those
final bindings in PR #428 and provider evidence without changing a frozen commit
to insert its own SHA. Merge only after that actual success, then read main,
Issue and Project separately. Any new failure reopens its affected work before
integration; no old result or single-merge waiver substitutes for the final check.
