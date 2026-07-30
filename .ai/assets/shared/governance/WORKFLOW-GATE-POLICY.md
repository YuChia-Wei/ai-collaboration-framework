# Portable Workflow Gate Policy

This target-facing policy separates work-management state from authorized
repository execution without requiring a tracker provider.

## Work Lifecycle

| State | Authority | Repository consequence |
| --- | --- | --- |
| Conversation or exploration | Conversation participants | No branch, workflow, commit, or integration claim. |
| Candidate work | The target's selected provider or conversation when none is selected | Records possible work but does not authorize execution. |
| Authorized execution | Explicit owner authorization, optionally bound to an approved work item under target policy, plus a skill-owned workflow when the gate applies | Create the dedicated branch before workflow artifacts or material edits. |
| Integrated repository fact | The target repository's configured integration mechanism | Integration and workflow completion are separate facts and must be verified separately. |

A provider is replaceable. Provider identifiers, states, links, and
availability are optional evidence; they never replace repository workflow
truth or authorize execution. When no provider is configured, an authorized
repository workflow remains fully operable.

## Work-Item Binding Selection

A valid work-item binding jointly preserves traceability to the approved work
outcome and evidence of execution authorization. A provider item or provider
state alone never authorizes work; the binding is valid only when explicit
owner approval is recorded.

Each target team selects `workManagement.workItemBinding.mode` in
`.dev/project-config.yaml`:

- `required`: bind an approved work item before execution;
- `optional`: prefer a binding, but allow separately recorded explicit owner
  authorization; or
- `disabled`: do not use work-item bindings.

The team separately selects `mergeGate` as `required`, `optional`, or
`disabled`. A required merge gate blocks integration without a valid binding.
An optional gate may report or request the binding but permits an explicitly
owner-approved exception. A disabled gate performs no binding check.

These are target-owned decisions. Initialization leaves both selections
unresolved until the target team decides them, and upgrades preserve or
reconcile the target's choices rather than copying the source repository's
provider setting.

## Workflow Gate

Use workflow mode when authorized execution changes source-of-truth, affects
future agent behavior, crosses stages or skills, needs durable task state, or
is explicitly required by the owner. Keep transient analysis, exploration,
and small single-pass work in direct mode. Persist a read-only assessment
without remediation as assessment mode.

Workflow mode requires a dedicated branch, a locator, skill-owned tasks, exact
validation outcomes, and a closeout that checks workflow completion separately
from integration. A candidate record, detailed plan, provider event, pushed
branch, or integrated change does not by itself prove workflow completion.

Blocked, deferred, and not-applicable outcomes are not passed. Any provider or
integration customization belongs to target-owned policy and must be preserved
or reconciled rather than overwritten by a framework upgrade.
