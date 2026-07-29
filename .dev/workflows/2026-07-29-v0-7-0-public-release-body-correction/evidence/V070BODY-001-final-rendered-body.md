<!-- ai-context-release-automation: REL-v0.7.0 -->

# REL-v0.7.0 — Portable Work Management, Provenance, And Release Safety

## Status

Published.

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

The exact backlog and renderer contracts, deterministic package and archive
parity, clean-install apply, exact initialized v0.6.0 upgrade apply, package
matrices, and independent candidate verification passed. The package matrix
recorded 26 passed tests and one environment-gated skip; the apply matrix
recorded 23 passed tests and one Windows capability skip. Neither skip is
counted as passed. Both real apply receipts intentionally leave downstream
provenance finalization to `ai-context-init` or `ai-context-upgrader`; that
later target-owned step is not counted as a candidate pass.

PR #15 passed the hosted release gates and merged the validated candidate to
`main`. The owner-created annotated tag, tag-phase gate, hosted publication,
and exact four-asset Release validation then passed.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Published from immutable annotated tag `v0.7.0`, peeled commit
`49723a943f744820f4bdb2c22de7930693a7106d`, through successful hosted run
`30363397794`. The stable GitHub Release exposes the governed ZIP, tar.gz, and
both checksum sidecars.

## Included Work

- `GOV-002`
- `GOV-003`
- `PKG-004`
- `REL-003`

## Release provenance

- Release ID: `REL-v0.7.0`
- Tag: `v0.7.0`
- Commit: `49723a943f744820f4bdb2c22de7930693a7106d`
- Distribution profile: `dotnet-backend`
- Package: `ai-context-dotnet-backend-v0.7.0`
- Archive integrity: verify each archive against its adjacent `.sha256` asset.

## Migration guide

# Migrate To v0.7.0

## Supported Sources

Automatic upgrade and reviewed reconciliation support only the exact published
v0.6.0 package inventory. Use that package's `metadata/files.yaml` with
`--previous-version v0.6.0`. Targets on v0.5.0 or older must first follow their
published migration route to v0.6.0. A target without credible component-aware
provenance requires manual reconciliation and is not an automatic upgrade.

## Before You Start

1. Use Python 3.11 or newer and install the exact source dependencies when
   running source-side validation.
2. Start from a clean target worktree and record its current commit.
3. Obtain the exact published v0.6.0 `metadata/files.yaml` and verify the
   v0.7.0 archive against its adjacent checksum before extraction.
4. Review target provenance, semantic customizations, provider selection,
   integration branch, review policy, merge policy, and local changes.

## Migration Steps

1. Extract the v0.7.0 package outside the target repository.
2. Run `plan-ai-context-package-apply.py` in its default dry-run mode with the
   extracted package root, target root, exact v0.6.0 files manifest, and
   `--previous-version v0.6.0`.
3. Review every operation and reconcile locally changed target-owned or
   target-template content. The three portable policy targets are managed by
   framework bytes only when their exact previous-release hashes still match.
4. Acknowledge every required reconciliation explicitly, then apply from the
   same clean starting commit. Do not enable a provider merely to complete the
   framework upgrade.
5. Review `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then run `ai-context-init` for
   a clean installation or `ai-context-upgrader` for an existing v0.6.0 target.
   Finalize provenance only after target validation succeeds; the package apply
   receipt does not claim that later step.
6. Run the installed target AI-context, workflow, package, and applicable
   project-owned validation commands. Preserve blocked, skipped, deferred, and
   not-applicable outcomes as distinct from passed checks.

## Clean Installation

For a clean target, apply the default `dotnet-backend` profile in dry-run mode,
review the plan, and then apply from a clean Git worktree. The optional
`repo-backlog` provider remains disabled unless the target owner separately
selects it. No GitHub Issue or Project resource is created.

## Scope Boundaries

- Target work-management state remains usable without a tracker, and tracker
  provider choice remains replaceable and target-owned.
- Existing target modifications enter reconciliation rather than being
  silently overwritten.
- Source workflows, assessments, backlog items, roadmap, release history, and
  source-local GitHub policy are excluded from the downstream payload.
- The upgrade does not migrate historical source evidence, retire deprecated
  identifiers, simplify standards, or adopt GitHub Issues or Projects.
