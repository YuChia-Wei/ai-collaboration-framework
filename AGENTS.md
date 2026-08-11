# AGENTS.md

[Traditional Chinese](AGENTS.zh-TW.md)

This document is the canonical English agent-facing root collaboration guide. `AGENTS.zh-TW.md` is its Traditional Chinese (Taiwan) translation.

## Scope & Precedence

- This document is the root collaboration guide for AI agents and humans working in this repository.
- This repository is an AI collaboration knowledge base and reusable context framework, not a product application repository.
- If a subdirectory has another `AGENTS.*` file, the deeper file takes precedence.
- Command priority: User/Approval > Subfolder AGENTS > This file > Other general documents.
- If an IDE MCP server is configured and provides refactoring capabilities, prefer the IDE MCP refactoring tools.

## Default Execution Principles

- Do not invent project truth. State material assumptions, uncertainty, and tradeoffs. Ask only when an unresolved direction materially affects the outcome.
- Implement the smallest coherent change that satisfies the defined acceptance criteria. Avoid speculative features, abstractions, and context.
- Touch only files required by the task. Avoid unrelated cleanup, and remove artifacts introduced by your own changes.
- Establish verifiable completion criteria before execution. Iterate until they pass, or report concrete blockers and any skipped validation.

## Repository Identity

This repository exists to:

- extract software engineering, architecture, .NET backend, and AI collaboration knowledge;
- maintain reusable AI Agent context, skills, sub-agent prompts, and workflow rules;
- separate universal AI context from tech-stack-specific context;
- preserve current non-universal capability for .NET C# backend Web API development;
- remove, isolate, or templatize historical source-project facts.

Do not treat historical sample backend information as current product truth unless a file explicitly states that it is retained as a template, migration artifact, or dotnet-backend reference.

## Quick Start for AI Agents

1. Read `README.md` or `README.en.md` to understand this repo's purpose.
2. Read `.dev/standards/AI-CONTEXT-BOUNDARY.md` and `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` before moving or rewriting AI context.
3. Use `.ai/assets/skills/README.MD` as the canonical skill registry.
4. Use `.dev/guides/ai-collaboration-guides/INDEX.MD` for human-facing skill and workflow guides.
5. Use `.ai/INDEX.MD` and `.ai/README.MD` for agent-facing AI asset navigation.

## Mandatory Workflows

### Workflow Gate

1. Read `.dev/standards/WORKFLOW-GATE-POLICY.md` when work may affect source-of-truth, AI context, skill routing, wrapper sync, or more than one stage.
2. Create workflow artifacts proactively when the gate requires workflow mode.
3. Keep small, local, single-pass changes in direct mode.
4. Before creating separate workflows for multiple approved work items, evaluate delivery cohesion; shared outcome, branch, validation, reviewers, release gate, and rollback normally use one delivery.
5. Treat fewer than three substantive tasks as a proportionality review signal. Do not invent validation or closeout tasks to justify workflow mode.

Workflow artifact rules:

- Follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`.
- Follow `.dev/TEAM-GIT-FLOW-RULES.MD` for branch naming, checkpoint continuation, push, and merge strategy.
- Create or switch to a dedicated workflow branch before creating workflow artifacts or making material workflow changes. Default Codex naming is `codex/<workflow-id>`.
- Create `.dev/workflows/<workflow-id>/workflow.yaml` as the discovery locator.
- Use a full-date `YYYY-MM-DD-<topic>` workflow ID for new work.
- Let the workflow-owning skill define its plan, task, report templates, task IDs, and declared artifact root.
- Default artifacts to `.dev/workflows/<workflow-id>/`; when a skill uses another repository-relative root, keep the locator under `.dev/workflows/`.
- Record ISO 8601 `created_at` and `updated_at` metadata on new workflow and task artifacts.
- Record `branch` and `base_branch` on workflows created on or after 2026-07-11.
- Do not store runtime workflow records under canonical skill or runtime wrapper directories.
- Treat an explicitly requested merge/push before completion as a checkpoint handoff and keep the workflow active. Resume a push-only handoff from the pushed branch; after a checkpoint merge, start a new dedicated continuation branch from the updated target.
- Follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` before transferring an active workflow across a model, runtime, host, machine, or fresh session; the receiving checkpoint must remain executable without hidden session context.
- Select linear or merge-commit integration positively under `.dev/TEAM-GIT-FLOW-RULES.MD`; workflow mode alone does not select topology.

### Long-Running Validation Gate

- Treat a validation command as long-running when its profile is `release` or
  `nightly-full`, it selects a full matrix, or its expected or observed wall
  time is at least 120 seconds.
- Finish tracked mutations and focused validation first, then bind the exact
  command to a clean immutable commit before dispatching long-running
  validation.
- Run long-running validation in a separate external runtime task using the
  least expensive capable execution profile. Keep it read-only except for
  ignored validation artifacts, and do not let it repair failures.
- The primary implementation conversation must not execute a repeated polling
  loop. After one dispatch read-back it yields; the external task reports one
  final result with commit, command, duration, outcome counts, and evidence
  references.
- Timeout, interruption, missing completion evidence, and blocked execution are
  never passed. If the runtime cannot provide a separate completion-reporting
  task, record the validation as blocked or hand it off; do not fall back to
  synchronous polling in the primary conversation.
- Do not parallelize an aggregate runner until dependency ordering, isolated
  artifacts, bounded concurrency, deterministic evidence, and fail-closed
  cancellation have independent contract coverage.

### Assessment Gate

- Follow `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md` when a read-only audit,
  large code review, architecture assessment, or similar report must be retained.
- Store durable observations under `.dev/assessments/<assessment-id>/`; do not
  create a workflow solely because a report is persisted.
- Use stable `ASM-YYYYMMDD-NNN` IDs in the locator, report, commit subject, and
  `Assessment-Id` trailer.
- Keep assessed surfaces read-only. If remediation is authorized, create or use
  the owning workflow and reference the assessment and selected finding IDs.

### Git Commit Policy

1. Follow `.dev/standards/GIT-COMMIT-POLICY.md`.
2. Use exactly one of `<type>(#<issue-number>): <summary>` or `<type>(<scope>): <summary>`; they are alternatives.
3. Treat `|` in historical examples as meta-notation for “or”, never as a literal character in a new commit title.
4. For workflow-stage commits, include `Why`, `What`, `Validation`, and `Workflow` body sections.
5. Commit one validated durable stage or coherent bounded batch, not each skill
   invocation. Rewrite only unshared, unpushed history, and preserve approval,
   review, evidence, checkpoint, and handoff boundaries.

### AI Context Governance

Use `ai-context-governance` for:

- universal versus tech-stack-specific context classification;
- AI documentation cleanup;
- language policy changes;
- skill routing changes;
- runtime wrapper sync;
- context migration planning or execution.

When governance terminology affects authority or state, resolve the qualified
term and canonical owner through `.dev/standards/AI-CONTEXT-OWNERSHIP.yaml`.
Never infer a cross-owner transition from bare candidate, validated,
integration, publication, closeout, finalization, or lifecycle wording.

Do not route pure AI documentation governance work to `bdd-gwt-test-designer`.

### AI Context Audit

Use `ai-context-auditor` for read-only AI context health and drift analysis. A conversational analysis may remain transient direct mode; when persistence is requested without remediation, create a standalone assessment and assessment branch rather than a workflow.

- Default to AI context and governance surfaces.
- Exclude `src/`, `tests/`, and other product implementation trees.
- If the user asks to scan product source or test code, stop and route that work to `code-reviewer` instead of expanding the audit.
- Keep audit findings separate from remediation; use `ai-context-governance` to coordinate the AI-context remediation lifecycle after remediation is authorized.
- Multi-pass or sub-agent analysis alone does not require workflow artifacts when the result stays in the conversation and no repository mutation or remediation occurs.
- For a durable report-only audit, keep audited surfaces read-only and commit only assessment-owned artifacts and assessment index updates.

### Development Workflow Orchestration

Use `software-development-orchestrator` when software-development work needs multi-stage planning, development skill routing, sub-agent coordination, approval pauses, target-aware test execution, validation checkpoints, or commit checkpoints. Activate it from high-level software-development intent even when the user does not name `software-development-orchestrator` or downstream skills; derive stages from the requested outcome, current artifacts, and repository policy rather than skill names.

The skill may coordinate downstream skills, but it must not replace their domain responsibilities.

Pause before creating or executing implementation work while requirement,
design, or specification approval is pending. Record the authorization source
before continuing.

Treat `test-execution` as an optional, unmapped capability contract rather than
a new required skill. Prefer target-owned commands, then a separately evaluated
external skill, then the fallback contract. Unit and integration are default;
E2E, browser, Playwright, and environment-dependent tests are conditional.
Record exact outcomes as `passed`, `failed`, `blocked-by-environment`,
`not-applicable`, or `deferred-with-owner`; blocked is never passed.

Do not route general AI-context audit, documentation governance, or repository initialization through `software-development-orchestrator`; use their owning skills and skill-specific workflow templates.

### Codex Runtime Worker Profiles

This source repository defines two project-scoped Codex execution profiles:

| Profile | Model | Default use |
| --- | --- | --- |
| `bounded-general-worker` | `gpt-5.6-terra` / `xhigh` | One independently meaningful, bounded unit that needs judgment and tool use; explicit write scope is required for mutation. |
| `bounded-routine-worker` | `gpt-5.6-luna` / `high` | Clear, repeatable, read-heavy or mechanical work such as inventory, extraction, classification, exact comparison, and log summarization. |

These files are **runtime execution profiles**, not canonical skills or canonical sub-agent roles.

- They do not add entries under `.ai/assets/sub-agent-role-prompts/**`.
- They do not own skill-to-role applicability and do not appear in the SAG canonical role inventory.
- When delegated work maps to an existing canonical role, the parent must supply the exact owning skill and `.ai/assets/sub-agent-role-prompts/<role-id>/sub-agent.yaml` path. The selected worker executes that contract but does not replace it.
- Direct execution remains the default. Delegate only when the safety gates and material-value triggers in `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md` support delegation.
- The parent owns authorization, routing, concurrent-write isolation, Issue/workflow/release state, integration, and final acceptance.
- Do not use a generic worker merely to avoid loading or following an applicable skill-owned role.
- Do not spawn nested workers from either generic worker.
- Unless the canonical product-source decision explicitly promotes them later, these two profiles are source-repository-only and must not be distributed downstream.

### Repo Init / Template Adaptation

Use `ai-context-init` as the first skill after this framework is copied into an existing or empty target repository.

The skill must:

1. inventory the target repository from file-backed facts;
2. identify copied template or historical source-project truth;
3. refresh target-specific `AGENTS.md`, `.dev/`, and necessary `.ai/` entry docs;
4. preserve framework-level collaboration rules unless the target repo clearly invalidates them;
5. remove or rewrite source-repo-specific requirements, specs, operations docs, workflow artifacts, and ADRs.

Treat `.ai/assets/skills/ai-context-init/references/migration-boundaries.md` as the authoritative migration boundary.

### AI Context Version Upgrade

Use `ai-context-upgrader` after an initialized target repository needs to move between published framework versions.

- Require `.dev/ai-context/provenance.yaml` plus
  `.dev/ai-context/customizations.yaml`, or perform explicit unresolved
  provenance reconciliation. Treat `.dev/AI-CONTEXT-SOURCE.yaml` as legacy
  read compatibility and never retain both authorities.
- Follow the governance-owned semantic customization lifecycle; require owner
  reconciliation and an independent post-upgrade audit before provenance
  finalization.
- Use `.ai/scripts/validate-ai-context-target.py` in downstream repositories;
  source release-registry and publication validation are not downstream
  prerequisites.
- Compare the recorded framework version, requested framework version, and current target state before writing.
- Preserve target-owned collaboration, requirement, spec, ADR, architecture, operations, and project configuration truth.
- Treat `automatic-candidate` entries as proposals, not write authorization; update provenance only after successful validation.
- Use Git and repository files as evidence. Optional graphs and indexes may accelerate discovery but cannot establish completeness.

### Code Review

Use `code-reviewer` only when reviewing .NET backend code or dotnet-backend implementation guidance.

When code review applies:

1. Read `.ai/assets/skills/code-reviewer/references/review-routing.yaml`.
2. Select routes by explicit scope, then type hierarchy, then path; stop when
   the applicable route is unresolved.
3. Load only the selected routes' canonical references and applicable finding
   rule IDs; do not add compatibility checklists or unrelated standards.
4. Build a scoped checklist comparison table.
5. Categorize issues as `CRITICAL`, `MUST FIX`, or `SHOULD FIX`.
6. If tests apply in the target repo, run the narrowest meaningful test command.

### Spec Compliance

Spec compliance is selectable. When it is not explicitly selected by a target
profile, problem-frame workflow, requirement, or owner decision, record it as
`not-applicable`. Once selected:

1. Run `spec-compliance-validator`.
2. Gate: coverage must be 100%.
3. Fail closed on partial configuration, missing execution evidence, or
   coverage below 100%; return to implementation or test generation before
   claiming completion.

## Skill Routing

- Canonical skill registry: `.ai/assets/skills/README.MD`
- Current runtime wrappers: `.agents/skills/README.md`
- Claude-compatible wrappers: `.claude/skills/README.md`
- Human-facing skill guides: `.dev/guides/ai-collaboration-guides/INDEX.MD`

When canonical spec and runtime wrapper differ, treat `.ai/assets/skills/` as the source of truth.

Use these boundaries:

| Need | Skill |
| --- | --- |
| Multi-stage software-development workflow orchestration, development skill routing, validation and commit checkpoints | `software-development-orchestrator` |
| Read-only AI context health, drift, and structure analysis with conversational or persisted output | `ai-context-auditor` |
| AI context cleanup, prompt boundary, language policy, wrapper sync | `ai-context-governance` |
| First sync after copying this framework into a target repo | `ai-context-init` |
| Upgrade an initialized target between published framework versions | `ai-context-upgrader` |
| .NET backend architecture design | `ddd-ca-hex-architect` |
| GWT scenario and assertion design | `bdd-gwt-test-designer` |
| .NET backend code review | `code-reviewer` |
| Problem-frame spec compliance validation | `spec-compliance-validator` |
| Requirement authoring | `requirement-author` |
| Spec authoring | `spec-author` |
| Problem frame authoring | `problem-frame-author` |
| Bounded implementation slice | `slice-implementer` |
| Local technical code change | `local-change-implementer` |

`test-execution` intentionally has no required skill mapping. Resolve it from
target-owned commands, a separately evaluated external provider, or the
fallback contract.

## File & Directory Index

### Root Entry Docs

| Path | Description |
| :--- | :--- |
| `README.md` | Human-facing Traditional Chinese repository identity |
| `README.en.md` | English translation of the repository identity |
| `AGENTS.md` | Canonical English agent-facing root collaboration guide |
| `CLAUDE.md` | Thin Claude Code project-memory entry that imports `AGENTS.md` |
| `AGENTS.zh-TW.md` | Traditional Chinese (Taiwan) translation of the root collaboration guide |

Use `.ai/INDEX.MD` for canonical AI assets, `.dev/INDEX.md` for project
knowledge and governance, and the runtime wrapper registries named under
**Skill Routing** for adapter inventories. Keep detailed directory catalogs in
those owned indexes rather than duplicating them in this always-loaded guide.

## Language Rules

- Agent-facing context should prefer English unless the source material is inherently human-facing Traditional Chinese.
- Human-facing guides and README content should prefer Traditional Chinese Taiwan usage.
- Keep runtime wrappers thin and point them to canonical specs.
- Prefer folder placement over per-file metadata for context classification.
