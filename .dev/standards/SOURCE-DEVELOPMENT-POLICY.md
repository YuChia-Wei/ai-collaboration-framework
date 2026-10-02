# Source Development Policy

**Status: adopted by the owner on 2026-10-02. Source repository only.**
The [adoption record](../workflows/2026-10-02-source-development/adoption.md)
records the direct owner decision covering this cutover, independent scoped
review, Source checks activation, PR integration and backlog reconciliation.
These rules govern this authorized transition immediately; repository-wide
integration follows the reviewed PR and successful actual current-head CI.
Policy adoption itself is not independent review, hosted success or a merge.

## Scope and retained authority

These adopted rules govern newly authorized development in
this framework source repository, including skill instructions, schemas, tools,
distribution code, tests and source governance. They supersede conflicting
ordinary-source aggregate, receipt, packet, lease and handoff requirements.
The exact bootstrap review and first hosted check remain separately observable.

Existing released target semantics, published assets, selected release phases,
active legacy execution/recovery records, frozen backlog and credential owners
retain their contracts. Legacy maintenance selects its compatible source revision,
policy/configuration and actual available tools; this transition does not make
removed `artifact_core`, registries or resolvers available. Do not run old
validators against the new configuration as if its schema were backward compatible.
Do not restore old code merely to admit unrelated source work.

## Eight source rules

1. Bind material work to the authorized online Issue, owning capability and
   bounded acceptance. Keep Issue, Project, execution, integration, publication
   and adoption states separate. Small single-pass instruction/documentation
   changes may use direct mode and a concise PR record; durable transitions and
   connected multi-stage work retain one source-owned workflow.
2. Use a dedicated branch and one tracked writer per worktree; preserve unrelated
   changes. Edit reusable product in `src/`; consume managed core/runtime entries.
   Keep project configuration/data and released support with their actual owners.
   Select existing routes explicitly, rather than inventing unavailable tooling.
3. Select affected checks from both pinned Git trees, including deleted and
   renamed paths. Prose needs content/reference/whitespace inspection. Schemas,
   tools and distribution select their actual bounded suites. Unknown ownership,
   missing checks, errors, skips or failures block the affected check. No automatic
   whole-history/full/nightly fallback or schema per instruction file is required.
4. Record full source identity, exact commands, actual outcomes, retained failures,
   limitations and next owner. Distinguish static, fixture, local, hosted, native
   and actual agent evidence. Logical selection is not physical assembly or
   installation coverage. Unavailable/deferred/neutral results are never passed.
5. Inspect the diff and validate the complete planned commit message before
   each coherent commit. Retain grammar, selected workflow identity and truthful
   AI attribution. Push, PR and integration need their actual authorization.
   Validate PR-added authored commits when applicable, without rewriting history
   or requiring an aggregate gate. Provider-native commits retain their owner.
6. Ordinary changes need author inspection and maintainer PR acceptance. Changes
   to authority, security, credentials, publication, installation or recovery
   additionally need independent scoped read-only review of an immutable diff,
   acceptance criteria and governing source rules. Record reviewer, full commit,
   findings and disposition. Implementation or author inspection is not independent.
   Changed reviewed content, criteria or authority needs affected review again;
   history-only drift may reuse review only with exact tree equivalence and fresh
   head binding. No mandatory legacy receipt, review-input packet or lease applies
   to this adopted source scope. Policy/selector changes cannot approve a lower
   review or admission standard for themselves.
7. After CI restoration, require actual current-head `Source change gate` success,
   live PR head/base, effective review conditions and selected native/release
   evidence before integration. Missing provider facts block that claim. Source
   test success does not discharge separately listed admission requirements.
   State final/deferred intent for each Issue; use `Refs` with reason and next
   owner for checkpoints. Read merge, Issue and Project separately. Already
   integrated delivery may be closed administratively after accepted evidence
   and explicit owner authority; never invent a historical closing keyword.
8. Preserve published support, recovery records, frozen history, credentials and
   external-setting ownership. A source PR never implicitly publishes, installs,
   changes branch protection or resolves a provider defect. Legacy validators
   apply only to explicitly selected version/release/incident obligations. Retiring
   an ordinary gate does not authorize deleting its implementation or evidence.

## Execution and evidence

Bounded delegation identifies owning skill, input revision, scope, permitted
reads/writes, non-goals, result, stop conditions and integration owner. Select
the least expensive capable execution profile within actual authority. Preserve
one tracked writer per worktree; reviewers remain read-only on a clean fixed
subject. No tool/profile declaration is proof that an agent ran.

Selected lengthy validation still pins source, isolates writers, preserves logs,
uses a bounded completion wait and stops on drift. No automatic external-agent
platform, signed packet, acceptance ledger or snapshot lease is required. Keep
failed attempts; retry only after a relevant change, and re-plan repeated failures
instead of retrying unchanged input. Unknown evidence dependencies are not reused.
Graph discovery needs known source identity/coverage or an explicit tracked-file
fallback. PowerShell automatic/reserved variable names are never assigned.

Source workflows continue under `.dev/workflows/<id>/` with the existing locator
and task identity fields from WORKFLOW-ARTIFACT-POLICY. This selects no new #416
online record store and migrates no historical record. Check relationships for
changed records, not every workflow in history. Handoffs need source/branch,
authority, completed/pending work, exact commands/outcomes, residuals and next
action; historical critical/registry machinery is not an ordinary prerequisite.

## Gate dispositions

| Surface | Adopted ordinary-source treatment | Retained boundary |
| --- | --- | --- |
| Five old required contexts | Exactly `Source change gate` | Separately selected release evidence; no claim of server enforcement |
| Audit/v3, review-input packets, digest/rebind and leases | Scoped independent review under rule 6 | Historical receipt meanings and selected release audits |
| Terminal declaration/admission/reconciliation platform | Per-Issue intent plus actual checks and live read-back | Historical validator/configuration contracts; no hybrid receipt |
| `check-all`, full/history/nightly matrices | Affected suites via `tests/run.py` | Explicit legacy incident/release scope only |
| `artifact_core` and old effective-rule resolver | Not a dependency of ordinary source admission | Missing routes remain unavailable until separately restored |
| Universal handoff registry and whole-workflow scan | Bounded source workflow/handoff described above | Active legacy records and release phase requirements |
| Runtime parity | Changed actual source/installed owners only | Managed installed projections remain protected |
| High-I/O/installation/linked-worktree trials | Retired by #425; no automatic recreation | New real consumer need requires a selected scenario and acceptance |
| Fixture acceleration and benchmarks | No ambient drive selection or unmeasured speed claim | #274/#275 receive explicit obsolete-scope disposition; no measured benchmark pass |
| Release, support, credentials and protection | Unchanged | Their explicit owners and approval boundaries remain |

## CI subset and remaining U001 obligations

The selected source gate runs on Windows with Python 3.13 and pinned
dependencies from `tests/requirements.txt`. It invokes
`python -I -B .github/scripts/check-source-change.py --base <full-sha> --head <full-sha>`;
that selector invokes only affected `tests/run.py --suite` commands. Optional
platform/loader suites do not establish native installation acceptance.

The owner authorized enabling only `source-checks.yml` for this transition. Keep the existing
package-candidate/publish-release workflows in their independently authorized
state, and leave the other six workflows disabled, including obsolete
`source-native.yml`. No Actions permission, ruleset, protection, credential,
release-environment or publication setting changes are selected. Maintainer
admission is not server-side required-status enforcement.

U001 remains for explicitly selected uncompleted legacy/native/release obligations
outside this adopted ordinary-source scope. Missing native acceptance stays
`deferred-by-owner` or blocked for its affected operation. Hosted source success,
downstream adoption and full P7 completion are separate facts.
