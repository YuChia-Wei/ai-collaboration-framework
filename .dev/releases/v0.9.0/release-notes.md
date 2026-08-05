# REL-v0.9.0 — Governed Rule Resolution, Bundled Validation, And Release Safety

## Status

Validated governed candidate integrated by PR #130. All hosted checks and the
merged-main pre-tag gate passed. No tag, published package, or GitHub Release
exists; immutable tag creation remains owner-controlled.

## Highlights

- Establishes stable engineering-rule identities and moves their reusable
  portable and .NET-profile content to explicit canonical owners.
- Adds target-effective rule state, freshness-checked task packets, and one
  deterministic rule-resolution contract for in-scope action skills.
- Makes the bundled .NET mechanical-validation provider source-available at a
  stable profile-owned root while keeping analyzers and runtime validation
  separately selectable and inactive by default.
- Fails closed when selected framework-managed paths are hidden by target Git
  ignore or exclude rules during package planning, application, or provenance
  finalization.
- Records canonical owning-skill reachability and provider-neutral
  role-execution evidence without treating static reachability as delegated
  execution.
- Adds bilingual root navigation for the stable bundled provider and clearly
  distinguishes portable production projects from source-only framework tests.

## Compatibility

v0.9.0 is a pre-1.0 minor release with breaking changes. Stable engineering
rule and standards locations, bundled-provider production roots, and
target-effective rule-consumption contracts have changed. The exact published
v0.8.0 package is the sole automatic and reviewed reconciliation source.
Targets on older releases must first follow their published route to v0.8.0.

Automatic planning remains dry-run first and never replaces target-owned
content. The target must review every proposed move, merge, removal, local
customization, provider selection, and ignored framework-managed path. An
acknowledgement preserves the target value; it never authorizes an overwrite
or deletion.

The Architecture Kit remains unavailable and non-selectable. This release
ships an explicit readiness gate only; it does not perform the separately
authorized future provider package, proof production, or cutover.

## Known Limitations

- The owner waived duplicate clean-install and v0.8.0 upgrade fixture execution
  after a commit-message-only rewrite. Independent verification established an
  identical Git tree, payload inventory, migration contract, archive contents,
  and checksums; the original fresh fixture passes are therefore retained as
  bounded equivalence evidence rather than represented as a second execution.
- The online-only timing/block validation correction in Issue #128 is already
  integrated into the source train. It has no local backlog item, is not a
  ninth canonical Included Work entry, and does not complete EVAL-002 or Issue
  #95's broader evaluation contract.
- `materialize-to-tools` remains unsupported without target limitation
  evidence and separate authorization; reference-in-place remains the only
  implemented bundled-provider activation mode.

## Release Validation

The release record uses the canonical v0.9.0 phase contract and the exact
resolved eight-item backlog set. Deterministic candidate packages, the fresh
clean-install and exact-v0.8.0 upgrade fixtures, the 49/49 repository critical
gate, and independent assessment `ASM-20260805-004` support the validated
candidate state. PR #130 passed all five hosted checks and merged through merge
commit `c14a3260cba7d0a9e2b67b73df9e221280d2d2ef`; the sanctioned current-main
pre-tag critical gate then passed in 910.2 seconds. Owner-created annotated tag
and hosted publication remain separate pending stages. A blocked, skipped,
deferred, or not-applicable check is recorded separately from a passed check.

From v0.7.0 onward, the renderer appends the canonical `Included Work` section
from `release.yaml.planning.backlog_refs`. Do not duplicate that generated
section in this authored source.

## Publication Completion

Pending. The repository owner creates the immutable annotated tag only after
the merged current-main pre-tag gate passes.
