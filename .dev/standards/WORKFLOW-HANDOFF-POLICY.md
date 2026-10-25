# Workflow Handoff Policy

This source-project policy governs continuation of authorized unfinished work.
Use the [source development policy](SOURCE-DEVELOPMENT-POLICY.md) for validation
and [branch policy](../TEAM-GIT-FLOW-RULES.MD) for Git transport. A new session,
model, host or executor is not itself a reason to rerun product tests.

## A usable handoff

Update the selected native workflow's existing entrypoint or work record under
[workflow storage](WORKFLOW-STORE-POLICY.md) with:

- the Issue, accepted scope and actual authorization, including exclusions;
- repository, branch/base and source commit, plus any uncommitted work;
- completed and pending work, decisions, unresolved findings and next owner;
- relevant commands/results and where their evidence can be read;
- the next concrete action and any missing permission or environment;
- the complete WorkflowRef, accepted native revision, logical entrypoint document
  and explicit configuration path; preserve the exact pending operation request
  or receipt when its outcome is uncertain.

The source-store policy gives the actual source CLI and complete-read procedure.
`context`/`resume` are bounded projections: when complete metadata/tasks are
needed, paginate `source-list`, select the matching native snapshot, compare
`manifest.source.native_revision` with context and verify `_native/state.json`
chunks and full hash before using its fields. Missing configuration/store stops
dependent continuation without Git fallback. Local acceptance and pending replica
intents must not be reported as Board synchronization completion.

The receiver must be able to continue without private conversation history.
Keep one current entrypoint. Do not duplicate the same facts into a universal
registry, a machine checkpoint and a second human report. A bounded sub-agent
assignment may carry this information in its dispatch rather than creating a
new workflow. Do not fabricate missing model/runtime or validation observations.

## Before continuing

Read the handoff, selected native state, current Issue authority, branch and
working-tree changes.
Check only the inputs needed for the next action. Resolve stale or conflicting
state before writing; preserve other writers' work. Resume from the correct
branch instead of restarting work already completed.

An explicitly continued historical Git workflow first needs the store policy's
native creation and provenance read-back. Imported archives alone do not establish
native continuation; preserve one current entrypoint rather than updating both.

Apply source policy to decide whether any new change affects existing evidence.
Keep earlier results attributed to their actual subject. Unknown coverage stays
unknown; a handoff does not require a critical/full gate, whole-history scan,
hash inventory or proof that unchanged work was executed again.

The receiving agent must honor the prior authorization boundary. A handoff is
not permission to change the model/provider, use credentials, push, integrate,
publish, install or close an Issue. A pending owner-sensitive decision blocks
only the work that depends on it.

## Transport and completion

If transport is authorized, record whether the checkpoint was pushed or merged
and the exact resume branch/action. After a checkpoint merge, create a
continuation branch from the updated target before further material edits.
Unfinished work remains unfinished; transport and local workflow completion
are separate from PR integration, Issue/Project closure and publication.

## Historical context — NOT AN EXECUTION TRIGGER

The [earlier handoff contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/standards/WORKFLOW-HANDOFF-POLICY.md)
and retained YAML describe legacy checkpoint/critical-gate records. They do not
select a current command or mandatory template. Do not load them for ordinary
handoff. An explicitly selected legacy/release recovery obligation retains its
compatible revision and evidence requirements; missing tooling stays unavailable.
