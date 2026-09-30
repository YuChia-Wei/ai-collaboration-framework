# REL-v0.4.2 — Context Correctness And Patch-Safe Portability

## Status

Published. Annotated tag `v0.4.2` resolves to
`f474c3b058cb9f89f93929e0732fc1f276422dd9`. GitHub Actions run
`29679273269` published the governed ZIP, tar.gz, and adjacent checksum assets.

## Highlights

- Corrects runtime wrapper identity and routing tables without adding new
  adapter or wrapper contracts.
- Aligns positive Handler, time abstraction, naming, and spec examples with
  existing canonical doctrine.
- Repairs navigation, lifecycle, requirement-outcome, prompt-status, and
  installation guidance while retaining published historical paths.
- Makes required Python-backed gates select a usable interpreter consistently
  and declares the existing Python and dependency expectations.
- Corrects the advisory test-compliance script's repository-root resolution.
- Preserves package, files, and migration schema version `1.0.0`; this patch
  adds no multi-source upgrade contract and removes no published path.

## Compatibility

This release is patch-compatible with the v0.4.1 public contract. The governed
automatic package source remains `v0.3.0`.

Targets already on v0.4.0 should remain there and upgrade directly to v0.5.0
after `PKG-003` publishes the multi-source migration contract. They may instead
choose an explicitly reviewed manual reconciliation, but v0.4.2 does not claim
v0.4.0 as an automatic planner source.

Targets originating at v0.0.1 must first establish governed v0.3.0 provenance
through the published manual v0.1.0 and v0.2.0 reconciliation path.

## Release Validation

The v0.4.2 remediation workflow passed the required Windows Git Bash and hosted
Ubuntu quick gates at 21/21, deterministic package validation, and independent
assessment `ASM-20260719-001`. macOS remains explicitly unverified.

The first tag push targeted a commit that lacked the required release registry;
GitHub Actions run `29678934006` failed closed before publication. The final
annotated tag resolves to
`f474c3b058cb9f89f93929e0732fc1f276422dd9`, and run `29679273269`
successfully published the release.

## Publication Completion

- Release ID: `REL-v0.4.2`
- Annotated tag: `v0.4.2`
- Published commit: `f474c3b058cb9f89f93929e0732fc1f276422dd9`
- GitHub Actions run: `29679273269`
- Release state: stable, non-draft, non-prerelease
- Tag ownership: user-created; automation did not create or select the tag

## Finalization Correction

The post-publication repository finalization was repaired under
`ASM-20260720-001` and workflow
`2026-07-20-v0-4-2-release-finalization-hotfix`. This file is the authored
release-note source; generated automation markers and provenance blocks belong
only in the rendered GitHub Release body.

