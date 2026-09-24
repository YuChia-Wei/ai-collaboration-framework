# S2 delivery to the coordinator and S3

`engineering-common@0.1.0` and `dotnet-backend@0.1.0` are optional content packages.
The exact [S3 handoff](s3-package-handoff.json) supplies package/member/resource/
dependency/reference rows and SHA-256 values from actual bytes. No manifest edit
or installation has occurred. Resolve this checkpoint's transport commit from
Git; the package bytes and their independent handoff hashes are the content pins.

| Package | Members | Resources | Declared references | Metadata bytes | Required knowledge |
| --- | ---: | ---: | ---: | ---: | --- |
| engineering-common | 6 | 5 | 6 | 4759 | none |
| dotnet-backend | 229 | 228 | 356 | 247347 | engineering-common@0.1.0 |

All 272 source inventory identities are checked against Git path/blob/mode and raw
size/SHA-256. The 194-file profile is fully reconciled: 185 portable files, 5
excluded historical evidence files and 4 obsolete forwarders. The remaining
portable sources come from the explicitly assigned reusable reference closure.
232 members are source-derived; the common README and both metadata files are
explicitly new. All C# example/source-include bytes remain unchanged.

The 381 original edges retain their original disposition provenance: 287 declared
installed references, 53 retained-authority/provenance dispositions, 24 role
projection dispositions and 17 excluded-source edges with no installed consumer.
Additional actual links and index navigation are declared. The README uses topic
entrypoints; the full member/resource inventory remains in metadata. YAML contains
no anchors/aliases/merge-key compression and remains below the S1 256 KiB cap.

All 14 registered IDs retain normative meaning, strength, scope, applicability,
override policy and target evidence ownership. Exact link/target-parameter deltas
and both normative hashes are in [normative-rewrites.json](evidence/normative-rewrites.json).
The .NET catalog text matches the relocated Markdown owner sections. The 11
unregistered guidance rows retain their state; stale catalog digests are inert
provenance, and current hashes use actual relocated bytes. Source history under
provenance keys is not a loadable dependency or target adoption.

Legacy role declarations become technical guidance with no trigger, routing,
workflow or runtime activation fields. Target-authority markers are descriptive
inputs to existing target owners, not a new resolver protocol, file fallback or
executable command. Examples and source includes stay inert until separately
selected target adoption and execution.

## Direct checks and limits

The Issue-owned `check-content.py` performs UTF-8 and JSON/YAML syntax reads,
source identity/member/hash/mode comparisons, installed Markdown link/anchor and
declared resource/dependency comparisons, exact normative substitution checks and
catalog/owner digest comparisons. See [direct-checks.json](evidence/direct-checks.json)
and [preparation-history.json](evidence/preparation-history.json). This is direct
static evidence only, not schema compliance, independent review, behavioral
acceptance, SDK compatibility, installation or CI success.

All legacy/formal/critical/full, installation/upgrade, hosted/CI and behavioral
consumption checks remain `deferred-by-owner`: U001, program #322 coordinator / P7
and selected S5/S6. Next action is S3 integration followed by those separately
selected checks and target authority reconciliation. No unresolved member addition
or normative semantic decision is required by this bounded content delivery.

## Receiving action

1. Verify the local branch/commit and the exact package bytes against the handoff.
2. Review only this Issue's owned paths and accept the content checkpoint.
3. Give S3 the exact handoff rows for serialized shared manifest/reader integration.
4. Keep S5/S6 target binding/behavioral and P7 verification/CI decisions explicit.

The executor stops before first push. Integration, Issue closure, Project state,
CI restoration, tag/Release and publication remain separate coordinator decisions.
