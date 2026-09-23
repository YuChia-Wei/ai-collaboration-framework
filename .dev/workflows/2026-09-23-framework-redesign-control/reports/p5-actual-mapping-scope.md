# First actual P4/P5 mapping handoff

Coordinator assignment to the SAME #346 task/worktree after source checkpoint `4795f7c1c6751a1702042ef76276f355e4ed7c37`. Source #346/#348 is online in PR #353 (`07b83383de467928701c8905c6bb0d5e8da8b246`); #341 source is online through PR #350. Only actual source enters this mapping. The containing coordinator checkpoint is the new exact fast-forward base; retain original source commit.

## Exclusive mapping files

- `src/distribution/manifest.yaml`: keep manifest_version 1 and Codex adapter; preserve existing five component rows; add four exact component closures below and one engineering profile registration.
- `src/profiles/work-management.yaml`: add only software-development-orchestrator 0.1.0 to existing PR/backlog.
- `src/profiles/collaboration.yaml`: all nine actual packages below at exact versions.
- New `src/profiles/engineering.yaml`: code-reviewer, requirement-author, spec-author 0.1.0 only, profile_version 1, Codex adapter. This is the currently delivered subset, not a claim to all engineering methods.
- Own instruction-operations design/workflow/report. No shared index, root or other source edits. lesson-minimal and knowledge bytes remain unchanged.

Every member maps `src/skills/<id>/<member>` to `.ai/core/skills/<id>/<member>` explicitly. Copy no source workflow/design/history. The adapter will later generate one exact `.agents/skills/framework-<id>/SKILL.md` per selected package; do not render/build now.

| Actual package | Metadata | Version | Exact member count |
| --- | --- | --- | --- |
| lesson | 2 | 0.2.0 | 9 |
| adr | 2 | 0.1.0 | 8 |
| standards-promotion | 2 | 0.1.0 | 9 |
| pr | 2 | 0.1.0 | 10 |
| local-backlog | 2 | 0.1.0 | 8 |
| software-development-orchestrator | 2 | 0.1.0 | 10 |
| code-reviewer | 3 | 0.1.0 | 3 |
| requirement-author | 3 | 0.1.0 | 4 |
| spec-author | 3 | 0.1.0 | 7 |

The five prior packages retain their exact 44 members. New four members come from actual metadata plus Git-tracked files:

- Workflow: SKILL.md, skill-package.yaml, references/configuration.md, operations.md, retention.md, composition.md, example.md (all five under references), schemas/workflow-record.schema.json, templates/workflow.md, scripts/workflow.py.
- Reviewer: SKILL.md, skill-package.yaml, references/review.md.
- Requirement: SKILL.md, skill-package.yaml, references/authoring.md, references/requirement-template.md.
- Specification: SKILL.md, skill-package.yaml, references/authoring.md, references/production-template.md, references/entity-template.md, references/adapter-template.md, references/formal-test-template.md.

Expected declared profile counts: lesson-minimal 9 + 1 runtime entry; knowledge 26 + 3; work-management 28 + 3; engineering 14 + 3; collaboration 68 + 9. These are direct source/count expectations, not built artifacts. No package dependency is added by a convenience profile; each source capability remains separately selectable through an explicit profile.

Do not include the five #347 packages or #351/#352 future work: no actual source is delivered yet. Return this coherent local mapping checkpoint, maintain #346 in_progress for the coordinator's disposition of later actual engineering mapping, and wait. Do not invent future rows or self-expand mapping. #341 can complete its bounded source/mapping Issue after this phase is actually integrated; P7 remains separate.

Allowed checks are direct YAML/content/member/reference/Git/diff and exact planned-message validation only. No import, product CLI/help, package loader/renderer/build or fixtures. Schema/behavior/tests/install/migration/CI remain deferred-by-owner under U001 to program #322 coordinator / P7. Coordinator owns first push and online integration.
