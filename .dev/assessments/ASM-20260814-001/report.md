# CLI Execution Routing Contract Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260814-001`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-14`
- `created_at`: `2026-08-14T22:38:38+08:00`
- `updated_at`: `2026-08-14T22:38:38+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `codex/2026-08-14-environment-execution-routing`
- `subject_commit`: `cca50f67f8a8a460a78af95820cdddd5781ec71b`
- `previous_assessment`: `not-applicable; GitHub Issue #210 is the approved design baseline`
- `workflow_refs`: `2026-08-14-environment-execution-routing`

## Executive Summary

- Overall assessment: `verified-ready-for-pull-request`.
- Overall score: `9/10` for the bounded Issue #210 surface.
- Decision: `healthy-with-followups`.
- The fixed subject defines only CLI execution routing after higher-priority policy has already selected CLI. It does not claim authority over connectors, CI, external tasks, browsers, or delegation.
- The portable contract and schema contain no populated personal route. A concrete per-clone record is accepted only at `.dev/ai-context/local/cli-execution-routing.yaml` after explicit consent and only while the path remains ignored, untracked, unstaged, non-symlinked, structurally valid, and free of forbidden sensitive fields.
- The current local record is ignored and untracked. Source validation read it as four valid local CLI routes without exposing it to Git or package projection.
- Windows host and explicit `Ubuntu-24.04` focused suites each passed 9/9 against the fixed subject. The source validator and committed package lifecycle projection also passed.
- No blocking or high-severity regression was identified. Hosted pull-request checks, merge, downstream adoption, and any release or publication remain separate gates.

## Scope

### Included AI Context Surfaces

- `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md` and `.ai/assets/shared/cli-execution-routing.schema.yaml`.
- `.ai/scripts/ai_context_cli_routing.py`, source/target validator integration, and focused context tests.
- `.gitignore`, root/runtime agent guidance, init/upgrader rules, package profile, and human-facing guides.
- Workflow #210 remediation records through fixed commit `cca50f67`.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- Non-CLI capability selection and routing.
- Personal secret, credential, session, username, endpoint, and approval-message values.
- Downstream target adoption, release, tag, publication, and hosted pull-request state.

### Code Review Handoff

- Requested: `no`.
- Paths not scanned: product source and product test implementation.
- Recommended skill: not applicable; this is AI-context governance verification.

## Methodology And Evidence

### Pass A: Independent Baseline

- Fixed the subject at clean tracked commit `cca50f67f8a8a460a78af95820cdddd5781ec71b` before assessment writes.
- Compared the contract and schema against least-authority, data-only local configuration, explicit-consent, deterministic fallback, and execution-evidence separation principles.
- Verified the exact ignore rule, absence of tracked local files, and current ignored-directory status using Git-native commands.
- Ran the same focused GWT suite on Windows host Python and outside the sandbox in WSL distribution `Ubuntu-24.04`.

### Pass B: Repository-Aware Skill Review

- Applied repository AI-context boundary, assessment, workflow, package, init, upgrade, and Git policies.
- Confirmed runtime wrappers stay thin and point to canonical assets.
- Confirmed local values are excluded from package selection while the portable validator and contract assets remain distributed.
- Treated saved readiness or route state as configuration only, never as evidence that a command ran or passed.

### Delegation

- Sub-agents used: `no`.
- Assigned surfaces: none; the auditor performed the fixed-subject read-back directly.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase knowledge graph | refreshed at the assessment subject checkout | fresh, but configured to exclude `.ai/scripts`, `.ai/assets`, `.claude`, and `.dev/ai-context/local` | useful for repository orientation only | new routing implementation, Markdown contracts, ignored local state, and wrapper parity | exact Git diff, tracked files, focused searches, and executable validators were authoritative |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Canonical CLI contract | 2 files | agents and validator authors | portable | verified | no populated local defaults |
| CLI routing validator | 1 module plus 2 entrypoints | source and downstream targets | portable | verified | fail-closed local-state checks |
| Local binding | 1 ignored per-clone file | this machine only | personal | verified local | four routes; untracked and excluded from package truth |
| Init/upgrader/runtime guidance | canonical specs, thin wrappers, guides | downstream agents and humans | portable | verified | init does not create; upgrade does not read or migrate local values |
| Distribution profile | lifecycle component entries and local exclusion | package builder | portable | verified | portable validator included; `.dev/ai-context/local/**` excluded |

## Strengths

1. The contract begins only after CLI has been selected, preventing a personal record from overriding connector-first or other capability-owned policy.
2. Personal route data has one conventional ignored location and cannot become authoritative when tracked, staged, unignored, or behind a symlink boundary.
3. The schema admits only four CLI surfaces and four CLI selectors; a connector surface or selector is rejected by executable tests.
4. Persistence requires explicit consent and records only route facts after successful recovery; forbidden sensitive field names are recursively rejected.
5. Readiness, saved routing, and actual execution receipts remain separate, reducing false claims that configuration proves success.
6. Windows and named-distribution WSL validation exercise the same portable contract without promoting this machine's values into repository truth.

## Findings

No new blocking finding.

### Issue Finding Reconciliation

| Finding | Before severity | Verification status | Evidence | Residual |
| --- | --- | --- | --- | --- |
| `Issue-210-contract` | HIGH | `addressed` | Canonical CLI-only contract/schema plus 9/9 positive and fail-closed GWT cases on Windows and Ubuntu-24.04. | Future incompatible schema changes require versioned migration. |
| `Issue-210-local-persistence` | HIGH | `addressed` | Exact `/.dev/ai-context/local/` ignore rule; local file is ignored and untracked; validator enforces consent, sensitive-field, staged/tracked, retry, and symlink gates. | The record remains per clone and must be revalidated when environment facts change. |
| `Issue-210-downstream` | HIGH | `addressed` | Init/upgrader contract, target validator integration, package exclusion, and focused committed package projection passed. | No downstream repository adoption was exercised in this workflow. |

### Observed Non-Blocking Limitations

- The local record is validated structurally and by current readiness constraints, but it is not an execution receipt and cannot guarantee that a future command will succeed.
- A previous full `validate-ai-context.py` attempt inside Ubuntu-24.04 timed out after 124 seconds and remains a timeout. The bounded WSL routing suite passed 9/9; the full source validator passed on Windows host Python.
- Hosted checks and branch-protection gates cannot be verified until the pull request exists.

## Baseline And Skill Comparison

### Confirmed

- The portable/local boundary, explicit-consent rule, secret exclusion, and deterministic fallback design are sound for the requested CLI-only scope.
- Git ignore and package exclusion are necessary controls, not documentation-only conventions.

### Added By Repository-Aware Review

- Init must create only the ignore boundary; upgrade must preserve ignored state without reading or migrating it.
- Runtime wrappers must remain thin and package projection must carry the canonical validator while excluding all personal values.

### Downgraded Or Deferred

- Downstream adoption is a follow-up rather than a defect in the source contract.
- Hosted checks, merge, Issue closure, release, and publication are lifecycle gates outside this fixed-subject assessment.

### Overturned

- None.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git subject/state | passed | fixed `cca50f67`; tracked worktree clean before assessment writes |
| Local ignore/tracking boundary | passed | `git check-ignore -v` resolves `.gitignore:353`; `git ls-files .dev/ai-context/local` is empty; ignored status reports only `!! .dev/ai-context/local/` |
| Windows CLI routing GWT | passed | 9/9 in 3.154 seconds, outside sandbox |
| Ubuntu-24.04 CLI routing GWT | passed | 9/9 in 0.662 seconds, explicit named distribution outside sandbox |
| Source AI-context validator | passed | 27 indexes, 17 skills, 389 language-policy files, 35 manifests, 4 local CLI routes, and remaining governed counts passed |
| Committed package lifecycle projection | passed | focused real component-matrix test 1/1 in 24.846 seconds |
| Contract/schema content | passed | CLI-only surfaces/selectors, exact local path, explicit consent, sensitive-field exclusions, and execution-evidence separation confirmed |
| Hosted pull-request checks | deferred | pull request did not exist at the fixed-subject assessment point |

### Skipped Or Failed Validation

- The earlier full Ubuntu-24.04 source validator timeout remains failed-by-timeout and was not relabeled as a pass.
- Product code/tests, downstream repository adoption, hosted checks, release, and publication were outside assessment scope.

## Recommended Action Order

1. Reconcile this verification assessment into workflow `2026-08-14-environment-execution-routing`.
2. Validate assessment/workflow artifacts and the complete `main..HEAD` commit range.
3. Push the workflow branch and open a ready pull request to `main` using merge-commit topology because the branch contains durable owner-review and cross-host checkpoints.
4. Merge only after hosted checks and review gates pass with an unchanged head.
5. Keep Issue closure, downstream adoption, release, and publication as separate decisions.

## Deferred Items

- Downstream repository adoption evidence.
- Hosted pull-request checks and remote merge read-back.
- Issue closure, release, tag, and publication.

## Appendix

### Commands Run

```text
git diff --stat main...HEAD
git diff --name-status main...HEAD
git rev-parse HEAD
git check-ignore -v .dev/ai-context/local/cli-execution-routing.yaml
git ls-files .dev/ai-context/local
git status --short --ignored .dev/ai-context/local
py -3 .ai/scripts/tests/test_cli_execution_routing.py -q
wsl.exe -d Ubuntu-24.04 -- bash -lc "cd /mnt/c/Github/YuChia/ai-collaboration-prompts-dotnet-backend && python3 .ai/scripts/tests/test_cli_execution_routing.py -q"
py -3 .ai/scripts/validate-ai-context.py
py -3 .ai/scripts/tests/test_ai_context_packaging.py DeterministicPackageGwtTests.test_gwt_000a_given_real_component_matrix_when_payload_is_projected_then_both_mandatory_cores_keep_their_capabilities -q
rg -n "local/cli-execution-routing|local_cli|CLI_EXECUTION|non-CLI|connector" .ai/scripts/tests/test_cli_execution_routing.py .ai/scripts/tests/test_ai_context_packaging.py
rg -n "symlink|gitignore|consent|forbidden|surface|selector|tracked|staged" .ai/scripts/ai_context_cli_routing.py
rg -n "CLI-EXECUTION-ROUTING|cli-execution-routing|ai_context_cli_routing|.dev/ai-context/local" .ai/distribution/profiles/dotnet-backend.yaml .ai/scripts/tests/test_ai_context_packaging.py .ai/assets/skills/ai-context-init .ai/assets/skills/ai-context-upgrader
```

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260814-001/report.md`
- Verified findings: `Issue-210-contract`, `Issue-210-local-persistence`, `Issue-210-downstream`
- Owning workflow: `2026-08-14-environment-execution-routing`
- Remediation performed by this verification pass: `no`; the subject commit was fixed before the assessment was written.
- Pull-request readiness: `yes`, subject to artifact/range validation.
- Hosted integration, Issue closure, release, or publication verified: `no`.
