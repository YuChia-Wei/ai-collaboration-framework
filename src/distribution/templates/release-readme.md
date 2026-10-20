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

Installation ownership comes from verified installed inventory and bytes, not
directory names, Git tracking or a caller cleanup list. Preserve unknown/custom
skills, supporting resources and project development records by default.
Missing managed files, committed managed modifications and unowned destination collisions remain
conflicts; reinstall does not bypass them. Missing or unsupported historical
ownership blocks cleanup. Reinstall observes affected paths, not all history.
Old managed members absent from the new candidate need explicit cleanup or
preserved_inputs pins; omission stops before preview or cleanup. Explicitly
preserved old members leave the new installation's management, and retained
runtime entries may still be discovered or reference removed dependencies.
Preservation is not deactivation or continued framework ownership.

Paired project edits accept only AGENTS.md, AGENTS.zh-TW.md, CLAUDE.md, README.md,
README.en.md, .ai/INDEX.MD, .ai/custom/installation.json,
.agents/skills/README.md, .claude/skills/README.md, .codex/config.toml and
.claude/settings.json. Review exact content changes and retain custom settings;
other project editing is a separate operation. This protective restriction
rejects formerly accepted arbitrary edits without changing API/lock versions.
Use the original pinned engine/journal to recover an existing operation.
Explicit preservation hashes do not certify every untouched project file.

Snapshot builds are development artifacts, even though the current Catalog 1
builder requires a numeric rc.N distribution label. The full SHA identifies them.
Build/archive success does not establish test, runtime or native acceptance.
Draft readiness is not publication. Release notes and publication are owner actions.
