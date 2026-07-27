# Portable Branch And Integration Policy

This target-facing policy defines a provider-neutral branch lifecycle. The
target repository owns its integration branch, review mechanism, merge method,
protection rules, and permissions.

## Branch-First Execution

- Start authorized workflow work from the target's configured integration
  branch.
- Create a bounded short-lived branch before workflow artifacts or material
  edits.
- Record the branch and base branch in the workflow locator and plan.
- Commit coherent validated stages; a push or integration event before
  completion is a checkpoint, not workflow closure.
- After integration, verify the target branch separately and do not claim
  publication or release completion from integration alone.

## Handoff And Customization

A push-only handoff resumes from the pushed workflow branch. A workflow that is
integrated before completion resumes on a new continuation branch from the
updated target. Cross-session or cross-runtime continuation must retain an
executable checkpoint.

The framework does not choose a branch name, hosted provider, review UI,
required reviewer, merge strategy, or automation for a target. Those settings
are target-owned customizations and must be preserved or reconciled during
installation and upgrade.
