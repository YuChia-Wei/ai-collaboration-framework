# REL-v0.11.0 — Product Boundary, Delivery Contract, And Evidence Completion

## Status

Published on the immutable annotated `v0.11.0` tag under Issues #151 and #152.

## Highlights

- Establishes an explicit single-authority product-source and deterministic distribution-projection contract.
- Adds changed-path-aware, dependency-expanded validation selection that escalates unknown impact instead of guessing.
- Makes unavailable execution metrics explicit and retains privacy-preserving durable evidence contracts.
- Defines portable environment-readiness states separately from execution results.
- Defines contract-only boundaries for the Distribution CLI, Portable Validator Engine, and source-only Maintainer CLI.
- Converges release, workflow, Issue, and provider terminal-state ownership without modifying immutable prior releases.

## Compatibility

This is a breaking pre-1.0 framework release. Automated governed upgrade is supported from v0.10.0; earlier sources require reviewed reconciliation. Target-owned collaboration, configuration, provenance, and customization truth remains protected by dry-run, acknowledgement, and rollback contracts.

## Validation Disclosure

The original fast-path publication deferred validation. A later source-only closeout rerun passed focused release tests, registry and workflow validators, Windows and WSL closeout profiles, the Windows PR profile, hosted finalization read-back, and the official closeout verifier. The original publication run remains truthfully recorded as failed, and no new hosted PR run or full release-profile fixture matrix is claimed.

## Included Work

#96, #95, #145, #146, #147, and #148. Issues #143, #144, and #152 are traceability/authorization slices and are not counted separately.

## Known Limitations

Native validator runtime/language selection (#149), repository rename (#150), and first-class Copilot support (#153) remain deferred. This release defines the CLI contract but does not ship a native CLI binary or package-registry artifact.
