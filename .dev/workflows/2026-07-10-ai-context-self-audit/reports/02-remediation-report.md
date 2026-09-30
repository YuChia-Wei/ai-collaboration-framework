# AI Context Remediation Report

## Report Metadata

- `report_id`: `remediation-report-2026-07-10-ai-context-self-audit`
- `workflow_id`: `2026-07-10-ai-context-self-audit`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-07-11T08:18:07+08:00`
- `updated_at`: `2026-07-11T23:30:00+08:00`
- `template_source`: `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`
- `template_version`: `1.0.0`
- `baseline_report`: `.dev/workflows/2026-07-10-ai-context-self-audit/reports/01-audit-report.md`
- `post_remediation_report`: `.dev/workflows/2026-07-10-ai-context-self-audit/reports/03-post-remediation-audit-report.md`

## Remediation Summary

- Authorized scope: triage and begin correcting AIC-001 through AIC-009 without scanning product `src/` or `tests/` trees.
- Completed scope: current-evidence triage; Batch 1 corrections for AIC-003, AIC-006, AIC-008, and the objective portion of AIC-009; user-decided testing contract for AIC-002.
- Completed machine-governance batch: AIC-001 ownership, AIC-004 canonical schema, and AIC-005 deterministic capability routing now have candidate resolutions.
- Closure decision: `closed-with-deferred-finding`; AIC-007 remains owned by a separate tooling workflow.

## Finding Resolution Matrix

| Finding | Before Severity | Current Status | Evidence Summary | Planned Action | Owner / Decision |
| --- | --- | --- | --- | --- | --- |
| AIC-001 | HIGH | `resolved` | Independent post-audit confirmed the ownership policy, six registered conflicted rule families, declared projections, and conditional soft deletion close the baseline ambiguity. | Expand the registry incrementally when another cross-surface conflict is found. | Governance maintenance. |
| AIC-002 | HIGH | `resolved` | Canonical and human guidance now define BDDfy as the default with explicit opt-out, mandatory GWT without 3A fallback, and conditionally supported `.feature` artifacts. | Request independent verification across testing consumers. | User decision implemented; auditor verifies. |
| AIC-003 | HIGH | `resolved` | Stale onboarding is now explicitly legacy/profile-conditional, current initialization routes to `repo-structure-sync`, and missing `CLAUDE.md` links were removed. | Request independent verification; retained profile examples must remain conditional. | Governance completed; auditor verifies. |
| AIC-004 | HIGH | `resolved` | Independent post-audit confirmed schema v1.0, `asset_id`, 30 conforming active manifests, four canonical templates, and structural/path validation. | Register discovery roots and validator coverage before activating another manifest family. | Governance maintenance. |
| AIC-005 | HIGH | `resolved` | Independent post-audit confirmed ten deterministic mappings, matching skill `capability_slots`, and YAML/Markdown parity validation. | Validate the profile whenever a skill or mapping changes. | Dev-workflow contract maintained by governance. |
| AIC-006 | HIGH | `resolved` | Workflow/commit policies and auditor contracts now distinguish transient conversational analysis, durable report-only audit, and governance remediation. | Request independent verification of authorization and persistence boundaries. | Governance completed; auditor verifies. |
| AIC-007 | HIGH | `deferred` | Required shell checks remain mode `100644`; `check-all.sh` can exit zero after required checks are skipped as warnings. | Create tooling/validation workflow for fail-closed gates and executable-mode enforcement. | Tooling workflow; outside this documentation-governance batch. |
| AIC-008 | MEDIUM | `resolved` | Current catalogs list Agents/Codex and Claude; Gemini paths, targets, branch prefixes, and descriptions were removed; Copilot alone remains planned/optional. | Request independent runtime-truth verification. | Governance completed; auditor verifies. |
| AIC-009 | MEDIUM | `resolved` | Translation waves 1-5 corrected 46 agent-facing documents including `src/knowledge/dotnet-backend/design/architecture-overview.md`; policy-aware lint now checks tracked and untracked context, exact language exceptions, active paths/runtime/wrapper parity, and root bilingual structural parity. | Request independent verification; do not interpret structural parity as semantic translation equivalence. | Governance completed; auditor verifies. |

## Remediation Batches

### Batch 1 — Stop Active Wrong Guidance

- AIC-003: downgrade or rewrite stale onboarding and missing entry references.
- AIC-006: define transient read-only and durable report-only audit modes.
- AIC-008: correct the supported runtime matrix.
- AIC-009: repair active index corruption and add narrow objective context validation.

### Batch 2 — Machine Governance

- AIC-001: candidate resolution established per-rule ownership for the conflicted testing, Aggregate/UoW, mapper-event, and deletion families.
- AIC-004: schema v1.0 and all 30 active canonical manifests migrated; duplicate template family removed and structural validation added.
- AIC-005: deterministic machine-readable capability profile and profile-to-skill validation added.

### Decision / Reroute

- AIC-002: decision received and implemented: BDDfy default with explicit opt-out, mandatory GWT, no 3A substitution, conditional `.feature` support.
- AIC-007: defer to a dedicated tooling/validation workflow.

## Validation Plan

- Structured YAML/JSON parse with PyYAML and Python JSON tooling.
- Active path and wrapper/runtime declaration checks.
- Workflow artifact validation and `git diff --check`.
- Repository `check-all.sh --quick`, while retaining AIC-007 because its current warning/exit semantics are under review.
- Independent `ai-context-auditor` post-remediation report before closure.

## Changes And Evidence

### AIC-003

- Changes: downgraded `coding-guide.md` and `NEW-PROJECT-GUIDE.md` to legacy/retired examples; made fixed stack choices conditional; routed current initialization to `repo-structure-sync`; repaired root-entry references and indexes.
- Evidence: `.dev/standards/coding-guide.md`, `src/knowledge/dotnet-backend/guides/NEW-PROJECT-GUIDE.md`, `src/knowledge/dotnet-backend/guides/LEARNING-PATH.md`, their README/INDEX owners.
- Validation: targeted searches found no stale `CLAUDE.md` link or active Todo application identity in the corrected entries; repository diff check passed.
- Remaining risk: architecture-specific examples must not be promoted back to target truth without explicit adoption.

### AIC-002

- Decision: BDDfy is the default profile, but a target team may explicitly decline the package. Unit, use-case, and integration tests must still use recognizable Given-When-Then structure and naming; Arrange-Act-Assert/3A is not an allowed substitute.
- Feature policy: `.feature` is optional and not generated by default. It is supported when supplied directly, explicitly requested for design/generation, or enabled by a target profile that names a runner. The context must not infer a runner or package.
- Evidence: dotnet-backend shared testing rules, code-review references, test sub-agent prompts, `bdd-gwt-test-designer`, `spec-compliance-validator`, `.dev/standards/coding-standards/test-standards.md`, and `.dev/specs/tests/` were synchronized.
- Validation: relevant YAML parsed with PyYAML; `bdd-gwt-test-designer` passed `quick_validate.py`; active non-example search found no remaining BDDfy-only/no-feature prohibition or positive 3A rule.
- Remaining risk: historical/reference examples may still demonstrate a specific runner but must remain non-normative.

### AIC-006

- Changes: added transient read-only direct mode, durable report-only workflow mode, and remediation lifecycle boundaries to workflow/commit policy, auditor canonical assets, runtime wrappers, and human guides.
- Evidence: `.dev/standards/WORKFLOW-GATE-POLICY.md`, `.dev/standards/GIT-COMMIT-POLICY.md`, `.ai/assets/skills/ai-context-auditor/`, `.agents/skills/ai-context-auditor/`, `.claude/skills/ai-context-auditor/`.
- Validation: auditor and governance wrappers passed `quick_validate.py`; changed YAML parsed with PyYAML.
- Remaining risk: post-remediation audit must test that generic multi-pass analysis does not accidentally create repository artifacts.

### AIC-008

- Changes: corrected repository identity and runtime catalogs, then removed Gemini targets, templates, branch prefixes, paths, and descriptions entirely. GitHub Copilot remains a planned/optional adapter.
- Evidence: `README.md`, `README.en.md`, `agents.md`, `agents.zh-tw.md`, `.dev/INDEX.md`, `.dev/guides/ai-collaboration-guides/LOCAL-RUNTIME-WRAPPER-GUIDE.md`.
- Validation: new AI context validator confirmed two current runtime roots and wrapper parity.
- Remaining risk: planned adapters must be deliberately promoted and validated when implemented.

### AIC-009

- Changes: repaired three literal table corruptions; added `.ai/scripts/validate-ai-context.py`; translated six active `.ai` documents, five test-spec documents, and problem-frame semantics; declared canonical/translated ownership for root bilingual entries and synchronized auditor mode descriptions.
- Evidence: translated `.ai` files include the code-review index, pitfalls, building-block index, shared/template READMEs, and canonical schema. Translated `.dev` files include test-spec guidance and `.dev/problem-frames/SEMANTICS.md`.
- Validation: translated execution contracts have no residual Han prose; relative Markdown links resolve; root README/agents pairs pass semantic parity review; context lint and repository quick checks pass.
- Remaining risk: 21 high-priority and several medium-priority `.dev/standards`/`.dev/specs` translation candidates remain. Language lint stays deferred until that backlog is reduced and explicit trigger/domain exceptions are encoded.

## Translation Migration Progress

### Wave 1 — Completed

- Six active `.ai` agent-facing documents translated to English.
- Five `.dev/specs/tests` execution documents translated to English while preserving BDDfy-default, mandatory-GWT, no-3A, and conditional-`.feature` semantics.
- `.dev/problem-frames/SEMANTICS.md` translated to English.
- `README.md` / `README.en.md` and `agents.md` / `agents.zh-tw.md` now declare canonical versus translated ownership; auditor descriptions and root-entry catalogs are synchronized.

### Wave 2 — Completed

- Translated `.dev/standards/coding-standards/test-standards.md` while preserving BDDfy-default, mandatory-GWT, no-3A, optional-`.feature`, and no-`BaseTestClass` rules.
- Translated the repository code-review checklist and ASP.NET Core configuration checklist.
- Translated the primary spec authoring and organization guides.
- Translated the ADR catalog and remaining short standards entry surfaces selected for this wave.
- Corrected one positive Contract Test example that still used Arrange/Act terminology; negative examples retain it only as explicitly incorrect behavior.

### Wave 3 — Completed

- Translated aggregate and use-case standards.
- Translated repository and mapper standards.
- Translated controller, projection, reactor, and archive standards.
- Preserved code, identifiers, architecture boundaries, rule strength, and positive/negative example labels.
- Translation review exposed three pre-existing semantic-governance issues without silently changing their architecture decisions:
  - the one-command/one-aggregate rule versus the multi-aggregate `IUnitOfWork` example;
  - the mapper `ClearDomainEvents()` checklist versus an event-rebuild example that omits it;
  - the soft-delete/hard-delete prohibition versus an EF example that calls `Remove()`.

### Wave 4 — Completed

- Translated the main coding-standards entry and coding-standards registry.
- Translated project-structure, anti-pattern, and best-practice contracts.
- Translated profile-configuration and UseCase/Command/Handler relationship standards.
- Translated the selected rationale catalog and rationale documents while preserving the distinction between normative standards and explanatory rationale.
- No new rule conflicts were identified during this wave.
- Updated `check-coding-standards.sh` section matching from retired Chinese headings to the translated English canonical headings; this is a narrow validator-compatibility correction, not the deferred fail-closed tooling redesign.

### Wave 5 — Completed

- Translated the ADR creation guide and development-tools guide.
- Translated database migration and EF Core configuration guides while preserving their conditional technology scope.
- Translated application-properties and profile-isolated configuration templates without changing configuration values, placeholders, or code semantics.
- The remaining Han matches in active scoped surfaces are intentional user trigger phrases or script output/pattern semantics, not untranslated documentation prose.

### Language And Bilingual Structural Lint — Completed

- `validate-ai-context.py` scans both cached and untracked non-ignored agent-facing context so new files cannot bypass the gate before staging.
- Product `src/`, `test/`, and `tests/` roots are explicitly excluded, including their indexes; active context indexes remain checked.
- Han exceptions are exact path-and-line contracts for the auditor's two Traditional Chinese routing triggers and the workflow gate's user-trigger line. Additional Han on those paths still fails.
- Markdown documentation under `.ai/scripts` is checked; script source lexical scanning remains deferred because comments, output, and rule patterns may carry execution semantics.
- Root bilingual entries are checked for reciprocal links, ownership markers, heading-level shape, ordered backtick table paths, and the required root catalog rows.
- The validator reports structural parity only and explicitly does not claim semantic translation equivalence.
- `src/knowledge/dotnet-backend/design/architecture-overview.md` was translated to English and added as an explicit language-policy surface.
- Negative probes confirmed that an untracked Han Markdown file fails before staging and that exact allowlist lines do not permit unrelated Han prose.

## Architecture Semantic Reconciliation

### Aggregate And Unit Of Work

- Established one Command/one Aggregate as the default transaction model; cross-Aggregate effects use events and eventual consistency by default.
- Restricted multi-Aggregate `IUnitOfWork` to a documented same-bounded-context exception with a named all-or-nothing invariant, unacceptable/non-compensable intermediate state, Aggregate-boundary recheck, and explicit involved-Aggregate evidence.
- Prohibited adopting the exception for shared storage, I/O reduction, ORM/framework capability, convenience, general future need, default dependency injection, or cross-bounded-context transactions.
- Ownership: Aggregate standards own the default transaction boundary; Use Case standards own exceptional orchestration criteria; the architect playbook summarizes and links them.

### Mapper Rehydration Events

- Replaced the unconditional method-call rule with the canonical invariant that `ToDomain()` returns an Aggregate with no pending `DomainEvents`.
- Rehydration constructors should replay through `When(...)` or an equivalent non-enqueuing path. When constructor cleanliness is unknown or reconstruction enqueues events, the mapper explicitly calls `ClearDomainEvents()` before return.
- Updated the unknown `Product` examples conservatively and synchronized code-review/example summaries without changing already-correct `PlanMapper` examples.
- Ownership: mapper standards own the invariant; code-review indexes and examples are derived consumers.

### Archive State And Physical Purge

- General Archive ports now expose lookup and save only; archived/soft-delete state belongs to read-side data and is persisted rather than physically deleted.
- Explicit state transitions use `ArchiveAsync`/`MarkArchivedAsync` semantics, not ambiguous `DeleteAsync`.
- Physical read-model purge is isolated behind a restricted capability-specific port with authorization, retention, legal-hold, audit-evidence, and dependent-cleanup gates. It is not an Aggregate purge port or normal Reactor dependency.
- Removed EF `Remove()` from positive Archive examples and synchronized the inquiry-archive contract and usage guidance.
- Ownership: Archive standards own read-model state/retention behavior; Repository standards continue to own Aggregate deletion and restricted Aggregate purge principles.
- Residual tooling debt: generated archive shell checks still carry the retired lexical `HardDelete` rule and remain part of deferred AIC-007 tooling remediation.

### Next Translation Waves

1. Request the independent post-remediation audit for candidate-resolved findings.
2. Preserve the generated archive-check drift under deferred AIC-007 tooling ownership.
3. Request an independent post-remediation audit after the remaining finding work is complete.

Each wave must preserve identifiers, paths, code blocks, normative strength, and explicit language exceptions. Do not create bilingual copies for non-entry execution contracts.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| AIC-007 | Requires executable-mode and gate-semantics tooling changes, not only context documentation. | Tooling workflow | Create a dated tooling workflow and make required gates fail closed. |

## Independent Post-Remediation Audit

- Report: `reports/03-post-remediation-audit-report.md`
- Decision: `remediation-recommended`, score `8.8/10`.
- Independently resolved: AIC-001, AIC-002, AIC-003, AIC-004, AIC-005, AIC-006, AIC-008, and AIC-009.
- Confirmed deferred: AIC-007 remains `HIGH` because tracked shell scripts use mode `100644` and required skipped checks can still yield exit `0`.
- Regressions or new findings: none.
- Closure interpretation: this documentation-governance lifecycle may close with AIC-007 explicitly deferred; overall repository health remains `remediation-recommended` until the tooling workflow resolves it.

## Closure Evidence

- Required validations: context and workflow validators passed; mutation probes failed as expected and were restored; quick gate passed 5/5 with 49/49 tooling tests; independent post-audit completed.
- Commit status: remediation checkpoints include `7f75c77` (AIC-001) and `e971d0f` (AIC-004/AIC-005); final report and closure metadata are included in the lifecycle closure commit.
- Workflow/task status: AICSA-001 through AICSA-005 completed; AIC-007 explicitly deferred.
- Final next action: create a new dated tooling/validation workflow and branch for AIC-007 when authorized.
