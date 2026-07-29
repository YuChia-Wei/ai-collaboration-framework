# v0.7.0 Public Release Body Correction Remediation Report

## Template Metadata

- template_id: ai-context-governance-remediation-report
- template_version: 2.0.0
- created_at: 2026-07-10T18:22:49+08:00
- updated_at: 2026-07-13T23:11:56+08:00

## Report Metadata

- report_id: remediation-report-2026-07-29-v0-7-0-public-release-body-correction
- workflow_id: 2026-07-29-v0-7-0-public-release-body-correction
- owner_skill: ai-context-governance
- status: final
- created_at: 2026-07-29T16:06:15+08:00
- updated_at: 2026-07-29T16:21:30+08:00
- template_source: .ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md
- template_version: 2.0.0
- baseline_assessment: transient V070 finding set captured by the active workflow
- verification_assessment: ASM-20260729-001

## Remediation Summary

- Authorized scope: correct only the v0.7.0 public Release body after a
  source-only phase-correct renderer and validator contract is integrated.
- Completed scope: hosted before-state frozen; published-phase source contract,
  focused regression tests, source-only payload proof, and independent
  verification completed; source PR #18 passed required checks and merged as
  b5b1a5223657933b222833f4ccf2f21e77d8c97a. From updated main, the exact
  published body was rendered and reviewed, then only the hosted Release body
  was updated.
- Validation summary: renderer 8/8, release-state 24/24, package projection,
  GitHub workflow contract, workflow artifact, assessment artifact, and
  AI-context validation pass. Post-edit read-back proves the hosted body equals
  the renderer and Release identity, annotated tag object, peeled commit, and
  four asset name/digest pairs are unchanged; hosted finalization passes.
- Closure decision: ready

## Finding Resolution Matrix

| Assessment Finding | Before Severity | Status | Changed Files | Validation | Commit | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |
| V070-PUBLIC-BODY-001 / ASM-20260729-001#VFY-004 | HIGH | resolved | final rendered body and post-edit evidence | exact body read-back, immutable-fact comparison, hosted finalization pass | b5b1a52 and this closure commit | no remaining public-body mismatch |
| V070-VALIDATOR-PHASE-002 / ASM-20260729-001#VFY-001, VFY-002 | HIGH | resolved | renderer and release-state validator | 8/8 renderer, 24/24 release-state suites | cbe1553 | finalization cannot accept tagged candidate body or supplied bypass body |
| V070-PACKAGE-BOUNDARY-003 / ASM-20260729-001#VFY-003 | HIGH | resolved | package-boundary regression test | package projection suite passes | cbe1553 | stop for owner input if later package selection evidence contradicts this result |
| V070-RELEASE-ALLOCATION-004 | MEDIUM | resolved | none | workflow and task scope retain no allocation | cbe1553 | none |
| V070-README-BASELINE-005 | HIGH | resolved | README.en.md in prior checkpoint | prior critical gate 44/44 | 96a4968 | none |

## Changes And Evidence

### V070-VALIDATOR-PHASE-002

- Changes: published renderer mode requires published status, immutable tag and
  commit, successful run, public URL, required phase sections, and no
  candidate-only publication claims. Finalization derives its body from that
  mode and compares any supplied body against it.
- Evidence: V070BODY-001-hosted-before.json captures the old body,
  V070BODY-001-published-validator-negative.json records the expected live
  failure, V070BODY-001-final-rendered-body.md records the reviewed body, and
  V070BODY-001-hosted-after.json records the immutable-fact comparison.
- Validation: focused renderer and release-state suites pass; post-edit hosted
  finalization passes.
- Remaining risk: none in source contract.

### V070-PACKAGE-BOUNDARY-003

- Changes: the package regression explicitly excludes both release-body scripts,
  script tests, and workflow artifacts from payload selection.
- Evidence: ASM-20260729-001#VFY-003.
- Validation: source-only package projection passes.
- Remaining risk: no package was rebuilt, altered, or republished.

## Verification Assessment Reconciliation

- Independent auditor: ASM-20260729-001.
- Confirmed resolved: source renderer, finalization validator, and package
  boundary findings.
- Recurring findings: none. VFY-004 is resolved by the authorized body-only
  edit and immediate invariant read-back.
- New or regressed findings: none.

## Deferred Work

| Finding | Reason | Owner | Next Action |
| --- | --- | --- | --- |
| REL-004 and successor scope | Explicitly outside this completed self-correction. | owner | Keep unallocated. |

## Closure Evidence

- Required validations: source validation bundle, independent verification,
  source PR checks, exact published-body review, immediate invariant read-back,
  and hosted finalization validation are complete.
- Commit status: source contract cbe1553; verification 7b782c3; source
  integration b5b1a52; closure evidence awaits this continuation commit.
- Workflow/task status: V070BODY-001 and the workflow are completed pending
  closure PR integration.
- Final next action: push this continuation branch, pass required checks, merge
  the ready closure PR, and synchronize local main.
