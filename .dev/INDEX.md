# .dev Index

This index owns the file and directory catalog for `.dev/`. The `.dev/README.MD` file explains the folder purpose and boundary.

## Entry Documents

| Path | Description |
| --- | --- |
| `README.MD` | Purpose, scope, and usage of `.dev/`. |
| `INDEX.md` | File and directory catalog for `.dev/`. |
| `REPOSITORY-RENAME-COMPATIBILITY.md` | Source-repository rename migration risks, compatibility limits, and operational read-back guidance. |
| `TEAM-GIT-FLOW-RULES.MD` | Canonical single-trunk branch and merge policy: pull-request-only `main` integration, workflow-mode branches, checkpoint continuation, and default merge commits. |

## Standards

| Path | Description |
| --- | --- |
| `standards/README.md` | Standards purpose, scope, and placement boundary. |
| `standards/INDEX.MD` | Canonical standards catalog. |
| `standards/AI-CONTEXT-BOUNDARY.md` | AI context placement, boundary, and tool-neutral evidence policy. |
| `standards/AI-CONTEXT-LANGUAGE-POLICY.md` | Agent-facing and human-facing language policy. |
| `standards/AI-CONTEXT-VERSION-POLICY.md` | Stable compatibility route to the portable target version, provenance, and upgrade policy projection. |
| `standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md` | Source-only framework version-candidate, release-source status, tag handoff, hosted publication, and finalization validation policy. |
| `standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.md` | Source-only GitHub Issue/Project authority, workflow/main separation, and frozen legacy-backlog boundary. |
| `standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml` | Executable source work-management authority, freeze, and release-compatibility contract. |
| `standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml` | Single active source GitHub binding, merge-gate, and terminal-closure configuration. |
| `standards/WORKFLOW-GATE-POLICY.md` | Conversation, candidate-work, assessment, and authorized-execution workflow gate. |
| `standards/ASSESSMENT-ARTIFACT-POLICY.md` | Standalone assessment identity, storage, lifecycle, Git lookup, and workflow handoff contract. |
| `standards/GIT-COMMIT-POLICY.md` | Agent-assisted commit format and timing policy. |
| `standards/GIT-COMMIT-POLICY.yaml` | Machine-readable commit subject, workflow-section, assessment-ID, and AI-signature contract. |
| `standards/WORKFLOW-HANDOFF-POLICY.md` | Fail-closed receiving checkpoint and provider-attribution preservation policy. |
| `standards/WORKFLOW-HANDOFF-POLICY.yaml` | Machine-readable handoff vocabulary, output bounds, and read-only Git allowlist. |
| `standards/coding-standards/` | Legacy compatibility notices; old profile projections are unavailable here. |
| `standards/examples/` | Legacy examples compatibility notices; not an executable example catalog. |
| `standards/rationale/` | Rationale records for retained standards. |
| `standards/templates/` | Legacy templates compatibility notices. |

## Guides

| Path | Description |
| --- | --- |
| `guides/ai-collaboration-guides/` | AI collaboration, skill, prompt, workflow, and runtime wrapper guides. |
| `guides/design-guides/` | .NET backend design and context-placement guides. |
| `guides/implementation-guides/` | .NET backend implementation and setup guides. |

## Lessons

| Path | Description |
| --- | --- |
| `lessons/` | Evidence-backed, reusable, non-normative lessons derived from durable repository sources. |
| `lessons/README.MD` | Lesson responsibility, boundary, identity, lifecycle, promotion, and supersession contract. |
| `lessons/INDEX.MD` | Lesson category and lifecycle discovery catalog. |
| `lessons/environment/` | Host, shell, process-environment, and runtime-availability lessons. |
| `lessons/validation/` | Validation scheduling, immutable-snapshot, timeout-orchestration, and evidence-integrity lessons. |

## Requirements And Authoring Resources

| Path | Description |
| --- | --- |
| `requirement/` | Retained source requirement records. |
| `../.ai/core/skills/requirement-author/references/requirement-guide.md` | Managed requirement-authoring guide; not project requirements. |
| `../.ai/core/skills/spec-author/references/spec-guide.md` | Managed specification-authoring guide; not project specifications. |
| `../.ai/core/skills/spec-author/references/spec-organization-guide.md` | Managed specification-organization guide. |

## Problem-Frame Records

| Path | Description |
| --- | --- |
| `problem-frames/records/` | Project-owned problem-frame record destination; currently a tracked placeholder. |

## Operations

| Path | Description |
| --- | --- |
| `operations/` | Operations authoring guides and target-repo operations documentation area. |
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
| `../releases/` | Durable framework release identity, compatibility declarations, and migration guidance. |
| `../releases/README.MD` | Release directory purpose and boundary. |
| `../releases/INDEX.MD` | Published and planned release discovery view. |
| `standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md` | Source release preparation, tag immutability, hosted publication, and source/provider evidence gates. |
| `standards/AI-CONTEXT-VERSION-POLICY.md` | Portable installed-version identity, target provenance, and upgrade safety. |

## Durable Assessments

| Path | Description |
| --- | --- |
| `assessments/` | Durable audits, large code reviews, and other observations that do not by themselves authorize remediation. |
| `assessments/README.MD` | Assessment purpose and boundary guide. |
| `assessments/INDEX.MD` | Draft, final, superseded, and withdrawn assessment catalog. |
| `standards/ASSESSMENT-ARTIFACT-POLICY.md` | Assessment ID, locator, lifecycle, branch, commit, and handoff contract. |

## Historical References

The removed `.dev/backlog/` tree and `.ai/assets/skills/README.MD` remain
historical references only. Retrieve their compatible historical revision when
selected; this catalog does not imply those paths exist in the current tree.

## AI Runtime And Canonical Assets

| Path | Description |
| --- | --- |
| `../.ai/INDEX.MD` | Installed framework selection, generated core, and source-tooling data catalog. |
| `../src/skills/` | Editable product source for reusable framework skills. |
| `../.ai/core/skills/` | Generated installed skill payload shared by Codex and Claude. |
| `../.agents/skills/README.md` | Current original-ID Codex skill inventory and source-specific duties. |
| `../.claude/skills/README.md` | Current original-ID Claude skill inventory and source-specific duties. |
