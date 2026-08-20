# UPG-003 Retained-Origin Multi-Hop Upgrade

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-20-upg-003-multi-hop-upgrade`
- `plan_id`: `development-plan-2026-08-20-upg-003-multi-hop-upgrade`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-21-upg-003-v014-source-candidate-s3`
- `base_branch`: `main`
- `branch_segment`: `3`
- `status`: `active`
- `created_at`: `2026-08-20T17:03:25+08:00`
- `updated_at`: `2026-08-21T04:10:28+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/`

## Development Objective

- Product or software outcome: Preserve supported v0.6.0, v0.9.0, and immediate-predecessor upgrades behind one user operation while resolving exact routes before mutation.
- Current lifecycle entry point: S3 v0.14.0 source-candidate and cumulative route proof from integrated #207/#208 main `bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`.
- User constraints: Use one online Issue #206 and this one technical workflow across three sequential PRs; S1 and S2 defer closure, S3 terminal-closes #206.
- Non-goals: Target mutation in S1; duplicating #200 transactions or #203 remediation/finalization; changing historical backlog/roadmap; Project-field restoration; tag, Release, publication, or nightly activation.

## Inputs

- Requirements: Live Issue #206, open release-coordination Issue #222, and explicit repository-owner v0.14.0 instructions.
- Specifications: Existing package/migration schemas, checksums, validators, provenance and semantic-customization contracts.
- Architecture decisions: Four exact route kinds; proven direct first unless a semantic cutover would be bypassed; ambiguity and missing assets fail before mutation; deprecation requires explicit owner evidence.
- Existing implementation or tests: #200 durable package apply, #201 package closure, #203 single-hop remediation correctness, and published release assets.

## Development Stages

### Stage 1

- `stage_id`: `UPG-003-S1`
- Goal: Deliver the support policy, machine-readable support matrix, and read-only route resolver.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Immediate predecessor, v0.9.0, and v0.6.0 origins; direct, orchestrated-multi-hop, reconciliation-required, unsupported; exact edges/assets/cutovers; ambiguity, missing-asset, bypass, and deprecation gates.
- Non-goals: Target mutation, transaction sequencing, resume, rollback, or final provenance.
- Dependencies: Integrated #200, #201, #203 and live published release identities.
- Validation: Focused route GWTs, isolated package projection, source governance, exact-head independent audit, hosted checks, deferred Issue read-back.
- Commit checkpoint: One deferred PR with `Refs #206`; #206 remains open because S2 transaction and S3 v0.14 candidate proof remain.

### Stage 2

- `stage_id`: `UPG-003-S2`
- Goal: Compose one user operation from immutable per-hop transactions with interruption, resume, rollback, and no mixed provenance.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Compose S1 with #200, #201, and #203; retain per-hop package, manifest, checksum, validator, decision, and receipt evidence.
- Non-goals: Final v0.14.0 source candidate or Issue closure.
- Dependencies: Merged S1 deferred PR.
- Validation: Focused multi-hop transaction, interruption, resume mismatch, rollback, cutover, and validation-disagreement GWTs; exact-head independent audit and hosted checks.
- Commit checkpoint: One deferred PR with `Refs #206`; #206 remains open pending S3 release proof.

### Stage 3

- `stage_id`: `UPG-003-S3`
- Goal: Instantiate and prove the governed v0.14.0 source candidate across retained origins.
- Capability slot: `ai-context-upgrader`
- Owner skill: `ai-context-upgrader`
- Scope: Release matrix, notes, migration guide, phase checks, route evidence, exact candidate package and retained-origin proof.
- Non-goals: Tag, Release, asset/package publication, or coordination-Issue closure.
- Dependencies: Merged #203, #205, #207, #208 and S1/S2.
- Validation: Candidate package, v0.13/v0.9/v0.6 routes, release profile, provider/delegation paths, fixed-head audit, hosted provider preflight.
- Commit checkpoint: One terminal-close PR for #206; coordination Issue #222 remains open.

## Role Execution Coordination

Before #207 integrates, every delegated context is generic and is not evidence that #207 canonical roles exist or were invoked.

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| UPG-003-S1 | pre-#207 generic bounded contexts / no canonical path | ai-context-upgrader | integrated | Terra Max performed bounded implementation and repair work. Fresh Sol High passed exact admitted head `95b37747cee83cbe837bca9438b2450ee8c1bb85`; five hosted contexts and live merge admission passed; PR #226 merged as `41a1b4bcc942b9a412d55a8dab77bcc5d7b6fbf2`. Earlier failed audits and hosted attempts remain retained. | root / merged exact admitted head and kept #206 open | `tasks/UPG-003-S1.json` |
| UPG-003-S2 | pre-#207 generic bounded contexts / no canonical path | ai-context-upgrader | integrated | Declaration head `980df0356782d43cc0e571c4e2ca8f3ef1c1f0e0` failed truthfully; fixture-only head `412fa25a898fd45ea2ccb6360a2bfee795fe54d6` then passed fresh Sol High audit, five hosted checks, live admission capture/replay, and merged through PR #227 as `e27540bb34721a14d097316af8f5fd708b6982b2`. No #207 role is claimed. | root / merged exact admitted head and kept #206 open | `tasks/UPG-003-S2.json` |
| UPG-003-S3 | root plus generic Terra Max bounded release-artifact lane | ai-context-upgrader | in-progress | #207/#208 are integrated. The Phase-A scaffold is committed, and immutable builder failures at `803a0771ada510a9c5faf630a36a096d74117a64`, `7680190bf673c403ffbb970c75d397f91606872c`, and `a66f1901584cc2dba89065273e998bdc6f1b3c20` remain retained. A first synthetic portable-projection guard passed, but a real code-reviewer manifest probe exposed flat-mode parsing; the helper and fixture are corrected and await the immutable foundation commit plus Phase-B rebuild. No canonical-role invocation is claimed. | root owns workflow/validator integration; generic Terra Max owns only `.dev/releases/v0.14.0/**` and release index | `tasks/UPG-003-S3.json` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| Issue contract -> S1 implementation | approved | Explicit repository-owner v0.14.0 delivery prompt authorizes #206 S1/S2/S3 implementation, PR, audit, and merge. | none |
| Merged S1 -> S2 implementation | approved | Explicit repository-owner v0.14.0 delivery prompt and merged exact S1 admission. | none |

## Validation Strategy

- Requirement/spec traceability: Bind every S1 owner requirement to matrix fields, resolver outcomes, or a fail-closed GWT.
- Architecture validation: Keep resolution read-only and reuse, never duplicate, package/transaction/remediation authority.
- Test and implementation validation: Run focused deterministic route tests first, then isolated package projection and clean immutable hosted validation.
- Review/compliance gates: Fresh exact-head Sol High independent audit, required hosted checks, live merge admission, merge at admitted head, then #206 open/In-progress read-back.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root or isolated package fixture selected by repository tests.
- Target-owned commands: focused route resolver/schema/package tests plus repository-owned validation profiles.
- Prerequisites and environment boundary: Follow the existing ignored CLI routing binding only when a selected command crosses the sandbox boundary.
- Target policy: Preserve first failures/timeouts; long-running validation requires a clean immutable commit and one external task.
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: `release` only in S3 candidate proof.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | Focused S2 groups cover route/active context, exact checkpoint admission, decision/receipt gates, prepared-evidence tampering, interruption/recovery, active-hop rollback, and resolver-result/validator-asset binding. Final re-audit passed GWT003/GWT017/GWT032. | none |
| integration | passed | Real unmocked two-hop GWT010 passed within 120 seconds; isolated core-only package projection, wrapper metadata, shell-assets parity, and validation registry passed. Aggregate timeout/cancelled attempts remain non-passing evidence. | Immutable exact-head Sol High audit and hosted exact-head checks remain admission gates. |

## Spec Compliance Selection

- Selected: no
- Activation source: Live Issue #206 selects deterministic GWT and release gates, not a problem-frame compliance run.
- Outcome: `not-applicable`
- Coverage and evidence: Acceptance-traceable route fixtures and independent audit are the selected gates.

## Progress And Handoff

- Current stage: S3 remains active. Earlier immutable builder failures at `803a0771ada510a9c5faf630a36a096d74117a64`, `7680190bf673c403ffbb970c75d397f91606872c`, `a66f1901584cc2dba89065273e998bdc6f1b3c20`, and `2e6c5906882705e00b80f656c22c2925ed75c63a` remain retained. The sole canonical builder on immutable `b24da15f1948a9b17361fa49232c94485b4777e1` succeeded after rehashing exact v0.6.0, v0.9.0, and v0.13.0 historical inputs, producing ZIP sha256 `1445f0bf05e0f1e9a99700cbd70d23e6a021bc663a2f5ad10719018fe515ded9` and TAR.GZ sha256 `a0f2d0b26d19dfaab3014015344e01c6e48c675febfcddf64003b143970e1669`. The canonical package-native validator ran once and failed `selected-inputs migration proof diverges from migration.yaml`: migration.yaml uses semantic numeric v0.6.0, v0.9.0, v0.13.0 while selected-inputs.json used lexical v0.13.0, v0.6.0, v0.9.0. Parity was not established and no support-matrix or route files were created. The current uncommitted repair changes selected_input_document to semantic numeric version ordering and strengthens VersionedMigrationPackaging GWT013 with the v0.9.0/v0.13.0 crossover, selected/migration order assertions, and ZIP/TAR native validation. Its first focused run failed because SyntheticPackageRepo lacked target_owned_reference_patterns; that actionable fixture failure was repaired and the current GWT013 passes 1/1. This is mutable focused-test evidence only; no rebuilt package success is claimed.
- Post-change source-applicability evidence: The final precommit framework-source resolver resolved with `AICTX-EVIDENCE-001` and `TEST-GWT-001`; packet digest is `992a69bf3c0b37fe5d23df7e3158b86ca53e1935537de0f31426137cc9d6db50`, git-status digest is `280bb711d90b9f304e80f655b94a0d998b9810dad88b1bdef7488574f221e3bb`, and selection evidence is the `local-change-implementer` skill plus active `UPG-003-S3` task. The all-skill direct probe passed with 10 projected manifests and 7 byte-unchanged manifests; it remains helper evidence, not package or route proof. The initial PowerShell JSON display parse message was a display-tool misuse only, not a product, package, or validator failure.
- Terra precommit review evidence: The first review failed and remains retained because source-only `required_by_mode`/prose persisted in projected output and the profile `content_bytes` contract falsely claimed Git-blob bytes for transformed payload content. The repair removes that source-only projection residue and makes the real profile byte contract truthful. The current re-review passes: all 10 actual skills are target-only with no framework-source mode; code-reviewer source bytes are unchanged and idempotent; malformed source-mode evidence fails closed; both collection paths are covered; the actual profile byte contract, focused GWT, and scoped diff-check pass. This is not immutable builder success.
- Target-owned reference review evidence: Fresh read-only Terra review passed on diff fingerprint `b6eae2a746bbf0f6125d8eb6a480b08295a1742b7dcea3ca179413197f073909`. Only capability closure recognizes the exact target-owned list; Markdown navigation and actionable commands remain strict. The real current-profile/code-reviewer direct probe passed and unknown, source-only, navigation, and actionable missing references rejected. The dedicated positive GWT remains synthetic, and neither proof is package or route evidence. Final focused GWT, AI-context, workflow, source-governance, and diff gates pass.
- Completed stages: S1 route resolution through PR #226 and S2 multi-hop transaction through PR #227, each with exact-head independent audit, hosted admission, merge-at-admitted-head, and online #206/#222 read-back.
- Deferred stages and reasons: Long release-profile and cumulative pre-tag validation wait for a clean immutable S3 source-candidate commit; publication remains owner-only and unauthorized.
- Open decisions: None for S1; unavailable or ambiguous assets become reconciliation-required rather than inferred.
- Continuation instructions: Create the immutable portable-skill-projection foundation commit, execute the Phase-B package rebuild, and only then construct package-bound matrix and route evidence. Keep #206 open until the exact S3 terminal-close PR merges, then run post-merge provider read-back and cumulative v0.14 readiness from clean integrated main. Do not claim route-wide reversal of finalized hops.
- Target policy references: `.ai/assets/skills/ai-context-upgrader/skill.yaml`; `.dev/standards/WORKFLOW-GATE-POLICY.md`; `.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 starts from clean integrated main `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; Segment 2 starts from S1 merge `41a1b4bcc942b9a412d55a8dab77bcc5d7b6fbf2`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-upg-003-route-resolution-s1-admission` | `main@ead96acb0ac4ea73a94c6de59604b47f1f78b5ae` | active-stage | `2e468445ff876c78b4284e3548134dfdf37bb5b3` | draft PR #226 / PR S1 | `2026-08-20T19:45:54+08:00` | Declaration-head audit and hosted missing-validator failures are repaired at an exact committed head. | Obtain a fresh independent exact-head audit and fresh hosted admission, then merge S1 before branching S2 from integrated main. |
| 2 | `codex/2026-08-20-upg-003-multi-hop-upgrade-s2` | `main@41a1b4bcc942b9a412d55a8dab77bcc5d7b6fbf2` | integrated-stage | `412fa25a898fd45ea2ccb6360a2bfee795fe54d6` | merged PR #227 / deferred S2 | `2026-08-21T00:00:28+08:00` | Fixture-only repair passed fresh independent audit, five hosted checks, and live admission capture/replay; merge commit is `e27540bb34721a14d097316af8f5fd708b6982b2`. | Resume S3 after #207/#208 integrate. |
| 3 | `codex/2026-08-21-upg-003-v014-source-candidate-s3` | `main@bf8ad9c624ffc2154722dfb266c9090c72e4ac5f` | active-stage | pending | S3 terminal-close PR pending | `2026-08-21T03:12:02+08:00` | Instantiate the governed v0.14.0 source candidate and exact retained-origin route proof after #207/#208 integration. | Finish focused source proof, commit exact candidate, audit, hosted admission, and terminal-close #206. |

## Completion Summary

- Outcome: S1 and S2 are integrated. S3 is active from integrated #208 main and Issue #206 remains open until its governed v0.14.0 source-candidate PR passes terminal admission and merges.
- Changed artifacts: Multi-hop transaction runtime, child package/finalization composition, canonical transaction contract/schema/template, skill/profile and wrapper projection, validation runner wiring, focused transaction and package-projection GWTs, and this workflow evidence.
- Approved requirement/specification evidence: Live Issue #206 and explicit owner instructions.
- Implementation completion evidence: Resolver emits only four governed route kinds, cross-binds checksum sidecars, validator argv, canonical receipts, output bytes, and owner-approved deprecation evidence, and never accepts a target or invokes package apply. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` additionally cross-binds receipt from/to versions and ordered required cutover claims, rejects matrix duplicate keys, and uses retained canonical candidate authority bytes.
- Required test outcomes: Prior route 20/20, isolated package projection 1/1, validation registry 6/6, and shell-assets validation passed. The first full-module external attempt failed because its output capture was missing and remains failed evidence. The exact a57e484ba6456358971f86bcf3198acf04e6ac1e full-module task then failed after 156.213 seconds with GWT-014/GWT-020 fixture failures; it remains failed evidence and was not rerun unchanged. The repair committed at `14621d0c2f6bceb795d33d38f7ec86e2b607c354` passes route 24/24 in 0.895 seconds plus GWT-014 1/1 in 67.216 seconds and GWT-020 1/1 in 61.502 seconds on the normal Windows ACL boundary. For the current bounded CI repair, Bash syntax, shell-assets validation, and validation registry 7/7 in 0.525 seconds passed. Package projection first failed 1/1 in 2.855 seconds because its synthetic receipt lacked the current exact from/to/cutover fields; after materially changing only that fixture, the selector passed 1/1 in 2.971 seconds. No full package module or hosted job was rerun.
- Selected compliance evidence: Not applicable.
- Review disposition: Fresh exact-head independent audit passed at `26d5ccbcd063e28df7d3cfddeb2a715c6f193644` with zero findings. The read-only audit of `b87d0bd071696195976e77afd4fc59264f76aee5` failed only on stale workflow claims and made no repair. Commit `2e468445ff876c78b4284e3548134dfdf37bb5b3` requires fresh audit.
- Validation evidence: Base identity `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; framework-source packet `b244520f8cb7653c067e2fe13a2aeef62f9974f8f345b0cac2dee3c63159ff05`; live published v0.6-v0.13 identities; historical packages have no portable validator and v0.10-v0.11 remains deferred-with-owner. Fresh Sol High audits of `f6de771bb37a6224fb09543edf911f61aa7ab2bc` and `a57e484ba6456358971f86bcf3198acf04e6ac1e` failed without repair in their audit contexts. The audit of `635abaeb532a2383dfb03cc1d13bd50e41f7e80b` likewise made no repair and found: edge receipts could be matrix-relabelled because they omitted `from_version`, `to_version`, and required cutover claims; route-matrix YAML accepted duplicate keys; and GWT-014/GWT-020 used placeholder candidate authority digests. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` contains that focused repair; `26d5ccbcd063e28df7d3cfddeb2a715c6f193644` passed its exact-head audit. Declaration head `b87d0bd071696195976e77afd4fc59264f76aee5` failed audit only on stale workflow claims. At exact `b87d`, hosted governance job `96408142630` and Ubuntu PR job `96408142919` failed from the shared missing evidence-producing `upgrade-route-package-projection` execution; Build and validate candidate, Ubuntu prerequisite contract, and Windows prerequisite contract passed. No hosted job was rerun. Failed sandbox, fixture, and external-capture attempts remain recorded and are not promoted.
- Workflow task state: S2 completed; S3 in progress.
- Commits: `f6de771bb37a6224fb09543edf911f61aa7ab2bc`, `a57e484ba6456358971f86bcf3198acf04e6ac1e`, `71c4ec35ff180a70934333cdd296eb4b016050f8`, `ce0b4b6988030af1994edbbf37786fe7a7fbd952`, `635abaeb532a2383dfb03cc1d13bd50e41f7e80b`, `14621d0c2f6bceb795d33d38f7ec86e2b607c354`, `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`, `b87d0bd071696195976e77afd4fc59264f76aee5`, and `2e468445ff876c78b4284e3548134dfdf37bb5b3`.
- Branch / checkpoint / handoff evidence: S3 branch `codex/2026-08-21-upg-003-v014-source-candidate-s3` starts from exact #208 integration commit `bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`; framework-source packet `d01b6e5462fc645ada446a5edeef703059234713211fc6995e000da01d3cc700` resolved with `AICTX-EVIDENCE-001` and `TEST-GWT-001`.
- Residual risks: Historical origin routes remain unproven until the immutable foundation commit supplies exact package assets and planner evidence. The builder requires `automatic_upgrade_sources` to equal all three exact migration-source inputs; the candidate records v0.13.0, v0.9.0, and v0.6.0 accordingly. Candidate provider closure cannot be final until #206 terminal merge. Project-field restoration remains owned by another conversation.
- Current next gate: Preserve the retained builder and first fixture failures, commit the current semantic-order and fixture repair at an immutable head, rebuild using the exact retained historical inputs, and run the canonical package-native validator. Only a parity pass may lead to package-bound support-matrix and route evidence; do not treat GWT013 as rebuilt-package, parity, matrix, or route proof.
