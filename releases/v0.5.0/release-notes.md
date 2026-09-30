# REL-v0.5.0 - Multi-Source, Runtime, Governance, And Release Safety

## Status

Published stable governed release. Annotated tag `v0.5.0` peels to merge commit
`1477181f0b43fa7ee82fcd482141758ac9e22eb6`; hosted publication run
`29922585651` completed successfully. Independent successor verifications
`ASM-20260722-002` and `ASM-20260722-004` pass.

## Highlights

- Introduces migration schema `2.0.0`, binding each supported source version to
  its exact immutable files-manifest digest and deterministic operation set.
- Supports direct governed package upgrades from v0.3.0, v0.4.0, v0.4.1,
  and v0.4.2, plus an independently validated clean-install route.
- Promotes the context-translator sub-agent through explicit Codex, Claude, and
  GitHub Copilot adapter metadata while retaining dynamic loading as the
  default for other roles.
- Adds semantic thin-wrapper enforcement, exact published-path dispositions,
  and a dedicated read-only governance pull-request workflow.
- Adds deterministic offline dependency/version checks and proves the declared
  gate on Windows Git Bash, hosted Ubuntu, and an owner-arranged macOS arm64
  host using native bash 3.2.57.
- Adds deterministic agent-facing language-policy checks with retained
  bilingual structural parity and bounded semantic review evidence.
- Adds a machine-readable, fail-closed receiving checkpoint for cross-model,
  runtime, host, machine, and fresh-session continuation without rewriting
  provider-native Git attribution.
- Adds blank-value release templates, exact release-phase commands,
  pre-tag validation, a cold-start publication runbook, and hosted terminal
  checks so publication does not depend on hidden session context.

## Compatibility

This is a pre-1.0 minor release and intentionally changes the public migration
contract from schema `1.0.0` to `2.0.0`. Schema `1.0.0` packages remain
readable, while v0.5.0 packages publish multiple exact source-specific
operation sets.

The automatic sources are v0.3.0, v0.4.0, v0.4.1, and v0.4.2. A source version
and its exact published files manifest must both match one declared source;
ambiguous, partial, unknown, or mismatched identities fail closed.

Targets originating at v0.0.1 must first establish governed v0.3.0 provenance
through the retained manual v0.1.0 and v0.2.0 reconciliation path.

## Release Validation

Implementation checkpoints have verified four-source package behavior,
runtime-adapter parity, governance enforcement, dependency consistency,
Windows, hosted Ubuntu, and attributed macOS portability, language policy, and
receiving-handoff mechanics. The candidate passes its exact clean-state gate, two deterministic
four-source builds, hosted candidate CI, hosted governance, and hosted Ubuntu
quick validation. Independent assessment `ASM-20260722-001` found stale
release discovery and resume state; the workflow corrected those surfaces,
successor `ASM-20260722-002` verifies every selected finding resolved, and the
macOS portability successor `ASM-20260722-004` verifies the owner-arranged
evidence intake and fixture isolation with no new release-readiness blocker.

Known limitations:

- macOS execution was performed on the owner-arranged Fable 5 host at
  `9ac40bee4ab3d4ac169c05c6229895d7a22265ff`; the receiving Windows host did
  not repeat that platform run, and this evidence is not a universal support
  guarantee;
- online package currency and vulnerability state remain advisory rather than
  claims of the deterministic offline dependency gate;
- Copilot CLI, Copilot cloud-agent, and Claude native attribution fixtures
  remain explicitly unavailable, so no provider-specific identity rule was
  invented.

## Publication Completion

Publication completed on 2026-07-22 through immutable annotated tag `v0.5.0`
and hosted run `29922585651`. The stable public Release is
[GitHub Release](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/releases/tag/v0.5.0).
It contains the governed ZIP and tar.gz packages plus both checksum sidecars.
The finalized registry records the tag peel, run, URL, and hosted asset digests.
