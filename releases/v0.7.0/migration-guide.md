# Migrate To v0.7.0

## Supported Sources

Automatic upgrade and reviewed reconciliation support only the exact published
v0.6.0 package inventory. Use that package's `metadata/files.yaml` with
`--previous-version v0.6.0`. Targets on v0.5.0 or older must first follow their
published migration route to v0.6.0. A target without credible component-aware
provenance requires manual reconciliation and is not an automatic upgrade.

## Before You Start

1. Use Python 3.11 or newer and install the exact source dependencies when
   running source-side validation.
2. Start from a clean target worktree and record its current commit.
3. Obtain the exact published v0.6.0 `metadata/files.yaml` and verify the
   v0.7.0 archive against its adjacent checksum before extraction.
4. Review target provenance, semantic customizations, provider selection,
   integration branch, review policy, merge policy, and local changes.

## Migration Steps

1. Extract the v0.7.0 package outside the target repository.
2. Run `plan-ai-context-package-apply.py` in its default dry-run mode with the
   extracted package root, target root, exact v0.6.0 files manifest, and
   `--previous-version v0.6.0`.
3. Review every operation and reconcile locally changed target-owned or
   target-template content. The three portable policy targets are managed by
   framework bytes only when their exact previous-release hashes still match.
4. Acknowledge every required reconciliation explicitly, then apply from the
   same clean starting commit. Do not enable a provider merely to complete the
   framework upgrade.
5. Review `.dev/AI-CONTEXT-APPLY-PENDING.yaml`, then run `ai-context-init` for
   a clean installation or `ai-context-upgrader` for an existing v0.6.0 target.
   Finalize provenance only after target validation succeeds; the package apply
   receipt does not claim that later step.
6. Run the installed target AI-context, workflow, package, and applicable
   project-owned validation commands. Preserve blocked, skipped, deferred, and
   not-applicable outcomes as distinct from passed checks.

## Clean Installation

For a clean target, apply the default `dotnet-backend` profile in dry-run mode,
review the plan, and then apply from a clean Git worktree. The optional
`repo-backlog` provider remains disabled unless the target owner separately
selects it. No GitHub Issue or Project resource is created.

## Scope Boundaries

- Target work-management state remains usable without a tracker, and tracker
  provider choice remains replaceable and target-owned.
- Existing target modifications enter reconciliation rather than being
  silently overwritten.
- Source workflows, assessments, backlog items, roadmap, release history, and
  source-local GitHub policy are excluded from the downstream payload.
- The upgrade does not migrate historical source evidence, retire deprecated
  identifiers, simplify standards, or adopt GitHub Issues or Projects.
