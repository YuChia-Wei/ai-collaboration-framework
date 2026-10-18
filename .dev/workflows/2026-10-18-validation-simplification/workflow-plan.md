# Local source validation simplification — #461

## Authority and scope

- Input: `ba28cdbc3d7001dfb101cacba5e8f71406919797`, clean `main`.
- Work branch: `codex/2026-10-18-validation-simplification`.
- Issue: [#461](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/461),
  read at its `2026-10-18T03:17:17Z` update, open with all ACs unchecked.
- On 2026-10-18 the owner explicitly authorized local implementation of that
  Issue, direct deletion/replacement of ineffective rules, preservation of the
  PR gate, test necessity decisions and an Astra high/xhigh independent review.
  The newer execution instruction supersedes the Issue's earlier planning-only
  authorization paragraph for this local work only.
- No push, PR or merge; no Issue/Project mutation or installation/publication.
  [#463](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/463)
  remains unimplemented. `src`, installed projections, CI, runner, test code,
  machine policy/schema configuration and historical records are excluded.
- Primary owner/writer: this Codex conversation, using ai-context-governance.
  The primary exact runtime label is not exposed; locator/commit attribution
  uses configured `gpt-6-astra` / `medium` as the existing policy fallback, not
  an assertion of measured runtime or cost. Reviewer selection is explicitly
  `gpt-6-astra` / `xhigh` under the user's instruction.

One workflow retains the policy-changing authority and independent review/repair
handoff on immutable commits. Its two tasks are not separate delivery Issues.
Local implementation, review, external integration and product adoption remain
distinct. No additional ledger or parallel report projection is introduced.

## Change plan and validation decision

1. Replace the ineffective source policy text and reduce root EN/zh-TW rules
   to the same meaning and navigation. Preserve source PR checks and conditional
   independent review from the baseline; do not lower this change's review.
2. Remove ordinary-source legacy preflight/packet/lease/admission/handoff steps
   from directly involved policies. Necessary retained meanings live in bounded
   non-executable historical sections with a fixed original revision; no old
   command recipe remains in the current operating body.
3. Clarify actual-change test selection in existing test documentation. Preserve
   selected expensive-test triggers, valid protections and unknown/failed states.
4. Inspect the diff, changed references, bilingual parity and the new locator;
   commit a fixed subject, then dispatch the owner-selected read-only reviewer.
   Repair findings as needed and send affected changes back to the same reviewer.

No product/schema/default suite is selected for these prose-only edits. The
graph returned no match for `test_source_policy`; its indexed coverage was not
sufficient to establish absence. A tracked-file fallback inspected the existing
`tests/source/test_source_policy.py` and `test_source_workflow.py`: they read
unchanged YAML policy/CI configuration or check owner-path existence, not the
edited Markdown semantics. Literal-reference search found only fixture uses of
`AGENTS.md` in other tests. This is a bounded inspection, not executed tests.
The runner, schemas, machine configuration and CI bytes are unchanged. No
installation, E2E, usability, actor or benchmark trigger is selected.

Necessary validation is content review, `git diff --check`, changed-link/path
checks, new YAML parsing/status relationships and the existing commit-message
validator. This policy change needs independent semantic review, not a new
automated test mirroring its prose. Hosted checks are not run; this path scope
does not trigger source CI under the retained filters.

## Acceptance mapping and current state

| #461 criterion | Intended local evidence / current disposition |
| --- | --- |
| AC01 | Source policy distinguishes actual semantics, whitespace and schema effects before tests; pending independent review |
| AC02 | PR gate, fixed suite, path filters and CI/config bytes unchanged; optional local pre-PR run only |
| AC03 | High-cost checks require an affected behavior/boundary or explicit accepted requirement |
| AC04 | Affected-scope repair and concrete retry reasons; existing #459 case is referenced, not rerun |
| AC05 | No product rerun for report/SHA/handoff alone; no ordinary reuse packet/hash inventory |
| AC06 | Effective bodies replaced; bounded historical sections are not execution triggers; EN/zh-TW parity to review |
| AC07 | Ordinary preflight/critical/lease/admission routes removed; retained legacy/release obligations remain explicit |
| AC08 | Diff/record checks and independent review only; no new trial or self-verification test |
| AC09 | Actual results/limitations retained; no new execution, cost or saving claim |
| AC10 | #463 linked but not implemented; product bytes and installed projections unchanged |

The [existing #459 validation report](../2026-10-17-user-story-author/validation-report.md)
records four affected checks after metadata repair and one final default suite;
it is historical illustration of bounded rerun, not new #461 execution evidence.

## Results and next action

Policy edits and author inspection are complete; independent review is pending.
`git diff --check` passed on the policy edits. Two edit-preparation attempts
failed before writing (unsupported combined
delete/add patch; malformed PowerShell here-string); corrected write methods
succeeded. Neither failure was a product test or a passing validation result.
No source code or test was repaired because of those preparation errors.

Focused inspection command: `python -I -B .dev/ai-context/local/issue-461-check.py`
(one-off ignored helper, not a product test or maintained gate). It passed for
16 allowed files, 14 new local links/anchors, 7 fixed-revision references,
locator/task structure and bilingual heading/bullet parity. The new record has
no baseline blob; its expected Git lookup miss is not a validation failure.
Author inspection compared the changed EN/zh-TW meanings as well as structure.
The same scope check confirmed product, installed, CI, machine configuration,
runner and test-code bytes unchanged. No product tests were run.

Next: create the immutable local review commit, then dispatch Astra/xhigh with
this scope, the Issue ACs and baseline authority.
Do not push, create a PR, merge or close #461. Review findings and dispositions
will be recorded here, without duplicating product-test evidence.
