# Subsequent coordinator dependency update

This addendum preserves the original 94741016bd7baae9936bb77dd6c4f56d37036e97 inventory. It is not a merge, an amended source snapshot or new execution evidence. [Exact read-back](../../../workflows/2026-09-23-capability-consolidation/evidence/dependency-update.json) records Git blobs and parsed members.

## P3 integrated mapping

Coordinator supplied ac4175948045590d1a1942022435ab438ad30ac3 (PR #343). Direct Git read-back confirms five component mappings, **44 exact members**, and four profiles: lesson-minimal, knowledge, work-management, collaboration. No src/skills source changed between the #342 baseline and that commit. The coordinator reports #334/#337 CLOSED/Done; #342 did not independently reread those provider states. Earlier text about missing P3 mapping is explicitly the baseline observation, no longer the coordinator's latest integration state. Build/install/runtime checks remain deferred.

## P4 selected, source not delivered

Coordinator selection is 9aa93ff4b9df396d28d0a9ae1bd2dd24715e05c0:.dev/design/framework-next/p4-selected-contract.md; retained design is 7f821ee866e7e54e551036785e19dffaa3d7ac39. The selected package is software-development-orchestrator@0.1.0, metadata/config v2, one project-owned software-development-orchestrator.record@1.0.0. Ten members and ten public operations are listed in dependency-update.json. Expected source root is src/skills/software-development-orchestrator/; installed members would preserve relative paths beneath .ai/core/skills/software-development-orchestrator/.

The planned scripts/workflow.py owner will read inspect/query/resume/render/retention-preview, write create/checkpoint/transition/retrospect, and expose explain. Its owned schema/lifecycle validator is not delivered source at this observation. Unknown record versions and legacy import/conversion remain unsupported; preserve originals. This is a selected additional schema, **not** a seventh actual schema resource or sixth implemented package in the baseline inventory.

Composition is semantic candidate handoff only, empty dependencies, no foreign invocation/private import. Retention previews do not delete/schedule, purge never says safe-to-delete; completed-with-deferrals does not claim validation/approval/provider completion. Retention/resume operational defaults (30/90/null days, 12000 characters) have the owned executable as sole operational authority and documentation as its description. Existing metadata-v2 store/template fields stay unchanged. P5's optional v3 proposal is not needed by this selected P4 contract and does not rewrite it.

The F08 group has a selected workflow successor but no automatic equivalence between its eight legacy kinds and the new record. External execution facts/receipts remain separately owned observations, not invented by workflow checkpoints. #341 keeps exclusive workflow source ownership; coordinator owns integration and mapping after actual delivery.
