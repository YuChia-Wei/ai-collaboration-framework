# Workflow Proportionality, Delivery Cohesion, And Merge Topology Baseline

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260803-004`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-03`
- `created_at`: `2026-08-03T23:47:10+08:00`
- `updated_at`: `2026-08-03T23:47:10+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `80b013803ee29ca2f4dd458a393eb1da451212e1`
- `previous_assessment`: [`ASM-20260803-003`](../ASM-20260803-003/report.md)
- `workflow_refs`: [`2026-08-03-workflow-delivery-cohesion`](../../workflows/2026-08-03-workflow-delivery-cohesion/workflow.yaml)

## Executive Summary

- Overall assessment: the repository has strong authorization, assessment, validation, and commit-boundary controls, but workflow entry and Git topology are insufficiently proportional to delivery value.
- Overall score: `6.5/10`
- Decision: `remediation-recommended`
- Primary strengths: provider state is non-authoritative, assessment mode is distinct from workflow mode, commits are batched by validated stage, all current `main` changes require pull requests, and the audited single-commit PRs all had successful hosted checks.
- Primary risks: broad workflow triggers can create durable ceremony without unique state; Issue count has no delivery-cohesion grouping rule; and fast-forward integration is framed as an exceptional tiny-direct-mode path instead of a normal topology selected independently from review risk.

The audit does not infer wasted tokens. No historical token telemetry exists. It uses tracked artifact files, lines, bytes, Git diffs, and live GitHub metadata only as reproducible volume and behavior evidence.

## Scope

### Included AI Context Surfaces

- 57 formal workflow directories with `workflow.yaml`, their task counts, and their retained artifact volume.
- Workflow, assessment, commit, branch, and merge policies plus portable projections and skill routing.
- Live metadata for all 37 merged pull requests available on 2026-08-03.
- The team-supplied multi-Issue case as a reported operating scenario, clearly separated from repository-native history.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- Raw conversation text beyond the owner-selected scenario and decisions.
- Claims about actual historical prompt tokens, model compute, or monetary cost.
- Remediation changes; this assessment freezes `main@80b0138`.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product implementation and product tests
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Separated four decisions: execution record (`direct`, `assessment`, `workflow`), delivery grouping, integration gate (`direct push` or `pull request`), and Git topology (`linear` or `merge commit`).
- Evaluated whether each retained workflow carried unique state that a GitHub Issue, ADR, assessment, commit, pull request, or release record did not already provide.
- Treated task, Issue, commit, and file counts as review signals rather than automatic decisions.

### Pass B: Repository-Aware Skill Review

- Applied `WORKFLOW-GATE-POLICY`, `TEAM-GIT-FLOW-RULES`, `GIT-COMMIT-POLICY`, assessment ownership, work-item binding, governance lifecycle, and orchestrator routing.
- Verified historical cases through tracked artifacts and Git commits, then read current PR metadata through `gh` outside the sandbox.
- Preserved the repository rule that Issue/Project state never authorizes execution by itself.

### Delegation

- Sub-agents used: `no`
- Assigned surfaces: not applicable; the main agent performed and reconciled the audit.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| PowerShell workflow inventory | `main@80b013803ee29ca2f4dd458a393eb1da451212e1` | clean baseline | `.dev/workflows/**`; product code excluded | cannot establish business value by itself | manual workflow purpose and Git-history review |
| `gh api` PR metadata | 37 merged PRs as of 2026-08-03 | live, authenticated outside sandbox | PR commits, files, lines, reviews, checks | cannot prove review quality or token cost | local Git commits and tracked workflow artifacts |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Formal workflows | 57 directories | agents / maintainers | source execution history | active historical corpus | directories contain locators |
| Workflows with fewer than three tasks | 28 workflows; 134 files; 8,759 lines; 472,706 bytes | agents / maintainers | mixed | retained | 49.1% of formal workflows |
| One-task workflows | 23 workflows; 111 files; 7,334 lines; 396,066 bytes | agents / maintainers | mixed | retained | count is a review signal, not a defect verdict |
| Strong over-orchestration candidates | 8 workflows; 33 files; 2,142 lines; 116,689 bytes | agents / maintainers | planning / small repair | historical | no history rewrite recommended |
| Merged PRs | 37 total; 18 single-commit | maintainers | source integration | live read-back | all 18 single-commit PRs had zero submitted reviews and only successful hosted checks |

## Strengths

1. Direct, assessment, and workflow modes already have distinct durable homes.
2. The commit policy rejects one commit per skill invocation and preserves real approval, evidence, review, and handoff boundaries.
3. Work-item binding keeps provider state non-authoritative and permits explicit owner authorization without inventing Issue identifiers.
4. Pull-request automation provided successful hosted checks for every audited single-commit PR.
5. Existing policy already recognizes that multi-pass transient analysis does not require workflow mode.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| WFG-001 | HIGH | Workflow entry has broad one-of triggers but no explicit workflow-value test. | 28/57 formal workflows have fewer than three tasks; 23 have one. Eight strong candidates retain 2,142 lines. CTX-002 bootstrap added 162 lines before a repair whose product change was one deleted index line; its completion commit added 112 lines and removed 33 across workflow/backlog records. | Agents can produce execution records whose unique coordination value is lower than their creation and maintenance cost. | Require the agent to name unique workflow state that cannot be represented adequately by an Issue, ADR, assessment, commit, PR, or release record. Treat one task or fewer than three tasks as a review signal; generic validation and closeout are lifecycle steps, not artificial tasks. | `ai-context-governance` |
| WFG-002 | HIGH | No policy evaluates whether multiple Issues belong to one delivery before creating workflows. | The work-item contract defines authorization and traceability, but not Issue-to-workflow cardinality. The owner reports a team branch with several Issues, one intended branch/PR, and one single-task workflow per Issue. | AI may mechanically turn Issue count into workflow, branch, and PR count, duplicating prompts and artifacts while diverging from the team's review unit. | Add a delivery-cohesion check using shared outcome, branch, validation, reviewer set, release gate, and atomic rollback. Permit many approved Issue bindings to one workflow/PR; split only when delivery boundaries differ or the owner selects independent delivery. | `ai-context-governance`; `software-development-orchestrator` routing |
| WFG-003 | MEDIUM | Linear history is framed as an explicit tiny-direct-mode exception rather than a normal integration topology. | `TEAM-GIT-FLOW-RULES` defaults all workflow and multi-commit branches to merge commits and permits fast-forward only for tiny direct-mode branches explicitly chosen by a maintainer. Single-commit PR size ranges from 3 files / 217 additions to 10 files / 6,747 additions; PR #73 changed 21 files. | Commit count and workflow mode can dominate topology even when review risk, rollback grouping, or durable boundaries point elsewhere. README-only history updates are forced into the same topology framing as normative governance changes. | Define positive normal rules for linear and merge-commit topology. Keep PR requirement separate. Default historical README-only updates to direct mode + PR + linear merge unless they change normative, release, generated, or security truth. | `ai-context-governance` |

## Baseline And Skill Comparison

### Confirmed

- Artifact volume is material enough to require a proportionality rule, but it is not token telemetry.
- Task count alone cannot decide mode; 18 low-task workflows remain justified by release, publication, external-host, or cross-boundary lifecycle state.
- Single-commit PR count alone cannot decide topology because size and semantic risk vary widely.

### Added By Repository-Aware Review

- Assessment mode already solves retained read-only analysis without requiring workflow artifacts.
- `WIBIND-001` permits multiple identifiers as traceability evidence but lacks a delivery-grouping decision.
- Owner authority permits this workflow to select linear integration even before the default policy is remediated.

### Downgraded Or Deferred

- The eight historical workflows are not labeled invalid retroactively; they are calibration examples for future selection.
- Direct push to `main` is not recommended for ordinary README history updates because pull-request checks and visible review remain useful while linear topology removes the unnecessary merge node.

### Overturned

- "Every single-commit PR should fast-forward" is unsupported.
- "Every Issue needs its own workflow" is unsupported.
- "Fewer than three tasks means workflow mode is forbidden" is unsupported.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | clean `main@80b013803ee29ca2f4dd458a393eb1da451212e1` before the workflow branch |
| Workflow inventory | passed | 57 formal, 28 with fewer than three tasks, 23 with one task |
| Artifact volume | passed | exact tracked local file, line, and byte counts recorded above |
| Historical small-repair sample | passed | `5458123` and `2b00a3b` reproduce CTX-002 bootstrap and completion scope |
| Live PR inventory | passed | 37 merged PRs, 18 single-commit; REST read outside sandbox |
| Review/check read-back | passed | all 18 had zero submitted reviews and one or more hosted checks, all successful/neutral/skipped |

### Skipped Validation

- Historical token counts and prompt cost: no telemetry; explicitly not claimed.
- Team repository branch contents: not available in this repository; the scenario is owner-supplied operational evidence rather than a file-backed defect reproduction.

## Recommended Action Order

1. Add workflow-value and low-task review rules.
2. Add delivery-cohesion grouping before Issue-to-workflow creation.
3. Separate execution record, integration gate, and Git topology decisions.
4. Add positive linear and merge-commit rules plus representative fixtures.
5. Verify the policy independently and register it as the next successor release gate without naming the version.

## Deferred Items

- Actual token telemetry and execution-cost instrumentation remain with `ASM-20260803-003` / `REL-004`; this audit does not duplicate them.
- Branch-protection enforcement for a merge method remains provider-specific and requires a separate owner decision if desired.

## Appendix

### Commands Run

```text
PowerShell inventory of .dev/workflows/*/workflow.yaml, tasks, files, lines, and bytes
git show --stat/--numstat 5458123 2b00a3b
gh api repos/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pulls?state=closed&per_page=100
gh api repos/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pulls/<number>
gh api repos/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pulls/<number>/reviews?per_page=100
gh api repos/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/commits/<head-sha>/check-runs?per_page=100
```

### Notes

- The GitHub GraphQL aggregate query exceeded its node limit; the audit used authenticated REST calls outside the sandbox instead of treating the query failure as missing data.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260803-004/report.md`
- Stable finding references: `ASM-20260803-004#WFG-001`, `ASM-20260803-004#WFG-002`, `ASM-20260803-004#WFG-003`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-08-03-workflow-delivery-cohesion`
- Verification assessment: `ASM-20260803-005` (planned)
- Remediation intentionally not performed by this skill: `yes`
