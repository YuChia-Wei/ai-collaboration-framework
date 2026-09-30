# REL-v0.4.0 — Truth Alignment And Reconstruction Contracts

## Status

Published. Annotated tag `v0.4.0` resolves to
`5af1db672928f9d51f55fee04183ad27b79fb9f8`. Tag-triggered automation
successfully published `REL-v0.4.0` and its governed ZIP, tar.gz, and adjacent
checksum assets.

## Highlights

- Centralizes target-owned technology selections so products can override
  framework defaults for mocking, ORM, broker, and similar implementation
  choices without rewriting unrelated architecture rules.
- Keeps NSubstitute as the default mocking library while making the choice an
  explicit product profile rather than a universal invariant.
- Defines soft delete as the default Aggregate Repository profile, supports an
  explicit target opt-out, and preserves hard delete as a separate
  purpose-specific capability.
- Replaces historical BuildingBlocks assumptions with an interface-first
  reconstruction contract. The only retained optional base class is the
  executable-tested `EsAggregateRoot<TId>` replay/pending-event mechanism.
- Defines one logical solution grammar using
  `<workload>/DomainCore` and `<workload>/Presentation`, with workload mapped to
  a bounded context for micro-system mono repos and to a system for mono-system
  repos. Physical solution-folder layout remains target-owned.
- Aligns Controller examples and delegated guidance with asynchronous
  `ExecuteAsync`, request cancellation, typed results, and separate immutable
  DTOs.
- Reclassifies examples by machine-readable evidence tier, consolidates
  duplicate BDD and Outbox routes, and retires hollow fixture or placeholder
  material that had no executable evidence.
- Moves human migration/tooling guidance out of normative standards, retires
  legacy product-shaped prompt bodies after recording current skill routes,
  and separates README purpose from INDEX catalogs across standards and guide
  areas.
- Adds Git-backed file-disposition validation so every changed distributable
  framework path is accounted for without treating incoming intent as target
  write authorization.
- Renames the coding standards shell gate to structural integrity, expands its
  catalog coverage, and classifies every shell asset by execution role,
  lifecycle, distribution, authority, and replacement direction so packaging
  is not mistaken for semantic endorsement.
- Removes the stale test-compliance grep helper from automatic gates and marks
  it as a packaged retirement candidate for the v0.4.0 migration window.

## Compatibility

This pre-1.0 minor release intentionally changes several reusable contracts and
therefore declares breaking changes. `v0.3.0` is the governed reconciliation
source. No source version is declared safe for unattended upgrade: target-owned
truth, local overrides, renamed paths, retired examples, and copied source
includes require a reviewed dry-run plan.

The full Observability/AOP framework remains deferred in backlog item
`OBS-001`. This release only retains the bounded rule that runtime
CrossCutting/Observability concerns must not become a Domain dependency.

## Release Validation

The remediation workflow completed, and independent closeout assessment
`ASM-20260717-003` reported no new release-blocking findings. At candidate commit
`79db0d199016af5c17f0e47e1a821c9a69704633`:

- the composed full gate passed 21/21 required checks with zero failures or
  advisories;
- focused profile, analyzer, validation, and executable BuildingBlocks tests
  passed;
- two package builds produced byte-identical ZIP and tar.gz archives;
- archive envelopes, inventories, member checksums, external checksum sidecars,
  and ZIP/tar parity passed validation.

The candidate archives were local validation artifacts. Publication automation
rebuilt the final assets from the immutable user-created tag.

Post-merge validation also passed at
`7de3036f72aa4454d3ddbde8f188f0cc5e9acb14`: the full gate passed and two
immutable-tree package builds were byte-identical with valid archive parity and
checksums.

The final tagged-tree commit
`5af1db672928f9d51f55fee04183ad27b79fb9f8` also passed the full gate and two
byte-identical package builds. GitHub Actions run `29544032150` completed
successfully. The four published assets were downloaded again; archive
inventories, member checksums, external checksum sidecars, and ZIP/tar parity
all passed validation.

## Publication Completion

- Release ID: `REL-v0.4.0`
- Annotated tag: `v0.4.0`
- Published commit: `5af1db672928f9d51f55fee04183ad27b79fb9f8`
- GitHub Actions run: `29544032150`
- Release state: stable, non-draft, non-prerelease
- Tag ownership: user-created and immutable; automation did not create or move
  the tag
