# Source compatibility and tooling data

This directory is not the current product source or runtime skill registry.
Reusable framework packages are authored under `../src/`; the managed installer
generates the selected payload under `../.ai/core/` and original-ID runtime
entries under `../.agents/skills/` and `../.claude/skills/`.

Keep only source compatibility and tooling inputs that still have an active
source-maintenance caller. These files support legacy published formats,
source release/record-authoring tools, and source validation. Their presence
does not make them current portable skills or engineering-knowledge routes.

New product skill and knowledge content belongs under `../src/skills/` and
`../src/knowledge/`. Human-facing guides, effective source policy, and workflow
records remain under `../.dev/`. Use `../.ai/INDEX.MD` for the current `.ai/`
catalog.
