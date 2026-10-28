# Project Knowledge Index

`.dev` contains records, standards and collaboration for this framework source
project. [README.MD](README.MD) explains the boundary. Use current paths below;
historical paths in retained records do not establish current availability.

## Source Collaboration

| Entry | Purpose |
| --- | --- |
| [Standards](standards/INDEX.MD) | Current source policies and selected legacy obligations |
| [Source development](standards/SOURCE-DEVELOPMENT-POLICY.md) | Ordinary execution, checks and conditional independent review |
| [Daily workflow storage](standards/WORKFLOW-STORE-POLICY.md) | SQLite-only daily records, explicit configuration/source CLI, continuation, backup and retained Board replica history |
| [Contracts](contracts/README.md) | Source execution, provider bindings and record interpretation |
| [Git flow](TEAM-GIT-FLOW-RULES.MD) | Source branch/integration rules under adopted source policy |
| [Repository rename](REPOSITORY-RENAME-COMPATIBILITY.md) | Repository/package identity and compatibility limits |
| `ai-context/environment-policy.yaml` | Source runtime/environment selection |
| [Skill responsibility history](guides/ai-collaboration-guides/SKILL-RESPONSIBILITY-CHANGES.md) | Source decisions and experience |
| [Release draft guide](guides/implementation-guides/FRAMEWORK-RELEASE-DRAFT-GUIDE.md) | Source draft/package procedure; publication has separate authority |

## Project Records

| Path | Purpose |
| --- | --- |
| `design/` | Source design records |
| [Framework-next historical design](design/framework-next/README.md) | Historical redesign decisions and retained obligations; current product navigation is separate |
| [Skill evolution design (2026-10-22)](design/skill-evolution-2026-10-22/README.md) | Authorized domain/software split: complete design, responsibility contracts, source mapping and references; local workflow/customization are separate future work |
| [Workflow 0.22.0 design](design/workflow-0220-2026-10-25/design.md) | Issue 483 design: optional local work items, selected Board platform, migration and multi-carrier contract; remaining owner choices explicit |
| `requirement/` | Source requirement records |
| `adr/` | Architectural decisions |
| `assessments/` | Durable observations and their evidence |
| `workflows/` | Historical/pre-cutover Git execution locators and handoffs; current discovery follows the store policy |
| [Domain/software split](workflows/2026-10-22-domain-architecture-split/workflow-plan.md) | Historical Git record of design review, Issues 476-480, authorized source work and validation |
| [Workflow 0.22.0 records and Board V2 query adapter](workflows/2026-10-25-workflow-0220-design/workflow-plan.md) | Pre-cutover Git record of bounded design, SQLite and Board increments, tests, plugin queries and review; native continuation acceptance is recorded separately |
| [Lessons](lessons/INDEX.MD) | Evidence-backed experience; not independent normative authority |

Existing design/requirement/ADR/assessment/workflow contents are excluded from
this cleanup. New authorized execution uses the selected native identity and
entrypoint; formal artifact locators remain with their Git-owned families. Removed legacy backlog,
operations and release-navigation roots are not current routes; select the
compatible historical revision for an actual retained duty.

## Product And Installed Resources

| Entry | Purpose |
| --- | --- |
| [Product manuals](../docs/README.md) | Installation, component selection, use and limitations |
| [Document maintenance](../docs/maintaining-documentation.md) | Product documentation ownership and authoring |
| `../src/skills/`, `../src/knowledge/`, `../src/sub-agents/` | Editable reusable product sources |
| [Engineering methods](../src/knowledge/engineering-common/README.md) | Source-owned reusable context and engineering methods |
| `../.ai/core/` | Managed installed resources; update through selected installation |
| `../.ai/project/` | This project's AI settings, selections and resources |
| [Installed context index](../.ai/INDEX.MD) | Generated selection and installed state |
| `../.agents/skills/`, `../.claude/skills/` | Managed runtime skill entries |
