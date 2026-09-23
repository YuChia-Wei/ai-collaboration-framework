# Issue #365 design handoff

Report status: bounded design complete; implementation and restoration not adopted.
Template adapted from the owning skill's ai-context-remediation-report-template.md
under U001; no assessment finding or independent verification is closed.

## Deliverables and choices

Three design files under `.dev/design/framework-next/pipeline-redesign/`:
`README.md`, `pipelines.md`, `source-rules.md`.
Workflow locator, plan, task and bounded provider observation accompany them.
No policy, workflow implementation, source, tests or provider state changed.

The proposal replaces five ordinary source contexts with one `Source change gate`,
plus conditional `Source native trial` admission. Every legacy workflow and affected
mandatory gate has a specific successor or preserved legacy scope. Nightly/full
and benchmark automation are not restored. Exact #364 behavior command bindings
remain explicit coordinator reconciliation work.

Live main matched the base. Actions/seven workflows remain disabled. Main protection
and rulesets are absent; the five contexts currently exist in source policy only.
Release environment has no protection rules. Published v0.18.0 / closed #302 do not
erase the failed hosted history or open #309 defect. #274/#275/#308 remain open.

## Actual checks and limitations

Observed checks:
- Inline Python direct parsing/readability: eight UTF-8 files, two JSON, one YAML,
  five Markdown files, 12 local links; no conflict markers.
- `git ls-files .github/workflows/*` plus direct YAML name comparison:
  exactly seven paths/names match the provider projection.
- `git diff --cached --check` and staged path/status inspection at
  2026-09-23T14:40:53+08:00: passed; eight intended files in the two allowed roots.
- `python .ai/scripts/validate-git-commits.py --message-file
  .dev/workflows/2026-09-23-pipeline-redesign/commit-message.tmp --workflow-id
  2026-09-23-pipeline-redesign`: exit 0, planned message passed at
  2026-09-23T14:40:29+08:00. Commit uses those unchanged bytes.
- Final direct parsing, staged whitespace/scope and clean-state read-back are
  repeated after these result-only updates and reported with the delivery SHA.

No actual product verification, independent review or hosted execution is claimed.

Retain earlier failures: sandbox network proxy refusal, expected protection HTTP 404,
three absent speculative workflow filenames, an inaccessible old GitHub docs URL,
and Windows process-creation error 206 for the initial oversized write command.
That command started no process; per-file writes succeeded in the same allowed roots.
The subsequent scoped provider reads, tracked seven-path inventory and current
official docs resolved those specific discovery needs without settings changes.

All framework/product/schema/tests/fixtures/build/package/install/migration/native
trials/audit/lease/effective-rule/acceptance/CI checks are **deferred-by-owner**,
U001, **program #322 coordinator / P7**. Next action: reconcile #364 exact commands
and select implementation and later trials. Design observations prove neither
behavior, independent review, support retirement nor provider permission readiness.

## Receiving checkpoint

Resume from this report's containing commit on `codex/2026-09-23-pipeline-redesign`
in `F:/framework-next/365`; obtain exact full delivery SHA and clean state from Git
and the final task response. Base is `171f33474f88888fbe853600de04bfe9c5716b25`.
All tracked writes are inside the two assigned roots; shared indexes are untouched.

Coordinator selects the implementation only after comparing #364 and #365 designs.
Then choose concrete trials/#361 target-engine-storage activation; finally present
exact pipeline/context/settings changes and observed limits for user adoption.
No executor push/PR/merge, message-to-coordinator call or CI restoration is authorized.
There is no blocking design ambiguity: executable #364 bindings, actual pilot inputs
and final restoration adoption are explicit later decisions, not fabricated results.