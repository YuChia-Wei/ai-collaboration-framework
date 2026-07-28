# AI Collaboration Knowledge Base and .NET Backend Context Framework

[繁體中文](README.md)

This repository is the source for a portable AI collaboration framework. It brings together software-development practices, reusable Agent context, skills, sub-agent prompts, and collaboration workflows. It currently retains and develops specialized .NET / C# backend capability while separating cross-stack collaboration rules into reusable shared content.

It is not a product application or a sample system for one product. Its purpose is to help teams bring curated and validated AI collaboration capability into new or existing repositories, while letting each target repository establish its own facts from its code, configuration, and documentation.

> This root README is a human-facing guide to the source repository, not part of a portable release payload. Packages are built from an explicit allowlist that deliberately excludes root README files, so this source-repository introduction is never carried into a target repository.

## What This Repository Is

| This repository is | This repository is not |
| --- | --- |
| A reusable AI collaboration knowledge base and framework source | A complete implementation of one product, microservice, or Web API |
| A collection of shared software-development practices and specialized .NET backend capability | A mechanism for copying this source repository's requirements, specifications, workflows, or decisions into a target project as facts |
| A governed source for portable AI context release packages | A raw source snapshot to install into a target repository |

## Problems It Helps Solve

- Give AI Agents consistent collaboration rules, document locations, and validation expectations before work begins.
- Organize requirements, specifications, architecture, implementation, tests, reviews, and handoffs into routable skills and workflows.
- Separate knowledge that is reusable across repositories from facts that only a target repository can establish, preventing historical-project context from contaminating a new project.
- Retain .NET backend implementation, design, and review experience so discussions of DDD, Clean Architecture, CQRS, and message-driven backends start from a consistent baseline.

## When It Fits

This repository is useful for teams and individuals who want a maintainable AI collaboration practice, especially when they:

- introduce durable AI Agent context into a new or existing repository;
- provide .NET / C# backend architecture and implementation conventions to multiple Agents;
- need clear ownership and handoff boundaries for requirements, specifications, implementation, tests, and code review; or
- want to preserve portable framework rules without overwriting a target repository's business, architecture, or operations facts.

## Quick Navigation

| Goal | Start here |
| --- | --- |
| Understand the source repository's architecture and scope | [`.dev/ARCHITECTURE.md`](.dev/ARCHITECTURE.md) |
| Find available AI skills | [`.ai/assets/skills/README.MD`](.ai/assets/skills/README.MD) |
| Read human-facing collaboration guides | [`.dev/guides/ai-collaboration-guides/INDEX.MD`](.dev/guides/ai-collaboration-guides/INDEX.MD) |
| Help an Agent collaborate correctly in this source repository | [`AGENTS.md`](AGENTS.md) |
| Obtain or upgrade a portable framework release | [`.dev/releases/INDEX.MD`](.dev/releases/INDEX.MD) |

## Core Content

### Shared AI Collaboration Content

The shared content is intended for reuse across languages, frameworks, and product types. It covers:

- AI collaboration workflows, workflow gates, and handoff rules.
- Git commits, validation, requirements, specifications, ADRs, and review practices.
- Skill routing, sub-agent collaboration, and traceable execution boundaries.
- System and software architecture, along with conceptual guidance for DDD, Clean Architecture, and CQRS.

### .NET Backend Capability

The retained technology profile focuses on .NET / C# backend work, including:

- Backend project structures for Web APIs, workers, and consumers.
- Practical DDD, Clean Architecture, CQRS, Hexagonal Architecture, and message-driven backend guidance.
- Common backend combinations involving WolverineFx, Dapper, EF Core, PostgreSQL, RabbitMQ, and Kafka.
- Architecture design, implementation-slice, and code-review guidance for .NET backends.

## Main Directories

| Path | Purpose |
| --- | --- |
| `.ai/` | Agent-facing reusable AI context, canonical assets, scripts, and skill specs. |
| `.ai/assets/shared/` | Cross-stack prompt fragments, rules, and reusable materials. |
| `.ai/assets/tech-stacks/dotnet-backend/` | .NET C# backend Web API-specific context. |
| `.ai/assets/skills/` | Canonical skill specs and the skill registry. |
| `.ai/assets/sub-agent-role-prompts/` | Canonical source for sub-agent role prompts. |
| `.agents/skills/` | Codex and current-runtime skill wrappers. |
| `.claude/skills/` | Claude-compatible skill wrappers. |
| `.dev/` | Human-facing standards, guides, requirements, specifications, releases, and workflow records. |
| `.dev/releases/` | Release identities, compatibility declarations, and migration guidance. |
| `AGENTS.md` | Canonical root collaboration guide for Codex and general Agents. |
| `CLAUDE.md` | Thin Claude Code project-memory entry that imports `AGENTS.md`. |

## Adopting It in Another Repository

1. Obtain the appropriate portable AI context package from a published release instead of copying this entire source repository.
2. Install or upgrade it using that version's release and migration guide.
3. In the target repository, use `ai-context-init` first to inventory real files, configuration, and existing documents, then establish target-specific truth.
4. Preserve the target repository's own requirements, specifications, architecture, operations documents, and decisions; this source repository must not overwrite them.
5. Choose the relevant skill for the work at hand, such as requirements, specifications, architecture, implementation, test design, or code review.

For detailed migration and boundary rules, see [`migration-boundaries.md`](.ai/assets/skills/ai-context-init/references/migration-boundaries.md).

## Release Boundary

This repository is both the maintenance source and the build source for framework packages, but those scopes intentionally contain different files:

- Root README files, source-repository Agent entry files, historical workflows, assessments, release records, and product placeholders are source-only information and are never included in a downstream package.
- A portable package contains only reusable content named by the distribution profile's allowlist, with explicit exclusions providing a second protection boundary.
- As a result, editing this README improves the readability of the source repository only. It neither changes a published release nor makes the README eligible for inclusion in future packages.

## Language

- `README.md` is the Traditional Chinese (Taiwan) human-facing guide.
- `README.en.md` is the corresponding English version.
- Agent-facing context prefers English; human-facing guides may use Traditional Chinese (Taiwan). See [`.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`](.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md) for the full policy.
