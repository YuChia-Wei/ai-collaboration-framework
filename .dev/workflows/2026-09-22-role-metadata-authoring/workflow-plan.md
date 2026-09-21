# Author and migrate dynamic role metadata

## Workflow Metadata

- `workflow_id`: `2026-09-22-role-metadata-authoring`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-22-role-metadata-authoring`
- `base_branch`: `main`
- `status`: `in_progress`
- `current_phase`: `verification`
- `artifact_root`: `.dev/workflows/2026-09-22-role-metadata-authoring`
- `created_at`: `2026-09-22T07:16:55+08:00`
- `updated_at`: `2026-09-22T07:28:50+08:00`
- `branch_segment`: `1`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

Implement the first bounded P3 family from ASM-20260921-18-gav: guarded updates and the documented dynamic sub-agent metadata migration from 1.0 to 1.1. [Issue 318](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/318) owns this material scope. P1 and P2 remain immutable evidence; local base is 228bf4576610a4a07b8ca5d13d2b429edd0bf1af.

## Authorization

The owner instructed “continue P3” on 2026-09-22. Prior authorization permits local branch integration into main without hosted PR/CI transport for this stage. This is a task-local exception, not a repository policy amendment. Keep local validation truthful. Remote push, PR creation, Issue/Project closure, release/tag/publication and target adoption remain separate actions.

## Accepted Criteria

1. Deterministic preview and guarded update preserve unrelated and nested extension data.
2. Dynamic 1.0 to 1.1 conversion matches the historical transformation at 6aed5786033d404fdfe9eaa8961f51a071321b5f and preserves original bytes in the recovery journal.
3. Unknown versions, runtime reconciliation needs, protected identity/disposition edits, malformed records, missing owner/reference relationships and stale previews fail before writes.
4. Interrupted writes recover exact prior bytes; external changes and forged outputs are refused.
5. Canonical admission, existing gates/tests, CLI behavior and portable dependency closure remain intact.
6. Retain actual focused validation, independent fixed-subject verification and a Traditional Chinese explanation report.

## Execution Plan

ROLE-001 implements the family adapter and focused regression tests. ROLE-002 independently verifies the fixed implementation, retains evidence and completes local delivery. Root is the only tracked writer. Advisory explorers are read-only ordinary bounded analysis. Authority-sensitive independent review uses validated full-tier preparation and a snapshot lease.

## Discovery And Scope Decisions

The refreshed code graph explicitly excludes .ai/scripts and .ai/assets; selected code discovery uses Git-tracked evidence. No absence claim derives from the graph. Existing dynamic role migration changes only schema_version and adds adapter_metadata: {}. Historical promoted roles required explicit adapter paths and are not automatically convertible. Creation and owner-binding changes require coordinated semantics and are deferred. No validator or test is removed. All P3 families are not claimed complete.

## History

Initial branch creation in the filesystem sandbox failed because Git ref writes were denied. The authorized elevated local branch creation succeeded; no tracked edit preceded the dedicated branch. Issue 318 is open. Latest remote-main observation is 8830cdfc252b8845efcbe6cce539041c17cf8e7a; P1 and P2 are local only.

## Resume

Implement ROLE-001, then transfer to independent verification. Preserve baseline AIC-001 through AIC-005 dispositions in the remediation report; P4 removal remains deferred to the owner-approved later stage.
