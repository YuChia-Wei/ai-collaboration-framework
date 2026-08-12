# v0.13 Terminal Release Readiness Report

## Status

`in_progress`

## Reconciliation

| Authority | Current disposition | Evidence | Remaining action |
| --- | --- | --- | --- |
| #187 / `ASM-20260811-001` | addressed, integrated, and closed | `ASM-20260811-002`, PR #195 hosted checks, live Issue/Project read-back | no prepublication action |
| #194 | resolved, validated, and closed | schema 1.1, focused tests, fixed commit `1491178`, retained dispatch/completion, independent cross-record validation, live Issue/Project read-back | no prepublication action |
| #193 | implementation complete, candidate review deferred | `ASM-20260811-006`, PR #195 | review the real v0.13 archive and close before prepublication |
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

## Residual Risk

Issue #193 remains open until the owner reads back the real candidate report. No tag is authorized until the final clean integrated `main` preparation command passes and prints the exact owner command.
