# v0.13 Terminal Release Readiness Report

## Status

`in_progress`

## Reconciliation

| Authority | Current disposition | Evidence | Remaining action |
| --- | --- | --- | --- |
| #187 / `ASM-20260811-001` | addressed, integrated, and closed | `ASM-20260811-002`, PR #195 hosted checks, live Issue/Project read-back | no prepublication action |
| #194 | resolved, validated, and closed | schema 1.1, focused tests, fixed commit `1491178`, retained dispatch/completion, independent cross-record validation, live Issue/Project read-back | no prepublication action |
| #193 | addressed, owner-approved, and closed | `ASM-20260811-006`, real candidate report, comment `5260333539`, live Issue/Project read-back | no prepublication action |
| #197 | addressed, focused-validated, and closed | PR base/head changed-release selection, 13/13 renderer tests, candidate workflow contract test, comment `5265085663`, live Issue/Project read-back | exact-head hosted checks remain the release integration gate |
| #61 | release coordination | R2/R3/package implementation integrated | retain open through candidate and tag handoff; close after hosted publication |

## Validation

- External-task delegation contract: 14/14 passed.
- Orchestrator capability contract: 14/14 passed.
- Canonical schema and AI-context validators: passed.
- Real source-task callback from task `019ff328-1490-7cb3-87d1-13b3e246cbf9`: passed after delegated pre-send validation; source-side cross-record validation also passed.
- Candidate build attempt 1: failed because `--profile dotnet-backend` was not the required repository-relative profile YAML; failure retained and callback independently validated.
- Candidate build attempt 2: failed because the external runtime could not write `.codex/release/v0.13.0/candidate`; failure retained and callback independently validated.
- Attempt 3 was explicitly workflow-authorized after proving `artifacts/v0.13.0/candidate` ignored and writable; it passed on clean commit `5ee9b2f5c6307795dd75627992e683144d56f391` and its callback was independently accepted.
- Both real archives passed canonical package validation and external SHA-256 verification; 639 file members were byte-identical across ZIP and TAR, including the 633-file payload.
- A dry-run and real apply from the verified published v0.12.0 payload passed. The apply changed 131 framework-managed operations and safely skipped the two acknowledged target-template reconciliations.
- The version-owned candidate release-state gate passed at `ee348d79986279a9696609613855d77f63473fea` after live read-only Issue/Project reconciliation. A sandbox proxy-blocked attempt was not counted as passing.
- The release profile behind `--critical` passed 9/9 executed checks at clean commit `a9a00dc29063fd5ed5ca86b15d62add11e02e798`, with 0 failures and 0 environment blocks. Fifty-two registry checks were outside that profile and remain explicitly not selected.
- The critical-gate callback/dedup transport failed independently: the successful task's terminal payload drifted from the reported validated record, and a delayed duplicate task overwrote the shared ignored completion path. The owner accepted the split execution/transport evidence, prohibited a fourth local rerun, and authorized exact-head hosted PR validation.
- AI attribution reconciliation rebuilt all nine workflow commits with the primary `gpt-5.6-sol/max` identity and added `gpt-5.6-luna/high` Sub-Agent trailers only where delegated evidence was committed. The owner then rewrote the branch to the clean linear corrected chain at `ff70dc38ab97d287dde9b5a3fe9f364a26b4c947`; all nine old/new pairs remain tree-equivalent, while the old chain and abandoned preservation merge are no longer ancestors.
- #197 binds PR candidate selection to governed release records changed between the PR base and head. Git-backed fixtures prove v0.12 historical validation plus one v0.13 change selects v0.13, no candidate returns the dedicated not-applicable status, multiple candidates fail closed, and deleting a release record fails closed.

## Residual Risk

The owner read back and accepted the real candidate, and #193 is closed with completed prepublication state. The external-task callback/dedup defect remains unresolved and must not be represented as passing; it is not used as the release-runner oracle. The owner's clean history rewrite is authoritative: the old evidence chain and preservation merge remain historical references only and must not be merged back. Any future force-push requires an explanation plus explicit owner authorization, or a prepared branch and exact owner commands. No tag is authorized until #197 provider closeout and exact-head hosted checks pass, the branch integrates through the selected merge-commit topology, and the final clean integrated `main` preparation command passes and prints the exact owner command.
