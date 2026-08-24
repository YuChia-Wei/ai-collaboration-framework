# GOV-012 Remediation Report

## Subject

- Issue: `#245`
- Base: `origin/main@4be33ff90de061dc1db221f60e57ff6130cab54a`
- Branch: `codex/2026-08-24-retire-repository-backlog-authority`
- Owner: `ai-context-governance`

## Decisions

- Live GitHub Issues and Project #3 own current work-item and portfolio state.
- `.dev/workflows/` owns execution and validation evidence; integrated `main`
  owns repository truth; provider state alone does not authorize execution.
- `.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml` is the single active
  source GitHub policy. The old backlog-owned path is absent; its migration
  adapter is retained only as `github-legacy-migration.yaml` historical evidence.
- The 77 tracked `.dev/backlog` paths are frozen by a path-and-Git-blob-byte
  SHA-256, independent of checkout line-ending materialization. Staged or
  unstaged backlog drift is rejected separately.
  ROADMAP, local items, plans, provider mapping, and Project snapshot are not
  current planning inputs.
- v0.5.0-v0.9.0 release `planning.backlog_refs` remain resolvable. v0.10.0 and
  later release scope remains online GitHub Issue based.
- The downstream provider-neutral work-item binding capability remains packaged
  through the public target backlog template; source-only policies and tools are
  excluded.

## Validation State

Focused authority, workflow, terminal closure, legacy provider, release-state,
profile projection, packaging boundary, source entrypoint, shell asset, and AI
context checks were run. Windows Temp ACL blocks observed in the sandbox were
preserved and the affected workflow-provider suite passed in host context.
HEAD-bound source governance, delegated aggregate validation, and the independent
exact-head audit completed under `GOV012-VAL-001`.

The first independent audit at
`0c6c9c88a84ef358b52d732c66844b858d51e7c3` is retained as
`ASM-20260824-001`. It found `GOV012-AUD-001` (HIGH): prospective task JSON was
checked for retired local bindings, but the canonical workflow locator was not.
Governance accepted that finding and applied the same recursive check to every
prospective locator with a locator-specific regression test. The repaired head
requires fresh release validation and a separate independent audit.

The next audit at `801679ee0fc9a30d8d9af81f12bc941c8c2f0a1c` is retained as
`ASM-20260824-002`. It confirmed locator scanning but found
`GOV012-AUD-002` (HIGH): serialized timestamps with different explicit offsets
were compared lexically. Governance replaced that gate with offset-aware
chronological comparison, rejects naive or malformed timestamps, and tests
later and equal instants expressed with different offsets.

The first audit of `ba9b5277f98626b9ff6d07dc1062956a476eff2b` stopped fail-closed
after a redundant packaging suite hit Windows ACL cleanup failure; that blocked
attempt is retained and was not relabeled as passed. A fresh read-only audit of
the same subject found `GOV012-AUD-003` (HIGH): the frozen aggregate read
worktree bytes, so clean CRLF/LF materialization could vary by checkout while
Git status remained clean. Governance now hashes raw `HEAD` blob bytes and
separately rejects staged or unstaged backlog drift.

The first aggregate run for the repaired subject
`ba7c159a2d8fd58291ddc1e92036cb82acd23fb6` retained a failed 824-second
receipt after sandbox Temp ACL behavior caused `python-source-entrypoints` to
time out. A focused host-context run passed in 21.194 seconds. The separately
dispatched host-context aggregate reroute then passed in 2012 seconds with 65
selected, 62 executed, zero failed, blocked, warning, or deferred checks, and
three not-applicable checks. The failed receipt remains failed.

`ASM-20260825-001` is the terminal independent assessment for the same exact
subject. It verified all three prior findings closed, the 77-path Git-blob
digest, staged and unstaged drift rejection, release compatibility, provider-
neutral packaging, and both retained aggregate receipts. It returned `PASS`
with no severity finding and did not mutate the subject.

## Excluded Actions

No push, pull request, merge, Issue closure, Project mutation, target-release
assignment, tag, Release, asset, published package byte, bulk backlog mutation,
or physical historical-record deletion was performed.
