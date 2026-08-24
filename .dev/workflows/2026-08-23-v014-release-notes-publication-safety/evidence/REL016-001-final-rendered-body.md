<!-- ai-context-release-automation: REL-v0.14.0 -->

# REL-v0.14.0 — Retained-Origin Upgrade Routing

v0.14.0 delivers deterministic retained-origin upgrade routing for the
`dotnet-backend` distribution while preserving exact package and migration
identity across each supported source.

## Highlights

- Records exact migration inputs for governed sources v0.13.0, v0.9.0, and
  v0.6.0 under the v0.14.0 package identity.
- Establishes the source-only support matrix and route-evidence locations for
  the retained origins.
- Adds canonical direct-route evidence for each retained source and keeps the
  nine-item Included Work set bound to the release.

## Compatibility

v0.14.0 is a breaking migration checkpoint with a minimum governed source of
v0.6.0. The package records v0.13.0, v0.9.0, and v0.6.0 as exact package
migration inputs. Their direct or orchestrated route classification must come
only from the completed support matrix and its receipt-bound evidence.

## Release Validation

ZIP/TAR package parity, release-note rendering, package lifecycle validation,
and the canonical retained-origin route proofs for v0.13.0, v0.9.0, and v0.6.0
passed. The generated Release provenance below binds the public artifacts to
the immutable release tag and commit.

## Known Limitations

- Retained-origin routing is defined only for v0.13.0, v0.9.0, and v0.6.0;
  other sources require a separately reviewed migration route.
- Route resolution is read-only and does not authorize package apply or any
  target-owned reconciliation decision.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->

## Included Work

- `#200`
- `#201`
- `#202`
- `#203`
- `#204`
- `#205`
- `#206`
- `#207`
- `#208`

## Release provenance

- Release ID: `REL-v0.14.0`
- Tag: `v0.14.0`
- Commit: `412bb14a16fe75ee65a020b16680def0acc0ff1b`
- Distribution profile: `dotnet-backend`
- Package: `ai-context-dotnet-backend-v0.14.0`
- Archive integrity: verify each archive against its adjacent `.sha256` asset.

## Migration guide

# Migrate To v0.14.0

## Supported Sources

v0.14.0 is a breaking migration checkpoint. Its governed package records
exact migration inputs for v0.13.0, v0.9.0, and v0.6.0. Before applying a
retained-origin upgrade, resolve the source-only support matrix for the
installed version; it is the authority for a direct versus an
orchestrated-multi-hop route. Do not infer a route from this guide.

## Before You Start

1. Start with a clean worktree, retain the installed release manifest, and
   run the applicable route resolver with the exact installed source version.
2. Review any reconciliation operations in the selected package migration
   plan before an apply operation is authorized.

## Migration Steps

1. Use the v0.14.0 package in dry-run mode with the exact selected source
   manifest; do not substitute a similarly named historical package.
2. If the matrix resolves an orchestrated route, preserve each ordered edge,
   its validator output, and its required cutovers before advancing.
3. Apply only after required reconciliation is acknowledged, then run the
   incoming and target-owned validation required by the selected route.

## Clean Installation

For a clean installation, use the v0.14.0 governed package without an upgrade
plan and retain the resulting package manifest as the installed baseline.

## Scope Boundaries

- This source release records framework-owned migration inputs and route
  evidence only; target-owned customizations, approvals, and provider state
  remain outside the package.
- A route resolver is read-only. It does not authorize package apply, target
  mutation, tag creation, GitHub Release creation, or publication.
