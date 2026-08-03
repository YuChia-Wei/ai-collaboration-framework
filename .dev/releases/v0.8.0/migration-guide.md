# Migrate To v0.8.0

## Supported Sources

Automatic migration is supported from the exact published v0.7.0 package
inventory. Targets on an older release must first follow each published route
to v0.7.0. Targets without trusted provenance require reviewed reconciliation.

## Before You Start

1. Confirm the target records the exact published v0.7.0 source and has a clean
   Git worktree at the expected starting commit.
2. Provide Python 3.11 or newer and install the exact dependencies from the
   extracted package `requirements.txt`; the framework will not install them.
3. Preserve target-owned configuration and review every required reconciliation
   instead of treating an automatic candidate as write authorization.

## Migration Steps

1. Extract the v0.8.0 package and run its package-apply planner in dry-run mode
   against the target's recorded v0.7.0 provenance.
2. Review the component selection and all reconciliation items, especially
   target-owned work-management and validation policy.
3. Apply only after the worktree, starting commit, and required reconciliation
   acknowledgements satisfy the package safety contract.
4. Run the target AI-context validator and retain its actual passed, failed,
   blocked-by-environment, not-applicable, or deferred outcome.

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
