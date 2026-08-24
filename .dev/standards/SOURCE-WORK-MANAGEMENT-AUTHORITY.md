# Source Work-Management Authority

Rule ID: `SOURCE-WORK-MANAGEMENT-001`

This source-repository-only policy separates current provider state, repository
execution evidence, integrated Git truth, and frozen historical planning
records. It does not replace the provider-neutral work-item binding capability
or target-owned `repo-backlog` selection distributed by the framework.

## Current Authority Boundary

- Live GitHub Issues own candidate, approved, authorized, in-progress, and
  completed source-repository work-item state.
- Live GitHub Project #3 owns current priority, status, owner-review,
  target-release, and published-in views.
- `.dev/workflows/` owns authorized execution and validation evidence.
- Integrated `main` owns repository-integrated truth. A branch, workflow,
  Issue, Project field, commit, or pull request is not integrated truth by
  itself.
- Provider state alone never authorizes execution. The applicable online Issue
  must also contain explicit owner authorization.

The single active provider configuration is
[`GITHUB-WORK-MANAGEMENT-POLICY.yaml`](GITHUB-WORK-MANAGEMENT-POLICY.yaml).
Ordinary deterministic validation reads tracked repository files and requires
no ambient GitHub credentials. Any claim about current Issue or Project state
must perform an explicit live read-back; provider unavailability blocks that
claim and never promotes a repository snapshot, backlog item, or ROADMAP to
current truth.

## Historical And Legacy-Compatibility Boundary

The tracked `.dev/backlog/` tree is frozen historical and legacy-compatibility
evidence. Its 55 item records, ROADMAP, planning sources, mapping receipts, and
the renamed historical GitHub migration adapter retain their paths or explicit
compatibility replacements so old links and release evidence remain
deterministic. They do not accept new source-repository work, priority,
lifecycle, authorization, or release-planning updates.

`.dev/backlog/providers/github.yaml` is retired and must remain absent. The
2026-07 adapter bytes that still support historical migration verification are
retained only as
`.dev/backlog/providers/github-legacy-migration.yaml`; that file is not an
active provider policy.

The executable freeze and compatibility projection is
[`SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml`](SOURCE-WORK-MANAGEMENT-AUTHORITY.yaml).
Its deterministic validator rejects tracked path or byte drift in the frozen
tree, a reintroduced retired provider path, prospective workflow bindings to
local backlog items or ROADMAP, or release-scope regression across the
v0.9.0/v0.10.0 boundary.

## Release Compatibility Boundary

- v0.5.0 through v0.9.0 retain their exact
  `release.yaml.planning.backlog_refs` and resolve them against frozen local
  item records.
- v0.10.0 and later use online Issue references for release scope and must not
  introduce `planning.backlog_refs`.
- Historical receipts, failures, blocked evidence, and authored release notes
  keep their recorded outcome and wording; this policy does not rewrite them
  as current or passed.

## Prospective Rule

New material source work starts with an authorized online GitHub Issue and, when
the workflow gate applies, a dedicated workflow branch and workflow artifacts.
Do not create or update local backlog items, use ROADMAP as current planning,
refresh the frozen `github-project-current.yaml` receipt, or fall back to local
planning because GitHub is temporarily unavailable. Physical archive deletion
or compaction requires a separate owner-authorized migration.
