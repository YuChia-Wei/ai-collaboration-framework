# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This file is the canonical English root collaboration guide. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation.

## Source Development Rules

Read [the source development policy](.dev/standards/SOURCE-DEVELOPMENT-POLICY.md)
for ordinary source work: validation necessity, PR checks, conditional independent
review and rule maintenance. It owns these rules; this entry supplies navigation.
The owner's 2026-10-18 #461 decision simplifies this project's rules only;
framework product changes under #463 require separate implementation authority.
Release, support, credentials, protection and downstream adoption retain their
owners. No merge or date proves CI success.

## Scope And Authority

- This is the source repository for a reusable AI collaboration framework, not a product application.
- A deeper `AGENTS.*` file overrides this file in its subtree.
- Precedence is: user and explicit approval, deeper `AGENTS.*`, this file, then other general documents.
- Use current Git-tracked files, validated records, and live provider read-back. Historical workflows, assessments, releases, examples, and migrated records are evidence, not current state.
- Keep source-framework, downstream target, provider, and runtime session truth separate.
- Do not invent facts, authorization, availability, execution, validation, Issue state, or release state. Stop for unresolved owner-sensitive decisions.

- Public Epic/Feature/Story, Issue and PR content, including comments and review discussions, MUST follow [public requirement content](.dev/standards/PUBLIC-REQUIREMENT-CONTENT-POLICY.md). Keep execution authorization and handoff in the workflow mechanism, never in the Issue or PR channel; preserve functional discussion, dependencies, validation/review evidence and feature completion summaries.

## Execution Rules

- Make the smallest coherent change that satisfies accepted scope and observable completion criteria.
- Touch only required files; preserve unrelated user changes.
- Treat implementation, push, pull request, merge, Issue or Project mutation, tag, release, publication, and credential use as separate actions unless authorized together.
- Prefer deterministic tools for inventories, paths, hashes, schemas, Git identity, build, test, and receipts.
- `failed`, `blocked-by-environment`, `not-applicable`, and `deferred-with-owner` are not `passed`.
- Prefer an applicable and permitted IDE MCP refactoring operation.
- Select sub-agent model and effort by task from `.ai/project/sub-agent-policy.json`, never by inheriting this conversation. Prefer deterministic tools; Codex defaults to Luna and uses Sol for substantive reasoning, Claude defaults to Haiku and uses Sonnet by task. Astra/Opus require separate explicit authorization. Check runtime overrides and actual invocation identity; missing policy or unavailable selection stops that delegation. Project model preferences are maintained separately from managed role packages; see [sub-agent management](docs/sub-agent-management.md).
- Resolve registered sub-agent purposes through `.ai/project/sub-agent-registry.json`; verify the selected package and runtime entry before delegation. Project authoring lives under `.ai/project/sub-agents/`. Preserve unknown entries and keep upstream coverage, owner adoption, file readback and runtime activation separate. Registry records never grant framework ownership or authorize an automatic route switch.

## Progressive Context Loading

1. Start with the request, current Git/worktree state, this file, and explicitly named Issues or artifacts.
2. Select one owning skill or policy, then load its canonical entry. A generated runtime entry may serve directly; reload its full source only for metadata, maintenance, or discrepancy resolution.
3. Expand only for an applicable phase, finding, file type, provider, decision, or execution boundary.
4. Do not preload `README.md`, all indexes, all standards, every skill reference, historical workflows, or assessment archives.
5. Do not broad-scan `src/`, `tests/`, `.dev/workflows/`, or `.dev/assessments/` unless scope requires it.
6. Verify material conclusions with Git-tracked evidence, current provider read-back, or repository-owned validators. No search result is not proof of absence.

## Task Routing

Use the original skill IDs in `.agents/skills/<skill-id>/SKILL.md` for Codex and `.claude/skills/<skill-id>/SKILL.md` for Claude. These generated entries and `.ai/core/skills/` are installed projections of editable product sources in `src/skills/`; select them through `.ai/project/installation.json`. Do not edit generated installed files. The current source distribution catalog has 21 skills; see the [skill catalog](docs/skills/README.md) for versions and responsibilities. It replaces `ddd-ca-hex-architect` with `domain-model-designer` and `software-architect`, without an alias. The four source presets that selected the old ID now select both new IDs. This source project's installation uses a reviewed local source snapshot with 17 skills, including `domain-model-designer` and `software-architect`; the retired combined architect entry is removed. Verify the actual runtime entry before invocation. Optional `ai-context-init`, `workflow-records` and `user-story-author` remain independently selectable source packages. The `project-initialization` preset selects initialization separately. Installing the package supplies authoring resources, not initialized root documents. `standards-promotion@0.1.1-alpha.1` remains editable in `src/skills/` for independently copied experiments and is excluded from catalogs, presets and release products pending owner-selected validation; it is not an installed source-project route. Generated installation state is updated separately. Removed compatibility roots do not provide current executable routes.

| Need | Owning route |
| --- | --- |
| AI-context audit or comparison | `ai-context-auditor` |
| AI-context governance and reusable context maintenance | `ai-context-governance` |
| Domain exploration/modeling or software architecture | Use [domain-model-designer](.agents/skills/domain-model-designer/SKILL.md) for domain exploration/modeling and [software-architect](.agents/skills/software-architect/SKILL.md) for software architecture (Claude: the matching `.claude/skills/<skill-id>/SKILL.md` entries). Use each installed contract; neither is an alias for the retired combined skill. |
| Test design, code review, diagnosis, or implementation | `test-designer` / `code-reviewer` / `diagnostic-analyst` / `slice-implementer` / `local-change-implementer` |
| Requirements, specifications, problem frames, or selected compliance | `requirement-author` / `spec-author` / `problem-frame-author` / `spec-compliance-validator` |
| Decisions, lessons, or pull requests | `adr-author` / `lesson-author` / `pr-author` |
| Multi-stage software development | `software-development-orchestrator` for stage selection and specialist handoffs; source `.dev/` policy and Issue authority own workflow records and integration |
| Initialization or upgrade of a previously published legacy package format | Retained source compatibility duty with no current portable or executable route; restore a verified source-owned procedure before execution. |
| Historical or exceptional source release closeout | `releases/` and source release policy; no portable installed skill route. |

For Issue operations, explicitly read `.ai/project/framework.json` and its
`skills.software-development-orchestrator.issue_control` selection. Empty means
use available authorized tools under the source GitHub policies. A selected
project or experimental route must be available; never silently switch it.
Standalone `local-backlog` is retired; no replacement issue-control skill is
currently provided. Preserve existing external work references when settings change.

For source work, `.dev/standards/` continues to own source policy, GitHub work authority, release governance, U001 and the P7 deferrals. Preserve the retained source duties explicitly: source assessment persistence and terminal records; source customization and policy reconciliation; legacy CBF/SWF intake and active records; the target-selected legacy .NET 100% gate and rule resolver, only when maintaining that legacy downstream format or target (not for this framework source or its own installation); and old published-format initialization, upgrade and recovery. Duty retention does not establish tool availability. The removed legacy roots and validators that still depend on them are unavailable until a verified source-owned route is restored; they do not restore removed runtime discovery entries.

- For AI-context placement or language changes, load `.dev/standards/AI-CONTEXT-BOUNDARY.md` and `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` only when applicable.
- For code review, load the installed `code-reviewer` entry and only its applicable route and finding references.
- `test-execution` has no required skill; resolve target-owned commands first.
- Direct execution remains valid. Scope delegation under `.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md`; load a selected role's current instructions only when applicable. `.dev/contracts/ROLE-EXECUTION-CONTRACT.md` describes source execution evidence; its historical formats do not select ordinary-source procedures. Static profile presence is not invocation evidence.

## Workflow And Change Control

- Small, local, single-pass work may remain direct mode.
- For source-of-truth, AI-context, routing, wrapper, multi-stage, or durable cross-session work, load `.dev/standards/WORKFLOW-GATE-POLICY.md`.
- In workflow mode, follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` and `.dev/TEAM-GIT-FLOW-RULES.MD`; switch to the dedicated branch before material edits.
- Daily execution storage and explicit native continuation follow [workflow storage](.dev/standards/WORKFLOW-STORE-POLICY.md). Use its explicit configuration and source CLI; the optional `workflow-records` package is not installed here. Formal artifacts stay Git-owned and historical workflow files remain provenance; no automatic discovery or Git fallback is selected.
- A retained read-only report uses `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`; it does not require a workflow by itself.
- For cross-session transfer, follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`; the checkpoint must not depend on hidden conversation state.
- Before committing, follow `.dev/standards/GIT-COMMIT-POLICY.md` and validate the complete planned message from a message file before invoking `git commit`.
- Merge, workflow completion, Issue closure, Project status, release allocation, publication, and target upgrade are distinct states.

## Validation And Review

- Before running tests, apply the source policy's necessity decision to the actual diff, semantics and direct dependencies. An edit or file extension alone is not a local test trigger.
- Preserve the PR hosted gate and applicable independent review. Local checks, review, hosted results and acceptance establish different facts.
- For authorized rule changes, replace obsolete instructions at their owner. Preserve valid protections and unrelated content; do not stack priority disclaimers over conflicting operational text.
- Keep failures and limitations visible. Do not claim an unexecuted test passed or weaken behavior merely to make a check green.
- For delegated work, read [agent guardrails](.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md). Keep one tracked writer and immutable, read-only independent review; follow actual user-selected model/effort and permissions.
- Use [evidence guidance](.dev/contracts/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md) only when interpreting an earlier result. Ordinary work needs no separate reuse receipt, hash inventory or acceptance ledger.
- Verify code-graph index SHA and coverage before discovery claims. Reindex stale/missing graphs or use an explicit tracked-file fallback; search absence is not proof.
- Never assign PowerShell automatic or reserved variables, case-insensitively; use purpose-specific names.

### Historical Context — NOT AN EXECUTION TRIGGER

Earlier U001/redesign and fixture-acceleration instructions are not ordinary
source procedures. Do not load or execute them merely because they are mentioned
in historical records. Only separately selected legacy/native/release obligations
use their compatible revision and verified route; missing tooling remains
unavailable and retained deferrals are not passes. Their owners retain release,
support and recovery duties. The
[temporary execution override](.dev/standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md)
is historical context for those explicitly retained obligations only.

## CLI And Runtime Boundaries

- After higher-priority policy selects cross-boundary CLI execution, load `.dev/contracts/CLI-EXECUTION-ROUTING-CONTRACT.md`.
- The optional binding may exist only at `.dev/ai-context/local/cli-execution-routing.yaml`; it must remain ignored, untracked, unstaged, secret-free, and outside package or provenance truth.
- Never create or update it implicitly. Verify recovery first, then disclose the exact path, fields, `create/merge/replace` action, and secret exclusion; decline or no answer writes nothing.
- Do not silently substitute a model, provider, execution surface, credential boundary, or permission. Static configuration does not prove current-session execution.

## Stop Conditions

Stop before mutation when authorization is missing or contradictory, authority cannot be resolved, the write exceeds scope, target-owned truth lacks reconciliation, required evidence cannot be proven, the fixed subject drifted, or a new owner-sensitive decision is required.

Repairable implementation, test, or CI failures inside authorized scope are not owner checkpoints by themselves.

## Documentation Ownership

- Editable reusable resources belong in `src`; resources required by a framework capability must be included there or declared as knowledge dependencies. Every downstream package member and required runtime resource must originate in `src`. Root `tools` serves source-project orchestration and validation; product execution must not reuse it or any resource outside `src`.
- `.dev` owns this project's records, policies and collaboration; `docs` owns product documentation. Source and installed copies may coexist because this repository develops and uses the framework.
- Prepare reusable resources in source before separately selected self-installation/upgrade. Remove obsolete documents without experience-transfer value; preserve existing `.dev/design`, `.dev/assessments`, `.dev/requirement`, `.dev/adr` and `.dev/workflows` history in this cleanup.

## Navigation And Language

Use indexes only when needed:

- `.ai/INDEX.MD`: generated installed content and source-tooling data.
- `.dev/INDEX.md`: project knowledge and current records.
- `.dev/standards/INDEX.MD`: standards navigation.
- `docs/`: human-facing product manuals; `.dev/guides/` explains source-project work and experience.
- `.agents/skills/README.md` and `.claude/skills/README.md`: installed skill inventories.

### Root Entry Files

| Path | Responsibility |
| --- | --- |
| `README.md` | Human-facing Traditional Chinese repository entry |
| `README.en.md` | English repository entry |
| `AGENTS.md` | Canonical English root collaboration guide |
| `AGENTS.zh-TW.md` | Traditional Chinese translation |
| `CLAUDE.md` | Thin Claude project-memory adapter |

- Agent-facing execution contracts should prefer English.
- Human-facing guides may use Traditional Chinese (Taiwan) or English.
- Keep `AGENTS.zh-TW.md` structurally and normatively aligned; it must not add or remove rules.
