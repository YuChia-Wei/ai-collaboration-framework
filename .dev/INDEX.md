# .dev Index

This index owns the file and directory catalog for `.dev/`. The `.dev/README.MD` file explains the folder purpose and boundary.

## Entry Documents

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.dev/`. |
| `INDEX.md` | File and directory catalog for `.dev/`. |
| `ARCHITECTURE.md` | Framework repository architecture and context model. |
| `TEAM-GIT-FLOW-RULES.MD` | Canonical single-trunk branch and merge policy: pull-request-only `main` integration, workflow-mode branches, checkpoint continuation, and default merge commits. |

## Standards

| Path | Description |
| --- | --- |
| `standards/README.md` | Standards purpose, scope, and placement boundary. |
| `standards/INDEX.MD` | Canonical standards catalog. |
| `standards/AI-CONTEXT-BOUNDARY.md` | AI context placement, boundary, and tool-neutral evidence policy. |
| `standards/AI-CONTEXT-LANGUAGE-POLICY.md` | Agent-facing and human-facing language policy. |
| `standards/AI-CONTEXT-VERSION-POLICY.md` | Framework SemVer, immutable release, target provenance, and upgrade safety policy. |
| `standards/WORKFLOW-GATE-POLICY.md` | Conversation, candidate-work, assessment, and authorized-execution workflow gate. |
| `standards/ASSESSMENT-ARTIFACT-POLICY.md` | Standalone assessment identity, storage, lifecycle, Git lookup, and workflow handoff contract. |
| `standards/GIT-COMMIT-POLICY.md` | Agent-assisted commit format and timing policy. |
| `standards/GIT-COMMIT-POLICY.yaml` | Machine-readable commit subject, workflow-section, assessment-ID, and AI-signature contract. |
| `standards/WORKFLOW-HANDOFF-POLICY.md` | Fail-closed receiving checkpoint and provider-attribution preservation policy. |
| `standards/WORKFLOW-HANDOFF-POLICY.yaml` | Machine-readable handoff vocabulary, output bounds, and read-only Git allowlist. |
| `standards/coding-standards/` | .NET backend coding standards by component type. |
| `standards/examples/` | Reusable .NET backend examples and templates. |
| `standards/rationale/` | Rationale records for retained standards. |
| `standards/templates/` | Reusable standards templates. |

## Guides

| Path | Description |
| --- | --- |
| `guides/README.MD` | Purpose and usage of `.dev/guides/`. |
| `guides/INDEX.MD` | File and directory catalog for guides. |
| `guides/ai-collaboration-guides/` | AI collaboration, skill, prompt, workflow, and runtime wrapper guides. |
| `guides/design-guides/` | .NET backend design and context-placement guides. |
| `guides/implementation-guides/` | .NET backend implementation and setup guides. |
| `guides/learning-guides/` | Learning path and new-project guidance. |

## Lessons

| Path | Description |
| --- | --- |
| `lessons/` | Evidence-backed, reusable, non-normative lessons derived from durable repository sources. |
| `lessons/README.MD` | Lesson responsibility, boundary, identity, lifecycle, promotion, and supersession contract. |
| `lessons/INDEX.MD` | Lesson category and lifecycle discovery catalog. |
| `lessons/environment/` | Host, shell, process-environment, and runtime-availability lessons. |

## Requirements And Specs

| Path | Description |
| --- | --- |
| `requirement/` | Requirements and requirement authoring materials. |
| `requirement/REQUIREMENT-GUIDE.MD` | Requirement authoring guide. |
| `requirement/TECH-STACK-REQUIREMENTS.MD` | Tech stack requirements for the framework profile. |
| `specs/` | Spec authoring and test-spec guidance for this framework. |
| `specs/README.MD` | Purpose and usage of `.dev/specs/`. |
| `specs/INDEX.MD` | File and directory catalog for specs. |
| `specs/SPEC-GUIDE.MD` | Spec authoring guide. |
| `specs/SPEC-ORGANIZATION-GUIDE.MD` | Spec organization guide. |
| `specs/tests/` | Test-spec storage guidance and examples. |

## Domain Language And Problem Frames

| Path | Description |
| --- | --- |
| `domain-language/` | Domain language templates and target-repo vocabulary area. |
| `domain-language/templates/` | Bounded context, aggregate vocabulary, and domain event language templates. |
| `problem-frames/` | Problem-frame authoring guidance and templates. |
| `problem-frames/INDEX.md` | File and directory catalog for problem-frame assets. |
| `problem-frames/templates/` | Reusable CBF/SWF problem-frame templates. |

## Operations

| Path | Description |
| --- | --- |
| `operations/` | Operations authoring guides and target-repo operations documentation area. |
| `operations/README.MD` | Purpose and usage of `.dev/operations/`. |
| `operations/CONTEXT-MAP-GUIDE.MD` | Context-map authoring guide. |
| `operations/EVENT-CATALOG-GUIDE.MD` | Event-catalog authoring guide. |
| `operations/MQ-TOPOLOGY-GUIDE.MD` | MQ topology authoring guide. |
| `operations/RUNBOOK-GUIDE.MD` | Runbook authoring guide. |
| `operations/runbooks/` | Runbook folder and runbook index. |
| `operations/runbooks/AI-CONTEXT-RELEASE-PUBLICATION-RUNBOOK.MD` | Cold-start governed AI context candidate, tag handoff, publication, and finalization procedure. |

## Workflow Records

| Path | Description |
| --- | --- |
| `workflows/` | Workflow discovery locators and default artifact roots. |
| `workflows/README.MD` | Workflow discovery, ownership, and artifact-root guidance. |
| `workflows/INDEX.MD` | Active, completed post-adoption, and legacy workflow discovery view. |
| `workflows/handoff-checkpoints.yaml` | Registry of durable machine-readable receiving checkpoints. |
| `standards/WORKFLOW-ARTIFACT-POLICY.md` | Shared workflow locator, ID, timestamp, and minimum task contract. |

## AI Context Releases

| Path | Description |
| --- | --- |
| `releases/` | Durable framework release identity, compatibility declarations, and migration guidance. |
| `releases/README.MD` | Release directory purpose and boundary. |
| `releases/INDEX.MD` | Published and planned release discovery view. |
| `standards/AI-CONTEXT-VERSION-POLICY.md` | Version selection, tag immutability, provenance, upgrade, and publication gates. |

## Durable Assessments

| Path | Description |
| --- | --- |
| `assessments/` | Durable audits, large code reviews, and other observations that do not by themselves authorize remediation. |
| `assessments/README.MD` | Assessment purpose and boundary guide. |
| `assessments/INDEX.MD` | Draft, final, superseded, and withdrawn assessment catalog. |
| `standards/ASSESSMENT-ARTIFACT-POLICY.md` | Assessment ID, locator, lifecycle, branch, commit, and handoff contract. |

## Durable Backlog

| Path | Description |
| --- | --- |
| `backlog/` | Cross-workflow durable work items that must remain discoverable outside execution records. |
| `backlog/README.MD` | Backlog ownership, state, and workflow-handoff contract. |
| `backlog/INDEX.MD` | Current durable backlog catalog. |

## AI Runtime And Canonical Assets

| Path | Description |
| --- | --- |
| `../.ai/INDEX.MD` | Agent-facing reusable AI asset catalog. |
| `../.ai/assets/skills/README.MD` | Canonical skill registry entry. |
| `../.agents/skills/README.md` | Current runtime wrapper index. |
| `../.claude/skills/README.md` | Claude-compatible wrapper index. |
