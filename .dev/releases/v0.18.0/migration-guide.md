# Migrate To v0.18.0

## Supported Sources

The required direct origins are v0.6.0, v0.9.0 and v0.17.0. Preparation is active;
do not treat the planned release record as an admitted or published package.
Each origin must select its own exact previous `metadata/files.yaml` and use the
incoming package's planner. No intermediate package may replace a required
direct-origin acceptance case.

## Before You Start

1. Preserve target provenance, effective rules and semantic customizations.
2. Start from a clean target checkout and verify the incoming archive checksum,
   package identity and exact prior-version manifest.
3. Review target-owned root instructions, private role changes, selected
   messaging rules and target validation commands. Do not overwrite them with
   source-repository facts.

## Migration Steps

1. For each supported origin, invoke the incoming
   `plan-ai-context-package-apply.py` with `--target-root`, `--package-root`,
   `--previous-version v0.6.0`, `v0.9.0` or `v0.17.0`, and the matching
   `--previous-files`. Begin without `--apply` and retain the resulting plan.
2. Reconcile private roles by stable role identifier. Their destination is
   `.ai/assets/skills/<owner>/roles/<role-id>/`: code-reviewer owns its four
   review roles, slice-implementer owns its twelve implementation/test roles,
   and problem-frame-author owns its framing role. Shared roles stay under
   `.ai/assets/sub-agent-role-prompts/`. Preserve customized source content until
   destination reconciliation is complete; update active references together.
3. Reconcile generated runtime entries through their canonical inputs. Do not
   maintain an independent manual execution rule in Codex or Claude wrappers.
4. Review transaction semantics against target topology. Preserve one completion
   owner, native framework enrollment, transport versus business idempotency,
   and target-selected operational policy. The guidance does not authorize
   infrastructure replacement or business-transaction expansion.
5. Bind the exact candidate provenance and customization documents to the
   approved remediation decision before applying. Rebuild effective-rule state
   and selected packets from reconciled authority.
6. Run the target-owned validation profile, retain its actual receipt and obtain
   independent post-upgrade verification before finalizing provenance. An
   interrupted transaction uses its exact `--resume` or `--rollback` identity;
   it is never reported as a completed upgrade.

## Clean Installation

Use the selected package's `INSTALL.md` and `ai-context-init`. Reusable root
entries are seeds; repository identity and commands require target evidence.

## Scope Boundaries

- Routine bounded execution does not weaken release, adoption, authorization,
  transaction durability or actual-execution evidence gates.
- A private implementation helper may remain local only within the accepted
  responsibility, behavior, dependency and lifetime boundaries.
- Target-specific schemas, endpoints, message retention, retry policies,
  package versions and operations remain target-owned.
