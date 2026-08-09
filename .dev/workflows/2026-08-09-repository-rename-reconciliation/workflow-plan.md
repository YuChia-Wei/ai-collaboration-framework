# Repository Rename Identity And Link Reconciliation

## Workflow Metadata

- `workflow_id`: `2026-08-09-repository-rename-reconciliation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-08-09-repository-rename-reconciliation-closeout`
- `base_branch`: `main`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-08-09-repository-rename-reconciliation`
- `created_at`: `2026-08-09T19:49:54+08:00`
- `updated_at`: `2026-08-09T21:39:20+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Authorization And Work-Item Binding

- Work item: [GitHub Issue #150](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/150).
- Authorization: Issue #150 records the repository owner's explicit authorization for a dedicated workflow, inventory, remediation, validators, provider read-back, Issue/Project reconciliation, and a pull request. The current owner request on 2026-08-09 directs execution and requires pauses for material owner decisions.
- Subject baseline: local `main` and fetched `origin/main` were both read back at `e1dedd688707d84f5e7a26c7c7532f74a9860a94` before branch creation.
- Pull-request gate: required; no direct mutation of `main`.
- Prohibited mutations: provider rename repetition, Git history rewrite, existing tag/Release/asset mutation, and automatic product/package/archive/profile/namespace/CLI renaming.

## Objective And Scope

- Problem statement: the GitHub repository is now `YuChia-Wei/ai-collaboration-framework`, but current operational surfaces still contain the retired repository identity while historical, compatibility, generated, fixture, and unrelated occurrences require explicit disposition instead of bulk replacement.
- Authorized remediation scope: build a reproducible old-name inventory; classify every occurrence; correct current operational repository coordinates, security links, automation inputs, source repository metadata, and source-repository capability identity; disposition fixtures; add a compatibility notice and fail-closed drift validator; preserve before/after provider receipts; reconcile Issue and Project state; submit the delivery through a pull request.
- Exclusions: product, archive, package, technology-profile, namespace, and CLI identity decisions; #166 implementation; broad `.ai`, `.dev`, or distribution inventory owned by #170, #171, and #172; existing tags, Releases, assets, and immutable historical evidence.
- Completion criteria: every Issue #150 acceptance surface has a classified disposition and evidence; all authorized operational changes and validator tests pass; unautomated surfaces are explicitly `owner-readback-required`; baseline and post-remediation assessments reconcile all selected findings; workflow commits and hosted checks pass; provider and repository states are read back separately.

## Delivery Cohesion And Proportionality

- Four substantive tasks share one repository-rename outcome, branch, reviewer, v0.12.0 release gate, validation boundary, and rollback unit, so they remain one workflow and pull request.
- Issues #170, #171, #172, and #166 remain independent deliveries because they have broader inventory or owner-decision boundaries and are not v0.12.0 blockers by default.
- Workflow mode preserves cross-surface classification, remediation, independent verification, external provider reconciliation, and failure-recovery state that an Issue or commit alone cannot carry.
- The owner explicitly selected merge-commit integration on 2026-08-09. The PR must use a true no-fast-forward merge commit; fast-forward, rebase-and-merge, and squash merge are prohibited for this delivery. The repository rename and provider/security reconciliation form the external lifecycle boundary retained by that merge node.

## Artifact Contract

- Baseline assessment: `.dev/assessments/ASM-20260809-001/assessment.yaml`.
- Reproducible occurrence inventory: `.dev/workflows/2026-08-09-repository-rename-reconciliation/evidence/old-name-inventory.yaml`.
- Provider before receipt: `.dev/workflows/2026-08-09-repository-rename-reconciliation/evidence/provider-before.yaml`.
- Provider after receipt: `.dev/workflows/2026-08-09-repository-rename-reconciliation/evidence/provider-after.yaml`.
- Remediation report: `.dev/workflows/2026-08-09-repository-rename-reconciliation/reports/remediation-report.md`.
- Verification assessment: `.dev/assessments/ASM-20260809-002/assessment.yaml`.
- Tasks: `.dev/workflows/2026-08-09-repository-rename-reconciliation/tasks/`.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| `ASM-20260809-001#AIC-001` | HIGH | `ai-context-governance` | remediate within #150 boundaries | `GOV007-002` | targeted references and repository gates |
| `ASM-20260809-001#AIC-002` | HIGH | `ai-context-governance` | implement classification policy and validator | `GOV007-003` | positive, negative, stale-rule, and overlap tests |
| `ASM-20260809-001#AIC-003` | MEDIUM | `ai-context-governance` | update current fixture and isolate real redirect compatibility | `GOV007-002`, `GOV007-003` | fixture intent and validator tests |
| `ASM-20260809-001#AIC-004` | MEDIUM | `ai-context-governance` | reconcile provider fields and retain before/after receipts | `GOV007-004` | Project and Issue read-back |

## Stages And Checkpoints

1. Freeze GitHub, Git, redirect, and repository occurrence evidence; produce the baseline inventory and assessment.
2. Apply the smallest authorized operational identity, fixture, and compatibility remediation without crossing #166/#170/#171/#172 boundaries.
3. Add the fail-closed retired-name validator, exception/classification contract, and deterministic tests.
4. Run repository and provider verification, create the independent post-remediation assessment, and reconcile every finding.
5. Create compliant workflow commits, push, open the #150 pull request, read back hosted gates, and complete terminal Issue/Project reconciliation only after accepted integration.

## Boundary Decisions And Owner Gates

- The new canonical repository coordinate is `YuChia-Wei/ai-collaboration-framework`; the old repository URL may remain only as classified compatibility or immutable historical evidence.
- Portable capability names must describe reusable capability, not the GitHub repository provider name. Source-repository-only IDs may adopt the new repository identity when their contract is explicitly repository-specific.
- Product, package, archive, technology profile, namespace, and CLI identity decisions are deferred to #166 or its owning follow-ups and are not inferred from the repository rename.
- #170, #171, and #172 may consume this workflow's inventory evidence, but this delivery does not claim their broader inventories complete.
- Any occurrence whose disposition would change product/package bytes or semantic identity is paused for owner decision or deferred with an explicit owner and next action.
- Any provider surface that cannot be verified safely through read-only automation is recorded as `owner-readback-required`; this label is not treated as a pass.
- PR integration topology is an owner decision: use a merge commit and read back the resulting two-parent commit before claiming integration.

## Validation Selection

- Old-name inventory reproduction and classification schema: selected.
- Repository identity validator positive/negative fixtures: selected.
- AI-context, source-governance, workflow, assessment, structured-file, reference, and Git-diff checks: selected.
- Provider HTTPS/SSH clone, redirect, Issues, PRs, Actions, Projects, Releases, security-report link, and release-download coordinate read-back: selected where read-only automation is available; otherwise `owner-readback-required`.
- Spec compliance: `not-applicable`; no problem frame, requirement, target profile, or owner decision selected it.
- Product unit/integration tests: `not-applicable`; this delivery changes repository governance, configuration, documentation, and source-side validation rather than product code.
- Existing tag, Release, or asset mutation: prohibited and therefore not selected.

## Resume Checkpoint

- Last completed action: merged PR #173 through verified two-parent commit `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005`, closed Issue #150 as completed, and read Project Status `Done` while retaining `Not yet published`.
- Current task: none; `GOV007-004` is completed.
- Exact next action: integrate this records-only closeout through a merge commit; no workflow execution remains.
- Validation already completed: all local gates listed above; owner-approved prerequisite correction 14/14, 4/4, and 5/5; fresh runs `31316137412`, `31316137415`, and `31316137431` passed at head `a6e01dea27f53fdfe3659e119ceb25fe952af25e`; merge commit has exactly two parents; Issue #150 and Project #3 terminal fields were read back.
- Git state: `codex/2026-08-09-repository-rename-reconciliation-closeout` from integrated `main@18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005`.
- Branch history and checkpoint handoffs: segment 1 integrated through PR #173; segment 2 is the records-only terminal continuation from the updated target.
- Blockers or unresolved decisions: none. Signed-in security-report form usability remains `owner-readback-required`, and credentialed SSH clone remains `blocked-by-environment`; neither is reported as passed. Product/package/archive/profile/CLI identity remains outside this workflow.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-09-repository-rename-reconciliation` | `main@e1dedd688707d84f5e7a26c7c7532f74a9860a94` | merge-commit integration | `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005` | [PR #173](https://github.com/YuChia-Wei/ai-collaboration-framework/pull/173) / `main` | `2026-08-09T21:36:23+08:00` | Integrate the authorized reconciliation after fresh hosted checks. | Continue records-only closeout from updated `main`. |
| 2 | `codex/2026-08-09-repository-rename-reconciliation-closeout` | `main@18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005` | terminal records | `18aeaef2732ecdd4db84fceae8ef9fd0eb9e7005` | local / closeout PR pending | `2026-08-09T21:39:20+08:00` | Retain final GitHub, Issue, Project, and merge-topology read-back without changing implementation. | Integrate the records-only closeout through a merge commit. |
