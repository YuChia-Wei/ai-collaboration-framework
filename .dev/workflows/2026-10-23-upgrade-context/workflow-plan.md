# Upgrade context delivery

## Authority and baseline

On 2026-10-23 the user requested a latest-version recheck, solution arrangement,
Feature/User Story creation and development. This authorizes the local source
implementation and necessary validation. Push, PR, merge, release and downstream
installation remain separate. Public requirements are #500, #501 and #502;
authorization and continuation remain in this workflow.

The user's subsequent instruction authorized independent read-only review,
repair of findings, necessary validation, then branch push and PR creation after
passing. Merge, Issue closure, release and downstream adoption remain separate.

Local and remote main were both 83df8fcef8b2b05388eb876490fb148f75e8f79a.
The worktree was clean. Compared with the prior a7ecb86 assessment, root starter
0.2.4 adds public requirement rules but the refresh boundary and installer
not-assessed results still lack an actionable context handoff. Prior preview
observations are historical, not newly executed downstream acceptance.
Graph discovery located inspect but does not establish complete current coverage;
material conclusions use the selected current tracked sources.

## Delivery design

One cohesive branch covers #501 and #502. Add advisory context_follow_up only to
consistent installed inspect and successful apply/unchanged. Do not read root
semantics or imply a confirmed mismatch. It persists on subsequent inspect,
because context completion remains target-owned and no second ledger is created.
Keep recovery/error diagnostics and writes unchanged. Use existing refresh and
governance operations; strengthen their upgrade handoff and thin root navigation.
Update product guidance for in-place preview callers without rewriting historical
F: scripts or applying the source changes to the preview.

## Validation plan and state

Use focused maintenance contract tests for installed/uninstalled/drift/marker
inspect and apply/unchanged/failure/recovery output boundaries. They use mocked
observations, not an installation acceptance claim. Check source package/version
consistency and changed Markdown links. Source hosted gate remains required for
future integration. Independent scoped review is required for the installation
output contract and instruction changes against an immutable commit.

IMPLEMENT source changes and author inspection are complete. The installer adds
only an output advisory; refresh keeps its existing authority and hands selected
rule changes to existing governance. Source package versions are init 0.2.5 and
governance 0.1.3. Installed source-project projections remain unchanged.

Validation on 2026-10-23 with Python 3.13.14:
- `python -I -B tests/framework_next/test_maintenance_contracts.py`: 33 passed,
  including unchanged apply remaining read-only while returning the advisory.
  Fixtures used process-local TEMP/TMP at verified RAMDRIVE F:/aicf500-context;
  fixture cleanup completed. This is mocked/fixture evidence, not target adoption.
- `python -I -B tests/framework_next/test_contracts.py`: initially failed two
  manifest/metadata version comparisons. Synchronized the two manifest versions;
  rerun: 12 passed. No unrelated versions changed.
- Changed documentation/reference local links: six files checked, no missing
  local paths. `git diff --check`: passed. Author inspected the complete diff.

PR preparation validation: `python -I -B tests/run.py` on clean implementation
commit b458abdc506f8252bbdc183a8fd1509265941cf9 passed all 338 tests in
101.120 seconds, with zero failures, errors or skips. Selected suites were
schemas, tools, distribution, release and source. Python 3.13.14; process-local
TEMP/TMP remained F:/aicf500-context on re-observed RAMDRIVE. The full raw log is
F:/aicf500-context/pr-source-tests.log (disposable local evidence). This one local
PR integration run supplements the focused checks; it does not replace hosted CI.

## Independent review and disposition

Reviewer `/root/upgrade_independent_review` was independently invoked through
`fixed-head-independent-auditor`, with installed `code-reviewer` operation
`review` and the registry-selected project role at
`.ai/project/sub-agents/project-fixed-head-independent-auditor/sub-agent.yaml`.
The runtime projection matched the selected package. Policy selected task
independent-review, gpt-6.1-sol, medium. Actual execution identity was not
independently exposed and remains unknown.

Reviewed head: b458abdc506f8252bbdc183a8fd1509265941cf9.
Comparison base: 83df8fcef8b2b05388eb876490fb148f75e8f79a.
The reviewer inspected the complete 16-file diff, direct installation callers,
failure/dispatch paths, tests, skill instructions and version declarations against
#501/#502 criteria and the source policy. Checkout remained clean and fixed.
Result: no actionable defects; advisory approve/accept, not integration approval.
No repairs were needed. Static checks included diff whitespace and subject checks;
the reviewer did not run tests, create fixtures or verify runtime/downstream use.
Parent accepted this bounded evidence. The follow-up commit changes only this
workflow evidence and phase: product, tests, acceptance criteria and governing
rules remain identical to the reviewed commit, so affected review is not repeated.

Next: push the reviewed branch, create the authorized PR and read back its
current-head hosted Source change gate. Maintainer acceptance and integration
remain pending. The workflow remains in progress for PR delivery/integration.
No full installation matrix, runtime actor trial or publication is selected.
Feature #500 and Stories #501/#502 remain open; local implementation is not
integration or Issue completion.

Preferred eventual integration is linear: this is one cohesive outcome without
a separate migration or release boundary. Integration is not performed here.

## Bug #504: public PR content remediation

The user identified execution authorization/handoff in PR #503 and requested a
bug fix merged with that PR. This supersedes the previous pending merge authority:
repair, review, validation, push, PR update and integration are authorized.
Issue closure and Project mutation are not selected. Public PR content must not
carry these execution facts. PR #503 was created at head 62a50d47; its Source
change gate passed in run 39959546620 before this additional source change.

Observed cause: the source PR template requested owner authorization, execution
record and remaining owner decisions; PUBLIC-REQ-001 did not explicitly name
PRs, and pr-author lacked a public prose boundary. The author incorrectly copied
workflow facts into the public body. On 2026-10-23 the live PR body was corrected
first and Bug #504 created with functional problem and acceptance only.

BUG-504 uses slice-implementer generic mode with remediation overlay. Fix the
source policy, root bilingual navigation, PR template, closure wording, reusable
pr-author instructions and starter. Preserve validation/review facts and product
permission requirements; no blacklist, provider schema change or historical sweep.
Source pr-author advances to 0.1.1. Init remains the unpublished 0.2.5 candidate
in this PR, now including the clarified public boundary. Installed projections
are not hand-edited or implicitly upgraded.

Validation selection: source contract suite checks metadata/manifest closure;
manual semantic examples check forbidden execution history versus allowed product
permission behavior, test evidence, defects and dependencies. Check bilingual
parity, actual public PR readback, links and diff whitespace. The PR tool has an
exact package-version admission check; synchronize it to 0.1.1 and run the tools
suite to verify loading and existing operations. Schemas are unchanged; do not
add tests that mirror policy strings or rerun the full local suite merely for
prose. The graph search did not cover the package loader; selected tracked source
and literal version checks supplied the direct evidence. Current-head hosted source checks and
independent affected review are required before integration; the previous review
does not establish this correction's semantic acceptance.

Bug validation results: source contract suite 12 passed; tools suite 80 passed
(48.212 seconds, zero failures/errors/skips; raw disposable log
F:/aicf500-context/bug504-tools.log). Thirteen changed Markdown files had no
missing local links. Diff whitespace passed. Author compared the English and
Traditional Chinese root clause for the same PR/comment/review scope and the
same allowed evidence. Semantic counterexamples: agent push permission and
resume instructions are excluded; product approval behavior, test results,
defect findings and API dependencies remain valid. The live PR readback contains
product and technical evidence without the previously copied execution passages.
No runtime language-model enforcement is claimed. Next: commit this bounded
repair, obtain independent review including public PR content, then push and
require fresh hosted CI before the user-authorized same-PR merge.

Independent Bug review attempt 1: `/root/upgrade_independent_review` inspected
clean d628e1116ba915fd294811871f6b1f358dea8bd0 against 62a50d47, with original
PR base 83df8fce, using the same policy-selected gpt-6.1-sol/medium project role.
It requested changes for F1 (medium, high confidence): operations.md and
example.md still instructed deferred validation reasons to name owner/next action,
which the public renderer emits. It found no supported violation in the live PR
or Bug and no additional version/bilingual/installer regression. No tests ran in
the read-only review; actual model identity remained independently unavailable.

F1 remediation replaces those instructions with technical causes, coverage limits
or functional dependencies and supplies a technical-only example. The renderer
and schema remain unchanged. Also clarified reference-only completed delivery:
Refs may report actual product status without inventing a functional gap or
publishing missing closure authority. This preserves explicit closure authority
in the workflow. Only prose changed after the passing 12/80 tests; reuse those
results, inspect changed links/diff and return the fixed commit for affected review.

Independent Bug review attempt 2 approved clean
3655dee9e489aa905aa94b487edb1013e9065a42, delta from
d628e1116ba915fd294811871f6b1f358dea8bd0 and cumulative Bug base 62a50d47.
The same independent reviewer confirmed F1 resolved, reference-only complete
delivery coherent, no actionable remaining defect in the correction, and the
current live PR sanitized. The proposed public content envelope was accepted;
the final rendered body still needs publication readback. The reviewer performed
static inspection, diff whitespace and clean-subject checks, not test execution.
Parent accepted the evidence. This record-only commit leaves product, tests,
policies and acceptance unchanged from the reviewed head.

BUG-504 implementation and independent review are complete. The user-selected
same-PR integration remains next: push, update PR #503 with product/evidence
content, verify the new head's hosted gate, then merge with expected-head binding
using rebase (linear topology). Read back merged provider state and synchronize
local main. Do not close Issues or mutate Project fields in this selected scope.
Public Issue/PR bodies carry no execution continuation or authority. The provider
PR is the source for later merge/CI observations; no evidence-only source loop is
needed after integration. No downstream installation or release is selected.
