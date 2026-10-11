# AI Collaboration Framework ${label}

Source commit: ${source_commit}
Catalog identity: ${catalog_identity}
Distribution label: ${release_version}
Engine: framework-managed-installation 2.0.0 (23 pinned product-source files).

This generic package includes the full catalog, standalone engine, independently
selected engine pin and raw content hashes. Catalog metadata includes the actual
build receipt. It contains no project-bound selection or installed target state.

Use engine/src/tools/derive-subset.py with an explicitly selected preset/selection,
the included catalog and its identity, and engine-pin.json. Run Python with -I -B;
provide PyYAML 6.x and explicit disjoint output/scratch roots.
Distribution and engine identity must be reviewed before target installation.

Snapshot builds are development artifacts, even though the current Catalog 1
builder requires a numeric rc.N distribution label. The full SHA identifies them.
Build/archive success does not establish test, runtime or native acceptance.
Draft readiness is not publication. Release notes and publication are owner actions.
