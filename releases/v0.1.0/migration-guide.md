# Migration To v0.1.0

`v0.1.0` is the first historical source snapshot and provenance anchor, so there is no earlier governed source version to migrate from. It is not an installable distribution package.

Do not initialize a new target by copying the `v0.1.0` tag tree. Use the latest published governed package; until one is published, use an explicitly reviewed allowlist and treat the result as an unreleased framework import.

For a repository already derived from `v0.1.0`, use tag commit `69c285077708dfb96ee49bb39258aec83eb7f1a9` as a comparison base, not as a whole-tree desired state. Preserve target truth, exclude source requirements, backlog instances, workflows, assessments, release history, and source root entries, and reconcile local changes before recording provenance.
