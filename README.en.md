# AI Collaboration Framework

This repository is the source for a reusable AI collaboration framework. It maintains the product packages and installs a selected version for Codex and Claude work in this repository.

## Start here

| Purpose | Path |
| --- | --- |
| Agent collaboration rules and current routes | [`AGENTS.md`](AGENTS.md) |
| Source operating policies | [`.dev/standards/`](.dev/standards/INDEX.MD) |
| Editable reusable framework source | [`src/`](src/) |
| Generated package installed here | [`.ai/core/`](.ai/core/) |
| Codex skill entries | [`.agents/skills/README.md`](.agents/skills/README.md) |
| Claude skill entries | [`.claude/skills/README.md`](.claude/skills/README.md) |
| Source policy, workflow records, and release governance | [`.dev/INDEX.md`](.dev/INDEX.md) |

## This repository's installation selection

The current distribution catalog contains 18 portable skills with Codex and Claude adapters. Optional [`ai-context-init@0.1.0`](src/skills/ai-context-init/SKILL.md) adds evidence-based project context and structure authoring through the separate `project-initialization` preset. Existing presets and this source project's 17-skill installation are unchanged; installing this package does not create root documents automatically. `standards-promotion@0.1.1-alpha.1` remains under `src/skills/` for standalone experiments and is excluded from framework release products and installation until its purpose and behavior are separately validated. `software-development-orchestrator` again coordinates development stages; the project selects its workflow record format and location. The authoring package IDs are `adr-author`, `lesson-author` and `pr-author`. This source project's installation selection excludes engineering knowledge packages. The lock records the generated installation identity separately from the source catalog. `.ai/custom/installation.json` records the project-owned selection; the managed installer generates `.ai/framework.lock`, `.ai/core/`, and both runtime entry sets. Do not edit generated content directly. Edit product sources under `src/` and update the installation through the source workflow.

See the [skill responsibility history](.dev/guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md) for additions, removals, renames and changed duties.

Installation selection is separate from skill operation settings. `.ai/custom/framework.json` binds Lesson, ADR, PR, CBF, and standards-promotion skills to five project-owned filesystem roots with exact write_roots and package templates, using tracked intent. No records or evidence have been created, and no ADR decision, promotion target/source adapters, or local-backlog provider are configured. The standards-promotion namespace settings are retained while that skill is not installed. These are path selections, not proof of authorization, store availability, or runtime capability.

RC3 provides an explicit Git-backed breaking reinstall through the pinned engine's `tools/reinstall-framework.py`. It requires exact cleanup and preservation lists, preflights the new installation in an external preview, and verifies retained bytes after installation. Cleanup is non-atomic: the committed Git baseline owns obsolete-file recovery, and the pinned API 2 journal owns the new installation. Read the [reinstall contract](.dev/workflows/2026-09-30-rc3-reinstall/breaking-reinstall.md) and [actual source/MQ trial results](.dev/workflows/2026-09-30-rc3-reinstall/results.md).

## Source and compatibility boundaries

- `src/skills/` and `src/knowledge/` are the editable reusable product sources; this repository selects no engineering knowledge package.
- `.ai/core/`, `.ai/framework.lock`, and runtime entries are installation outputs.
- Legacy compatibility roots have been removed from this source layout. Historical references do not establish current executable tooling.
- `.dev/standards/` owns source policy, Issue authority, U001, and P7 deferrals; `releases/` owns release records and version-support boundaries.
- Initialization, upgrade, and transaction recovery for previously published formats remain source-owned compatibility duties with no current portable or executable legacy route. Historical or exceptional release closeout remains governed by source release policy.

Follow [`AGENTS.md`](AGENTS.md) and the `.dev/standards/` policies it names. The RC3 report records the actual packaging, reinstall and read-back scope. Runtime discovery, application behavior, failure recovery and hosted admission retain their specific S6/P7 verification status. Stable publication and a GitHub Release are separate owner decisions.
