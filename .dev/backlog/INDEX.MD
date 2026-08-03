# Backlog Index

This index catalogs durable work that must remain visible outside workflow
artifact directories. See [README.MD](README.MD) for ownership and lifecycle.

## Active Release Roadmap

| Roadmap | Current Target | Status | Next Gate | Updated |
| --- | --- | --- | --- | --- |
| [ROADMAP.md](ROADMAP.md) | `v0.8.0` | `release preparation` | `SKILL-002`, `TOOL-002`, and `WIBIND-001` are the owner-approved exact release set; execute the candidate workflow and stop at the immutable-tag owner gate. | 2026-08-03 |

Source planning records are retained under [`plans/`](plans/); they inform the
roadmap but do not replace it or a governed assessment.

## In Progress

No canonical backlog item is currently in progress.

## Planned / Open

| Item | Priority | Target Release | Gate | Summary | Decision / Handoff | Updated |
| --- | --- | --- | --- | --- | --- | --- |
| [REL-004](items/REL-004.yaml) | MEDIUM | `unassigned` | independent | Evaluate a repo-only AI context release closeout capability that simplifies post-tag registry finalization without leaking into the published framework. | Decide naming, source-only placement, product-isolation proof, zero skill dependencies, runtime fallback, failure containment, and terminal Git behavior before implementation. | 2026-07-28 |
| [INIT-001](items/INIT-001.yaml) | LOW | `unassigned` | independent | Evaluate safe framework adoption in repositories that already use AI agents. | Define collision inventory, dry-run, authority, and synthetic fixtures before a future real-target pilot. | 2026-07-27 |
| [DEVWF-001](items/DEVWF-001.yaml) | MEDIUM | `unassigned` | independent | Evaluate optional issue traceability and richer task lifecycle timestamps from WorkService. | Keep the portable core tracker-neutral; decide schema placement and compatibility before implementation. | 2026-07-22 |
| [STD-001](items/STD-001.yaml) | HIGH | `unassigned` | planned; related to `OBS-001` | Run three bounded rounds on workflow-mode proportionality, code-review progressive disclosure, and terminology discovery before assigning implementation to a release. | Complete applicable standards-format decisions before `OBS-001` publishes a canonical standard; permit a dedicated standards release after owner review. | 2026-07-30 |
| [OBS-001](items/OBS-001.yaml) | MEDIUM | `unassigned` | related to `STD-001` | Design the reusable CrossCutting Observability and attribute/AOP boundary. | Read-only architecture evidence may proceed; standards structure, placement, and publication wait for applicable `STD-001` decisions unless the owner grants an exception. | 2026-07-30 |

## Declined

| Item | Priority | Target Release | Decision | Resolution | Updated |
| --- | --- | --- | --- | --- | --- |
| [UPG-001](items/UPG-001.yaml) | HIGH | `unassigned` | Owner cancelled the real legacy-target intake because no target or feedback capacity is expected to be available. | Historical evidence is retained; `INIT-001` tracks a distinct existing-AI-agent initialization question without claiming to complete the legacy upgrade acceptance. | 2026-07-27 |

## Resolved / Awaiting Publication

| Item | Priority | Completed In | Publication Gate | Resolution | Workflow | Updated |
| --- | --- | --- | --- | --- | --- | --- |
| [WIBIND-001](items/WIBIND-001.yaml) | MEDIUM | `v0.8.0` | Included by the 2026-08-03 owner decision; `published_in` remains unset until immutable publication. | PR #73 merged the provider-neutral policy as `d4d9220`; PR #74 retained workflow closeout evidence as `2263744`. | [`2026-07-31-work-item-binding-policy`](../workflows/2026-07-31-work-item-binding-policy/workflow.yaml), [`2026-08-03-v0-8-0-release-publication`](../workflows/2026-08-03-v0-8-0-release-publication/workflow.yaml) | 2026-08-03 |
| [TOOL-002](items/TOOL-002.yaml) | MEDIUM | `v0.8.0` | Await separately authorized `v0.8.0` publication; `published_in` remains unset. | PR #78 merged the validated prerequisite contract as `2070e44`; Issue #77 and Project #3 closed only after merged-main read-back. | [`2026-08-02-python-prerequisite-diagnostics`](../workflows/2026-08-02-python-prerequisite-diagnostics/workflow.yaml) | 2026-08-03 |
| [SKILL-002](items/SKILL-002.yaml) | HIGH | `v0.8.0` | Await separately authorized `v0.8.0` publication; `published_in` remains unset. | PR #66 merged the validated canonical-skill colocation into `main`; Issue #65 closed only after merge read-back. | [`2026-07-30-skill-script-colocation`](../workflows/2026-07-30-skill-script-colocation/workflow.yaml) | 2026-07-30 |

## Resolved

| Item | Priority | Completed In | Published In | Resolution | Workflow | Updated |
| --- | --- | --- | --- | --- | --- | --- |
| [GOV-002](items/GOV-002.yaml) | HIGH | `v0.7.0` | `v0.7.0` | Provider-neutral lifecycle and repository-truth policy is projected downstream; source-local GitHub policy remains excluded and provider adoption remains deferred. | [`2026-07-27-v0-7-governance-release-readiness`](../workflows/2026-07-27-v0-7-governance-release-readiness/workflow.yaml) | 2026-07-28 |
| [GOV-003](items/GOV-003.yaml) | HIGH | `v0.7.0` | `v0.7.0` | The AI execution provenance and attribution policy is complete, independently verified, and published. | [`2026-07-27-ai-execution-provenance-policy`](../workflows/2026-07-27-ai-execution-provenance-policy/workflow.yaml) | 2026-07-28 |
| [PKG-004](items/PKG-004.yaml) | HIGH | `v0.7.0` | `v0.7.0` | Deterministic payload, source-history exclusion, portable-policy mapping, clean-install, and initialized-upgrade evidence pass. | [`2026-07-27-v0-7-governance-release-readiness`](../workflows/2026-07-27-v0-7-governance-release-readiness/workflow.yaml) | 2026-07-28 |
| [REL-003](items/REL-003.yaml) | HIGH | `v0.7.0` | `v0.7.0` | Candidates fail closed unless backlog refs and generated Included Work match the canonical completed backlog set exactly while authored notes remain intact. | [`2026-07-28-v0-7-0-release-preparation`](../workflows/2026-07-28-v0-7-0-release-preparation/workflow.yaml) | 2026-07-28 |
| [CI-001](items/CI-001.yaml) | HIGH | `v0.6.0` | `v0.6.0` | Candidate and publication workflows execute native Node.js 24 artifact actions with hosted package and publication evidence. | [`2026-07-24-v0-6-ci-lifecycle`](../workflows/2026-07-24-v0-6-ci-lifecycle/workflow.yaml) | 2026-07-24 |
| [CI-002](items/CI-002.yaml) | HIGH | `v0.6.0` | `v0.6.0` | The four-workflow responsibility, trigger, concurrency, mutation, and release-phase lifecycle matrix is verified through publication. | [`2026-07-24-v0-6-ci-lifecycle`](../workflows/2026-07-24-v0-6-ci-lifecycle/workflow.yaml) | 2026-07-24 |
| [EVAL-001](items/EVAL-001.yaml) | HIGH | `v0.6.0` | `v0.6.0` | Deterministic regression and the owner-selected Terra evaluation passed 8/8 critical and 8/8 full outcomes. | [`2026-07-24-v0-6-model-evaluation`](../workflows/2026-07-24-v0-6-model-evaluation/workflow.yaml) | 2026-07-24 |
| [SKILL-001](items/SKILL-001.yaml) | MEDIUM | `v0.6.0` | `v0.6.0` | `ai-context-init` and `software-development-orchestrator` are active with thin deprecated compatibility aliases and no scheduled removal. | [`2026-07-24-v0-6-config-skill-transition`](../workflows/2026-07-24-v0-6-config-skill-transition/workflow.yaml) | 2026-07-24 |
| [CFG-001](items/CFG-001.yaml) | HIGH | `v0.6.0` | `v0.6.0` | ADR-001 is accepted; source configuration, dedicated downstream seeds, centralized immutable evidence, exact upgrades, and target-owned preservation are verified. | [`2026-07-24-v0-6-config-skill-transition`](../workflows/2026-07-24-v0-6-config-skill-transition/workflow.yaml) | 2026-07-24 |
| [SIMPL-001](items/SIMPL-001.yaml) | MEDIUM | `v0.6.0` | `v0.6.0` | Five controlled session families and seven candidate dispositions were independently verified; the root entry shrank 12.9% without deleting history, and archive migration remains a separately approved v0.7.0 concern. | [`2026-07-24-v0-6-context-load-simplification`](../workflows/2026-07-24-v0-6-context-load-simplification/workflow.yaml) | 2026-07-24 |
| [DIST-001](items/DIST-001.yaml) | HIGH | `v0.6.0` | `v0.6.0` | Componentized release metadata, optional backlog selection, source-only projection, and deterministic clean/upgrade behavior pass the immutable package matrix. | [`2026-07-23-v0-6-product-contract-planning`](../workflows/2026-07-23-v0-6-product-contract-planning/workflow.yaml) | 2026-07-24 |
| [CUST-001](items/CUST-001.yaml) | HIGH | `v0.6.0` | `v0.6.0` | One target-owned semantic customization ledger, four-skill lifecycle, fail-closed validation, and aggregate regressions are independently verified. | [`2026-07-23-v0-6-product-contract-planning`](../workflows/2026-07-23-v0-6-product-contract-planning/workflow.yaml) | 2026-07-24 |
| [DEVWF-002](items/DEVWF-002.yaml) | HIGH | `v0.6.0` | `v0.6.0` | Preclassified high-level activation, approval pause, target-aware tests, selectable compliance, commit batching, and repository-verified fresh-session acceptance pass. | [`2026-07-23-v0-6-product-contract-planning`](../workflows/2026-07-23-v0-6-product-contract-planning/workflow.yaml) | 2026-07-24 |
| [REL-002](items/REL-002.yaml) | HIGH / P0 | `v0.5.0` | `v0.5.0` | Git Bash selection, child PATH, byte decoding, and complete failure diagnostics passed local and hosted gates before immutable tag publication. | [`2026-07-22-v0-5-0-pretag-portability-hotfix`](../workflows/2026-07-22-v0-5-0-pretag-portability-hotfix/workflow.yaml) | 2026-07-22 |
| [REL-001](items/REL-001.yaml) | HIGH | `v0.5.0` | `v0.5.0` | Repository-owned release mechanics, hosted publication, and terminal finalization completed for REL-v0.5.0. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-22 |
| [HANDOFF-001](items/HANDOFF-001.yaml) | HIGH | `v0.5.0` | `v0.5.0` | The registered receiving checkpoint fails closed across model/runtime/host/session boundaries, preserves native attribution, and passes the repository critical gate. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [ENF-001](items/ENF-001.yaml) | HIGH | `v0.5.0` | `v0.5.0` | Semantic wrapper enforcement, evidence-bound published-path dispositions, source/downstream routing, and the read-only governance PR workflow are verified locally and on hosted Ubuntu. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [LANG-001](items/LANG-001.yaml) | MEDIUM | `v0.5.0` | `v0.5.0` | The stale 21-item planning count is reconciled; four active defects are fixed, deterministic language/structure fixtures pass, and both root bilingual pairs pass retained semantic review at `2db0636`. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [TOOL-001](items/TOOL-001.yaml) | MEDIUM | `v0.5.0` | `v0.5.0` | Retain the literal runner with fail-closed format/set parity; Windows Git Bash, hosted Ubuntu, and the owner-arranged macOS host pass the governed gates, and inherited Python override leakage is isolated by regression coverage. | [`2026-07-22-v0-5-0-macos-portability`](../workflows/2026-07-22-v0-5-0-macos-portability/workflow.yaml) | 2026-07-22 |
| [VAL-001](items/VAL-001.yaml) | LOW | `v0.5.0` | `v0.5.0` | Repository validation is superseded; deterministic offline dependency/version consistency is required and online currency/vulnerability checks remain advisory. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [SAG-001](items/SAG-001.yaml) | MEDIUM | `v0.5.0` | `v0.5.0` | Dynamic loading remains the default for 17 roles; context-translator alone has exact Codex, Claude, and Copilot adapters with deterministic schema, canonical-link, path, and package validation. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [PKG-003](items/PKG-003.yaml) | HIGH | `v0.5.0` | `v0.5.0` | REL-v0.5.0 publishes deterministic exact upgrades from v0.3.0, v0.4.0, v0.4.1, and v0.4.2. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-22 |
| [GOV-001](items/GOV-001.yaml) | MEDIUM | `v0.5.0` | `v0.5.0` | Legacy follow-ups are reconciled as satisfied, superseded, intentionally retained, or non-requirement suggestions without rewriting historical artifacts. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [CAP-001](items/CAP-001.yaml) | LOW | `v0.5.0` | `v0.5.0` | Terminology remains a domain-language document pattern; no repeated action evidence justifies a dedicated skill. | [`2026-07-21-v0-5-0-development`](../workflows/2026-07-21-v0-5-0-development/workflow.yaml) | 2026-07-21 |
| [R042-005](items/R042-005.yaml) | HIGH / P0 | `v0.4.2` | — | Local finalization and the authorized public Release body correction are verified; the immutable tag and four published assets were unchanged. | [`2026-07-20-v0-4-2-release-finalization-hotfix`](../workflows/2026-07-20-v0-4-2-release-finalization-hotfix/workflow.yaml) | 2026-07-20 |
| [R042-001](items/R042-001.yaml) | HIGH | `v0.4.2` | `v0.4.2` | Existing wrapper identity and routing corrections are independently verified without adding adapter contracts. | [`2026-07-19-v0-4-2-remediation`](../workflows/2026-07-19-v0-4-2-remediation/workflow.yaml) | 2026-07-20 |
| [R042-002](items/R042-002.yaml) | HIGH | `v0.4.2` | `v0.4.2` | Handler, time, naming, and spec examples align with existing canonical doctrine. | [`2026-07-19-v0-4-2-remediation`](../workflows/2026-07-19-v0-4-2-remediation/workflow.yaml) | 2026-07-20 |
| [R042-003](items/R042-003.yaml) | MEDIUM | `v0.4.2` | `v0.4.2` | Navigation and lifecycle facts are corrected while published historical paths remain retained. | [`2026-07-19-v0-4-2-remediation`](../workflows/2026-07-19-v0-4-2-remediation/workflow.yaml) | 2026-07-20 |
| [R042-004](items/R042-004.yaml) | HIGH | `v0.4.2` | `v0.4.2` | Patch-safe interpreter, dependency, root, and test portability corrections pass Windows Git Bash and Codespaces Ubuntu 24.04. | [`2026-07-19-v0-4-2-remediation`](../workflows/2026-07-19-v0-4-2-remediation/workflow.yaml) | 2026-07-20 |
| [PKG-001](items/PKG-001.yaml) | HIGH / P0 | `v0.4.1` | `v0.4.1` | Versioned migration metadata binds the exact v0.3.0 manifest and produces deterministic executable operations. | [`2026-07-18-v0-4-1-downstream-upgrade-remediation`](../workflows/2026-07-18-v0-4-1-downstream-upgrade-remediation/workflow.yaml) | 2026-07-18 |
| [PKG-002](items/PKG-002.yaml) | HIGH / P0 | `v0.4.1` | `v0.4.1` | Source-only suites remain required at source and are excluded/not-applicable in downstream packages; extracted target gate passed 19/19. | [`2026-07-18-v0-4-1-downstream-upgrade-remediation`](../workflows/2026-07-18-v0-4-1-downstream-upgrade-remediation/workflow.yaml) | 2026-07-18 |
| [CTX-003](items/CTX-003.yaml) | HIGH | `v0.1.0` | `v0.1.0` | Remediated and independently verified all five CTX-001 findings with no regression. | [`2026-07-12-ai-context-truth-contract-remediation`](../workflows/2026-07-12-ai-context-truth-contract-remediation/workflow.yaml) | 2026-07-18 |
| [CTX-001](items/CTX-001.yaml) | HIGH | `v0.1.0` | `v0.1.0` | Completed the independent post-AIC-007 audit; five findings were handed to AI context governance. | [`2026-07-12-post-aic-007-ai-context-audit`](../workflows/2026-07-12-post-aic-007-ai-context-audit/workflow.yaml) | 2026-07-18 |
| [CTX-002](items/CTX-002.yaml) | HIGH | `v0.1.0` | `v0.1.0` | Removed the retired generated-script catalog entry and restored AI context validation. | [`2026-07-12-ctx-002-ai-index-repair`](../workflows/2026-07-12-ctx-002-ai-index-repair/workflow.yaml) | 2026-07-18 |
| [AIC-007](items/AIC-007.yaml) | HIGH | `v0.1.0` | `v0.1.0` | Required gates fail closed; Git-index executable modes and runner/manifest parity are validated with GWT fixtures. | [`2026-07-11-aic-007-fail-closed-validation`](../workflows/2026-07-11-aic-007-fail-closed-validation/workflow.yaml) | 2026-07-18 |
