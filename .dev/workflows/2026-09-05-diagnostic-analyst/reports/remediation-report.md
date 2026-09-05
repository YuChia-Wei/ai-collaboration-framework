# Diagnostic Analyst Remediation Report

Issue: #269. Status: locally complete and independently reviewed; provider delivery pending.

## Change And Acceptance Evidence

| Acceptance | Evidence | Current disposition |
| --- | --- | --- |
| SKILL003-AC1: skill, wrappers, registries, routing and validation | Canonical diagnostic-analyst skill; diagnosis capability and intent route; Codex/Claude wrappers; prerequisite registry and governed CI entry | locally validated |
| SKILL003-AC2: complete diagnostic output | Diagnostic/output contracts; strict JSON validator with evidence byte binding and controlled causal isolation | locally validated |
| SKILL003-AC3: PERF-002, REL-016 and UPG-005 examples | Human guide cites Issues 251, 241 and 237; source retrospective for PERF-002 reviewed; no historical tracked files changed | document evidence |
| SKILL003-AC4: reject insufficient sampling | Negative fixture plus 14 synthetic contract tests | passed, synthetic-test |
| SKILL003-AC5: no inferred repair/provider authority | Canonical constraints, ownership/handoff contract, null authorization fixture; unknown permission fields rejected | locally validated |

## Validation

- Diagnostic contract: 14 passed (0.397 seconds). Synthetic fixtures do not prove an actual historical diagnosis.
- Python prerequisites: 14 passed (6.552 seconds).
- Orchestrator capability contract: 14 passed (0.162 seconds); acceptance: 3 passed (3.021 seconds).
- Skill script colocation: 4 passed; validation profile registry: 10 passed (2.728 seconds).
- Shell asset and validation lifecycle contracts passed.
- Workflow artifact validator passed after index reconciliation.
- AI context validator passed; after commit, source disposition validated 1461 tracked .dev paths with zero implicit omissions.
- Independent review of `7e45d7b90d6848d7f75aac6b0d7789be9d720f41` passed with zero blocking findings; subject digest `db62fc168c1c39e0b341359f8fbbc1fea6bc8e836ee3fb501edfebe6474de4bc`. Review preserved the synthetic-versus-actual and no-repair authority boundaries.

## Preserved Failures And Corrections

- Initial diagnostic run was blocked by Windows TEMP permissions before fixture setup; 14 empty directories remained after failed cleanup. Normal-permission rerun passed and all 14 verified empty directories were removed.
- First context validation found missing exact wrapper identity/reference lines and an incorrectly inserted routing-table row. Workflow validation found a title projection mismatch.
- Second context validation found the remaining required runtime-use line. The workflow records a bounded third-attempt authorization after that actual content repair; no unchanged retry was used.

## PR 284 Entrypoint Contract Correction

Hosted Ubuntu prerequisite validation on `9759ef0b` failed because the new
diagnostic CLI was absent from the explicit portable expectation. The first
local correction then exposed the corresponding standard-library-only
expectation omission. Both exact approved sets now include that existing
registered CLI; unknown portable entries and all other strict checks remain
rejected. The bounded third contract attempt passed all seven tests in 3.454
seconds. Hosted failure output and the independent audit remain retained under
ignored Issue 269 validation artifacts; fresh hosted checks are still required.

The same hosted PR profile exposed the package projection fixture's old count
of 21. A focused local reproduction observed the exact 21-versus-22 mismatch;
the approved diagnostic CLI is the additional selected operation. The corrected
exact-count assertion and unchanged exact-path assertion passed the one selected
test in 1.606 seconds. The remaining package-apply matrix will run in hosted CI.

## Diagnostic Boundaries

Diagnosis validators check declared inference prerequisites and evidence digests, not causal truth. Human/independent review still judges whether execution and complete observation are credible. No incident is rerun by writing a worked example. No actual repair, provider action or publication is authorized by a diagnostic record. Issue 280 and direct upgrade Issue 272 remain separate deliveries.
