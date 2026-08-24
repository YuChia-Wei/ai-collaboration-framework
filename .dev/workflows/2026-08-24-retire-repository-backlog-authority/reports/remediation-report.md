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
- The 77 tracked `.dev/backlog` paths are frozen by a path-and-byte SHA-256.
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
exact-head audit remain assigned to `GOV012-VAL-001`.

## Excluded Actions

No push, pull request, merge, Issue closure, Project mutation, target-release
assignment, tag, Release, asset, published package byte, bulk backlog mutation,
or physical historical-record deletion was performed.
