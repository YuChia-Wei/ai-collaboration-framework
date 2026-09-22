# Issue 319 artifact lifecycle independent audit

## Executive Summary

Outcome: `failed`. Parent action: `reroute` for a tracked repair and fresh affected validation before any integration decision.

One high-severity finding prevents acceptance of this fixed subject. The implementation registers `artifact-catalog-tests` as a required check in every validation profile, but the canonical gate-classification authority does not classify it. The lifecycle validator requires the classification set to exactly equal the validation registry and loads that authority unconditionally. Consequently, the required `validation-lifecycle-contract` check fails closed for `fast`, `pr`, `release`, and `nightly-full`, and subject-manifest construction cannot classify the new gate.

The finding is bound to content subject `3828e045a0cbb7b17318926569a01feefa54f08aaa00ed4b0ed48b70139e7751`, canonical review input SHA-256 `5c95a64f971c3a703692a8655781556e56958e09b4226a4f399ef435621bf4f8`, execution commit `b29f3ae9c079b05ab144ba0eddd10294e452988a`, and tree `15add83f4202ba5d2a74fff669e31bf6281b53ce`. The base is commit `4cc41d3b57b591895a528d6ae4dd5745b8877cf5`, tree `7a9ae326048f3caa17fc6f0f214a8b061bec3a84`.

The exact dispatched package-smoke command ran once at the authorized elevated Windows fixture boundary. It passed 1 of 1 test with exit code 0, no failures, errors, skips, timeout, or launch error. Its declared disposable fixture root was empty after execution. The command result does not cover the classification authority defect.

No repair, tracked mutation, provider action, credential use, network action, lease release, or additional behavioral test execution occurred. This audit does not grant final integration acceptance and does not claim workflow, Issue, Project, release, publication, hosted CI, or downstream-adoption completion. Root remains the integration owner.

## Scope and Method

Included:

- The Git diff from the fixed base to the fixed clean head, with the six criteria and authority manifest from the validated machine review input.
- The 91-kind lifecycle registry, its authoring and migration dispositions, the selected catalog/skill/target/lifecycle operations, recovery and wrapper behavior, P4 validation-scope change, validation-profile dependency closure, package inclusion, retained p34 evidence, and the current Traditional Chinese remediation report.
- One exact-head execution of `python -B .ai/scripts/tests/test_ai_context_package_smoke.py -v`.

Excluded:

- Repair, provider or credential mutation, other test matrices, final integration acceptance, remote operations, release, publication, and target adoption.
- Product source and product tests. The selected `.ai` framework implementation and tests are explicitly within this review.

The current code graph excludes `.ai/scripts` and `.ai/assets`. In accordance with the task envelope, discovery used the explicit tracked diff and targeted Git-tracked file reads. No absence conclusion relies on graph search alone.

## Finding

### F-001 — High — Required catalog gate has no sensitivity classification

The change adds `artifact-catalog-tests` as a `required` check for all four profiles in `.ai/scripts/validation-profile-registry.sh:389-393`. The complete `.ai/assets/shared/validation-gate-classification.yaml` authority contains `artifact-authoring-tests` at line 43 but contains no `artifact-catalog-tests` entry.

This is a required one-to-one authority relationship:

- `.ai/scripts/validation_subject.py:284-370` loads the registry and classification authority and raises `SubjectError("gate classification does not exactly cover the validation registry")` whenever their gate-ID sets differ.
- `.ai/scripts/validate-validation-lifecycle.py:442-445` invokes that loader unconditionally before validating any lifecycle record.
- `.ai/scripts/validation-profile-registry.sh:358-362` registers that validator as the required `validation-lifecycle-contract` check in `fast`, `pr`, `release`, and `nightly-full`.
- `.ai/scripts/validation_subject.py:390-402` and `:608-620` also require the same authority before building a gate subject manifest.
- `.ai/scripts/tests/test_validation_subject_digest.py:381-385` owns an exact registry/classification coverage assertion, but none of the retained focused commands or the single authorized package smoke executed that file at the fixed head.

Impact: every declared profile contains a required contract check that deterministically rejects the current registry/classification pair. The new gate also cannot receive a sensitivity, reuse-eligibility, reusable-profile, or environment-contract binding, so evidence subject construction for it fails closed. This violates AC5's required-gate and profile-closure requirement and blocks integration of the current content subject.

Required repair: add `artifact-catalog-tests` to the appropriate classification group with its intended sensitivity/reuse/environment policy, retain exact registry/classification coverage, and run the affected lifecycle/profile validation on the repaired clean subject. Because that is a tracked authority change, it creates a new content subject and requires fresh admission and affected review disposition under the parent workflow. This auditor did not choose the policy group or modify the authority.

No other material findings were identified within the bounded criteria.

## Independent Baseline Pass

Apart from F-001, the implementation establishes a coherent bounded lifecycle model:

- The registry contains 91 record kinds: 52 `executable`, 18 `semantic-owner`, 16 `manual-gap`, 4 `external`, and 1 `creation-template`. It explicitly binds the 33 named schema sources and I01-I19 implicit-contract sources. Callable presence is treated as route existence rather than proof of semantic completeness.
- Executable routes require an explicit Python callable and top-level declaration. Non-executable routes cannot claim producers. Model and owner paths are bound to tracked bytes, and baseline/coverage lists are exact rather than open-ended.
- The only conversion routes are dynamic role metadata `1.0 -> 1.1` and external dispatch/completion `1.2 -> 1.3`. Receipt, approval, provider, journal-recovery, historical assessment, and target facts remain preserve/re-execute/regenerate/unsupported/owner-controlled dispositions rather than fabricated conversions.
- Catalog, skill, target, and lifecycle operations use fixed family authorities and field policies. Candidate validation observes selected schemas, owner/runtime inputs, directory membership, wrappers where applicable, and Git source identity before apply.
- Literal `ViewPath` traversal validates each path component and avoids treating a fixed directory as a broad glob. Symlink, reparse/junction, hard-link, traversal, device-name, and special-file boundaries fail before writes.
- Apply re-derives the plan and checks the committed source head/tree plus the candidate overlay. Recovery retains exact prior bytes, refuses external candidate edits, and does not claim multi-file atomicity.
- Skill edits preserve ordinary thin-wrapper bytes; the two existing generated pilots re-project both runtime wrappers from final canonical bytes. Lifecycle changes protect kind, baseline, coverage, model, and owner identity.
- Target selections validate the relevant schemas and existing records, reject booleans as integer schema versions, preserve target extensions, and observe decision-reference bytes without inferring approval.
- Source route registration is not presented as a universal writer. The 18 semantic-owner, 16 manual-gap, 4 external, and 1 creation-template records retain their distinct limits.

## Repository-Aware Policy Pass

The repository-aware pass confirms the bounded behavior and identifies the gate defect:

- The owning `ai-context-auditor` skill explicitly selects the fixed-head independent auditor. Review-input, packet, dispatch, and active read-only shared-frozen lease preflights passed before behavior. The observed head/tree and tracked status matched the fixed subject before and after the command.
- P4 changes only the linked workflow/assessment full-directory calls for disjoint authoring families. Public validators, CLI routes, and existing tests remain in source; workflow and assessment families retain their linked checks. F-001 concerns a newly registered gate's missing classification authority, not the intended authoring-scope relaxation itself.
- The portable profile rows require mandatory sources and treat the .NET profile as optional only while its directory is absent. If that profile directory appears, missing profile sources fail. The exact package-smoke command verifies archive bytes, member metadata, and inclusion of the lifecycle helper/registry, not downstream adoption.
- The remediation report accurately limits the route catalog, preserves manual gaps and the historical failed attempt, distinguishes overlapping executions, leaves fixed-head smoke and independent review pending at the audited commit, and does not claim hosted, provider, release, performance, token, or adoption results. Its statement that required gates remain refers to source retention; F-001 shows the resulting gate authority is not operationally complete.

## Retained Evidence and Reuse Boundaries

All inspected p34 JSON records retain log SHA-256 values matching their corresponding log bytes and record `input_drift: []` for their own execution-time manifests. Their reuse is narrower than that fact:

| Evidence | Audit disposition | Boundary |
| --- | --- | --- |
| `extended-01` | `blocked` historical attempt | 10 cases produced 9 passes and 1 error. It remains failure evidence for the overly broad recovery-directory observation and is not relabeled after the later fix. |
| `catalog-03` | `reused-with-proof` for its historical 21-case result only | Passed with exit 0. Five recorded inputs differ at the fixed head, so it is not an exact-current-input proof of the whole catalog surface. |
| `routing-01` | `reused-with-proof` for the final seven-case affected subset | The recorded tracked inputs match the current bytes. Six cases overlap the 21-case execution; it is not a single 22-case run. |
| `authoring-02` | `reused-with-proof` as prior 36-case support | Passed with exit 0; five recorded inputs differ at the fixed head, so it is not whole-subject final-head evidence. |
| `contracts-01` | `reused-with-proof` as prior 11-case profile-registry support | Passed with exit 0; five recorded inputs differ at the fixed head. It does not establish classification-authority parity. |
| `evaluation-01` | `reused-with-proof` for its 18-case evaluation scope | Recorded tracked inputs match current bytes; it does not exercise F-001. |
| `shell-01` | `reused-with-proof` for 16 tracked shell assets | Recorded tracked inputs match current bytes; it does not execute the lifecycle authority validator. |
| `canonical-02` | `reused-with-proof` for the canonical context validator it ran | Recorded tracked inputs match current bytes. The canonical validator's 39-manifest/91-route checks do not replace registry/classification parity. |
| fixed-head package smoke | `re-executed` | Passed 1/1 at the exact subject; it covers packaging and helper inclusion only. |
| hosted/provider checks | `not-applicable` | The bounded task authorizes no hosted or provider operation. |

The `catalog-03`, `authoring-02`, and `contracts-01` receipts each predate five fixed-head input changes: the lifecycle registry, lifecycle helper, package-smoke test, packaging test, and catalog test. Their retained outputs remain truthful historical evidence, while current-content conclusions use static review plus the final seven-case subset where applicable. No prior pass is used to override F-001.

## Exact Command Observation

Command: `python -B .ai/scripts/tests/test_ai_context_package_smoke.py -v`

- Dispatch count: exactly one.
- Boundary: authorized elevated Windows fixture execution.
- Outcome: command `passed`; exit code `0`.
- Test result: 1 run, 1 successful, 0 failures, 0 errors, 0 skipped.
- Test-reported duration: 3.490 seconds.
- Tool-observed wall duration: 5.3874171 seconds.
- Timeout/launch error: none.
- Cleanup: `.tmp/p` existed and contained zero children after execution.
- Output custody: `execution.log` retains the combined output exposed by the execution tool. The tool did not expose separate stdout/stderr channels.
- Timestamp limit: the runtime did not expose native process event timestamps. The command observation records a bounded wall-time proxy derived from the post-cleanup `.tmp/p` last-write timestamp and the tool-observed elapsed duration; it does not relabel those values as native process start/finish events.

## Criteria Disposition

| Criterion | Disposition | Evidence |
| --- | --- | --- |
| AC1 | `reused-with-proof` plus static review | The exact 91-kind inventory, E01-E33/I01-I19 coverage, five authoring categories, and explicit manual/external/template limits match the criterion. |
| AC2 | `reused-with-proof` plus static review | Family field policies, fixed paths, candidate validation inputs, Git binding, ViewPath safety, wrapper projection, apply re-derivation, and recovery boundaries are present. |
| AC3 | `reused-with-proof` plus static review | Exactly three conversion records implement only the allowed version edges; no receipt, approval, provider, journal, target, or historical result is fabricated. |
| AC4 | `re-executed` with retained prior evidence | The fixed-head smoke passed once; cleanup succeeded. Original p34 evidence keeps the 9-pass/1-error attempt, later fix, overlapping 21/7-case runs, and each command's actual identity. |
| AC5 | `failed` | F-001 breaks exact registry/classification coverage and therefore the required lifecycle contract in every profile. The P4 authoring-scope relaxation itself remains bounded. |
| AC6 | `reused-with-proof` plus static review | The Chinese report explains scope, limitations, gaps, measured runs, and local-only integration authority without inventing hosted/provider/performance results. Its pending-review state remains truthful. |

## Parent Action

`reroute`: return F-001 to the implementation owner. After the owner supplies the missing gate classification and validates the affected lifecycle/profile path on a new clean content subject, the parent should re-admit that subject and determine the required fresh/reused review scope. The current audit remains retained evidence for commit provenance and unaffected observations; it is not acceptance of the repaired subject.
