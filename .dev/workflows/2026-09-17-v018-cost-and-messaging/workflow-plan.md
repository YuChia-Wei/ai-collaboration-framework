# v0.18.0 Skill Usability And Transactional Messaging

## Template Metadata
- template_id: ai-context-governance-maintenance-workflow-plan
- template_version: 1.2.0
- created_at: 2026-09-17T23:54:11+08:00
- updated_at: 2026-09-18T09:40:26+08:00

## Workflow Metadata
- workflow_id: 2026-09-17-v018-cost-and-messaging
- workflow_kind: ai-context-maintenance
- owner_skill: ai-context-governance
- branch: codex/2026-09-17-v018-cost-and-messaging
- base_branch: main
- status: in_progress
- current_phase: remediation
- artifact_root: .dev/workflows/2026-09-17-v018-cost-and-messaging
- template_source: .ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md
- template_version: 1.2.0

## Objective And Scope
Owner authorization on 2026-09-17 covers autonomous implementation, Issue/Project management, a disposable downstream lab clone on the explicitly supplied RAM disk, external analysis artifacts, and preparation for v0.18.0. Source Issues #300, #301 and #302 were created and read back OPEN; Project 3 shows In progress, Approved and Target release v0.18.0. The public issue bodies contain bounded intent without private host/account details.

This is one cohesive release delivery with independent acceptance mappings. Source routing, packaging and downstream usability share validation and review boundaries; messaging defaults supply a substantive downstream task. Canonical framework work stays in this branch. The active lab branch is read-only reference input, never an integration target.

## Artifact Contract
- Baseline: ../../assessments/ASM-20260917-23-c18/assessment.yaml
- Remediation: reports/remediation-report.md
- Tasks: tasks/COST-001.json, tasks/MSG-001.json, tasks/EVAL-001.json, tasks/REL018-001.json
- Raw runtime/provider evidence: ignored `.dev/ai-context/local/v018/`.
- External analysis reports and disposable evaluation checkouts may be used under the owner's authorized roots; copy only stable conclusions/identity references into source records.

## Accepted Design Direction
1. Keep universal/profile semantics shared and target effective state in `.dev/ai-context`. Cohesive skill-private resources may live with the skill; do not duplicate normative text.
2. Pilot generated runtime execution entries with exact canonical provenance and parity checks, preserving conditional loading and all applicable rules.
3. Ordinary same-runtime analysis/local edits use a bounded envelope and one tracked writer. Full immutable packets/leases remain for terminal/high-risk, external/long validation, publication/adoption and frozen cross-boundary work. Routine output cannot satisfy formal acceptance.
4. Judge local scope by contract/side-effect/responsibility impact; a private implementation type inside an accepted boundary alone need not trigger a new owner.
5. Transactional messaging defaults have one completion owner, native capability preference, explicit inbox receipt/completion, EF context/Factory scope, deduplication/business-idempotency separation and real-effect evidence. Wolverine is conditional, not mandatory.

## Findings And Acceptance
| Finding | Task | Evidence |
| --- | --- | --- |
| ASM-20260917-23-c18#F-001: capability dispersion and multi-hop loading | COST-001 | one canonical resource owner, packaged dependency closure, wrapper parity |
| ASM-20260917-23-c18#F-002: routine execution overhead and type-based routing | COST-001 | proportional boundaries with preserved terminal safeguards |
| ASM-20260917-23-c18#F-003: transactional messaging gaps and completion ambiguity | MSG-001 | one contract and consistent selected design/review/implementation/test routes |
| Usability/cost hypothesis | EVAL-001 | pinned baseline/candidate, actual Terra/Luna task outputs, quality and measured cost limits |
| Release readiness | REL018-001 | explicit gate necessity/outcomes, package/upgrade identity, independent final review |

## Validation Strategy
Run focused deterministic checks after each coherent edit. Heavy unrelated I/O/OS suites are deferred during iteration by owner instruction, not passed or permanently waived. Before candidate readiness, enumerate affected release gates, justify execution/reuse/not-applicable/deferral, and preserve OS/durability semantics where they matter. Do not route durability tests through RAM-disk fixture acceleration. Reuse evidence only under the existing content-subject contract.

## Evidence Intake
Base/source: f643b56cd68faec590f23a8c8a7436f813285e5d, clean and equal to origin/main. Lab reference: ed27f6b7c63fdb45dfa9a8e6ff010b4be63b4045. Terra read-only guidance review verified the external report manifest's 10 exported artifacts and returned five bounded findings; no product code or tests were executed. It identified the Use Case versus native middleware completion ambiguity and missing inbox/Factory/idempotency contracts. Historical sample tests do not establish current-head execution, crash recovery or business OperationId deduplication.

Codebase Memory was refreshed in fast mode, but reported `.ai/assets`, `.ai/scripts` and `.claude` excluded. Use explicit Git-tracked file inventories and direct code/document reads for these scoped surfaces; graph absence is not evidence.

## Resume Checkpoint
- Updated: 2026-09-18T09:40:26+08:00
- Last completed: Candidate09 finalized in the isolated short-root target at `e19dc802326ac19dae90dc0b5df3b9b683450e1e`; 55 actual target tests, canonical receipt binding, 11 independent audit gates and exact-tree rebind passed. Original lab/product bytes remain unchanged.
- Usability: Both candidate02 models resolved `review/direct/dotnet-backend/dotnet-mixed-review` and consumed the freshness-verified packet containing MESSAGING-TX-001. Each received 6 met and 2 partial rubric findings. Compared with the v0.16 baseline, uncached input decreased 9.87% for Terra and 33.13% for Luna in this one task. This is not company-credit or whole-project cost evidence.
- Active: REL018-001. Implementation tasks retain pending final independent acceptance. Candidate01 incomplete rule consumption and all earlier failed operations remain preserved.
- Next: Freeze this clean workflow checkpoint and canonically rebind unchanged candidate09 ZIP `764eb3197b0ab76efaea1ca272e76fe7c9b780db348b60ab2b1bd3b7ccefd811`; then execute the required matrix and release profile before independent source review.
- Execution decision: The workflow owner authorizes one nine-case matrix attempt03 after this freeze. Its new retry authorization binds the immutable subject, retained timeout fingerprint, corrected runner, unchanged candidate09 and duration-based 7200s timeout. After a passing terminal record and explicit lease release, run the policy-selected 76-check release profile once with a 9000s bound. No extra nightly/OS suite or duplicate target-suite/model replay is added.
- Publication decision: Draft lab PR13 is an unfinalized public checkpoint. Source push, PR, merge, tag and publication are not inferred from local preparation; present the concrete validated result for the final owner decision.

## Candidate07 Failure And Bounded Recovery

Candidate07 applied successfully in the isolated short-root target, but its
separately routed validation stopped at a retained v0.16 audit that incorrectly
compared historical authority pins to current files. No passing receipt was
created and the subsequent 52-test suite did not execute. Reconcile the
target-owned gate on a fresh preapply branch: completed audits verify their
immutable commit, while in-progress audits and explicit admission keep current
authority checks. The 21 focused target audit tests passed.

The first canonical rollback stopped after restoring an executable script.
Read-only replay and focused reproduction identified a stale in-process dirty
snapshot, rather than a persisted content mismatch. Issue #304 records the
correction: accept a restored snapshot baseline only after sealed bytes, index
identity and applicable modes verify. Three focused rollback tests and four
dependent target-validation runner tests passed. Preserve both original failed
operations and separately record the real rollback retry outcome; no journal or
receipt is repaired manually.

The corrected canonical rollback then completed with `rolled-back` and exit 0.
The isolated target is clean at its original preapply commit
`4507aecb7f2132abf7ec7f1b41aabc7f1aa35ed5`; the original failed validation and
rollback records remain retained.
