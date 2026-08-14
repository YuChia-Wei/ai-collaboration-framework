# PKG-012 Portable Package Closure Remediation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-14-pkg-012-package-closure`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-14-pkg-012-package-closure`
- `base_branch`: `codex/2026-08-14-val-006-dependency-closure`
- `branch_segment`: `2`
- `status`: `in_progress`
- `current_phase`: `remediation-planning`
- `artifact_root`: `.dev/workflows/2026-08-14-pkg-012-package-closure`
- `created_at`: `2026-08-14T07:03:23+08:00`
- `updated_at`: `2026-08-14T07:09:30+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: source-tree package checks can certify a payload whose declared runtime, validators, profiles, fixtures, imports, component ownership, or document bytes are incomplete after extraction.
- Authorized remediation scope: GitHub Issue #201 and `ASM-20260813-001#PKGCLOSURE-001`; close package-native validation over a freshly extracted candidate, establish one authoritative component ownership projection, classify source-only checks, record incoming validator identity, and fail on portable manifest or byte-integrity omissions.
- Authorization source: the owner authorized repository-native implementation of Issues #200-#208 and subsequently required all segments to complete locally before one cumulative push, PR, and merge.
- Exclusions: durable target mutation, journal, recovery, and Hybrid target-state identity belong to #200; target-prospective policy cutover and remediation packets belong to #203; long-range route orchestration belongs to #206. Issue closure, Project/milestone mutation, release allocation, tag, release, and publication remain unauthorized.
- Completion criteria: an isolated extracted candidate passes its documented package-native validation using identified incoming validators; omissions of required runtime imports, schemas, profiles, fixtures, or component-owned paths fail closed; component ownership has no overlap, omission, or divergent projection; source-only checks cannot contribute to portable success; full payload byte/path/case/encoding/EOL/EOF/mode/manifest fixtures pass on Windows-compatible and POSIX paths; identical selections reproduce identical payload identity outside the source checkout.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260813-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-14-pkg-012-package-closure/reports/remediation-report.md`
- Verification assessment: pending under `.dev/assessments/<verification-assessment-id>/assessment.yaml`
- Tasks: `.dev/workflows/2026-08-14-pkg-012-package-closure/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#PKGCLOSURE-001` / DS-15 | HIGH | `ai-context-governance` | establish one authoritative ownership and selection view | `PKGCLOSURE-001-component-ownership` | deterministic projection, overlap, omission, divergence, and identity fixtures |
| `ASM-20260813-001#PKGCLOSURE-001` / DS-04, DS-07, DS-13, DS-14 | HIGH | `ai-context-governance` coordinating bounded tooling | close isolated candidate validation over incoming portable authority | `PKGCLOSURE-002-isolated-validation` | extracted candidate command plus missing import/schema/profile/fixture failures |
| `ASM-20260813-001#PKGCLOSURE-001` / DS-17 | HIGH | `ai-context-governance` coordinating bounded tooling | validate complete built payload bytes and modes | `PKGCLOSURE-003-payload-integrity` | EOF, encoding, path-case, EOL, mode, manifest, Windows-compatible, and POSIX fixtures |

## Stages And Checkpoints

1. Baseline audit, live Issue read-back, graph-assisted code discovery, and stacked clean checkpoint — completed.
2. Finding triage, #200 boundary analysis, and task ownership — in progress.
3. Canonical ownership and isolated validation implementation with focused deterministic fixtures — pending.
4. Complete payload-integrity validation, fixed-clean-commit aggregate/POSIX evidence, and independent post-remediation assessment — pending.
5. Finding reconciliation and local closeout; continue stacking later #200-#208 segments without remote integration — pending.

`ai-context-governance` owns the assessment-to-remediation lifecycle. `software-development-orchestrator` coordinates only bounded Python/tooling implementation, tests, review, long-running validation, and commits. Product source review, spec compliance, and release closeout are not selected.

## Validation Strategy

- Focused tests: `.ai/scripts/tests/test_ai_context_packaging.py` and directly affected package-native contract modules.
- Isolated package proof: build from an immutable clean commit, extract outside the source tree, run only the documented candidate-native command with source checkout paths removed from import and working-directory resolution.
- Static and artifact checks: Python AST/compile, YAML/JSON parsing, workflow validation, distribution/schema validators, `git diff --check`, and commit-policy validation.
- Cross-platform: Windows-compatible focused fixtures first; POSIX execution against the same immutable commit.
- Long-running commands at or above the repository threshold use exactly one external-task dispatch/receipt pair per attempt and remain read-only/fail-closed.

## Integration And Rollback Boundary

- This segment may modify package construction, distribution/profile/schema ownership contracts, package-native validators, and their tests. It must not implement #200 target transaction semantics.
- Rollback is the coherent #201 implementation and governance commit range. Later #200 consumes its selected-input and component proof but remains independently reviewable.
- The final cumulative PR to `main` is deferred until all #200-#208 segments complete. The local stack preserves per-segment commits and validation evidence.

## Resume Checkpoint

- Last completed action: rewrote every unpushed local commit subject to carry #201 or #202 as required by the owner, preserved fixed validation commit `4ecaa5cf`, and reconciled the new clean #202 checkpoint `f9483469dba4cbd64c20606e33597ffa30793c74`.
- Current task: `PKGCLOSURE-001-component-ownership` planning, with parallel read-only inventory of #201 and #200 boundaries.
- Exact next action: reconcile explorer evidence, finalize implementation ownership, and commit this workflow-planning checkpoint before changing package contracts.
- Validation already completed: predecessor #202 workflow commit-policy range passed; branch creation and Git status were clean.
- Git state: branch `codex/2026-08-14-pkg-012-package-closure` based on local #202 closeout; workflow artifacts are the only intended dirty files.
- Branch history and checkpoint handoffs: cumulative segment 2; no push, PR, merge, Issue close, or release mutation.
- Blockers or unresolved decisions: none yet for #201. Any need to redefine #200 transaction identity or #203 target-policy authority stops this task at its declared boundary.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | `codex/2026-08-14-pkg-012-package-closure` | `codex/2026-08-14-val-006-dependency-closure@f9483469dba4cbd64c20606e33597ffa30793c74` | local active stacked segment | workflow plan `caf2256123b1ab03e5da435f6eff9818543611aa`; implementation pending | not pushed | `2026-08-14T07:09:30+08:00` | package closure precedes durable apply and upgrade correctness | finish #201 locally, verify, close, then stack #200 without remote integration |
