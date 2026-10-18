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
| AC01 | Source policy distinguishes actual semantics, whitespace and schema effects before tests; supported by independent static review |
| AC02 | PR gate, fixed suite, path filters and CI/config bytes unchanged; optional local pre-PR run only |
| AC03 | High-cost checks require an affected behavior/boundary or explicit accepted requirement |
| AC04 | Affected-scope repair and concrete retry reasons; existing #459 case is referenced, not rerun |
| AC05 | No product rerun for report/SHA/handoff alone; no ordinary reuse packet/hash inventory |
| AC06 | Effective bodies replaced; bounded historical sections are not execution triggers; EN/zh-TW parity reviewed |
| AC07 | Ordinary preflight/critical/lease/admission routes removed; retained legacy/release obligations remain explicit |
| AC08 | Diff/record checks and independent review only; no new trial or self-verification test |
| AC09 | Actual results/limitations retained; no new execution, cost or saving claim |
| AC10 | #463 linked but not implemented; product bytes and installed projections unchanged |

The [existing #459 validation report](../2026-10-17-user-story-author/validation-report.md)
records four affected checks after metadata repair and one final default suite;
it is historical illustration of bounded rerun, not new #461 execution evidence.

## Initial implementation results

The initial policy edits and author inspection completed before independent review.
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

The initial implementation was committed and reviewed as recorded below.
No push, PR, merge or Issue closure was authorized.

## Independent review attempt 1 and repair

Reviewer `/root/astra_461_review`, explicitly dispatched as `gpt-6-astra` /
`xhigh`, reviewed `ba28cdbc3d7001dfb101cacba5e8f71406919797` through
`646da176f1630b141f350b0d2e7120700d0e4445` read-only. The reviewer inspected
all 16 changed files, baseline authority and direct entry/config dependencies;
`git diff --check` passed and the worktree stayed clean. No product tests or
provider operations were performed. AC01–AC05 and AC08–AC10 were supported by
static evidence; changed EN/zh-TW rules preserved the same normative meaning.

F1 (P2): the still-active ROLE-EXECUTION-CONTRACT referred to the deleted
proportionate-execution classification, full role records and third-attempt
authorization. The existing precedence disclaimer did not satisfy AC06/AC07's
direct cleanup. Accepted and repaired: replace that source contract with current
bounded execution, results and justified retries; isolate old formats behind a
fixed-revision historical reference. Clarify the root bilingual entry's current
role instructions versus historical execution records. No product or schema
change is needed. This brings the local scope to 17 files.

The repair was committed for review by the same independent reviewer.
Earlier findings remain recorded; author repair is not independent verification.
Product tests remain unselected for the same reason.

## Independent review attempt 2 and local completion

The same `/root/astra_461_review` reviewer, `gpt-6-astra` / `xhigh`, reviewed
repair commit `97e8a7277ea7e373b08b03656da03ed2afde571b` against the previously
reviewed `646da176f1630b141f350b0d2e7120700d0e4445`. F1 was resolved; no new
actionable findings were found in the affected scope. The reviewer confirmed
AC06/AC07, bilingual normative parity and retained ownership, permission,
independence and truthful-evidence boundaries. Unaffected AC conclusions were
retained from attempt 1. Five changed files and their full contents were read,
fixed historical Git blobs checked, and repair `git diff --check` passed.
The worktree remained clean at that exact reviewed commit.

Local implementation and the requested independent review/repair are complete.
All ten ACs have bounded static evidence within this source-policy delivery;
this is not hosted CI, integration, downstream adoption or owner final acceptance.
No product/schema test, installation, E2E, usability trial or benchmark ran.
No measured time/cost savings are claimed. #463 remains unimplemented.

The subsequent local completion commit changes only this plan and its locator,
recording actual results and completed task state. The reviewed policy, root
entries and test documentation are unchanged from the full reviewed commit.
Inspect the final record and compare that scope; no behavioral re-review or
product rerun is selected for this record-only completion.

Handoff: branch `codex/2026-10-18-validation-simplification`, original base
`ba28cdbc3d7001dfb101cacba5e8f71406919797`. No push, PR, merge, Issue/Project
mutation, installation or publication occurred in this implementation phase.
Any external integration remains a separately authorized next action; read
actual provider gates then. Local completion does not close #461.

## Authorized continuation — #463, one intended PR with #461

On 2026-10-18, after #461 local completion, the owner requested continuation of
`src` corrections and one PR covering both Issues. This supersedes the earlier
#463 exclusion and the Issue's creation-only/separate-delivery text for this
implementation and delivery grouping. The #461 results above remain historical
local evidence. Continue on the same branch; do not repeat completed #461 work.
Input commit: `545248eeff8f26a3c11e43005ac3a3eed76c8235` (clean).
#463 was read live, Open, at its `2026-10-18T03:16:29Z` revision. No installation,
release, downstream adoption or merge authority follows from this continuation.
The earlier no-push/no-PR instruction remains the external-operation boundary;
prepare the cohesive local delivery for one PR.

T3 owner: software-development-orchestrator; product instruction edits apply
skill-creator. Scope: ai-context-governance maintenance owner and the direct
orchestrator, local-change and slice implementation consumers, their metadata,
distribution manifest and directly affected human manuals. Slice has the same
unconditional narrow-check wording and is needed to keep the coordinated
implementation path consistent. These independently optional skills need their
own operational decision; no new shared knowledge dependency or rule engine.
Use patch versions for instruction corrections, preserving public operations,
metadata shapes, member sets and dependency declarations. Update exact manifest
versions and manual version labels. Existing presets select IDs, not versions.
Do not edit installed projections, locks, published assets or historical docs.

Before implementation, select validation: semantic review against all eight #463
ACs and representative decisions (authorized replacement, retained history,
nonsemantic whitespace, parsing-sensitive whitespace, affected behavior and
mandatory target gates); existing distribution suite for actual changed package
versions/manifest closure; skill creator frontmatter/scaffold checks and diff
inspection. No new wording tests, schema tests for unchanged schemas, full
installation/E2E/usability/actor matrix or benchmark. Static decisions are not
observed downstream behavior. Independent review returns to the same Astra/xhigh
reviewer on an immutable local commit, preserving the prior review results.
Because this delivery now changes src, its future PR requires the retained
current-head hosted Source change gate. #461's path-only non-applicability no
longer describes the combined PR. No hosted result is claimed here.

### #463 implementation and pre-review evidence

Four instruction packages now use corrected procedures: governance `0.1.1`,
local-change and slice `0.2.4`, orchestrator `0.3.2`. Patch increments correct
instruction behavior without changing operation names, metadata shapes, member
sets or dependencies. Exact versions agree with the distribution manifest and
current manuals. Presets select IDs and need no version edit. The installed
source-project projection deliberately remains at its earlier version; no
installation, product publication or downstream adoption is claimed.

| #463 AC | Implemented evidence and limit |
| --- | --- |
| AC01 | Governance Apply step 3 replaces authorized obsolete rules while preserving valid protections and unrelated content |
| AC02 | Governance isolates necessary history, states non-trigger applicability and removes active superseded entry links; no model guarantee |
| AC03 | Governance and three implementation/orchestration entrypoints distinguish harmless text from parsing/schema/output/behavior effects before tests |
| AC04 | Affected behavior/boundary or explicit request/accepted criterion selects high-cost checks; required target gates remain |
| AC05 | Existing output can state the reason; no receipt, ledger, complete hash inventory or classification platform added |
| AC06 | Four src-owned packages, exact manifest versions and direct manuals agree; no source-specific CI/path/model/record rules exported |
| AC07 | Validation choice was recorded before edits; static review and existing structural/unit evidence remain distinct from downstream behavior |
| AC08 | Failure and retry below remain separate; no release, installation, adoption or guaranteed model behavior asserted |

Static author inspection considered replacement versus unrelated protections,
retained legacy text versus active navigation, prose-only edits versus YAML
indentation/schema/output effects, affected integration versus report-only
closeout, and unconditional target PR/security/release gates. The instructions
support the intended distinctions. This is semantic analysis, not a trial of
another model applying the skill. Independent review is pending.

Actual checks:
- `skill-creator/scripts/quick_validate.py` on each of the four changed packages:
  passed frontmatter/naming/scaffold checks (not behavioral validation).
- `python -I -B tests/run.py --suite distribution`: failed; 73 tests, 0 assertion
  failures, 24 errors, 0 skips, reported duration 6.575357 seconds. Source
  declaration/member/version/preset checks passed. The shown fixture errors were
  `PermissionError / WinError 5` in sandbox temporary-directory creation and
  cleanup, not an instruction or package mismatch. The raw error paths identify
  ephemeral sandbox roots, not product output. Cleanup errors are retained;
  removal of those original sandbox directories was not verified.
- Bounded selected-module inspection found only `test_maintenance_contracts.py`
  uses those FixtureTestCase temporary roots among the six distribution modules.
  Under ordinary host permissions, `python -I -B
  tests/framework_next/test_maintenance_contracts.py` passed all 15 tests in
  0.155 seconds. No product repair, test rewrite or TEMP setting change preceded
  the retry. This module retry does not relabel the original run as passed;
  unaffected results keep their original run. No full-suite repeat was selected.
- One-off read-only metadata comparison confirmed only the four version fields
  changed; manifest/manual versions, changed-document local links and continued
  workflow state agree. No maintained checker was added.
- Graph search identified relevant existing metadata tests, but index freshness
  was not established from its dynamic Git identity. Direct tracked-file reads
  of the selected test modules/runner supplied validation applicability; no graph
  absence claim or broad product scan was used.
- Two early wildcard-path rg lookups were invalid on Windows and were replaced
  with concrete paths; neither changed files or supplied absence evidence.

No new tests, schema changes, full default run, candidate assembly, native
installation, actor trial, E2E, usability matrix or benchmark were selected.
The upcoming combined PR will still need its actual current-head hosted gate.

### #463 independent review and combined local completion

The same `/root/astra_461_review` subagent, selected `gpt-6-astra` / `xhigh`,
reviewed immutable `f33ad8cecdf10a8df06457034563e24e9f5cbfaf` against product
base `545248eeff8f26a3c11e43005ac3a3eed76c8235`. The reviewer received the
exact eight live-read Issue ACs and inspected all 16 changed files, four skill
entries/metadata, slice's direct mode/test/repair references, manifest, selected
presets and work record. No actionable findings were found. AC01–AC08 were
supported at the reported static instruction/package/evidence boundary; no
candidate assembly, installation or downstream agent behavior was asserted.
Earlier #461 conclusions and the resolved F1 were reused for unchanged content.

The reviewer checked the immutable Git subject, actual diff and references,
excluded paths and `git diff --check` (passed), and ended with a clean worktree
at the reviewed commit. Product tests and provider operations were not repeated.
An initial reviewer lookup used a nonexistent preset directory; the actual
`src/profiles` declarations were then read through manifest navigation. It did
not establish absence or create a product failure. The supplied test execution
records were checked for truthful claims, not independently re-executed.

#461 source-policy changes and #463 portable instruction corrections are now
complete locally on one branch for the owner's intended single PR. This later
completion supersedes the earlier #463-not-implemented checkpoint; earlier
results retain their original scope and time. The next record-only commit
updates this plan and locator without changing any reviewed source/docs bytes.
Final record/commit inspection is selected; no product rerun or new behavioral
review is needed for these status-only changes.

Remaining external work: push/create the one combined PR only under the
applicable external-operation authorization, obtain its actual current-head
hosted Source change gate, and handle merge/Issue/Project state separately.
The earlier explicit no-push/no-PR/no-merge boundary remains in force for this
local delivery. No provider mutation, installation, release or adoption occurred.

## Owner-adopted validation timing refinement

After reviewing #463, the owner approved: plan validation purpose/items/triggers
and execution timing during task orchestration; reconcile conditional checks
through actual implementation; confirm necessity before execution and required
acceptance evidence after implementation. Reproduction, TDD and incremental
checks may precede completion. Mandatory gates and accepted criteria cannot be
silently cancelled. Coordinate shared checks at integration points and return
wider impact to the selected orchestration/task owner.

The owner explicitly requested adjustment and local commit. Reopen T3 for this
bounded continuation from `ecbc5d69`; retain the prior review as historical
coverage, with affected conclusions requiring re-review. Update only three
source operation references, their current manuals, the source policy and this
existing record. Governance's before-execution wording already fits and needs
no change. Keep the existing unreleased #463 patch versions: no new publication,
operation, member, dependency, metadata or manifest change is selected.

Validation selection before edits: inspect the instruction diff and timing
semantics, mandatory/conditional boundaries, standalone implementation behavior
and direct manual parity; diff/record checks and the same independent reviewer.
No package/metadata/runner/schema/test code changed, so previous structural
checks retain their original scope and no distribution/product test rerun is
needed. Static review does not establish downstream actor behavior. No new
records, test platform, installation, provider operation or release is selected.
