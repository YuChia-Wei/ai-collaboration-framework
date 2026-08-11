# AI Context Releases

This directory stores durable release identities, compatibility declarations, and migration guidance for the reusable AI context framework.

Start with [INDEX.MD](INDEX.MD). Follow the source-only [AI Context Source Release Policy](../standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md) for framework version-candidate preparation, release-source status, tag handoff, hosted publication, and hosted finalization validation. Target provenance and upgrade safety remain owned by the portable [AI Context Version Policy](../standards/AI-CONTEXT-VERSION-POLICY.md).

Each version directory owns one `release.yaml`, `release-notes.md`, and `migration-guide.md`. Historical published records are immutable except for clearly identified factual corrections; candidate records remain editable until integration. From v0.12.0 onward, the integrated and tagged `status: validated` record is terminal source truth and is not rewritten after hosted publication.

For a new governed release, instantiate the placeholder-only files in
[`release-publication`](../../.ai/assets/skills/ai-context-governance/templates/release-publication/).
Never copy a previous version directory, its run IDs, timestamps, commit SHA,
or validation text. Each version directory owns its
`release-phase-checks.yaml`; use its exact commands and the publication runbook
before asking the user to create an annotated tag. Historical contracts remain
with their release so their original gates can be revalidated without changing
the next release.

Active upgrade testing starts from the retained `v0.6.0` baseline. Each later
governed package declares one automatic source: the immediate previous governed
package. Breaking releases are migration checkpoints and cannot be crossed by
an automatic-upgrade claim. Older release records stay immutable, but routine
candidate gates do not rebuild their full historical source matrix.

`release-notes.md` is authored source. Generated GitHub Release automation
markers and provenance are renderer output and must not be committed to an
authored notes file.

For v0.7.0 through v0.9.0 candidates, `release.yaml.planning.backlog_refs`
matches the accepted canonical backlog set. From v0.10.0 onward,
`planning.github_issue_refs` binds Included Work to online Issues; v0.11.0 and
later require those implementation Issues to be closed as completed before the
candidate is valid. From v0.12.0 onward, `provider_reconciliation` also binds
the exact prepublication and postpublication Issue/Project fields. The renderer
appends one generated `Included Work` section per reference while preserving
human-authored notes. Missing, duplicate, unrelated, incomplete, or
provider-mismatched references fail closed. Historical release records and
notes retain their original contract and are not rewritten.

Do not store workflow progress, assessments, or target-repository override details here.
