# Short Assessment Identities

## Workflow Metadata

- `workflow_id`: `2026-09-12-short-assessment-ids`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-12-short-assessment-ids`
- `base_branch`: `main`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-12-short-assessment-ids`
- `created_at`: `2026-09-12T11:55:26+08:00`
- `updated_at`: `2026-09-12T12:19:45+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Authority

Implement [Issue 213](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/213) under the owner's 2026-09-12 authorization. Keep the suffix at three characters to limit path growth. Root owns integration and is the sole tracked writer. The separate Issue 21 reassessment remains conversation-only and does not authorize its implementation or closure.

This one-task workflow preserves the compatibility decision, cross-skill template changes and independent source admission needed before marking the changed future-agent behavior complete. It does not add tasks merely for test execution or commit bookkeeping. Transport, integration and provider closure remain separate.

## Acceptance Criteria

- AC1: New IDs use ASM-YYYYMMDD-HH-xxx with exactly three lowercase ASCII alphanumeric characters; old sequential allocation is retired for new IDs.
- AC2: Local date/hour bind to created_at; independent per-assessment random suffixes avoid deterministic same-HEAD identity reuse.
- AC3: Historical legacy IDs and shared artifacts remain valid and unchanged.
- AC4: Existing locator/index and commit identity consumers, templates and guidance agree; duplicate and reference checks remain effective.
- AC5: Focused new/legacy, same-hour and malformed/collision cases pass on Windows and POSIX without new coordination infrastructure.

## Scope And Validation

Update the assessment policy, existing identity parser/index matcher and commit extraction pattern; maintain current templates and instructions. Keep all historical assessment instances unchanged. Add focused tests for old/new identities, hour consistency, suffix syntax, duplicate rows, references and commit trailer binding. Use native Windows Python and the configured Ubuntu-24.04 POSIX route; preserve blocked or failed execution instead of relabeling it. Run current assessment, workflow and AI-context validators. Review one clean source commit independently; keep validation command receipts and terminal admission under declared ignored local artifacts.

No allocation service, remote reservation, graph-wide scanner, generator CLI, migration framework, source release or publication is part of this delivery.

## Local Completion

- `ASM213-001` is complete on repaired source `33c624f23ee9b74b4c39587185b780fb7c039ffa`. All five acceptance criteria pass.
- Native Windows and POSIX each have 15 passing assessment tests and 30 passing commit-policy tests. Unchanged assessment inputs retain proved reuse; the changed commit policy and tests were re-executed.
- Two failed independent reviews identified CR-001. The positive delimiter repair passed the third read-only source review; all earlier results remain evidence.
- Root will validate the completed workflow records, commit them and request one bounded final AI-context admission. No implementation remains pending.
- No push, PR, merge, Issue closure, Project change or release action is included. Issue 21 remains a conversation-only reassessment.
