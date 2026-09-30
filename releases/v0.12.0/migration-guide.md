# Migrate To v0.12.0

## Supported Sources

Automatic governed upgrade is supported from exactly v0.11.0. Earlier framework versions require reviewed reconciliation rather than chained assumptions.

## Before You Start

1. Keep the target worktree clean and preserve target-owned `AGENTS.md`, requirements, specifications, ADRs, operations, provenance, and customization truth.
2. Verify the v0.12.0 archive checksum and confirm the recorded source is exactly v0.11.0 before selecting the automatic migration path.
3. Retain the dry-run plan and review all removals, renames, collisions, and acknowledgement-required reconciliation items before apply.

## Migration Steps

1. Run the governed dry-run planner with the v0.11.0 files inventory and the target's current provenance/customization records.
2. Review the active naming changes: `examples/reference/ezspec-test-template.md` becomes `bdd-gwt-test-template.md`; the old EZDDD import map and UContract-specific guides are removed in favor of the neutral Contract guidance.
3. Review target-owned references to the former repository name or deleted example paths. The framework migration must not silently rewrite target-owned documentation or customizations.
4. Acknowledge only the reviewed reconciliation items, apply the bound fresh plan, and retain its receipt.
5. Run target validation against the resolved component/profile selection. Use rollback against the apply receipt if the result is rejected.

## Clean Installation

A clean install selects the mandatory software-development and AI-context lifecycle cores plus the `dotnet-backend` profile by default. Optional provider material remains disabled unless the target explicitly selects it. The package is still one versioned archive; component selection controls effective installation rather than creating separately versioned products.

## Scope Boundaries

- Source-repository workflows, assessments, release history, GitHub Project state, and release-provider reconciliation remain source-only and are not installed as target truth.
- The source-disposition registry explains package omissions but is not itself a downstream policy input.
- Historical old names may remain in immutable evidence. They must not be restored as current operational identity.
- No CLI binary, registry package, signing, or notarization artifact is introduced by this release.
