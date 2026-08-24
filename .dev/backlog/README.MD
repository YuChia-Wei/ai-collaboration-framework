# Frozen Historical Backlog

This directory preserves the repository backlog, ROADMAP, plans, provider
receipts, and legacy migration adapter as historical or release-compatibility
evidence. It stopped accepting current source-repository work-management and
release-planning updates on 2026-08-24 under
[`SOURCE-WORK-MANAGEMENT-001`](../standards/SOURCE-WORK-MANAGEMENT-AUTHORITY.md).

Current source-repository work lives in online GitHub Issues, with Project #3
providing current priority, status, owner-review, target-release, and
published-in views. Provider state alone does not authorize execution;
workflows own execution evidence and integrated `main` owns repository truth.

## Historical Ownership Boundary

- `INDEX.MD` is the frozen catalog snapshot for the 55 retained item records.
- `ROADMAP.md` is the frozen post-v0.4 release-planning record; its last
  recorded target is not a current release allocation.
- `plans/` preserves historical sources that informed that roadmap.
- `items/<item-id>.yaml` preserves one historical problem, priority, origin,
  acceptance boundary, lifecycle, and release record.
- `.dev/assessments/<assessment-id>/` owns durable observations and finding
  evidence; current source follow-up is selected through an online Issue.
- `.dev/workflows/<workflow-id>/` owns execution plans, tasks, evidence, and
  commits after work is authorized.
- `.dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml` owns the one active
  source GitHub binding and merge-reference configuration.

Do not create or update files here for new source work, refresh the frozen
Project snapshot, or infer current provider state from retained bytes. The
source-governance validator enforces the exact tracked path-and-byte freeze.

## Historical Item States

`open -> planned -> in_progress -> resolved`

These literals remain accepted only to validate retained item records. They are
not a current source work-management state machine.

## Legacy Item Identity

- Preserve an existing finding or decision ID when one already exists.
- Existing stable uppercase path-safe IDs such as `CTX-001` remain immutable.
- Do not allocate new local item IDs or files.
- Record full-date timestamps with an explicit UTC offset.
- Preserve `origin_refs`, `workflow_refs`, and `task_refs` so deferred findings
  remain traceable without copying workflow progress.
- Reference assessment findings as `<assessment-id>#<finding-id>` in
  `origin_refs`; do not copy the full assessment report into a backlog item.

## Legacy Release Metadata

Every backlog item records:

```yaml
release:
  target: "v0.5.0"   # or "unassigned"
  completed_in: null # set when the item reaches resolved
  published_in: null # set to the first release tag containing the resolution
```

- `target` preserves the release expectation recorded before the freeze.
- `completed_in` identifies the release train that accepted the completed work.
- `published_in` identifies the first immutable published version containing the
  resolution. It may remain `null` between completion and publication.
- A resolved item must set `completed_in`.
- For governed releases from v0.7.0 onward, all resolved items whose
  `completed_in` equals the version form that version's canonical included-work
  set. Candidate `release.yaml.planning.backlog_refs` must equal that complete
  set, with each item listed exactly once. A target assignment without resolved
  completion is not included work.
- When `published_in` is set, preserve Git ancestry evidence in the item when
  available.
- v0.5.0-v0.9.0 release validation continues to resolve these frozen records.
- v0.10.0 and later release scope uses online Issue references instead of local
  backlog refs.

The downstream provider-neutral `repo-backlog` capability remains available
through the public target template. This source-only freeze does not disable or
redefine a target repository's selected backlog provider.
