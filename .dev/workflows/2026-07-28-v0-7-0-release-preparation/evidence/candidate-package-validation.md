# v0.7.0 Candidate Package Validation

## Subject

- Candidate source commit: `b474730d453c27f2b5338f5bbe0b5efd5e9b0628`
- Previous immutable source: annotated `v0.6.0` commit
  `8b98b5f917513f2d143f42a322050a1162bb63f9`
- Package identity: `ai-context-dotnet-backend-v0.7.0`
- Tag and publication: not created

## Compatibility Repair

The first independent candidate audit failed because package metadata used
hard-coded `breaking_changes: true` and `minimum_governed_source: v0.1.0`.
Commit `b474730` removed those defaults: the builder now reads the version-owned
release record and fails closed when its automatic sources differ from the
actual migration inputs.

The rebuilt candidate records:

- `breaking_changes: false`
- `minimum_governed_source: v0.6.0`
- `automatic_upgrade_sources: [v0.6.0]`

## Deterministic Payload

| Evidence | Result |
| --- | --- |
| Payload paths | 606 |
| `files.yaml` SHA-256 | `6c4a22889e525509521398439e3cdf9ca362b99f1f52ff434fe691fa4c213b64` |
| `migration.yaml` SHA-256 | `9007e03abea33a9756c0fd407eab1235d0467f20942aa5f38054a617d7f04f70` |
| Source workflow, assessment, backlog-item, roadmap, and release-history instances | 0 |
| ZIP/tar member and mode parity | passed |

The manifest projects the three target policy paths from shared portable
governance assets. It does not project this repository's GitHub provider,
pull-request transport, or `main` branch choices as target defaults.

## Focused Tests

| Check | Observed result |
| --- | --- |
| Packaging matrix | 26 passed; 1 environment-gated skip not counted as passed |
| Package apply matrix | 23 passed; 1 Windows symlink-capability skip not counted as passed |
| Profile projection contract | 3/3 passed |
| Compatibility positive/negative fixtures | 2/2 passed |
| Corrected candidate ZIP/tar validation | passed for both archives |

The first archive-validator invocation used unsupported option names and the
first metadata read raced extraction; both were command/environment errors and
were rerun successfully. A reused v0.6.0 extraction was rejected after an
import-created `__pycache__` changed checksum coverage; the fixture re-extracted
the immutable ZIP and then passed. None of these failed attempts is counted as
a passed check.

## Actual Target Fixtures

| Fixture | Applied | Intentional provider skip | Reconciliation |
| --- | ---: | ---: | ---: |
| Empty Git target clean install | 604 operations | 2 `repo-backlog` operations | 0 |
| Initialized exact v0.6.0 target upgrade | 25 operations | 1 `repo-backlog` operation | 0 |

Both receipts record `repo-backlog.enabled: false` and
`provenance_updated: false`. The `pending-validation` receipt is the package
tool's intended safe-apply result. Downstream `ai-context-init` or
`ai-context-upgrader` validation and provenance finalization require credible
published source evidence and were not performed or counted as passed.

## Independent Verification

`ASM-20260728-001` records the read-only auditor sequence: the first audit
failed the compatibility mismatch; the remediation audit confirmed the fix;
the final acceptance review passed the PKG-004 candidate package-fixture gate.
Tagging, publication, and downstream provenance finalization remain separate.
