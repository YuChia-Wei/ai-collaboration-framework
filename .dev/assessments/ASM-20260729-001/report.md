# v0.7.0 Public Release Body Source Contract Verification

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260729-001`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-29`
- `created_at`: `2026-07-29T16:03:20+08:00`
- `updated_at`: `2026-07-29T16:03:20+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `YuChia-Wei/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `codex/2026-07-29-v0-7-0-public-release-body-correction`
- `subject_commit`: `cbe1553f0fc30a856a35e85ec17ecd8cd91838d2`
- `previous_assessment`: no durable baseline exists for the transient
  `V070-*` finding set; related candidate verification is `ASM-20260728-001`.
- `workflow_refs`: `2026-07-29-v0-7-0-public-release-body-correction`

## Executive Summary

- Overall assessment: the committed source contract is phase-correct and
  fail-closed for finalization. It deterministically renders the published
  v0.7.0 body from current published facts and rejects the still-hosted
  candidate-only body.
- Overall score: `9.0/10`
- Decision: `healthy-with-followups`
- Primary strengths: immutable hosted facts are frozen before mutation;
  published rendering requires tag, peeled commit, successful run, public URL,
  explicit published status, and phase-owned source sections.
- Primary risk: the live public Release body is still stale. This verification
  proves that condition is detected; it does not claim the external correction
  has already occurred.

## Scope

### Included AI Context Surfaces

- v0.7.0 release record, authored release notes, and phase command contract.
- Source-only renderer and release-state validator.
- Release publication workflow contract and the active governance workflow,
  task, and bounded evidence.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- `.ai/scripts/tests/**` implementation; only recorded test-command outcomes
  were used as validation evidence.
- Git tags, GitHub Release assets, and GitHub Issues/Projects resources.
- Any GitHub write operation.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and test implementation trees.
- Recommended skill: not applicable.

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used: the frozen hosted snapshot
  `V070BODY-001-hosted-before.json`, current `release.yaml` and
  `release-notes.md`, and the live read-only finalization attempt.
- Checks performed: compared the non-draft published Release, annotated tag,
  peeled commit, and four asset digests against body claims; rendered the
  published body from the subject commit and checked that it contains
  `Published.` while omitting `not tagged or published` and
  `Not published.`.

### Pass B: Repository-Aware Skill Review

- Policies and skills used: `ai-context-auditor`,
  `ai-context-governance`, assessment artifact policy, workflow plan, task,
  release phase-check contract, and source-only package boundary.
- Checks performed: confirmed that finalization selects
  `render_published_body`, verifies any supplied body matches that renderer,
  and uses the hosted exact-body check. Confirmed published-mode inputs fail
  closed without published tag/commit/run/URL facts or without required
  phase-owned sections.

### Delegation

- Sub-agents used: none.
- Assigned surfaces: none.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| codebase-memory-mcp | pre-remediation index; not used as proof | stale for subject changes | prior symbol discovery only | Markdown and current dirty/commit state | direct file reads and Git evidence |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Release record | 3 files | agent and human | v0.7.0 release truth | active | published facts are source-owned |
| Release tooling | 2 files | agent-facing | source-only validation | remediated | excluded from downstream payload |
| Workflow evidence | 2 JSON files | governance | active correction workflow | active | frozen hosted baseline and expected negative result |
| Runtime wrappers | not changed | agent-facing | skill routing | unchanged | no wrapper drift introduced |

## Strengths

1. The exact current rendered published body has SHA-256
   `6e2b2eb1c4b6b95a7bd8e7acf678b1d8cbde22d492bbed9a454d56d74ed3c298`;
   it contains published-phase truth and not the frozen candidate-only claims.
2. The source contract preserves the immutable tag and asset boundary: it only
   reads hosted state and fails before any mutation when body semantics drift.
3. The package projection test records that both release-body scripts,
   test implementations, and workflow artifacts remain outside downstream
   payload selection.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| `VFY-001` | resolved-high | Published rendering now requires published registry facts and rejects candidate-only `not published` or terminal-unperformed claims. | renderer lines 18-24 and 119-152; committed focused renderer suite 8/8 | Removes the false-positive source contract. | Retain published mode as the sole finalization renderer. | `ai-context-governance` |
| `VFY-002` | resolved-high | Finalization now derives its expected body from `render_published_body` and rejects a supplied bypass body. | validator lines 527-546 and 693-706; committed release-state suite 24/24 | Hosted byte equality can no longer validate tagged candidate prose as finalization truth. | Keep finalization hosted validation fail-closed. | `ai-context-governance` |
| `VFY-003` | resolved-high | Remediated tooling and workflow evidence remain source-only. | committed package projection suite; task validation ledger | Avoids silently changing v0.7.0 downstream bytes or scope. | Stop and request owner direction if a later payload check contradicts this proof. | `ai-context-governance` |
| `VFY-004` | HIGH | The live body remains the frozen candidate body. The independent hosted finalization command fails with `hosted release body differs from governed rendered body`. | before snapshot SHA-256 `2e121c416198196e6d9006835eed2c7d256668d95194de026e2541557892d649`; live read-only command | Public release semantics are still incorrect until the authorized body-only correction occurs. | Integrate source contract, render and review exact body from updated main, then perform the bounded body-only mutation and invariant read-back. | `ai-context-governance` |

## Baseline And Skill Comparison

### Confirmed

- The hosted body contradicts non-draft publication, annotated tag, peeled
  commit, and four uploaded asset facts.
- The public body must not be treated as corrected before an online read-back.

### Added By Repository-Aware Review

- Finalization must not accept `--rendered-body` as an alternate authority.
  The committed validator now proves supplied content equals the published
  renderer before calling the hosted check.

### Downgraded Or Deferred

- No package leakage was observed. The source-only package proof is accepted
  for this stage; it is not a claim about reissued or changed v0.7.0 bytes.

### Overturned

- The prior finalization pass is not evidence of public-body truth. It only
  passed the tagged-candidate byte-equality contract that this remediation
  replaces.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state at audit start | passed | clean subject checkpoint `cbe1553` |
| Published renderer | passed | deterministic SHA-256 above; published terms present and stale terms absent |
| Hosted finalization check | expected-fail | read-only GitHub GET returned body mismatch; not counted as passed |
| Focused renderer suite | passed | 8/8 recorded in the committed task evidence |
| Focused release-state suite | passed | 24/24 recorded in the committed task evidence |
| Source-only package projection | passed | committed package suite evidence |
| Workflow artifact validation | passed | 48 post-adoption workflows, 68 indexed directories, 41 backlog items |
| AI-context validation | passed | active indexes, canonical skills, wrappers, language policy, owned rules, manifests, and mappings passed |

### Skipped Validation

- The auditor did not scan test implementation or product code.
- No aggregate critical gate was run by this audit; aggregate validation belongs
  to the exact source and closure commits.
- No GitHub mutation was attempted.

## Recommended Action Order

1. Preserve `VFY-004` as active until hosted read-back proves the corrected
   body and immutable invariants.
2. Integrate the source checkpoint through the required ready pull request.
3. Create a continuation branch from updated `main`, render and word-check
   the exact body, then edit only the v0.7.0 GitHub Release body.
4. Read back Release identity, tag object, peeled commit, asset names, and
   digests before closing the workflow.

## Deferred Items

- Broader `REL-004`, roadmap allocation, successor release work, and tracker
  provider adoption remain outside this verification.

## Appendix

### Commands Run

```text
git status --short
git rev-parse HEAD
rg -n -C 2 -e PUBLISHED_FORBIDDEN -e PUBLISHED_REQUIRED -e assert_published_body_source -e render_published_body -e "finalization rendered body differs" .ai/scripts/render-ai-context-release-notes.py .ai/scripts/validate-ai-context-release-state.py
python -c <render published v0.7.0 body and inspect digest/forbidden terms>
python .ai/scripts/validate-ai-context-release-state.py --phase finalization --version v0.7.0 --hosted
```

### Notes

- The hosted command was run with the unavailable localhost proxy variables
  removed only for that child process. It was read-only and intentionally failed
  because the public body has not yet been changed.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260729-001/report.md`
- Stable finding references: `ASM-20260729-001#VFY-001` through `VFY-004`
- Remediation owner: `ai-context-governance`
- Related remediation workflow:
  `2026-07-29-v0-7-0-public-release-body-correction`
- Verification assessment: `ASM-20260729-001`
- Remediation intentionally not performed by this skill: `yes`
