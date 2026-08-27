# REL-v0.15.0 — Unified Public Framework Identity

v0.15.0 adopts `ai-collaboration-framework` as the single public package and
archive identity while keeping `dotnet-backend` as the technology profile.
The release also completes the package-apply performance, validation-lane, and
agent-execution reliability work required before this identity cutover.

## Highlights

- Publishes ZIP and tar.gz packages under the canonical
  `ai-collaboration-framework-v0.15.0` base, with matching SHA-256 sidecars.
- Keeps every v0.14.0-and-earlier package name and published artifact immutable;
  the rename applies only to v0.15.0 and later releases.
- Provides an explicit v0.14.0-to-v0.15.0 upgrade boundary with consistent
  package, envelope, archive, manifest, receipt, and payload-fingerprint
  identity.
- Batches package-apply Git inspection into bounded phase snapshots instead of
  repeating target inspection for each managed path.
- Separates fast identity checks, clean-install checks, and actual durable
  upgrade execution so synthetic evidence cannot stand in for a real upgrade.
- Adds deterministic execution packets, worktree leases, evidence binding,
  retry controls, and graph-freshness checks for delegated agent work.

## Compatibility

This is a breaking pre-1.0 package-identity release. Automatic upgrade input is
the published v0.14.0 package. Consumers must select the new
`ai-collaboration-framework-v0.15.0` archive explicitly; the historical
`ai-context-dotnet-backend-v0.14.0` name remains valid only for the immutable
v0.14.0 release.

The default technology profile remains `dotnet-backend`. No CLI, binary,
registry, installer, or toolchain identity is renamed by this release.

## Upgrade Summary

Start from a clean target worktree, retain the v0.14.0 files manifest, and run
the extracted v0.15.0 package planner in dry-run mode with
`--previous-version v0.14.0`. Review every reconciliation item before an apply
operation and preserve the resulting receipt and provenance records.

## Known Limitations

- Automatic package migration is defined from v0.14.0. Earlier installations
  must first follow their governed route to v0.14.0.
- Package apply never authorizes target-owned reconciliation decisions; those
  remain with the target repository owner.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
