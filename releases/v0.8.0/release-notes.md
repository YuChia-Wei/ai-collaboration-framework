# REL-v0.8.0 — Canonical Skill Ownership, Python Readiness, And Work Authorization

## Status

Published.

## Highlights

- Co-locates single-owner Python implementations and contract tests with their
  canonical skills while preserving published compatibility entrypoints.
- Adds consistent fail-closed Python 3.11+ and exact dependency diagnostics to
  all 25 governed production CLIs, including portable POSIX and PowerShell
  launchers plus human-readable and JSON outcomes.
- Adds provider-neutral work-item binding and independently selectable merge-
  gate policy. Explicit owner approval remains required; provider state alone
  never authorizes execution, and downstream teams retain their own selection.

## Compatibility

v0.8.0 is a backward-compatible pre-1.0 minor release with exact
automatic upgrade support from the published v0.7.0 package. Existing Python
command paths and thin compatibility entrypoints remain supported, and the
current payload comparison removes no published path.

Python 3.11 or newer remains required. Commands that require YAML use the exact
PyYAML version declared by the repository or extracted package. Prerequisite
diagnostics never install dependencies, create an environment, access the
network, replace the selected runtime, or mutate a target.

Existing target-owned work-management and validation choices remain target-
owned. New initialization templates leave work-item binding and merge-gate
selection unresolved until the target team explicitly chooses `required`,
`optional`, or `disabled`.

## Known Limitations

- The retained external downstream integration requires an explicitly supplied
  repository; its prior conditional skip is not counted as passed.
- This Windows host cannot create the package-apply symlink fixture without an
  unavailable capability; that conditional skip is not counted as passed.
- Proposal #75 aggregate/downstream selection architecture and Proposal #76
  generalized environment readiness are not part of this release.
- Published shell compatibility-entrypoint relocation remains deferred pending
  separate downstream lifecycle evidence.

## Release Validation

The candidate archives, clean installation, exact initialized v0.7.0 upgrade,
release contracts, package matrices, and independent candidate verification
passed. The packaging matrix recorded 28 passed tests and one retained-
downstream conditional skip; the package-apply matrix recorded 25 passed tests
and one Windows symlink-capability skip. Neither skip is counted as passed.
Both real apply receipts intentionally leave downstream provenance finalization
to `ai-context-init` or `ai-context-upgrader`; that target-owned step is not
counted as a candidate pass.

The complete repository critical gate also passed. PR #81 passed all five
hosted jobs and merged the validated candidate to `main`. Merged-main provider
read-back and the current-main pre-tag gate then passed. The owner-created
annotated tag, tag-phase gate, hosted publication, downloaded checksum
sidecars, and exact ZIP/tar payload-parity validation also passed.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Published from immutable annotated tag `v0.8.0`, peeled commit
`97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25`, through successful hosted run
`30786537723`. The stable GitHub Release exposes the governed ZIP, tar.gz, and
both checksum sidecars.
