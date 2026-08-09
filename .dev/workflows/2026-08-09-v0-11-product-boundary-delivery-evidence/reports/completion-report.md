# v0.11.0 Completion Report

> Current status: terminal source-only closeout evidence is complete. Hosted publication run `31268095541` remains truthfully failed, while the immutable tag and public Release remain accepted only under the owner's non-transferable v0.11.0 exception. Hosted fix PRs #158 through #161 passed, `main` is `29a36934f172fa61bd3a2abf1d9d96dad2479f40`, and all required independent mechanical validation passed. Online Issues #148 and #151 are the authorized post-merge provider receipt for this final records-only commit.

## Release Identity

- Candidate and peeled tag commit: `05199ed0a9ed509ef1696df014fce244f8e7cffa`
- Annotated tag object: `b8d766125714cd79006c1c43abd372bb51a59d3a`
- Candidate PR: #154
- GitHub Release: `RE_kwDOSBe2Hc4V49W9`

## Delivered Canonical Work

#96, #95, #145, #146, and #147 were implemented and published in v0.11.0. #148's terminal source evidence is complete; its Issue and Project reconciliation occurs after this records-only commit merges, followed by #151.

## Implementation Slices

#143 and #144 were delivered as traceability-only slices. #152 supplied bounded source-only publication authority.

## Explicitly Not Delivered

No native validator implementation or language selection, repository rename, first-class Copilot support, production downstream upgrade, observability backend redesign, or existing release mutation was performed.

## Product Source Decision

### Chosen Model

`PRODUCT-SOURCE-001` keeps the current canonical source tree in place as the sole authority and makes immutable Git-tree distribution-profile output the deterministic projection.

### Rejected Alternatives

A duplicate `framework/` source tree and hand-maintained staging authority were rejected because they create two canonical truths.

### Compatibility

Downstream target paths remain stable; the two generic Codex worker profiles remain source-only and `context-translator` remains the only promoted canonical adapter.

### Migration

Automatic governed migration is supported from v0.10.0; earlier inputs require reviewed reconciliation.

### Rollback

The existing plan/apply receipt and transaction boundaries remain authoritative. No Release asset can be rewritten during rollback.

## CLI And Tooling Contract

`CLI-TOOLING-001` defines `init`, `plan`, `apply`, `upgrade`, `validate`, `rollback`, `uninstall`, and `inspect`; a process-based Validator Engine; and a never-distributed Source Maintainer CLI. No runtime or language was selected.

## Environment Readiness

The tracked policy separates availability, authorization, verification, and freshness. Readiness never substitutes for execution evidence and performs no implicit install, network, credential, or privileged operation.

## Changed-Path Selection

The aggregate runner accepts explicit base/head identity, normalizes changed paths, expands dependencies, records not-selected evidence, and escalates unknown/global impact to the full applicable profile.

## Execution And Workflow Evidence

Evidence schema 2 represents unavailable child-process, Git, and temporary-repository metrics explicitly instead of using proxy zero/one values. CI workflows preserve summary artifacts with explicit retention.

## Observability

The existing validation JSONL/summary boundary is used. Backend/export status is `unavailable`; no second telemetry authority or high-cardinality private attributes were introduced.

## Validation

| Check/Profile | Environment | Selected | Executed | Reused | Not Selected | Blocked | Failed | Duration | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| focused release tests | Windows | 50 | 50 | 0 | 0 | 0 | 0 | < 2s | release-state 29/29; version governance 21/21 |
| workflow contract tests | Windows | 18 | 18 | 0 | 0 | 0 | 0 | < 12s | governance 7/7; GitHub workflow 7/7; entrypoints 4/4 |
| PR profile | Windows Git Bash | 37 | 37 | 0 | 0 | 0 | 0 | 80s | local evidence artifact |
| closeout profile | Windows Git Bash | 1 | 1 | 0 | 0 | 0 | 0 | 5s | selected=1, failed=0 |
| closeout profile | WSL | 1 | 1 | 0 | 0 | 0 | 0 | 29s | selected=1, failed=0 |
| focused entrypoint case | WSL over NTFS | 1 | 0 | 0 | 0 | 1 | 0 | 184s | process timeout; not passed |
| hosted finalization + official closeout | Git/GitHub read-only | 2 | 2 | 0 | 0 | 0 | 0 | < 6s | exact tag/Release/assets/deviation read-back |
| hosted fix PRs #158-#161 | GitHub Actions | 20 | 20 | 0 | 0 | 0 | 0 | provider-recorded | each PR passed 5/5 required checks |
| release profile | Windows Git Bash | 52 | 52 | 0 | 4 | 0 | 0 | 897s | `validation-v011-release-correct-20260809/20260809T034026Z-1788/evidence-summary.json` |
| release profile | fresh-login WSL | 52 | 52 | 0 | 4 | 0 | 0 | 199s | `validation-v011-release-wsl-29a369-20260809/20260809T044038Z-288/evidence-summary.json`; .NET SDK 10.0.302 |
| exact published-asset upgrade | independent Luna/high task | 1 | 1 | 0 | 0 | 0 | 0 | provider-recorded | clean 657-file seed, customization-preserving finalize, and injected rollback passed |
| changed-path fixture matrix | independent Luna/high task | 10 | 10 | 0 | 0 | 0 | 0 | provider-recorded | all ten section 8.8 selection/escalation cases matched the expected outcome |

## Before / After

| Metric | v0.10 Baseline | v0.11 Result | Evidence Quality |
|---|---:|---:|---|
| package schema | 2.1.0 actual | 2.1.0 | source/provider receipt |
| terminal projection | stale fields | source evidence complete at main `29a36934`; Issue/provider receipt follows records merge | exact source/provider read-back |
| changed-path/evidence contracts | partial/proxy | implemented and exercised | 10/10 fixture cases plus Windows and WSL full release profiles passed |

## Workflow Cost

### Wall Span

Unavailable as a governed event total.

### Active Execution

Unavailable; not inferred from messages or commits.

### External Wait

Unavailable.

### Approval Wait

Zero new owner pauses; authority was supplied at intake.

### Environment Retry

Unavailable.

### Unknown

Unclassified time remains unknown.

## Sub-Agent Use

| Execution Profile | Canonical Role Path | Owning Skill | Model / Effort Evidence | Input Packet Digest | Outcome | Parent Disposition | Elapsed | Token Evidence |
|---|---|---|---|---|---|---|---:|---|
| bounded-general-worker | not applicable | ai-context-governance | configured `gpt-5.6-terra` / `xhigh` | unavailable | #143/#144 patch | accepted | unavailable | unavailable |
| bounded-general-worker | not applicable | ai-context-governance | configured `gpt-5.6-terra` / `xhigh` | unavailable | #145/#146/#147 contracts | accepted | unavailable | unavailable |

## Package And Upgrade

Four immutable assets exist from the candidate tree. ZIP digest is `cd7010f65941cccfa2151ded2e0d7b3ef27f7a9d0bb3c5772a5b5c9855a0a10c`; tar digest is `087810cd444d5c3aff9311079a0051020e0d03784803ebcc677e906bd4602404`. The exact published v0.10.0 inputs used ZIP digest `e45f88917d6a8d0db798600db414436634ba140a89590acd70a1f26bd5c1e489` and tar digest `8e11748ccd2cb8d490dcbcf0590230f07c952ad5ba409c17dbe643d03bbdd3f9`. Clean seed, upgrade, finalize, customization preservation, and injected rollback all passed. This records-only continuation did not rebuild or mutate any asset.

## Release Publication

The public non-draft, non-prerelease Release contains the governed ZIP, tar.gz, and adjacent checksum sidecars. Provider read-back is retained in `release.yaml`. The exact Sol-created tag, failed run, parsed tagged YAML, and direct authored Release body are accepted only for v0.11.0; the failed run is not relabeled as successful.

## Closeout

Canonical implementation work and the public Release exist; source-only closeout, hosted fix checks, both full release environments, exact published-asset upgrade, and changed-path matrix all pass. The final records-only commit is integrated with `--ff-only`; #148 is then reconciled and closed before #151, and their online lifecycle/Project state is retained as the provider receipt. No package bytes, tag, or Release asset are rebuilt or mutated.

## Deviations

The original fast path deferred validation and produced an immutable tagged registry that did not match the then-current validator. The later owner instruction accepts only that exact v0.11.0 Sol tag/publication history, confirms the administrator-reset and pushed main state, and authorizes the records-only correction and online closeout. Earlier WSL runs with missing SDK, fixture portability, or aggregate-runner failures remain historical failed/blocked evidence; the final fresh-login WSL run at `29a36934` supersedes them with 52/52 and zero blocked checks. This exception does not transfer to future tag creation.

## Remaining Risks

No validation blocker remains for the v0.11.0 closeout. Residual scope is intentionally limited to deferred Issues #149, #150, and #153 and to the future owner discussion of general tag authority; neither changes this release. The failed publication run and superseded WSL attempts remain visible as historical evidence.

## Deferred Issues

- #149
- #150
- #153

## Recommended v0.12.0 Entry Plan

Do not begin #150 until #148/#151 reach a terminal source/provider state. Evaluate #149 only against published product and protocol boundaries. Keep #153 deferred until repository-identity coordination is complete.

## Exact Next Action

Merge this records-only terminal commit only after its hosted checks pass, using `--ff-only`. Then reconcile and close #148 followed by #151, read back their lifecycle and Project fields, and leave #149, #150, and #153 open. Do not move, delete, recreate, or otherwise mutate `v0.11.0`.
