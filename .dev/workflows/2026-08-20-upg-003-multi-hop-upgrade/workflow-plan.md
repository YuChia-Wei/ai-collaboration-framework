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
- `updated_at`: `2026-08-21T08:38:12+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-20-upg-003-multi-hop-upgrade/`

## Development Objective

- Product or software outcome: Preserve supported v0.6.0, v0.9.0, and immediate-predecessor upgrades behind one user operation while resolving exact routes before mutation.
- Current lifecycle entry point: Repair head `3a466b2133e8ef20d752f08d2e1b4b9df8869eed` is committed and pushed. Its exact 15-commit range from `bf8ad9c624ffc2154722dfb266c9090c72e4ac5f` passed commit policy. A sandbox candidate attempt was blocked only by proxy `127.0.0.1:9` during read-only Issue #200 GET; normal-network exact candidate validation then passed at clean pushed repair head `3a466`. The `fab9` candidate PASS and its fresh exact-head Sol audit FAIL/no receipt after live run `32431077702` / job `96622569129` remain historical evidence of the schema-2.2 v0.13 missing-field and merge-ref identity blockers. Compatibility is limited to absent field on archived schema 2.2.0; altered present/current/schema-2.3 missing cases fail closed. One job-level `CANDIDATE_COMMIT` binds checkout, renderer, validator, builder, source disposition, and artifact identity while `PR_BASE_SHA` and `PR_HEAD_SHA` remain changed-record discovery inputs. Payload 7/7, workflow-contract 10/10, retained archive, canonical package at `60572c01`, AST/YAML/diff, and the no-blocker four-file review pass. This evidence-only reconciliation will advance the head; the resulting clean evidence head still requires exact candidate revalidation, fresh Sol audit and receipt, then one hosted watch.
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
| UPG-003-S3 | root plus generic Terra Max bounded release-artifact lane | ai-context-upgrader | in-progress | #207/#208 are integrated and earlier immutable builder/package-native failures remain retained. Repair head `3a466` is committed/pushed; its 15-commit range from `bf8ad9` passed policy, sandbox candidate was blocked only by proxy on read-only Issue #200 GET, and normal-network exact candidate passed. Retain fab9 candidate PASS/audit FAIL-no-receipt and live run `32431077702` / job `96622569129` as historical blocker evidence. Compatibility remains limited to absent field on archived schema 2.2.0; altered present/current/schema-2.3 missing cases fail closed. `CANDIDATE_COMMIT` binds all candidate identity consumers while PR base/head remain discovery inputs. Payload 7/7, workflow-contract 10/10, retained archive, canonical v0.14 package, AST/YAML/diff, and raw-diff review `4ecaef44a9b0636588df882308a3ea784c80e5669daf5b68bf7614590b93e349` pass. The resulting clean evidence head requires revalidation, fresh audit/receipt, and one hosted watch. No hosted admission is claimed. | root owns workflow/validator integration; generic Terra Max owns only `.dev/releases/v0.14.0/**` and release index | `tasks/UPG-003-S3.json` |

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

- Current stage: S3 remains active. Earlier immutable builder failures at `803a0771ada510a9c5faf630a36a096d74117a64`, `7680190bf673c403ffbb970c75d397f91606872c`, `a66f1901584cc2dba89065273e998bdc6f1b3c20`, and `2e6c5906882705e00b80f656c22c2925ed75c63a` remain retained, as do the initial `b24da15f1948a9b17361fa49232c94485b4777e1` package-native parity failure and its focused fixture failure. At immutable foundation `60572c01e31abf58191d38adb5ca39e05338b08d` on `codex/2026-08-21-upg-003-v014-source-candidate-s3`, the canonical builder and package-native validator passed for `ai-context-dotnet-backend-v0.14.0`: ZIP sha256 `6f332f2a17549eb46109d1b2786cdefb32839eea18520cd65476c246d1337116` (1404420 bytes) and TAR.GZ sha256 `b08b18012f1db1cb8367f0e9bd378b6e079b6a31171d68d538fe77c1d363c35a` (992036 bytes), with `AI context package validation passed for 2 archive(s).` Exact historical `files.yaml` inputs are v0.6.0 `20ca69ef4e1b4085476a2b15eeba93da7a75ea580fd2ab9f6c8815938b0af3be`, v0.9.0 `c293247612eb2f01ef42e4d7c55be4ff36201cdf034157c518de871ec2acb5c7`, and v0.13.0 `850b74f5f23825f42912ac401a52692bc4cf02627fd9f8a452753f41611fbce4`.
- Committed source candidate: The planner-byte fix and the three receipt-bound direct-route proofs are committed at `ad1973304e7fd2f170434c1fb5c77ff20c229fae`, distinct from immutable package foundation `60572c01e31abf58191d38adb5ca39e05338b08d`. A precommit independent audit passed on dirty diff fingerprint `ef764808542c2a4e7ff0295d0dd05ec18e8ac1815d1711d107a16a873aac5e2a`. The exact-head Sol High audit of `ad1973304e7fd2f170434c1fb5c77ff20c229fae` terminally failed only because current workflow and release narrative records were stale; the repair is in draft/open PR #232 initial head `aaae7aaf9f64be49574f9b35a6ca7e011bf9d593`.
- PR declaration state: PR #232 remains draft/open/unmerged against `main@bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`; #206 remains open terminal-close and #222 deferred. Repair head `3a466` is committed/pushed; its 15-commit range passed commit policy, sandbox candidate was proxy-blocked only at read-only Issue #200 GET, and normal-network exact candidate passed. The `fab9` candidate PASS and audit FAIL/no receipt after run `32431077702` / job `96622569129` remain historical. This evidence-only reconciliation will advance the head; candidate revalidation, fresh audit/receipt, hosted admission, merge admission, and provider reconciliation remain pending for the resulting clean evidence head.
- Canonical direct route evidence is now v0.13.0 `ef7b9683f830b65089c3ab828e759270a02db33a7f21df080c8d01dff259da4e` (2292 bytes; receipt `ff278808c9470ccb143cd9f7af8ec5ac1c797b720d1c744a4873ed2a34d48401`), v0.9.0 `04f651c16ea79d10e454f180649eb066762201b70bcbf30d4552652c25606b1b` (2281 bytes; receipt `8a957f7e0163ed14b52c65a06abe7ac18a88b60c5b12d1868203050652539e24`), and v0.6.0 `28f989d984e85276a1eb8c7e6c20420a7a651e28c043db9c7556613c5ffee725` (2281 bytes; receipt `d6a078fb308730de12dd26695a1fea4f6602feb5bdbe1e1846960c090a446e41`). Each is canonical UTF-8 with one LF/no CR, `route_kind: direct`, and zero diagnostics.
- Retained route history: the first v0.6.0 validator rejected `target files manifest.files uses unsupported YAML structure` from a numeric-sha256 parser defect; after the `[a-z0-9_]` repair, v0.6.0 rerun and v0.9.0/v0.13.0 first runs passed. Initial receipts had double LF and planners reported reconciliation-required/not-canonical until canonical receipt repair. The next semantically direct planner output used CRLF, so the candidate validator rejected its bytes. The subsequent `plan-ai-context-upgrade.py` fix uses `sys.stdout.buffer`/`sys.stderr.buffer`, passed normal ACL raw-byte GWTs 2/2 in 0.355 seconds after a sandbox WinError 5 block, and is committed at `ad1973304e7fd2f170434c1fb5c77ff20c229fae`.
- Post-change source-applicability evidence: The final precommit framework-source resolver resolved with `AICTX-EVIDENCE-001` and `TEST-GWT-001`; packet digest is `992a69bf3c0b37fe5d23df7e3158b86ca53e1935537de0f31426137cc9d6db50`, git-status digest is `280bb711d90b9f304e80f655b94a0d998b9810dad88b1bdef7488574f221e3bb`, and selection evidence is the `local-change-implementer` skill plus active `UPG-003-S3` task. The all-skill direct probe passed with 10 projected manifests and 7 byte-unchanged manifests; it remains helper evidence, not package or route proof. The initial PowerShell JSON display parse message was a display-tool misuse only, not a product, package, or validator failure.
- Terra precommit review evidence: The first review failed and remains retained because source-only `required_by_mode`/prose persisted in projected output and the profile `content_bytes` contract falsely claimed Git-blob bytes for transformed payload content. The repair removes that source-only projection residue and makes the real profile byte contract truthful. The precommit re-review passed: all 10 actual skills are target-only with no framework-source mode; code-reviewer source bytes are unchanged and idempotent; malformed source-mode evidence fails closed; both collection paths are covered; the actual profile byte contract, focused GWT, and scoped diff-check pass. This is not immutable builder success.
- Target-owned reference review evidence: Fresh read-only Terra review passed on diff fingerprint `b6eae2a746bbf0f6125d8eb6a480b08295a1742b7dcea3ca179413197f073909`. Only capability closure recognizes the exact target-owned list; Markdown navigation and actionable commands remain strict. The real current-profile/code-reviewer direct probe passed and unknown, source-only, navigation, and actionable missing references rejected. The dedicated positive GWT remains synthetic, and neither proof is package or route evidence. Final focused GWT, AI-context, workflow, source-governance, and diff gates pass.
- Completed stages: S1 route resolution through PR #226 and S2 multi-hop transaction through PR #227, each with exact-head independent audit, hosted admission, merge-at-admitted-head, and online #206/#222 read-back.
- Deferred stages and reasons: Long release-profile and cumulative pre-tag validation await candidate revalidation, Sol audit/receipt, hosted admission, and merge of draft/open PR #232 at the resulting clean evidence head. Repair head `3a466` is committed/pushed and candidate-passed; fab9 blocker evidence remains historical. Publication remains owner-only and unauthorized.
- Open decisions: None for S1; unavailable or ambiguous assets become reconciliation-required rather than inferred.
- Continuation instructions: This evidence-only reconciliation will advance the head. Run `python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version v0.14.0` on the resulting clean evidence head, obtain a fresh Sol audit and receipt, then perform one hosted watch. Keep #206 open until the admitted head merges, defer #222, then run post-merge provider read-back and cumulative v0.14 readiness from clean integrated main. Do not claim hosted admission, merge, Issue closure, provider closure, or route-wide reversal before its own evidence exists.
- Target policy references: `.ai/assets/skills/ai-context-upgrader/skill.yaml`; `.dev/standards/WORKFLOW-GATE-POLICY.md`; `.dev/standards/GITHUB-TERMINAL-ISSUE-CLOSURE-POLICY.md`.
- Registered handoff checkpoint: none.
- Branch history and checkpoint handoffs: Segment 1 starts from clean integrated main `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; Segment 2 starts from S1 merge `41a1b4bcc942b9a412d55a8dab77bcc5d7b6fbf2`.

### Current S3 Correction State

- This current-state section supersedes earlier S3 next-gate and hosted-snapshot wording in this plan; that wording remains retained historical evidence.
- Repair head `3a466b2133e8ef20d752f08d2e1b4b9df8869eed` is committed and pushed. Its exact 15-commit range from `bf8ad9c624ffc2154722dfb266c9090c72e4ac5f` passed commit policy. Sandbox candidate validation was blocked only by proxy `127.0.0.1:9` during read-only Issue #200 GET; normal-network exact candidate validation passed at clean pushed repair head `3a466`.
- The fab9 candidate PASS and exact-head audit FAIL/no receipt after live run `32431077702` / job `96622569129` remain historical evidence of the two original blockers. Compatibility infers the exact canonical list only when archived schema 2.2.0 has the field absent; altered present values, current packages, and schema 2.3 packages with the field absent remain fail-closed. The retained v0.13 archive and canonical v0.14 package at `60572c01` pass.
- One job-level `CANDIDATE_COMMIT` selects PR head or dispatch SHA and binds checkout, renderer, validator, builder, source disposition, and artifact identity. `PR_BASE_SHA` and `PR_HEAD_SHA` remain distinct changed-record discovery inputs. Current-byte payload 7/7, workflow-contract 10/10, AST/YAML/diff, and independent read-only review of four-file raw binary Git diff SHA-256 `4ecaef44a9b0636588df882308a3ea784c80e5669daf5b68bf7614590b93e349` passed with no blockers. The first PR_HEAD_SHA-only review failure and historical renderer/schema and payload fixture findings remain retained.
- S3 remains in progress. PR #232 is draft/open/unmerged; #206 is open terminal-close; #222 is deferred. This evidence-only reconciliation will advance the head; the resulting clean evidence head requires exact candidate revalidation, fresh Sol audit with receipt, then one hosted watch. No hosted admission, merge, Issue closure, provider closure, tag, GitHub Release, or publication is claimed.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-20-upg-003-route-resolution-s1-admission` | `main@ead96acb0ac4ea73a94c6de59604b47f1f78b5ae` | active-stage | `2e468445ff876c78b4284e3548134dfdf37bb5b3` | draft PR #226 / PR S1 | `2026-08-20T19:45:54+08:00` | Declaration-head audit and hosted missing-validator failures are repaired at an exact committed head. | Obtain a fresh independent exact-head audit and fresh hosted admission, then merge S1 before branching S2 from integrated main. |
| 2 | `codex/2026-08-20-upg-003-multi-hop-upgrade-s2` | `main@41a1b4bcc942b9a412d55a8dab77bcc5d7b6fbf2` | integrated-stage | `412fa25a898fd45ea2ccb6360a2bfee795fe54d6` | merged PR #227 / deferred S2 | `2026-08-21T00:00:28+08:00` | Fixture-only repair passed fresh independent audit, five hosted checks, and live admission capture/replay; merge commit is `e27540bb34721a14d097316af8f5fd708b6982b2`. | Resume S3 after #207/#208 integrate. |
| 3 | `codex/2026-08-21-upg-003-v014-source-candidate-s3` | `main@bf8ad9c624ffc2154722dfb266c9090c72e4ac5f` | evidence-reconciliation-pending-resulting-head-gates | `60572c01e31abf58191d38adb5ca39e05338b08d` package foundation; `ad1973304e7fd2f170434c1fb5c77ff20c229fae` source candidate; `ea0414edf1260f0a317ee4b406b9eafb29d7f859` validator fix; `66ec`/`b4b38` retained history; `fab9` candidate/audit history; repair head `3a466b2133e8ef20d752f08d2e1b4b9df8869eed` | draft/open PR #232 | `2026-08-21T08:38:12+08:00` | Repair head 3a466 is committed/pushed; 15-commit policy and normal-network candidate passed, while sandbox candidate was proxy-blocked only. Payload/workflow/archive/package/AST-YAML-diff/review evidence remains passed. | Resulting clean evidence head: exact candidate revalidation, fresh Sol audit/receipt, then one hosted watch. Keep #206 open and #222 deferred. |

## Completion Summary

- Outcome: S1 and S2 are integrated. S3 remains in progress from integrated #208 main with immutable package/validator evidence at `60572c01e31abf58191d38adb5ca39e05338b08d`, the planner-byte plus three direct-route proof bundle at `ad1973304e7fd2f170434c1fb5c77ff20c229fae`, validator fix at `ea0414edf1260f0a317ee4b406b9eafb29d7f859`, and retained `66ec`/`b4b38` observations. Repair head `3a466` is committed/pushed; its 15-commit range passed policy and normal-network candidate passed after sandbox proxy block. Fab9 candidate/audit blocker evidence remains historical. This evidence-only reconciliation will advance the head; the resulting clean evidence head still requires revalidation, fresh audit/receipt, and hosted watch. PR #232 remains draft/open/unmerged, #206 open terminal-close, and #222 deferred. No hosted admission, merge, Issue closure, or provider closure exists.
- Changed artifacts: Multi-hop transaction runtime, child package/finalization composition, canonical transaction contract/schema/template, skill/profile and wrapper projection, validation runner wiring, focused transaction and package-projection GWTs, and this workflow evidence.
- Approved requirement/specification evidence: Live Issue #206 and explicit owner instructions.
- Implementation completion evidence: Resolver emits only four governed route kinds, cross-binds checksum sidecars, validator argv, canonical receipts, output bytes, and owner-approved deprecation evidence, and never accepts a target or invokes package apply. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` additionally cross-binds receipt from/to versions and ordered required cutover claims, rejects matrix duplicate keys, and uses retained canonical candidate authority bytes.
- Required test outcomes: Prior route 20/20, isolated package projection 1/1, validation registry 6/6, and shell-assets validation passed. The first full-module external attempt failed because its output capture was missing and remains failed evidence. The exact a57e484ba6456358971f86bcf3198acf04e6ac1e full-module task then failed after 156.213 seconds with GWT-014/GWT-020 fixture failures; it remains failed evidence and was not rerun unchanged. The repair committed at `14621d0c2f6bceb795d33d38f7ec86e2b607c354` passes route 24/24 in 0.895 seconds plus GWT-014 1/1 in 67.216 seconds and GWT-020 1/1 in 61.502 seconds on the normal Windows ACL boundary. For the bounded validator repair, Bash syntax, shell-assets validation, and validation registry 7/7 in 0.525 seconds passed. Package projection first failed 1/1 in 2.855 seconds because its synthetic receipt lacked the current exact from/to/cutover fields; after materially changing only that fixture, the selector passed 1/1 in 2.971 seconds. GWT033's first sandbox run was blocked before logic by Temp `WinError 5`; normal-ACL focused GWT033 and the full release-state module 36/36 passed. At clean `ea0414` the exact candidate release-state gate passed. No hosted job was rerun; the single live snapshot records one completed FAILURE, two IN_PROGRESS checks, and two SUCCESS prerequisites as observations, not results or admission.
- Retained historical test boundary: The preceding `ea0414` no-rerun and IN_PROGRESS snapshot, together with the `60e689` candidate/audit pass and later hosted renderer/payload failure analysis, is historical only. At clean `66ec`, candidate gate passed and audit failed solely on stale active narratives. Renderer 20/20, payload 6/6, direct renderer CLI, AST/scoped diff, and independent precommit review remain retained prior-repair evidence.
- Current S3 proof: The `60572c01e31abf58191d38adb5ca39e05338b08d` immutable builder plus package-native validator passed for both archives; the planner raw-byte first sandbox GWT remains blocked before assertions and normal ACL passed 2/2 in 0.355 seconds. Repair head `3a466` is committed/pushed; its range policy and normal-network candidate gates passed, while sandbox candidate was blocked only by proxy at read-only Issue #200 GET. Fab9 audit blocker evidence remains historical. Compatibility remains archived-schema-2.2 absent-field only, with all other missing/altered cases fail-closed; job-level `CANDIDATE_COMMIT` binds candidate identity consumers. Current-byte payload 7/7, workflow-contract 10/10, retained v0.13 archive, canonical v0.14 package, AST/YAML/diff, and raw diff review `4ecaef44a9b0636588df882308a3ea784c80e5669daf5b68bf7614590b93e349` passed. The resulting clean evidence head requires candidate revalidation, audit/receipt, hosted admission, merge, Issue closure, and provider closure evidence.
- Historical framework-source resolver evidence bound dirty precommit bytes at HEAD `60572c01e31abf58191d38adb5ca39e05338b08d`: resolved rules `AICTX-EVIDENCE-001` and `TEST-GWT-001`; selection evidence `.ai/assets/skills/local-change-implementer/skill.yaml` plus active `UPG-003-S3` task; packet digest `38d24ac505fcc8c37cadab05467401fd7d23f9e6b59e70810b87e19b98b1d7bf`; git-status digest `c7ccd8c9b69b94bae11cd2eb9203d05e83ed38d42daaebef62e3c91525c1e813`; freshness was verified. This is not candidate admission.
- Historical framework-source rule resolution at clean `0a9a25784d6fd3ba2429fb19bd04b45fac327029` resolved `AICTX-EVIDENCE-001` and `TEST-GWT-001` with packet digest `2b95be6d8338103d49eaade3bca08a361074ff698f547d6573f29e6f57a91d68`. The earlier attempted `python` technology route failed; the corrected exact route was `dotnet-backend/python`. This is not candidate admission.
- Selected compliance evidence: Not applicable.
- Review disposition: Fresh exact-head independent audit passed at `26d5ccbcd063e28df7d3cfddeb2a715c6f193644` with zero findings. The read-only audit of `b87d0bd071696195976e77afd4fc59264f76aee5` failed only on stale workflow claims and made no repair. Precommit independent audit passed on dirty diff fingerprint `ef764808542c2a4e7ff0295d0dd05ec18e8ac1815d1711d107a16a873aac5e2a`; the exact-head Sol High audit of `ad1973304e7fd2f170434c1fb5c77ff20c229fae` terminally failed only because active narrative records were stale, repaired in initial PR #232 head `aaae7aaf9f64be49574f9b35a6ca7e011bf9d593`. For the validator fix, the first independent precommit review failed on wrong-contract fail-open and a malformed deferred fixture; after repair, re-review passed with manifest `4fbdc164c2b7e811dfb7316bfe4eb879809167a78651f3c11506dcb9f848382e` and diff `4e37d38e9bcf02ae9fae3b3ffeade5f5c85fdf58bda834866738fdf107e9e787`. Fresh Sol High audit of `ea0414edf1260f0a317ee4b406b9eafb29d7f859` terminally failed with exactly one blocking finding: active narratives still described the prior `0a9a` state, the pre-commit repair state, and commit/push as next work. It otherwise passed release-state 36/36, route 25/25, terminal/workflow/AI-context/source-governance/version-registry/commit-policy/AST-YAML-JSON-diff checks, and package plus three route cross-bindings, and made no repair. No hosted admission is inferred.
- Current review boundary: The preceding `ea0414` audit failure and `60e689` audit pass are retained historical evidence. The fab9 exact-head Sol audit failure/no receipt after live job `96622569129` remains historical. Repair head `3a466` is committed/pushed, but no fresh audit receipt exists for the resulting clean evidence head. The independent read-only raw-diff review `4ecaef44a9b0636588df882308a3ea784c80e5669daf5b68bf7614590b93e349` is not a replacement for that required fresh Sol audit.
- Current S3 admission state: Historical `0a9a` candidate failure, `ea0414` discovery-fix gate pass, `ea0414` stale-narrative audit failure, the first GWT033 Temp `WinError 5` block, the `60e689` hosted renderer/payload findings, and fab9 candidate/audit blocker evidence remain retained. Repair head `3a466` passed policy and normal-network candidate validation after sandbox proxy block. This evidence-only reconciliation will advance the head; exact revalidation, fresh Sol audit/receipt, and one hosted watch remain required for the resulting clean evidence head. No hosted admission, merge, Issue closure, or post-merge provider read-back exists.
- Validation evidence: Base identity `ead96acb0ac4ea73a94c6de59604b47f1f78b5ae`; framework-source packet `b244520f8cb7653c067e2fe13a2aeef62f9974f8f345b0cac2dee3c63159ff05`; live published v0.6-v0.13 identities; historical packages have no portable validator and v0.10-v0.11 remains deferred-with-owner. Fresh Sol High audits of `f6de771bb37a6224fb09543edf911f61aa7ab2bc` and `a57e484ba6456358971f86bcf3198acf04e6ac1e` failed without repair in their audit contexts. The audit of `635abaeb532a2383dfb03cc1d13bd50e41f7e80b` likewise made no repair and found: edge receipts could be matrix-relabelled because they omitted `from_version`, `to_version`, and required cutover claims; route-matrix YAML accepted duplicate keys; and GWT-014/GWT-020 used placeholder candidate authority digests. Commit `14621d0c2f6bceb795d33d38f7ec86e2b607c354` contains that focused repair; `26d5ccbcd063e28df7d3cfddeb2a715c6f193644` passed its exact-head audit. Declaration head `b87d0bd071696195976e77afd4fc59264f76aee5` failed audit only on stale workflow claims. At exact `b87d`, hosted governance job `96408142630` and Ubuntu PR job `96408142919` failed from the shared missing evidence-producing `upgrade-route-package-projection` execution; Build and validate candidate, Ubuntu prerequisite contract, and Windows prerequisite contract passed. At the later single live `ea0414` snapshot, Build and validate candidate completed FAILURE, Read-only governance and Ubuntu PR profile were IN_PROGRESS, and Ubuntu and Windows prerequisites were SUCCESS; no logs were fetched and no hosted admission is inferred. No hosted job was rerun. Failed sandbox, fixture, and external-capture attempts remain recorded and are not promoted.
- Current hosted-evidence boundary: The preceding `ea0414` no-log/no-rerun sentence, the `60e689` completed hosted watch, clean `66ec` checks, and fab9 live candidate failure are retained historical snapshots. Repair head `3a466` normal-network candidate PASS is not hosted admission. No hosted watch has run for the resulting clean evidence head.
- Workflow task state: S2 completed; S3 in progress.
- Commits: `f6de771bb37a6224fb09543edf911f61aa7ab2bc`, `a57e484ba6456358971f86bcf3198acf04e6ac1e`, `71c4ec35ff180a70934333cdd296eb4b016050f8`, `ce0b4b6988030af1994edbbf37786fe7a7fbd952`, `635abaeb532a2383dfb03cc1d13bd50e41f7e80b`, `14621d0c2f6bceb795d33d38f7ec86e2b607c354`, `26d5ccbcd063e28df7d3cfddeb2a715c6f193644`, `b87d0bd071696195976e77afd4fc59264f76aee5`, `2e468445ff876c78b4284e3548134dfdf37bb5b3`, source candidate `ad1973304e7fd2f170434c1fb5c77ff20c229fae`, validator fix `ea0414edf1260f0a317ee4b406b9eafb29d7f859`, candidate/audit head `66ec616b4d2c5e42129ae1a09557039d15ddb7df`, placeholder-attempt head `b4b38b136d69a1d3e3938598edcb4c6d7285b795`, historical candidate/audit head `fab9cf6787f0d4fad9384c29a6e0f514389667ba`, and repair head `3a466b2133e8ef20d752f08d2e1b4b9df8869eed`.
- Branch / checkpoint / handoff evidence: S3 branch `codex/2026-08-21-upg-003-v014-source-candidate-s3` starts from exact #208 integration commit `bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`; framework-source packet `d01b6e5462fc645ada446a5edeef703059234713211fc6995e000da01d3cc700` resolved with `AICTX-EVIDENCE-001` and `TEST-GWT-001`.
- Residual risks: Historical direct routes are proven in committed source candidate `ad197`, but candidate release-state is not admitted until #206 is closed with completed reason or is the exact open terminal-close Issue of the current source-candidate PR. The builder still requires `automatic_upgrade_sources` to equal all three exact migration-source inputs. Candidate provider closure cannot be final until #206 terminal merge; #222 and Project-field restoration remain outside this task.
- Current next gate: This evidence-only reconciliation advances the head. Run exact clean candidate release-state validation on the resulting clean evidence head, obtain a fresh Sol audit and receipt, then perform one hosted watch. Retain all historical failures, including the `ea0414` stale-narrative audit and its no-log hosted snapshot. Do not claim hosted admission, merge, Issue closure, provider closure, or post-merge read-back until independently evidenced.
