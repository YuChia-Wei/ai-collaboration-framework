# Installed framework and source tooling

This directory contains the source repository's installed framework selection,
generated package payload, and local source-maintenance tooling. It is not the
editable product source or the human-facing guide root.

The reusable product is authored under `../src/`. The source repository
explicitly selects 18 skills with Codex and Claude adapters and no engineering
knowledge package in `custom/installation.json`. The managed installer creates
`framework.lock`, `core/skills/`, and the runtime entries. Do not edit those
generated files directly.

Use `INDEX.MD` for the file catalog. `.ai/assets/` contains only source
compatibility and tooling data with active callers; current skill discovery
uses original-ID entries under `.agents/skills/` and `.claude/skills/`.
Human-facing guides, project policy, and workflow records remain under `.dev/`.
