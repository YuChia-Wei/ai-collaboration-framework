# REL-v0.12.0 — Explicit Resources, Stable Identity, And Terminal Publication

## Status

Validated release candidate. Publication requires the user-owned annotated `v0.12.0` tag on the exact accepted `main` commit.

## Highlights

- Makes the shipped product boundary reviewable: packaged paths have explicit component and ownership assignments, while every source-only `.dev/**` omission is covered by a machine-readable exclusion or disposition instead of an unexplained gap.
- Consolidates product, package, archive, technology-profile, repository, and compatibility identities in versioned registries with fail-closed validation.
- Removes active `ez`-series names and UContract-specific references in favor of neutral Contract and BDD/GWT concepts, while retaining historical evidence only where history owns it.
- Separates immutable historical evidence from current validation so retained `.dev` records remain trustworthy without forcing obsolete historical instances to satisfy every current rule.
- Changes the normal release lifecycle to a terminal validated source record: a user-created tag triggers deterministic publication, hosted verification, and Issue/Project reconciliation without a post-tag source closeout PR.

## Product Boundary And Practical Effect

v0.12.0 keeps one versioned, componentized framework release. Mandatory collaboration and lifecycle cores, the `dotnet-backend` technology profile, and optional providers now have explicit identities and dependency rules. The archive still contains all declared component bytes; clean-install and migration planning determine the effective target selection.

The classification work is therefore a governance and review improvement, not an artificial split into many separately versioned packages. Reviewers can distinguish shipped framework bytes, target templates, target-owned truth, source-only operations, generated projections, and retained evidence before publication. New implicit omissions fail the candidate gate.

## Compatibility

This is a breaking pre-1.0 framework release. Automated governed upgrade is supported from exactly v0.11.0; earlier versions require reviewed reconciliation. The breaking surface is bounded to renamed or removed active example/reference paths and terminology. Target-owned collaboration, requirements, specifications, ADRs, operations, provenance, and customization truth remain protected by dry-run, acknowledgement, and rollback contracts.

## Release Validation

The implementation PR passed all five hosted candidate, governance, Windows, and Ubuntu checks. The exact v0.12.0 candidate additionally requires deterministic archive parity, provider preflight, a final frozen independent Luna validation, and the merged-main pre-tag gate before tag handoff.

## Publication Completion

After the exact tag workflow succeeds, hosted automation verifies the Release and assets, changes included Issues from `Not yet published` to `v0.12.0`, and completes the release-coordination Issue. The tagged source record remains `status: validated` and is not rewritten.
