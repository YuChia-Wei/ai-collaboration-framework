# Validator Observation And Incident Fault-Injection Plan

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-09-02-validator-observation-and-fault-injection`
- `plan_id`: `development-plan-2026-09-02-validator-observation-and-fault-injection`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-02-validator-observation-and-fault-injection`
- `base_branch`: `main`
- `base_commit`: `c7f348694421048245da824dd79742372179f730`
- `branch_segment`: `1`
- `status`: `completed`
- `created_at`: `2026-09-02T22:43:57+08:00`
- `updated_at`: `2026-09-03T07:15:55+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-09-02-validator-observation-and-fault-injection/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-09-02-validator-observation-and-fault-injection/`

## Development Objective

- Product or software outcome: Deliver Issues [#268](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/268) and [#267](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/267) as one v0.16.0 safety-precondition delivery while preserving their independent acceptance outcomes.
- Current lifecycle entry point: Completed implementation delivered to GitHub PR [#281](https://github.com/YuChia-Wei/ai-collaboration-framework/pull/281) for owner review.
- User constraints: Complete #268 first, then use #267 to falsify the validation chain; the owner subsequently authorized branch push and PR creation on 2026-09-03.
- Non-goals: #270 production manifest/rebind implementation, reuse pilot enablement, merge, release/publication, Issue closure, or terminal Project mutation.

## Authority And Preflight

- Live GitHub read-back on 2026-09-02 found #267 and #268 open, Project status `Inbox`, and target release `v0.16.0`; their Issue bodies are the acceptance authority.
- Live `origin/main` and the new worktree both resolved to `c7f348694421048245da824dd79742372179f730`; the worktree was clean before branch creation.
- On 2026-09-03, live remote read-back still resolved `origin/main` to `c7f348694421048245da824dd79742372179f730`; the owner then explicitly authorized push and PR creation, and PR #281 was opened from the clean workflow branch.
- The owner authorization is the source-task delegation from thread `01a05526-95b8-7723-b23f-50bba311ce06`, which expressly authorizes branch/workflow creation, accepted-scope repository mutation, validation, and local commits.
- Issue #270 owner decision [comment 5478024060](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/270#issuecomment-5478024060) and read-only design checkpoint `3df455bd0ae6502b863990fd6aa104239d6f86ed` establish dependency-first sequencing and the no-pilot boundary. The commit is not cherry-picked.
- Effective-rule attempt 1 used an unsupported `source` technology profile and failed with `source-rule-selection`; after correcting the request to the repository's exact `dotnet-backend` source catalog route, the framework-source packet resolved with `loaded_rule_ids=[AICTX-EVIDENCE-001]` and packet digest `7d3cdae66882a5669daf7813f17353292137abcc77b126a8ca329ac1a8d328da`.
- Code graph: a moderate exact-baseline index named `ai-collaboration-framework-1dcf-c7f3486` indexed 30,053 nodes and 33,127 edges, but explicitly excluded `.ai/scripts`, `.ai/assets`, and `.ai/evaluation/fixtures`; direct tracked-file fallback is authoritative for those paths.
- Routine validation: `.dev/project-config.yaml` is absent at the verified base, so the orchestrator default is `manual`; no routine command is auto-selected. Explicit Issue-owned tests and lifecycle validation remain selected.

## Delivery Cohesion

One workflow and branch are used because #267 and #268 share the same safety outcome, base, release horizon, validation infrastructure, reviewer/owner boundary, and acceptable atomic rollback. Separate ledgers retain every acceptance identifier and evidence digest; one aggregate success flag is prohibited.

## Inputs

- Requirements: live Issue #268 and live Issue #267 bodies.
- Specifications: #270 owner-decision comment and the read-only design at `3df455bd0ae6502b863990fd6aa104239d6f86ed`.
- Architecture decisions: extend `.ai/evaluation/` and registered validation surfaces; observation is a lower bound and cannot shrink declarations; always-fresh gates remain fresh.
- Existing implementation or tests: `.ai/evaluation/`, `.ai/scripts/validate-ai-behavior-evaluation.py`, `.ai/scripts/tests/test_ai_behavior_evaluation.py`, `.ai/scripts/check-all.sh`, and `.ai/scripts/validation-profile-registry.sh`.

## Development Stages

### Stage 1 — VAL-012 bounded dependency observation

- `stage_id`: `VAL012-implementation`
- Goal: Observe bounded file, subprocess, Git, environment, and runtime signals and compare them with declarations using privacy-safe lower-bound reports.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Issue #268 production harness, schema/fixtures, focused tests, and registered validation surface.
- Non-goals: complete transitive closure claims, automatic declaration edits/removal, or reuse enablement.
- Dependencies: live Issue authority, resolved effective-rule packet, existing validation registry/evidence contracts.
- Validation: focused unit tests, representative harness fixtures, schema/registry checks, and tracked-worktree comparison.
- Commit checkpoint: one validated local commit when every VAL012 acceptance is evidenced.

### Stage 2 — VAL-011 incident-derived fault injection

- `stage_id`: `VAL011-implementation`
- Goal: Add deterministic critical known-incident mutants and exploratory reporting, with a gate that fails on any surviving critical mutant.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`
- Scope: Issue #267 mutant corpus, runner/schema integration, focused tests, and release/nightly registration.
- Non-goals: stochastic model/judge evaluation, mutation of tracked source during execution, or #270 pilot enablement.
- Dependencies: completed VAL-012 stage and its lower-bound/blind-spot vocabulary.
- Validation: focused mutation tests, injected critical-survivor negative test, deterministic corpus validation, registry checks, and tracked-worktree comparison.
- Commit checkpoint: one validated local commit when every VAL011 acceptance is evidenced.

## Role Execution Coordination

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| VAL012-implementation | all slice role bindings | slice-implementer | `not-applicable` | Generic Python validation-tooling slice; no domain/use-case role applies. | primary Codex / accepted after 9 focused and 10 registry tests passed | `tasks/VAL012-implementation.json` |
| VAL011-implementation | mutation-testing-sub-agent / `.ai/assets/sub-agent-role-prompts/mutation-testing-sub-agent/sub-agent.yaml` | slice-implementer | `completed-direct` | The parent loaded the complete role and mandatory references, produced the bounded six-mutant corpus, and retained no fabricated child invocation evidence. | primary Codex / accepted after 5/5 critical detection, the negative survivor proof, and exact-head observation | `tasks/VAL011-implementation.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `approved` | 2026-09-02 source-task owner delegation | none within #267/#268 accepted scope |
| completed local delivery -> branch push and PR creation | `approved` | 2026-09-03 owner message: "是否可以發 PR 並結束作業?" | none; PR #281 opened with deferred Issue dispositions |
| PR #281 -> merge, Issue closure, or Project terminal mutation | `awaiting-approval` | explicitly not inferred from push/PR authorization | owner review, fresh exact-head audit, hosted checks, and separate merge/closure authorization |
| #267/#268 completion -> #270 production implementation or pilot | `awaiting-approval` | explicit user exclusion and #270 owner comment | separate future authorization required |

## Validation Strategy

- Requirement/spec traceability: maintain `acceptance-ledger.val-012.yaml` and `acceptance-ledger.val-011.yaml` independently.
- Architecture validation: confirm lower-bound observation semantics and unchanged always-fresh admission boundaries.
- Test and implementation validation: run the new focused test modules first, then existing AI-behavior/registry/lifecycle validators affected by the changed paths.
- Review/compliance gates: self-review against both ledgers and repository policies; spec compliance remains unselected and `not-applicable`; no independent fixed-head audit is claimed.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root
- Target-owned commands: focused Python unittest modules and registered validation entrypoints introduced or changed by each stage.
- Prerequisites and environment boundary: Python 3.11+, PyYAML, Git, and Bash only where the registry integration is exercised; no credentials.
- Target policy: Issue acceptance plus `.ai/scripts/validation-profile-registry.sh` and affected repository validators.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: release/nightly lifecycle registration is validated structurally; no release profile execution is authorized or selected in this workflow.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | `passed` | VAL012 passed 9 of 9 bounded observation tests; VAL011 passed 18 of 18 exact-head behavior/fault-injection tests including the disabled-critical-detector failure proof | none |
| integration | `passed` | Registry 10 of 10, source entrypoints 3 of 3, shell assets, deterministic corpus, exact-head fault injection, exact-head bounded observation, and tracked-status checks passed | full release/nightly profile execution remains outside this focused local workflow |

## Spec Compliance Selection

- Selected: `no`
- Activation source: none; no problem-frame compliance gate was requested.
- Outcome: `not-applicable`
- Coverage and evidence: not applicable.

## Acceptance-To-Evidence Human Projection

### Issue #268 / VAL-012

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| VAL012-A1 | passed | `24d0bb6cc1ee86a6131bc23ee5d451000a178ea90f97c32852924cbae4f1ac28` |
| VAL012-A2 | passed | `546934cddc9f418bc5e693400202d789b07f859ac87bf7678aed50b3b163f7fe` |
| VAL012-A3 | passed | `a18734f11acc76c4a34eef1fa3d275bb908b6785984ddf1401dfe948049f24a1` |
| VAL012-A4 | passed | `4c5252c8f2f17e83a4f9cb1912b690abc35ab21568860972567e25c980dcd2b5` |
| VAL012-A5 | passed | `184abdda3bd2f9c098ed57fcfd89971c706319ae1d1fc247ae48abd4215a5c5c` |
| VAL012-A6 | passed | `6461fbd488becf5777d1c1ed3974eeae63bac4ebf018cdd5b808102411bd614f` |

### Issue #267 / VAL-011

| Acceptance ID | Outcome | Evidence digest |
| --- | --- | --- |
| VAL011-A1 | passed | `ed35a8ee571c33f267ef7047555b586d8667d21d444ffd3475e90705a3f494be` |
| VAL011-A2 | passed | `54dd26b3afdf847aebeb085f1bd79692c838356ae8c81428f67f06baa058bda0` |
| VAL011-A3 | passed | `ce505ea9a6584041409d0e74f393f18bd22ef88d3e777ba986770a176090a8ef` |
| VAL011-A4 | passed | `10f150459846f47adf3cbf71e604c25a1bd096dd1730c425b104b0ff4f094d6c` |
| VAL011-A5 | passed | `55cc201d77081d19db14613a64133a5c40ada7d6b0928cd3e6ebc21466728023` |
| VAL011-A6 | passed | `8f39fddedc476795f2847b4faefa34c410db7abfb3130d8c6847396a57ea88d8` |

## Progress And Handoff

- Current stage: completed and handed off through open PR #281; no active implementation task remains.
- Completed stages: provider/baseline/policy preflight, workflow bootstrap, VAL012 bounded dependency observation at `d8105e3dc038880d70803383a8928fc017a9f2f1`, and VAL011 incident-derived fault injection at `f7e1d7537226ff773dbb57508f98d3527fd88d3f`.
- Deferred stages and reasons: #270 production and pilot are outside authorization.
- Open decisions: PR review/merge and terminal Issue/Project disposition remain owner-controlled; #270 remains separately unauthorized.
- Continuation instructions: any #270 subject manifest, rebind validator, one-pilot observation, or reuse enablement requires a separate owner-authorized workflow; retain both closed ledgers as independent evidence.
- Target policy references: workflow gate, workflow artifact, handoff, Git commit, and branch policies named in the locator.
- Registered handoff checkpoint: none; this task remains in the same session/runtime.
- Branch history and checkpoint handoffs: branch created directly from verified `main@c7f348694421048245da824dd79742372179f730`, pushed after explicit authorization, and handed off in PR #281; merge is not authorized.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `main@c7f348694421048245da824dd79742372179f730` | local workflow bootstrap | `d66eec5915584a7e6df48ac6ab61a7261f1f134c` | local only | `2026-09-02T22:43:57+08:00` | cohesive #267/#268 delivery | continue VAL012 locally |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `d66eec5915584a7e6df48ac6ab61a7261f1f134c` | local validated stage | `d8105e3dc038880d70803383a8928fc017a9f2f1` | local only | `2026-09-02T23:21:04+08:00` | VAL012 acceptance passed independently | continue VAL011 locally |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `d8105e3dc038880d70803383a8928fc017a9f2f1` | local validated stage | `f7e1d7537226ff773dbb57508f98d3527fd88d3f` | local only | `2026-09-03T00:08:37+08:00` | VAL011 acceptance passed independently after exact-head falsification checks | close the local workflow; no remote action |
| 1 | `codex/2026-09-02-validator-observation-and-fault-injection` | `main@c7f348694421048245da824dd79742372179f730` | provider PR bootstrap | `995e90af44cde8f35709d9e6964372b670c50854` | PR #281 | `2026-09-03T07:15:55+08:00` | owner authorized push and PR creation after local completion | commit the PR-bound deferred declaration, push the new head, and leave merge/closure to the owner |

## Completion Summary

- Outcome: completed locally and delivered for review in PR #281; VAL012 and VAL011 each passed all six independently recorded acceptance outcomes.
- Changed artifacts: workflow records; the bounded observation contract/schema/CLI/fixtures; and the digest-bound incident mutant corpus, normalized result schema, deterministic adapters, tests, and release/nightly registration.
- Approved requirement/specification evidence: live Issues #267/#268, owner instruction, #270 owner decision and read-only design checkpoint.
- Implementation completion evidence: VAL012 is complete at `d8105e3dc038880d70803383a8928fc017a9f2f1`; VAL011 is complete at `f7e1d7537226ff773dbb57508f98d3527fd88d3f` with normalized report digest `b8ac291525e8cebe1eb7b6ec982266bdcbb1ac2d36b91b0f2c15fd48ad87232f`.
- Required test outcomes: VAL012 9/9 focused tests passed; VAL011 18/18 exact-head tests passed with 5/5 critical mutants detected and the critical-survivor negative control passing.
- Selected compliance evidence: not applicable.
- Review disposition: parent self-review completed against both ledgers; the fresh exact-head independent audit and hosted merge-admission gates remain pending and are not claimed.
- Validation evidence: focused and affected integration gates passed; exact-head VAL011 observation is explicitly partial/lower-bound-only; the initial undeclared-runtime observation, initial UPG detector mismatch, and wrong-Bash closure invocation remain preserved as failures in the task.
- Workflow task state: VAL012 completed; VAL011 completed.
- Commits before the PR-bound declaration: `d66eec5915584a7e6df48ac6ab61a7261f1f134c`, `d8105e3dc038880d70803383a8928fc017a9f2f1`, `fade069607baf22655d0b084477edf66bc555e38`, `f7e1d7537226ff773dbb57508f98d3527fd88d3f`, `995e90af44cde8f35709d9e6964372b670c50854`.
- Branch / checkpoint / handoff evidence: pushed branch and open PR #281; `.dev/workflows/2026-09-02-validator-observation-and-fault-injection/evidence/terminal-issue-closure-pr-281.yaml` binds both Issues as deferred, so no merge or Issue closure is implied.
- Residual risks: runtime observation remains a lower bound, the exploratory unknown-field mutant remains an explicit follow-up candidate, and all #270 reuse/pilot work remains separately unauthorized.
