# Migrate To v0.4.2

This is the published migration contract for `REL-v0.4.2`. Annotated tag
`v0.4.2` resolves to
`f474c3b058cb9f89f93929e0732fc1f276422dd9`. Validate a downloaded archive
against its adjacent `.sha256` asset before planning an upgrade.

## Supported Governed Source

The automatic package source is `REL-v0.3.0` at
`1e782909b7753b2889014516595d72f703a260f3`. Migration schema `1.0.0`
represents one source and does not authorize treating a v0.4.0 inventory as
equivalent.

## v0.3.0 To v0.4.2

1. Preserve a rollback commit and require a clean target worktree.
2. Confirm `.dev/AI-CONTEXT-SOURCE.yaml` records published v0.3.0 provenance,
   local overrides, and unresolved reconciliation.
3. Download the v0.4.2 archive and matching `.sha256` sidecar, plus
   `metadata/files.yaml` from the published v0.3.0 archive.
4. Install the extracted envelope dependencies from `requirements.txt`.
5. Run the extracted planner in dry-run mode with the v0.3.0 files manifest.
6. Review every operation and acknowledge reconciliation only after deciding
   which target-owned or locally changed files must be preserved.
7. Apply from the same clean target commit.
8. Run `ai-context-upgrader` to reconcile target-owned collaboration,
   requirement, spec, ADR, architecture, operations, project configuration,
   and local override truth.
9. Run the target's required gate. Source-only release and builder tests are
   not applicable downstream; packaged safe-apply checks remain required.
10. Record v0.4.2 provenance only after target validation succeeds.

The exact planner commands and acknowledgement rules remain those documented by
the v0.4.1 migration guide because v0.4.2 does not change the package or
migration schema contract.

## Existing v0.4.0 Targets

The recommended path is to stay on v0.4.0 and upgrade directly to v0.5.0 after
`PKG-003` publishes a multi-source migration contract. Do not pass a v0.4.0
`files.yaml` to the v0.4.2 single-source planner.

If v0.4.2 corrections are urgently required, use `ai-context-upgrader` for a
fully reviewed manual three-way reconciliation. Do not record v0.4.2
provenance until target-specific validation succeeds.

## Targets Originating From v0.0.1

v0.0.1 is a source-snapshot identity, not a governed package inventory. First
follow the published manual route through the v0.1.0 and v0.2.0 contracts and
establish governed v0.3.0 provenance. If provenance cannot be established,
keep the target unresolved and do not use the automatic planner.

## Clean Installation

For a new target, omit the previous-files input, apply the clean-install
proposal, then run `repo-structure-sync` before recording v0.4.2 provenance.

## Scope Boundaries

- Target requirements, specs, ADRs, architecture, operations, domain language,
  root collaboration files, project configuration, and local overrides remain
  target-owned.
- Source workflow, assessment, backlog, and release instances remain excluded.
- Runtime wrapper, doctrine, navigation, and portability corrections do not
  authorize overwriting target-owned truth.
- Multi-source direct upgrades remain v0.5.0 work under `PKG-003`.
