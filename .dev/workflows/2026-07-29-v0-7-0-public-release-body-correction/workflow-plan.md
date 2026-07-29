# v0.7.0 Public Release Body Correction Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-29-v0-7-0-public-release-body-correction`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-29-v0-7-0-public-release-body-correction`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `baseline-repair`
- `artifact_root`: `.dev/workflows/2026-07-29-v0-7-0-public-release-body-correction`
- `created_at`: `2026-07-29T15:08:23+08:00`
- `updated_at`: `2026-07-29T15:27:57+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: The stable GitHub Release for `v0.7.0` is correctly
  published from annotated tag `v0.7.0` at
  `49723a943f744820f4bdb2c22de7930693a7106d`, but its public body still contains
  tagged candidate wording that says the version is not tagged or published
  and that publication steps remain unperformed. The terminal validator
  compares the hosted body with a body rendered from the tagged candidate tree,
  so it confirms byte equality without confirming published-phase semantic
  truth.
- Authorization source: The owner authorized this source-repository
  self-correction and asked Codex to correct the online data in the 2026-07-29
  conversation. The authorization is limited to the `v0.7.0` GitHub Release
  body and the source-only tooling needed to prevent recurrence. After the
  bootstrap critical gate exposed pre-existing current-main README validation
  drift, the owner separately authorized the minimum bilingual ownership and
  inline-code parity repair as a prerequisite; this does not allocate release
  scope or broaden the online-mutation authority.
- Authorized remediation scope:
  - reproduce and retain bounded evidence of the public-body phase mismatch;
  - define a phase-correct public-body rendering and validation contract;
  - add positive and negative tests, including rejection of published bodies
    that still claim `not published` or unperformed terminal phases;
  - prove that the changed release tooling is source-only and absent from the
    downstream package payload;
  - integrate the source correction through a ready pull request and required
    checks;
  - after that contract is integrated, replace only the owner-authorized public
    `v0.7.0` Release body, read it back, and verify immutable evidence;
  - record the online correction and close this workflow through a continuation
    pull request.
- Exclusions:
  - do not create, move, recreate, delete, or replace any Git tag;
  - do not replace, delete, upload, or otherwise modify the four published
    package assets;
  - do not rebuild or republish `v0.7.0` package bytes;
  - do not create or modify GitHub Issues or Projects;
  - do not adopt or implement a tracker provider;
  - do not activate a successor release, change roadmap `current_target`, or
    make this workflow a future release gate;
  - do not add this correction to the canonical Included Work of `v0.7.0`,
    because it is post-tag source-repository remediation rather than content in
    the immutable published tree;
  - do not implement the broader `REL-004` closeout capability in this workflow.
- Release allocation: none. This is an independent source-repository
  self-correction. If package evidence shows any changed path or semantic
  dependency enters a downstream payload, stop and request an owner decision
  instead of silently converting it into product or successor-release work.
- Completion criteria:
  - the corrected public body states that `v0.7.0` is published and retains all
    four Included Work IDs exactly once;
  - the published-body contract is deterministic and fail-closed for stale
    candidate wording;
  - package selection evidence proves no downstream payload change;
  - an independent `ai-context-auditor` verification reports the finding
    resolved;
  - annotated tag object, peeled commit, Release identity, and all four asset
    names and digests remain unchanged;
  - both source-remediation and online-closeout changes enter `main` through
    ready pull requests with required checks;
  - local `main` is synchronized and the workflow is closed without assigning a
    successor release.

## Artifact Contract

- Baseline evidence: live `gh release view v0.7.0`, release run
  `30363397794`, tag object `ac57bc0f400c9e8fafdb553407b65ced5f61ee2c`,
  peeled commit `49723a943f744820f4bdb2c22de7930693a7106d`, and the
  2026-07-29 transient `ai-context-auditor` finding.
- Precedent: `.dev/backlog/items/R042-005.yaml` and workflow
  `2026-07-20-v0-4-2-release-finalization-hotfix`.
- Remediation report:
  `.dev/workflows/2026-07-29-v0-7-0-public-release-body-correction/reports/remediation-report.md`
- Verification assessment: allocate a new assessment during independent
  post-remediation verification; do not invent its ID during bootstrap.
- Tasks:
  `.dev/workflows/2026-07-29-v0-7-0-public-release-body-correction/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `V070-PUBLIC-BODY-001` | HIGH | `ai-context-governance` | repair now | `V070BODY-001` | hosted read-back, phase semantics, tag and asset invariants |
| `V070-VALIDATOR-PHASE-002` | HIGH | `ai-context-governance` | repair now | `V070BODY-001` | positive and negative release-state/renderer tests |
| `V070-PACKAGE-BOUNDARY-003` | HIGH | `ai-context-governance` | prove source-only; stop on leakage | `V070BODY-001` | payload manifest/diff and package regression |
| `V070-RELEASE-ALLOCATION-004` | MEDIUM | owner | resolved by owner: no release assignment | `V070BODY-001` | roadmap and backlog remain unassigned/unchanged |
| `V070-README-BASELINE-005` | HIGH | `ai-context-governance` | repair prerequisite only | `V070BODY-001` | bilingual ownership marker, inline-code parity, AI-context validation |

## Stages And Checkpoints

1. Bootstrap this workflow, repair the owner-authorized source-only README
   validation prerequisite, and create a fresh-session handoff checkpoint
   without changing the hosted Release.
2. Reproduce the live mismatch and freeze tag, Release, asset, and body digests.
3. Implement the smallest phase-correct renderer/validator contract and focused
   regression tests.
4. Prove source-only package isolation, run independent auditor verification,
   complete the declared source validation bundle, and integrate the source
   correction through a ready pull request.
5. From synchronized `main`, create a continuation branch, render the exact
   approved body, replace only the `v0.7.0` Release body, and immediately read
   it back while re-verifying tag and asset invariants.
6. Record online evidence, close the task and workflow, run final validation,
   integrate the closure through a ready pull request, and synchronize local
   `main`.

## Validation Strategy

- Run fast contract checks before package or aggregate validation.
- Run each aggregate gate at most once per exact commit and phase.
- Do not treat blocked, skipped, deferred, or not-applicable results as passed.
- Minimum focused tests:
  - release-state tests;
  - release-note renderer tests;
  - publish/workflow contract tests affected by the renderer boundary;
  - workflow, assessment, AI-context, YAML, and JSON validation;
  - package selection and deterministic payload isolation proof;
  - `git diff --check` and workflow commit-range validation.
- The online mutation step must verify before and after values for the tag
  object, peeled commit, Release identity, asset names, and asset digests.

## Resume Checkpoint

- Last completed action: The owner authorized a minimal source-only README
  bilingual parity repair after the bootstrap critical gate exposed drift in
  the current `main` baseline.
- Current task: `V070BODY-001`
- Exact next action: Validate and commit the README prerequisite, rerun the
  critical gate on that exact commit, then register and validate the
  fresh-session checkpoint.
- Validation already completed: repository `main` was clean and synchronized at
  `b2f1354f85ba1cee4acb497820d57a0d35547ef8` before branch creation. The first
  real critical gate at bootstrap commit
  `2cf094d4c3185b194e257e190d1c48a4ea0e343b` executed 44 required checks and
  failed one current-main README bilingual validation check; blocked/error
  fixture attempts were not counted as passes.
- Git state: workflow bootstrap is being prepared on the dedicated branch.
- Branch history and checkpoint handoffs: segment 1 started from synchronized
  `main`; a local fresh-session checkpoint will be recorded before transfer.
- Blockers or unresolved decisions: none for the bounded body correction. Stop
  for owner input if package isolation fails or any tag/asset mutation would be
  required.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-29-v0-7-0-public-release-body-correction` | `main@b2f1354f85ba1cee4acb497820d57a0d35547ef8` | started | `b2f1354f85ba1cee4acb497820d57a0d35547ef8` | local | `2026-07-29T15:08:23+08:00` | Prepare an executable fresh-session correction workflow. | Commit and validate the workflow bootstrap, then create the handoff checkpoint. |
