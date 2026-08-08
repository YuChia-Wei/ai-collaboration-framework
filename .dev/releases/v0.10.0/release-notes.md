# REL-v0.10.0 — Validation Cost And Release Flow

## Status

Published.

## Highlights

- Adds distinct fast, PR, release, and records-only closeout validation profiles with retained structured evidence.
- Separates package content identity from commit provenance so eligible equivalent inputs can be reused honestly.
- Adds source-only post-tag closeout verification and GitHub Issue-based source release-scope read-back.

## Compatibility

This is a breaking framework release. Automated governed upgrade is supported from v0.9.0; earlier releases require reviewed reconciliation before applying the v0.10.0 package.

## Release Validation

The candidate requires release-profile package, clean-install, v0.9.0 upgrade, Windows, WSL, and hosted Ubuntu evidence before tag creation. The post-tag closeout profile is records-only and does not rerun the full packaging matrix or .NET test projects.

## Publication Completion

Complete this section only after the new annotated v0.10.0 tag and GitHub Release are read back successfully.
