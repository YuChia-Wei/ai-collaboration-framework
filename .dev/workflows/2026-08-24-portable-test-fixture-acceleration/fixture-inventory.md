# PERF-001 Fixture And Benchmark Inventory

## Subject And Evidence Boundary

- Subject commit: `4be33ff90de061dc1db221f60e57ff6130cab54a`
- Inventory date: `2026-08-24T22:40:04+08:00`
- Work item: GitHub Issue #246
- Discovery accelerator: Codebase Memory MCP fast index `ai-collaboration-framework-bc11`.
- Index limitation: `.ai/scripts`, `.ai/assets`, and other reported roots were excluded; no graph absence claim was accepted.
- Direct verification: `rg` over tracked Python/shell sources and direct reads of every selected or retained fixture.

## Current Surface

- `79` tracked Python test files exist under the source test roots.
- Highest temporary-directory counts: release-state `33`, release-notes renderer `19`, version-governance `15`, semantic-customization `9`, workflow-backlog and dependency-version `6` each.
- Highest Git/subprocess call-site counts: packaging `89`, package-apply `41`, validation-evidence `40`, immutable-history `29`, effective-rules `17`.

These static counts are inventory signals, not runtime duration or executed-child counts.

## Tracked Classification Decisions

| Test file | Classification | Evidence and route |
| --- | --- | --- |
| `.ai/scripts/tests/test_ai_context_release_state.py` | `ephemeral-fixture-io` | Synthetic release records and validator inputs; no flush, recovery, symlink/reparse, permission, or device-boundary assertions. Migrate its disposable roots. |
| `.ai/scripts/tests/test_release_notes_renderer.py` | `ephemeral-fixture-io` | Synthetic Git/release-note inputs and subprocesses; no storage/platform semantic assertions. Migrate its disposable roots. |
| `.ai/scripts/tests/test_ai_context_version_governance.py` | `ephemeral-fixture-io` | Synthetic version/provenance files and isolated Git state; no storage/platform semantic assertions. Migrate its disposable roots. |
| `.ai/scripts/tests/test_ai_context_package_apply.py` | mixed `durability-storage-semantics` and `platform-filesystem-semantics` | Covers journal/crash/resume/rollback, durable unlink, atomic replacement, readonly behavior, symlink/reparse boundaries, Windows volume behavior, and NTFS-sensitive behavior. Never route this file through acceleration. |
| `.ai/scripts/tests/test_ai_context_packaging.py` | unclassified mixed surface | Workspace-owned root preserves Windows ACL/path-length behavior; file also covers symlink, permissions, archive metadata, and Git packaging. Retain `.tmp/p`. |
| `.ai/scripts/tests/test_fail_closed_validation.py` | unclassified mixed surface | Exercises executable modes, file permissions, process supervision, profiles, and fail-closed evidence. Retain current behavior. |

All other tests remain unclassified. No path name, drive letter, device name, or ambient host capability infers classification.

## Selected Benchmark Profile

The reproducible `ephemeral-fixture-io` profile runs the same ordered list in default and accelerated modes:

1. `.ai/scripts/tests/test_ai_context_release_state.py`
2. `.ai/scripts/tests/test_ai_context_version_governance.py`
3. `.ai/scripts/tests/test_release_notes_renderer.py`

It records platform class, classification, test/fixture counts, cold/warm condition, per-run and median wall time, fixture-creation time when available, and nested-subprocess metrics as `unavailable` when not reliably instrumented. It excludes absolute roots, user names, hostnames, and drive letters. Comparative evidence requires one host, commit, profile, condition, and at least three runs per route; cross-host seconds are never a correctness gate.

## Deferred Inventory

- Package-apply fixture splitting is deferred because one shared fixture owns disposable and durability/platform semantics.
- Packaging, fail-closed, validation-evidence, immutable-history, and effective-rule suites retain current routing until per-fixture disposability is proven.
- Post-#245 synchronization must repeat overlap discovery for source/workflow validation files.
