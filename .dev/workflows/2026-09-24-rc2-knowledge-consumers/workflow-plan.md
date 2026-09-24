# S5C selected knowledge consumers

Issue [#407](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/407) is the accepted bounded scope under program #322. Source input is the integrated S1 contract and accepted S2 package declarations. The five direct consumers remain instruction-only with null configuration and optional knowledge.

## Acceptance status

| ID | Local source result | Limit / next action |
| --- | --- | --- |
| S5C-A1 | Five public skill IDs and operation IDs remain; metadata 4 and version 0.2.0 declare optional knowledge only in `knowledge_consumption`. Raw skill dependencies retain their original empty metadata-3 shape. | S3 derives typed component dependencies and integrates exact members; other 13 skills remain outside this worktree. |
| S5C-A2 | Seven operation methods name the fixed read-only `distribution.catalog.read_installed_resources` interface, exact inputs/return fields, selected filtering and raw-byte re-observation. | S3 implementation and actual reader use remain pending. |
| S5C-A3 | Knowledge, example and normative rule treatment, raw identity and target-owned authority limits are explicit. | Real target applicability and target gate remain separate S6/adoption evidence. |
| S5C-A4 | A compact transient status/resources/rules/authorities/coverage/diagnostics result is specified. | No durable record family or executable rule parser was added. |
| S5C-A5 | [Machine-readable S3 handoff](s3-consumer-handoff.json) contains exact changed-member raw SHA-256, size, mode, versions, operations, dependencies, consumption rows and the fixed S3 reader seam. | Shared manifest/catalog/presets and reader implementation remain S3-owned. |
| S5C-A6 | Direct YAML, UTF-8, resource-ID, link, Git and exact message checks are selected. | Product parsers, resource loading, actual use, installation/recovery, runtime, target gate, formal/legacy/hosted/CI stay `deferred-by-owner` under U001. |

## Focused S6 actual-use scenarios to select later

1. With source selection containing zero knowledge packages, invoke one common operation and show useful output plus explicit unavailable requested specialist coverage, without a source-tree content fallback.
2. With a real selected catalog/lock and binding in the target, invoke each of the architecture, review, test-design and implementation consumers on a bounded task. Observe only task-matching verified resources loaded and the transient result's exact identities.
3. Check an optional absent resource, stale authority hash, ambiguous selector and conditional rule separately. Preserve common work only when unaffected; prevent unsupported normative/specialist coverage claims.
4. In actual mq-lab use, preserve target-owned Inventory EF Core/Npgsql, Products/Orders Dapper, Orders-selected event sourcing, target testing conventions and existing rule/customization/route authority. The target gate and independent review remain distinct.

The initial `gh issue view` read failed because the CLI network proxy was unavailable; the GitHub connector then returned the full live #407 body. A direct resource-order check command had Python syntax error and was corrected; the later direct YAML/resource-order check succeeded. These preparation failures are retained as such.

## Resolved metadata contract defect

The provisional commit `8f2f16dc3c3f3d728c0d4470ace9471a6d7e4b0f`
incorrectly put typed knowledge rows under the five raw skill
`dependencies.optional` fields. The coordinator's fixed-commit comparison
found the mismatch: metadata 4 adds `knowledge_consumption` to the unchanged
closed metadata-3 shape, whose skill dependencies remain empty here. This
correction restores `{required: [], optional: []}` in every skill metadata
file. The S3 handoff now separates those raw fields from the typed optional
component dependencies that S3 derives from consumption rows. The earlier YAML
parse showed readability and resource IDs only; it did not prove this closed
metadata contract. No behavioral check ran.

The first seam edit used a following-section boundary that two review methods
did not have; diff inspection caught their removed method bodies before commit.
Their exact original suffixes were restored from the provisional commit, while
the new installed-knowledge section remained. Direct source comparison was
repeated afterward.

## Fixed S3 seam and delivery limit

The source instructions are bound to S3's fixed interface at
`15bca530ea9eb3cc429cd7be37acf0ba45031507`,
`.dev/workflows/2026-09-24-rc2-selected-distribution/s5-interface.md`.
It names the read-only `distribution.catalog.read_installed_resources(project_root,
expected_lock_sha256, authorities)`, complete verified lock-2 closure, exact
selected resource/binding/authority observations and raw-hash checks. Consumer
methods filter only task-matching resources, bounded-read the selected installed
bytes and re-observe lock/marker/authority hashes. Target owners retain semantic
applicability. This is static interface alignment; S3 code implementation and
actual invocation remain pending.

The bounded S5C instruction/metadata delivery is completed locally under U001.
Behavioral use, product parser execution, installation/recovery, runtime
discovery, target gates, formal/legacy/hosted/CI verification remain
`deferred-by-owner` to program #322 coordinator and selected S6/P7. The original
provisional commit is retained as a checkpoint; this correction carries the
fixed seam. First push, PR, merge and Issue/Project updates remain coordinator-owned.
