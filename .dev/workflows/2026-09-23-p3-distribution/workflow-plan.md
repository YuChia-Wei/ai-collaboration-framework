# P3 distribution workflow

## Template and workflow metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- Template timestamps: created `2026-07-10T18:22:49+08:00`; updated `2026-07-13T23:11:56+08:00`.
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `workflow_id`: `2026-09-23-p3-distribution`
- `workflow_kind`: `ai-context-maintenance`; `owner_skill`: `ai-context-governance`.
- Branch: `codex/2026-09-23-p3-distribution`; base: `main`; segment: `1`.
- `status`: `completed`; `current_phase`: `completed` (bounded source scope under U001).
- Artifact root: `.dev/workflows/2026-09-23-p3-distribution`.
- `created_at`: `2026-09-23T08:33:01+08:00`; `updated_at`: `2026-09-23T09:12:38+08:00`.

## Authority, objective and scope

[Issue #337](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/337), the coordinator's explicit implementation dispatch and [P3 selected contract](../../design/framework-next/p3-shared-contract.md) authorize metadata v2 source support while preserving metadata v1. [U001](../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md) governs this source-only work. Live Issue read-back found it OPEN with the assigned first-stage scope; provider state is not implementation acceptance.

The first stage owned `src/distribution/package.py`, necessary direct distribution call sites, the distribution-implementation design and this workflow; source inspection found no necessary call-site changes. The [continuation assignment](../2026-09-23-framework-redesign-control/reports/p3-package-mapping-scope.md) authorized only the manifest, lesson-minimal plus knowledge/work-management/collaboration profiles, owned design and workflow. Both source stages are complete. Skill/adapter/loader code, root/runtime/core/custom, tests, CI, legacy tools, coordinator records and shared indexes were not changed in the mapping stage. First push, provider completion, release, adoption and credential changes remain outside this executor scope.

The one-task workflow preserves the first local source handoff and independently resumable second mapping stage. Its unique state is the dependency on actual #334/#335 delivery and the coordinator's later exact mapping dispatch. No placeholder task is created for suspended auditing.

## Observable completion criteria

1. Explicit integer metadata 1/2 handling with the original v1 closed fields and single-schema-ID behavior.
2. V2 schemas unique by exact `(id, version)` with distinct contained member paths; cross-kind IDs still unique.
3. Every v2 project role has one writable `schema` and nonempty unique declared `read_schemas` including that writable identity. Derived roles and other closed fields stay unchanged.
4. V2 schema references inspect only finite same-document `#/$defs/` pointers; no resolver, schema execution, external retrieval or skill import. Existing package-relative document checks remain.
5. Exact manifest/profile mappings use real integrated package members and preserve independent selection of all five P3 packages. The continuation completed 44 members and the four authorized profiles by direct configuration/source comparison; runtime selection remains deferred.
6. Record actual permitted checks and all U001 verification deferrals; hand coherent local commits to the coordinator before push.

Source implementation and direct syntax inspection do not establish behavioral satisfaction of these criteria. P7 owns runtime verification.

## Artifacts and stages

- Task: [ISSUE-337](tasks/ISSUE-337.json), `completed` for both bounded source stages, with P7 verification deferred.
- Report: [source checkpoint and completion](reports/source-checkpoint.md), final for bounded source scope; retains the initial checkpoint observations.
- Contract: [metadata v2 implementation](../../design/framework-next/distribution-implementation/metadata-v2.md).
- Stage 1 completed: loader source implementation, limited checks and local commit handoff `13a08f3c886513cead3bfea080224f3323131977`; preserved unchanged.
- Stage 2 completed: same task fast-forwarded from the clean first checkpoint to `2bd7acdaf8a580df965396bdb9dbb8c05f6308af`, then reconciled 44 actual members and the four exact profiles. No product execution was used for completion.
- Behavioral/schema/package testing, independent audit, native handoff validation and CI: `deferred-by-owner`, U001, program #322 coordinator / P7. Next action: P7 selects and executes replacement checks on the integrated immutable subject. No audit packet or lease is fabricated.

## Completed source handoff

- Assigned worktree/branch: `F:/framework-next/337`, `codex/2026-09-23-p3-distribution`; same conversation and branch throughout.
- First starting HEAD: `0d0556d4c60105a28eb39cfb06efab9b069728cb`; first implementation checkpoint: `13a08f3c886513cead3bfea080224f3323131977`.
- Continuation admission: exact first checkpoint and clean status read back; `git merge --ff-only 2bd7acdaf8a580df965396bdb9dbb8c05f6308af` completed, resulting HEAD matched and status remained clean.
- Common Git directory: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.git`; persistent objects/refs retained and no main-checkout edits.
- Final mapping checkpoint identity: containing commit of this report, resolved with `git log -1 --format=%H -- .dev/workflows/2026-09-23-p3-distribution/reports/source-checkpoint.md`; exact HEAD is returned after the local commit. It is not a runtime-validated commit.
- Last completed implementation: loader support followed by exact committed-source manifest/profile mapping. Actual checks and initial environment failure are retained in the report.
- Task/workflow: `completed` for bounded source under U001. Issue/Project closure and online integration remain coordinator-owned; no closed/provider state is inferred.
- Next action: coordinator reads the final local checkpoint, updates its shared index row, and performs separately authorized first push/PR/online merge and Issue/Project read-back. Program #322/P7 selects and executes deferred replacement checks.
- Mapping result: lesson@0.2.0 (9), adr@0.1.0 (8), standards-promotion@0.1.0 (9), pr@0.1.0 (10), local-backlog@0.1.0 (8); four profiles with codex and profile_version 1. No unfinished implementation decision remains within #337's assigned source scope.
- Preserve #334 design `99adb0762328c8f8d6cff7338f17caec99685c0a`, source `552e218d039245482ed422be7d4fb642d5463ff0`; #335 design `446a579d03a25edf1b6e64b5e5c13016740025c0`, corrected source `5409641f19244bc44467af7fba3fc496d7f5195c`; all #337/coordinator checkpoints.
- Coordinator task: `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`.
- Execution provenance: OpenAI Codex, `gpt-6-astra` / `ultra`, user-declared dispatch requirement; no independent runtime attestation. No sub-agents, nested agents, new tasks or new worktrees.
- Hidden conversation context required: false; the current source assignment and report contain the handoff.

## Branch lifecycle

| Stage | Branch | Input | Checkpoint | Transport owner | Remaining action |
| --- | --- | --- | --- | --- | --- |
| Loader | codex/2026-09-23-p3-distribution | 0d0556d4c60105a28eb39cfb06efab9b069728cb | 13a08f3c886513cead3bfea080224f3323131977 | Program #322 coordinator | Preserved ancestor; coordinator reported PR #339 integration |
| Actual mapping | Same branch after authorized fast-forward | 2bd7acdaf8a580df965396bdb9dbb8c05f6308af | Containing completion commit | Program #322 coordinator | Push/PR/online merge and provider closure; P7 verification remains deferred |
