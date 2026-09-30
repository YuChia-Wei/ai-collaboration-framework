# Migrate To v0.5.0

This guide covers the governed package migration contract for REL-v0.5.0.
Validate every downloaded archive against its adjacent `.sha256` asset before
planning an upgrade. Begin from a clean committed target and preserve a
rollback commit.

## Supported Automatic Sources

Migration schema `2.0.0` supports these exact automatic sources:

- v0.3.0;
- v0.4.0;
- v0.4.1;
- v0.4.2.

The planner selects operations only when `--previous-version` and
`--previous-files` match the version and SHA-256 of one published source
inventory. Do not substitute a nearby version or reuse another release's
`files.yaml`.

## Before You Start

1. Confirm `.dev/AI-CONTEXT-SOURCE.yaml` records one supported source version,
   its immutable source commit, local overrides, and unresolved reconciliation.
2. Download the v0.5.0 archive and matching `.sha256` sidecar.
3. Obtain `metadata/files.yaml` from the exact published source package.
4. Install dependencies from the extracted envelope's `requirements.txt`.
5. Require a clean committed target worktree and retain a rollback commit.

## Automatic Upgrade

1. Extract the v0.5.0 package envelope outside the target repository.
2. Run the extracted
   `payload/.ai/scripts/plan-ai-context-package-apply.py` in dry-run mode with
   the exact previous version and files manifest.
3. Review every operation. Target templates, target-owned truth, and locally
   changed framework-managed files must appear as reconciliation rather than
   overwrite candidates.
4. Acknowledge a reconciliation item only after deciding to preserve that
   target value. Acknowledgement means skip; it never grants overwrite or
   deletion authority.
5. Apply from the same clean target commit using the same package and exact
   source inventory.
6. Run `ai-context-upgrader` to reconcile target-owned collaboration,
   requirement, spec, ADR, architecture, operations, project configuration,
   domain language, and declared override truth.
7. Run the target repository's required gate.
8. Record v0.5.0 provenance only after target validation succeeds and no
   unresolved reconciliation remains.

## Existing v0.4.2 Targets

v0.4.2 is an automatic source. Supply the exact `metadata/files.yaml` from the
published v0.4.2 package together with `--previous-version 0.4.2`. The planner
rejects a v0.4.1, v0.4.0, or v0.3.0 manifest presented as v0.4.2 provenance.

Review every proposed operation and preserve target-owned truth and local
overrides through reconciliation acknowledgement. Record v0.5.0 provenance
only after the target's complete gate passes.

## Targets Originating From v0.0.1

v0.0.1 is a source snapshot rather than a governed package inventory. Follow
the published manual v0.1.0 and v0.2.0 reconciliation path, establish governed
v0.3.0 provenance, and then use the exact v0.3.0 automatic route.

## Clean Installation

For a new target, omit previous-source inputs and select only the package's
`clean_install.operations`. After apply, run `repo-structure-sync` before
recording v0.5.0 provenance.

## Scope Boundaries

- Target requirements, specs, ADRs, architecture, operations, domain language,
  root collaboration files, project configuration, and local overrides remain
  target-owned.
- Source workflow, assessment, backlog, and release instances remain excluded
  from the installed package.
- A dry-run proposal is not write authorization.
- Unknown provenance, source-manifest mismatch, dirty worktree state, or
  unacknowledged reconciliation must fail closed.
