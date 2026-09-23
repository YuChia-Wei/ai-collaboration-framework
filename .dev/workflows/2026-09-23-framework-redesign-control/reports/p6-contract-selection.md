# P6 design reconciliation and first source assignment

Received clean #345 checkpoint `8a479ddc3204d0f031d9b9844aeb933af26f36f7`, parent `51229b63565ce6e836d57a4b107cf6df5554bf7c`, same F:/framework-next/345 and branch. Ten original design/workflow files only. The coordinator read the revised contract, formats and cutover, preserving the initial proposal as history. Synthetic examples remain syntax-only non-admissible illustrations.

[Selected contract](../../../design/framework-next/p6-selected-contract.md) narrows the original invocation guard to quiescent maintenance. This avoids a mandatory runtime dependency for every skill while explicitly limiting concurrency guarantees. Full managed snapshots remain necessary for the selected whole-RAM-loss recovery guarantee; destination delta reduces destination rewrites but does not remove snapshot I/O. No performance or durability result is claimed.

The proposed generic compatibility selection is removed. Package maintenance observes managed bytes and explicitly selected protected hashes, while project owners separately decide config/data readiness. Unknown readiness is never converted into a pass. M01 remains a separately owned conditional edge and is not assigned absent real target need.

The coordinator additionally inspected actual assembly source: candidates emit only payload/runtime and three metadata documents; build-input/source/profile identities are provenance, not external source bytes. #354 must validate available internal bindings without claiming source authenticity/reproduction or silently fetching history. The actual #346 v3 loader is now online and can be consumed without another metadata parser.

#354 implements read-only state/plan in one independent Astra Ultra task. Later mutation/coordination/bootstrap form one coherent successor after that interface is delivered. No root adoption, engine execution, generic CLI rollout or converter is selected here. #345 bounded design is complete pending online integration; the program is not complete.

PR #353 online read-back at 10:06:56 +08:00: merged `07b83383de467928701c8905c6bb0d5e8da8b246`, remote main matches, #348 CLOSED/COMPLETED and Project Done, #346 OPEN/In progress, #341 OPEN. Empty check rollup is not CI success. Completed #348 worktree was clean, detached at its preserved checkpoint, and only the merged branch removed. #347 remains blocked by automatic approval review pending the direct confirmation already requested; no retry or substitute writer was used.

U001 allowed direct syntax/reference/Git and exact planned-message checks only. Product execution, schema validation, tests/trials, backend durability/locking, installation/recovery/migration, audit/lease machinery and CI remain deferred-by-owner, owner program #322 coordinator / P7. Missing native or failure-domain proof is not a passed gate.

Coordinator direct read-back: 22 UTF-8 files, 6 JSON, 2 YAML and 64 existing local references; no missing local references. No product import, function invocation or schema validation.
