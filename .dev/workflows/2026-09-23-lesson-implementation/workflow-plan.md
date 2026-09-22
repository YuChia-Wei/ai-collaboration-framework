# Lesson implementation workflow

- Workflow: `2026-09-23-lesson-implementation`
- Owner: `ai-context-governance`; Issue [#330](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/330)
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version `1.2.0`, adapted under U001.
- Created: `2026-09-23T01:51:34+08:00`; updated: `2026-09-23T01:58:20+08:00`.
- State: implementation completed; bounded task `LESSON-001`; verification deferred to P7.
- Worktree: `F:/framework-next/330`; branch `codex/2026-09-23-lesson-implementation`.
- Starting HEAD: `a1d8b750b8c81fd17697a39e04b55c35c4f3c4dc`.
- Persistent Git common database: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git`.

## Scope and authority

Implement the integrated P1 Lesson specimen under `src/skills/lesson/` and only
this workflow's records. U001, the temporary execution override, live Issue #330
and coordinator handoff bind this work. The older handoff's P1 subject
`b4d54966a0ed704d6b300b9f965976e27cd8512d` is design ancestry; the exact dispatch
starting commit above is the execution baseline. Dedicated branch was clean
before edits. Online Issue was read back open with no comments.

One independent conversation, dispatched as `gpt-6-astra` / `ultra`; this is
declared dispatch provenance, not an independent runtime attestation. No
sub-agents or child conversations. The existing governance skill's generic
production-code exclusion is narrowed by the explicit source-framework Issue
assignment; its workflow templates are retained proportionally.

Exclusions: root/runtime/distribution/shared files, legacy records, tests,
promotion/adoption/delete/import/migration, provider changes, push/PR/merge,
Issue closure, release and publication. No shared index writes.

## Completion criteria and stages

1. Create one package retaining the six P1 semantic members and declaring every
   additional member. Coordinator accepted `scripts/lesson.py` and
   `references/example.md`; metadata remains version 1 and no generic helper
   resource field is added. #331 owns assembly alignment.
2. Implement explicit config/project/package bindings, strict parsing, all seven
   candidate operations, actual related-query decisions, safe bounded writes,
   partial/cleanup/conflict truth and inert rendering.
3. Document exact requests/results, concrete unexecuted custom paths and product
   limits. Read source, parse Python via `ast.parse` without importing it, parse
   JSON/YAML, check links/scope/diff and full planned commit-message format.
4. Commit coherent source and handoff to the coordinator before first push.

## Verification disposition

All CLI execution (including help), behavioral tests, package/install/migration
trials, legacy validators except commit-message format, independent audits,
receipts and hosted checks are `deferred-by-owner` under U001. Responsible owner:
program #322 coordinator / P7. Next action: select and execute the new product's
focused checks at P7. Source inspection and syntax parsing do not satisfy them.

## Resume

`LESSON-001` implementation is complete. [Delivery report](reports/delivery.md)
and [handoff](handoff.yaml) preserve public interfaces, package members,
inspection evidence, limitations and deferred verification. Read the containing
commit identity and actual commit message before integrating. Coordinator owns
first push and #331 member alignment; P7 owns actual tool trials and redesigned
verification. No unresolved cross-contract choice is known. Local workflow
completion does not mean Issue closure, integration or tested behavior.
