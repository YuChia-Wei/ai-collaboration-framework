# Migrate To v0.15.0

## Supported Source

The automatic upgrade source is the immutable published v0.14.0 package. Its
public archive base remains `ai-context-dotnet-backend-v0.14.0`; the incoming
v0.15.0 archive base is `ai-collaboration-framework-v0.15.0`.

Do not rename a v0.14.0 archive or substitute a similarly named file. Select
each package by its own version-aware identity and verify its adjacent SHA-256
sidecar before extraction.

## Before You Start

1. Use a clean, committed target worktree and retain a recoverable starting
   commit.
2. Preserve the installed v0.14.0 `metadata/files.yaml` manifest.
3. Extract the v0.15.0 package into a location outside the target repository.
4. Keep the plan output outside both the extracted package and target.

## Dry-Run And Apply

1. From the extracted v0.15.0 envelope, run
   `payload/.ai/scripts/plan-ai-context-package-apply.py` with the package root,
   target root, `--previous-version v0.14.0`, the retained v0.14.0 files
   manifest, and an external plan-output path. Omit `--apply` for this first
   run.
2. Review every add, replace, remove, rename, and reconcile result. Acknowledge
   only the operation IDs whose target-owner disposition has been decided.
3. Confirm that the target is still at the same clean starting point, then run
   the same command with `--apply` and the approved acknowledgements.
4. Retain the apply receipt, pending-remediation packet when present, and the
   installed provenance and customization records.

An acknowledgement skips or accepts the named reconciliation disposition; it
does not grant blanket permission to overwrite or delete target-owned files.

## Clean Installation

For a clean target, use the v0.15.0 package planner without previous-version or
previous-manifest arguments. Keep the default `dotnet-backend` profile unless
the target owner explicitly selects another supported component.

## Identity Boundary

- v0.14.0 and earlier: `ai-context-dotnet-backend-v{version}`.
- v0.15.0 and later: `ai-collaboration-framework-v{version}`.
- `dotnet-backend` remains the profile/component identity.
- CLI, binary, registry, installer, and toolchain identities are outside this
  migration.

## Scope Boundaries

- Never rewrite historical tags, Releases, assets, checksums, receipts, route
  assets, package metadata, or published bytes.
- Dry-run output is a proposal, not apply authorization.
- Target-owned validation and reconciliation decisions remain outside the
  source package.
