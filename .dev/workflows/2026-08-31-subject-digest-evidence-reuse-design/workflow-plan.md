# Subject Digest Evidence Reuse Design Workflow

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-31-subject-digest-evidence-reuse-design`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-31-subject-digest-evidence-reuse-design`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `completed`
- `current_phase`: `closed`
- `artifact_root`: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design`
- `created_at`: `2026-08-31T20:02:51+08:00`
- `updated_at`: `2026-09-02T22:36:24+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: Issue #270 requires a safe content-equivalent evidence identity that avoids SHA-only revalidation without weakening exact-head or mutable-provider admission.
- Authorized remediation scope: create design documentation, examples, historical avoided-work analysis, and an HTML explanation for owner review.
- Exclusions: no current gate enablement, production validator or policy change, push, pull request, merge, release, publication, Issue closure, or terminal Project mutation.
- Completion criteria: repository-backed gate inventory; immediate-enable and dependency-first assessment; minimal versioned manifest and digest model; truthful rebind semantics; one proposed pilot; examples; visually verified HTML; validated workflow artifacts; explicit implementation and enablement approval gates.

## Artifact Contract

- Baseline assessment: not applicable; this workflow derives from Issue #270 owner decisions and preserves source evidence in the design report.
- Design report: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/design/subject-digest-evidence-reuse.md`
- Examples: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/examples/`
- Visualization: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/visuals/subject-digest-reuse.html`
- Tasks: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/tasks/`

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `GOV-017` | high | `ai-context-governance` | design-only, awaiting owner enablement decision | `GOV-017-design-subject-digest-reuse` | workflow validation, example parsing, HTML structure and visual QA |

## Stages And Checkpoints

1. Freeze Issue #270 decisions and repository/code-graph coverage evidence.
2. Inventory current gate identities and historical SHA-only rerun candidates.
3. Design minimal subject manifest, sensitivity classification, reuse eligibility, rebind behavior, dependency sequencing, and pilot.
4. Produce examples and HTML explanation; validate semantics and rendering.
5. Return to owner review without enabling reuse.

## Closure Checkpoint

- Completed action: delivered the subject-manifest design, nine behavior scenarios, three machine-readable examples, historical equivalence analysis, and a responsive HTML explanation.
- Validation completed: all 74 current registry gates appear in the decision table; five YAML files and the task JSON parse; workflow validation passes; `git diff --check` passes; desktop and 390-pixel browser QA show working scenario and strategy interactions without horizontal overflow.
- Git state: branch `codex/2026-08-31-subject-digest-evidence-reuse-design`, based on `main` at `c7f348694421048245da824dd79742372179f730`; the design checkpoint resolves through its containing commit and remains unpushed.
- Design disposition: complete Issues #267 and #268 prerequisites, then enable only `multi-hop-upgrade-transaction` as the first Issue #270 pilot and observe three qualifying head transitions before expansion.
- Remaining owner gates: accept or revise this design; separately authorize implementation of #267/#268 prerequisites and later authorize the #270 manifest/rebind implementation and pilot enablement.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-31-subject-digest-evidence-reuse-design` | `main@c7f348694421048245da824dd79742372179f730` | local design | containing commit | local only | `2026-09-02T22:36:24+08:00` | Preserve the validated owner-review design as a durable checkpoint | Keep #270 implementation and pilot enablement separate; use the online decision record and this commit as input to the new #267/#268 workflow |
