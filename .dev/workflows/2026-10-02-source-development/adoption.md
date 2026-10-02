# Exact source adoption proposal

Status: pending owner decision. This document records a concrete proposal, not
approval, independent review, CI success or downstream adoption.

## Requested boundary

Adopt SOURCE-DEVELOPMENT-POLICY for newly authorized ordinary source development,
including conditional independent review for authority/security/publication/
installation/recovery changes. Retire automatic ordinary use of the unavailable
artifact_core/receipt/packet/lease/aggregate machinery. Preserve all selected
release/support/recovery and active legacy obligations. No support code deletion.

For this cutover only, authorize an independent read-only review of the exact
policy/root/YAML/template/selector/workflow diff without the unavailable legacy
preflight packet. Record immutable source, reviewer, findings and disposition.
The cutover cannot approve its own lower standard; this explicit owner bootstrap
decision is needed before treating that review as adoption evidence.

After that review and focused checks, enable only Source checks (workflow ID
364914272). Use Windows, Python 3.13 and tests/requirements.txt. Retain the two
already active release workflows; the other six remain disabled. Keep all
repository permissions, credentials, environments, protection and rulesets as
observed. Push/PR transport needed to observe this exact hosted head is included
in the proposed activation; merge still requires its actual checks and review.

The effective scope/date and owner response will be recorded here before the
candidate policy/configurations are called adopted. First hosted result and
integration are later read-backs, never inferred from that decision.

## Concrete effect

- Root English/Traditional Chinese instructions route new source work to the
  eight source rules; full legacy mechanisms remain only for selected old work.
- GITHUB-WORK-MANAGEMENT-POLICY version 2 uses Source change gate and conditional
  scoped review. Historical version 1 remains in Git; old validators do not read
  version 2 as a compatible receipt contract.
- AI-CONTEXT-SOURCE-EFFECTIVE-RULES version 2 names current policy owners directly.
- PR form captures authority, checks, conditional review and per-Issue intent.
- Selector validates changed source workflow relationships without one-Issue
  whitelists and keeps unknown executable ownership blocked.
- #274/#275 can be cancelled as superseded scope, with no performance claim.
  #425 can close as completed after its accepted merged evidence; Project state
  will be read separately. The owner removed actual skill evaluation from scope.

## Alternatives and limits

Keeping the legacy ordinary gates would require restoring their removed module,
skill and registry dependencies and their validation scope. A standing merge
waiver would retain the original contradiction. The proposed scoped replacement
is the previously designed #369 direction, now tied to actual current tests.

No Linux support, native install/recovery acceptance, general skill quality,
release publication, or full P7 completion follows from this cutover.
