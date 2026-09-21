# Issue 309 Hosted Provider Check

## Workflow Metadata

- Workflow: `2026-09-21-issue-309-hosted-preflight`
- Owner: `ai-context-governance`
- Status: `in_progress`
- Branch: `codex/2026-09-21-issue-309-hosted-preflight`
- Base: `main` at `f3cbef14595e6fc3c41930794c0a0835758a41e3`
- Created: `2026-09-21T13:47:43+08:00`
- Updated: `2026-09-21T14:03:28+08:00`
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

## Necessity Reassessment And Bounded Diagnosis

The owner requested reassessment before continuation and authorized work if
still necessary. Decision: retain #309 to restore future automated publication.
The scope is hosted provider access, not another v0.18.0 publication or a broad
framework rewrite. Existing local-only approval still governs transport,
merge, dispatch and credential decisions.

Current live read-back confirms the publication workflow is active. The latest
three runs are:

| Version | Hosted run | Project preflight | Reconciliation |
| --- | --- | --- | --- |
| v0.16.0 | [33972121533](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/33972121533) | success | success |
| v0.17.0 | [34688930133](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/34688930133) | failed, unknown owner type | skipped |
| v0.18.0 | [35487203277](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/35487203277) | failed, unknown owner type | skipped |

All three releases are published. That provider state and the manual recovery
do not establish that the next hosted preflight can succeed. No newer publication
run exists in the current run listing. This is a bounded current observation,
not a claim that no credential or GitHub service change could have happened.

| Hypothesis | Falsifying observation | Method and scope | Observation / disposition |
| --- | --- | --- | --- |
| The workflow path is retired or replaced | Active current tag workflow still requires Project preflight | Live workflow state and current YAML | Falsified: the gate still precedes publication |
| Source changes broke the first owner lookup between v0.16 and v0.17 | Identical command implementation and owner/number across both tags | Deterministic Git blob comparison, both selected tags plus v0.18 | Falsified within the first-lookup source/configuration scope |
| Existing credential is invalid, expired or lacks Projects access | The same hosted credential succeeds in a fresh probe and Project lookup | Hosted experiment not executed | Unconfirmed; metadata is insufficient |
| Runner, CLI or provider behavior changed | Controlled execution with relevant versions and the same credential rules out the change | Historical logs only; no controlled intervention | Unconfirmed; runner image changed from 20260831.293.1 to 20260907.300.1 |

The reconciliation script blob is `905d67af17e0114422ccb948bf4a0f7c484374ce`
for all three release tags. Current remote main
`f3cbef14595e6fc3c41930794c0a0835758a41e3` uses blob
`57a2d03c50e45e7dd88df5a9df2ab2ace3887a9b`, whose relevant difference is the
secret-free diagnostic for the existing failure. `project_owner=YuChia-Wei`
and `project_number=3` are unchanged. v0.18 contract field differences are
checked after the failing first lookup and cannot explain that lookup by
source inspection alone.

Bounded same-runtime delegation `provider_history_evidence` used the canonical
mechanical-evidence-worker role, read only the selected Git blobs, and returned
supporting facts. The parent owns all decisions and writes. An extra comparison
to stale local `main` was excluded; remote `origin/main` is the current provider
branch. This was evidence extraction, not independent behavioral review.

Minimal reproduction in the actual hosted credential environment: not executed.
Controlled causal isolation: not executed. Root cause: **unconfirmed**. Neither
secret age nor an unchanged source script proves expiry or a permissions defect.

The local check now runs `gh api rate_limit --silent` before the Project lookup,
using the already selected step token. It reports a failed general REST probe
separately; a successful probe explicitly leaves Projects access unverified.
The [GitHub rate-limit endpoint](https://docs.github.com/en/rest/rate-limit/rate-limit?apiVersion=2022-11-28)
supports PAT and GitHub App tokens without additional fine-grained permissions.
It also permits unauthenticated access, so success must not be promoted to
Projects permission or a confirmed credential diagnosis. The workflow's prior
nonempty-token guard remains in force.

Focused regression result: 16 tests passed in 0.464 seconds, including four
executed Bash cases with intercepted `gh` and `python` functions: missing token,
REST failure, Project failure and success. No real credential or provider call
was used by those tests; they are supporting synthetic evidence only.

Next owner decision remains the concrete transport/integration and one hosted
verify dispatch described above. Do not rotate a secret, add Projects scopes,
remove the publication gate, or close #309 without the respective authority and
actual evidence.

## Authorized Integration Checkpoint

The owner explicitly authorized pushing this branch, opening PR #315, merging
after independent review and all required CI pass, and dispatching exactly one
read-only hosted verify. This supersedes the pending transport/integration/run
decisions above; earlier local-only approval remains historical evidence.
Credential replacement, permission expansion, release publication and Issue
closure remain outside this authorization.

PR: https://github.com/YuChia-Wei/ai-collaboration-framework/pull/315
Disposition: `deferred`, `Refs #309`. Merge topology: merge commit. After
admission and merge, dispatch `release-provider-preflight.yml` on `main` once
with `version=v0.18.0`, `phase=verify`. Accept the actual run outcome and retain
it in ignored provider evidence; do not retry or change a credential on failure.
The workflow remains active while hosted follow-up is pending. No tracked
post-merge evidence-sync commit is required.
