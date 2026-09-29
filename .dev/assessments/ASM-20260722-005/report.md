# dev-workflow Comparison And Post-v0.5 Backlog Intake

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260722-005`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-22`
- `created_at`: `2026-07-22T21:53:50+08:00`
- `updated_at`: `2026-07-22T21:53:50+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `79ac24dbd8be4b2385b9517fe35e727112fe007a`
- `previous_assessment`: none
- `workflow_refs`: `.dev/workflows/2026-07-22-post-v0-5-backlog-intake/workflow.yaml`

## Executive Summary

- Overall assessment: The current framework already resolves the external
  report's three primary WorkService execution risks through proactive workflow
  gates, owned tasks, commit checkpoints, and closing validation. Three bounded
  follow-ups remain useful: remove Node.js 20 artifact actions before the next
  release, evaluate optional issue and richer timeline metadata without making
  the portable core depend on one tracker, and make the legacy customized-target
  upgrade bootstrap more executable.
- Overall score: `8.8/10`
- Decision: `healthy-with-followups`
- Primary strengths: structural workflow gates, explicit task/commit evidence,
  provenance-aware three-way upgrades, and target-owned truth protection.
- Primary risks: two artifact actions still target Node.js 20; legacy targets
  without provenance require a manual bootstrap; useful WorkService metadata
  has no portable representation in the current dev-workflow templates.

## Scope

### Included AI Context Surfaces

- Supplied WorkService comparison report as attributed external evidence.
- Current `dev-workflow`, `ai-context-upgrader`, workflow/version policies,
  v0.5.0 migration guide, and GitHub Actions artifact steps.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- The private WorkService repository was not available and was not inspected.
- WorkService file counts, behavior history, and project-local validator state
  remain reviewer-supplied claims rather than reproduced repository facts.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: all product source and test implementation.
- Recommended skill: not applicable.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: the supplied comparison's architecture, task, commit, trigger,
  and migration observations before applying this repository's policy labels.
- Checks performed: separated reusable candidate improvements from WorkService-
  specific doctrine and identified claims requiring current file verification.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `ai-context-governance`,
  `ai-context-upgrader`, assessment intake, workflow artifact, version, boundary,
  and language policies.
- Checks performed: current template field scan, package migration boundary
  review, provenance/local-override review, workflow action inventory, and
  hosted v0.5.0 check-run annotation read-back.

### Delegation

- Sub-agents used: none.
- Assigned surfaces: not applicable.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| GitHub Actions API | run `29922585651`; captured in `evidence/github-actions/v0.5.0-node20-annotations.json` | immutable v0.5.0 run | both job annotations; job logs and other runs excluded | no source ownership inference | direct `.github/workflows/**` scan and recorded reproduction commands |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| External package | 1 report | human | WorkService comparison | attributed | SHA-256 `24A12C4FDA19FF8F7AAE6902E66C0D95F799BFBF2EF8BDC5CDF1CE710AAAB427` |
| `dev-workflow` | canonical spec, references, templates, wrappers | agent | portable | active | owns commit checkpoints but not issue/timeline enrichment |
| `ai-context-upgrader` | canonical spec, references, template, wrappers | agent | portable | active | preserves target truth through three-way reconciliation |
| GitHub workflows | 4 workflows | automation | source repo | active | three artifact-action call sites use two Node.js 20 action families |

## Strengths

1. The current workflow gate and task lifecycle structurally address the
   external report's missing-workflow, task ownership, and delayed-commit risks.
2. The v0.5.0 upgrader distinguishes reusable framework changes, target-owned
   truth, local overrides, and excluded source history before any write.
3. Existing commit subjects already accept issue-number scopes when an issue
   exists, so task metadata can be evaluated without changing commit syntax.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | Published workflows still call Node.js 20 artifact-action majors. | `package-candidate.yml` and `publish-release.yml` use `actions/upload-artifact@v4`; `publish-release.yml` uses `actions/download-artifact@v5`. `evidence/github-actions/v0.5.0-node20-annotations.json` preserves one warning for each action family from run `29922585651`. | GitHub currently forces Node.js 24, but Node.js 20 removal can turn future candidate or publication runs into failures. | Track a v0.6.0 blocker to upgrade to Node.js 24-native majors, verify runner compatibility, preserve artifact semantics, and require a warning-free hosted run. | `CI-001` / `ai-context-governance` |
| AIC-002 | MEDIUM | Useful WorkService issue-tracking and lifecycle timestamps have no field-level representation in current portable dev-workflow tasks. | Current task template has `created_at` and `updated_at`, but no `issue_tracking`, `started_at`, `completed_at`, `last_validated_at`, or `timezone`; commit checkpoints and result commits already exist. | Traceability can be weaker in issue-driven or regulated targets, but imposing one tracker or mandatory issue number would reduce portability. | Evaluate optional, profile-aware issue references and richer lifecycle timestamps with schema, state-transition, and compatibility rules before changing canonical templates. | `DEVWF-001` / `dev-workflow` plus governance |
| AIC-003 | MEDIUM | The upgrader safely preserves customizations, but a pre-governed customized target still needs an explicit manual provenance bootstrap before v0.5.0 automation. | v0.5.0 accepts exact v0.3.0-v0.4.2 sources; the guide routes v0.0.1 through manual v0.1.0/v0.2.0 reconciliation to governed v0.3.0. Missing provenance fails closed and local differences require reconciliation. | A WorkService-like target cannot safely use direct latest-package replacement; an incomplete inventory could lose framework-path customizations or misclassify target truth. | Add a reusable legacy-target intake packet and dry-run checklist that captures a rollback commit, credible base, target-only truth, framework-path overrides, unresolved collisions, and staged validation. | `UPG-001` / `ai-context-upgrader` plus governance |

## Baseline And Skill Comparison

### Confirmed

- The current dev-workflow has stronger gate, task, commit, and closure
  enforcement than the supplied WorkService generation.
- Current task artifacts lack issue-tracking and extended lifecycle timestamps.
- The v0.5.0 upgrade path protects local changes but does not automatically
  accept v0.0.1 or unknown provenance.

### Added By Repository-Aware Review

- The exact Node.js 20 warnings map to `actions/upload-artifact@v4` and
  `actions/download-artifact@v5`, not to the already-modern checkout/setup actions.
- Issue numbers must remain optional or profile-controlled in the portable core.

### Downgraded Or Deferred

- WorkService counts, task examples, and behavioral incidents are retained as
  external evidence because that private repository was not available.
- The richer WorkService review-report format is a candidate for later
  `DEVWF-001` evaluation, not a current defect by itself.

### Overturned

- None. The report's primary conclusions about the older WorkService generation
  are not contradicted; they are simply not independently reproduced here.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | pass | assessment subject pinned to clean `main@79ac24d` before workflow edits |
| Current template fields | pass | direct scan confirms commit fields and missing issue/timeline fields |
| Upgrade preservation | pass | version policy, upgrader references, source template, and v0.5.0 migration guide agree |
| Hosted warning attribution | pass | retained JSON records source run, both check IDs, verbatim messages, scope, exclusions, and reproduction commands |
| External package integrity | pass | evidence paths disable text normalization; archived Git blob and root intake digest both equal `24A12C4FDA19FF8F7AAE6902E66C0D95F799BFBF2EF8BDC5CDF1CE710AAAB427` |

### Skipped Validation

- WorkService repository inspection and target upgrade dry-run were not possible
  because that private target was outside this workspace.

## Recommended Action Order

1. Resolve `CI-001` before the next release publication.
2. Inventory a real WorkService baseline and execute `UPG-001` before applying
   any package to that target.
3. Deliberate `DEVWF-001` independently; adopt issue/timeline fields only with
   a portable optionality and compatibility contract.

## Deferred Items

- Actual WorkService upgrade execution belongs in a WorkService-owned workflow.
- Canonical dev-workflow template changes require a separate authorized workflow.

## Appendix

### Commands Run

```text
Get-FileHash -Algorithm SHA256 2026-07-22-dev-workflow-skill-comparison.md
git cat-file blob HEAD:<evidence-path>
rg -n "issue_tracking|started_at|completed_at|last_validated_at|timezone|commit_checkpoint" .ai/assets/skills/dev-workflow
rg -n "local_overrides|v0.0.1|v0.3.0|target-owned" .ai/assets/skills/ai-context-upgrader releases/v0.5.0/migration-guide.md
rg -n "upload-artifact|download-artifact" .github/workflows .ai/scripts/tests
gh api .../actions/runs/29922585651/jobs
gh api .../check-runs/<id>/annotations
```

### Notes

- Raw external evidence is preserved unchanged under `evidence/workservice/`.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260722-005/report.md`
- Stable finding references: `ASM-20260722-005#AIC-001` through `AIC-003`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-07-22-post-v0-5-backlog-intake`
- Verification assessment: pending `ASM-20260722-006`
- Remediation intentionally not performed by this skill: `yes`
