# REL-v0.14.0 — Retained-Origin Upgrade Routing

v0.14.0 delivers deterministic retained-origin upgrade routing for the
`dotnet-backend` distribution while preserving exact package and migration
identity across each supported source.

## Highlights

- Records exact migration inputs for governed sources v0.13.0, v0.9.0, and
  v0.6.0 under the v0.14.0 package identity.
- Establishes the source-only support matrix and route-evidence locations for
  the retained origins.
- Adds canonical direct-route evidence for each retained source and keeps the
  nine-item Included Work set bound to the release.

## Compatibility

v0.14.0 is a breaking migration checkpoint with a minimum governed source of
v0.6.0. The package records v0.13.0, v0.9.0, and v0.6.0 as exact package
migration inputs. Their direct or orchestrated route classification must come
only from the completed support matrix and its receipt-bound evidence.

## Release Validation

ZIP/TAR package parity, release-note rendering, package lifecycle validation,
and the canonical retained-origin route proofs for v0.13.0, v0.9.0, and v0.6.0
passed. The generated Release provenance below binds the public artifacts to
the immutable release tag and commit.

## Known Limitations

- Retained-origin routing is defined only for v0.13.0, v0.9.0, and v0.6.0;
  other sources require a separately reviewed migration route.
- Route resolution is read-only and does not authorize package apply or any
  target-owned reconciliation decision.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
