# S5 consumer local delivery review

Issue #407 / S5C-A1 through S5C-A6. Accepted local instruction/metadata delivery is b4dfe1cbc60193f3cb84b3ee8b427e871b063fdc from baseline 50adb657b388074e072c8a7ed15a93368a7ba149. Provisional 8f2f16dc3c3f3d728c0d4470ace9471a6d7e4b0f remains in history. Online integration, Issue closure and actual S6 consumption are separate and pending.

## Receiving checks and review

The coordinator compared immutable Git bytes for all 21 changed paths, confined to the five assigned skill roots and the producer workflow. All 17 changed skill member hashes/sizes/Git modes equal the handoff. The five packages are metadata 4/version 0.2.0 with configuration null. After excluding knowledge_consumption and the two version changes, every metadata-3 field equals the baseline; the seven operations remain unchanged.

All 34 declared resource references exist in the accepted S2 content declarations. Knowledge rows are optional, exact-version and sorted with unavailable semantics. Raw skill dependencies remain the original empty arrays. Independently derived typed knowledge dependency rows match the separate handoff component fields. The seven original operation bodies remain exact suffixes after the added protocol instructions. UTF-8, changed JSON/YAML parsing and Git diff whitespace checks passed.

A bounded read-only reviewer found no additional actionable semantic defects in the provisional methods and then reviewed the correction delta at the accepted commit against S3's fixed interface. It reused unchanged first-pass coverage, confirmed restored dependency shapes and the target-owned applicability boundary, and reported no actionable regression. The reviewer's Issue network read was unavailable; it used the pinned producer acceptance record. The coordinator independently read the exact live #407 body and accepted scope. This is static content review, not a formal audit or execution result.

The producer separately recorded direct local-link, sorted-row/resource, metadata-parity, method-body, Git and exact complete commit-message checks. Those are attributed to the producer; the parent checks above are independently performed comparisons. No parser, resource loader, builder, installer, recovery, runtime or target gate was executed.

## Preserved failures and corrections

The first parent comparison at 8f2f16d failed because raw skill dependencies.optional had typed knowledge rows. That changed the closed metadata-3 shape beyond S1's metadata-4 extension. The correction restores empty skill dependency arrays, retaining knowledge only in knowledge_consumption and distinguishing S3-derived component dependencies in the handoff. The parent reran the affected comparisons successfully at b4dfe1c; the initial failure is not a pass.

Producer preparation history also retains a provider proxy failure, a malformed direct-check attempt and an edit-induced loss of original operation text. The latter was repaired before the accepted commit; the parent independently compared all seven final bodies against the exact baseline suffixes. No failed or unexecuted check is represented as successful behavioral evidence.

## S3 integration handoff and limits

The [machine-readable handoff](../../2026-09-24-rc2-knowledge-consumers/s3-consumer-handoff.json) raw SHA-256 is 1d9a6bc06efd27dab6a29ead3082863fcf3fb1b72d27e7c17baf03919f550dbb. It includes exact members, five component versions, unchanged operations, raw versus derived dependencies and knowledge rows. The fixed S3 reader protocol is at commit 15bca530ea9eb3cc429cd7be37acf0ba45031507, producer path .dev/workflows/2026-09-24-rc2-selected-distribution/s5-interface.md. Its implementation remains in progress.

S3 alone integrates the shared manifest/catalog/presets and complete verified engine. Accepting these instructions does not establish actual loading, .NET coverage, source dogfood, target adoption or runtime discovery. S5 source/target adoption and S6 actual evidence remain pending. Under U001, legacy/formal/hosted/CI checks remain deferred-by-owner to program #322 coordinator/P7.
