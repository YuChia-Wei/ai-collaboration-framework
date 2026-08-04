# AI Context Audit Report

## Metadata

- `assessment_id`: `ASM-20260804-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-04`
- `created_at`: `2026-08-04T21:49:30+08:00`
- `updated_at`: `2026-08-04T21:49:30+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `4e7b5e0d59be831453b5c34f5f1eb3a1daae1245`
- `previous_assessment`: none
- `workflow_refs`: `2026-08-04-framework-managed-ignore-detection`

## Executive Summary

- Overall assessment: The current package application safety contract has a reproducible high-risk gap at the boundary between framework-managed payload identity and target Git ignore rules.
- Overall score: `N/A`
- Decision: `remediation-recommended`
- Primary strengths: The profile declares Codex adapters as managed payload; the package planner binds a clean target HEAD and observed file state; apply remains pending-validation and does not directly update provenance.
- Primary risks: An ignored selected managed path can be planned as an ordinary add, written invisibly to Git porcelain output, and omitted from the existing target-validation identity.

## Scope

### Included AI Context Surfaces

- `.ai/distribution/profiles/dotnet-backend.yaml`
- package plan/apply, target provenance, target validator, and critical-gate routing under `.ai/scripts/`
- upgrader guidance and current GitHub Issue #93
- a disposable Git fixture that models the exact selected Codex adapter path

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`, except focused AI-context validation evidence
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- REL-004, #92, #94, release work, target-owned ignore edits, and any repository-wide terminology rename

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product implementation trees
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: current main checkout, package-profile declaration, plan/apply code, target validator/finalizer, critical-gate routing, and a disposable Git repository.
- Checks performed: verified that the selected managed adapter is declared in the profile; inspected the current clean-target test; reproduced a target `.gitignore` rule that excludes the selected adapter; compared plan, apply, Git-ignore, and status observations.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `ai-context-governance`, workflow/assessment/commit/handoff policies, and current Issue #93 acceptance criteria.
- Checks performed: confirmed workflow mode and owner authorization; confirmed Issue #93 requires plan evidence, owner-preserved ignore bytes, pre-finalization failure or unresolved state, provenance preservation, and target critical-gate consistency.

### Delegation

- Sub-agents used: none.
- Assigned surfaces: not applicable.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory-mcp moderate index | `4e7b5e0d59be831453b5c34f5f1eb3a1daae1245` | indexed on a clean checkout | repository metadata; `.ai/scripts` is excluded by the index | package-script control flow and ignore-rule behavior | direct source reads, `rg`, Git commands, and a disposable Git fixture |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Package profile | 1 profile | agent / downstream maintainer | portable AI Context package | active | `.codex/agents/**` is a framework-managed `software-development-core` entry. |
| Package planner/apply | 2 Python modules | agent / downstream maintainer | portable package apply | active defect | uses clean porcelain status and file observations but has no ignore-rule observation. |
| Target validation/finalization | 2 Python modules | agent / downstream maintainer | portable AI Context package | active gap | validates provenance/ledger, but the receipt does not bind required managed path identity. |
| Critical gate routing | 1 shell script | target maintainer | portable package | active | target repositories route `validate-ai-context-target.py` through the critical gate when provenance exists. |

## Strengths

1. `.codex/agents/**` is explicitly declared as framework-managed package content, rather than inferred from a historical target.
2. The current planner requires a committed clean target and binds observations to the planned starting commit.
3. Apply emits `pending-validation` and leaves `provenance_updated: false`, which makes it feasible to block finalization without rewriting target-owned files.
4. The target critical gate already invokes `validate-ai-context-target.py` for initialized package targets, offering one canonical post-install route.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | Selected framework-managed paths excluded by target Git ignore rules are not represented in the plan or target-validation identity. | `clean_target_head()` uses only `git status --porcelain`; `.codex/agents/**` is selected by the current profile. The disposable target with `/.codex/*` and `!/.codex/agents/skills/**` planned `context-translator.toml` as `add`, applied it, and `git check-ignore -v --no-index` matched it while porcelain reported only the pending receipt. | A managed adapter can be absent from a target checkout or invisible after apply, while the package process can continue toward a generic provenance finalization. | Record Git ignore evidence in dry run, fail apply before mutations while unresolved, bind selected managed path identity into the pending receipt, and make target validation/finalization reject the same missing or ignored identity. | `ai-context-governance` / `IGN93-002` |

## Baseline And Skill Comparison

### Confirmed

- General fail-closed package safety and repository-specific Issue #93 acceptance both confirm that an ignored selected managed path must not become a silent skip.

### Added By Repository-Aware Review

- Target critical validation has one existing portable route: `check-all.sh` selects `validate-ai-context-target.py` for initialized packaged targets.
- Owner authority is required for preserve-rule, narrow-exception, or component-selection disposition; no automatic `.gitignore` rewrite is authorized.

### Downgraded Or Deferred

- The historical v0.6 downstream narrative was not used as current proof; only the current main code and fresh disposable fixture establish this finding.

### Overturned

- None.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | Refreshed `origin/main` at `4e7b5e0d59be831453b5c34f5f1eb3a1daae1245` before branch creation. |
| Assessment ID scan | passed | Inspected all local and remote refs: `ASM-20260804-001` exists and `ASM-20260804-002` is explicitly reserved by another worktree; this baseline uses `ASM-20260804-003`. |
| Profile and plan review | passed | Current profile and `clean_target_head()` source evidence read directly. |
| Reproduction fixture | passed | Current behavior reproduced: `planned_action=add`, `apply_status=pending-validation`, `file_exists=true`, and `git check-ignore` matched `.gitignore:1:/.codex/*`. |
| Target critical route | passed | `check-all.sh` selects `validate-ai-context-target.py` for targets with `.dev/ai-context/provenance.yaml`. |

### Skipped Validation

- No remediation validation was run during this read-only baseline.

## Recommended Action Order

1. Add shared, exact-path Git-ignore observation for selected framework-managed package paths.
2. Preserve owner control by returning plan evidence and refusing apply before any target mutation while unresolved.
3. Bind the verified required path/component/ownership identity into the pending receipt, then reject it consistently in standalone target validation, critical gate, and provenance finalization.
4. Add Windows/POSIX and exact-case fixtures, then perform an independent verification assessment.

## Deferred Items

- No target-owned ignore-rule repair is selected; the plan must offer owner dispositions but never choose one automatically.
- REL-004, #92, and #94 remain excluded.

## Appendix

### Commands Run

```text
git fetch --all --prune
git log --all --oneline --grep='ASM-20260804-'
git grep -n -I -e 'ASM-20260804-' <all local and remote refs>
rg -n -C 8 -F '.codex' .ai/distribution/profiles/dotnet-backend.yaml
rg -n -C 10 -S 'porcelain|check-ignore|build_plan|apply_plan' .ai/scripts/ai_context_package_apply.py
disposable Python/Git fixture: plan -> apply -> git check-ignore -v --no-index -> git status --porcelain
```

### Notes

- The fixture used a committed target `.gitignore` containing `/.codex/*` and `!/.codex/agents/skills/**`; it never modified a user target or repository-owned ignore configuration.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260804-003/report.md`
- Stable finding references: `ASM-20260804-003#AIC-001`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-08-04-framework-managed-ignore-detection`
- Verification assessment: pending new ID allocation after remediation.
- Remediation intentionally not performed by this skill: `yes`
