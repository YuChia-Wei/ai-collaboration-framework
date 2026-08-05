# v0.9.0 Candidate Package Validation

## Subject

- Candidate source commit: `d3236e6dfe54c56a5b9d040e95071569ccc493a3`
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
| ZIP SHA-256 | `db314ef5f1f0428f6e0907a7877c0050575c9f58f2f3a54528528ff6f0d4195f` |
| tar.gz SHA-256 | `d1c7e2dd1349fa8c62573ef62da01c1a196a2d2dbf8c34c1e8cfc6a779db3208` |
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

## Message-Rewrite Equivalence And Owner Waiver

The unpushed branch history was rewritten only to repair commit subjects and
AI trailers. The original package subject `25ae56647a93668c800409f4306a9485b78cce3c`
and rewritten subject `d3236e6dfe54c56a5b9d040e95071569ccc493a3`
have the identical Git tree
`863f50ae4679b3d908299435168d118414284262`. Because the package envelope
records the source commit, the rewritten candidate was still built twice from
`d3236e6`; its new archives and sidecars were deterministic and ZIP/tar parity
validation passed. The payload inventory and migration contract remained
byte-identical at the `files.yaml` and `migration.yaml` hashes recorded above.

On 2026-08-06 the owner explicitly waived a second clean-install and exact
v0.8.0-upgrade fixture run after this message-only rewrite because the payload
tree, inventory, and migration bytes were identical. The fixture results in
this report were executed against the equal-tree `25ae566` package and are
inherited by equivalence; they were not rerun against the rewritten envelope.
The new archive construction, checksums, determinism, and archive validator
were rerun and are the current candidate evidence. No stale pre-rewrite
archive digest is treated as current.

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
- A redundant post-rewrite fixture rerun was started, then stopped on explicit
  owner direction before its partial results were used. The equivalence and
  waiver above define the accepted scope instead.

## Focused Validation

- `python .ai/scripts/tests/test_ai_context_package_apply.py -v`: 29 passed,
  one Windows symlink-privilege skip.
- `python .ai/scripts/validate-ai-context-package.py <zip> <tar.gz>`: passed.
- Clean-install receipt validation and installed target validation: passed.
- Exact v0.8.0 upgrade receipt validation and installed target validation:
  passed after the filemode fix.

Independent post-remediation assessment and hosted pull-request validation
remain separate gates.
