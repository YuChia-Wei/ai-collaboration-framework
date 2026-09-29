# Legacy skill compatibility and tooling data

This directory is not the current skill registry or runtime discovery source.
RC2 product skills are authored under `src/skills/`, installed under
`.ai/core/skills/`, and exposed to Codex and Claude through original-ID entries
in `.agents/skills/` and `.claude/skills/`.

Some files under this directory remain inputs to active source compatibility,
release, record-authoring, and validation tools. Keep only files with such an
active source-tooling responsibility. Their presence does not make them
discoverable runtime skills and does not authorize ordinary tasks to load them
instead of the installed package entry.

Published-format initialization, multi-hop upgrade and transaction recovery, and
historical or exceptional release closeout remain source-owned duties. They are
not portable installed skills. Root `AGENTS.md`, `.dev/standards/`,
`.dev/releases/`, and the specific tool inputs that still have active callers
define those boundaries.

Do not add new skill content here. Update the product in `src/skills/` and
regenerate installed content through the managed installer. `.ai/core/` and
runtime entries are generated and must not be edited directly.
