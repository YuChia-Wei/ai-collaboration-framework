# Source Layout Design Delivery Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.1`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-09-12T11:58:27+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-09-23-source-layout`
- `workflow_id`: `2026-09-23-source-layout`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-09-23T01:20:56+08:00`
- `updated_at`: `2026-09-23T01:20:56+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.1`
- `baseline_assessment`: `ASM-20260923-00-6oq` (design direction, not findings closed here)
- `verification_assessment`: `deferred-by-owner` under U001

## Remediation Summary

Delivered the design-only scope of #326 in six source-layout documents/examples and five workflow artifacts. No product/runtime/source-root relocation occurred. Completed the governance template's bounded design task; package/install/rollback correctness and all legacy gates remain unverified. Closure decision: `ready-with-deferrals` for local design delivery, not provider integration or Issue closure.

## Acceptance Resolution Matrix

The IDs below are Issue acceptance criteria, not invented assessment findings.

| Criterion | Status | Delivered content | Evidence/limit |
| --- | --- | --- | --- |
| AC1 | design-delivered | Ownership/input-output tables, exact five-member allowlist, source/project exclusion rules | Read content; no package executed |
| AC2 | design-delivered | One-skill edit -> immutable development selection -> install -> fix source sequence | Described future behavior, no CLI availability claim |
| AC3 | design-delivered | Whole replacement vs digest/mode delta; paired core/lock/runtime/config/record/index recovery | No migration/recovery trial |
| AC4 | design-delivered | Bounded P2 move/create list plus later P3-P7 inventory | Curated groups, not complete relocation manifest |
| AC5 | design-delivered | English design, mapping, three examples, zh-TW explanation, issue workflow and U001 deferrals | Actual files inspected and syntax checked |

## Changes And Evidence

- Design entry: `.dev/design/framework-next/source-layout/README.md`.
- Canonical design: `design.md`; inventory: `mapping-inventory.md` in the same subtree.
- Examples: `examples/distribution-manifest.example.yaml`, `examples/installation-plan.example.yaml`, `examples/layout.txt`; all explicitly unimplemented/non-executable.
- Issue workflow: locator, plan, `tasks/SL326-001.json`, this report and `handoff.yaml`.
- Names aligned through coordinator with P1-A: `lesson`, `lesson.record` / `1.0.0`, schema/template/operations member paths and `lesson.fs` planned/null. No P1-A schema or config copied.
- Initial branch/status read-back: clean `codex/2026-09-23-source-layout` at `53c9c8e58615e87e36f7b74ea8851fe845312daa`.
- `git rev-parse --git-common-dir` located the persistent Git database at `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git`; worktree files are on F:.

## Actual Checks

| Check | Observed result | Meaning |
| --- | --- | --- |
| Issue #326 via `gh issue view` | OPEN and acceptance read successfully with scoped network access | Scope observation only; no provider mutation |
| UTF-8 direct reads; `json.loads` / `yaml.safe_load` | Passed on the nine design/workflow files then present (one JSON, three YAML); final workflow metadata is reread before commit | Readability/syntax, not schema or runtime acceptance |
| Local Markdown link-target reads | Passed on links then present | Existing local documentation links resolve; P1-A future source paths are descriptions, not installed paths |
| Actual file-content inspection | Completed design, inventory, examples and zh-TW read-back | Self-review, not independent audit |
| `git diff --cached --check` | Passed on initial nine-file staged payload | Whitespace only; final staged payload is checked again before commit |
| `python .ai/scripts/validate-git-commits.py --message-file .dev/workflows/2026-09-23-source-layout/artifacts/commit-message.txt --workflow-id 2026-09-23-source-layout` | Passed for exact planned message | Explicit U001 format-check exception; no other legacy validator invoked |

Preparation history: the first sandboxed GitHub read failed against a local proxy; scoped network execution succeeded. A combined long authoring command exceeded the Windows process command-line limit and did not start; bounded per-file commands succeeded. A wildcard path read was corrected to an explicit file. None was a product validation attempt or a passed runtime check.

## Verification Assessment Reconciliation

No independent auditor or sub-agent was invoked. U001 defers validation-only audit machinery and legacy handoff/critical gates. No verification assessment or synthetic receipt was manufactured. The native handoff validator is not claimed satisfied; `handoff.yaml` is the explicit U001 adaptation.

## Deferred Work

| Work | Status / reason | Owner / next action |
| --- | --- | --- |
| Legacy validators, critical/check-all, test suites | deferred-by-owner, U001 | P7 redesign/select validation after development |
| Package builds, install/upgrade/migration trials and performance experiments | deferred-by-owner, U001 | P6 development and P7 validation; no current correctness/performance claim |
| CI and audit/admission machinery | deferred-by-owner, U001 | Coordinator/P7 restoration review; never call absent CI passed |
| Product moves, runtime/config edits and initial Lesson implementation | Outside P1-B design scope | P2, then P5/P6 under separate bounded Issues |
| Shared workflow index row and combined contract review | Coordinator-owned | Read `handoff.yaml` row and cross-review #325/#326 before integration |

## Closure Evidence

The task and workflow are complete for design delivery only. Resolve delivery commit with `git log -1 --format=%H -- .dev/workflows/2026-09-23-source-layout/handoff.yaml`, then compare to branch HEAD. Exact final HEAD and clean-status read-back are returned to coordinator after the commit. No push, PR creation, merge, Issue closure, release/tag, credential mutation or downstream adoption is performed.

No substantive contract conflict remains after name alignment. Coordinator review still selects the proposed tracked stable dogfood installation and generated Codex entry before implementation; no such root changes are made here. Final next action: coordinator cross-review, organize commits, then decide online integration under U001.
