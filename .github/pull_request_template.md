<!--
Dormant source-form preview; not adopted or effective.
See .dev/standards/SOURCE-DEVELOPMENT-POLICY.md. The current form below remains
applicable with U001; this comment activates no replacement or CI requirement.
A later adopted source form would ask for scope and owner authority, actual checks
and their limitations/deferrals, conditional independent review/native evidence,
and each Issue's final or deferred disposition with next gate/owner.
The owner must adopt the exact replacement and applicability before changing the
active receipt/declaration checklist. No empty evidence section is required by
this preview, and no current checklist is removed.
-->

## Summary
- What change is being introduced and why?

## Changes
- Key changes (services, projects, endpoints, contracts)

## Related Issues
- Issue #:
- Delivery disposition: `terminal-close` / `deferred`
- Reference: `Refs #` for deferred, or one approved closing keyword for terminal-close
- `closure_deferred_reason` (required for deferred):
- Next terminal gate or owner (required for deferred):
- Owner authorization or approved no-Issue exception:

Repeat the fields above for every named Issue. Mixed dispositions are allowed.
A closing keyword records terminal intent; it never authorizes work.

## Delivery And Integration
- Delivery grouping: single work item / cohesive multi-Issue delivery
- Execution record: direct / assessment / workflow
- Selected topology: linear / merge commit
- Topology reason:

## Screenshots / Evidence (optional)
- e.g., Scalar UI, Kafka/RabbitMQ UI, console output

## Checklist
- [ ] Selected repository-native build and test commands pass, or `not-applicable` is explained
- [ ] Target-owned .NET commands were run only when this repository selected a .NET SDK/project contract
- [ ] Docs updated (README/AGENTS.md, comments)
- [ ] No secrets committed; config via env vars
- [ ] Every named Issue has exactly one validated delivery disposition
- [ ] The repository's target-owned review gate is satisfied (this source repo uses a content-addressed single-maintainer audit receipt plus current-head binding)
