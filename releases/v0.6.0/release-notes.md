# REL-v0.6.0 — Componentized AI Context And Development Orchestration

## Status

Published.

## Highlights

- Defines one componentized release with mandatory software-development and
  AI-context lifecycle cores, the `dotnet-backend` profile, and an optional
  repository-backlog provider that defaults off for clean installations.
- Moves target provenance and semantic customization authority to
  `.dev/ai-context/provenance.yaml` and
  `.dev/ai-context/customizations.yaml`.
- Activates `software-development-orchestrator` and `ai-context-init` while
  retaining `dev-workflow` and `repo-structure-sync` as thin deprecated
  compatibility aliases with no scheduled removal.
- Preserves requirements, specifications, architecture, workflows, target-aware
  unit and integration testing, and selectable spec-compliance validation as
  first-class software-development capabilities.
- Introduces component-aware package metadata, deterministic upgrade planning,
  Terra model-in-the-loop release evidence, version-owned release gates, and
  Node.js 24-native hosted artifact transfer.

## Compatibility

v0.6.0 is a pre-1.0 breaking release. The automatic upgrade route accepts only
the exact published v0.5.0 package inventory. Existing component and backlog
selection is preserved and recorded; target-owned truth and semantic
customizations are reconciled rather than overwritten. Older releases must
first reach v0.5.0 through their published supported route.

## Release Validation

All v0.6.0 roadmap blockers, activation work, and simplification disposition
are resolved. Deterministic and target reconciliation suites passed, the
owner-selected Terra evaluation passed 8/8 critical and 8/8 full outcomes, and
PR #7 passed its hosted governance, Ubuntu, and candidate-discovery jobs before
merging to `main`. PR #8 then passed governance, Ubuntu quick, and the actual
package-candidate build and archive-parity job before merging the candidate to
`main`. The current-main pre-tag and tag gates also passed.

## Publication Completion

Published from immutable annotated tag `v0.6.0`, peeled commit
`8b98b5f917513f2d143f42a322050a1162bb63f9`, through successful hosted run
`30074558122`. The stable GitHub Release exposes the governed ZIP, tar.gz, and
both checksum sidecars.
