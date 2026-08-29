# Migrate To v0.15.1

## Supported Source

The automatic upgrade source is the immutable published v0.15.0 package. Use
the `ai-collaboration-framework-v0.15.1` archive and verify its adjacent
SHA-256 sidecar before extraction.

## Before You Start

1. Use a clean, committed target worktree and retain a recoverable starting
   commit.
2. Preserve the installed v0.15.0 `metadata/files.yaml` manifest.
3. Extract the v0.15.1 package outside the target repository.
4. Keep plan output outside both the extracted package and target repository.

## Dry-Run And Apply

1. From the extracted v0.15.1 envelope, run
   `payload/.ai/scripts/plan-ai-context-package-apply.py` with the package root,
   target root, `--previous-version v0.15.0`, the retained v0.15.0 files
   manifest, and an external plan-output path. Omit `--apply` first.
2. Review every add, replace, remove, rename, and reconcile result. Acknowledge
   only operation IDs whose target-owner disposition has been decided.
3. Confirm the target still matches the clean starting point, then repeat the
   command with `--apply` and the approved acknowledgements.
4. Retain the apply receipt, any pending-remediation packet, installed
   provenance, and customization records.

An acknowledgement applies only to its named reconciliation disposition; it
does not authorize blanket overwrite or deletion of target-owned files.

## Clean Installation

For a clean target, use the v0.15.1 package planner without previous-version or
previous-manifest arguments. Keep the default `dotnet-backend` profile unless
the target owner explicitly selects another supported component.

## Validation Readiness

If initialization reports `action_ready: false` with
`effective-rule-state-missing`, do not treat installation as ready for governed
actions. Complete `ai-context-init` for first adoption or
`ai-context-upgrader` for an initialized target, produce the effective-rule
state, and rerun the target validation before continuing.

## Scope Boundaries

- v0.15.0 tags, Releases, assets, checksums, receipts, routes, and package bytes
  remain immutable.
- Dry-run output is a proposal, not apply authorization.
- Target-owned reconciliation and validation decisions remain outside the
  source package.
