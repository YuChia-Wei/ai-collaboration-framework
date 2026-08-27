# v0.15.0 Release Publication

## Objective

Prepare the governed v0.15.0 source record, merge it to current `main`, create
and push the immutable annotated tag, allow the repository-owned tag workflow
to publish the GitHub Release, and verify the public assets and checksums.

## Authorization And Validation Exception

The repository owner explicitly authorized the complete v0.15.0 publication,
including branch push, pull request, merge, tag creation and push, hosted
Release publication, asset upload, and necessary provider reconciliation.

For this publication the owner directed that local syntax checks, focused test
suites, package validation lanes, full matrices, and performance runs not be
repeated. Previously executed results remain bound to their original subjects;
this workflow does not relabel them as fresh passes or canonical evidence reuse.

The remaining publication-safety checks are deliberately narrow:

- review the authored release notes and migration guide;
- construct the exact v0.15.0 archives and checksum sidecars;
- bind the canonical identity across release metadata and archive manifests;
- create one annotated tag that peels to the merged source record;
- allow one tag-triggered publication workflow run and one event wait;
- read back the stable GitHub Release, its exact four assets, checksums, tag
  peel, release body, and provider reconciliation state.

## Source And Provider Scope

- Base: fetched `origin/main@acb0cfc75f6331e376b1806fa7e4d7ffe143e769`.
- Included Work: #249, #250, #251, #252, and #253.
- Coordination: #254.
- All six Issues were read back as closed/completed with Project Status Done at
  workflow entry.
- Project `Target release` and `Published in` have no v0.15.0 options. The
  owner-approved provider contract therefore uses schema 1.1 and requires only
  the existing `Status: Done` field; no Project option is created or replaced.

## Identity Matrix

| Release range | Public package/archive base | Profile identity |
| --- | --- | --- |
| v0.14.0 and earlier | `ai-context-dotnet-backend-v{version}` | `dotnet-backend` |
| v0.15.0 and later | `ai-collaboration-framework-v{version}` | `dotnet-backend` |

The public v0.15.0 asset set is exactly ZIP, ZIP SHA-256, tar.gz, and tar.gz
SHA-256 under the new base. Historical public objects are read-only.

## Completion Meaning

The tracked source workflow completes when the exact release source candidate
and its route metadata are committed and ready for merge and the
owner-authorized tag. Publication completion itself is
proved only by live provider read-back after the immutable tag workflow; the
terminal source release record intentionally remains `validated`.
