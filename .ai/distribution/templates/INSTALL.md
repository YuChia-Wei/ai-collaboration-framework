# AI Context Package Installation

This package is a versioned framework payload, not a whole-repository overwrite.

1. Start from a clean Git worktree and record the current commit.
2. Use Python 3.11 or newer and install the checksum-governed target-tool dependency from the extracted envelope root:

   ```text
   python -m pip install -r requirements.txt
   ```

   The portable direct CLIs support `--diagnostic-format=json`; otherwise a
   blocked preflight is human-readable. Use the POSIX or PowerShell launcher
   when interpreter discovery is needed:

   ```text
   sh payload/.ai/scripts/run-python-entrypoint.sh .ai/scripts/plan-ai-context-package-apply.py --diagnostic-format=json
   pwsh -File payload/.ai/scripts/run-python-entrypoint.ps1 .ai/scripts/plan-ai-context-package-apply.py --diagnostic-format=json
   ```

   A blocked diagnostic suggests, but never executes, a recovery command. Do
   not treat a source-only CLI or release publication operation as part of the
   extracted target prerequisite contract.

3. Validate the archive and its external `.sha256` sidecar. Then validate the
   freshly extracted incoming candidate from the envelope root, using only the
   checksum-governed validator and payload carried by that candidate:

   ```text
   python payload/.ai/scripts/validate-ai-context-payload.py --package-root .
   ```

   This is the portable validation success boundary. Source-only tests are
   classified in `metadata/validation.json`, are not packaged, and cannot
   contribute to this result.
4. From the extracted envelope root, run a dry-run against the target and review every add, replace, remove, rename, and reconcile result:

   ```text
   python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root <target-repository>
   ```

   Clean installations use the package's default component selection. The
   optional backlog provider is disabled by default; enable it explicitly with
   `--enable-provider repo-backlog`. Provider flags are clean-install choices
   and cannot override an upgrade's recorded selection.

   For a migration-schema `2.0.0` or `3.0.0` upgrade, also pass
   `--previous-version <vMAJOR.MINOR.PATCH>` and
   `--previous-files <previous-files.yaml>`. Both values must exactly match one
   source identity in `metadata/migration.yaml`. Schema `1.0.0` packages remain
   readable and infer their single declared source version.
   A component-aware upgrade reads its effective selection from
   `.dev/ai-context/provenance.yaml`. A legacy schema-1 inventory derives
   backlog preservation only from its recorded `.dev/backlog/**` entries.
   Schema-2 inventory without component-aware provenance, or simultaneous
   legacy and new provenance authorities, fails closed.
   If `--plan-output` is used, its path must be outside both the extracted envelope and the target repository so it does not invalidate package checksums or the clean-worktree gate.

5. Apply only after all reconciliation items are acknowledged by operation ID.
   Acknowledgement skips a reconciliation item; it never authorizes overwriting
   or deleting the target path:

   ```text
   python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root <target-repository> --apply --acknowledge <operation-id>
   ```

6. Review `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, including its default and
   resolved selection, resolution evidence, and applied/skipped component
   operation counts. Then run
   `ai-context-init` after a clean installation or `ai-context-upgrader`
   for a versioned upgrade. The package tool does not update validated
   `.dev/ai-context/provenance.yaml` provenance. Legacy
   `.dev/AI-CONTEXT-SOURCE.yaml` remains read-compatible only.
7. Commit target-specific synchronization separately from the framework application when practical.

Target-local validation selection, when a target policy enables it, uses the
ignored and unpackaged `.dev/validation.local.conf`. It must contain exactly
one `validation.routine.local=<approved-mode>` line, can only strengthen the
checked-in policy, and cannot be supplied through an environment variable.

Framework-managed content may be replaced or removed only when its current hash matches the previous released hash. Target templates and target-owned truth are never silently overwritten or deleted.
