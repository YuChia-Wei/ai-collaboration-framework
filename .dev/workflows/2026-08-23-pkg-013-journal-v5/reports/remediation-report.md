# PKG-013 Journal v5 Remediation Report

## Template Metadata

- `template_id`: `ai-context-governance-remediation-report`
- `template_version`: `2.0.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-13T23:11:56+08:00`

## Report Metadata

- `report_id`: `remediation-report-2026-08-23-pkg-013-journal-v5`
- `workflow_id`: `2026-08-23-pkg-013-journal-v5`
- `owner_skill`: `ai-context-governance`
- `status`: `draft`
- `created_at`: `2026-08-23T18:53:54+08:00`
- `updated_at`: `2026-08-23T20:27:05+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `2.0.0`
- `baseline_assessment`: live GitHub Issue #239 and repository-owned journal v4 behavior
- `verification_assessment`: historical implementation audit accepted `c3ffc2f4d2b576943595f2b0b99692f39d7895e5`; the fresh PR-head audit failed `6502c29603cb46c52b200c20d00ff3098e71ca5a` with P1/P2/P3=2/0/0 and exact-head repair verification is pending

## Remediation Summary

- Authorized scope: journal v5 only, bounded write amplification, durable per-operation progress, v4 mutation-safety classification without v4 recovery, deterministic I/O instrumentation, stderr-only opt-in progress, and owning contracts/tests/documentation.
- Completed scope: digest-chained append-only v5 apply/rollback progress, identity-bound snapshots and target/recovery validation parity, safe Git-admin transaction boundaries, deterministic logical write-call/byte accounting, and `--progress` on stderr.
- Excluded scope remained unchanged: no v4 resume/rollback/migration/conversion, Issues #149/#168, CLI/runtime rewrite, downstream mutation, release notes, push, PR, merge, Issue/Project mutation, release allocation, tag, Release, or publication.
- Closure decision: `blocked-pending-exact-head-verification` after the PR-head audit exposed two in-scope P1 path-safety defects.

## Finding Resolution Matrix

| Finding | Status | Changed Surface | Validation | Accepted Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- |
| `Issue-239/PKG-013` quadratic journal rewrite | resolved | package apply journal and tests | GWT-061 plus full suite 88/88 | `c3ffc2f4` | high-N replay/read cost is not a write-amplification gate |
| v5 crash/resume/rollback parity | resolved | apply/recovery and target provenance | GWT-062, GWT-065 through GWT-068 | `c3ffc2f4` | adversarial concurrent path replacement is outside deterministic fixtures |
| unfinished v4 mutation safety | resolved | new apply plus resume/rollback guard | GWT-063 and GWT-065 | `c3ffc2f4` | prior tooling or owner-directed manual recovery remains required |
| symlink/reparse journal escape | verification-pending | progress, transaction-root, lock, legacy-journal, and target-admission boundaries | GWT-069 through GWT-072 focused pass | repaired PR head pending | native Windows junction fixture may use deterministic reparse fallback |
| stdout/stderr compatibility | resolved | package-apply CLI | GWT-064 | `c3ffc2f4` | none observed |

## Validation And Review Evidence

- Focused GWT-061 through GWT-070 and selected historical corruption, receipt, resume, rollback, rejection, finalization, and target-validation regressions passed after their relevant repairs.
- Exact-head full command `python .ai/scripts/tests/test_ai_context_package_apply.py -v` at `c3ffc2f4d2b576943595f2b0b99692f39d7895e5`: 88 passed, 0 failed, 1 skipped in 533.226 seconds.
- External-task schema 1.1 completion validated against its exact dispatch; expected and observed SHA matched and the tracked worktree remained clean.
- Independent high-risk audit accepted the same implementation SHA with no actionable P1/P2/P3 findings.
- Four earlier exact-head audits failed and remain preserved: `c196c558`, `ed48ec99`, `34753883`, and `679bc0be`.
- The fresh PR-head audit at `6502c29603cb46c52b200c20d00ff3098e71ca5a` also failed and remains preserved: P1 transaction-lock leaf redirection and P1 unclassified legacy-journal leaf bypass.
- GWT-062, GWT-063, GWT-065, and GWT-069 through GWT-072 passed after the PR-head remediation on the normal Windows host ACL boundary; exact repaired-head full validation and review remain pending.
- `validate-ai-context.py`, `validate-source-governance.py`, `validate-workflow-artifacts.py`, Python syntax compilation, and `git diff --check` passed before closeout and are rerun on final evidence.
- Retained non-pass evidence includes sandbox Temp ACL blocking, initial raw-snapshot assertion failures before v5 replay-aware corrections, and one wrong unittest selector loader error before its corrected selector passed.

## Release Impact And Deferred Work

| Item | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| Release allocation | journal v5 is an intentionally breaking recovery contract and is unsuitable for a patch | release owner | Consider batching into a future minor release such as v0.15.0; no release is assigned here |
| Native Windows junction fixture | host capability may require deterministic reparse classification fallback | future validation owner | Add a native junction lane when a suitable Windows runner is available |
| Concurrent path replacement hardening | deterministic fixtures do not model an adversarial actor racing validation and open | future security/design owner | Evaluate handle-relative or platform-specific no-follow directory operations if threat scope expands |

## Closure Evidence

- Historical accepted implementation commit: `c3ffc2f4d2b576943595f2b0b99692f39d7895e5`; it is not the current PR-head gate after later audit findings.
- Workflow/task status: reopened for bounded PR-head remediation and exact-head verification; PR #240 remains draft.
- Remote and release state: Issue #239 remains open and Project/release allocation remains unassigned; no tag, Release, publication, or downstream mutation is authorized.
- Exact next gate: commit the bounded repair, obtain an immutable-head full-suite receipt plus fresh independent audit, rerun hosted checks, capture live merge admission, and only then integrate PR #240 with merge-commit topology.
