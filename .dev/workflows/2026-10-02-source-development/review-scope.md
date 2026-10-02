# Independent source cutover review criteria

Owner: root coordinator. Reviewer is an independent read-only delegated agent,
under the explicit 2026-10-02 source adoption/bootstrap decision. This source-only
review uses the installed code-reviewer common method and the adopted source
policy; no legacy packet/lease tooling or specialist .NET coverage is selected.

The coordinator binds the full immutable head and base
`4f231fe7f08eaa9ae296ec243be524658f8d3849` at dispatch, with clean state and a tree
identity check. Review the complete diff and immediate code/policy consumers.
No writes, provider actions, installations, full matrices or child delegation are
permitted. Root is the sole writer and keeps the reviewed subject frozen while
the review runs. Stop if head, tracked bytes, acceptance or authority drifts.

## Required coverage

1. Policy adoption is coherent across root English/Traditional Chinese rules,
   source Markdown/YAML, workflow/commit/role applicability and the PR form.
   Old ordinary gates cannot block new work accidentally; retained support,
   release, credential and downstream owners are not silently waived.
2. The selector binds exact base/head, handles both sides of rename/deletion,
   resolves current package and workflow ownership, rejects unknown executable
   scope, and cannot turn missing/empty/skipped/failed tests into success.
3. The CI workflow actually invokes the selected supported runner/dependencies
   on Windows/Python 3.13; event identity, checkout/fetch, exit propagation,
   least permissions, immutable actions and unconditional PR context are sound.
   The check does not claim independent review or merge admission.
4. Bounded tests cover material selector/runner failure paths without restoring
   removed high-I/O/native/install trials. Runtime and hosted evidence remain
   distinct from simulations and static policy consistency.
5. Optional initialization is declared and packaged coherently, uses the old
   AGENTS intent and MQ document responsibilities without copying target facts,
   preserves existing/custom context, and does not silently install or manage
   project root documents. Existing presets/installation stay unchanged.
6. T1-T3 and I1-I6 acceptance/evidence boundaries are accurate; historical native
   promises receive explicit disposition instead of a fabricated acceptance.

Return reviewed identities, scope, checks performed, actionable findings with
precise locations/trigger/impact, and limits. No findings means no supported
defects in this inspected scope, not universal correctness or a hosted pass.
After repairs, re-review affected content on a new immutable subject; metadata
that records the review itself is inspected separately and cannot validate itself.
