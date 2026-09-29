# REL-v0.4.1 — Executable Upgrade And Downstream Gates

## Status

Published. Annotated tag `v0.4.1` resolves to
`3daefcef1318c12d03c189f232993ccbe04665f2`. Tag-triggered automation
successfully published the stable governed release and its ZIP, tar.gz, and
adjacent checksum assets.

## Highlights

- Replaces the clean-install-only migration metadata emitted by v0.4.0 with a
  versioned operation set bound to the exact published v0.3.0 files manifest.
- Derives deterministic add, replace, remove, rename, and reconcile operations
  from immutable previous and incoming inventories.
- Keeps clean installation independently supported while making the declared
  v0.3.0 upgrade path executable through the extracted package planner.
- Excludes source release-governance and package-builder tests from the public
  payload while keeping them required in the source repository.
- Keeps the packaged safe-apply suite required and reports source-only checks as
  not applicable in downstream repositories.
- Preserves package, files, and migration schema version 1.0.0. This patch does
  not add a multi-source migration contract or remove a published path.

## Compatibility

This is a contract-preserving patch for the governed v0.3.0 package source.
Automatic package migration is declared only from `v0.3.0`.

Targets already on v0.4.0 should remain there and upgrade directly to v0.5.0
after the multi-source contract in `PKG-003` is published. A v0.4.0 target may
perform an explicitly reviewed manual reconciliation to v0.4.1, but v0.4.1
does not claim that path as a governed package-planner source.

Targets originating from v0.0.1 must first follow the published v0.3.0 manual
reconciliation route through the v0.1.0 and v0.2.0 contracts. After validated
v0.3.0 provenance is established, this release provides the governed automatic
v0.3.0-to-v0.4.1 package path.

## Deferred Work

- The full correction set originally assigned to v0.4.1 is moved to required
  v0.4.2 work.
- Multi-source direct upgrades, including v0.4.0-to-latest and the retained
  `dotnet-mq-arch-lab` acceptance target, are assigned to v0.5.0.

## Release Validation

Candidate commit `962919bfa15e7dba1f56e4a9741538d9caf1d7e6`
passed the full source gate at 21/21, the real extracted v0.3.0 upgrade, the
synchronized downstream gate at 19/19, and two byte-identical package builds.
Independent verification `ASM-20260718-001` found no new release blocker.

Final tagged-tree commit
`3daefcef1318c12d03c189f232993ccbe04665f2` passed the 21/21 full gate,
publish-mode rendering, archive validation, and two byte-identical package
builds. GitHub Actions run `29650583394` completed successfully. The four
published assets were downloaded again and passed adjacent checksum, inventory,
member-checksum, and ZIP/tar parity validation.

## Publication Completion

- Release ID: `REL-v0.4.1`
- Annotated tag: `v0.4.1`
- Published commit: `3daefcef1318c12d03c189f232993ccbe04665f2`
- GitHub Actions run: `29650583394`
- Release state: stable, non-draft, non-prerelease
- Published ZIP SHA-256:
  `86ff43d9ba4e8494e3b1ba0d62f8664336f18207f5948c5b6cac0c64aaef0371`
- Published tar.gz SHA-256:
  `f0c1da6f63ccaf105fca2aa0f6795e86744c5ef0ae1b6e135256d0f2372d1323`
- Tag ownership: user-authorized and immutable; automation did not create or
  move the tag
