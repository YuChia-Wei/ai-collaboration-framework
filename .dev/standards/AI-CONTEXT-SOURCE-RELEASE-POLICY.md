# AI Context Source Release Policy

## Purpose And Distribution Boundary

This source-only policy owns framework release preparation, source record
validation, repository integration evidence, tag handoff, hosted publication,
provider reconciliation, and hosted finalization validation. It is excluded
from downstream packages. A target repository consumes an already published
framework version under the portable AI Context Version Policy; it never runs
this source release procedure merely because the framework is installed.

Published version identity and SemVer compatibility are defined by the
portable [AI Context Version Policy projection](../../.ai/assets/shared/governance/AI-CONTEXT-VERSION-POLICY.md).
This policy adds source-repository procedure and authority without redefining
that identity.

## Source Release State And Authority

Use the qualified terms below on first use. A bare alias is allowed only inside
the same clearly headed source-release section and never transfers authority
between rows.

| Qualified term | Meaning and authority |
| --- | --- |
| `framework version candidate` | A governed source release record and migration set being prepared before owner-controlled tag creation. It is not a package archive, migration category, hosted publication, or authorization to publish. |
| `release-source status: validated` | The terminal v0.12-or-later source-record value after required source gates pass. It is not hosted provider state. |
| `repository integration` | The reviewed change entering the configured integration branch under the Git policy. It does not by itself prove workflow completion, source validation, or hosted publication. |
| `hosted publication` | The user-created immutable tag has triggered the authorized hosted workflow and the Release/assets/provider state have been created and read back. It is not a later source status transition. |
| `publication validation phase` | The read-only hosted Release, asset, checksum, and provider-preflight gate selected by the machine literal `publication`. The phase name grants no mutation authority. |
| `hosted finalization validation` | The post-publication parity and provider-reconciliation read-back selected by the machine literal `finalization`. It is not workflow completion or a normal source closeout stage. |
| `historical/exception release closeout` | Read-only historical verification or a separately authorized records-only recovery when normal hosted automation cannot complete. It is never a normal v0.12-or-later source release step. |

The exact machine literals remain compatible:

- release-source status values include historical `planned`, `validated`,
  `published`, and `superseded` records according to their versioned contract;
- release validation phases remain `candidate`, `tag`, `publication`, and
  `finalization`;
- hosted/provider fields remain separate from `release.yaml.status`.

Changing those literals requires an explicit schema/version migration. Prose
qualification is not a machine-state rename.

## Framework Version Candidate Preparation

Each governed version uses `.dev/releases/<version>/`:

- `release.yaml`: machine-readable source identity, source status,
  compatibility, planning, and evidence locator;
- `release-notes.md`: authored changes, compatibility, validation, and known
  limitations;
- `migration-guide.md`: source-version-aware target migration actions;
- `release-phase-checks.yaml`: version-owned sanctioned validation commands.

Instantiate the placeholder-only release-publication templates. Never copy a
previous version directory, its run IDs, timestamps, commit, or observed
validation. A historical record created after its tag declares
`record_origin: retrospective` and does not imply that the record existed at
publication time.

From v0.10.0 onward the framework version candidate binds Included Work to
online Issues. From v0.12.0 onward the source record also declares exact
prepublication and postpublication provider reconciliation. Required included
work, compatibility declarations, migration guidance, and source gates must be
complete before the source record reaches `status: validated`.

## Bounded Upgrade-Test Horizon

`v0.6.0` is the retained baseline for active framework upgrade testing.
Published package and migration contracts before that baseline remain immutable
historical evidence, but routine source gates do not rebuild every older
archive or replay a Cartesian cross-version matrix.

For every governed package after `v0.6.0`:

- `compatibility.automatic_upgrade_sources` contains exactly the immediate
  previous governed package version, so the required automatic-upgrade gate has
  one representative route;
- a release with `compatibility.breaking_changes: true` is a migration
  checkpoint and its `minimum_source_version` is that same immediate previous
  version;
- earlier versions may remain named only as reviewed reconciliation sources;
  they do not add automatic-upgrade test routes; and
- clean installation, the one declared automatic upgrade, rollback, and
  target-owned reconciliation remain distinct evidence. Passing one never
  substitutes for another.

Supporting another automatic source is a new compatibility decision. It needs
explicit owner approval, its own bounded work item, and versioned policy change;
it is not inferred from a retrospective baseline or historical test.

## Repository Integration And Tag Handoff

Integrate through the topology selected by
[TEAM-GIT-FLOW-RULES.MD](../TEAM-GIT-FLOW-RULES.MD). Re-run the framework
version candidate and critical gates against the integrated commit. Repository
integration is evidence for the selected Git event; it is not hosted
publication and does not complete an unfinished workflow.

The user owns tag timing and version selection. The source pre-tag interface is:

```text
python .ai/scripts/prepare-ai-context-release.py --version <vMAJOR.MINOR.PATCH>
```

It validates the integrated `main` commit and prints an annotated-tag command;
it never creates, moves, recreates, deletes, or pushes a tag. Any later commit
to `main` invalidates the prepared command and requires a fresh pre-tag run.

## Source Release Validation Phases

Each exact command comes from the selected version's
`release-phase-checks.yaml` contract:

```text
python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version <vMAJOR.MINOR.PATCH>
python .ai/scripts/validate-ai-context-release-state.py --phase tag --version <vMAJOR.MINOR.PATCH>
python .ai/scripts/validate-ai-context-release-state.py --phase publication --version <vMAJOR.MINOR.PATCH> --hosted
python .ai/scripts/validate-ai-context-release-state.py --phase finalization --version <vMAJOR.MINOR.PATCH> --hosted
```

These are validation-phase literals, not a source status state machine and not
standalone mutation authorization. Candidate/pull-request automation may build
and retain evidence, but it must not receive the Project write credential,
create a GitHub Release, or mutate tags.

Pushing the user-created annotated release tag authorizes only the configured
tag-triggered hosted publication path. That workflow verifies the tag, builds
the package, publishes the Release assets and notes, and performs bounded
provider reconciliation with read-back.

## Terminal Source Record And Hosted Publication

Historical governed releases may retain `status: published` source records.
From v0.12.0 onward, the immutable tagged tree's `status: validated` record is
terminal source truth. Hosted publication and hosted finalization validation
produce workflow/provider evidence; they do not require a post-tag source
rewrite, records-only pull request, or lifecycle-only merge.

The annotated tag object and its resolved full commit are the publication
identity. Hosted Release state, provider receipts, and retrospective registry
records are supplemental evidence and never authorize tag movement.

## Historical And Exception Release Closeout

The source-only `ai-context-release-closeout` capability verifies historical
post-tag records or plans a separately authorized records-only exception. Use
it only when the immutable tag and hosted Release already exist and normal
hosted reconciliation cannot finish the historical or exceptional case.

Retryable credentials, Issue state, or Project state belong to hosted retry and
read-back. They do not justify a source patch. Normal v0.12-or-later completion
has no source closeout commit.

## Authorization Boundaries

Framework version candidate preparation, repository integration, tag creation,
push, hosted publication, provider mutation, historical exception recovery,
and downstream target upgrade are separate decisions. Evidence that one event
occurred never authorizes the next event.
