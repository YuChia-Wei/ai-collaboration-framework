# VAL-006 Changed-Path Dependency Closure Remediation

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-14-val-006-dependency-closure`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-14-val-006-dependency-closure`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-14-val-006-dependency-closure`
- `created_at`: `2026-08-14T00:06:47+08:00`
- `updated_at`: `2026-08-14T00:38:42+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: The changed-path selector can mark a direct match selected before dependency traversal. The selected-state guard then suppresses traversal and permits a false-pass selected set.
- Authorized remediation scope: GitHub Issue #202 and `ASM-20260813-001#VALSEL-001`; correct dependency graph validation and changed-path selection evidence in the aggregate validation runner, with deterministic focused fixtures.
- Authorization source: owner instruction in Codex source task `019ffb42-297b-7922-91ee-74d19e7b962a`, delegated to task `019ffbdb-f015-7581-a8e6-33cb09cb1155`, explicitly authorizing repository-native design, implementation, validation, local durable commits, and sub-agents for Issues #200 through #208.
- Exclusions: process-tree supervision, immutable execution snapshots, timeout/cleanup and nightly scheduling (#204); package payload/apply work (#200/#201); upgrade packet and route work (#203/#206); provider runtime projections (#207/#208); .NET analyzer provider work (#205); push, pull request, merge, Issue closure, Project or milestone mutation, tag, release, and publication.
- Completion criteria: direct and transitive matches select the full closure; diamond dependencies execute once; cycles fail before execution with the exact path; unknown dependencies fail before execution; reasons and order are deterministic; disabled or not-applicable dependencies remain selected but preserve execution disposition; focused tests and workflow artifact validation pass; an independent post-remediation assessment records the fixed clean commit result.
- Workflow proportionality: one remediation task is intentional. The workflow preserves the assessment-to-remediation-to-independent-verification lifecycle, cross-runtime evidence, and merge-ready owner gate that an Issue or commit alone does not own; no validation or closeout tasks are invented.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260813-001/assessment.yaml`
- Remediation report: `.dev/workflows/2026-08-14-val-006-dependency-closure/reports/remediation-report.md`
- Verification assessment: `ASM-20260814-003` at `.dev/assessments/ASM-20260814-003/assessment.yaml`, committed as `f3647f8bd89bbcfaf75fd261681c92dce1ceb220`
- Tasks: `.dev/workflows/2026-08-14-val-006-dependency-closure/tasks/`

## Live Intake And Dependency Analysis

Read back on 2026-08-13/14 Asia/Taipei:

- local clean `main`, local `origin/main`, and GitHub `main`: `a679d4990c3a37b59bb8592e4fc78180ef165c6b`;
- Issues #200 through #208: all open, no comments, no assignee, no milestone, and no duplicate/closed state;
- baseline assessment: final `ASM-20260813-001`, merged at the same `main` commit.

| Issue | Semantic class | Dependencies | Delivery boundary |
| --- | --- | --- | --- |
| #202 VAL-006 | defect remediation and validation enabler | none; precedes reliance on changed-path evidence | independent first segment |
| #201 PKG-012 | defect remediation and package-closure enabler | benefits from #202 validation correctness | package payload/ownership segment before #200 |
| #200 PKG-011 | defect remediation and transaction enabler | consumes portable selected-input proof owned by #201 | separate higher-risk apply transaction segment after #201 |
| #204 VAL-007 | defect remediation | runner correctness independent of #200/#201; nightly scheduling depends on proven runner correctness | runner safety first; scheduling only after its evidence |
| #203 UPG-002 | upgrade correctness enabler | composes #200/#201; exact packet schema and retention remain an owner decision | analysis before the owner gate, implementation after it |
| #206 UPG-003 | compatibility feature and release-candidate correctness gate | #200, #201, #203, and required validator fixes | later one-entrypoint route segment; no v0.14 publication in this workflow |
| #207 SAG-003 | provider-neutral runtime capability enabler | reuses existing role and execution contracts | independent capability/projection segment before #208 |
| #208 UPG-004 | upgrader experience feature | depends on #207; composes with #203/#206 | separate upgrader opt-in/advisory segment |
| #205 CTX-010 | .NET-only provider lane | independent of upgrade engine; package-native selected/declined validation benefits from #201 | independent .NET reviewer and rollback boundary |

Proposed merge order after this segment: #202; #201; #200; #204 runner correctness, then nightly scheduling; #203 after its owner decision; #206 after #200/#201/#203 and required validator evidence; #207 then #208; #205 remains an independent .NET lane and does not block upgrade-engine correctness. File overlap, live head state, and validation cost must be re-read before each later branch is created.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260813-001#VALSEL-001` | HIGH | `ai-context-governance` | authorized remediation in progress | `VALSEL-001-dependency-closure` | focused runner GWT fixtures, shell syntax, workflow artifacts, Git diff checks, independent verification |

## Stages And Checkpoints

1. Baseline audit and live Issue/Git/GitHub evidence freeze — completed.
2. Finding triage, delivery-cohesion analysis, and remediation authorization — completed.
3. Bounded selector remediation and focused deterministic validation — completed at implementation commit `4ecaa5cf5c079011f765542253f2faafb2b814ca`.
4. Fixed-commit aggregate validation, POSIX-path confirmation, and independent post-remediation audit — completed; canonical WSL receipt `VAL006-003` passed 44/44 and `ASM-20260814-003` reconciled the baseline finding as resolved.
5. Finding reconciliation, commit verification, and merge-ready owner gate — completed locally. Push, PR, merge, Issue closure, and release remain separately unauthorized and unverified.

`software-development-orchestrator` is used only to coordinate the bounded tooling implementation, test, review, and commit checkpoints. It does not own this governance workflow or replace `ai-context-governance`. The read-only bounded worker supplies analysis evidence only and has no mutation or integration authority.

## Validation Strategy

- Focused contract tests: `.ai/scripts/tests/test_fail_closed_validation.py`, narrowed to the six selector/registry fixtures first and then the containing test module from the immutable commit.
- Static shell check: `bash -n .ai/scripts/check-all.sh`.
- Artifact checks: JSON parse, `.ai/scripts/validate-workflow-artifacts.py`, `git diff --check`.
- Workflow commit range: `.ai/scripts/validate-git-commits.py --range main..HEAD --workflow-id 2026-08-14-val-006-dependency-closure` after the durable commit exists.
- The full aggregate-runner contract module is selected because the runner itself changed and its observed duration exceeds 120 seconds. It must run once from the fixed clean implementation commit under the external-task contract; it may not repair or rerun failures.
- A POSIX execution-path confirmation remains required by Issue #202 and must use the same immutable source state. The Windows-compatible Git Bash path has passed locally.
- Spec compliance: not selected and therefore not applicable.

## Integration And Rollback Boundary

- Integration gate: one pull request to `main` is required by repository policy, but creating or merging it is outside current authority.
- Proposed topology: linear. This segment is one coherent defect fix with no external lifecycle or independently resumable merge-node meaning.
- Rollback: revert the single coherent remediation commit; no package format, target mutation, release record, or hosted state changes are included.

## Resume Checkpoint

- Last completed action: reconciled independent final verification `ASM-20260814-003` against canonical clean implementation commit `4ecaa5cf5c079011f765542253f2faafb2b814ca`; no active implementation finding remained and `ASM-20260813-001#VALSEL-001` is resolved locally.
- Current task: `VALSEL-001-dependency-closure` completed.
- Exact next action: owner decides whether to authorize push and PR creation. Merge, Issue closure, Project/milestone mutation, release, and publication remain separate decisions.
- Validation already completed: final Windows-compatible selector fixture class 6/6 passed in 26.703 seconds; POSIX WSL selector fixtures 6/6 passed in 19.760 seconds; profile-registry tests 6/6 passed; three existing aggregate-runner regressions 3/3 passed in 55.355 seconds; shell asset validator passed 16 assets; Bash syntax, Python AST parsing, workflow/assessment artifact validation, commit-policy validation, and Git diff checks passed. Canonical `VAL006-003` against clean `4ecaa5cf` passed the complete aggregate contract 44/44 in 46.443 seconds and its dispatch/completion pair passed the canonical schema validator. `ASM-20260814-003` independently revalidated that receipt and resolved the finding. The initial new-fixture run produced 4 passes and 2 failures because its synthetic path overlapped legitimate broad registry owners; after using a uniquely owned synthetic path, the complete class passed. The initial workflow validator run failed because the new locator was absent from the index; the indexed rerun passed. External `VAL006-001` remains blocked by Windows Temp `WinError 5`; `VAL006-002` passed only on superseded commit `125d85db` and is historical, not canonical.
- Git state: local workflow branch with canonical implementation commit `4ecaa5cf`; assessment and governance closeout changes await the final local durable commit. No push or hosted mutation.
- Branch history and checkpoint handoffs: segment 1 started locally; no push, PR, merge, or continuation checkpoint.
- Blockers or unresolved decisions: none for #202. UPG-002 packet schema and retention are outside this workflow and remain an owner gate.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-14-val-006-dependency-closure` | `main@a679d4990c3a37b59bb8592e4fc78180ef165c6b` | local merge-ready segment | implementation `4ecaa5cf5c079011f765542253f2faafb2b814ca`; assessment `f3647f8bd89bbcfaf75fd261681c92dce1ceb220`; this closeout stage | not pushed | `2026-08-14T00:38:42+08:00` | independently mergeable selector defect with fixed-head verification | obtain separate owner authority before push or PR creation |
