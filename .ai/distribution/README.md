# AI Context Distribution Contracts

This directory owns source-side, machine-readable contracts for building portable AI context packages. It is not copied into a target repository as project truth.

## Entry Points

- `profiles/dotnet-backend.yaml` defines the initial complete distribution profile, source allowlist, ownership classes, and exclusions.
- `identity-registry.yaml` defines repository, public product, framework release, technology profile, package/archive, and governed legacy alias identities without selecting a CLI identity.
- `schemas/identity-registry.schema.yaml` defines the source-only identity registry contract; `validate-repository-identity.py` validates its uniqueness, separation, aliases, and declared consumers.
- `source-dispositions.yaml` explains every tracked `.dev/**` source path that is neither selected by the `dotnet-backend` payload nor covered by a profile exclusion. `schemas/source-dispositions.schema.yaml` defines its taxonomy; `validate-source-dispositions.py` recomputes the Git-tree partition and fails on implicit omissions, stale or overlapping patterns, and payload/exclusion conflicts.
- `../assets/shared/PRODUCT-SOURCE-PROJECTION-CONTRACT.md` defines the single canonical product-source and derived-projection boundary.
- `CLI-TOOLING-CONTRACT.md` defines the contract-only Distribution CLI, Portable Validator Engine, and source-only Source Maintainer CLI boundaries.
- `schemas/package.schema.yaml` defines package-envelope metadata.
- `schemas/files.schema.yaml` defines the generated per-file inventory.
- `schemas/migration.schema.yaml` defines version-to-version migration operations.

## Boundary

- A builder must start from the profile allowlist. It must not archive the repository and then rely on exclusions for safety.
- For the governed `.dev/**` coverage, every tracked source path must resolve to exactly one of three states: packaged source, explicit profile exclusion, or one active source-disposition record. Candidate review emits JSON and Markdown read-back without adding the source-only contract to package bytes.
- Exclusions are a deny boundary over the allowlist. An `except` entry restores only the named reusable path and must also be covered by an allowlist entry.
- Source paths are resolved from a clean Git tree at the requested immutable commit or tag.
- Builders read Git blob bytes and Git tree modes, not checkout bytes; this prevents `autocrlf` or local mode settings from changing package output. Symlinks, submodules, and non-regular Git entries are rejected.
- Generated metadata belongs under the package envelope's `metadata/` directory and is not installed as target project truth.
- `requirements.txt` is checksum-governed envelope metadata for the packaged target-side tooling. Install it with Python 3.11 or newer before invoking the planner.
- Root entries and empty target catalogs come from public templates owned by `ai-context-init`; active source-repository root documents and catalogs are not templates.
- External indexes or knowledge graphs may accelerate discovery but cannot prove package completeness.
- Repository, public product, release, technology profile, archive/package, skill alias, and future CLI/toolchain namespaces are separate identity classes. The registry may bind relationships between them, but a repository rename never authorizes another identity change.
- Distribution profile and release records remain stable compiled consumers. The source validator cross-checks their literals against the registry so #166 adds no package payload, archive-name, schema, or migration behavior change.
- A profile entry marked `allow_empty_until` is a workflow bootstrap exception. A release candidate validator must reject every remaining empty entry.
- Template-manifest `source` paths are resolved relative to the manifest directory. Targets are repository-relative payload paths; reject absolute paths, `..`, backslashes, duplicates, and collisions. A template may exist once at its canonical managed path and once at its mapped target seed path.
- `metadata/SHA256SUMS.txt` covers every other envelope member and excludes itself. Archive digests are external `.sha256` sidecars because an archive cannot contain its own final digest.
- The profile's `reference_integrity` contract rejects concrete links or backtick paths from packaged text back into dated source workflows, assessment instances, release instances, or source backlog items. Generic placeholders remain allowed; package payload must not depend on excluded source lifecycle history.
- Migration schema `2.0.0` keeps clean-install operations separate from an
  ordered `sources` list. Each automatic source is selected by both its declared
  version and the SHA-256 of its exact immutable `files.yaml`; missing,
  unknown, mismatched, duplicate, or ambiguous identities fail closed.
- Target-side planners retain read compatibility for migration schema `1.0.0`.
  A schema `2.0.0` upgrade must pass both `--previous-version` and
  `--previous-files`; a clean install passes neither.
- The supported v0.5.0 automatic source set is v0.3.0, v0.4.0, v0.4.1, and
  v0.4.2. Each route requires the exact published source inventory; listing a
  version never permits a different release's `files.yaml`.
  A target whose earliest recorded provenance is v0.0.1 must first follow the
  governed v0.0.1-to-v0.3.0 reconciliation route, then use the direct
  v0.3.0-to-v0.5.0 migration. v0.0.1 is not silently treated as an automatic
  v0.5.0 source.

## Ownership Classes

| Class | Meaning | Automatic update rule |
| --- | --- | --- |
| `framework-managed` | Reusable framework content whose released bytes are controlled by this repository. | May replace or remove only when the target hash matches the previous released hash. |
| `target-template` | Seed content that becomes target-owned after initialization or reconciliation. | Create only when absent; otherwise require reconciliation. Never automatically remove. |
| `target-owned` | Target-specific truth recorded for classification but not supplied as reusable payload. | Never overwrite or remove automatically. |

## Installation Behaviors

- `managed`: use three-way, previous-release-hash-aware replacement and removal.
- `seed`: create only when absent and hand ownership to the target.
- `reconcile`: report a required target-specific decision or rewrite; do not apply automatically.
- `exclude`: never place the source path in a distributable payload.
