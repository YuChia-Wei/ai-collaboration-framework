# REL-v0.2.0 — Assessments And Remediation Contracts

## Status

Published retrospectively at tag `v0.2.0`, commit `9abc75b543ae201865c1e119d29fac2bcd2f4542`.

This record was created after the tag. It summarizes the material framework difference from `v0.1.0` without claiming that release governance existed at publication time.

This tag is a `source-snapshot-only` provenance anchor and is not an installable package. Its repository tree must not be used as a whole-tree overlay.

## Highlights

- Normalized the root `AGENTS.md` entry and thin `CLAUDE.md` adapter.
- Added durable standalone assessments with stable `ASM-*` identities and assessment-to-remediation boundaries.
- Clarified GitHub-Flow-like workflow branches, checkpoint continuation, and default `--no-ff` merges.
- Added AI-authored commit trailers and stronger workflow/AI-context validation.
- Separated slice task intent from command/query/reactor/generic execution modes and introduced a remediation overlay.
- Made external code indexes optional discovery accelerators rather than evidence sources.

## Compatibility

This pre-1.0 minor release contains contract changes. Targets copied from `v0.1.0` require reconciliation, especially for root entry files, local workflow/task templates, skill wrappers, and target-owned project documents.

## Known Limitations

- The release does not yet contain a target provenance manifest or dedicated upgrade skill.
- Historical workflow artifacts retain their original schemas.
- Dependency/version validation remains deferred until a dotnet-native replacement exists.
- New installations must use a published governed package rather than this tag tree.
