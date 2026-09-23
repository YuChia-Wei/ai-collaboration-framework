# Instruction operations workflow

- Workflow: `2026-09-23-instruction-operations`; owner: `ai-context-governance`.
- Issue: [#346](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/346).
- Status: `in_progress`; phase: mapping selected but write blocked by automatic approval review.
- Created: `2026-09-23T09:47:04+08:00`; updated: `2026-09-23T11:56:40+08:00`.
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`; version `1.2.0`.
- Branch: `codex/2026-09-23-instruction-operations`; base branch: `main`.
- Worktree: `F:/framework-next/346`; exact starting commit: `842b73ca09d701d1561109255193d80439dc996b`.
- Common Git directory: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git`.

## Authority and bounded outcome

Use [U001](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md), the
[execution plan](../../assessments/ASM-20260923-00-6oq/execution-plan.md),
[selected P5 contract](../../design/framework-next/p5-selected-contract.md) and
[coordinator assignment](../2026-09-23-framework-redesign-control/tasks/ISSUE-346.json).
Live Issue #346 was read as OPEN and confirmed this scope. The initial sandboxed
GitHub read failed at the local proxy; the scoped network read succeeded. No
provider state was changed.

Deliver metadata-v3 source semantics, direct Codex consumers and exactly three
portable code-reviewer members as one source slice. Preserve v1/v2 and P3 source.
Observable source criteria and future P7 cases are recorded in the
[implementation note](../../design/framework-next/instruction-operations/implementation.md).
The package does not depend on that note or any source-only authority.

One task records the two-stage source then mapping handoff. This workflow preserves
an independently resumable coordinator ownership boundary: source can be handed
off while exact mapping remains unassigned. It is not padded with audit tasks.
The owning templates are adapted proportionally under U001; legacy schema, audit,
lease, effective-rule and native handoff compliance is not asserted.

## Execution and ownership

Declared dispatch: one independent `gpt-6-astra` / `ultra` conversation, no agents or
new conversations. This records the coordinator's selection, not independent
runtime attestation. All repository commands use the assigned F: workdir and all
edits use absolute paths in that worktree. Preserve other worktrees and F:/ai-context-tests.

Own only shared package loader, necessary distribution consumers, Codex template,
`src/skills/code-reviewer/`, this workflow and its instruction-operations design.
The coordinator owns other package sources, manifest/profiles until explicit
handoff, indexes/root activation and first push. No remote write, root cutover,
release, deletion, credentials/settings change or downstream adoption is authorized.

## Stages and resume

1. Inspect live authority and exact assigned Git identity: completed.
2. Implement the source vertical slice and record direct syntax/content/reference
   and Git checks: completed as syntax/content evidence only.
3. Create the coherent local source commit and return full HEAD, scope, package members/public
   operations and deferrals to coordinator `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`.
4. Stop at local checkpoint. Keep workflow/task in_progress for the exact mapping
   handoff in this same conversation. Do not infer mapping scope from future rows.

Coordinator later reported P5 design integrated through PR #349 at main
`5079fdf8e92e281cee0d5b9d26e6a1c9afa4166a`. This is dependency information only;
it does not change this worktree's assigned base or authorize merge/rebase.

All product execution, schema validation, tests/fixtures, package/install/migration,
compatibility, audits/leases/effective-rule machinery and CI: `deferred-by-owner`;
authority U001; owner program #322 coordinator / P7; next action P7 selects redesigned
checks after implementation. Only direct UTF-8/content/JSON/YAML/AST parsing without
product imports or pycache, reference/Git/diff and exact planned commit-message
format checks are performed now.

Integration gate remains GitHub PR under coordinator ownership. A retained source
handoff favors preserving the checkpoint boundary; the coordinator selects final
commit organization and topology before first push. No local commit is remote
integration or Issue closure. Current evidence and next action live in the
[task](tasks/ISSUE-346.json) and [report](reports/remediation-report.md).

## First mapping handoff and approval block

Source checkpoint `4795f7c1c6751a1702042ef76276f355e4ed7c37` was retained. On the
coordinator's exact continuation instruction, the assigned clean branch was
fast-forwarded once to `5986b2146bb4559609acb0d5c7d09e8570375ea8`. The
[first actual mapping scope](../2026-09-23-framework-redesign-control/reports/p5-actual-mapping-scope.md)
and updated coordinator task/P5 contract select four mapping files and nine
actual packages. No further merge/rebase or source changes were performed.

The shared mapping write was rejected before execution by automatic approval
review. After reading the immutable handoff/commit and live Issue #346, a second
attempt was also rejected: the reviewer requires trusted direct user authorization
for the shared manifest/profile change and treats tool output/coordinator transcript
as insufficient. Neither attempt changed a mapping file. This is an approval block,
not a metadata/schema/product failure. Do not retry or use another write mechanism
without resolving that authorization requirement.

Read-only YAML/member/Git comparison found nine actual package closures matching
metadata and tracked paths: existing 44 plus proposed 24 = 68 members. Current
lesson-minimal and knowledge bytes are unchanged. Proposed counts remain unbuilt
expectations: 9+1, 26+3, 28+3, 14+3, 68+9 payload/runtime entries for lesson-minimal,
knowledge, work-management, engineering and collaboration respectively.

Next action: obtain direct user approval for only manifest.yaml, work-management.yaml,
collaboration.yaml and new engineering.yaml under the exact selected scope; then
resume mapping in this same task. Until then, mapping is not implemented. Keep
workflow/task in_progress. No callback, push, PR or CI action is requested; the
coordinator will read the final result. All U001 verification deferrals remain.

### Owner-confirmed resumption: third write still rejected

The coordinator supplied the owner's new direct reply, recorded in
[owner-confirmed resume](../2026-09-23-framework-redesign-control/reports/p5-owner-confirmed-resume.md),
and advanced this same branch to `4cda6689bf469a2273e14e237a0c3bf7ad4b6eed`.
This task read back the exact root/branch/HEAD/common Git directory and clean state.
One new scoped request for the original four mapping files was made after this
material authority change. Automatic review rejected it before execution because
it required trusted direct user authorization in this conversation and did not
accept forwarded transcript/file content. Earlier rejections remain unchanged.

Fresh direct metadata/tracked-member comparison again confirms the selected nine
packages/68 members exist, while the actual manifest remains five/44 with four
profiles and no engineering.yaml. lesson-minimal and knowledge bytes are unchanged.
Only this task's workflow records are updated. Next action: the user confirms the
four-file mapping directly in task `01a0cbeb-c1c8-7ba1-a0c8-de9026a355ff`, or resolves
the approval restriction through the app. Do not retry, change writer or bypass the
rejection. No callback or provider write is performed. U001 deferrals remain.
