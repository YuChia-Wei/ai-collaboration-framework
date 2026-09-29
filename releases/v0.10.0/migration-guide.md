# Migrate To v0.10.0

## Supported Sources

Automated governed upgrade is supported from v0.9.0. Earlier source versions require a reviewed reconciliation before an apply operation.

## Before You Start

1. Start from a clean, initialized target repository and retain its target-owned customizations.

## Migration Steps

1. Plan the v0.10.0 package upgrade with the target's existing v0.9.0 inventory and review the reconciliation output.
2. Acknowledge the reviewed reconciliation, apply only to a clean worktree, then run the target-owned validation commands.

## Clean Installation

Use the governed v0.10.0 package for a clean target and validate the installed package manifest, archive checksums, and profile-owned commands.

## Scope Boundaries

- Source-repository GitHub Issue authority and release-closeout tooling are not included in the downstream package.
