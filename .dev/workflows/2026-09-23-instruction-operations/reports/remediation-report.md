# Issue #346 source and mapping report

- Report: `remediation-report-2026-09-23-instruction-operations`.
- Owner: `ai-context-governance`; workflow: `2026-09-23-instruction-operations`.
- Created: `2026-09-23T09:47:52+08:00`; updated: `2026-09-23T14:17:17+08:00`; status: final-bounded-delivery; source checkpoint retained.
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

## First mapping result: original nine-package mapping implemented

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

## Final bounded source/mapping delivery

Recorded at `2026-09-23T14:16:17+08:00` on clean starting base `34400e0ff377301601be5b7e167ed9e05261830c`.
The [final handoff](../../2026-09-23-framework-redesign-control/reports/p5-final-mapping-scope.md)
selected the already integrated actual package source. One scoped write request
succeeded for exactly manifest.yaml, engineering.yaml, collaboration.yaml, new
source-repository.yaml and new context-maintenance.yaml. Own design/workflow records
are the only additional changes. Earlier refused attempts remain in history and
are not reclassified as successes; no new failure occurred in this mapping write.

| Additional actual package | Version / metadata | Members |
| --- | --- | --- |
| diagnostic-analyst | 0.1.0 / 3 | 3 |
| ddd-ca-hex-architect | 0.1.0 / 3 | 4 |
| bdd-gwt-test-designer | 0.1.0 / 3 | 4 |
| local-change-implementer | 0.1.0 / 3 | 3 |
| slice-implementer | 0.1.0 / 3 | 9 |
| problem-frame-author | 0.1.0 / 3 | 10 |
| spec-compliance-validator | 0.1.0 / 3 | 6 |
| ai-context-auditor | 0.1.0 / 3 | 3 |
| ai-context-governance | 0.1.0 / 3 | 3 |

The additional nine closures/45 members plus the original nine/68 total
**18 components / 113 members**. Direct metadata, tracked-file and manifest-member
sets match for every component. Exact destinations retain each package-relative
member path; no design/workflow/history source is included. Lesson stays 0.2.0 and
all other selected package versions are 0.1.0. No skill/tool/loader/adapter code changed.

| Final declared profile | Packages / expected unrendered Codex entries | Payload members |
| --- | --- | --- |
| lesson-minimal | 1 | 9 |
| knowledge | 3 | 26 |
| work-management | 3 | 28 |
| engineering | 10 | 53 |
| collaboration | 16 | 107 |
| source-repository | 15 | 99 |
| context-maintenance | 2 | 6 |

All profile/manifest versions remain 1 with Codex only. Ordinary profiles exclude
both optional context packages. Source-repository is collaboration minus local-backlog.
These are complete selections: context-maintenance is **not an overlay**, sequential
apply does **not** union selections and may remove earlier managed files. No combined
profile is introduced. No application, root activation or installation occurred.

The original nine component rows remain byte-identical. All existing profile
registration rows and the Codex adapter are preserved. Protected profile bytes match
these unchanged Git blobs:

| Protected profile | Git blob |
| --- | --- |
| lesson-minimal | `540645382e5b40ae79e0069bf2ee5f36cd816761` |
| knowledge | `8061bd801cc6065f9997b912694859979a1715b5` |
| work-management | `0599e6a1ce14144ac0b145f7996e8cf8a0dea839` |

Actual evidence includes direct UTF-8/YAML/content/member/profile/Git comparison,
10 changed UTF-8 files, 6 YAML documents, 1 JSON document, 20 existing local Markdown
links and git diff --check. The complete ignored planned message passed
`python -B .ai/scripts/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-346-final-mapping.txt --workflow-id 2026-09-23-instruction-operations`;
commit uses that exact message file.
These are not schema, behavior, compatibility or independent-review passes.
Product CLI/help/import, schema validation, tests/fixtures/build/render/package/
install/migration/probes, audit/lease/acceptance machinery and CI remain
**deferred-by-owner**, authority **U001**, owner **program #322 coordinator / P7**;
next action **P7 selects redesigned checks after implementation**.

The owned workflow/task are completed for bounded source/mapping only. No source
implementation remains here. The coordinator receives the coherent local commit
and owns remote integration and provider Issue closure; no push, PR or callback
is performed. Full verification and downstream adoption remain separate decisions.
