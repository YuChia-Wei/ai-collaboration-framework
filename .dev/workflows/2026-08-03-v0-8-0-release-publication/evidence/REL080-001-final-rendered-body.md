<!-- ai-context-release-automation: REL-v0.8.0 -->

# REL-v0.8.0 — Canonical Skill Ownership, Python Readiness, And Work Authorization

## Status

Published.

## Highlights

- Co-locates single-owner Python implementations and contract tests with their
  canonical skills while preserving published compatibility entrypoints.
- Adds consistent fail-closed Python 3.11+ and exact dependency diagnostics to
  all 25 governed production CLIs, including portable POSIX and PowerShell
  launchers plus human-readable and JSON outcomes.
- Adds provider-neutral work-item binding and independently selectable merge-
  gate policy. Explicit owner approval remains required; provider state alone
  never authorizes execution, and downstream teams retain their own selection.

## Compatibility

v0.8.0 is a backward-compatible pre-1.0 minor release with exact
automatic upgrade support from the published v0.7.0 package. Existing Python
command paths and thin compatibility entrypoints remain supported, and the
current payload comparison removes no published path.

Python 3.11 or newer remains required. Commands that require YAML use the exact
PyYAML version declared by the repository or extracted package. Prerequisite
diagnostics never install dependencies, create an environment, access the
network, replace the selected runtime, or mutate a target.

Existing target-owned work-management and validation choices remain target-
owned. New initialization templates leave work-item binding and merge-gate
selection unresolved until the target team explicitly chooses `required`,
`optional`, or `disabled`.

## Known Limitations

- The retained external downstream integration requires an explicitly supplied
  repository; its prior conditional skip is not counted as passed.
- This Windows host cannot create the package-apply symlink fixture without an
  unavailable capability; that conditional skip is not counted as passed.
- Proposal #75 aggregate/downstream selection architecture and Proposal #76
  generalized environment readiness are not part of this release.
- Published shell compatibility-entrypoint relocation remains deferred pending
  separate downstream lifecycle evidence.

## Release Validation

The candidate archives, clean installation, exact initialized v0.7.0 upgrade,
release contracts, package matrices, and independent candidate verification
passed. The packaging matrix recorded 28 passed tests and one retained-
downstream conditional skip; the package-apply matrix recorded 25 passed tests
and one Windows symlink-capability skip. Neither skip is counted as passed.
Both real apply receipts intentionally leave downstream provenance finalization
to `ai-context-init` or `ai-context-upgrader`; that target-owned step is not
counted as a candidate pass.

The complete repository critical gate also passed. PR #81 passed all five
hosted jobs and merged the validated candidate to `main`. Merged-main provider
read-back and the current-main pre-tag gate then passed. The owner-created
annotated tag, tag-phase gate, hosted publication, downloaded checksum
sidecars, and exact ZIP/tar payload-parity validation also passed.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Published from immutable annotated tag `v0.8.0`, peeled commit
`97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25`, through successful hosted run
`30786537723`. The stable GitHub Release exposes the governed ZIP, tar.gz, and
both checksum sidecars.

## Included Work

- `SKILL-002`
- `TOOL-002`
- `WIBIND-001`

## Release provenance

- Release ID: `REL-v0.8.0`
- Tag: `v0.8.0`
- Commit: `97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25`
- Distribution profile: `dotnet-backend`
- Package: `ai-context-dotnet-backend-v0.8.0`
- Archive integrity: verify each archive against its adjacent `.sha256` asset.

## Migration guide

# Migrate To v0.8.0

## Supported Sources

Automatic migration is supported from the exact published v0.7.0 package
inventory. Targets on an older release must first follow each published route
to v0.7.0. Targets without trusted provenance require reviewed reconciliation.

## Before You Start

1. Confirm the target records the exact published v0.7.0 source and has a clean
   Git worktree at the expected starting commit.
2. Verify the public v0.7.0 archive against its adjacent checksum sidecar and
   retain that package's exact `metadata/files.yaml` inventory.
3. Provide Python 3.11 or newer and install the exact dependencies from the
   extracted package `requirements.txt`; the framework will not install them.
4. Complete or reconcile any earlier `.dev/AI-CONTEXT-APPLY-PENDING.yaml`
   receipt before starting another package apply.
5. Preserve target-owned configuration and review every required reconciliation
   instead of treating an automatic candidate as write authorization.

## Migration Steps

1. Extract the v0.8.0 package and run its package-apply planner in dry-run mode
   against the target's recorded v0.7.0 provenance. Supply the exact public
   inventory with `--previous-files` and `--previous-version v0.7.0`.
2. Review the component selection and all reconciliation items, especially
   target-owned work-management and validation policy.
3. Apply only after the worktree, starting commit, and every required
   `--acknowledge OPERATION_ID` satisfy the package safety contract.
   Acknowledgement preserves the target value; it never grants overwrite or
   deletion authority.
4. Review `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then run
   `ai-context-upgrader` to reconcile provenance, semantic customizations, and
   target-owned truth. Finalize provenance only after target validation and the
   required independent post-upgrade audit succeed.
5. Run the target AI-context validator and project-owned gates, retaining each
   actual passed, failed, blocked-by-environment, not-applicable, or deferred
   outcome separately.

## Clean Installation

For a clean installation, select the required components through the package
planner. During `ai-context-init`, explicitly decide work-item binding and
merge-gate modes for the target; the template intentionally leaves both values
unresolved. Python prerequisite recovery remains a human decision and is never
performed automatically.

## Scope Boundaries

- Target-owned collaboration, provider, work-management, validation, product,
  requirement, specification, ADR, architecture, and operations truth remains
  target-owned.
- GitHub Issues and Projects are not required by the portable framework.
- Source release/build/provider tools and repository workflow history remain
  excluded from the downstream payload.
- Proposals #75 and #76, historical archive migration, legacy identifier
  retirement, and published shell entrypoint relocation are not included.
