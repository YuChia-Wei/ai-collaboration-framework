# Issue #369 blocked local handoff

This report retains checkpoint `5ee20036392b6ad217e4029c8a256e176e9d8cdf`.
The later [runner-only follow-up](runner-binding-handoff.md) supersedes only the
V1 binding-pending state below; original failures and policy refusal remain.

Status: **local source-gate checkpoint; policy approval-blocked; no readiness claim**.
Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/369
Program: #322 / U001. Owner: program #322 coordinator / P7.
Worktree: `F:/framework-next/369`; branch: `codex/2026-09-23-source-gates`.
Starting HEAD: `38e6458f8d3e81dc2568daf1fa467571fb529fee`.
Execution declaration: independent OpenAI Codex, `gpt-6-astra` / `ultra` as
assigned; no separate runtime attestation, sub-agent, callback, push or provider
mutation. The bootstrap C: checkout was not edited or tested.

## Implemented files, local checkpoint

- `.github/scripts/check-source-change.py`: finite ownership selection from both
  pinned Git trees; additions/deletions/renames; changed content/link/whitespace
  checks; bounded subprocess output; strict event identities and failures.
  Reads manifest/metadata without importing product code. Unknown members,
  dependency impact, legacy scope and selected missing commands fail explicitly.
- `.github/scripts/run-source-native.py`: Windows/manual/main validation and
  unconditional explicit V3-binding failure; no subject fetch or native operation.
- `.github/workflows/source-checks.yml`: unconditional proposed `Source change gate`
  for the selected PR events, exact event base/head, shallow fixed-base fetch,
  credential-free checkout, minimal permissions, bounded timeout/concurrency and
  always-run failure summary. Dormant; no hosted run.
- `.github/workflows/source-native.yml`: dormant Windows-only dispatch entry,
  fixed trusted runner revision, no runnable native case until V3 delivery.
- `.github/tests/test_source_gates.py`: 24 selected selector/content/event/outcome
  tests. Synthetic ownership/provider/subprocess cases are labelled. The first tiny
  Git fixture attempt failed at parent preflight; the later permitted repair passed.

No effective policy/root/template edits were made. All seven legacy workflows,
`src/`, `tools/`, `tests/framework_next/`, manifests/profiles/indexes, installed
routes/config/data and coordinator task file remain unchanged.

## Actual observations

1. First repository command verified assigned root/branch/HEAD/common Git directory
   and clean starting state. Common Git directory is the persistent C: repository.
2. Initial sandbox `gh issue view` for #369/#365 failed because the configured
   sandbox proxy at `127.0.0.1:9` refused connection. A normal scoped read-only
   escalation succeeded: #369 OPEN, #365 CLOSED; live bodies were read.
3. Read-only provider observation during this run: repository Actions `enabled:false`,
   `sha_pinning_required:false`; all seven legacy workflow IDs below were
   `disabled_manually`. This is a settings observation, not hosted execution.
4. Official `actions/checkout` v6 resolved to
   `d23441a48e516b6c34aea4fa41551a30e30af803`; official `actions/setup-python` v6 to
   `ece7cb06caefa5fff74198d8649806c4678c61a1`. Their exact `action.yml` files both
   declare Node 24. Hosted compatibility/execution is still unobserved.
5. Graph discovery: project `369` absent. Created only in-memory bounded indexes
   for this checkout's `.github/scripts` (127 nodes, no skipped files) and
   `src/distribution` (221 nodes, no skipped files), persistence false. The names
   bind starting SHA; the tool did not supply independent Git-SHA attestation.
   Explicit tracked-file fallback verified selected paths/metadata at starting
   HEAD. No full tree/history/test scan or graph absence claim.
6. Runtime: Python 3.13.14; PyYAML 6.0.3 already installed. Installed nothing.
7. Command: `python -I -B F:/framework-next/369/.github/tests/test_source_gates.py --output-root F:/framework-next/p7-runs/369-source-gates`.
   Result: **FAILED**, 24 tests, 23 successful, 1 error, 0 skipped, 0.248 s reported
   test duration. The error was `Path.resolve(strict=True)` in `fresh_fixture`,
   `OSError [WinError 1]` on the exact authorized F: output parent. This occurred
   before creating its unique fixture child or running its Git case. The parent
   was safely created after absolute-path/ancestor/reparse preflight; it remains.
   No whole checkout copy, native/durability or product case was run.
8. After the rejection below, unaffected read-only checks succeeded: AST parsing
   of the three new Python files, YAML parsing of two new workflows, UTF-8/final
   newline/trailing-whitespace checks of all five new files, and selector ownership
   lookup for all 113 actual declared members at the starting SHA (0 lookup
   failures). This last observation tests selector mapping only, not product
   contracts, assembly, execution, installation or profile acceptance.
9. `git diff --check` on the tracked tree was empty; new untracked files received
   the explicit whitespace check above. Exact legacy workflow diff was empty.

## Automatic approval rejection, retained verbatim

The combined proposed write was rejected before process creation. Therefore **none
of it executed**, including the fixture repair at the beginning of the command.
No retry, alternate tool, writer or destination was used to apply the rejected
policy batch. The coordinator later explicitly allowed a separate fixture-only
correction through normal review; that narrower action was approved and executed.

> This action was rejected due to unacceptable risk.
> Reason: This broad mutation changes canonical governance policies, AGENTS guidance, workflow rules, release/management standards, and the PR template; the transcript does not provide trusted authorization for this persistent policy-surface change.
> Do not bypass this rejection through a workaround or indirect execution. Continue with a safer alternative, or carry out checks to prove that the action is authorized or low risk before trying again. Complete unaffected work without asking for confirmation. Report anything that remains blocked, clarify why it was blocked by auto-review, inform the user of the risk and ask for approval.

The rejected batch proposed these exact changes:

- Repair only this Issue's `fresh_fixture` preflight/cleanup using absolute lexical
  paths after every ancestor's directory/reparse `lstat` check, because the RAM disk
  refuses strict final-path resolution. Preserve contained unique children and
  reject links; no product monkeypatch, C: reroute or global TEMP/TMP change.
- Add `.dev/standards/SOURCE-DEVELOPMENT-POLICY.md` as explicitly dormant, source-only
  canonical prospective rules; no activation or CI/support/credential mutation.
- Add parity-preserving dormant pointers in `AGENTS.md` and `AGENTS.zh-TW.md`.
- Add concise prospective applicability paragraphs to `.dev/TEAM-GIT-FLOW-RULES.MD`
  and these `.dev/standards/` Markdown files: `WORKFLOW-GATE-POLICY.md`,
  `WORKFLOW-ARTIFACT-POLICY.md`, `WORKFLOW-HANDOFF-POLICY.md`,
  `GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`, `AI-CONTEXT-BOUNDARY.md`,
  `SOURCE-WORK-MANAGEMENT-AUTHORITY.md`, `GIT-COMMIT-POLICY.md`,
  `FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md`, `AI-CONTEXT-SOURCE-RELEASE-POLICY.md`.
- Add comment-only pointers to `GITHUB-WORK-MANAGEMENT-POLICY.yaml` and
  `AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml`, preserving every effective field.
- Add a dormant adoption preview comment to `.github/pull_request_template.md`,
  retaining the active form. No executable commit-policy YAML edit was needed.

Required next authority: explicit user approval of these persistent policy-surface
changes, supplied through the coordinator. The fixture-only correction was separately
permitted and completed; it grants no authority for the rejected policy writes. The
live Issue and delegated scope were already read; they did not satisfy automatic
approval review for that batch. Do not claim this is a skill-required approval.

## Continuation and remaining limits

1. Resolve the automatic approval block before retrying any rejected policy mutation.
   Retain this failure alongside subsequent evidence. No successful retry exists.
2. #368 must supply the actual fixed runner command/result interface through the
   coordinator. `command_for` currently fails `runner-binding-pending:#368` for
   contracts/public selection; no product invocation or fake result parser exists.
3. Bind actual V3 Windows cases later: native-windows argv, separate explicit
   native/recovery roots, exact runner/subject verification, bounded execution and
   truthful process-termination outcomes. Current native entry always exits 1.
4. The separately permitted fixture correction passed the second focused run: 24/24,
   0 skips, 1.733 s. Add actual runner-contract tests using labelled synthetic command
   responses after #368 delivery. Do not run product/native suites without assignment.
5. The coordinator requested one local checkpoint of the unaffected source work.
   The complete planned-message validator and final staged scope/whitespace checks
   are required before that commit. Its exact SHA/clean state is returned in the final
   handoff; use the containing commit as this record identity rather than a self-hash.
6. Coordinator owns scoped independent review, first push/PR/merge, real trials,
   root adoption, user adoption of restoration, provider read-back and Issue/Project
   state. Keep #369 open. No policy, CI or native readiness has been achieved.

Unselected legacy validators/full/history/upgrade matrices, audit/lease/effective
rule/acceptance packet machinery and CI remain **deferred-by-owner**, U001,
**program #322 coordinator / P7**; next action is selected evidence and adoption.
The stopped policy work is **approval-blocked**, not a waived or passed gate.

## Separately authorized fixture correction

After the rejection, the coordinator explicitly instructed: keep all rejected
policy/AGENTS/template writes stopped; retain this report and one local checkpoint;
the unrelated fixture-only correction may be proposed separately if it changes no
policy/protected rule and normal approval permits it. That distinct narrow action
was approved. It changed only `.github/tests/test_source_gates.py` and reran the
same selected test command. No policy write was retried.

Actual second result: 24 tests, 0 failures/errors/skips, **passed**, 1.733 s.
The real tiny Git case then ran and its unique directory was cleaned; the assigned
parent remains. The first WinError 1 failure is retained above, not rewritten as
success. This proves only the selected local selector/event contracts.

## Concrete prospective rule text, not applied

The following is the blocked design content for coordinator/owner review, not an
active policy or an alternate policy destination:

1. Bind material source work to its authorized online Issue and bounded acceptance;
   permit direct mode for small instruction/docs, retain workflows for durable
   transitions. Keep Issue/Project/implementation/transport/adoption states separate.
2. Dedicated branch, one writer, preserve unrelated changes; `src/` owns reusable
   new product, installed entries are consumed and target config/data remains owned.
3. Select smallest affected checks from both pinned trees. Unknown ownership,
   dependency impact, missing/skipped/failed command fails narrowly; no full matrix
   fallback or schema forced onto instruction prose.
4. Record full source, exact commands, outcomes/failures, limitations and next owner.
   Distinguish synthetic/local/hosted/native results and logical versus actual build
   coverage. A Lesson smoke does not establish every package/profile assembly.
5. Retain grammar, exact planned-message validation and truthful AI attribution;
   no ordinary whole-history or aggregate gate after explicit new-policy adoption.
6. Maintainer PR acceptance plus author diff inspection for ordinary changes;
   authority/security/credentials/publication/installation/recovery additionally
   require independent scoped read-only fixed-diff review. Record findings and
   dispositions without a new receipt/lease platform. Changed scope needs re-review.
7. After restoration require actual current-head Source change gate success and
   effective review/native conditions. Missing/skipped/neutral/deferred is not
   success. Use per-Issue final/deferred PR intent and separate live merge/Issue/
   Project read-back. Selector/policy edits cannot approve their own weaker gates.
8. Preserve published assets/support, active recovery, frozen history, credentials
   and provider ownership. Source PRs never implicitly publish, install or change
   protections. Retain legacy validators only for their explicitly selected scope.

All eight rules would be marked **dormant, source-only, not adopted** in the proposed
canonical document. Existing effective YAML fields and active root/template rules
would remain unchanged; concise bilingual pointers/comments only. Actual activation
must record exact owner adoption, scope/date, evidence and U001 remainder. Root
routes, provider settings, release, support withdrawal and downstream adoption are
separate. This report does not activate or apply the rejected changes.
