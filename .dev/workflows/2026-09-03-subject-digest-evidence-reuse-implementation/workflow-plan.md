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
- `updated_at`: `2026-09-05T00:12:11+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
- `template_version`: `1.2.0`

## Objective And Scope

- Problem statement: SHA-only invalidation forces expensive eligible evidence to rerun after history-only changes even when the complete applicable subject is unchanged.
- Authorized remediation scope: implement Issue #270's approved manifest, digest, rebind, deterministic fixture, and single-pilot behavior after merged Issues #267 and #268; prospectively replace exact-head-only independent-review validity with content-addressed review plus current-head binding; remove the same SHA-only invalidation semantics from the next downstream package projection.
- Authorization source: the owner resumed this conversation on 2026-09-03 with `267/268 已完成，這邊可以繼續了`, on 2026-09-04 approved the proposed content-addressed review correction and necessary Issue-body synchronization, and on 2026-09-05 required the new portable version not to impose SHA-only evidence invalidation on downstream teams.
- Exclusions: push, pull request, merge, Issue or Project terminal mutation, allowlist expansion beyond `multi-hop-upgrade-transaction`, tag, release, publication, or historical backfill.
- Completion criteria: every locally applicable GOV017 acceptance is evidenced; the pilot is the only subject-digest-enabled behavioral gate; independent review and code-graph freshness use content validity plus cheap current-head binding; no portable rule uses commit-SHA inequality alone as an evidence-validity key; hosted, provider, tag/release, and mutable-state gates remain live or current-head-bound.

## Authority And Preflight

- Live provider read-back on 2026-09-04 confirmed Issue #270 remains open in Project status `Inbox`; its body now records the owner-approved content-addressed review model and local implementation boundary.
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
4. Replace prospective exact-head-only review receipts with content-addressed v2 receipts and deterministic current-head binding while preserving historical v1 semantics.
5. Correct the portable package boundary so downstream targets receive the content-addressed rule, target-scoped provenance, and content-tree graph freshness rather than source identity or SHA-only invalidation.

These five stages retain distinct state: manifest identity can complete before rebind is admissible; rebind can complete before any current gate is enabled; pilot execution and observation can be disabled without removing the shared contract; review binding can change prospectively without rewriting historical evidence; package correction can be locally complete while already-installed v0.15.1 targets remain unchanged until separately authorized upgrades.

## Finding Triage

| Finding | Severity | Owner | Disposition | Task | Validation |
| --- | --- | --- | --- | --- | --- |
| GOV017-F1 canonical subject identity is absent | high | `slice-implementer` | implement | `GOV017-subject-manifest` | focused manifest/schema tests and closure resolution |
| GOV017-F2 final-head rebind is absent | high | `slice-implementer` | implement after F1 | `GOV017-final-head-rebind` | deterministic change fixtures and #267 falsification |
| GOV017-F3 no approved current gate uses the new identity | medium | `slice-implementer` | one-gate pilot after F2 | `GOV017-multi-hop-pilot` | actual pilot, #268 lower-bound observation, and fresh-gate presence |
| GOV017-F4 independent review still uses commit SHA as its validity key | high | `slice-implementer` | replace prospectively after owner decision | `GOV017-multi-hop-pilot` | v2 receipt, current-head content rebind, v1 compatibility, and content-drift rejection |
| GOV017-F5 the v0.15.1 portable projection carries the historical every-tracked-head review rule and source-scoped validation provenance | high | `slice-implementer` | correct the next package prospectively; do not mutate installed targets | `GOV017-multi-hop-pilot` | version-boundary comparison, portable lifecycle/schema validation, graph tree-equivalence tests, and focused package-projection regression |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| design -> #270 implementation | `approved` | 2026-09-03 owner message resuming after #267/#268 completion | none within accepted implementation scope |
| shared manifest/rebind -> one `multi-hop-upgrade-transaction` pilot | `approved` | prior owner direction to enable promptly after dependencies plus the 2026-09-03 resume message | prerequisite tests and fail-closed checks must pass |
| one pilot -> additional allowlist entries | `awaiting-approval` | explicitly excluded by approved design | three qualifying head transitions, zero false reuse, zero missing fresh gates, then owner decision |
| exact-head-only review -> content-addressed review plus current-head binding | `approved` | 2026-09-04 owner message and synchronized Issue #270 body | preserve v1 historical meaning and current-head hosted/provider gates |
| source correction -> next portable package projection | `approved` | 2026-09-05 owner requirement that downstream upgrades must not impose SHA-only evidence invalidation | existing targets remain unchanged until separately authorized upgrade work |
| local completion -> push/PR/merge/Issue/Project/release/publication | `awaiting-approval` | not inferred from local implementation authorization | separate owner authorization |

## Test And Evidence Strategy

- Run focused unit and fixture tests before registry/package projections.
- Prove history-only equality and tracked-byte, dependency, runtime, policy, environment, and provider drift outcomes deterministically.
- Use #268 bounded observation only as a lower bound: observed-but-undeclared pilot dependencies block reuse; absence of observation never proves closure.
- Use #267 critical mutants to prove identity substitution, evidence omission, and missing fresh-gate regressions remain detectable.
- Bind any real 360-second pilot to a clean immutable commit and delegate it under the long-running validation contract; do not treat fixture evidence as the actual pilot.
- Independent review runs once against an immutable checkout and binds validity to the canonical base/head content subject; current-head review binding, required hosted contexts, and live provider admission remain fresh.
- Project the current payload deterministically and assert that source-only GitHub closure machinery stays excluded while the portable lifecycle, schema, auditor, code-graph validator, and target-scoped provenance all preserve the commit-identity boundary.

## Issue 270 Acceptance Projection

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| GOV017-A1 | passed | authoritative 76-gate classification; only `multi-hop-upgrade-transaction` is `pilot-approved` |
| GOV017-A2 | passed | deterministic 11-scenario matrix plus real temporary-Git history and tracked-drift tests |
| GOV017-A3 | passed | real temporary-Git amend preserves the subject digest and produces authenticated `reused-with-proof` without invoking the gate |
| GOV017-A4 | passed | complete tracked closure, runtime, authority, environment, source evidence, and original seal are re-authenticated; unknown closure blocks before output |
| GOV017-A5 | pending | content-addressed review and deterministic current-head binding are implemented locally; a final admitted remote head and its hosted/provider gates do not yet exist |
| GOV017-A6 | passed | behavioral and review bindings preserve the original commit provenance without claiming execution or review at a different commit |
| GOV017-A7 | passed | real amend fixtures preserve execution and reviewer provenance while equal content avoids validation rerun or independent re-review; volatile receipts remain untracked |
| GOV017-A8 | passed | retained historical analysis separates confirmed subject-equivalence groups, observed duration envelopes, and unsupported savings claims |
| GOV017-A9 | passed | legacy cache reuse is disabled for the pilot; no other gate is enabled for subject-digest reuse |
| GOV017-A10 | passed | v0.15.1 is identified as the affected package boundary; the next package forbids SHA-only validity and its focused projection regression passes |

## Resume Checkpoint

- Last completed action: implemented and locally validated the owner-approved v2 content-addressed review receipt plus the downstream package correction for portable lifecycle, target-scoped provenance, and content-tree graph freshness.
- Current task: `GOV017-multi-hop-pilot`.
- Exact next action: stop at the local correction checkpoint and await separate owner authorization for push, PR, hosted admission, or another qualifying pilot transition.
- Validation already completed: the prior subject tests passed 8/8, registry tests passed 10/10, and external invocation `20260903T031341Z-829` passed in 487s with 48 selected, 47 executed, zero reused, failed, or blocked checks. The content-review and portable-boundary correction additionally passed 57 terminal-closure, 13 lifecycle, 20 provider, 8 subject-digest, 9 dependency-observation, 29 guardrail, 10 language-parity, 16 wrapper-metadata, 8 governance-routing, 31 sub-agent-adapter, 10 profile-registry, and focused package-projection tests plus the relevant static validators. The prior baseline subject digest is `aeeeba52f1504dff9fdb430fc8a631c3a045a4dca939803b0623b83ca8f2a69e`; its sealed-manifest SHA-256 is `a4afc342c32576f1797564d253a29d85e2becadf3470d4aa2f88d1f846f92b57` and is not relabeled as execution of the correction.
- Git state: the branch remains local-only. The content-review correction is represented by the commit containing this record; its concrete SHA remains branch provenance and is not copied into a follow-up tracked evidence-sync commit. Current-head rebind evidence remains only under ignored validation artifacts. No push, PR, merge, or terminal provider mutation occurred.
- Branch history and checkpoint handoffs: one local branch from `main@34893ab7`, design `4e0e677a`, initial implementation/evidence `a77e3010`, first rebind `9dfdb72d`, observation `4ad2f436`, remediation/new baseline `f6c7a382`, and a locally history-shaped metadata checkpoint with preserved ignored terminal evidence; no push or PR.
- Blockers or unresolved decisions: no local design decision remains. Observation remains 1/3, expansion is unauthorized, final admitted-head hosted/provider proof requires separate push/PR authority, and already-installed v0.15.1 downstreams remain affected until a fixed release exists and each target upgrade is separately authorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-03-subject-digest-evidence-reuse-implementation` | `main@34893ab7021d2119200a3b9ca153325a4d9dcbb8` | local implementation bootstrap | `4e0e677a08b0bdc819460a1afe6ec185e7440fff` | local only | `2026-09-03T09:19:06+08:00` | preserve approved design after dependency integration | implement `GOV017-subject-manifest` |
| 1 | `codex/2026-09-03-subject-digest-evidence-reuse-implementation` | `4e0e677a08b0bdc819460a1afe6ec185e7440fff` | implementation and original pilot subject | `a77e30102cb996a01e54ad3b57c68caefd53f442` | local only | `2026-09-03T10:31:06+08:00` | seal the one approved pilot's first actual execution before a history-only transition | create and authenticate the first final-head rebind |
| 1 | `codex/2026-09-03-subject-digest-evidence-reuse-implementation` | `a77e30102cb996a01e54ad3b57c68caefd53f442` | first observed subject-rebind transition | `9dfdb72d19c106a66123fd2eb2259210724d5a35` | local only | `2026-09-03T10:38:50+08:00` | prove workflow-only history can reuse the one allowlisted gate without false fresh-head claims | record transition 1/3 and hold expansion |
| 1 | `codex/2026-09-03-subject-digest-evidence-reuse-implementation` | `4ad2f436883a4d7dd1d1d066458f95f9c97a5ed9` | audit remediation and new subject baseline | `f6c7a38288bcac38f1b48987666f89fb2599916c` | local only | `2026-09-03T11:25:09+08:00` | close two fixed-head audit findings and prove changed subject evidence re-executes | apply the owner-approved content-review correction and validate current-head binding |
