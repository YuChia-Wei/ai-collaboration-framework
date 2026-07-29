# GitHub Backlog Provider Stage A Report

## Scope And Authorization

The owner authorized the repository-only Stage A contract on 2026-07-29 after
approving the Issue, Project, Story Pack, lifecycle, field, view, automation,
migration, and pilot decisions. This stage did not create or mutate any online
GitHub Issue, label, Project, view, field, or automation.

## Implemented Contract

- Preserved `.dev/backlog/items/*.yaml`, `.dev/backlog/ROADMAP.md`, and
  `.dev/workflows/` as distinct canonical authorities.
- Added a source-only GitHub provider declaration with the approved nine labels,
  five Project fields, four views, two low-risk automation outcomes, public
  Project identity, Story Pack mapping, and 41 explicit kind/scope proposals.
- Added a public bilingual Proposal intake form while disabling blank Issues.
- Added an empty Stage A mapping receipt and schema for future provider IDs and
  read-back evidence.
- Added a read-only adapter that fails closed on source count, identity,
  classification, lifecycle, automation, label, canary, batch, and evidence
  contract drift.
- Updated the PR template to use `Refs #` and avoid automatic Issue closure.
- Explicitly excluded the adapter and its tests from downstream package payloads.

## Dry-Run Result

- Canonical snapshot: `main@08b9fd9f75edc373b693f6c38242ba141917f2c2`
- Formal items: 41 unique backlog IDs
- Desired Issue lifecycle: 5 open, 35 closed as completed, 1 closed as not planned
- Kind proposal: 11 Story, 30 Enabler
- Scope proposal: 23 framework, 16 mixed, 2 source-repository-only
- Blocked classification or closure: 0
- Canaries: `DEVWF-001`, `AIC-007`, `R042-005`, `UPG-001`
- Remaining batches: `10 + 10 + 10 + 7`
- Online writes: none

The YAML preview preserves every generated title, body, label set, Project field
value, desired state, close reason, historical closing comment, source digest,
evidence class, and warning. The Markdown preview provides the complete summary
table and execution order.

## Validation

- Provider contract tests: 15 passed.
- Package regression: 27 tests passed, 1 expected skip.
- Repository configuration contract: 13 passed.
- Governance workflow contract: 7 passed.
- Workflow lifecycle contract: 10 passed.
- Profile projection contract: 3 passed.
- GitHub workflow contract: 6 passed.
- Workflow artifact, source governance, and aggregate AI-context validators passed.
- Deterministic dry-run regeneration check passed at the recorded main commit.
- Python compile and `git diff --check` passed.

The first package and repository-config attempts used Windows system Temp and
encountered `PermissionError: [WinError 5]`. Both were rerun with `TEMP` and
`TMP` bound to the repository-writable `.tmp` directory; the reruns passed. The
failure was environmental and did not require product changes.

## Residual Risk And Handoff

- No live provider read-back exists in Stage A by design.
- The committed preview is review evidence, not permission to run Stage B.
- After merge, a fresh `main` preview will have a new canonical revision and
  must receive explicit owner approval before online writes.
- Stage B must record every successful Issue mapping immediately, stop the
  current batch on identity/body/label/comment/close mismatch, correct in place,
  and never delete migrated Issues as rollback.
- The pilot ends only when the owner decides, with earliest review after roughly
  two complete development rounds or two releases; historical migration does
  not count as a round.

## Local Checkpoint

- Implementation commit: `f6826e34b739d0e0ab6a974bc4eca12cb5666f20`
- Stage A workflow state: `completed`
- Online provider state: unchanged
- Next transport: push the dedicated branch and open a PR; do not merge or begin
  Stage B without the separately required owner decision.
