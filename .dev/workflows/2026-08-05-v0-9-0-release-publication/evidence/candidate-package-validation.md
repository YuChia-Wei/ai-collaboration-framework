# v0.9.0 Candidate Package Validation

## Subject

- Candidate source commit: `25ae56647a93668c800409f4306a9485b78cce3c`
- Previous immutable source: published `v0.8.0` package
- Package identity: `ai-context-dotnet-backend-v0.9.0`
- Environment: Windows host Python `3.13.14` and PowerShell; WSL was not used
- Tag and publication: not created

The candidate contains exactly `GOV-004`, `PKG-005`, `GOV-006`, `CTX-004`,
`CTX-005`, `PKG-006`, `VAL-003`, and `SAG-002`. Issue #128 is disclosed as
an online-only packaged correction and is not a ninth canonical Included Work
item.

## Published Source Verification

The public v0.8.0 ZIP and adjacent checksum sidecar were downloaded through
`gh release download` outside the sandbox. The archive SHA-256
`94fe4ff17222423f2fa521343e02b8a7e4709c566ea22e264f5b1b1ac3a4701c`
matched its published sidecar before its exact `metadata/files.yaml` was used
as the sole v0.9.0 migration source.

## Deterministic Payload

| Evidence | Result |
| --- | --- |
| Payload paths | 652 |
| `ai-context-lifecycle-core` paths | 110 |
| `software-development-core` paths | 335 |
| `dotnet-backend` paths | 205 |
| Optional `repo-backlog` paths | 2 |
| `files.yaml` SHA-256 | `c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7` |
| `migration.yaml` SHA-256 | `ca0ec6f7d8694549a3cf6cfa6ef22bcfe7da88f7d7900b2c24e9f58c8f00d27a` |
| ZIP SHA-256 | `937ecec624577b2bc7c47ffe29b4c7ad91d17f27a86fdb9b9cf8c236fe3a7d44` |
| tar.gz SHA-256 | `cd233ab3272ccf25c9d26c34a1c0a1594d4b1ad9a0ff2236f95e29384d639c80` |
| Two-build determinism | ZIP, tar.gz, and both sidecar file digests matched |
| ZIP/tar package validation | passed for both archives |

## Actual Target Fixtures

| Fixture | Applied | Intentional skips | Verification |
| --- | ---: | ---: | --- |
| Clean Git target | 649 | one target-template reconciliation; optional `repo-backlog` excluded by selection | 636 required managed paths; 0 missing; 0 SHA mismatches; receipt and target validator passed |
| Initialized exact v0.8.0 target | 360 | `migration-0345` preserved the target-owned PR template | 636 required managed paths; 0 missing; 0 SHA mismatches; receipt and target validator passed |

The exact v0.8.0 upgrade dry-run contained 361 operations: 123 replace, 60
add, 144 rename, 33 remove, and one reconcile. The sole acknowledged item was
`migration-0345` for `.github/pull_request_template.md`. Acknowledgement
preserved the target-owned template and did not authorize overwrite or
deletion.

Both target validators reported the absent target-effective rule state as
`unresolved`; that state was not misreported as passed or failed. Package
installation and required-path integrity passed independently of later
target-owned effective-rule adoption.

## Corrected Attempts Not Counted As Passes

- A first metadata lookup omitted the package envelope directory and stopped
  before package logic.
- A first PowerShell digest loop had a parser error and executed no validation.
- The initial pre-fix exact upgrade acknowledged two Windows executable-mode
  reconciliations, then correctly failed target validation because the
  preserved v0.8.0 script bytes did not satisfy the v0.9.0 receipt hashes.
- The package planner was corrected only for byte-identical `0755` to `0644`
  loss when target Git explicitly reports `core.filemode=false`; all other
  hash or mode drift still reconciles.
- The first focused test run inside the sandbox could not create Windows TEMP
  fixtures and was not counted. The identical outside-sandbox matrix completed
  29 passed cases with one Windows symlink-privilege skip.
- Several sub-agent calls reached their per-call wait limit. Live processes
  were read back and allowed to finish; no apply was rerun over partial state.

## Focused Validation

- `python .ai/scripts/tests/test_ai_context_package_apply.py -v`: 29 passed,
  one Windows symlink-privilege skip.
- `python .ai/scripts/validate-ai-context-package.py <zip> <tar.gz>`: passed.
- Clean-install receipt validation and installed target validation: passed.
- Exact v0.8.0 upgrade receipt validation and installed target validation:
  passed after the filemode fix.

Independent post-remediation assessment and hosted pull-request validation
remain separate gates.
