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
