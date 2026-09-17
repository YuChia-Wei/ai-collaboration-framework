# Remediation Progress

Updated: 2026-09-17T23:54:11+08:00

Baseline: `ASM-20260917-23-c18`. Workflow: `2026-09-17-v018-cost-and-messaging`. This is the implementation owner's ledger, not independent verification.

| Finding | State | Evidence / remaining work |
| --- | --- | --- |
| F-001 | not-addressed | Skill resource/entry implementation pending. |
| F-002 | partially-resolved | Initial execution-tier policy authored; narrow checks and scope implementation pending. |
| F-003 | not-addressed | Terra proposal review complete; contract adoption pending. |

No usability improvement, release readiness, independent audit success or publication is claimed. Heavy unrelated I/O/OS checks are deferred to the explicit release necessity review.

## Initial Focused Validation

- `validate-workflow-artifacts.py`: passed.
- `validate-ai-context.py`: passed; structural bilingual parity only.
- Initial `validate-assessment-artifacts.py`: failed because required empty historical relation list was missing; restored before retry.
- `test_agent_execution_guardrails.py`: 29 tests executed; 8 errors from sandbox PermissionError on temporary evidence/lease directories. Non-passing environment result retained; no guardrail implementation changed and no success inferred. Reassess at release necessity review instead of pursuing unrelated OS behavior now.
