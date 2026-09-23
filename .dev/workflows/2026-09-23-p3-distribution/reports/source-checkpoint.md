# Metadata v2 and P3 mapping source completion

## Template and report metadata

- `template_id`: `ai-context-governance-remediation-report`; `template_version`: `2.0.1`.
- Template timestamps: created `2026-07-10T18:22:49+08:00`; updated `2026-09-12T11:58:27+08:00`.
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`.
- `report_id`: `remediation-report-2026-09-23-p3-distribution-source`.
- `workflow_id`: `2026-09-23-p3-distribution`; `owner_skill`: `ai-context-governance`.
- `status`: `final`; `created_at`: `2026-09-23T08:33:01+08:00`; `updated_at`: `2026-09-23T09:12:38+08:00`.
- Baseline: `ASM-20260923-00-6oq`, program #322. No assessment finding is claimed verified-resolved.
- Verification assessment: `deferred-by-owner` under U001 to program #322 coordinator / P7.

## Scope and disposition

[Issue #337](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/337) first-stage source implementation is complete: explicit metadata 1/2 handling, schema-pair identities, closed readable/writable project roles and bounded same-document reference inspection in `src/distribution/package.py`. V1 keeps the existing named-schema and project-role contract. The [implementation note](../../../design/framework-next/distribution-implementation/metadata-v2.md) records exact semantics and limitations.

The initial loader checkpoint `13a08f3c886513cead3bfea080224f3323131977` retained an in-progress workflow while awaiting actual packages. The same-task continuation below completes the assigned mapping source scope; task and workflow are now `completed` under U001. Closure disposition: `ready-with-deferrals` for bounded source only. Runtime acceptance, Issue/Project closure and online integration remain separate P7/coordinator actions.

## Initial checkpoint observations (13a08f3c886513cead3bfea080224f3323131977)

| Observation | Actual result | Limit |
| --- | --- | --- |
| Assigned root/branch/HEAD/common-dir/status | F:/framework-next/337; codex/2026-09-23-p3-distribution; 0d0556d4c60105a28eb39cfb06efab9b069728cb; persistent C: common Git database; clean starting status | Local identity only |
| Live `gh issue view 337 --repo YuChia-Wei/ai-collaboration-framework --json number,title,body,state,url` | OPEN; title and scoped metadata-v2 implementation match dispatch | No provider mutation or acceptance claim |
| First restricted Issue read attempt | Failed: local proxy connection refused at 127.0.0.1:9; no provider response | Retained environment failure; scoped read with network permission then succeeded |
| Graph discovery | Non-persisted fast index of assigned F: worktree; load_package/check_references/select/assemble located | No reported index SHA; navigation only, not proof of completeness |
| Source identity | `git hash-object` matched `git ls-tree HEAD` for package.py, data.py, selection.py, assembly.py and tools/build-development.py before mutation | Exact tracked baseline; tools/ excluded by graph, narrow tracked-source fallback used |
| Source/call-site inspection | Selection uses exact metadata/member closure; assembly records actual metadata_version; no call-site change required | Static content reasoning only |
| `python -B -` with `ast.parse(Path(...package.py).read_text(encoding='utf-8'))` | AST parsed without product import or execution | Syntax only; no schema or behavior check |
| `git diff --check` after source edit | Exit 0 | Whitespace only |

Direct `python -B -` readability/reference inspection completed: 7 strict UTF-8 files, 1 JSON and 1 YAML parse, and 14 local Markdown links resolved. This used standard parsing libraries only, without repository imports or schema validation. The exact complete ignored message was checked with `python -B .ai/scripts/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-337.txt --workflow-id 2026-09-23-p3-distribution`: exit 0, `Git commit validation passed for planned message.` That result is only message-format evidence. Final staged scope and post-commit Git identity will be returned in the task handoff. No product CLI, builder, tests, schema validator, install/migration or audit machinery has run.

## Remaining work and verification

| Work | Disposition | Owner and next action |
| --- | --- | --- |
| Metadata/schema/reference behavioral checks and v1 compatibility | deferred-by-owner | U001, program #322 coordinator / P7: select focused cases from implementation note and execute on integrated immutable source |
| Builder/package/profile execution and actual candidate inspection | deferred-by-owner | U001, program #322 coordinator / P7: run only selected replacement checks after real mappings exist |
| Legacy validators except exact planned commit message, independent audits, review packets, leases, native handoff validation, CI | deferred-by-owner | U001, program #322 coordinator / P7: adopt and execute replacement gates; disabled CI is not a pass |
| Install/migration, benchmarks and high-I/O trials | deferred-by-owner | U001, program #322 coordinator / P7: select any necessary later trials |
| Exact actual P3 package mapping | completed source | Same task received actual integrated source and completed the 44-member/four-profile mapping below; runtime execution remains P7-owned |
| First push, PR, online merge, Issue/Project completion and shared indexes | coordinator-owned | Read local handoff; preserve checkpoints; do not infer completion from source commit |

## Actual package mapping continuation

The coordinator authorized the [exact mapping scope](../../2026-09-23-framework-redesign-control/reports/p3-package-mapping-scope.md). The assigned F: root/branch and clean original HEAD `13a08f3c886513cead3bfea080224f3323131977` matched. `git merge --ff-only 2bd7acdaf8a580df965396bdb9dbb8c05f6308af` succeeded and the new HEAD/status were read back. This preserves the original loader/design commits; no reset, rebase, extra worktree or task was used.

The [knowledge integration record](../../2026-09-23-framework-redesign-control/reports/p3-knowledge-integration.md), [work-management integration record](../../2026-09-23-framework-redesign-control/reports/p3-work-management-integration.md) and both owned interface inventories were read. Direct `python -B -` parsing with `git show <baseline>:<path>` and `git ls-tree -r <baseline> -- src/skills/<id>/` compared actual committed metadata, inventory declarations and regular Git files; a second direct comparison included the edited manifest and four profiles. No repository module or product entrypoint was imported or invoked.

| Package | Exact version | Git / metadata / interface / manifest members |
| --- | --- | --- |
| lesson | 0.2.0 | 9, equal |
| adr | 0.1.0 | 8, equal |
| standards-promotion | 0.1.0 | 9, equal |
| pr | 0.1.0 | 10, equal |
| local-backlog | 0.1.0 | 8, equal |
| Total | Five metadata-v2 packages | 44, no missing, extra or duplicate members |

Every destination preserves `.ai/core/skills/<id>/<member>`, every source is its exact `src/skills/<id>/<member>`, and all 44 source entries are regular Git blobs. Source/destination paths have no duplicate/case aliases in the compared inventory. The legacy Lesson schema remains exact blob `8bced2d86584c87d34f8ca2927aab95b7802a3ac`; both Lesson schema members are mapped. The existing codex adapter declaration is unchanged. All five required/optional dependency arrays remain empty.

| Profile | Exact selection | Package member count | Adapter |
| --- | --- | --- | --- |
| lesson-minimal | lesson@0.2.0 | 9 | codex |
| knowledge | lesson@0.2.0 + adr@0.1.0 + standards-promotion@0.1.0 | 26 | codex |
| work-management | pr@0.1.0 + local-backlog@0.1.0 | 18 | codex |
| collaboration | All five versions above | 44 | codex |

All four are exact integer `profile_version: 1` declarations and match the current assignment, including the intentional lesson-minimal 0.2.0 selection. The older interface inventory's proposed minimal-profile names do not override this later selected scope. These convenience selections do not introduce mandatory dependencies or claim release/installed capability.

Changed paths in this continuation are the manifest, four named profiles, distribution `metadata-v2.md`, and this workflow's locator, plan, task and report (10 files). No loader/skill/adapter code, root/runtime/core/custom, tests/CI, coordinator/shared index or installed output is changed. Direct `git diff` of excluded source paths was empty and `git diff --check` completed with exit 0 after the mapping edits. Final document/readability and exact message results are recorded below; no AST rerun was needed because this stage changes no code.

## Final limited-check results

Direct readability/reference inspection completed with exit 0: 10 strict UTF-8 files, 6 YAML documents, 1 JSON document and 15 local Markdown links. Fenced coordinator index-row text was excluded from local-link resolution because its links are relative to the shared index. The exact complete ignored mapping message was checked with `python -B .ai/scripts/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-337-mapping.txt --workflow-id 2026-09-23-p3-distribution`: exit 0, `Git commit validation passed for planned message.` This is message-format evidence only. Final staged scope/whitespace and post-commit Git identity are returned in the local handoff. Product CLI/help/select/build, schema validation, tests/fixtures, package/install/migration/compatibility trials, audits/leases and CI remain `deferred-by-owner`, U001, program #322 coordinator / P7. No candidate, digest, runtime projection, installed lock or receipt was produced.

## Handoff

Use the [completed source handoff](../workflow-plan.md) and [task record](../tasks/ISSUE-337.json). The containing completion commit identifies this mapping delivery; the final task handoff returns exact HEAD/branch/worktree and post-commit status. The prior `13a08f3c886513cead3bfea080224f3323131977` checkpoint remains an ancestor. No source-scope blocker or unresolved shared semantic decision was found in this mapping comparison. First push, PR/online merge and Issue/Project closure remain coordinator-owned.

Coordinator index row, relative to `.dev/workflows/INDEX.MD` (not applied by this executor):

```markdown
| [`2026-09-23-p3-distribution`](2026-09-23-p3-distribution/workflow.yaml) | P3 metadata v2 distribution support and actual package mapping | `ai-context-governance` | `completed` | `2026-09-23T09:12:38+08:00` | [plan](2026-09-23-p3-distribution/workflow-plan.md) |
```
