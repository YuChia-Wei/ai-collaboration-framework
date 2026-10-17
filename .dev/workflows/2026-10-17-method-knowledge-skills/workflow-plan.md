# Common method knowledge and capability work

## Authority and fixed starting point

- Workflow: `2026-10-17-method-knowledge-skills`; owner: `software-development-orchestrator`.
- Branch: `codex/2026-10-17-method-knowledge-skills`; base: `main` at `b8cfbcc12c98c71a5b2d045febde69c292ef898f`.
- Template: `.dev/workflows/2026-10-03-documentation-boundaries/template.md`, version `1.0.0`.
- On 2026-10-17 the owner approved #442 as the Feature, six child Issues, the #452 relationship, and a separate Problem Frames proposal. The owner directed document contradictions to be repaired first, then the accepted development work to continue.
- Live hierarchy read-back: #442 children are #452 and #454–459. #460 has no parent. Project fields are planning observations, not implementation evidence.
- This workflow binds local source work #454–458. #452 preserves the prior BDD delivery; it is not silently declared complete here. #459 retains the Story A/B decision for the owner; #460 remains proposal-only. Neither is an implementation task in this workflow.
- Main executor: `gpt-6-astra` / `xhigh`, confirmed by the coordinator's active turn context. Bounded document implementation contributor: `gpt-6.1-sol` / `low`. The coordinator owns integration and review, and grants one tracked writer at a time.

## Work and current checkpoint

| Task ID | Issue | Scope | State |
| --- | --- | --- | --- |
| docfix | #454 | Optional Context Map guidance, current documentation and exact-version closure | completed |
| BDD | #455 | Task-selected BDD topics and explicit consumer boundaries | in_progress |
| DDD | #456 | Optional DDD topics and model exploration | pending |
| testdesigner | #457 | Canonical test-designer and one test-design semantic owner | pending |
| integration | #458 | Requirements exploration and design-to-specification handoffs | pending |
| validation-review | #454–458 | Affected checks, fixed-subject review and per-Issue evidence | pending |

Each task has its identity and timestamps under `tasks/`. Only `BDD` is active.
Do not infer later task completion from the package versions changed for dependency closure.

## Acceptance and verification plan

The following are planned criteria, not passed results. Preserve each Issue's own AC IDs and disposition when recording evidence.

- #454: Context Map retains responsibilities, relationships, owners, failures and consistency questions as optional guidance; no universal MQ, deployment, model-sharing or contract-location mandate. Current manual versions match metadata and manifest; historical release facts and .NET target rules remain intact.
- #455: BDD topics use separate, independently readable resources selected by task; discovery, formulation, automation and Gherkin retain clear relationships and uncertainty. Loading one topic does not require the whole library or a mandatory author pipeline.
- #456: DDD exploration separates business language, model/invariants and context relationships. It does not require MQ, distributed deployment or a particular implementation framework.
- #457: One owner controls test-design judgments and formal-test outputs, including non-GWT forms. Verify canonical ID discovery, fresh selection and controlled managed update; preserve target customization and report unsupported migration cases.
- #458: Requirement exploration uses accepted decisions without asking them again unnecessarily. Specification retains the identity of design sources, constraints, unresolved choices and approval status instead of inventing new architecture authority.
- Across affected consumers: optional knowledge absent is unavailable coverage, with bounded common work permitted; no source-checkout fallback, implicit installation or hidden resource dependency.
- Validate syntax, metadata, exact-version/resource closure and current documentation first. Record package/installed and actual agent behavior separately when selected; static checks do not prove behavior or target adoption.
- Review an immutable source subject with its criteria and governing rules. Reconcile findings and review applicability under source policy; changed subject content invalidates affected review. Maintainer acceptance and any current-head hosted gate remain separate.

## Authorized boundaries

Local source edits and necessary validation are authorized within #454–458. Preserve unrelated changes and managed installed projections. Do not alter .NET target normative choices while fixing general guidance.

Push, PR creation, merge, Issue closure, publication, tags, self-installation and real-target installation are not authorized by this workflow. A local check or commit does not imply any of those states. No release allocation or delivery date is selected.

## Resume and evidence

The first writer prepares #454 and returns the diff and focused checks without committing. The coordinator inspects it before its coherent local checkpoint and later task dispatch. Unexpected tracked changes, scope mismatch or a new owner-sensitive decision stop dependent writes.

Record exact commands, outcomes, failures and not-run limits in the selected task/report at its checkpoint. Full suites, hosted CI, package installation and agent behavior are not claimed by workflow bootstrap. The parent inspected the #454 diff and focused checks, corrected the five per-skill version headers, and accepted its local implementation checkpoint. Next action: integrate the reviewed BDD/DDD drafts and their exact resource declarations, then consolidate the selected capability owners.
