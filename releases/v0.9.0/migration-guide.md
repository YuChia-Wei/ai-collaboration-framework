# Migrate To v0.9.0

## Supported Sources

Automatic planning and reviewed reconciliation are supported only from the
exact published v0.8.0 package inventory. Targets on an older release must
first follow their published route to v0.8.0. Targets without credible
component-aware provenance require manual reconciliation and are not an
automatic upgrade.

## Before You Start

1. Confirm that the target records the exact published v0.8.0 source and has a
   clean Git worktree at the intended starting commit.
2. Verify the public v0.8.0 archive against its adjacent checksum sidecar and
   retain that package's exact `metadata/files.yaml` inventory. Verify the
   v0.9.0 archive the same way before extraction.
3. Preserve target-owned collaboration, requirements, specifications, ADRs,
   architecture, operations, provider selections, and local changes for
   reconciliation rather than treating the package as overwrite authority.
4. Review the target's provenance, semantic customizations, effective-rule
   state, and any unresolved `.dev/AI-CONTEXT-APPLY-PENDING.yaml` receipt.
5. Identify target Git ignore or exclude rules that match selected
   framework-managed paths. The package planner reports those paths as
   unresolved; it does not rewrite target-owned ignore configuration.

## Migration Steps

1. Extract the v0.9.0 package outside the target repository and run
   `plan-ai-context-package-apply.py` in its default dry-run mode with the
   extracted package root, target root, exact v0.8.0 `metadata/files.yaml`, and
   `--previous-version v0.8.0`.
2. Review the proposed file operations and every reconciliation item. Pay
   particular attention to moved canonical engineering-rule/standards content,
   the bundled-provider root, target-effective rule state and task packets,
   local customizations, and ignored framework-managed paths.
3. Apply only from the same clean starting commit after every required
   acknowledgement is explicit. An acknowledgement preserves target-owned
   content and does not grant an overwrite or deletion permission.
4. Reconcile `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then use
   `ai-context-upgrader` to finalize provenance, semantic customizations, and
   target-owned truth only after target validation and an independent
   post-upgrade audit succeed.
5. Keep the bundled provider inactive until the target explicitly supplies the
   required reference-in-place wiring, configuration, and invocation evidence.
   Architecture Kit remains unavailable and cannot be selected by this
   migration.
6. Run the installed target AI-context validator and applicable project-owned
   validation commands. Preserve each actual passed, failed,
   blocked-by-environment, not-applicable, or deferred outcome separately.

## Clean Installation

For a clean target, run the package planner in dry-run mode and select the
required `dotnet-backend` components. The optional `repo-backlog` provider
remains disabled unless the target owner explicitly enables it. Source-only
framework tests under `tools/` are not downstream package components and are
not copied as bundled-provider production projects.

## Scope Boundaries

- Target-owned collaboration, provider, work-management, validation, product,
  requirement, specification, ADR, architecture, and operations truth remains
  target-owned.
- GitHub Issues and Projects are not required by the portable framework.
- Source release/build/provider tools, source-only framework tests, workflow
  history, assessment instances, source backlog, and source release history
  remain excluded from the downstream payload.
- The online-only Issue #128 correction does not create a target backlog item
  or change the separately owned EVAL-002 / Issue #95 evaluation scope.
- Architecture Kit cutover, `materialize-to-tools`, historical archive
  migration, and legacy identifier retirement are not included.

## Published Package Identity

The governed package is published at the stable
[v0.9.0 GitHub Release](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/releases/tag/v0.9.0)
from immutable annotated tag `v0.9.0`, peeled commit
`c14a3260cba7d0a9e2b67b73df9e221280d2d2ef`. Verify the selected ZIP or tar.gz
against its adjacent checksum sidecar before planning installation or the
supported v0.8.0 upgrade.
