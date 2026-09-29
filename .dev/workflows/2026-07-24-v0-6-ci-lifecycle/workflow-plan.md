# v0.6.0 GitHub Workflow And Release Lifecycle Contracts

## Workflow Metadata

- `workflow_id`: `2026-07-24-v0-6-ci-lifecycle`
- `workflow_kind`: `ai-context-maintenance`
- `owner_skill`: `ai-context-governance`
- `branch`: `codex/2026-07-24-v0-6-ci-phase-contract`
- `base_branch`: `codex/2026-07-24-v0-6-config-skill-transition`
- `branch_segment`: `2`
- `status`: `completed`
- `current_phase`: `completed`
- `artifact_root`: `.dev/workflows/2026-07-24-v0-6-ci-lifecycle`
- `created_at`: `2026-07-24T10:00:00+08:00`
- `updated_at`: `2026-07-24T13:35:00+08:00`

## Objective And Scope

- Execute `CI-001` and `CI-002` as one release-engineering workstream.
- Upgrade artifact actions to verified Node.js 24-native majors while preserving
  transfer semantics.
- Enforce the exact trigger, permission, concurrency, responsibility, cost, and
  mutation matrix for every active GitHub workflow.
- Remove stale concrete release literals from general governance.
- Preserve historical version-specific phase truth and give v0.6.0 its own
  independently addressable phase contract.

## Decision Boundary

The owner approved version-scoped phase contracts on 2026-07-24. The canonical
path is `releases/<version>/release-phase-checks.yaml`; the release-state
validator and release handoff checkpoint both resolve the selected stable
version and fail closed on missing, mismatched, or unsanctioned contracts.
Hosted warning-free artifact and concurrency evidence still requires a pull
request and an authorized publication rehearsal or real release.

## Stages

1. Apply the locally decidable workflow matrix and Node.js 24 action majors.
2. Add fail-closed static lifecycle contract tests and runner registration.
3. Record the release phase-contract and hosted evidence boundary.
4. Implement and locally validate version-scoped phase contracts.
5. Push the continuation branch with a durable handoff checkpoint.
6. Collect the authorized integration pull-request evidence and transfer
   candidate/tag execution evidence to the release-publication lifecycle.

## Branch Segments

| Segment | Branch | Base | Purpose |
| --- | --- | --- | --- |
| 1 | `codex/2026-07-24-v0-6-ci-lifecycle` | `codex/2026-07-24-v0-6-eval-deterministic` | Static four-workflow lifecycle and Node.js 24 action migration. |
| 2 | `codex/2026-07-24-v0-6-ci-phase-contract` | `codex/2026-07-24-v0-6-config-skill-transition` | Approved version-scoped release and handoff phase contract plus push checkpoint. |

## Closure

- `CI-001` and `CI-002` implementation is complete.
- PR #7 passed the read-only governance, Ubuntu quick, and candidate-discovery
  jobs with the accepted trigger and concurrency boundaries.
- The governed v0.6.0 candidate PR owns actual `upload-artifact@v7` execution.
- The user-created v0.6.0 tag owns actual `download-artifact@v8` execution and
  publication transfer verification.
- Those observations are release-phase evidence, not unfinished CI design
  work. See `reports/hosted-evidence-and-closure.md`.
