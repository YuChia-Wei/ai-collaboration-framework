# Migration To v0.0.1

`v0.0.1` is a retrospective source snapshot and provenance anchor, not an
installable distribution. There is no earlier governed version to migrate from.

Do not initialize or downgrade a target by copying the `v0.0.1` tag tree. New
installations must use a published governed package.

For a repository historically derived from commit
`ac2e2937b5209ece93e104c4a389a15e164c0d1b`, preserve a rollback commit and
inventory the actual installed files before treating the tag as a comparison
base. If that selection cannot be proven, record unresolved provenance and use
manual reconciliation. Never infer managed-file ownership from path equality
alone, and never import source workflows, backlog, requirements, root identity,
or other source-repository lifecycle state into the target.
