# AI Context Release Index

This index is the discovery view for framework releases. Each version's `release.yaml` is its lifecycle source of truth.

## Create A Candidate

Instantiate, rather than copy, the canonical
[`release-publication`](../../.ai/assets/skills/ai-context-governance/templates/release-publication/)
templates. Then follow the exact commands in
`.dev/releases/<version>/release-phase-checks.yaml` and the
[publication runbook](../operations/runbooks/AI-CONTEXT-RELEASE-PUBLICATION-RUNBOOK.MD).
Historical `v*` directories below are records, never templates.

## Candidate Releases

_None._

## Planned Phase Contracts

| Release ID | Version | Status | Compatibility | Phase Contract |
| --- | --- | --- | --- | --- |
_None._

## Published Releases

| Release ID | Version | Published commit | Compatibility | Notes | Migration |
| --- | --- | --- | --- | --- | --- |
| [`REL-v0.7.0`](v0.7.0/release.yaml) | `v0.7.0` | `49723a943f744820f4bdb2c22de7930693a7106d` | non-breaking; schema 2 package/files; schema 3 migration; exact automatic source v0.6.0 | [notes](v0.7.0/release-notes.md) | [guide](v0.7.0/migration-guide.md) |
| [`REL-v0.6.0`](v0.6.0/release.yaml) | `v0.6.0` | `8b98b5f917513f2d143f42a322050a1162bb63f9` | schema 2 package/files; schema 3 migration; exact automatic source v0.5.0 | [notes](v0.6.0/release-notes.md) | [guide](v0.6.0/migration-guide.md) |
| [`REL-v0.5.0`](v0.5.0/release.yaml) | `v0.5.0` | `1477181f0b43fa7ee82fcd482141758ac9e22eb6` | migration schema 2.0; exact automatic sources v0.3.0, v0.4.0, v0.4.1, and v0.4.2 | [notes](v0.5.0/release-notes.md) | [guide](v0.5.0/migration-guide.md) |
| [`REL-v0.4.2`](v0.4.2/release.yaml) | `v0.4.2` | `f474c3b058cb9f89f93929e0732fc1f276422dd9` | governed package patch; automatic source v0.3.0; v0.4.0 consumers should wait for v0.5.0 | [notes](v0.4.2/release-notes.md) | [guide](v0.4.2/migration-guide.md) |
| [`REL-v0.4.1`](v0.4.1/release.yaml) | `v0.4.1` | `3daefcef1318c12d03c189f232993ccbe04665f2` | governed package patch; automatic source v0.3.0; v0.4.0 consumers should wait for v0.5.0 | [notes](v0.4.1/release-notes.md) | [guide](v0.4.1/migration-guide.md) |
| [`REL-v0.4.0`](v0.4.0/release.yaml) | `v0.4.0` | `5af1db672928f9d51f55fee04183ad27b79fb9f8` | governed package; pre-1.0 breaking changes; v0.3.0 reconciliation required | [notes](v0.4.0/release-notes.md) | [guide](v0.4.0/migration-guide.md) |
| [`REL-v0.3.0`](v0.3.0/release.yaml) | `v0.3.0` | `1e782909b7753b2889014516595d72f703a260f3` | governed package; pre-1.0 breaking changes documented | [notes](v0.3.0/release-notes.md) | [guide](v0.3.0/migration-guide.md) |
| [`REL-v0.2.0`](v0.2.0/release.yaml) | `v0.2.0` | `9abc75b543ae201865c1e119d29fac2bcd2f4542` | pre-1.0 breaking changes documented | [notes](v0.2.0/release-notes.md) | [guide](v0.2.0/migration-guide.md) |
| [`REL-v0.1.0`](v0.1.0/release.yaml) | `v0.1.0` | `69c285077708dfb96ee49bb39258aec83eb7f1a9` | historical baseline | [notes](v0.1.0/release-notes.md) | [guide](v0.1.0/migration-guide.md) |
| [`REL-v0.0.1`](v0.0.1/release.yaml) | `v0.0.1` | `ac2e2937b5209ece93e104c4a389a15e164c0d1b` | historical source snapshot; manual reconciliation only | [notes](v0.0.1/release-notes.md) | [guide](v0.0.1/migration-guide.md) |

## Related Governance

- [Version policy](../standards/AI-CONTEXT-VERSION-POLICY.md)
- [Release publication runbook](../operations/runbooks/AI-CONTEXT-RELEASE-PUBLICATION-RUNBOOK.MD)
- [Version-governance workflow](../workflows/2026-07-14-ai-context-version-governance/workflow.yaml)
