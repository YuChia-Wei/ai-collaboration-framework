# P7 source pipeline and policy proposal

Design for [Issue #365](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/365), program #322.
Status: **proposed; implementation and restoration not adopted**.
Source inspected: `171f33474f88888fbe853600de04bfe9c5716b25`.
[U001](../../../standards/FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md) remains effective.
This design changes no executable rule, workflow, support commitment or provider setting.

## Decision

Replace ordinary source admission's five legacy check contexts with one unconditional
PR context, **Source change gate**, selecting small checks by actual ownership and
changed behavior. Add one manual native workflow for specifically selected filesystem/
process/platform cases. Do not create a nightly matrix, universal audit packet,
lease service, evidence-reuse engine or another check registry.

Keep legacy release, published-package support and active recovery with their
existing version-specific owners. Retiring an ordinary CI invocation does not retire
a compatibility promise, delete historical evidence or approve a future release.

- [Pipeline dispositions and exact future interfaces](pipelines.md)
- [Source rules, mandatory-gate dispositions and adoption sequence](source-rules.md)
- [Fresh provider observation](../../../workflows/2026-09-23-pipeline-redesign/evidence/provider-observation.json)
- [Workflow and handoff](../../../workflows/2026-09-23-pipeline-redesign/workflow-plan.md)

## Evidence and present limits

The seven actual workflow files agree with #324's IDs/paths. Live observations on
2026-09-23 at 14:32 +08:00: repository Actions disabled; all seven workflows
`disabled_manually`; workflow token default `read`; PR-review approval disabled;
SHA pinning requirement false. The disabled Actions response omits `allowed_actions`;
only the historical before-state says `all`. Do not infer a current value.

Live main equals the inspected source. Its branch response says `protected:false`,
required checks enforcement off and empty contexts/checks. Protection lookup returns
404 `Branch not protected`; repository/parent rulesets and effective main rules
are both empty. Therefore the five contexts in
`GITHUB-WORK-MANAGEMENT-POLICY.yaml` are **source-policy requirements, not currently
enforced branch protection**. The release environment exists but has no protection
rules or deployment branch policy. A named environment is not an approval barrier.
No secret value, token validity or Projects permission was inspected.

#274/#275/#308/#309 are OPEN at observation. #302 is CLOSED, and v0.18.0 is a
published non-draft/non-prerelease Release. #302 records owner-accepted manual
publication closeout and a failed hosted run; #309 retains the unresolved hosted
Project preflight defect. This design neither reopens #302 nor marks that run passed.
No inventory of external targets, active journals or untracked recovery stores was
performed; their absence is not established.

Primary source inputs are the [P7 assignment](../p7-design-handoff.md),
[#324 inventory](../../../workflows/2026-09-23-redesign-transition/evidence/ci-restoration-inventory.yaml),
[final mapping](../../../workflows/2026-09-23-framework-redesign-control/reports/p5-final-mapping-scope.md),
[#361 root proposal](../source-adoption/root-bindings.md), current seven workflow
YAML files and the source policies identified in `source-rules.md`.
The final mapping supersedes #361's older counts: 18 packages / 113 members /
seven profiles; source-repository selects 15 ordinary packages / 99 members.
These are source declarations, not built, installed or validated results.
No implementation discovery or code-graph completeness claim is needed for this
non-code design; exact new behavior commands belong to #364.

## Small continuation

1. Coordinator reconciles this proposal with #364's check purposes, exact argv,
   case ownership, runner dependencies and I/O bounds. Select one implementation
   Issue for the dormant selector/workflows plus coherent source-policy edits.
   Undefined selected checks must fail explicitly, never run a placeholder green.
2. Select actual local trials and #361 Lesson pilot/root activation on explicit
   target/engine/storage bindings. Fix only observed defects; keep all earlier
   failed/deferred results. Root adoption and portable success are separate facts.
3. Present one exact restoration set with actual trial limits for user adoption.
   Only then enable the named workflows, observe runs and reconcile source policy.
   A merged design or dormant implementation is not adoption or CI success.

Material decisions remaining: coordinator's exact #364 command bindings and trial
selection; actual #361 activation bindings; user's concrete restoration adoption.
Protection changes, release enablement, credential repair, supported-version
withdrawal and retirement of active recovery data are separately owned decisions,
not hidden prerequisites for ordinary document improvement.

All product CLI/help/import, schema validation, tests/fixtures/build/render/package/
install/migration/probe, independent audit/lease/effective-rule/acceptance machinery
and CI remain **deferred-by-owner**, U001, **program #322 coordinator / P7**.
Next action is reconciliation and explicit selection of implementation/trials.