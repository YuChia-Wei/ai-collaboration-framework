# Repository Rename Identity And Link Baseline

## Metadata

- `assessment_id`: `ASM-20260809-001`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-09`
- `created_at`: `2026-08-09T19:57:58+08:00`
- `updated_at`: `2026-08-09T19:57:58+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `main`
- `subject_commit`: `e1dedd688707d84f5e7a26c7c7532f74a9860a94`
- `previous_assessment`: `none`
- `workflow_refs`: `2026-08-09-repository-rename-reconciliation`

## Executive Summary

- Overall assessment: the GitHub rename itself is healthy and provider redirects work, but the source repository has nine current operational files with eleven retired-name lines, one stale current fixture, no executable classification for 1,010 occurrence lines, and incomplete Project reconciliation for the only confirmed v0.12.0 work item.
- Overall score: `N/A`; this is a focused rename-reconciliation baseline rather than a whole-repository health score.
- Decision: `remediation-recommended` and already owner-authorized by Issue #150.
- Primary strengths: the canonical provider ID is stable, the old repository URL redirects with HTTP 301, local Git remotes already use the new coordinate, and current PR, Actions, Release, and release-asset URLs resolve under the new repository.
- Primary risks: stale operational links and source metadata, blind replacement of immutable history, a fixture with accidental retired identity, and no fail-closed control that distinguishes permitted history/compatibility from new drift.

## Scope

### Included AI Context Surfaces

- Root repository identity and Git remote evidence.
- `.ai/**` source-repository capability identity, distribution source metadata, and the release-closeout fixture.
- `.dev/**` provider policy, provider receipts, active lesson links, historical workflows, assessments, releases, and backlog evidence.
- `.github/ISSUE_TEMPLATE/config.yml` security-report link.
- GitHub repository, Issue #150, Project #3, PR, Actions, Release, redirect, security-link, and release-asset surfaces.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees other than explicitly scoped provider receipts

### Additional Exclusions

- Product, package, archive, technology-profile, namespace, and CLI identity decisions owned by #166.
- Broad `.ai`, `.dev`, and artifact inventories owned by #170, #171, and #172.
- Mutation of Git history, existing tags, Releases, or assets.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: all product source and product test trees.
- Recommended skill: `not-applicable`; this is repository AI-context and provider governance.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: pinned Git tree `e1dedd688707d84f5e7a26c7c7532f74a9860a94`, exact retired slug search, direct candidate-file reads, current Git remote, provider repository metadata, Issue/Project fields, and HTTP redirect headers.
- Checks performed: completeness and classification of every exact retired-name occurrence line; operational versus historical ownership; stale link and automation-input risk; provider endpoint continuity; fixture intent; and fail-open validation risk.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`, `ai-context-governance`, `AICTX-EVIDENCE-001`, workflow/assessment artifact policies, work-management lifecycle, distribution source-only exclusions, and Issue #150 taxonomy and authorization boundaries.
- Checks performed: direct file verification after discovery; historical evidence immutability; source-only versus portable boundaries; workflow and assessment persistence contract; Project lifecycle mapping; and explicit deferral of #166/#170/#171/#172 decisions.

### Delegation

- Sub-agents used: `no`.
- Assigned surfaces: none; all evidence gathering and synthesis were performed directly in the owning workflow.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| Codebase Memory MCP fast index | current workflow worktree, after bootstrap commit | re-indexed, but fast mode excluded `.ai/scripts/**`, `.ai/assets/**`, and `.claude/**` | code discovery only; not used for occurrence completeness | could not locate the new release-closeout function or establish Markdown/provider relationships | `git grep` pinned to the subject commit plus direct file reads |
| GitHub Project item projection | provider read-back at `2026-08-09T19:57:58+08:00` | current provider state | Issue #150 item and Project #3 fields | does not establish owner authorization or repository integration | Issue body, provider field list, local workflow, and Git evidence |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Current operational occurrences | 9 files / 11 occurrence lines | agent and human | source repository | remediation required | Security link, source coordinate, capability profile, provider config/schema, and active lesson links. |
| Source validation fixture | 1 file / 1 occurrence line | agent | source repository | disposition required | The old coordinate is unrelated to the tested path guard. |
| Generated provider receipts | 11 files / 62 occurrence lines | agent | source repository | retained projection | Time-pinned read-back receipts with source revisions and provider IDs. |
| Historical assessments | 78 files / 102 occurrence lines | agent and human | immutable evidence | retained | Subject-revision repository identity must not be rewritten. |
| Historical workflows | 59 files / 821 occurrence lines | agent and human | immutable evidence | retained | Largest class; bulk replacement would corrupt execution evidence. |
| Releases | 10 files / 11 occurrence lines | agent and human | immutable evidence | retained | Published coordinates remain factual at their publication boundary. |
| Historical backlog evidence | 2 files / 2 occurrence lines | agent and human | immutable evidence | retained | Explicit PR #10 evidence. |

## Strengths

1. GitHub reports stable repository ID `1209513501` / node ID `R_kgDOSBe2HQ` at the new `YuChia-Wei/ai-collaboration-framework` coordinate.
2. The retired repository page returns HTTP 301 to the new repository, including the security-advisory path.
3. The local `origin` fetch and push URLs already use the new HTTPS coordinate, and `main` matched fetched `origin/main` before branch creation.
4. Current PR, Actions, v0.11.0 Release, and all four release assets are exposed under the new repository URL without mutating the published release.
5. The repository already distinguishes source-only execution history and provider receipts from portable framework truth, which supports a narrow path-based classification contract.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | Nine current operational files contain eleven retired repository-name lines. | `old-name-inventory.yaml` rule `GOV007-CLASS-001`; direct reads of capability profile, distribution profile, provider config/schema, lesson indexes/record, and Issue template. | Security reports, package source metadata, repository-specific routing, provider automation, schema identity, and active evidence navigation continue to advertise the retired coordinate. | Update only these classified current-operational occurrences to `YuChia-Wei/ai-collaboration-framework`, preserving portable capability names and immutable evidence. | `ai-context-governance` / `GOV007-002` |
| AIC-002 | HIGH | The repository has 1,010 exact retired-name occurrence lines across 170 files but no fail-closed classification or drift validator. | Pinned `git grep` inventory; 946 lines are immutable assessment/workflow/release/backlog evidence and 62 are generated provider receipts. | A bulk rename would falsify evidence, while a simple blanket exemption would permit new operational drift. | Add a source-only machine-readable classification policy and validator that requires each retained occurrence to match exactly one permitted rule and rejects stale or unmatched rules. | `ai-context-governance` / `GOV007-003` |
| AIC-003 | MEDIUM | The release-closeout test fixture passes the retired repository coordinate even though the test asserts only that output cannot be written inside the primary worktree. | `.ai/scripts/tests/test_ai_context_release_closeout.py`; direct `plan_patch` read shows the output guard fails before repository validation or provider calls. | The fixture looks like redirect compatibility evidence but proves no redirect behavior, so future maintainers may preserve accidental drift. | Classify it as a current fixture and update it to the new coordinate. Keep redirect compatibility in the dedicated notice and validator fixture with explicit expected behavior. | `ai-context-governance` / `GOV007-002`, `GOV007-003` |
| AIC-004 | MEDIUM | Project #3 still shows #150 as `Inbox`; Priority, Owner review, Target release, and Published in are unset, the Project item title projection is stale, and Target release lacks a `v0.12.0` option. | `provider-before.yaml`; `gh project field-list` and `gh project item-list` read-back. | The selected release blocker is not visible in the active roadmap or lifecycle views, and provider state does not accurately represent authorized execution. | Set Status to `In progress`, Owner review to `Not required`, Published in to `Not yet published`, add/select `v0.12.0`, and apply the owner-selected Priority. Read back the item after mutation; do not infer integration from Project state. | `ai-context-governance` / provider reconciliation; owner selects Priority |

## Baseline And Skill Comparison

### Confirmed

- Independent review and repository policy agree that active operational coordinates must move to the new repository while historical evidence remains unchanged.
- Both passes identify lack of a classification-aware validator as the central recurrence risk.
- Both passes classify the existing release-closeout repository argument as a stale current fixture, not a redirect test.

### Added By Repository-Aware Review

- Generated provider mappings are time-pinned source-repository receipts and therefore remain byte-stable despite their retired URLs.
- The capability profile is repository-specific identity, but its capability slot names and canonical `software-development-orchestrator` identity remain portable and unchanged.
- #166/#170/#171/#172 cannot be closed or semantically decided by this remediation.

### Downgraded Or Deferred

- The signed-in security-report form is `owner-readback-required`; unauthenticated HTTP confirms redirect/login routing but not the authenticated form experience.
- Project Priority is deferred only until the owner responds; `P1 High` is recommended because #150 is the sole confirmed v0.12.0 blocker.

### Overturned

- The presence of the retired name in historical workflows, assessments, releases, provider receipts, and PR evidence is not itself a defect.
- No product, package, archive, technology-profile, namespace, or CLI rename is implied by the GitHub repository rename.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | passed | `main == origin/main == e1dedd688707d84f5e7a26c7c7532f74a9860a94` before branch creation; workflow branch created first. |
| Registry and wrapper parity | scoped / no drift found | No runtime wrapper contains the retired slug; the repository-specific capability profile owns the two profile identity lines. |
| Path and reference checks | passed for baseline inventory | 1,010 occurrence lines in 170 tracked files; classification rule counts sum exactly to both totals. |
| Schema / structured file parse | pending artifact validation | Baseline YAML and assessment artifacts must pass repository validators before commit. |
| Repository context checks | remediation required | Current provider endpoints work, but nine current operational files and Project state need reconciliation. |

### Skipped Validation

- HTTPS and SSH clone probes, release-download HEAD, and full after-state verification are reserved for `GOV007-004` after repository remediation.
- Signed-in security-report form interaction is `owner-readback-required`; no browser/account mutation was authorized or performed.
- No product tests or spec-compliance gate apply to this source-governance change.

## Recommended Action Order

1. Update the eleven current operational lines and the one current fixture while preserving all classified historical and generated evidence.
2. Add the source-only compatibility notice and classification policy.
3. Implement and test the fail-closed retired-name validator, then integrate it into the source-governance hosted surface.
4. Reconcile Project fields without treating provider state as authorization or integration truth.
5. Run independent post-remediation assessment and provider after-state probes before the no-ff merge-commit PR integration.

## Deferred Items

- Product, package, archive, technology-profile, namespace, and CLI identity: Issue #166.
- Broader `.ai`, `.dev`, and artifact/package inventories: Issues #170, #171, and #172.
- Signed-in security-report form: repository owner read-back after the new link lands.
- Issue #150 Project Priority: owner decision; recommended value `P1 High`.

## Appendix

### Commands Run

```text
git fetch origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git remote -v
git grep -n -I -F 'ai-collaboration-prompts-dotnet-backend' e1dedd688707d84f5e7a26c7c7532f74a9860a94 --
gh issue view 150 --repo YuChia-Wei/ai-collaboration-framework --json ...
gh project list --owner YuChia-Wei --format json
gh project field-list 3 --owner YuChia-Wei --format json
gh project item-list 3 --owner YuChia-Wei --format json --limit 200
gh api repos/YuChia-Wei/ai-collaboration-framework
gh pr list --repo YuChia-Wei/ai-collaboration-framework --state all --limit 1
gh run list --repo YuChia-Wei/ai-collaboration-framework --limit 1
gh release view v0.11.0 --repo YuChia-Wei/ai-collaboration-framework
curl.exe --head --max-redirs 0 <retired-and-current-urls>
```

### Notes

- `gh` and network probes were executed outside the sandbox as required by the owner.
- Raw HTTP cookies and unrelated headers were not retained in repository evidence.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260809-001/report.md`
- Stable finding references: `ASM-20260809-001#AIC-001` through `ASM-20260809-001#AIC-004`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-08-09-repository-rename-reconciliation`
- Verification assessment: planned `ASM-20260809-002`
- Remediation intentionally not performed by this skill: `yes`
