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
- [ ] The repository's target-owned review gate is satisfied (this source repo uses an exact-head single-maintainer audit receipt)
