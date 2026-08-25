# Acceptance Evidence Mapping

This projection keeps #249 and #253 acceptance independent while sharing one
validation and audit boundary. The canonical mapping is `acceptance-map.yaml`;
terminal actual-execution receipts remain ignored so their exact-head metadata
does not mutate the frozen subject.

## Issue #249 / GOV-013

| Acceptance | Evidence owner | Focused proof |
| --- | --- | --- |
| `GOV013-AC-01` taxonomy | validation lifecycle schema and contract | schema validation |
| `GOV013-AC-02` dependency/content closure | aggregate runner resolved-input closure | profile registry GWT 008 |
| `GOV013-AC-03` reuse receipt | lifecycle validator | lifecycle GWT 001-007 |
| `GOV013-AC-04` freeze sequencing | lifecycle contract | lifecycle GWT 008 |
| `GOV013-AC-05` hosted contexts | lifecycle validator plus provider policy | lifecycle GWT 010 |
| `GOV013-AC-06` audit dispositions | lifecycle schema | lifecycle GWT 009 |
| `GOV013-AC-07` unknown/drift fail-closed | lifecycle validator | lifecycle GWT 003-005 |
| `GOV013-AC-08` #246 regression | metadata-only synthetic fixture | lifecycle GWT 002 |
| `GOV013-AC-09` compatibility dimensions | reuse receipt and runner authority closure | lifecycle GWT 001/003/006 |
| `GOV013-AC-10` fresh gates | canonical contract and guidance | source-governance/profile validation |

## Issue #253 / GOV-014

| Acceptance | Evidence owner | Focused proof |
| --- | --- | --- |
| `GOV014-AC-01` planned commit preflight | Git commit validator and policy | Git commit policy GWT planned-message cases |
| `GOV014-AC-02` execution packet | agent guardrails schema/validator | guardrails GWT 001-003 |
| `GOV014-AC-03` worktree lease | agent guardrails validator | guardrails GWT 004-005 |
| `GOV014-AC-04` ledger/report parity | agent guardrails validator | guardrails GWT 006-008 |
| `GOV014-AC-05` retry identity/budget | agent guardrails validator | guardrails GWT 009-010 |
| `GOV014-AC-06` PowerShell safety | reserved-variable scanner | guardrails GWT 013-014 |
| `GOV014-AC-07` graph freshness | graph freshness record | guardrails GWT 011-012 |
| `GOV014-AC-08` baseline compatibility | orchestrator consumer contracts | capability and external delegation suites |
| `GOV014-AC-09` external packet binding | external delegation validator | external delegation GWT 015-016 |
| `GOV014-AC-10` guidance/projection parity | root/policy/orchestrator guidance | language and source-governance validation |

No entry claims provider admission, Issue closure, release readiness, merge, or
publication. Those remain separately authorized actions.
