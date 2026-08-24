# Historical Backlog Provider Adapter

This source-repository-only directory preserves the 2026-07 local-backlog to
GitHub migration adapter for deterministic historical compatibility. It owns no
active provider policy and must not be used for current Issue or Project state.

## Retired Authority Boundary

- `.dev/backlog/items/*.yaml` and `.dev/backlog/ROADMAP.md` are frozen
  historical and legacy-release evidence.
- Live GitHub Issues and Project #3 own current work-management and roadmap
  views.
- `.dev/workflows/` owns authorized plans, execution tasks, validation evidence,
  commits, and resumable checkpoints.
- A provider Issue may summarize an outcome and collect community feedback. A
  provider Project may project priority, state, owner review, and release views.
- Neither an Issue nor a Project card authorizes workflow execution. Provider
  unavailability blocks current provider claims and never promotes local files
  to current truth.

The single active source provider configuration is
[`../../standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml`](../../standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml).
Provider-neutral downstream selection remains target-owned.

## Historical Story Pack Projection

The provider-neutral handoff uses these semantic inputs when a Story Pack is
available: stable `story_id`, kind, statement, outcome, acceptance criteria,
boundaries, priority, lifecycle, release intent, owner-review gate, related
work, and canonical evidence links. The GitHub adapter maps those semantics to
an Issue title/body/labels and Project fields. GitHub Issue numbers, node IDs,
close reasons, and Project item IDs flow only into the provider receipt.

The current historical migration performs the same normalization directly from
the 41 canonical backlog items because no separate Story Pack artifact exists
for them. It does not manufacture workflow tasks or persist a duplicate Story
Pack authority.

## Historical GitHub Stage Boundary

[`github-legacy-migration.yaml`](github-legacy-migration.yaml) retains only the
historical Stage A/B adapter metadata needed to reproduce the 2026-07 migration
plan. It is frozen with the 55 local item records and cannot serve as active
work-item binding, merge-gate, or provider-state policy.

[`provider-mappings/github-project-current.yaml`](../provider-mappings/github-project-current.yaml)
is a frozen point-in-time read-back from 2026-08-10. Never refresh it or use it
for a current provider-state claim; perform explicit live GitHub read-back.

The retained Stage A adapter is deliberately read-only: it renders and validates
a historical migration plan but exposes no provider mutation operation. Online
Stage B work requires:

1. the Stage A pull request merged to `main`;
2. a fresh dry-run from that immutable `main` revision; and
3. explicit owner approval for the exact preview.

Successful Stage B writes must be read back and recorded immediately in the
mapping receipt. Never delete migrated Issues to simulate rollback; stop the
current batch and correct the recorded provider item in place.
