# P3 distribution workflow

## Template and workflow metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- Template timestamps: created `2026-07-10T18:22:49+08:00`; updated `2026-07-13T23:11:56+08:00`.
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `workflow_id`: `2026-09-23-p3-distribution`
- `workflow_kind`: `ai-context-maintenance`; `owner_skill`: `ai-context-governance`.
- Branch: `codex/2026-09-23-p3-distribution`; base: `main`; segment: `1`.
- `status`: `in_progress`; `current_phase`: `remediation`.
- Artifact root: `.dev/workflows/2026-09-23-p3-distribution`.
- `created_at`: `2026-09-23T08:33:01+08:00`; `updated_at`: `2026-09-23T08:34:41+08:00`.

## Authority, objective and scope

[Issue #337](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/337), the coordinator's explicit implementation dispatch and [P3 selected contract](../../design/framework-next/p3-shared-contract.md) authorize metadata v2 source support while preserving metadata v1. [U001](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md) governs this source-only work. Live Issue read-back found it OPEN with the assigned first-stage scope; provider state is not implementation acceptance.

First stage owns `src/distribution/package.py`, necessary direct distribution call sites, the distribution-implementation design and this workflow. Source inspection found no necessary call-site changes. No skill source, manifest/profile, root runtime, legacy tools, shared index or coordinator record is changed. No provider mutation, first push, publication, release, adoption or credential change is assigned to this executor.

The one-task workflow preserves the first local source handoff and independently resumable second mapping stage. Its unique state is the dependency on actual #334/#335 delivery and the coordinator's later exact mapping dispatch. No placeholder task is created for suspended auditing.

## Observable completion criteria

1. Explicit integer metadata 1/2 handling with the original v1 closed fields and single-schema-ID behavior.
2. V2 schemas unique by exact `(id, version)` with distinct contained member paths; cross-kind IDs still unique.
3. Every v2 project role has one writable `schema` and nonempty unique declared `read_schemas` including that writable identity. Derived roles and other closed fields stay unchanged.
4. V2 schema references inspect only finite same-document `#/$defs/` pointers; no resolver, schema execution, external retrieval or skill import. Existing package-relative document checks remain.
5. Later exact manifest/profile mappings use real integrated package members and independently select the five P3 packages. This criterion remains unfinished at the first source checkpoint.
6. Record actual permitted checks and all U001 verification deferrals; hand coherent local commits to the coordinator before push.

Source implementation and direct syntax inspection do not establish behavioral satisfaction of these criteria. P7 owns runtime verification.

## Artifacts and stages

- Task: [ISSUE-337](tasks/ISSUE-337.json), `in_progress` across both implementation stages.
- Report: [source checkpoint](reports/source-checkpoint.md), a draft report for the unfinished workflow.
- Contract: [metadata v2 implementation](../../design/framework-next/distribution-implementation/metadata-v2.md).
- Stage 1: loader source implementation, limited checks and local commit handoff.
- Stage 2: after actual #334/#335 integration and coordinator dispatch, reconcile exact members and add authorized manifest/profile mappings in this same task.
- Behavioral/schema/package testing, independent audit, native handoff validation and CI: `deferred-by-owner`, U001, program #322 coordinator / P7. Next action: P7 selects and executes replacement checks on the integrated immutable subject. No audit packet or lease is fabricated.

## Resume checkpoint

- Assigned worktree: `F:/framework-next/337`.
- Starting HEAD: `0d0556d4c60105a28eb39cfb06efab9b069728cb`; starting status clean.
- Common Git directory: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git` (existing persistent objects and refs; no main-checkout edits).
- Implementation checkpoint identity: containing commit of this report, resolved with `git log -1 --format=%H -- .dev/workflows/2026-09-23-p3-distribution/reports/source-checkpoint.md`; exact transport HEAD is returned in the task handoff. It is not called a validated commit.
- Last completed implementation: metadata v2 loader/reference source support. Limited observations and commit preparation are in the report.
- Current task: `ISSUE-337`; Issue and workflow remain in progress.
- Exact next action: coordinator reads the local checkpoint and actual #334/#335 package returns, integrates the chosen package subject, then sends this same task the exact manifest/profile scope. Do not map proposed or absent members and do not relax missing-file checks.
- Needed mapping inputs: integrated commit; five real metadata files; exact member/source/destination inventories; chosen profile IDs, skill versions and adapter selections; any agreed resource/operation changes.
- Selected package versions: lesson@0.2.0, adr@0.1.0, standards-promotion@0.1.0, pr@0.1.0 and local-backlog@0.1.0. These are selected source versions, not releases or proof of delivered source.
- Preserve #334 checkpoint `99adb0762328c8f8d6cff7338f17caec99685c0a`, #335 checkpoint `446a579d03a25edf1b6e64b5e5c13016740025c0`, dispatch HEAD and every referenced handoff commit.
- Coordinator task: `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`; owns first push, PR, online merge, provider completion and shared index registration.
- Execution provenance: OpenAI Codex; `gpt-6-astra`, `ultra`, user-declared dispatch requirement; no independent runtime attestation. No sub-agents, nested agents, new tasks or new worktrees were used.
- Hidden conversation context required: false; follow the linked selected contract and current coordinator dispatch before later mapping edits.

## Branch lifecycle

| Segment | Branch | Source | Checkpoint | Transport owner | Resume |
| --- | --- | --- | --- | --- | --- |
| 1 | codex/2026-09-23-p3-distribution | 0d0556d4c60105a28eb39cfb06efab9b069728cb | Containing source implementation commit; local only | Program #322 coordinator | Same task after actual package reconciliation; integration does not complete this workflow |
