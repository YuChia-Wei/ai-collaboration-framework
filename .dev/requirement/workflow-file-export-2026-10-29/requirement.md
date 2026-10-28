# Current workflow file export

Source authority: owner-approved FILE-EXPORT slice in native workflow
`2026-10-29-workflow-stabilization`; online requirement
[#524](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/524).
Implementation, review, integration, publication and adoption remain distinct.

The owner needs complete current raw records from native SQLite and local-group
authority exported as readable `workflow.yaml`, `tasks/*.yaml` and document/
attachment files. Project schema/template identity must prevent custom legacy
fields from being silently replaced by a framework upgrade.

Acceptance:

1. Explicit native revision and group revision/configuration/authority CAS select
   a consistent current cut. Missing authority never falls back.
2. All metadata/task extensions, order, checkpoint/event/body fields and raw
   document/attachment bytes remain recoverable; exported projections and complete
   current-record sidecar agree. No summary truncation or inserted default data.
3. Fresh destination and complete preflight reject unsafe/overlapping paths,
   case/prefix conflicts, missing/extra/modified members and payload inconsistency.
4. Explicit project-owned schema/template selection pins paths, digests and profile
   identity, permits `.ai/project`, rejects managed resources, validates locally and
   fails on missing/drifted/incompatible resources. No discovery, writes or transforms.
5. Defaults may be explicitly copied to project scope. Upgrade does not overwrite
   project copies or silently reinterpret project `schema_version` values.
6. Existing complete backup/inactive restore/activation behavior remains separate.
   Readable export establishes no historical 0.6/0.9 compatibility, Git import,
   store migration, remote acceptance, release or publication.

Validation: focused native/group file export, CAS, byte preservation, source
immutability, copied schema/template selection, conflict/path/refusal, tampering
and recovery-archive regression tests; package member/operation closure checks.
