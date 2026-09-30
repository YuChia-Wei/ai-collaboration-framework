# AI Collaboration Framework

This repository is the source for a reusable AI collaboration framework. It maintains the product packages and installs a selected version for Codex and Claude work in this repository.

## Start here

| Purpose | Path |
| --- | --- |
| Agent collaboration rules and current routes | [`AGENTS.md`](AGENTS.md) |
| Human guides and operating instructions | [`.dev/guides/`](.dev/guides/README.MD) |
| Editable reusable framework source | [`src/`](src/) |
| Generated package installed here | [`.ai/core/`](.ai/core/) |
| Codex skill entries | [`.agents/skills/README.md`](.agents/skills/README.md) |
| Claude skill entries | [`.claude/skills/README.md`](.claude/skills/README.md) |
| Source policy, workflow records, and release governance | [`.dev/INDEX.md`](.dev/INDEX.md) |

## This repository's installation selection

The RC3 source selection contains 17 portable skills with Codex and Claude adapters, and no engineering knowledge packages. The authoring package IDs are `adr-author`, `lesson-author` and `pr-author`; portable workflow orchestration has been retired. The generated installation identity remains recorded by its lock and is updated separately from this source selection. `.ai/custom/installation.json` records the project-owned selection; the managed installer generates `.ai/framework.lock`, `.ai/core/`, and both runtime entry sets. Do not edit generated content directly. Edit product sources under `src/` and update the installation through the source workflow.

Installation selection is separate from skill operation settings. `.ai/custom/framework.json` binds Lesson, ADR, PR, CBF, and standards-promotion skills to five project-owned filesystem roots with exact write_roots and package templates, using tracked intent. No records or evidence have been created, and no ADR decision, promotion target/source adapters, or local-backlog provider are configured. These are path selections, not proof of authorization, store availability, or runtime capability.

## Source and compatibility boundaries

- `src/skills/` and `src/knowledge/` are the editable reusable product sources; this repository selects no engineering knowledge package.
- `.ai/core/`, `.ai/framework.lock`, and runtime entries are installation outputs.
- Legacy compatibility roots have been removed from this source layout. Historical references do not establish current executable tooling.
- `.dev/standards/` owns source policy, Issue authority, U001, and P7 deferrals; `releases/` owns release records and version-support boundaries.
- Initialization, upgrade, and transaction recovery for previously published formats remain source-owned compatibility duties with no current portable or executable legacy route. Historical or exceptional release closeout remains governed by source release policy.

Follow [`AGENTS.md`](AGENTS.md) and the `.dev/standards/` policies it names. Installing RC2 does not establish runtime discovery, behavioral acceptance, upgrade/recovery trials, or downstream admission; owner-selected S6/P7 work owns those checks. Stable publication and a GitHub Release are separate owner decisions.
