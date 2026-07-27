# PKG-004 Payload And Fixture Proof

## Subject

- Source commit: `78fbba8f9c889880b7baceed8d42acf4b5508c76`
- Prior immutable source: annotated tag `v0.6.0`, commit
  `8b98b5f917513f2d143f42a322050a1162bb63f9`
- Candidate identity used only for deterministic package proof:
  `ai-context-dotnet-backend-v0.7.0`
- Formal `.dev/releases/v0.7.0` candidate, tag, hosted release, and publication:
  not created.

## Payload Manifest

- Full v0.7.0 files manifest:
  [`v070-payload-files.yaml`](v070-payload-files.yaml)
- v0.7.0 files manifest SHA-256:
  `6c4a22889e525509521398439e3cdf9ca362b99f1f52ff434fe691fa4c213b64`
- v0.7.0 payload paths: `606`
- Full v0.6.0-to-v0.7.0 migration manifest:
  [`v060-to-v070-migration.yaml`](v060-to-v070-migration.yaml)
- Migration manifest SHA-256:
  `9007e03abea33a9756c0fd407eab1235d0467f20942aa5f38054a617d7f04f70`

The generated archives validated with exact ZIP/tar payload and mode parity:

| Artifact | SHA-256 |
| --- | --- |
| `ai-context-dotnet-backend-v0.7.0.zip` | `24fd0504a8a67bf1b100ccda7b5d05a665d364a73f23e220873f7c582ea6af55` |
| `ai-context-dotnet-backend-v0.7.0.tar.gz` | `838a99a38cbd8d3d1da482417c68fbfe6003081fcb66837169c2aa4c4b428d72` |

## v0.6.0 To v0.7.0 Payload Diff

| Measure | Result |
| --- | ---: |
| v0.6.0 paths | 601 |
| v0.7.0 paths | 606 |
| Added | 5 |
| Removed | 0 |
| Changed | 21 |

Added paths:

- `.ai/assets/shared/governance/GIT-COMMIT-POLICY.md`
- `.ai/assets/shared/governance/TEAM-GIT-FLOW-RULES.MD`
- `.ai/assets/shared/governance/WORKFLOW-GATE-POLICY.md`
- `.ai/assets/shared/governance/portable-policy-manifest.yaml`
- `.dev/guides/ai-collaboration-guides/AI-EXECUTION-PROVENANCE-AND-ATTRIBUTION-GUIDE.md`

The 21 changed paths are the expected provenance validators/templates/guides,
portable target policy destinations, backlog capability README, and their
governance policies. The generated migration manifest owns their exact add and
replace operations and prior hashes; no path was removed.

## Source-History Exclusion Proof

The manifest contains no source instances matching any of these sets:

- `.dev/workflows/20*/**`
- `.dev/assessments/ASM-*/**`
- `.dev/backlog/items/**`
- `.dev/backlog/ROADMAP.md`
- `.dev/releases/**`

The target catalog paths `.dev/workflows/INDEX.MD`,
`.dev/assessments/INDEX.MD`, and `.dev/backlog/INDEX.MD` are empty
`target-template` seeds sourced from
`.ai/assets/skills/ai-context-init/templates/public-catalogs/`; they are not
the source repository's workflow, assessment, or backlog history. The optional
`.dev/backlog/README.MD` capability belongs to `repo-backlog`, defaults off,
and was absent after clean install and upgrade with the default selection.

## Portable Policy Projection Proof

| Target path | Manifest source path | Component |
| --- | --- | --- |
| `.dev/standards/WORKFLOW-GATE-POLICY.md` | `.ai/assets/shared/governance/WORKFLOW-GATE-POLICY.md` | `software-development-core` |
| `.dev/TEAM-GIT-FLOW-RULES.MD` | `.ai/assets/shared/governance/TEAM-GIT-FLOW-RULES.MD` | `software-development-core` |
| `.dev/standards/GIT-COMMIT-POLICY.md` | `.ai/assets/shared/governance/GIT-COMMIT-POLICY.md` | `software-development-core` |

The projected target bytes contain no source-repository provider selection,
provider resource rule, hard-coded `main` integration rule, or pull-request
transport requirement. The original source files remain unchanged in this
repository and are explicitly classified `source-only` by the profile.

## Clean Install And Upgrade Evidence

| Fixture | Result | Provider / policy evidence |
| --- | --- | --- |
| Full package matrix | 25 passed, 1 environment-gated test skipped and not counted as passed | Deterministic archives, clean install, exact upgrades, payload parity, source exclusions. |
| Profile projection contract | 3 passed | Current active projection surface remained coherent. |
| Package apply matrix | 23 passed, 1 Windows symlink-capability test skipped and not counted as passed | Default provider selection, target templates, local-change reconciliation, reserved paths, transactions. |
| Actual v0.7.0 clean install into an empty Git target | passed | Portable workflow policy installed; `repo-backlog` remained absent. |
| Actual initialized v0.6.0 target to v0.7.0 | passed | Exact v0.6.0 manifest selected; portable policy replaced the prior managed bytes; `repo-backlog` remained absent. |

The actual upgrade correctly failed closed before the v0.6.0 target had
component-aware provenance and again while its clean-install pending receipt
remained active. After the fixture reproduced the `ai-context-init` boundary by
recording explicit `repo-backlog: false` provenance and finalizing that pending
receipt, the exact upgrade plan and apply passed. Neither blocked attempt is
reported as passed.

## Future Release Notes And Migration Guide

The future v0.7.0 authored material must explain that:

1. `GOV-002`, `GOV-003`, and `PKG-004` are generated under `Included Work` by
   the release renderer and publication remains a separate fact;
2. target work-management state is provider-neutral and works without a
   tracker;
3. the three canonical target policy paths receive provider-neutral framework
   bytes, while existing target modifications enter reconciliation rather than
   being silently overwritten; and
4. existing target provider, integration branch, review, and merge selections
   remain target-owned. No provider adoption is performed by the upgrade.
