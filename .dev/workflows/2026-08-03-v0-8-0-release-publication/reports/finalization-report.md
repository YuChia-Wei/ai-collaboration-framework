# REL-v0.8.0 Finalization Report

## Outcome

REL-v0.8.0 is published. Its governed public body, source registries, GitHub
Project publication projection, and terminal workflow records are reconciled.

## Immutable Evidence

- Annotated tag: `v0.8.0`
- Tag object: `14a763876130cb8adcf876339c573ce0dbb9f330`
- Peeled commit: `97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25`
- Tagged at: `2026-08-03T13:12:55+08:00`
- Publication run: `30786537723` (`success`)
- Release database/node IDs: `363998750` / `RE_kwDOSBe2Hc4Vsi4e`
- Public Release:
  `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/releases/tag/v0.8.0`

The stable Release remains non-draft and non-prerelease. Its creation and
publication timestamps and all four asset ID, node ID, name, size, and digest
tuples are unchanged from the pre-mutation freeze.

## Published Body Reconciliation

- PR #82 passed all five hosted jobs and merged the published registry and
  authored notes to `main` as
  `5ad3f60ea08b8f1416b2d478ae1642a30bf11801`.
- The published renderer then produced SHA-256
  `05520da4dda5ddc1d98ca55741b07f10a2a4edb5ec8d36bfe785eae00e31fd86`
  from integrated source.
- The owner-authorized hosted mutation changed only the Release body.
- Immediate read-back proved exact rendered/live text equality at the same
  SHA-256. Release identity, annotated tag, peeled commit, timestamps,
  publication run, and the four assets were unchanged.
- The earlier hosted finalization mismatch is retained as an expected negative
  gate and is not counted as passed. The post-edit hosted finalization gate
  passed.

## Provider Reconciliation

- GitHub Project #3 field `Published in`
  (`PVTSSF_lAHOAwvEG84Bez7wzhZLZ_w`) retained all eight existing options and
  added source-declared option `v0.8.0` (`12007885`).
- `SKILL-002`, `TOOL-002`, and `WIBIND-001` each read back at `Status: Done`,
  `Target release: v0.8.0`, and `Published in: v0.8.0`.
- Provider receipts record canonical Project item node IDs, including the
  corrected live node ID for `TOOL-002`.
- Project state remains a non-authoritative visibility projection; it did not
  authorize the work, merge, or release.

## Validation

- Candidate packages, exact v0.7.0 upgrade, clean install, independent
  assessment, and the authoritative Git Bash critical gate passed before tag.
- PR #81 and PR #82 each passed all five hosted jobs before merge.
- Tag, publication, downloaded checksum/sidecar, archive parity, and package
  validation passed.
- Post-edit body equality and immutable Release/tag/asset read-back passed.
- Project #3 field-option and exact three-item read-back passed.
- Hosted finalization, version registry, workflow artifact, AI-context,
  release-state, release renderer, backlog-release, and GitHub-provider gates
  passed.
- Environment-blocked and conditional skipped outcomes remain recorded
  separately and are not counted as passed.

## Registry Closure

- `REL-v0.8.0` remains `published` at its immutable release commit.
- `SKILL-002`, `TOOL-002`, and `WIBIND-001` remain the exact Included Work and
  record `published_in: "v0.8.0"`.
- The roadmap records `current_target: unassigned`; no successor release is
  active without a new owner decision.
- Workflow `2026-08-03-v0-8-0-release-publication` and task `REL080-001` are
  completed.
- This completed closure record becomes canonical when integrated through the
  required ready pull request and synchronized-`main` read-back.
