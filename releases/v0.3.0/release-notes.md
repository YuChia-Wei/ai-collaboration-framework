# REL-v0.3.0 — Version Governance And Safe Upgrades

## Status

Published from the immutable user-created annotated tag `v0.3.0` at commit `1e782909b7753b2889014516595d72f703a260f3`. Post-merge validation and tag-triggered automation completed successfully. The automation did not create or move the tag.

Unlike retrospective `v0.1.0` and `v0.2.0` source snapshots, this record describes a governed installable package published from its validated Git tree.

## Highlights

- Defines SemVer meaning, immutable annotated tags, stable `REL-*` identities, and release lifecycle governance.
- Adds retrospective records and migration guidance for `v0.1.0` and `v0.2.0`.
- Introduces target `.dev/AI-CONTEXT-SOURCE.yaml` provenance with explicit local overrides and unresolved reconciliation.
- Adds the `ai-context-upgrader` skill with thin Codex and Claude wrappers and a human guide.
- Adds a read-only Git-backed three-way comparison tool.
- Adds fail-closed release/source-mode and target/manifest-mode validation with GWT regression tests.
- Defines the `dotnet-backend` portable distribution profile and deterministic `ai-context-dotnet-backend-v0.3.0` ZIP and tar.gz archives.
- Adds package, file-inventory, migration, member-checksum, and external archive-checksum metadata with ZIP/tar payload parity validation.
- Adds dry-run-first, previous-release-hash-aware migration planning that protects target templates and target-owned project truth from silent replacement or removal.
- Provides minimal public `AGENTS.md`, `CLAUDE.md`, and repository catalog seeds instead of packaging this source repository's active root truth.
- Derives `AGENTS.zh-TW.md` only after target English context is finalized, using one canonical translator role with thin Codex, Claude Code, and GitHub Copilot adapters.
- Uses a user-created version tag as publication authorization; GitHub Actions validates and publishes artifacts but never creates, chooses, or moves the tag.
- Keeps external graphs and indexes optional; Git and repository files remain evidence.

## Release Artifacts

The governed release provides these attachments:

- `ai-context-dotnet-backend-v0.3.0.zip`
- `ai-context-dotnet-backend-v0.3.0.zip.sha256`
- `ai-context-dotnet-backend-v0.3.0.tar.gz`
- `ai-context-dotnet-backend-v0.3.0.tar.gz.sha256`

Each archive contains `metadata/package.yaml`, `metadata/files.yaml`, `metadata/migration.yaml`, `metadata/SHA256SUMS.txt`, `INSTALL.md`, pinned target-tool `requirements.txt`, and the installable `payload/`. The packaged planner requires Python 3.11 or newer and `PyYAML==6.0.3`.

## Compatibility

This pre-1.0 minor release intentionally adds a required provenance/version gate and a new package envelope. `v0.0.1`, `v0.1.0`, and `v0.2.0` are supported reconciliation sources, not claims of unattended migration. Hash-gated automatic replace/remove/rename requires a matching previous governed `files.yaml`; when that version-specific baseline is unavailable, the upgrader must use unresolved-provenance reconciliation. Existing targets must create a validated provenance manifest while adopting the upgrader. Root collaboration entries and target-owned project knowledge remain manual reconciliation surfaces.

`v0.0.1` compatibility is limited to manual provenance reconciliation. Its tag confirms source identity, but it has no governed package inventory and does not prove which files a historical target installed.

## Known Limitations

- The comparison tool classifies paths and byte identity; semantic conflict resolution remains a human/agent decision.
- Unversioned or locally forked framework copies require manual baseline reconciliation.
- Version-specific `v0.1.0` and `v0.2.0` baseline manifests and generated migration operations are not bundled yet; those sources require reconciliation unless a separately validated baseline is supplied.
- Retrospective `v0.0.1` is a manual reconciliation source only; prerelease compatibility is not provided by this release.
- Dependency/version validation unrelated to this AI context release contract remains deferred.
