# Migrate To v0.17.0

## Supported Sources

The retained direct sources are **v0.6.0**, **v0.9.0** and **v0.16.0**. Every route applies one incoming v0.17.0 archive, with no intermediate release installation. Source-specific manifests and owner decisions remain distinct. Other installed versions require reviewed reconciliation; do not reinterpret them as one of these sources.

## Before You Start

1. Preserve a clean target commit, installed-version provenance, semantic customization ledger, effective-rule state and any unfinished transaction evidence. Resolve missing or conflicting authority before applying files.
2. Verify the incoming public archive and checksum against its immutable release identity. Obtain the original installed package's `metadata/files.yaml` from its published envelope; do not reconstruct that manifest from a current checkout.
3. Extract the incoming package outside the target and install its declared Python requirements. Select optional components and providers from target-owned evidence. From the extracted envelope, resolve the source-only support matrix with `python payload/.ai/scripts/plan-ai-context-upgrade.py --matrix SUPPORT_MATRIX --origin INSTALLED_VERSION --target v0.17.0` and require a direct route.

## Migration Steps

Run the incoming package planner from the extracted envelope. Each source has its own entry point:

```text
python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root TARGET --previous-version v0.6.0 --previous-files V060_FILES --plan-output PLAN --remediation-packet-output PACKET
python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root TARGET --previous-version v0.9.0 --previous-files V090_FILES --plan-output PLAN --remediation-packet-output PACKET
python payload/.ai/scripts/plan-ai-context-package-apply.py --package-root . --target-root TARGET --previous-version v0.16.0 --previous-files V0160_FILES --plan-output PLAN --remediation-packet-output PACKET
```

Choose only the command matching actual target provenance. `TARGET`, the original manifest, `PLAN` and `PACKET` are explicit local paths. Planning is read-only with respect to target-managed files; its proposed changes are not owner approval.

Review the plan and packet, then record an independent owner decision. All sources must reconcile selected components/providers, target commands and ignore policy, managed removals, semantic customizations, effective rules, and modified wrapper or AGENTS content. Remove a previous managed file only when original manifest evidence proves the applicable ownership and accepted disposition.

| Origin | Additional reconciliation focus |
| --- | --- |
| v0.6.0 | Migrate older provenance layout and identity, preserve target-specific rules through component/provider ownership changes, and reconcile historical skill references and commit-policy adoption. |
| v0.9.0 | Preserve recorded selections and target customizations while reconciling newer semantic governance, retired skill references, commit-policy adoption and effective-rule state. |
| v0.16.0 | Reconcile the review/design extension split, artifact-first authoring, implementation handoffs, test traceability and the task-led AGENTS seed. |

The common code-reviewer entry remains `references/review-routing.yaml`. Consumers that directly expected the fourteen .NET routes must now select `.ai/assets/tech-stacks/dotnet-backend/review/review-routing.yaml`. Preserve rule IDs and customized target rules when relocating consumers or retiring an unchanged old fixture path. Unknown technology receives only the selected common review coverage, not an assumed .NET review.

Architecture and BDD review modes assess a selected immutable artifact set. Their findings do not authorize implementation. Requirement/spec/problem-frame selection follows the requested output; implementation scope follows the operation and semantic boundary rather than file count. Preserve target-specific stage and approval requirements during reconciliation.

Keep historical assessment identifiers unchanged. For new records use `ASM-YYYYMMDD-HH-xxx`; check existing identifiers and choose another three-character suffix on a collision. The suffix is a local disambiguator, not a security or globally unique identity.

The public AGENTS template is an initialization seed. Upgrading the framework does not authorize wholesale replacement of an initialized target's root guide. Keep the target's repository-specific facts and apply accepted navigation or rule changes through the owning upgrade process.

After owner review, repeat the selected planner command with `--apply --remediation-decision DECISION`. Run the target-owned validation profile and retain its exact `target-validation-receipt/v1`. Finalize target provenance and customizations through `ai-context-upgrader` only after target validation, semantic reconciliation and required independent review pass. Regenerate effective-rule state from accepted selections and routing evidence; missing state or a pending receipt is not action readiness.

## Recovery

Keep the exact incoming envelope and sealed transaction. Resume with `--package-root . --target-root TARGET --resume TRANSACTION_ID`, or roll back before provenance finalization with `--target-root TARGET --rollback TRANSACTION_ID`. Recovery preserves the plan, original identities and owner decision. An unfinished journal v4 requires its prior tooling or explicit owner-directed recovery; v5 does not convert it. A finalized transaction cannot be rolled back.

## Clean Installation

Follow the incoming envelope's `INSTALL.md`, explicitly select optional components and providers, then initialize target provenance and customization authority from credible package evidence. Clean installation is a separate acceptance from retained-origin upgrades. Running the optional .NET teaching projects requires the target-selected .NET prerequisites; ordinary framework validation remains SDK-free.

## Scope Boundaries

- Preserve product source, tests, project policies, personal runtime configuration and unreviewed customizations.
- Source candidate validation, public asset identity, actual target application and downstream completion are distinct evidence.
- No route, version label, generated packet or successful framework test grants permission to overwrite target-owned truth.
