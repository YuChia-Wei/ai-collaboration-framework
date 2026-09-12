# Short Assessment Identities

## Workflow Metadata

- `workflow_id`: `2026-09-12-short-assessment-ids`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-12-short-assessment-ids`
- `base_branch`: `main`
- `status`: `in_progress`
- `current_phase`: `post-audit`
- `artifact_root`: `.dev/workflows/2026-09-12-short-assessment-ids`
- `created_at`: `2026-09-12T11:55:26+08:00`
- `updated_at`: `2026-09-12T12:01:33+08:00`
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

## Resume Checkpoint

- Current task: `ASM213-001`.
- Last completed: current Issue read-back, refreshed clean main `92c1c6908593a85bc1b28256a8f6e7a316d9c756`, dedicated branch and writer lease.
- Next action: commit the validated source and obtain independent review.
- Blockers: none.
