# Migrate To v0.16.0

## Supported Sources

The direct sources are v0.6.0, v0.9.0 and v0.15.1. Each source uses one migration edge to the same incoming v0.16.0 archive. Intermediate package installation is not part of these routes. Later releases retain v0.6.0, v0.9.0 and their immediate predecessor until an explicit owner-approved versioned deprecation.

## Before You Start

1. Preserve a clean target commit and its current provenance, semantic customization ledger, effective-rule state and packets. Reconcile missing, stale or duplicate authority before application.
2. Verify the incoming public ZIP and sidecar, the support matrix and its exact assets. Obtain the original installed version's public `metadata/files.yaml`; do not recreate it from a checkout.
3. Extract the incoming envelope outside the target and install its checksum-governed requirements. Resolve the matrix with `plan-ai-context-upgrade.py --matrix SUPPORT_MATRIX --origin INSTALLED_VERSION --target v0.16.0`; require `route_kind: direct`.

## Migration Steps

From the extracted incoming envelope, all three origins use this entry point:

```text
python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root TARGET --previous-version INSTALLED_VERSION --previous-files ORIGINAL_FILES_YAML --plan-output PLAN --remediation-packet-output PACKET
```

`INSTALLED_VERSION` is exactly v0.6.0, v0.9.0 or v0.15.1. Review the packet and every source-specific semantic cutover before writing an independent owner decision. An automatic proposal is not authorization.

Reconcile provider/component selections, target-owned validation and ignore policy, project naming and technology-provider references, commit grammar adoption, effective-rule catalog and packet freshness, and retired skill references. Preserve customized or target-owned files. Remove obsolete framework files only when the original manifest proves unchanged ownership. Retain historical skill identifiers in historical records.

Apply the same command with `--apply --remediation-decision DECISION`. Execute the target-owned validation profile, record its exact `target-validation-receipt/v1`, then finalize provenance and customizations through `ai-context-upgrader`. Generate effective state from explicit owner dispositions and routing evidence. A pending receipt or missing effective state is not action readiness.

## Recovery

Keep the exact extracted incoming package and sealed transaction. Resume with `--package-root . --target-root TARGET --resume TRANSACTION_ID`, or roll back before provenance finalization with `--target-root TARGET --rollback TRANSACTION_ID`. Recovery never changes the sealed plan, source identity or owner decision. Unfinished journal v4 requires prior tooling or owner-directed recovery; v5 does not convert it. A finalized transaction cannot be rolled back.

## Clean Installation

Use the incoming envelope's `INSTALL.md`, select optional providers explicitly and initialize target-owned provenance and customization authority from credible package evidence. Clean installation is distinct from retained-origin upgrade acceptance.

## Scope Boundaries

Source validation, target migration completion and public asset acceptance are separate. Target business code, personal CLI configuration, project-specific policies and unreviewed customizations are never implicitly overwritten.
