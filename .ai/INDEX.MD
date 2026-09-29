# .ai Index

This index owns the file and directory catalog for `.ai/`. The `.ai/README.MD` file explains the folder purpose and boundary.

## Entry Documents

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.ai/`. |
| `INDEX.MD` | File and directory catalog for `.ai/`. |
| `DIRECTORY-RULES.MD` | Operational placement rules that point to canonical boundary and language policies. |
| `SUB-AGENT-SYSTEM.MD` | Active sub-agent routing and artifact handoff rules. |
| `distribution/` | Source-side package profiles, ownership rules, and generated metadata schemas. |
| `evaluation/` | Source-side deterministic behavior corpus, exact baseline, and result schemas. |

## Product installation

| Path | Description |
| --- | --- |
| `../src/` | Only editable product source for reusable framework packages. |
| `core/` | Generated installed framework content. The source repository selects 18 skills and no engineering knowledge package. |
| `framework.lock` | Generated identity and receipt for the installed package set. |
| `custom/installation.json` | Project-owned desired selection for the source repository. |
| `assets/` | Source compatibility and tooling data; not the current product or runtime skill source. |
| `assets/shared/` | Source execution contracts and compatibility data still required by active tools. |
| `assets/tech-stacks/` | Legacy profile data still required by named source tooling; current product knowledge is authored under `src/knowledge/`. |
| `assets/skills/` | Legacy compatibility and tooling inputs only; see `assets/skills/README.MD`. |
| `assets/templates/` | Source-tooling templates retained only where an active tool consumes them. |

## Scripts

| Path | Description |
| --- | --- |
| `scripts/` | Transitional local workflow scripts and orchestration helpers. |
| `scripts/README.md` | Script transition policy and inventory. |
| `scripts/validate-ai-context.py` | Source validation tooling; keep its concrete inputs and report skipped execution separately. |
| `scripts/python-entrypoints.json` | Registry for supported Python CLI prerequisite contracts. |
| `scripts/run-python-entrypoint.sh` | POSIX interpreter-discovery launcher for registered Python CLIs. |
| `scripts/run-python-entrypoint.ps1` | PowerShell interpreter-discovery launcher for registered Python CLIs. |

## Related Human-Facing Docs

| Path | Description |
| --- | --- |
| `../.dev/guides/README.MD` | Human-facing guide root. |
| `../.dev/guides/ai-collaboration-guides/INDEX.MD` | AI collaboration guide index. |
| `../.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md` | Human-facing strategy for AI asset placement. |
| `../.dev/guides/ai-collaboration-guides/AI-CONTEXT-INIT-SKILL-GUIDE.md` | Legacy published-format initialization guidance; not a current runtime route. |
| `../.dev/guides/ai-collaboration-guides/PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md` | Human recovery and target-local validation-selection guide. |
| `../.dev/standards/AI-CONTEXT-BOUNDARY.md` | Canonical context boundary policy. |
| `../.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` | Canonical language policy. |
