# Backlog Provider Adapters

This source-repository-only directory defines projections from the portable
durable backlog into optional external work-management providers.

## Authority Boundary

- `.dev/backlog/items/*.yaml` owns durable outcome, priority, lifecycle, and
  release truth.
- `.dev/backlog/ROADMAP.md` owns release horizons, gates, and handoffs.
- `.dev/workflows/` owns authorized plans, execution tasks, validation evidence,
  commits, and resumable checkpoints.
- A provider Issue may summarize an outcome and collect community feedback. A
  provider Project may project priority, state, owner review, and release views.
- Neither an Issue nor a Project card authorizes workflow execution. Provider
  unavailability must not block repository work.

Provider-specific identifiers, fields, labels, read-back results, and repair
state belong in `.dev/backlog/provider-mappings/`, not in portable backlog
items. A future Azure DevOps adapter can project the same semantics without
reusing GitHub node IDs or field identifiers.

## Story Pack Projection

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

## GitHub Stage Boundary

[`github.yaml`](github.yaml) is the approved Stage A declaration. The Stage A
adapter is deliberately read-only: it renders and validates a migration plan
but exposes no provider mutation operation. Online Stage B work requires:

1. the Stage A pull request merged to `main`;
2. a fresh dry-run from that immutable `main` revision; and
3. explicit owner approval for the exact preview.

Successful Stage B writes must be read back and recorded immediately in the
mapping receipt. Never delete migrated Issues to simulate rollback; stop the
current batch and correct the recorded provider item in place.
