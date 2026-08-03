# REL-v0.8.0 — Canonical Skill Ownership, Python Readiness, And Work Authorization

## Status

Planned governed candidate. No tag, published package, or GitHub Release exists.

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

v0.8.0 is planned as a backward-compatible pre-1.0 minor release with exact
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
- Proposal #75 aggregate/downstream selection architecture and Proposal #76
  generalized environment readiness are not part of this release.
- Published shell compatibility-entrypoint relocation remains deferred pending
  separate downstream lifecycle evidence.

## Release Validation

Candidate package, archive parity, clean installation, exact v0.7.0 upgrade,
independent verification, repository critical gates, pull-request integration,
and current-main pre-tag validation remain pending in the owning workflow.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Pending. The repository owner creates the immutable annotated tag only after
the merged current-main pre-tag gate passes.
