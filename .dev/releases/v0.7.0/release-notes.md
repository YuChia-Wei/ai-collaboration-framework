# REL-v0.7.0 — Portable Work Management, Provenance, And Release Safety

## Status

Planned governed candidate. v0.7.0 is not tagged or published.

## Highlights

- Adds a tracker-neutral work-management lifecycle that keeps conversation,
  candidate work, authorized execution, workflow completion, PR integration,
  and integrated facts distinct.
- Adds portable AI execution provenance and attribution governance without
  normalizing unavailable provider-native identity.
- Proves deterministic downstream payload exclusion, clean installation, and
  exact initialized upgrade from the published v0.6.0 package.
- Makes candidate backlog membership and generated Included Work fail closed
  from v0.7.0 onward while preserving human-authored release notes.

## Compatibility

v0.7.0 is a backward-compatible pre-1.0 minor release. The only automatic and
reviewed reconciliation source is the exact published v0.6.0 package inventory.
Targets on an older version must first follow each version's published route to
v0.6.0. Existing target-owned customizations, provider choice, integration
branch, review policy, merge policy, and tracker identity remain target-owned.

The package and files schemas remain at `2.0.0`; the migration schema remains
at `3.0.0`. Deprecated compatibility aliases and historical evidence paths are
retained.

## Known Limitations

- The portable execution-provenance contract and deterministic fixtures are
  verified, but native Claude and GitHub Copilot commit-attribution fixtures
  remain unavailable. This deferred evidence is not reported as passed.
- Automatic upgrade is supported only from the exact published v0.6.0
  inventory. Direct automatic upgrade from v0.5.0 or older is unsupported.
- Candidate validation must report any environment-gated or platform-capability
  skip separately. A skip, deferred check, or not-applicable gate is never
  counted as passed.

## Not Included

- No GitHub Issue, GitHub Project, field, view, automation, mapping, or provider
  integration is created by this release. Source-local GitHub policy is not a
  downstream default.
- Historical archive migration, deprecated identifier retirement, standards
  simplification, issue/timeline schema deliberation, existing-agent
  initialization exploration, and observability architecture remain separately
  gated work.

## Release Validation

The included contracts passed their independent readiness assessments before
candidate authoring. The formal candidate must still pass exact backlog and
renderer validation, deterministic package and archive parity, clean install,
exact v0.6.0 initialized upgrade, AI-context and workflow validation, independent
candidate verification, hosted pull-request checks, merge, and current-main
pre-tag validation. Only observed outcomes will replace this planned statement.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Not published. Tag, hosted publication, package assets, run identity, and final
registry evidence remain absent until separately authorized and observed.
