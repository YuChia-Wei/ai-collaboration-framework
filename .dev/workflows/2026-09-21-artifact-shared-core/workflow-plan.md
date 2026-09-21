# Share artifact primitives and integrate existing producers

## Workflow Metadata

- `workflow_id`: `2026-09-21-artifact-shared-core`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-21-artifact-shared-core`
- `base_branch`: `main`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-09-21-artifact-shared-core`
- `created_at`: `2026-09-21T22:38:23+08:00`
- `updated_at`: `2026-09-21T23:15:03+08:00`
- `branch_segment`: `1`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

Implement the owner-approved P2 from [ASM-20260921-18-gav](../../assessments/ASM-20260921-18-gav/report.md): shared mechanical primitives and existing producer integration. [Issue 317](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/317) owns the material scope and authorization. Preserve explicit family parsing profiles, existing CLIs, semantic validators, deterministic output and authority/import closure. Resolve the documented quoted-hash comment false positive without discarding real comments.

## Authorization And Local Integration

The owner accepted the P1 report on 2026-09-21 and authorized the next stage plus local branch integration. This task-local instruction overrides the normal hosted PR/CI integration path for this stage; it does not rewrite repository policy. Hosted CI is not executed, and no failure or pass is invented. Retain meaningful local validation. Remote push, PR creation, Issue/Project closure, tag/release/publication and downstream adoption remain separate.

P1 local integration: merge commit `9b07d22f80f6ccbe28c1564253e3dab3d3ffad46`, parents `8830cdfc252b8845efcbe6cce539041c17cf8e7a` and `b032682d8efe8ff406b8a824a63541819a3c0c79`; its tree equals the P1 delivery tree. The retained merge node groups the analysis approval, implementation, repair and verification checkpoints. P2 starts from that clean local main on this dedicated branch. Latest read-only remote-main observation remained `8830cdfc`; no push occurred.

## Accepted Criteria

1. Share genuinely duplicate mechanics between authoring and execution producers without merging semantic authority.
2. Preserve CLI, serialized output, digests and family acceptance/rejection behavior except the selected hash-string false-positive fix.
3. Independently cover duplicate/non-string keys, aliases/merges/tags, scalar and finite JSON behavior, and deterministic bytes.
4. Accept scalar hash content while refusing actual YAML comments before rewriting, including CRLF and block/flow cases.
5. Bind the new dependency in preview and execution authority plus source/package import closure.
6. Keep existing test/gate identities; run affected focused checks with truthful outcomes.
7. Obtain independent fixed-subject verification and deliver a Chinese explanation with remaining limits.

## Execution Plan

CORE-001 implements the shared core and legacy producer integration, then focused validation. CORE-002 independently verifies one clean fixed subject, reconciles findings and completes the explanation report. Root owns integration and is the sole tracked writer; advisory explorers remain read-only. Full-tier review applies if evidence-custody authority is affected. Review timing must be captured directly; unavailable timing is never inferred from file metadata.

## Validation And Discovery History

Git status was clean; local main and freshly read remote main matched before P1 integration. The first sandbox remote read failed at the configured proxy; the read-only elevated retry passed. Code graph refresh succeeded but explicitly excluded `.ai/scripts` and `.ai/assets`; discovery in those paths uses explicit Git-tracked evidence, with no absence or completeness claim from the graph.

## Deferred Work

P3 covers other editable families and migration edges; P4 covers removal only with replacement coverage evidence. No release version is allocated. Baseline AIC-001/AIC-004 can only become partially resolved in this bounded stage; AIC-003 migration and AIC-005 consolidation remain deferred. P1 final reports remain historical and immutable.

## Resume

Issue 317 remains open. P1 is merged locally. P2 implementation and selected verification are complete; see ASM-20260921-23-qsn and reports/remediation-report.md. Next product scope is P3 family-by-family migration/authoring, followed by P4 only after replacement coverage. No provider mutation or release is authorized by this local completion.

## Implementation Checkpoint

Shared mechanics and both producer adapters are implemented. Focused checks are recorded in [the report](reports/remediation-report.md). The packaging fixture helper omissions and direct changed-path dependency gaps are repaired. No validator or test was removed. Full execution-artifact and package-smoke suites are classified long-running from their 120-second registry budgets and will run as one bounded external command against a clean commit. Root remains integration owner and will suspend tracked edits under a read-only lease.

## Verification And Local Delivery

Implementation subject: `b808533b71cb257fdfdd741b0dafe5c3b703178e`. Independent native auditor `/root/p2_independent_audit` retained blocked environment attempt 1, then executed the unchanged two-suite command once in authorized elevated attempt 2 and returned validated terminal delivery; counts {"errors": 0, "failures": 0, "skipped": 0, "successful_test_cases": 27, "tests_run": 27}, exit 0, duration 96.499 seconds. Original bytes and lease release are retained in assessment `ASM-20260921-23-qsn`; acceptance projection and role record are under `evidence/`. Root accepted the selected P2 evidence. Preparation-only role-binding refusal and prompt hash transcription correction are retained and do not become behavioral retries.

A non-fast-forward local merge retains the implementation freeze and separate review/evidence-intake commits as a meaningful review and rollback unit. Before integration, validate the final delivery metadata on a clean commit and bind its current content; do not relabel prior tests as execution on that later commit. Hosted/provider checks are outside the owner-authorized local integration path.
