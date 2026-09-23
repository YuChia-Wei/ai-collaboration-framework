# Issue #346 source checkpoint report

- Report: `remediation-report-2026-09-23-instruction-operations`.
- Owner: `ai-context-governance`; workflow: `2026-09-23-instruction-operations`.
- Created: `2026-09-23T09:47:52+08:00`; updated: `2026-09-23T13:31:22+08:00`; status: first-mapping-source-checkpoint; source checkpoint retained.
- Template source: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`; version `2.0.1`.
- Issue: [#346](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/346).
- Starting commit: `842b73ca09d701d1561109255193d80439dc996b`.
- Worktree/branch: `F:/framework-next/346`, `codex/2026-09-23-instruction-operations`.

## Source result and boundaries

Implemented selected D342-01/D342-02 in package loader, direct Codex consumers and
template; added the three-member common code-reviewer package. Exact semantics,
legacy method sources, member mapping handoff and proposed P7 cases are in the
[implementation note](../../../design/framework-next/instruction-operations/implementation.md).

`code-reviewer@0.1.0`: SKILL.md, skill-package.yaml, references/review.md. Public
operation `review` is instruction-driven. Configuration is null; no dependencies,
tools, schemas, templates or artifact roles. The method preserves correctness,
impact, evidence, test/GWT observability, uncertainty and target authority boundaries;
no .NET specialist coverage is delivered.

Only package.py, codex.py, selection.py, the Codex template, reviewer source and
owned design/workflow records change. Manifest/profiles, P3 packages, P4, other P5
packages, root/legacy assets and validators/tests remain under their existing owners.
No installed projection has been generated or activated by this source checkpoint.

## Checks and limitations

Actual permitted checks:

| Command or direct inspection | Observed result |
| --- | --- |
| Git root, branch, full HEAD, absolute common dir, porcelain status | Assigned identity matched; starting worktree clean. |
| `python -B -`: pathlib UTF-8, ast.parse, json.loads, yaml.safe_load, Markdown local-link existence | 12 UTF-8 files; 3 Python ASTs; 2 YAML; 1 JSON; 1 frontmatter; 14 existing local links. No product imports or pycache. |
| `python -B -`: AST literal keys and stdlib Template syntax/identifier inspection | Seven exact template/projection keys, valid template syntax; no template rendering or builder invocation. |
| Direct inventory and literal source-reference inspection | Reviewer has exactly three members; none contains source-only paths, U001 or program dependency text. |
| `git grep -n -F 'project_entry(' -- '*.py'` and direct distribution source read | One definition and one caller; selection supplies explicit configuration. Assembly only consumes source metadata/members and needs no change. |
| `git diff --check`, source diff and `git status --short --untracked-files=all` | No whitespace errors; exact assigned change scope inspected. |

The detailed file list and check observations are retained in the
[task](../tasks/ISSUE-346.json). The complete ignored message file passed
`python -B .ai/scripts/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-346-source.txt --workflow-id 2026-09-23-instruction-operations`.
`git check-ignore` confirmed its ignored location. Commit uses that exact file
with `git commit -F`; this message check is the explicit U001 exception. No product
module, CLI/help, schema validator, test, fixture, builder, installer or migration
was executed. The graph is a discovery hint only: fresh requested worktree index,
no SHA receipt, incomplete inbound call trace; fixed tracked source was used to
confirm direct call sites. An attempted adapter.yaml read found no such file;
the tracked adapter inventory resolved the actual single template path.

Initial sandbox GitHub read failed at the local proxy. A subsequent scoped network
read of the actual repository returned live Issue #346 OPEN and its assigned scope.
No retry with unchanged network context and no provider writes were performed.

## Deferred verification and remaining work

| Work | Disposition | Authority and owner | Next action |
| --- | --- | --- | --- |
| Product CLI/help, schema validation, tests/fixtures, build/package/install/migration/compatibility | deferred-by-owner | U001; program #322 coordinator / P7 | P7 selects redesigned checks after implementation. |
| Independent audit, lease, effective-rule or native handoff validation machinery | deferred-by-owner | U001; program #322 coordinator / P7 | P7 selects redesigned checks after implementation. |
| Hosted checks and CI | deferred-by-owner | U001; program #322 coordinator / P7 | P7 selects redesigned checks after implementation. |
| Exact manifest/profile mapping | awaiting-coordinator-handoff | Coordinator owns shared mapping assignment | Supply actual-source handoff to this same task after source checkpoint. |

No assessment findings are independently closed by this source implementation;
D342-01/D342-02 are implementation decisions, not invented finding IDs. The existing
ASM-20260923-00-6oq assessment remains unchanged. There is no independent verification
assessment or compatibility pass. Static parse success is syntax evidence only.

Workflow and task remain in_progress while mapping is pending. The coordinator
owns commit organization, first push, PR and online integration. Return a clean
coherent local source checkpoint and stop for that handoff. No new cross-contract
decision is currently unresolved; P7 behavioral risk and mapping assignment remain.

## First actual mapping continuation: blocked before write

The clean original source checkpoint was fast-forwarded once to the selected
`5986b2146bb4559609acb0d5c7d09e8570375ea8` handoff. Shared mapping is now assigned
in the coordinator's tracked scope, but has not been implemented in this worktree.
Automatic approval review rejected both write attempts before execution. The first
rejection cited untrusted coordinator transcript authorization; the second still
required direct user authorization after immutable Git and live Issue readback.
The four shared mapping files were not changed; no new engineering profile exists.

Direct YAML/content/Git inspection confirmed the following proposed comparison:

| Profile | Current payload members | Proposed payload members | Expected future runtime entries |
| --- | --- | --- | --- |
| lesson-minimal | 9 | 9 | 1 |
| knowledge | 26 | 26 | 3 |
| work-management | 18 | 28 | 3 |
| engineering | absent | 14 | 3 |
| collaboration | 44 | 68 | 9 |

The nine actual package metadata/member sets match tracked files and handoff counts:
lesson 9, adr 8, standards-promotion 9, pr 10, local-backlog 8,
software-development-orchestrator 10, code-reviewer 3, requirement-author 4,
spec-author 7. Existing five manifest closures/destinations match those sources;
lesson-minimal and knowledge raw bytes match the selected base. No loader, renderer,
builder or schema validator was invoked. Proposed counts do not describe built output.

Only issue-owned workflow records are updated to retain this block. Next action is
direct user authorization for the exact four shared mapping files, then continuation
in this same task. No alternate write route is attempted. Workflow/task remain
in_progress; all product verification stays deferred-by-owner under U001 to program
#322 coordinator / P7, which selects redesigned checks after implementation.

### Third request after forwarded direct owner confirmation

At clean base `4cda6689bf469a2273e14e237a0c3bf7ad4b6eed`, the new coordinator handoff
reported the owner's explicit confirmation of the original #346/#347 write scope.
One new scoped request was made for the same four mapping files. Automatic review
again rejected it before execution, specifically because the approval was forwarded
in transcript/file content rather than trusted direct user input in this task.
The prior two failures remain failures. No alternate write mechanism was attempted.

Refreshed direct YAML/Git member comparison confirms the nine selected source
closures still total 68 and match tracked members. Actual mapping is still five
packages/44 members/four profiles, and engineering.yaml is absent. Both protected
profile byte comparisons remain equal. Only four issue-owned workflow records
change to preserve this result. No product execution or additional package mapping
occurred. A direct user confirmation in this #346 task, or app-level resolution of
the approval restriction, is required before another request. All U001 deferrals
and the in_progress workflow state remain; no push or callback is performed.

## Current result: original nine-package mapping implemented

Observed at `2026-09-23T13:30:34+08:00` after the user's direct in-task approval. The exact write
request succeeded at base `7fab3ffd1698e2eb8ef791d6be7748f151506642`. Three previous
approval rejections remain historical failures; no failure was relabeled successful.
Only the original four product files were written: manifest.yaml, work-management.yaml,
collaboration.yaml and new engineering.yaml. Additional changes are this issue's
own design/workflow records. No loader, adapter, skill, other profile, root or index
was changed in this checkpoint. Later packages remain outside this selected batch.

| Package | Exact version | Metadata version | Explicit members |
| --- | --- | --- | --- |
| lesson | 0.2.0 | 2 | 9 |
| adr | 0.1.0 | 2 | 8 |
| standards-promotion | 0.1.0 | 2 | 9 |
| pr | 0.1.0 | 2 | 10 |
| local-backlog | 0.1.0 | 2 | 8 |
| software-development-orchestrator | 0.1.0 | 2 | 10 |
| code-reviewer | 0.1.0 | 3 | 3 |
| requirement-author | 0.1.0 | 3 | 4 |
| spec-author | 0.1.0 | 3 | 7 |

Total: nine packages, 68 explicit members. Each member maps to its unchanged
package-relative path under the corresponding managed core directory. Direct
metadata, Git-tracked-file and manifest comparisons match, including exact versions.

| Declared profile | Payload members | Expected unrendered Codex entries |
| --- | --- | --- |
| lesson-minimal | 9 | 1 |
| knowledge | 26 | 3 |
| work-management | 28 | 3 |
| engineering | 14 | 3 |
| collaboration | 68 | 9 |

Direct byte comparison confirms the five existing component rows and their 44
members are retained, and lesson-minimal/knowledge raw bytes are unchanged. Their
SHA-256 values are retained in the task. Manifest/profile versions remain 1; Codex
adapter selection is unchanged. These source counts are not built artifacts.

Actual checks: UTF-8/YAML parsing, metadata/tracked-member/destination/profile
comparison, preserved-byte comparison and git diff --check/content inspection.
The nine changed files passed direct UTF-8/syntax/reference readback: 5 YAML,
1 JSON and 17 local Markdown links. The complete ignored planned message passed
`python -B .ai/scripts/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-346-first-mapping.txt --workflow-id 2026-09-23-instruction-operations`;
commit uses those exact message bytes. No product loader, CLI/help, import, schema validation, test/fixture,
build/render/package/install/migration/probe, audit/lease/acceptance machinery or CI
was executed. All remain deferred-by-owner under U001, owner program #322 coordinator
/ P7; next action P7 selects redesigned checks after implementation.

Workflow/task stay in_progress for a later exact coordinator mapping handoff.
Current mapping is implemented; later packages, remote integration and downstream
adoption are separate. No push, PR, callback or provider mutation is performed.
