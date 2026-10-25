# Workflow Artifact Policy

The [source development policy](SOURCE-DEVELOPMENT-POLICY.md) owns validation
and evidence selection. This policy owns source workflow identity and minimal
records; it does not add test, receipt or admission gates.

This policy defines the repository-wide discovery and metadata contract for durable workflows. It does not define one universal plan, task, or report shape.

## Ownership Boundary

- Every skill that can create a workflow owns the templates and domain-specific layout it creates.
- A skill may define its workflow topic, task IDs, report set, and artifact root.
- The repository owns only the minimum discovery, identity, time, relationship, and lifecycle contract in this document.
- This source project owns its software-development workflow records and selected templates. Portable capability skills do not choose this source project's store. Other workflow kinds retain their project-selected owners.

## Workflow Discovery And Identity

Daily execution records use the selected native store and complete WorkflowRef
under [workflow storage](WORKFLOW-STORE-POLICY.md). No new Git locator is required.
The source project owns this selection; portable skills do not select a store.

Retain these workflow metadata fields in the native record:

- `schema_version` and the selected `lifecycle_contract`;
- immutable human `workflow_id`;
- `workflow_kind`, `title`, `owner_skill`, `status`;
- `created_at`, `updated_at`, `template_source`, `template_version`;
- `branch` and `base_branch` for current dedicated branch segments;
- `current_phase` and other template-owned progress/authority fields.

The native record's `entrypoint` names its current logical text document.
Preserve unknown metadata and the actual authority for execution. Required
field names and meanings must not be changed by a skill template.

### Legacy Git Discovery Locators

Existing `.dev/workflows/<workflow-id>/workflow.yaml` records retain their
original locator schema, `artifact_root`, timestamps and history. They are
historical provenance, not a required write destination for daily continuation.
An explicitly selected continuation follows the store policy's public native
creation and provenance procedure; no automatic migration or historical rewrite
is implied. A separately selected compatible legacy obligation retains its
original locator contract and verified route.

## Branch Metadata And Continuation

- Create the dedicated workflow branch before the current execution record or material workflow edits.
- The workflow branch must differ from `base_branch` and must not be `main` or
  another long-lived trunk.
- Default Codex naming to `codex/<workflow-id>`; use the active runtime or repository prefix when another convention applies.
- Keep `base_branch` as the integration branch from which the current workflow segment started.
- Treat `branch` as the current or most recent dedicated workflow branch. Update it when an incomplete workflow continues on a new branch after a checkpoint merge.
- Record push and merge handoff evidence in the plan or a skill-owned history field, including the resume source and action.
- A push-only handoff normally keeps the same branch; a checkpoint merge starts the next branch segment from the updated target branch.
- A checkpoint push or merge does not change `status` to `completed`; pending tasks and exact continuation instructions remain durable.
- Conversely, `status: in_progress` does not block an otherwise authorized push, pull request, or merge. Transport and workflow completion are independent facts.
- A historical active workflow without branch metadata must record it in its selected native continuation after creating the continuation branch; preserve the historical locator.

## Workflow ID

- Use `YYYY-MM-DD-<skill-owned-topic>[-<sequence>]`.
- The date is the local calendar date when the workflow is created.
- Keep the ID immutable after creation.
- Resolve a same-day collision with `-02`, `-03`, or a concise semantic suffix.
- A skill may define the topic and suffix but must preserve the sortable full-date prefix.
- Do not rename historical month-only workflows merely to conform. Preserve their paths and treat them as legacy artifacts.

## Artifact Root And Logical Documents

- Daily workflow metadata, task records, plans and progress reports live in the
  selected repository-external store, with logical document names and one current
  entrypoint. The entrypoint must lead to current progress, next work, blockers
  and deferrals without repeating repository analysis.
- Formal Git-owned artifacts keep their selected repository-relative paths;
  reference them from the native record with source provenance.
- Retain a legacy `artifact_root` as provenance for the original Git artifacts;
  it does not relocate the database or require a new Git execution tree.
- Do not store runtime workflow records inside managed skill resources, ignored
  scratch, generated/dependency directories or temporary locations. Use only the
  explicitly selected persistent store, not another repository-external path.
- Keep active workflow identities and their logical documents distinct. A
  document's source provenance does not make it a second current entrypoint.

## Time Metadata

- Use ISO 8601 / RFC 3339 timestamps with seconds and an explicit UTC offset.
- `created_at` is the actual artifact creation time and is immutable. It is not a Git commit timestamp.
- `updated_at` changes when content, status, ownership, artifact relationships, progress, or conclusions change materially.
- Formatting-only changes do not require a timestamp update.
- Derived artifacts such as translations have their own timestamps and a `derived_from` relationship. Creating a derived artifact does not update the canonical source timestamp.
- If a legacy timestamp is reconstructed, record `created_at_source: git-history | file-evidence | inferred`; do not present an inferred time as directly observed.

## Skill-Owned Templates

Every workflow-producing skill must declare its templates and defaults in its canonical skill spec. A template must include template metadata equivalent to:

- `template_id`;
- `template_version`;
- `template_created_at` and `template_updated_at`, or a clearly scoped Template Metadata section containing `created_at` and `updated_at`.

Artifacts generated from a template must record `template_source` and `template_version` when the format supports metadata.

The skill may define additional workflow, task, report, and status fields. Shared compatibility requires the selected workflow identity/metadata and the minimum task relationship fields below.

## Task Minimum Contract

Every durable task must include:

- `task_id`;
- `workflow_id`;
- `owner_skill`;
- `status`;
- `created_at`;
- `updated_at`;
- `template_source`;
- `template_version`.

For tasks created on or after `2026-07-27T09:52:09+08:00`, also require:

- `model` for the primary executing AI model;
- `reasoning_effort` for the primary executor's reasoning setting.

An unfinished task created earlier must add these two fields the next time it
is materially updated on or after the effective timestamp. Do not backfill a
completed historical task. Resolve values from the active session when
available; otherwise use the effective configured default after the client's
documented precedence, then its documented built-in default. Preserve the
reported or configured strings without cross-provider normalization. Additional
sub-agent contributors belong in marked Git trailers under
`GIT-COMMIT-POLICY.md`, not in extra task fields.

Task IDs are immutable, path-safe, and unique within the workflow. Use `<workflow-id>#<task-id>` for cross-workflow references. A skill may define its own task ID prefix and task body.

Use these shared lifecycle states when they apply:

```text
pending -> in_progress -> completed
```

Use `deferred` only with a recorded reason and handoff condition. Skills may add domain-specific states without redefining the shared meanings.

Workflow metadata from template version `1.2.0` or later selects
`lifecycle_contract: "1.0"`, including native continuations preserving that
selection. Under that prospective contract:

- an `in_progress` workflow has exactly one `in_progress` task;
- a `completed` workflow has no unfinished task and uses `completed` or `closed` as `current_phase`;
- a completed task has a non-empty result summary and an addressed finding status;
- legacy records without the field retain their original meaning and are not silently reinterpreted.

## Workflow Completion

`status: completed` means workflow completion only: every workflow-owned task
is terminal and the selected lifecycle contract is satisfied. The contextual
alias `workflow closeout` may be used inside this section, but it does not mean
repository integration, assessment finality, release-source validation,
hosted publication, or publication finalization. Evidence for any of those
separate events remains with its own owner.

A provider-only review, hosted check, admission, integration, or post-merge
read-back that creates no remaining workflow-owned implementation task does not
keep the workflow `in_progress`. Track that operation under its provider or
terminal policy. Do not create a tracked evidence-sync commit merely to copy a
later provider state into an already completed implementation workflow.

## Final and Derived Artifacts

- Do not silently overwrite a final baseline, review, or verification report.
- Correct a final artifact through an explicit reopen, corrigendum, addendum, or successor report.
- Record canonical-versus-derived relationships for translations and generated views.
- Preserve finding and decision IDs across remediation and verification artifacts.
- Preserve each work item's acceptance IDs, outcomes and relevant evidence in
  the existing record; one aggregate success flag is insufficient. Do not create
  a paired machine/human ledger or separate reuse, packet or lease artifacts
  for ordinary source work.

## Validation and Legacy Boundary

- New workflows dated 2026-07-10 or later must satisfy this policy.
- Historical workflows may retain month-only IDs and older layouts.
- When a historical workflow is explicitly continued, create its native continuation with baseline provenance under the store policy; preserve its original identity and Git history.
- Check changed workflow metadata/task fields, logical documents and status relationships directly,
  using an existing applicable validator if available. Do not scan all history
  or restore an unavailable validator solely to admit a new record.
- Validate `branch` and `base_branch` for workflows dated 2026-07-11 or later.

## Historical context — NOT AN EXECUTION TRIGGER

Existing terminal-anchor records retain their original meaning under the
[earlier artifact contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/ba28cdbc3d7001dfb101cacba5e8f71406919797/.dev/standards/WORKFLOW-ARTIFACT-POLICY.md).
Do not add those legacy contracts to ordinary workflows or execute their
historical validator instructions. Only an explicitly selected compatible
legacy/release obligation uses them; missing tooling remains unavailable.
