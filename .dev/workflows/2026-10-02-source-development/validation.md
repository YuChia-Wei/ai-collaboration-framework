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

These checks establish source/declaration/projection properties. They do not
establish instruction quality, actual preservation by an agent, runtime client
discovery, successful initialization in a consumer, or hosted/release acceptance.

## Remaining acceptance

1. Bind the affected gate to the final clean immutable candidate; preserve its
   report separately without rewriting the frozen subject to insert its own SHA.
2. Record the explicit owner bootstrap decision for independent review without
   unavailable legacy packet tooling; conduct that read-only fixed-diff review.
3. Adopt only the concrete scope, enable only Source checks and observe its exact
   hosted head. Local results cannot satisfy that provider observation.
4. Apply authorized backlog dispositions and read Issue/Project state separately.
