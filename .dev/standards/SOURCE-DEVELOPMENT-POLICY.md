# Source Development Policy

**Source repository only.** The owner adopted the source cutover on 2026-10-02
and native GitHub path filters on 2026-10-04. The 2026-10-18 decision in
[#461](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/461)
simplifies validation and replaces superseded operating instructions.
The [original adoption record](../workflows/2026-10-02-source-development/adoption.md)
retains its historical evidence. A policy decision is not CI success,
independent review, integration, publication or downstream adoption.

## Scope and retained authority

This policy owns ordinary development in this framework source repository,
including skills, schemas, tools, distribution, tests and source governance.
Product resources remain in `src`; managed installed projections are consumed,
not hand-edited. Framework changes for downstream rule maintenance are separate
under [#463](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/463);
this source policy does not implement or adopt that Feature.

Released target semantics, published assets, selected release phases, active
legacy execution/recovery records and credential owners retain their authority.
Ordinary source work does not restore removed tools or migrate historical
records. See the non-executable historical boundary below only when a retained
obligation is explicitly selected.

## Eight source rules

1. Bind material work to the authorized online Issue, owning capability and
   bounded acceptance. Keep Issue, Project, execution, integration, publication
   and adoption states separate. Small single-pass work may use direct mode;
   durable transitions needing unique coordination state use one source workflow.
2. Use a dedicated branch and one tracked writer per worktree; preserve unrelated
   changes. Edit the actual source owner within authorization. Keep project
   configuration and released support with their owners; do not invent tooling.
3. Before running tests, inspect the actual change and select only needed local
   checks using the rules below. The PR hosted gate remains fixed: GitHub's
   native `src/**` and `tools/**` filters select `python -I -B tests/run.py`.
   No Git-diff classifier, file-count gate or automatic high-cost matrix is used.
4. Record source identity, actual commands/results, retained failures, relevant
   limitations and next action in the existing work record. Distinguish static,
   fixture, local, hosted, installation and actor evidence. No result establishes
   more than it observed; failed, blocked, not-run and unknown are not passed.
5. Inspect the diff and validate the complete planned commit message before a
   coherent commit. Retain grammar, workflow identity when selected, and truthful
   AI attribution. Push, PR and integration need their actual authorization.
   Validate applicable PR-added authored commits without an aggregate gate or
   rewriting provider-native history.
6. Ordinary changes need author inspection and maintainer PR acceptance. Changes
   to authority, security, credentials, publication, installation or recovery
   additionally need independent scoped read-only review of an immutable diff,
   acceptance criteria and governing rules. Record reviewer, full commit,
   findings and disposition. Author inspection is not independent review.
   Relevant changes require affected review again; identity-only drift needs
   comparison of the reviewed diff and rules, not another review. No legacy
   receipt, preflight, packet or lease is required. Policy changes cannot lower
   their own review or admission standard.
7. For PRs selected by the native `src/**` or `tools/**` filters, require actual
   current-head `Source change gate` success before integration. Outside those
   paths the source CI context is not applicable, never a fabricated pass.
   Retain fresh PR head/base, effective reviews and actual required checks.
   Respect provider protection without implicitly changing it. Use final or
   deferred intent for each delivered Issue; read integration, Issue and
   Project state separately. Administrative closure of accepted integrated work
   requires explicit owner authority, not an invented historical closing keyword.
8. Preserve published support, recovery records, historical evidence, credentials
   and external-setting ownership. A source PR never implicitly publishes,
   installs, changes protection or resolves provider defects. Use only explicitly
   selected compatible legacy/release procedures; no unavailable route is passed.

## Decide before running a test

At task planning, identify validation purpose, expected evidence, trigger and
execution point. Distinguish mandatory gates and accepted acceptance requirements
from checks conditional on anticipated impact. Schedule shared checks at the
appropriate integration point rather than once per task, unless actual changes
or required gates justify repetition. Use the existing plan or task output.

During implementation, reconcile that plan with the actual diff, semantics and
direct dependencies; confirm necessity before execution. After the change,
confirm required acceptance evidence is complete. Bug reproduction, TDD and
incremental checks may run before or during edits for a concrete purpose.
A preliminary decision does not freeze the test plan. Return wider impacts to
the coordination owner; changes to accepted requirements need their owner's
decision. Do not silently cancel mandatory gates or accepted acceptance.
The presence of an edit, file extension, directory, commit or workflow stage
does not by itself select a local test.

- Whitespace-only changes with no parsing, output or content-contract effect,
  ordinary explanatory text, and changes that do not affect schema semantics
  or constraints need no product/schema tests merely because of their location.
  Check changed text, links or formatting when those are the actual subject.
- Whitespace can affect YAML, code, templates or exact output. Select the checks
  for that real effect; do not assume every whitespace edit is harmless.
- For behavior, contract or dependency changes, use the directly affected
  existing cases or suite. Add tests only for a real new behavior or confirmed
  defect that lacks necessary protection, not to mirror this policy.
- Large integration, E2E, usability, full installation/upgrade matrices and
  high-cost AI evaluations require a clearly affected behavior/integration
  boundary or an explicit user/accepted-acceptance requirement. Select only the
  relevant scenarios, not every model, catalog entry or upgrade path.
- If impact is unclear, investigate the relevant dependency first. Do not
  silently substitute a cheaper claim for required acceptance, mark unknown
  coverage passed, or expand uncertainty into an automatic full matrix.

A brief explanation in the current work record is enough; this decision does
not require a new classification file, tool, ledger or approval ceremony.

When planning hotfix validation or changes to installation, upgrade or reinstall
compatibility, consult the [v0.20.1 hotfix lesson](../lessons/records/hotfix-testing-release-20261019.md)
for observed gaps, timing limits and scenario-selection tradeoffs. Apply the
selection rules above; the lesson's historical trial matrix and improvement
proposals do not define additional gates.

| Stage | Validation choice |
| --- | --- |
| Local development | Only checks justified by the actual change; no mandatory per-edit/per-commit full suite |
| Repair after failure | Identify the cause and rerun the affected cases; expand only for a concrete wider impact |
| Preparing a PR | May run the same default suite once as a local integration check; not a mandatory double-run rule |
| PR integration | Required current-head hosted gate and applicable review; local passes cannot substitute |
| Reports, handoff and closeout | Inspect the changed record and necessary provider facts; no product rerun solely for the stage |

The hosted path filters intentionally remain independent of local semantic
selection. A new selected PR head still needs its actual hosted result, even
when local tests were not needed.

## Reuse and stop conditions

Keep a passing result when no subsequent change affects its claim. Assess the
diff, relevant inputs and dependencies, including environment where it matters.
Do not require a complete hash inventory, transitive resolver, receipt or paired
reports simply to avoid repeating a check. A changed SHA, report, session or
executor is not itself a product test trigger. Attribute old results to their
actual execution; never relabel them as a fresh run.

Retain failures and their disposition. A retry needs a relevant repair, new
information or another concrete reason; do not blindly repeat unchanged work.
Re-plan repeated failures and honor explicitly agreed limits. Missing coverage
stays missing; current provider facts and applicable review remain separately
required. No automatic third-attempt artifact or cost dataset is required.

Keep selected execution inputs stable. For long-running commands, finish the
relevant changes before execution, isolate any writers, bound the command and
timeout, preserve its result and stop on relevant drift. Choose a suitable
direct or delegated surface within authorization; duration alone does not
mandate an external platform, immutable commit, new schema or matrix.
Independent review still uses the fixed commit required by rule 6.
Use available completion events/callbacks for delegated long-running work,
rather than repeated status polling.

## Maintain the effective rule, not a stack of exceptions

For an authorized rule change, delete or replace obsolete, duplicate and
contradictory instructions at their owner. Keep one coherent effective body;
do not leave stale operational steps beneath an added priority disclaimer.
Preserve still-valid protections, unrelated custom content and historical records.

If old experience is unnecessary in the current policy, remove it from the
operating text. If retaining it is useful, place it in a clearly marked
`NOT AN EXECUTION TRIGGER / historical context only` section, state its actual
applicability and remove it from current operation navigation. A label alone is
not execution isolation; the effective body and entry links must agree.
Do not broaden this work into rewriting all repository history.

## Delegation and work records

A bounded assignment names owning skill, input revision, scope, permissions,
non-goals, result, stop conditions and integration owner. Select explicit model/effort by task under `.ai/custom/sub-agent-policy.json`;
never inherit the parent model as a fallback. Luna/Haiku are routine defaults,
Sol/Sonnet serve substantive reasoning, and Astra/Opus require separate explicit
authority. Never infer spending or privilege permission from a role name or available model. Configuration is
not proof of actual runtime identity, usage or billing. Keep one tracked writer
per worktree and a read-only reviewer on the immutable subject.

Use the existing locator/task identity fields in
[workflow artifacts](WORKFLOW-ARTIFACT-POLICY.md) when workflow mode is needed.
Check changed records, not every historical workflow. A
[handoff](WORKFLOW-HANDOFF-POLICY.md) records source/branch, authority, completed
and pending work, actual results, limitations and the next action.
No new record store or automatic historical migration is selected.
Graph discovery needs known source identity/coverage or an explicit tracked-file
fallback. Never assign PowerShell automatic/reserved variables.

## CI and publication boundaries

`source-checks.yml` runs on Windows/Python 3.13 with pinned
`tests/requirements.txt` dependencies and the fixed default suites. Optional
loader/platform tests are local selected checks, not native installation
acceptance. Documentation, project-policy, tests-only and workflow-only changes
do not automatically trigger this job under the existing native path filters.

Source checks, package snapshots and Draft Release delivery retain their
separate roles. No Actions permission, ruleset, credential, release environment
or publication setting change follows from this policy. Reconcile a provider
rule requiring an absent path-filtered check with its owner; never fabricate
success or silently change protection.

## Historical context — NOT AN EXECUTION TRIGGER

The [pre-simplification policy](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/standards/SOURCE-DEVELOPMENT-POLICY.md)
records earlier cutover dispositions. Legacy aggregate/critical gates, packet,
lease, receipt, closure-resolver and fixture-acceleration procedures are not
ordinary source commands. Do not invoke or restore them from historical mentions.
Only an explicitly selected legacy/native/release obligation chooses its own
compatible revision, authority and verified tools. Unrestored U001/P7 obligations
remain deferred-by-owner or blocked for that operation; this cleanup does not
waive them or alter published assets. Hosted success and downstream adoption
remain separate from those obligations.
