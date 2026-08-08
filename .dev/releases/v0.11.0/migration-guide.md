# Migrate To v0.11.0

## Supported Source

Automatic governed upgrade is supported from exactly v0.10.0. Earlier versions require reviewed reconciliation.

## Procedure

1. Keep the target worktree clean and preserve target-owned `AGENTS.md`, requirements, specifications, ADRs, operations, provenance, and customization truth.
2. Verify the v0.11.0 archive checksum before extraction or planning.
3. Run the existing dry-run planning interface against the v0.10.0 inventory.
4. Review every collision or reconciliation item; acknowledgement skips an item and never grants overwrite authority.
5. Apply only the bound, fresh plan and retain its receipt.
6. Use rollback against the apply receipt if the target result is rejected.

## Product And Tooling Boundary

The framework payload remains independently versioned and digest-verified. Distribution CLI installation, framework payload acquisition, target initialization, reconciliation, and upgrade are distinct operations. Network access is denied by default unless the selected operation and owner authorization explicitly allow it.

## Deferred Transitions

This migration does not select a native validator language, rename the repository, or add first-class Copilot projections.
