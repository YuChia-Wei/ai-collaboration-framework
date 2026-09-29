# Migrate To v0.4.1

This is the published migration contract for `REL-v0.4.1`. Annotated tag
`v0.4.1` resolves to
`3daefcef1318c12d03c189f232993ccbe04665f2`. Validate the downloaded archive
against its adjacent `.sha256` asset before planning an upgrade.

## Supported Governed Source

The automatic package source is `REL-v0.3.0` at
`1e782909b7753b2889014516595d72f703a260f3`. The v0.4.1 migration manifest
binds that version and the exact SHA-256 of its published `metadata/files.yaml`.

Migration schema 1.0.0 represents one source. It does not authorize treating a
v0.4.0 inventory as equivalent, nor does path similarity establish a safe base.

## v0.3.0 To v0.4.1

1. Preserve a rollback commit and require a clean target worktree.
2. Confirm `.dev/AI-CONTEXT-SOURCE.yaml` records published v0.3.0 provenance,
   local overrides, and any unresolved reconciliation.
3. Download the v0.4.1 archive plus its matching `.sha256` sidecar and obtain
   `metadata/files.yaml` from the published v0.3.0 archive.
4. Install the extracted envelope dependency from `requirements.txt`.
5. Run the extracted planner in dry-run mode:

   ```text
   python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root <target-repository> --previous-files <v0.3.0-files.yaml> --plan-output <outside-target-plan.yaml>
   ```

6. Review every operation. Acknowledge reconciliation items only after deciding
   that the target-owned or locally changed file must be preserved.
7. Apply from the same clean commit with each accepted acknowledgement:

   ```text
   python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root <target-repository> --previous-files <v0.3.0-files.yaml> --acknowledge <operation-id> --apply
   ```

8. Run `ai-context-upgrader` to reconcile target-owned root, catalog, project
   configuration, and local override truth.
9. Run the target's required gate. The packaged source release and builder
   tests must report not applicable; the safe-apply tests remain required.
10. Finalize `.dev/AI-CONTEXT-SOURCE.yaml` as v0.4.1 only after validation
    succeeds, then remove the pending-apply receipt through the upgrader
    closeout.

## Existing v0.4.0 Targets

The recommended path is to stay on v0.4.0 and upgrade directly to v0.5.0 after
`PKG-003` publishes a multi-source migration contract. This avoids pretending
that the single-source v0.4.1 manifest can safely plan from v0.4.0.

If a v0.4.1 correction is urgently required, use `ai-context-upgrader` for a
fully reviewed manual three-way reconciliation. Do not pass a v0.4.0
`files.yaml` to the v0.4.1 package planner, and do not record v0.4.1 provenance
until target-specific validation succeeds.

## Targets Originating From v0.0.1

`v0.0.1` is a source-snapshot identity, not a governed package inventory.
Follow the published v0.3.0 guide:

1. verify or reconcile the v0.0.1 source identity;
2. account for the v0.1.0 and v0.2.0 contracts without inferring automatic
   remove, rename, or replace authority;
3. complete target validation and establish governed v0.3.0 provenance;
4. use the governed v0.3.0-to-v0.4.1 sequence above.

If v0.3.0 provenance cannot be established, keep the target in unresolved
provenance and do not use the automatic v0.4.1 path.

## Clean Installation

For a new target, omit `--previous-files`, apply the clean-install proposal,
then run `repo-structure-sync` before recording v0.4.1 provenance.

## Scope Boundaries

- Target requirements, specs, ADRs, architecture, operations, domain language,
  root collaboration files, project configuration, and local overrides remain
  target-owned.
- Source workflow, assessment, backlog, and release instances remain excluded.
- The original v0.4.1 content correction set is deferred in full to v0.4.2.
- Multi-source direct upgrade selection is v0.5.0 work under `PKG-003`.
