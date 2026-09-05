# Draft Publication Recovery

- Workflow: `2026-09-05-draft-publication-recovery`
- Owner: `ai-context-governance`
- Branch: `codex/2026-09-05-draft-publication-recovery`; base: `main`
- Status: completed; current phase: completed
- Created: 2026-09-05T22:58:09+08:00; updated: 2026-09-05T23:01:27+08:00
- Template: `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`, version 1.2.0

## Scope And Authorization

Issue #287 records the owner's instruction to repair the failed publication and improve the process, including permission to consider tag adjustment. The earlier PR/merge/Issue-close authorization remains applicable. Actual public release acceptance remains coordinated by #280, which the owner explicitly retained until public bytes are verified.

This one-task workflow preserves a source automation repair plus the cross-boundary recovery decision for an existing immutable tag. The implementation is one coherent unit; independent review, hosted admission, merge and public recovery are separate gates, not artificial implementation tasks. Select merge-commit integration because this branch carries a publication recovery boundary.

## Diagnosis And Tag Decision

The failed publication is run 33972121533 attempt 1, job 101322466190. Tag object `41d71e58080f8a68b9ba1cd1d7c761ff431e005b` resolves to `f1ead6d676193ba24d8517aed08f05fcfa23cbd3`; Release ID 383271701 remains draft. Its four downloads match the admitted archives/checksums. The validator accepts a draft page locator but rejects matching draft asset locators. Changing only four URL fields in a controlled local fixture makes the comparison pass; this is causal evidence, not publication.

Preserve the tag. The source-only validator and hosted diagnostics can be repaired independently of the correct admitted package. Moving the tag would change publication identity without repairing any package bytes. `main` fixes do not affect a pinned workflow rerun, so actual recovery must first execute the reviewed verifier from a clean repair checkout against the original tag and actual draft, under the owner's recovery authorization.

## Implementation And Process Changes

- Accept only the expected versioned asset URL or the exact owned draft page's temporary token when draft permission is explicit; retain public/lifecycle/byte/identity guards.
- Exercise realistic draft-to-public URLs and negative locators, plus deterministic CLI failure evidence retention.
- Retain raw provider response before comparison. Use fresh artifact names per run attempt and actionable field-only diagnostics.
- Document preflight, original artifact availability, the reviewed repair/tag distinction, actual public-byte checks and original workflow retry. No source release-state rewrite or archive rebuild.

## Validation And Acceptance

| Acceptance | Evidence / gate |
| --- | --- |
| #287 draft and public locator boundaries | `test_release_asset_identity.py`; synthetic and CLI tests |
| #287 evidence retained on failure and across attempts | CLI raw-output tests; `test_github_workflow_contract.py` |
| #287 process and tag decision | Source release policy; fixed-head independent audit |
| #287 integrated source repair | Current-head hosted checks, audit receipt and PR admission |
| #280 actual v0.16.0 publication | Reviewed provider verifier against live draft; public downloads; original workflow success; publication/finalization and Issue/Project read-back |

Run narrow affected tests first. The previous nine-route execution continues to bind the unchanged archive; do not claim tests of the URL correction rerun that matrix. Required hosted contexts remain present. Use declared ignored validation output under `.dev/ai-context/local/validation/issue-287/` and retain failed attempts. Completion of this implementation workflow does not attest publication.

## Resume

Local implementation task `DRAFT-IDENTITY-REPAIR` is completed. Asset/CLI tests passed 20 cases and workflow contract tests passed 12 cases. Next: independent read-only audit, hosted PR admission and integration, followed by the separately tracked Issue280 public recovery. A new gate failure is preserved and repaired within scope; stop for byte/identity drift or a new owner decision.
