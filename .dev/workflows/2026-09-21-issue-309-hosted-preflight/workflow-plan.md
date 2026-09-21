# Issue 309 Hosted Provider Check

## Workflow Metadata

- Workflow: `2026-09-21-issue-309-hosted-preflight`
- Owner: `ai-context-governance`
- Status: `in_progress`
- Branch: `codex/2026-09-21-issue-309-hosted-preflight`
- Base: `main` at `f3cbef14595e6fc3c41930794c0a0835758a41e3`
- Created: `2026-09-21T13:47:43+08:00`
- Updated: `2026-09-21T13:51:04+08:00`
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- Template version: `1.2.0`

## Scope And Authorization

[Issue #309](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/309)
requires actual hosted Project preflight and bounded reconciliation evidence.
The owner requested work on #309, then explicitly authorized adding the local
workflow and tests after automatic approval review flagged the proposed hosted
credential-use entry point. Push, pull request transport, merge, dispatch,
credential changes, and provider mutations remain separate decisions.

This one-task workflow retains the hosted execution and credential approval
boundary across a local preparation checkpoint. That resumable external state
justifies the workflow; no unrelated tasks or package matrices are added.
Use a pull request for integration, with a merge commit if the owner authorizes
integration of this checkpoint, because its hosted follow-up remains open.

## Current Evidence

- Live Issue #309 is OPEN and has no comments as of this session.
- Run [35487203277](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/35487203277)
  remains failed at `Validate provider prepublication state` with
  `gh project view: unknown owner type`.
- Current publication uses `RELEASE_PROVIDER_TOKEN` in `ai-context-release`.
  Repository secret metadata reports an update at `2026-08-11T15:51:16Z`;
  the environment secret list is empty. Secret values were not read or copied.
  Metadata does not establish validity, token type, expiry, or Projects access.
- Existing workflow inventory has no standalone provider check. Publication is
  tag-triggered; rerunning the historical release is outside this scope.
- PR #311 already integrated actionable diagnostics. This change reuses the
  existing reconciliation implementation and adds a bounded hosted entry point.
- The code graph reports head `599136547bd30c9bcff288a51d7dc30a4b73950c`.
  Discovery therefore used explicit Git-tracked current-file fallback.

## Delivery And Acceptance

The new manual workflow runs only on `main`, checks out the dispatched commit,
and uses the publication environment, runner family, Python version, dependency
file, and existing secret reference. The token is present only in the provider
step. UI choices and a shell guard allow only `preflight` and `verify`.
Missing credentials fail before provider access. Failure remains failure;
bounded JSON evidence records the provider step's actual outcome and run identity.

- AC1: Local entry point cannot select `apply`, publish a release, or edit Issues
  and Projects. Regression coverage proves `verify` succeeds without mutation
  and fails on drift without repairing it.
- AC2: Existing secret-free owner-type diagnostics remain covered. Actual
  credential root cause remains unproven until hosted execution.
- AC3: Capture an authorized hosted result using the configured credential.
  For already reconciled v0.18.0 use `verify`; its historical prepublication
  expectations no longer describe current state. A successful `verify` proves
  read access and postpublication state only, not write permission or a new
  prepublication/apply execution.
- AC4: Keep #309 open until its actual hosted preflight and bounded
  reconciliation acceptance is met in an authorized execution. Unit fixtures
  cannot satisfy this gate.

## Validation And Resume Checkpoint

- Existing 12 focused unit tests: first attempt `blocked-by-environment`
  because sandbox denied temporary fixture access; permitted host retry passed
  all 12 in 0.137 seconds. No provider API is called by these tests.
- v0.18.0 offline contract validation passed.
- New focused checks passed: 15 unit tests, four shell syntax checks, four
  executed input guard cases, embedded Python syntax, workflow artifacts,
  AI context validation and whitespace. Full results and initial environment
  failures are retained in `tasks/ISS309-hosted-check.json`.
- Specialized E2E, spec compliance and unrelated full package/history matrices:
  not applicable to this local preparation checkpoint.
- Hosted validation: not executed. Independent integration review: pending.
- Exact next action after local validation and commit: obtain transport and
  integration authorization, satisfy current review/admission gates with a
  `Refs #309` deferred disposition, then request a separately authorized manual
  run of `release-provider-preflight.yml` on `main` with `version=v0.18.0` and
  `phase=verify`. This new dispatch workflow must first exist on the default
  branch. Preserve the failed run, tag and assets.
- If hosted access fails, use that run's secret-free evidence to propose the
  smallest credential correction for owner review. Do not copy a local CLI
  token into Actions or infer that local CLI success proves hosted access.
