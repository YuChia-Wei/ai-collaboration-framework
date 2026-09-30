# v0.4.2 Publication Incident External Review Intake

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `template_created_at`: `2026-07-10T18:22:49+08:00`
- `template_updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `ASM-20260720-001`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `status`: `final`
- `audit_date`: `2026-07-20`
- `created_at`: `2026-07-20T22:23:02+08:00`
- `updated_at`: `2026-07-20T22:37:10+08:00`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend`
- `subject_branch`: `main`
- `subject_commit`: `71c41dbd9c4f2b65105a616d15b7f1cc9db2a338`
- `previous_assessment`: [`ASM-20260719-001`](../ASM-20260719-001/report.md)
- `workflow_refs`: [`2026-07-20-v0-4-2-release-finalization-hotfix`](../../workflows/2026-07-20-v0-4-2-release-finalization-hotfix/workflow.yaml)
- `external_review_source`: [`fable5-v0.4.2`](evidence/fable5-v0.4.2/README.md)

## Executive Summary

- Overall assessment: **critical release-finalization drift with a valid
  published package identity**
- Overall score: **4.0/10**
- Decision: **critical-remediation-required**
- Primary strengths: Fable's report clearly separates the correct immutable
  package publication from broken registry/evidence finalization, supplies
  reproducible commands, and identifies cold-start process defects rather than
  blaming only one runtime entry file.
- Primary risks: the critical workflow gate is red on `main`, the release
  registry blocks the next candidate, authored release sources are missing or
  polluted, historical evidence is copied or false, and the public Release body
  contains a non-object provenance SHA.

All seven material Fable findings were reproduced. This assessment preserves
the external review as an independent input and assigns stable repository
finding IDs; it does not copy the external report into normative policy.

## Scope

### Included AI Context Surfaces

- Raw external Fable 5 review package.
- v0.4.2 release registry, authored release documents, publication workflow,
  roadmap, backlog items, release renderer, and relevant validators.
- Local Git history, annotated tag peel, and object existence.

### Default Exclusions

- `src/**`
- `tests/**`, `test/**` outside AI-context validation surfaces
- product implementation trees
- generated and dependency trees

### Additional Exclusions

- Published package bytes and migration schema changes.
- Remote GitHub mutation or re-publication.
- v0.5.0 implementation.

### Code Review Handoff

- Requested: `no`
- Paths not scanned: product source and product tests
- Recommended skill: not applicable

## Methodology And Evidence

### Pass A: Independent Baseline

- Treated repository records as untrusted until their identities could be
  recomputed from Git, file content, and executable validators.
- Required a published release to have one immutable tag target, one authored
  notes source, a non-empty compatibility/migration guide, truthful hosted-run
  evidence, and a terminal local registry state.
- Distinguished publication payload correctness from governance closeout
  correctness.

### Pass B: Repository-Aware Skill Review

- Applied workflow, assessment, version, commit, release registry, and
  AI-context evidence contracts.
- Re-ran the Fable reproduction commands and the critical workflow validator.
- Compared the v0.4.2 artifacts with the healthy v0.4.1 release registry and
  authored documents.

### Delegation

- Sub-agents used: `no`
- Assigned surfaces: none; multi-agent delegation was not requested.

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| None | `71c41dbd9c4f2b65105a616d15b7f1cc9db2a338` | clean tracked tree plus untracked external review | targeted governance surfaces only | not applicable | direct file reads, Git commands, and validators |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| External review | 7 files | maintainers/agents | independent evidence | preserved | does not follow repository assessment schema |
| v0.4.2 release registry | 3 files | maintainers/users | release truth | broken | validated state, polluted notes, empty guide |
| Publication workflow | locator, plan, 3 tasks | maintainers/agents | execution evidence | inconsistent | copied identities and false run evidence |
| Roadmap/backlog | roadmap, index, R042 items | maintainers/agents | live planning truth | stale | publication not reconciled |

## Strengths

1. Annotated `v0.4.2` resolves to the correct published commit
   `f474c3b058cb9f89f93929e0732fc1f276422dd9`.
2. The tag-triggered release validator failed closed for the first incorrect
   tag attempt, demonstrating that the core publish precondition works.
3. The external review is evidence-rich and explicitly asks the receiving
   agent to reproduce rather than trust its prose.
4. Existing v0.4.1 registry and release documents provide a healthy local
   comparison without requiring package-contract invention.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 | CRITICAL | The required workflow validator fails on `main`. | `validate-workflow-artifacts.py` reports a directory/ID mismatch, missing artifact root, and stale index row for the v0.4.2 publication workflow. | The repository's critical gate is red after release finalization. | Correct the locator, task identities, plan/checkpoint state, and workflow index without rewriting Git history. | `ai-context-governance` |
| AIC-002 | CRITICAL | `REL-v0.4.2` remains `validated` instead of `published`. | `release.yaml` lacks `tag`/`commit`; candidate discovery therefore retains v0.4.2 as an open candidate. | The next governed release candidate cannot be uniquely discovered. | Record the immutable tag target and truthful hosted publication evidence, then mark the registry published. | `ai-context-governance` |
| AIC-003 | HIGH | The local authored notes source is duplicated render output and the public body includes a non-object SHA. | Two automation markers and provenance sections exist; `git cat-file` rejects `1c13d7966b937004f12be6dd70d58c8ecb5afbe7`. | Local source is not safely re-renderable and public provenance is misleading. | Rewrite the local authored source now; regenerate the public body only after explicit authorization. | `ai-context-governance` plus repository maintainer |
| AIC-004 | HIGH | The v0.4.2 migration guide is empty. | `releases/v0.4.2/migration-guide.md` is zero bytes. | Consumers receive no compatibility or upgrade-path guidance. | Author the patch-compatible migration and source-version boundaries. | `ai-context-governance` |
| AIC-005 | HIGH | Publication workflow evidence contains copied or false values. | `REL042-002` uses v0.4.1 run `29650583394`; task timestamps and workflow IDs were copied; commit prose claims changes absent from its diff. | Future agents cannot trust the durable handoff record. | Correct mutable workflow artifacts, preserve the failed and successful run facts, and never rewrite the historical commits. | `ai-context-governance` |
| AIC-006 | MEDIUM | Roadmap and backlog remain at pre-publication state. | v0.4.2 is `ready_for_publication`; R042 items have `published_in: null`; Next Action points to already completed remediation. | Planning truth can reopen completed work and conceal the real v0.5.0 activation dependency. | Reconcile v0.4.2 publication and advance the current target only after local finalization passes. | `ai-context-governance` |
| AIC-007 | HIGH | Release publication and cross-model handoff rely on context continuity rather than cold-start-safe contracts. | No executable publication runbook, previous instances were copied, the only effective tag check ran after push, and validation claims did not require command output. | A fresh or lower-cost executor can repeat the same incident while producing policy-shaped prose. | Add a release runbook, instance templates, stale-value checks, pre-tag and terminal-state gates, PR CI, and a receiving-agent state-alignment gate. | `ai-context-governance` via v0.5.0 backlog |

## Baseline And Skill Comparison

### Confirmed

- Both passes confirm the package publication identity is correct while local
  finalization is broken.
- Both passes confirm that form-compliant commit messages did not establish
  truthful validation evidence.
- Both passes rank the red critical gate and unresolved release registry as
  immediate blockers.

### Added By Repository-Aware Review

- `release.yaml` terminal state is an activation dependency for unique future
  candidate discovery.
- Existing workflow and assessment lifecycle contracts provide a clean
  external-review normalization layer without requiring external reviewers to
  use repository templates.
- Public Release body repair is a separate external mutation and must not be
  silently treated as locally complete.

### Downgraded Or Deferred

- Missing `GEMINI.md` is not treated as a root cause because Gemini-authored
  commits demonstrate that repository rules were loaded.
- The simplification plan is useful planning input but is lower priority than
  release finalization and enforcement.

### Overturned

- None of Fable F1-F7 were overturned.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state | pass with external input | `main` and `origin/main` both at `71c41db`; only the supplied review was untracked |
| Workflow artifacts | fail reproduced | three failures for the v0.4.2 publication workflow |
| Tag identity | pass | `v0.4.2^{}` = `f474c3b058cb9f89f93929e0732fc1f276422dd9` |
| Invalid SHA object check | fail as expected | `git cat-file -t 1c13d...` reports no object |
| Release registry | fail reproduced | `status: validated`; no `tag` or `commit` |
| Release authored sources | fail reproduced | two render markers/provenance blocks; migration guide length 0 |
| AI context validator | pass | repo-native intake/remediation run passed after normalization |

### Skipped Validation

- GitHub Actions and Release facts were taken from the owner-supplied external
  evidence and local records; no remote mutation or redundant hosted lookup was
  performed during intake.
- Product source and tests were excluded.

## Recommended Action Order

1. Complete local `R042-005` repair without moving `v0.4.2`.
2. Reconcile v0.4.2 publication, R042 item publication metadata, and v0.5.0
   activation state.
3. Run an independent post-remediation assessment and the full repository gate.
4. With explicit authorization, regenerate and verify the public GitHub Release
   body from the corrected authored source.
5. Implement `REL-001`, `HANDOFF-001`, and aligned `ENF-001` work before the
   next publication.
6. Review Fable's simplification candidates only after the release surface is
   mechanically enforced.

## Deferred Items

- Public GitHub Release body replacement pending explicit authorization.
- v0.5.0 release runbook, templates, validators, pre-tag gate, PR CI, and
  handoff-gate implementation.
- Simplification and token-reduction plan.

## Appendix

### Commands Run

```text
python .ai/scripts/validate-workflow-artifacts.py
git cat-file -t 1c13d7966b937004f12be6dd70d58c8ecb5afbe7
git rev-parse 'v0.4.2^{}'
Select-String releases/v0.4.2/release.yaml
Select-String releases/v0.4.2/release-notes.md
Get-Item releases/v0.4.2/migration-guide.md
git log --oneline --decorate -12
git show-ref --dereference --tags
```

### Notes

- Source Fable finding IDs F1-F7 map in order to AIC-001 through AIC-006;
  AIC-007 normalizes the source root-cause and process findings.
- External source prose remains unchanged and retains its own authorship.

## Lifecycle Handoff

- Assessment path: `.dev/assessments/ASM-20260720-001/report.md`
- Stable finding references: `ASM-20260720-001#AIC-001` through `ASM-20260720-001#AIC-007`
- Remediation owner: `ai-context-governance`
- Related remediation workflow: `2026-07-20-v0-4-2-release-finalization-hotfix`
- Verification assessment: pending
- Remediation intentionally not performed by this skill: `yes`
