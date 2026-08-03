# v0.8.0 Candidate Package Validation

## Subject

- Candidate source commit: `ec50df072ec59f7e59322345f005450c48be28d7`
- Previous immutable source: annotated `v0.7.0` commit
  `49723a943f744820f4bdb2c22de7930693a7106d`
- Package identity: `ai-context-dotnet-backend-v0.8.0`
- Environment: Windows, Python `3.13.14`, PyYAML `6.0.3`
- Tag and publication: not created

The candidate contains exactly `SKILL-002`, `TOOL-002`, and `WIBIND-001` as
the owner-authorized release set. Proposals #75 and #76 and every other
unallocated backlog item remain outside the release.

## Published Source Verification

The exact public v0.7.0 ZIP and adjacent checksum sidecar were downloaded from
the existing GitHub Release. The ZIP SHA-256 is
`ce817b6635f515eec9fb824d6fea89a01a6273a4a0401682dd65b38202c5adb6`,
and its extracted `metadata/files.yaml` SHA-256 is
`6c4a22889e525509521398439e3cdf9ca362b99f1f52ff434fe691fa4c213b64`.
Both values matched the published evidence before the inventory was used as an
automatic-upgrade source.

## Deterministic Payload

| Evidence | Result |
| --- | --- |
| Payload paths | 625 |
| `ai-context-lifecycle-core` paths | 103 |
| `software-development-core` paths | 491 |
| `dotnet-backend` paths | 29 |
| Optional `repo-backlog` paths | 2 |
| `files.yaml` SHA-256 | `62708640213f7ab3d0cddc19fd15221cf1a11d1b02c6f5512a1b9b3b57d1ffbb` |
| `migration.yaml` SHA-256 | `9fa4c3e357ad24012313c0894748c30fef09b5c5f3a0796f48938c3b561063a9` |
| ZIP SHA-256 | `1e2b2356ae2ebd0fe6938261b1e054e7d467f92829bdcde6946ca245e9028775` |
| tar.gz SHA-256 | `a4b23ada7365b53592a2ae0edc92c68da53b07a1b6187e0a8d3f07e09143a7f0` |
| ZIP/tar package validation | passed for both archives |

The v0.7.0 migration contract contains 67 declared operations: 47 replace, 19
add, and one explicit target-template reconciliation. There are no remove or
rename operations. Source workflow, release, backlog-item, assessment, and
GitHub-provider instances remain outside the downstream payload.

## Actual Target Fixtures

| Fixture | Applied | Intentional skips | Verification |
| --- | ---: | ---: | --- |
| Empty Git target clean install | 623 | 2 `repo-backlog` paths | 0 missing paths; 0 payload SHA mismatches |
| Initialized exact v0.7.0 target upgrade | 64 | 1 `repo-backlog` operation; 2 reviewed reconciliations | target validator passed; 0 applied SHA mismatches |

The upgrade selection came from the target's validated provenance, which was
created by the published v0.7.0 `initialize_context()` API using the package
metadata source identity and effective selection from its apply receipt. An
uninitialized target was first rejected with
`component-aware upgrade requires .dev/ai-context/provenance.yaml`, proving the
gate fails closed rather than accepting a synthetic authority.

The two acknowledged reconciliation IDs were:

- `migration-0026`: preserve `.ai/scripts/check-all.sh`. Its bytes exactly
  match v0.7.0; Windows cannot retain the manifest's Unix executable mode.
- `migration-0067`: preserve the target-template
  `.github/pull_request_template.md` exactly as required by the migration.

Acknowledgement preserved both v0.7.0 byte sequences; it did not authorize an
overwrite. Both real receipts remain `pending-validation`, record
`provenance_updated: false`, and leave target-owned provenance finalization to
`ai-context-init` or `ai-context-upgrader`. That later downstream step is not
counted as a candidate pass.

## Test Matrices

| Check | Observed result |
| --- | --- |
| Packaging matrix | 28 passed; 1 retained downstream integration skipped because `AI_CONTEXT_DOWNSTREAM_REPO` was not supplied |
| Package apply matrix | 25 passed; 1 Windows symlink-capability skip |
| Release-state matrix | 24/24 passed |
| Release-note renderer | 8/8 passed |
| Version governance | 19/19 passed |
| Profile projection | 3/3 passed |
| Backlog release contract | 6/6 passed |
| GitHub provider contract | 19/19 passed |
| Workflow provider contract | 6/6 passed |
| Prepare-release contract | 10/10 passed |

Neither conditional skip is counted as passed. The complete packaging rerun
executed all 29 cases in 501.238 seconds after the release-transition assertion
was corrected to prove that the synthetic CP-2 fixture leaves source release
artifacts unchanged.

## Corrected Attempts Not Counted As Passes

- A first clean-install command omitted the envelope's `payload/` segment and
  did not execute package logic.
- The first upgrade attempt correctly rejected an uninitialized target.
- A later apply correctly rejected the prior v0.7.0 pending receipt until the
  v0.7.0 fixture initialization was completed and committed.
- Sandbox-only Python fixture runs hit Windows temporary-directory ACL errors;
  the identical matrices were rerun once outside the sandbox.
- The first final archive-validator command used an unsupported `--archive`
  option; the positional invocation then validated both archives.

None of these attempts is represented as a passed gate.

## Independent Verification

Independent read-only candidate verification is pending. Hosted pull-request
checks, merge, current-main pre-tag validation, owner-created tag, publication,
and terminal registry finalization also remain unperformed.
