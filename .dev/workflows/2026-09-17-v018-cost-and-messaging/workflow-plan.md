# v0.18.0 Skill Usability And Transactional Messaging

## Template Metadata
- template_id: ai-context-governance-maintenance-workflow-plan
- template_version: 1.2.0
- created_at: 2026-09-17T23:54:11+08:00
- updated_at: 2026-09-18T01:34:00+08:00

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
- Last completed: private-role colocation, proportional execution rules, generated runtime entry pilot, messaging contracts and first package candidates. Actual Terra/Luna baseline reviews completed on the lab's v0.16.0 installation.
- Active: COST-001.
- Next: integrate role-selection metadata and exact validation registration, build candidate 03, finish disposable downstream reconciliation, then run matched candidate reviews before freezing the final package.
- Validation: candidate 02 matrix timed out at 1800 seconds after three v0.6.0 cases; no complete terminal matrix or release acceptance. Callback and zero-process cleanup evidence are retained and the source lease is released. A fresh disposable v0.17.0 application passed 52 target tests; independent audit/finalization remain pending.
- Execution decision: the parent authorizes another matrix attempt only after candidate usability and payload freeze, using a new immutable subject, a timeout justified by observed duration, and retained prior failures. This is a bounded continuation of the owner's autonomous release preparation, not a new user approval or a test waiver.
- Publication decision: not requested yet; prepare a concrete candidate before any final owner publication decision.
