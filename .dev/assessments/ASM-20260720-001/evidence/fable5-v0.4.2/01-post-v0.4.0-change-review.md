# 01 — Post-v0.4.0 Change Review

Scope: `v0.4.0` (tag) → `main@71c41db` (2026-07-20). Purpose: background context
for the findings in `02`/`03`. Sources: git history, `.dev/backlog/`,
`releases/`, `.dev/workflows/`.

## v0.4.1 (2026-07-18, tag `v0.4.1` = `3daefce`)

Theme: restore the downstream upgrade contract broken in v0.4.0.

- `PKG-001` (HIGH/P0): the v0.4.0 published package emitted a
  clean-install-only `migration.yaml` while the published guide advertised a
  v0.3.0 upgrade path. Fixed by binding versioned migration metadata to the
  exact published v0.3.0 files manifest, producing deterministic
  add/replace/remove/rename/reconcile operations
  (`af18803`, `ff9908c`).
- `PKG-002` (HIGH/P0): the package included source-only release-governance and
  package-builder tests that cannot pass downstream. Fixed by separating
  source and target package gates; extracted target gate passed 19/19
  (`ff9908c`, `3221276`, `25c7847`).
- Governance infrastructure added alongside: post-v0.4 roadmap
  (`.dev/backlog/ROADMAP.md`), backlog item corpus expansion, release gate
  semantics (release-blocker / disposition-gate / activation-gate),
  sub-agent runtime integration planning (`SAG-001`), LF pinning via
  `.gitattributes` (`728fb73`).
- Release execution quality was good: `release.yaml` reached
  `status: published` with the final commit recorded; `release-notes.md`
  contains authored Status/Highlights/Compatibility sections; an 84-line
  migration guide exists. Treat the v0.4.1 registry as the reference example
  of a correctly finalized release.

## v0.4.2 (2026-07-19, tag `v0.4.2` = `f474c3b`)

Theme: patch-compatible content corrections and portability.

- `R042-001`: wrapper identity and routing corrections (five Claude wrappers
  and two routing tables misidentified existing capabilities) (`8345163`).
- `R042-002`: canonical doctrine example alignment — handler, time, naming,
  spec examples (`5d9cd7a`).
- `R042-003`: navigation and lifecycle fact corrections (`89df737`).
- `R042-004`: patch-safe portability corrections to gate scripts
  (interpreter, dependency, root resolution, tests); evidence: Windows Git
  Bash and Codespaces Ubuntu 24.04 both 21/21; macOS explicitly unverified
  (`e76d89c`, `8ecb79c`).
- Alongside: devcontainer (`51be197`), script test syntax fix (`931f5ac`),
  2026-07-19 release-gate revision (v0.4.2 strictly patch-compatible;
  v0.5.0 blockers fixed as `PKG-003`, `SAG-001`, `ENF-001`, `TOOL-001`,
  `LANG-001`) (`90edd79`).
- The remediation phase (executed by OpenAI Codex GPT-5) was sound. The
  publication phase (executed by Gemini 3.1 Pro after a model switch) failed
  in multiple ways — see `02` and `03`.

## Net assessment

The v0.4.x line delivered real contract fixes (upgrade executability, gate
separation, portability) and matured the planning layer (roadmap, gates,
backlog). The unresolved weakness is the release publication procedure
itself: it has never been written down as an executable runbook and has no
pre-tag or post-publication mechanical enforcement. v0.4.1 succeeded on
context continuity (the same model designed and executed it); v0.4.2 was the
first cold-start execution and it failed.
