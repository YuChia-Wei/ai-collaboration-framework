# Remediation Progress

Updated: 2026-09-18T00:28:00+08:00

Baseline: `ASM-20260917-23-c18`. Workflow: `2026-09-17-v018-cost-and-messaging`. This is the implementation owner's ledger, not independent verification.

| Finding | State | Evidence / remaining work |
| --- | --- | --- |
| F-001 | partially-resolved | 17 private roles colocated with owners; generated two-skill runtime entry and package projection integrated. Actual candidate usability comparison pending. |
| F-002 | partially-resolved | Routine evidence tiers propagated; private helper types permitted within unchanged semantic boundaries. Final package and independent acceptance pending. |
| F-003 | partially-resolved | MESSAGING-TX-001 and ARCH-UOW-001 clarification integrated with conditional design/review routing. Downstream and independent acceptance pending. |

No usability improvement, release readiness, independent audit success or publication is claimed. Heavy unrelated I/O/OS checks are deferred to the explicit release necessity review.

## Integrated Implementation

- Terra xhigh implemented private-role relocation and generated runtime entries;
  Terra high implemented the messaging guidance and selected consumer routing.
  Parent integration uses GPT-6 Astra ultra; this is not a Terra-only workflow.
- Seven integrated entry tests passed, including LF normalization, drift rejection,
  and regeneration from final portable package bytes. Generated parity passed.
- Messaging routing passed nine worker tests after an indentation/fixture repair.
  Source context validation found 14 owned rules. Final immutable package checks
  remain pending.
- Actual unchanged lab baseline reviews completed on the existing v0.16.0
  installation: Terra medium used 216.507 seconds and 22 tool calls; Luna medium
  used 236.416 seconds and 46 tool calls. Token counters include cached input and
  cumulative turns; they are not a measured credit bill. Candidate comparison and
  quality adjudication remain pending.
- RAM-disk model startup and relative-path package validation failed. Inputs and
  actual model trials moved to ordinary disk; F: remains disposable workspace
  storage. No operating-system repair or original lab mutation was attempted.

## Initial Focused Validation

- `validate-workflow-artifacts.py`: passed.
- `validate-ai-context.py`: passed; structural bilingual parity only.
- Initial `validate-assessment-artifacts.py`: failed because required empty historical relation list was missing; restored before retry.
- `test_agent_execution_guardrails.py`: 29 tests executed; 8 errors from sandbox PermissionError on temporary evidence/lease directories. Non-passing environment result retained; no guardrail implementation changed and no success inferred. Reassess at release necessity review instead of pursuing unrelated OS behavior now.
