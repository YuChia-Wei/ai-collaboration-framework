# Installed framework context

The installer owns `.ai/core/` and `framework.lock`. The project owns explicit
settings and selection in `custom/`. Runtime entries are generated into
`.agents/skills/` and `.claude/skills/` with the selected canonical names.

Editable framework sources live in `src/`; source governance and records remain
under `.dev/`. Use root `AGENTS.md` for current source routes and retained duties.
Portable workflow v2 is retired. Source `.dev/workflows` records are retained.

For a Git-backed breaking reinstall, use the independently pinned engine entry
`tools/reinstall-framework.py` and an exact cleanup/preservation plan. Ordinary
API 2 maintenance preserves its existing non-destructive contract.
