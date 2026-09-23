# Issue 354 source remediation report

- report_id: `remediation-report-2026-09-23-installation-planning`
- workflow_id: `2026-09-23-installation-planning`
- owner_skill: `ai-context-governance`
- template_source: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- template_version: `2.0.1`
- created_at: `2026-09-23T10:34:07+08:00`
- updated_at: `2026-09-23T10:39:14+08:00`
- status: `final`
- baseline_assessment: `ASM-20260923-00-6oq`
- verification_assessment: `deferred-by-owner` under U001

## Delivered source and scope

[Issue #354](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/354)
implements two issue-owned modules: actual candidate 1 / lock 1 readers and closed
read-only inspect/plan, exact old-member observations, strict ownership delta,
mode-only/no-op classification, bounded unknown preservation, selected byte-only
protected inputs, explicit roots/reader engine pin and conservative path budgets.
The [handoff](../../../design/framework-next/installation-planning/handoff.md)
specifies the exact API, serialized fields, dependency boundary, limits and P7 cases.

The original shared v1/v2/v3 package loader and reference checker are consumed,
not rewritten. Available payload/runtime/metadata bytes and cross-document
bindings are checked by the new source; external source/profile/generator claims
remain provenance. There is no source reproduction/authenticity claim and no
builder-format expansion or fetch. No schema file was added: the actual Python
readers own the closed formats/version refusal, with no unused validator facade.

No product function, CLI/help, build, test, fixture, schema validation, migration,
apply/recover or compatibility operation has been run. No shared file/index,
provider setting, Issue/Project state, credential, root route or downstream target
was changed. No sub-agent or executor-created conversation was used.

## Actual evidence and limitations

| Check/observation | Actual result and scope |
| --- | --- |
| Initial identity | Exact F:/framework-next/354 root, assigned branch, HEAD 5986b2146bb4559609acb0d5c7d09e8570375ea8, persistent C: common Git directory, clean porcelain. |
| Online Issue | #354 read back OPEN with matching body using read-only scoped escalation. |
| Graph discovery | Fresh fast index with persistence=false; no graph SHA attestation returned. Material facts came from native Git-tracked paths and direct source reads. |
| First direct syntax | Both new modules decoded as UTF-8 and parsed with AST; product never imported. |
| Subsequent direct syntax | Both modules re-parsed after changes; workflow JSON/YAML parsed directly. These are syntax observations only. |
| AST content inventory | Reader opens files only with rb; planner has no open call. The sole mutation-named AST match was string replace for path spelling, not file replacement. This is bounded source inspection, not a behavioral proof. |
| Changed local links | First pass 12; final pass 13 after adding the report handoff link, all within the assigned worktree. |
| Staged Git scope/diff | Exactly the 8 Issue-owned paths; `git diff --cached --check` passed. |
| Planned commit message | Allowed `validate-git-commits.py --message-file ... --workflow-id 2026-09-23-installation-planning` passed for the exact UTF-8/LF bytes; SHA-256 recorded in handoff.json. No history matrix. |

Retained unsuccessful attempts:

- Initial sandbox `gh issue view` failed because configured loopback proxy
  127.0.0.1:9 refused the network connection. The same read succeeded through the
  normal scoped escalation. No credentials/settings were changed.
- One exploratory read used nonexistent `src/distribution/source.py`; the actual
  tracked `git_source.py` was subsequently read. No source fact uses the missing path.
- First long source-write command could not start: Windows `os error 206`, command
  length. Bounded writes to the same assigned files succeeded. No other checkout
  or temporary worktree was used.

## Disposition and remaining owners

| Reference | Disposition | Owner and next action |
| --- | --- | --- |
| ASM-20260923-00-6oq / selected P6-B slice | Partially addressed by source; no assessment finding is declared behaviorally resolved. | Coordinator reconciles this source checkpoint with the larger program. |
| Candidate/lock/inspect/plan behavior and limits | deferred-by-owner; U001 | Program #322 coordinator / P7 selects and runs focused new checks before any pilot/use. |
| Full engine/bootstrap/import/resource closure and dependency provisioning | Separate later writer integration | Sole maintenance writer extends the reader closure coherently and binds the actual execution surface. |
| Native coordination, replacement, durability, operation/marker closure, apply/recover | Not implemented by this Issue | Sole maintenance writer implements, then P7 supplies actual platform/interruption evidence. |
| Config/data semantics, M01, project activation | Outside package planning | Capability/project owner selects real need/readers and activation independently. |
| Shared index row, push/PR/merge, Issue/Project disposition | Coordinator-owned | Collect local exact HEAD and changed paths; decide transport separately. |

The existing workflow/task/report templates are adapted under U001. Legacy
validators, tests/fixtures, build/install/migration/compatibility, native handoff
validation, independent audit/lease/effective-rule machinery and CI remain
`deferred-by-owner`, authority U001, owner program #322 coordinator / P7, next
select new bounded checks. A local source checkpoint or clean Git state is not a
behavior pass, hosted acceptance, installation outcome or readiness result.

## Local completion

The Issue-owned workflow/task is completed for the bounded source implementation
under U001, with verification assigned explicitly to P7. This does not close the
online Issue/Project or claim whole-program resolution. The containing commit of
[handoff.json](../handoff.json) is the local checkpoint identity; final task output
reports its full SHA, branch, clean status and exact changed paths. Coordinator
collects it read-only before first push. No cross-task callback is sent.

Actual command surfaces: direct `python -B -` scripts decoded the selected eight
files, used `ast.parse` for the two modules, `json.loads` / `yaml.safe_load` for
workflow records and resolved the changed Markdown file links. The scripts did
not import either product module. Git checks used `git diff --cached --check`,
`--stat` and `--name-only`; message validation used the full exact command retained
in handoff.json. Only default sample Git hooks were present; no settings changed.
