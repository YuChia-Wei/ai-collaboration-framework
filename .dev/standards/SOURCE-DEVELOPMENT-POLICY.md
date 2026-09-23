# Prospective Source Development Policy

**Status: dormant; not adopted; not effective. Source repository only.**
This document records the prospective rules selected by Issue #369 from the
[#365 source-rule design](../design/framework-next/pipeline-redesign/source-rules.md).
The owner's approval permits writing this dormant policy and applicability
pointers. It does not adopt these rules, narrow U001, enable CI or authorize any
provider, release, installation or downstream change.

Current effective policies and the applicable
[U001 override](FRAMEWORK-REDESIGN-EXECUTION-OVERRIDE.md) remain authoritative.
Every replacement below describes only a future, explicitly adopted source scope.
A date, local pass, pilot, commit or merge does not make any replacement effective.

## Eight Prospective Rules

1. Bind material source work to its authorized online Issue, owning capability and
   bounded acceptance. Keep Issue, Project, execution, integration, publication
   and adoption states separate. Small single-pass instruction or documentation
   improvements may use direct mode with a concise PR record; durable transitions
   and work crossing owner boundaries retain a workflow.
2. Use a dedicated branch and one tracked writer per worktree; preserve unrelated
   changes. Reusable new product belongs in `src/`; installed core/runtime entries
   are consumed, and project configuration/data retain their owners. Select actual
   current routes explicitly, including still-active legacy and release owners.
3. Select the smallest affected checks from both pinned Git trees, including
   deleted and renamed paths. Prose needs content, reference and whitespace
   inspection; tools, schemas and distribution changes need their actual owners'
   checks. Unknown ownership or dependency impact and missing, skipped or failed
   selected commands block the affected admission. Do not fall back to a whole
   history, full or nightly matrix, or require a schema for each instruction file.
4. Record full source identity, exact commands, actual outcomes, retained failures,
   limitations and the next owner. Distinguish synthetic, local, hosted and native
   evidence, and logical selection from actual assembly coverage. A Lesson smoke
   cannot establish every package/profile build. Never describe unavailable,
   blocked, deferred, skipped or neutral results as success.
5. Inspect the diff and validate the complete planned commit message before each
   coherent commit. Retain commit grammar, the selected workflow identity and
   truthful AI attribution. Authorized push and PR integration remain separate.
   After adoption, ordinary source work has no whole-history or aggregate gate;
   applicable CI message checks concern PR-added locally authored commits and do
   not rewrite provider-native or historical commits.
6. Ordinary changes need author diff inspection and maintainer PR acceptance.
   Authority, security, credential, publication, installation and recovery changes
   additionally need independent, scoped, read-only review of the fixed diff,
   criteria and applicable source rules. Record reviewer, full commit, findings
   and disposition in the PR/workflow; author inspection is not independent.
   Changed content, scope or authority requires the affected review again. This
   replacement does not mandate a new signed receipt, rebind packet, lease or
   registry platform. Policy and selector changes cannot approve their own lower
   review or admission requirements.
7. After adopted CI restoration, read the live PR head/base and require actual
   current-head **Source change gate** success, effective review conditions and
   any selected native/release results. Missing provider facts block that claim;
   credentials are not an ordinary local-check prerequisite. State each Issue's
   final or deferred intent in the PR; checkpoints use `Refs` with a reason and
   next gate/owner. Read merge, Issue and Project state separately. Closing intent
   never authorizes work or establishes factual closure.
8. Preserve published assets, support promises, active recovery records, frozen
   history, credentials and external-setting ownership. A source PR never
   implicitly publishes, installs into a target, resolves a provider defect or
   changes protection. After adoption, legacy validators run only for explicitly
   selected version, release or incident obligations. Retiring an ordinary gate
   does not retire support or authorize deletion of its implementation/evidence.

## Prospective Gate Applicability

All replacements in this table are dormant. Existing effective fields, required
contexts, receipt interpretations and U001 deferrals are unchanged by this file.

| Existing surface | Treatment only within a later adopted source scope |
| --- | --- |
| Five ordinary required contexts | Replace with exactly `Source change gate`; retain separately selected release checks. Do not impose both ordinary mandatory sets. |
| Audit/v3 receipt, review-input preflight, digest/rebind and live admission overlay | Replace ordinary admission with rules 6 and 7. Preserve historical receipt meaning, effective review blocks and version-owned release audits. |
| Terminal declaration/admission/reconciliation packet | Replace the ordinary mandatory packet with per-Issue PR intent and separate live read-back. Keep legacy validators unchanged for explicitly selected legacy records; invent no hybrid receipt. |
| `check-all` and broad legacy profiles | Replace ordinary invocation with affected checks. Preserve named legacy release/incident obligations, with no automatic full/nightly fallback. |
| External-task, acceptance-ledger, packet/lease and custody machinery | Replace ordinary mandatory machinery. Selected lengthy trials still pin source, isolate writers, preserve logs/outcomes, use a bounded completion wait and stop on drift. U001 remains applicable until separately narrowed. |
| Critical handoff and checkpoint registry | Replace with source/branch, scoped state, commands/outcomes, residuals and exact next action. Preserve active legacy checkpoints and release phases. |
| Universal workflow locator/task/terminal-anchor synchronization | Use the owning package's records only after its real adoption, including the #361 collection if selected. Preserve existing history and active contracts; no date-based migration or dual-format padding. |
| Source effective-rule packets and full guardrails | Read named owning policies directly for newly adopted source work; preserve explicitly selected legacy applicability and released target semantics. |
| Commit checks and AI signature | Retain exact planned-message validation, grammar, applicable workflow identity and truthful attribution. Remove no executable commit rule through this document. |
| Runtime parity and schema/registry validation | Select changed owning sources/routes and actual adopted installation. Still-active legacy entries retain their contracts; new prose does not inherit every legacy registry. |
| Frozen backlog and work-management authority | Retain live GitHub authority and frozen evidence. Check an affected freeze boundary without scanning every historical record for every PR. |
| Source release, admitted archives, publication, support and recovery | Retain the selected published-version and release-phase owners. #309 recovery and target journals remain separate; unknown activity prevents support deletion. |
| Portable fixtures and benchmark obligations | Preserve actual legacy acceleration/measurement scope and #274/#275 obligations. Claim no unmeasured savings or new universal evidence-reuse implementation. |

## Activation Is A Separate Decision

The [implementation checkpoint](../design/framework-next/source-gates-implementation/README.md)
records actual commands, runner bindings, failures and limits. Contracts and public
CLI bindings exist; their local synthetic tests do not establish actual product
acceptance. Native binding/trials, root adoption, independent scoped review and
hosted evidence remain outstanding at this checkpoint.

Before activation, present the concrete policy/root/template/runner diff, applicable
selected-check and trial evidence, proposed provider settings and workflow subset,
and the exact owner decision, adopted scope, effective date and remaining U001
obligations. Review those surfaces together. Narrow adoption must name its limits;
missing evidence stays blocked or deferred, not passed.

Both effective YAML files remain unchanged except for comments. Their closed
schemas receive no invented dormant keys or hybrid review values. A later approved
cutover must coherently update effective fields, root applicability and the PR form
for its selected scope, preserving historical and still-active legacy meanings.
The commit-policy YAML needs no change for this dormant delivery.

CI enablement, current-head hosted success, root/runtime adoption, integration,
Issue/Project disposition, releases, credentials and downstream adoption remain
separate decisions and observations. No restoration command is authorized here.
