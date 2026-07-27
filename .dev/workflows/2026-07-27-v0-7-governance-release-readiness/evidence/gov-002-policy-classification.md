# GOV-002 Work-Management Portability Classification

## Evidence Boundary

- Source change: PR #10, merge commit
  `a01e53c2e5123fa9d973a379f1580d4dd055cb82`.
- Authorized scope: portability and package boundary only.
- Excluded action: no tracker resource, field, view, automation, mapping, or
  provider-adoption implementation is created or designed here.

## Classification

| Surface | Classification | v0.7.0 disposition |
| --- | --- | --- |
| Conversation, candidate, authorized execution, and integrated fact remain distinct states. | portable framework contract | Project through the target-facing workflow gate. |
| Workflow completion and repository integration are separate facts. | portable framework contract | Project through workflow, branch, and commit policies. |
| A tracker provider is replaceable and repository workflow truth works without one. | portable framework contract | Project without a provider default or identifier requirement. |
| `.dev/standards/WORKFLOW-GATE-POLICY.md`, `.dev/TEAM-GIT-FLOW-RULES.MD`, and `.dev/standards/GIT-COMMIT-POLICY.md` as used by this source repository. | source-only policy | Exclude these source bytes from the downstream payload. |
| Target tracker selection, integration branch, review mechanism, merge strategy, and provider identifiers. | target customization boundary | Preserve existing target choices and reconcile local changes; never overwrite them from source-local policy. |
| Actual provider adoption, hosted resources, fields, views, automation, synchronization, and backlog-to-provider ID mapping. | deferred provider-adoption concern | Owner-controlled future work; non-blocking for the portable framework contract. |

## Projection Contract

The distribution profile maps provider-neutral files under
`.ai/assets/shared/governance/` onto the canonical downstream policy paths.
The source-repository versions are explicitly source-only. This keeps current
source policy intact while preventing its provider and `main` integration
choices from becoming target defaults.

No future provider is selected by this classification. A target with another
provider or no provider retains an operable repository workflow, and an
existing target policy remains subject to normal managed-path reconciliation.
