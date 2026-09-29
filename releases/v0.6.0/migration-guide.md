# Migrate To v0.6.0

## Supported Sources

The automatic route supports only an exact published v0.5.0 package inventory.
Use the v0.5.0 archive's `metadata/files.yaml` with
`--previous-version v0.5.0`. Targets on an older release must first follow its
published route to v0.5.0. Historical v0.0.1 targets require reviewed manual
reconciliation before they can establish governed v0.5.0 provenance.

## Before You Start

1. Begin from a clean committed target worktree and retain a rollback commit.
2. Download the v0.6.0 archive and its adjacent `.sha256` sidecar and validate
   both before extraction.
3. Obtain `metadata/files.yaml` from the exact published v0.5.0 package.
4. Review the current provenance, target-owned requirements, specifications,
   ADRs, workflows, operations policy, configuration, and local framework
   changes.
5. Install the extracted envelope's checksum-governed requirements with
   `python -m pip install -r requirements.txt`.

## Migration Steps

1. Extract the v0.6.0 envelope outside the target repository.
2. From the extracted envelope root, run a dry plan:

   ```text
   python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root TARGET_REPOSITORY --previous-version v0.5.0 --previous-files V050_FILES_YAML
   ```

3. Review every add, replace, remove, rename, and reconciliation operation.
   Simultaneous legacy `.dev/AI-CONTEXT-SOURCE.yaml` and new
   `.dev/ai-context/provenance.yaml` authorities fail closed.
4. Apply from the same clean target commit. Supply
   `--acknowledge OPERATION_ID` for each reviewed reconciliation item.
   Acknowledgement keeps
   the target value; it never grants overwrite or deletion authority.
5. Review `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then run
   `ai-context-upgrader` to reconcile provenance, the semantic customization
   ledger, target-owned truth, and the incoming official context.
6. Run the target repository's unit and integration gates plus any selected
   conditional tests or spec-compliance gate.
7. Record v0.6.0 provenance only after validation succeeds and no unresolved
   reconciliation remains.

## Clean Installation

Omit the previous-source inputs. The mandatory software-development and
AI-context lifecycle cores plus the `dotnet-backend` profile are installed.
The optional repository-backlog provider is disabled by default; select it
explicitly with `--enable-provider repo-backlog` when repository-owned backlog
storage is desired. After applying the package, run `ai-context-init` before
recording validated provenance.

## Scope Boundaries

- Target collaboration rules, requirements, specs, ADRs, architecture,
  workflows, operations documents, domain language, configuration, and
  semantic customizations remain target-owned.
- Existing repository backlog data is preserved during upgrade even though the
  provider is optional for clean installations.
- Source release registry, publication operations, source backlog instances,
  assessments, and completed source workflows are not downstream product
  payload.
- A dry-run proposal or reconciliation acknowledgement is never blanket write
  authorization.
