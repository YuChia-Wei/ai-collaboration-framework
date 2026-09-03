# GOV-017 Subject-Digest Evidence-Reuse Implementation Plan

## Template Metadata

- `template_id`: `ai-context-governance-maintenance-workflow-plan`
- `template_version`: `1.2.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-03-subject-digest-evidence-reuse-implementation`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-09-03-subject-digest-evidence-reuse-implementation`
- `base_branch`: `main`
- `base_commit`: `34893ab7021d2119200a3b9ca153325a4d9dcbb8`
- `design_commit`: `4e0e677a08b0bdc819460a1afe6ec185e7440fff`
- `branch_segment`: `1`
- `status`: `in_progress`
- `current_phase`: `remediation`
- `artifact_root`: `.dev/workflows/2026-09-03-subject-digest-evidence-reuse-implementation`
- `created_at`: `2026-09-03T09:19:06+08:00`
- `updated_at`: `2026-09-03T09:55:12+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: SHA-only invalidation forces expensive eligible evidence to rerun after history-only changes even when the complete applicable subject is unchanged.
- Authorized remediation scope: implement Issue #270's approved manifest, digest, rebind, deterministic fixture, and single-pilot behavior after merged Issues #267 and #268.
- Authorization source: the owner resumed this conversation on 2026-09-03 with `267/268 已完成，這邊可以繼續了`, following the approved design and dependency-first sequence.
- Exclusions: push, pull request, merge, Issue or Project terminal mutation, allowlist expansion beyond `multi-hop-upgrade-transaction`, tag, release, publication, or historical backfill.
- Completion criteria: every GOV017 acceptance is evidenced; the pilot is the only subject-digest-enabled gate; fresh exact-head, hosted, provider, tag/release, and mutable-state gates remain non-replaceable.

## Authority And Preflight

- Live provider read-back on 2026-09-03 found Issue #270 open in Project status `Inbox`; its body remains the acceptance authority.
- GitHub PR #281 merged Issues #267 and #268 into `main@34893ab7021d2119200a3b9ca153325a4d9dcbb8`; local `main` was fast-forwarded to that commit before this branch was created.
- The completed design workflow is preserved at `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/` and cherry-picked as `4e0e677a08b0bdc819460a1afe6ec185e7440fff`.
- A moderate code-graph index named `ai-collaboration-prompts-dotnet-backend` contains 40,255 nodes and 87,223 edges but explicitly excludes `.ai/scripts`, `.ai/assets`, and design examples; tracked-file fallback is authoritative for those excluded paths.

## Artifact Contract

- Approved design: `.dev/workflows/2026-08-31-subject-digest-evidence-reuse-design/design/subject-digest-evidence-reuse.md`
- Acceptance ledger: `.dev/workflows/2026-09-03-subject-digest-evidence-reuse-implementation/acceptance-ledger.gov-017.yaml`
- Tasks: `.dev/workflows/2026-09-03-subject-digest-evidence-reuse-implementation/tasks/`
- Final implementation report: this plan's completion summary and acceptance projection.

## Stages And Checkpoints

1. Implement and validate the canonical subject manifest, classification authority, and digest sealing.
2. Implement fail-closed final-head rebind plus deterministic identity/drift fixtures and incident falsification.
3. Enable only `multi-hop-upgrade-transaction`, run the governed pilot, and record the first qualifying transition without expanding the allowlist.

These three tasks retain distinct state: manifest identity can complete before rebind is admissible; rebind can complete before any current gate is enabled; pilot execution and observation can be disabled without removing the shared contract.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| GOV017-F1 canonical subject identity is absent | high | `slice-implementer` | implement | `GOV017-subject-manifest` | focused manifest/schema tests and closure resolution |
| GOV017-F2 final-head rebind is absent | high | `slice-implementer` | implement after F1 | `GOV017-final-head-rebind` | deterministic change fixtures and #267 falsification |
| GOV017-F3 no approved current gate uses the new identity | medium | `slice-implementer` | one-gate pilot after F2 | `GOV017-multi-hop-pilot` | actual pilot, #268 lower-bound observation, and fresh-gate presence |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| design -> #270 implementation | `approved` | 2026-09-03 owner message resuming after #267/#268 completion | none within accepted implementation scope |
| shared manifest/rebind -> one `multi-hop-upgrade-transaction` pilot | `approved` | prior owner direction to enable promptly after dependencies plus the 2026-09-03 resume message | prerequisite tests and fail-closed checks must pass |
| one pilot -> additional allowlist entries | `awaiting-approval` | explicitly excluded by approved design | three qualifying head transitions, zero false reuse, zero missing fresh gates, then owner decision |
| local completion -> push/PR/merge/Issue/Project/release/publication | `awaiting-approval` | not inferred from local implementation authorization | separate owner authorization |

## Test And Evidence Strategy

- Run focused unit and fixture tests before registry/package projections.
- Prove history-only equality and tracked-byte, dependency, runtime, policy, environment, and provider drift outcomes deterministically.
- Use #268 bounded observation only as a lower bound: observed-but-undeclared pilot dependencies block reuse; absence of observation never proves closure.
- Use #267 critical mutants to prove identity substitution, evidence omission, and missing fresh-gate regressions remain detectable.
- Bind any real 360-second pilot to a clean immutable commit and delegate it under the long-running validation contract; do not treat fixture evidence as the actual pilot.
- Exact-head audit, required hosted contexts, and live provider admission are always fresh and outside the reusable result.

## Issue 270 Acceptance Projection

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| GOV017-A1 | passed | authoritative 76-gate classification; only `multi-hop-upgrade-transaction` is `pilot-approved` |
| GOV017-A2 | passed | deterministic 11-scenario matrix plus real temporary-Git history and tracked-drift tests |
| GOV017-A3 | passed | real temporary-Git amend preserves the subject digest and produces authenticated `reused-with-proof` without invoking the gate |
| GOV017-A4 | passed | complete tracked closure, runtime, authority, environment, source evidence, and original seal are re-authenticated; unknown closure blocks before output |
| GOV017-A5 | pending | deterministic local rebind is implemented; a final admitted remote head and its fresh hosted/provider gates do not yet exist |
| GOV017-A6 | passed | the rebind statement names both commits and explicitly says the gate was not executed or audited at the current commit |
| GOV017-A7 | passed | history-only amend fixture preserves original evidence and seal provenance while rebinding to the new commit |
| GOV017-A8 | passed | retained historical analysis separates confirmed subject-equivalence groups, observed duration envelopes, and unsupported savings claims |
| GOV017-A9 | passed | legacy cache reuse is disabled for the pilot; no other gate is enabled for subject-digest reuse |

## Resume Checkpoint

- Last completed action: implemented and focused-tested the canonical subject manifest, rebind authentication, runner consumption, and single-gate allowlist.
- Current task: `GOV017-multi-hop-pilot`.
- Exact next action: create a policy-valid clean implementation commit, rerun the HEAD-bound closure/registry test, then dispatch the 360-second pilot under the long-running validation contract.
- Validation already completed: subject tests 7/7 passed in 30.672s; routine evidence tests 4/4 passed in 55.848s; lifecycle validation and shell syntax passed. The pre-commit registry run passed 9/10; its sole closure test correctly rejected the new untracked authority because it is not yet in `HEAD` and must be rerun after commit.
- Git state: local implementation changes are uncommitted on `codex/2026-09-03-subject-digest-evidence-reuse-implementation`; no push or remote mutation occurred.
- Branch history and checkpoint handoffs: one local branch from `main@34893ab7`; no push, PR, or external handoff.
- Blockers or unresolved decisions: the local actual pilot requires a clean immutable commit; admitted-head hosted/provider proof requires separate push/PR authority. Allowlist expansion and every remote or terminal action remain owner-controlled.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-03-subject-digest-evidence-reuse-implementation` | `main@34893ab7021d2119200a3b9ca153325a4d9dcbb8` | local implementation bootstrap | `4e0e677a08b0bdc819460a1afe6ec185e7440fff` | local only | `2026-09-03T09:19:06+08:00` | preserve approved design after dependency integration | implement `GOV017-subject-manifest` |
