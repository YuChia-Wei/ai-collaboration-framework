# AI Context Releases

This directory stores durable release identities, compatibility declarations, and migration guidance for the reusable AI context framework.

Start with [INDEX.MD](INDEX.MD). Follow [AI-CONTEXT-VERSION-POLICY.md](../standards/AI-CONTEXT-VERSION-POLICY.md) for version selection, tag immutability, release lifecycle, target provenance, and publication gates.

Each version directory owns one `release.yaml`, `release-notes.md`, and `migration-guide.md`. Published records are immutable except for clearly identified factual corrections; candidate records remain editable until publication.

For a new governed release, instantiate the placeholder-only files in
[`release-publication`](../../.ai/assets/skills/ai-context-governance/templates/release-publication/).
Never copy a previous version directory, its run IDs, timestamps, commit SHA,
or validation text. Each version directory owns its
`release-phase-checks.yaml`; use its exact commands and the publication runbook
before asking the user to create an annotated tag. Historical contracts remain
with their release so their original gates can be revalidated without changing
the next release.

`release-notes.md` is authored source. Generated GitHub Release automation
markers and provenance are renderer output and must not be committed to an
authored notes file.

For v0.7.0 and newer candidates, `release.yaml.planning.backlog_refs` must
exactly equal the canonical backlog set accepted by that version: every
resolved backlog item whose `release.completed_in` equals the release version.
The renderer appends one generated `Included Work` section with each backlog ID
exactly once while preserving the complete human-authored notes. Missing,
duplicate, unrelated, unresolved, completion-mismatched, or prematurely
published backlog references fail candidate validation. Historical release
records and notes retain their original contract and are not rewritten.

Do not store workflow progress, assessments, or target-repository override details here.
