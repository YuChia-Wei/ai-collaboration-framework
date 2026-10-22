# Agent Execution Guardrails Contract

This contract governs bounded delegation in this source repository. The
[source development policy](../standards/SOURCE-DEVELOPMENT-POLICY.md) owns
validation selection and conditional independent review. A role name, duration
or terminal label does not create an additional validation or admission gate.

## Bounded assignment

Give the worker the owning skill, purpose, input revision, allowed reads/writes,
non-goals, expected result, stop conditions and integration owner. State actual
authorization and any explicit execution limit. Resolve only an applicable
role; a static profile or configuration is not proof of an invocation.

Use task-selected model/effort from `.ai/custom/sub-agent-policy.json` and the
permitted execution surface. Supply task, model, effort, selection reason and
authority in the bounded assignment. Do not inherit the parent model. Codex
full-history forks cannot override the model here; use fresh bounded context.
Reconcile custom profile pins and forced Claude model/effort overrides before
invocation. Missing policy/availability stops delegation; deterministic direct
work remains available. An explicit user choice may select a different reviewer. Do not silently raise model,
effort, cost, credential privileges or provider scope. Record selected settings
separately from actual runtime observations; unavailable identity remains unknown.

There is one tracked writer per worktree. The parent stays read-only on that
worktree while a delegated writer owns it. Read-only reviewers do not repair
their own findings. Unknown ownership, authority or isolation blocks the
affected operation, not unrelated authorized work.

## Independent review

Use a clean immutable commit and explicit base-to-head diff, acceptance criteria
and governing rules. Changes to authority, security, credentials, publication,
installation or recovery require independent scoped review under source policy;
ordinary work otherwise needs author inspection and maintainer PR acceptance.
Policy edits cannot approve a lower review standard for themselves.

Record the actual reviewer, reviewed commit, findings, limitations and
disposition in the existing work record. An author's fixes are not independent
verification. Return affected fixes to the reviewer when needed; unchanged
conclusions need not be reviewed again. Identity-only drift uses a comparison
of the reviewed subject, criteria and rules, not another behavioral review.

No classifier invocation, machine-readable preflight, packet, snapshot lease or
acceptance ledger is required for ordinary source review, including review of
these project policies. Keep permission boundaries and the immutable input;
do not replace them with an unsupported claim of independence.

## Selected validation and retries

First decide whether the change warrants the test under source policy. Only
then choose direct or delegated execution suitable for the selected command.
Keep inputs stable, bound the command and output location, and preserve actual
errors and outcomes. Long duration alone does not select a matrix, external
platform or new report schema. Use an available completion event/callback for
delegated long-running work rather than repeated status polling.

After a failure, identify the cause and relevant repair or new information;
rerun only the affected checks. Do not repeat unchanged work without a concrete
reason. Re-plan repeated failures; do not silently exceed an explicitly agreed
retry/cost limit. Ordinary repair needs no separate fingerprint artifact or
automatic third-attempt authorization ceremony.

## Historical context — NOT AN EXECUTION TRIGGER

The [earlier guardrails contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/contracts/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md)
describes legacy packet, lease, preflight and ledger formats. Its presence is
not permission or a requirement to execute them. Retained records keep their
original meaning. Only an explicitly selected legacy/release obligation may
select that compatible revision and verified tooling; unavailable routes stay
unavailable. This cleanup does not waive security, recovery or publication duties.
