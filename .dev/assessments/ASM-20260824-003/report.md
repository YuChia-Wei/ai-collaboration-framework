# GOV-012 Frozen Blob Identity Verification

## Metadata

- `assessment_id`: `ASM-20260824-003`
- `assessment_type`: `ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-08-24`
- `created_at`: `2026-08-24T23:25:07+08:00`
- `updated_at`: `2026-08-24T23:25:07+08:00`
- `repository`: `YuChia-Wei/ai-collaboration-framework`
- `subject_branch`: `codex/2026-08-24-retire-repository-backlog-authority`
- `subject_commit`: `ba9b5277f98626b9ff6d07dc1062956a476eff2b`
- `previous_assessment`: `ASM-20260824-002`
- `workflow_refs`: `2026-08-24-retire-repository-backlog-authority`

## Executive Summary

- Overall assessment: The prior locator and offset-time findings are closed, but the frozen backlog aggregate reads checkout-materialized bytes instead of fixed Git blob bytes.
- Decision: `remediation-recommended`
- Finding count: one `HIGH`; no `CRITICAL`, `MEDIUM`, or `LOW` finding.
- Subject mutation: `false` for both read-only invocations.

## Methodology And Evidence

The first invocation, `GOV012-VAL-001-fixed-head-independent-auditor-03`,
stopped fail-closed after a redundant packaging suite hit two Windows ACL errors
and could not clean ignored `.tmp/`. It established no repository finding and
was not treated as passed. The integration owner removed only that exact ignored
temporary tree and rerouted the unchanged clean subject.

The fresh invocation,
`GOV012-VAL-001-fixed-head-independent-auditor-04`, inspected the clean fixed
subject, direct tracked files and Git objects, focused prospective enforcement,
and the existing exact-subject sealed release receipt without regenerating
repository-local temporary artifacts.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| GOV012-AUD-003 | HIGH | Frozen aggregate identity uses worktree bytes, which may be CRLF/LF materializations of unchanged Git blobs. | `.ai/scripts/validate-source-work-management.py` read `(root / path).read_bytes()` while `.gitattributes` declares LF normalization; multiple clean worktree paths differed from their `HEAD` blobs. | A clean checkout on another platform can fail the freeze digest, so ordinary deterministic validation depends on pre-existing checkout state. | Hash raw fixed-commit Git blob bytes and separately reject staged or unstaged backlog drift. | `ai-context-governance` |

## Confirmed Boundaries

- `GOV012-AUD-001` is closed: prospective locators and task JSON are scanned.
- `GOV012-AUD-002` is closed: explicit-offset timestamps are parsed and compared as instants, with malformed or naive inputs rejected.
- Current provider authority, one active standards-owned provider policy, 55 retained legacy items, historical snapshot/ROADMAP classification, legacy and prospective release boundaries, provider-neutral downstream binding, credential-independent ordinary validation, and source dispositions otherwise passed.
- The exact release receipt for `ba9b5277...` is schema-valid and reports 2268 seconds, 65 selected, 62 executed, zero failed/blocked/warning/deferred, and three not-applicable checks; all 226 sealed artifacts matched size and SHA-256.

## Validation State

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Exact subject and tracked state | passed | `ba9b5277f98626b9ff6d07dc1062956a476eff2b`, clean before and after |
| Prior findings | passed | `GOV012-AUD-001` and `GOV012-AUD-002` confirmed closed |
| Frozen blob identity | failed | one HIGH checkout-materialization finding |
| Sealed release receipt | passed | schema/digest and 226/226 artifact hashes verified |
| First invocation cleanup | blocked | Windows ACL; retained, not relabeled |

## Lifecycle Handoff

- Stable finding reference: `ASM-20260824-003#GOV012-AUD-003`
- Remediation owner: `ai-context-governance`
- Related workflow: `2026-08-24-retire-repository-backlog-authority`
- Next gate: focused validation, a new immutable subject and long-run receipt, then a fresh read-only exact-head audit.
- Provider/release actions remain excluded.
