# Installed Codex skills

Codex discovers the selected RC2 skills by their original IDs under
`.agents/skills/<skill-id>/`. Each entry is generated from the installed package
in `.ai/core/skills/<skill-id>/` and the editable product source in
`src/skills/<skill-id>/`.

The source repository selects all 18 delivered skills and the Codex and Claude
adapters in `.ai/custom/installation.json`. No engineering knowledge package is
selected. The installer owns `.ai/core/` and `.ai/framework.lock`; do not edit
those generated files directly. The same core is shared by both runtimes.

The selected skill IDs are:

- `adr`
- `ai-context-auditor`
- `ai-context-governance`
- `bdd-gwt-test-designer`
- `code-reviewer`
- `ddd-ca-hex-architect`
- `diagnostic-analyst`
- `lesson`
- `local-backlog`
- `local-change-implementer`
- `pr`
- `problem-frame-author`
- `requirement-author`
- `slice-implementer`
- `software-development-orchestrator`
- `spec-author`
- `spec-compliance-validator`
- `standards-promotion`

The old `ai-context-init`, `ai-context-upgrader`, and
`ai-context-release-closeout` discovery entries are retired from this runtime.
Source-owned maintenance of previously published formats and exceptional
release records is routed through root `AGENTS.md`, `.dev/standards/`,
`.dev/releases/`, and only the legacy tooling that still has an active caller.
`.ai/assets/skills/` is compatibility and tooling data, not the runtime skill
registry.
