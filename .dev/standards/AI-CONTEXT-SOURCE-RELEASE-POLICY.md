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
- `release-notes.md`: publication-ready authored changes, compatibility,
  validation, and known limitations;
- `migration-guide.md`: source-version-aware target migration actions;
- `release-phase-checks.yaml`: version-owned sanctioned validation commands.

From `v0.13.0` onward, authored release notes are phase-neutral. They do not
contain source candidate status, tag-handoff progress, pending publication, or
future hosted-reconciliation claims. Those mutable states belong to
`release.yaml`, workflow evidence, Issues, and Project state. Durable status
that consumers need after publication, such as beta, deprecated, withdrawn, or
support limitations, remains valid release-note content. Candidate review must
therefore review the publication-ready wording rather than a phase-specific
draft that becomes stale when the tag workflow succeeds.

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

## Exact Release Asset Promotion (From v0.16.0)

Logical `package_id` and `release_id` are labels. They never establish archive
byte identity. A `release-asset-admission/v1` record at
`.dev/releases/<version>/artifact-admission.json` binds the payload fingerprint,
selected-input fingerprint, original build commit, and the exact name, size,
SHA-256 and tracked path of all four ZIP/tar/checksum assets. Its
`artifact_set_id` is the SHA-256 of the canonical ordered name/size/digest list.
Each individual archive also has identity `sha256:<archive digest>`.

The asset lifecycle is `admitted-candidate` → `uploaded-draft` → `published`.
The admission stays immutable provenance. The latter states are separate
`release-asset-publication/v1` provider receipts, not edits to the admission or
release-source status. An owned draft may be retried with the same admitted
bytes. Different bytes require a newly reviewed candidate before publication;
an already published identity cannot be silently replaced. Historical candidate
archives with the same logical labels remain explicitly historical candidates.

From v0.16.0, `package-selected-input/v2` embeds one `release-package-input/v1`
projection. It preserves every top-level release field except `status`, `tag`,
`commit`, `tagged_at`, `recorded_at`, `created_at`, `updated_at`, and `validation`.
The release source-input entry hashes canonical compact sorted UTF-8 JSON of
that projection. Other source entries continue to hash raw Git blob bytes.
Planning allocation, provider requirements, compatibility, distribution and
unknown future fields remain identity-bound. An unknown projection version,
duplicate key, missing projection or package-contract disagreement fails closed.
Changing this boundary requires a new projection version. Releases before
v0.16.0 retain their original raw release-file identity and published proofs.

The complete current release record remains authoritative for phase, workflow
and provider gates. Identity admission never marks a planned record validated.
Freeze package-selected inputs while source acceptance is pending, build once
from a clean immutable preparation commit, and execute required archive and
target gates against those exact assets. Only after acceptance may source
status and validation evidence become validated. Fresh candidate gates still
check those complete current records and rebind the admitted source projection.
Lifecycle-only updates preserve asset identity; selected contract or payload
drift requires a new archive and affected execution evidence.

Retain the preparation commit's four exact assets under the version's
route-assets directory, then run:

```powershell
python .ai/scripts/manage-release-asset-identity.py admit --version v0.16.0 --ref <preparation-commit> --assets-dir .dev/releases/v0.16.0/route-assets/admitted --output .dev/releases/v0.16.0/artifact-admission.json
```

This creates an identity record, not proof of execution or approval. Execute the
incoming portable validator and each required direct origin edge against that
same archive, bind their matrix archive hashes, commit the evidence, and obtain
the applicable independent review. Candidate/tag gates compare the complete
selected source inputs and projected payload with the archive; history-only
commit changes retain build provenance without rebuilding. Any selected-input
drift blocks promotion and requires a newly validated candidate. All incoming
matrix edges targeting the release must bind the admitted ZIP digest and payload
fingerprint. Issue 272 supplies the actual v0.16.0 direct edge evidence.

Retain its actual terminal at `route-assets/actual/terminal.json`. The source
gate binds the admitted route archive and package source to that terminal and
checks the canonical executing runner digest, invocation and timing, all three
origin case sets, retained packet and decision identities, target command output
and receipts, before/after provenance and customization records, recovery state,
finalized readiness, semantic reconciliation, negative boundaries and exact
rollback snapshots. Missing or changed retained artifacts fail closed. A changed
runner requires fresh actual evidence. Candidate CI repeats
the actual v0.16.0 matrix against the unchanged staged archive.

Candidate CI and tag publication stage the tracked admitted assets unchanged.
Before publishing a draft, and again afterward, the hosted workflow downloads
the assets, compares exact bytes, and reads back provider name, size, SHA-256,
asset ID, release ID, tag, URL and state. Missing provider digest, unavailable
bytes, wrong identity or disagreement blocks. The publication receipt is a
retained hosted artifact; finalization repeats the fresh provider comparison.

Once published, governed route admission requires a fresh `provider` check with
the downloaded public assets and the same tracked admission. Candidate evidence
alone cannot attest publication. No later source closeout or archive rebuild is
needed. Public-body rendering may bind the final tag commit while the unchanged
archive keeps its original preparation-commit provenance.

Historical v0.15.0/v0.15.1 recovery is retained in the Issue 280 workflow's
`evidence/published-routes/` catalog and rebound matrix. Future routes select
those exact public ZIPs and origin manifests, preserving the old tagged matrix
and candidate archives as historical evidence. Both rebound archives must execute
their own portable validator and edge validator. Reused unchanged v0.14.0
segments retain their original receipt bytes and are not reported as re-executed.

## Bounded Upgrade-Test Horizon

`v0.6.0` is the retained baseline for active framework upgrade testing.
Published package and migration contracts before that baseline remain immutable
historical evidence, but routine source gates do not rebuild every older
archive or replay a Cartesian cross-version matrix.

For governed packages after `v0.6.0` and before `v0.16.0`, retain the historical
immediate-predecessor policy below, including the explicitly recorded
`v0.14.0` three-source exception:

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

From `v0.16.0`, owner-approved Issue 272 establishes three required direct
sources: `v0.6.0`, `v0.9.0`, and the immediate previous governed package. Declare
them in numeric order in `compatibility.automatic_upgrade_sources`; a breaking
release uses `v0.6.0` as `minimum_source_version`. Each origin must select exactly
one source-specific edge to the incoming version and execute its own migration,
semantic cutover, target validation, finalization and interruption recovery
against the same admitted incoming archive. Applying intermediate releases,
route-selection fixtures, or archive identity checks alone cannot satisfy this
acceptance. The migration guide exposes one direct entry point per origin and
preserves target-owned reconciliation decisions. Retained origins remain required
in later releases until an explicit owner-approved, versioned deprecation changes
this policy and its executable gates. Historical records and assets are immutable.

Supporting another automatic source or retiring a retained origin is a new
compatibility decision. It needs
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
