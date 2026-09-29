# Non-Generic Context Classification

This artifact classifies `.ai` and `.dev` files by portability. It applies the rule that patterns and conceptual design can be universal, while implementation and code-planning details are non-universal or tech-stack-specific.

## Classification Values

| Class | Meaning | Preferred Location |
| --- | --- | --- |
| `universal-concept` | General AI collaboration, governance, or conceptual design reusable across stacks. | `.ai/assets/shared/` or `.dev/standards/` |
| `dotnet-backend-implementation` | .NET backend implementation, code generation, package, host, DI, persistence, messaging, or testing rules. | `.ai/assets/tech-stacks/dotnet-backend/` or `.dev/guides/*` |
| `repo-specific-truth` | Current repo architecture, requirements, operations, specs, problem frames, workflows, and runtime facts. | `.dev/` |
| `runtime-wrapper` | Runtime-specific skill wrapper entry. | `.agents/`, `.claude/` |
| `deferred-review` | Mixed or high-link-count file that should not move without a focused pass. | keep for now |

## `.ai` Classification

| Path | Class | Recommended Action | Notes |
| --- | --- | --- | --- |
| `.ai/README.MD` | universal-concept | keep | Agent-facing root entry, now English. |
| `.ai/INDEX.MD` | universal-concept | keep | Agent navigation entry. |
| `.ai/DIRECTORY-RULES.MD` | universal-concept | keep | Links to canonical boundary and language policies. |
| `.ai/SUB-AGENT-SYSTEM.MD` | deferred-review | split later | Contains general sub-agent system guidance plus .NET backend role inventory and frontend-sub-agent references. |
| `.ai/CODE-REVIEW-INDEX.MD` | dotnet-backend-implementation | move later | Index points to .NET backend review rules and should likely live under `tech-stacks/dotnet-backend` or be rewritten as generic. |
| `.ai/BUILDING-BLOCKS-CLASS-INDEX.MD` | dotnet-backend-implementation | move later | BuildingBlocks index is .NET backend-specific. |
| `.ai/CODE-TEMPLATES.MD` | dotnet-backend-implementation | move later | Code templates are implementation-specific. |
| `.ai/COMMON-PITFALLS.MD` | dotnet-backend-implementation | move later | Current pitfalls are tied to this backend architecture. |
| `.ai/FAILURE-CASES.MD` | dotnet-backend-implementation | move later | Current failures are tied to .NET backend implementation patterns. |
| `.ai/scripts/` | dotnet-backend-implementation | defer | Most scripts validate .NET backend rules; moving scripts needs path and invocation review. |
| `.ai/assets/shared/PROMPT-PORTABILITY-RULES.md` | universal-concept | keep | Cross-repo prompt hygiene. |
| `.ai/assets/tech-stacks/dotnet-backend/shared/` | dotnet-backend-implementation | keep | Correct home for .NET backend-only shared rules. |
| `.ai/assets/skills/` | mixed | defer | Skill specs include universal governance skills and .NET backend-specific implementer/review skills. |
| `.dev/agents/frontend-sub-agent/` | deferred-review | defer | Frontend role is out of the current backend-only profile; likely candidate for future full-stack template. |

## `.dev` Classification

| Path | Class | Recommended Action | Notes |
| --- | --- | --- | --- |
| `.dev/standards/AI-CONTEXT-BOUNDARY.md` | universal-concept | keep | General context governance. |
| `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md` | universal-concept | keep | General language policy. |
| `.dev/standards/GIT-COMMIT-POLICY.md` | universal-concept | keep | General agent-assisted commit policy. |
| `.dev/standards/WORKFLOW-GATE-POLICY.md` | universal-concept | keep | General workflow governance. |
| `.dev/standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` | universal-concept | keep | Conceptual application-layer relationship; .NET examples are acceptable but should remain minimal. |
| `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` | dotnet-backend-implementation | keep in `.dev/standards` | Execution standard for this backend profile. |
| `.dev/standards/CODE-REVIEW-CHECKLIST.md` | dotnet-backend-implementation | keep in `.dev/standards` | Canonical review standard for current profile. |
| `.dev/standards/coding-standards*` | dotnet-backend-implementation | keep | Backend implementation standards. |
| `.dev/standards/project-structure.md` | dotnet-backend-implementation | keep | Current repo profile structure. |
| `.dev/guides/design-guides/` | dotnet-backend-implementation | keep | Human-facing design guides for .NET backend. |
| `.dev/guides/implementation-guides/` | dotnet-backend-implementation | keep | Human-facing implementation guides for .NET backend. |
| `.dev/guides/learning-guides/` | mixed | keep | Human-facing learning material; evaluate individual files only when moving. |
| `.dev/requirement/` | repo-specific-truth | keep | Project requirements and tech stack facts. |
| `.dev/specs/` | repo-specific-truth | keep | Project behavior truth. |
| `.dev/operations/` | repo-specific-truth | keep | Runtime topology and runbook truth. |
| `.dev/problem-frames/` | repo-specific-truth | keep | Validation artifacts for current examples. |
| `.dev/workflows/` | repo-specific-truth | keep | Workflow artifacts. |

## Low-Risk Relocation Candidates

Do not move these in the same pass unless references are checked immediately:

- `.ai/CODE-REVIEW-INDEX.MD`
- `.ai/BUILDING-BLOCKS-CLASS-INDEX.MD`
- `.ai/CODE-TEMPLATES.MD`
- `.ai/COMMON-PITFALLS.MD`
- `.ai/FAILURE-CASES.MD`

Recommended destination:

```text
.ai/assets/tech-stacks/dotnet-backend/references/
```

## Deferred Decisions

- Whether to retire or move `frontend-sub-agent` should be a separate full-stack or frontend template decision.
- Moving `.ai/scripts/` requires a script invocation and path compatibility pass.
- Splitting `.ai/SUB-AGENT-SYSTEM.MD` requires careful role taxonomy work because it is both a system overview and a routing reference.
