# Source development continuation

## Authority and scope

The owner instructed this conversation on 2026-10-02: "按照你規劃的順序處理那四件事情".
The referenced ordered actions are (1) source development rules and gate #369,
(2) lightweight test CI calling `tests/run.py`, (3) disposition of obsolete
#274/#275 and acceptance/closure of #425, and (4) representative actual skill-use
scenarios. The owner subsequently removed step 4 and will arrange it separately.
Only steps 1-3 remain in execution scope. #416 workflow online migration is excluded.
The same correction adds a read-only assessment of fresh-target root AGENTS
guidance after removal of init, including severity and remediation alternatives.

This authorizes preparation and implementation of the four outcomes. The concrete
policy adoption and CI restoration boundary must be recorded explicitly under
the existing source policy; PR #426's single-merge exception is not reused.
No tag, public release, credential change, branch protection/ruleset change,
downstream installation, old support deletion or branch deletion is selected.

Base: `4f231fe7f08eaa9ae296ec243be524658f8d3849`. One workflow owns all four steps.
Root integrates; read-only inventory agents are not independent reviewers.
The current source graph excludes `.github/scripts`, `tools` and tool packages;
explicit Git-tracked file reads supplement that partial index.

## Ordered tasks and observable acceptance

| Task | Owner | Acceptance |
| --- | --- | --- |
| T1 | ai-context-governance / root | One coherent proposed source policy, bilingual root applicability, effective configuration and PR form; known legacy gates receive explicit ordinary-source or retained-version disposition. Source selector recognizes current workflow records without admitting unknown executable files. Focused tests preserve fail-closed behavior. Exact adoption/review boundary is explicit. |
| T2 | local-change-implementer / root | CI uses the current runner, explicit dependencies and an actually supported environment. Only the selected Source checks workflow is proposed for enablement; existing release workflows and settings retain their owners. Actual hosted result is bound to the precise head or reported unavailable, never inferred from local tests. |
| T3 | software-development-orchestrator / root | Read current #274/#275/#425 scope, record cancellation/replacement versus completed delivery truthfully, mutate only authorized Issue/Project state and read it back. #369 remains open for any unresolved accepted scope. |

## Initial observations and limits

- `artifact_core` and old canonical role/skill assets required by legacy full
  review preparation are absent. Their unavailable validators must not be labelled
  passed; a source adoption needs an explicit bootstrap review decision.
- Source selector hardcodes one historical workflow root; current workflow
  JSON/YAML therefore has no owner. General workflow ownership must validate
  locator/task relationships, not accept every arbitrary file below `.dev/`.
- `source-checks.yml` is disabled and selects Ubuntu although some selected
  suites need Windows. Proposed first supported runner is Windows, with optional
  platform suite selected by changed paths.
- Live provider read-back at 2026-10-02T13:00:01+08:00: Actions enabled; only
  package-candidate and publish-release active; seven others disabled. Defaults
  are read token / cannot approve PRs, allowed actions all, SHA enforcement false.
- Historical native installation/recovery drivers were explicitly removed by
  #425. `source-native.yml` is an obsolete non-passing placeholder, remains
  disabled, and supplies no native acceptance.

## Current state

T1 in progress. T2-T3 pending; bounded read-only inventories may proceed in
parallel, while implementation/provider effects retain the ordered sequence.
Next: prepare the concrete transition, run focused checks and record the exact
remaining owner adoption boundary before enabling source CI.
