# P3 actual package mapping continuation

Selected by the coordinator for the SAME Issue #337 independent task, under U001. Source input is the containing integration checkpoint supplied by full SHA in the dispatch. It includes #337 loader checkpoint 13a08f3c886513cead3bfea080224f3323131977, #335 corrected source 5409641f19244bc44467af7fba3fc496d7f5195c and #334 source 552e218d039245482ed422be7d4fb642d5463ff0. These are actual committed package bytes, not a proposal inventory or assembled candidate.

## Exact selections

Map metadata-derived exact members under the same installed suffix: src/skills/<id>/<member> -> .ai/core/skills/<id>/<member>. Five packages: lesson@0.2.0 (9 members), adr@0.1.0 (8), standards-promotion@0.1.0 (9), pr@0.1.0 (10), local-backlog@0.1.0 (8). Total 44 package members. Derive the actual list from these exact committed metadata/files and compare the two owned interface inventories; no directory glob or absent-file entry. Preserve the exact legacy Lesson schema and the existing Codex adapter.

Select profile_version 1 and adapter codex for each of four explicit profiles:

| Profile | Exact skill selection |
| --- | --- |
| lesson-minimal | lesson@0.2.0 |
| knowledge | lesson@0.2.0, adr@0.1.0, standards-promotion@0.1.0 |
| work-management | pr@0.1.0, local-backlog@0.1.0 |
| collaboration | all five versions above |

These convenience selections do not create mandatory skill dependencies or claim installed capability. Individual packages remain selectable through the existing exact manifest contract. Existing lesson-minimal changes to 0.2.0 intentionally; no claim that the new tool writes legacy v1 records. Profile names are selection IDs, not framework release identities.

## Owned writes and stopping boundary

#337 may update src/distribution/manifest.yaml, src/profiles/lesson-minimal.yaml and the three named new profiles, plus its existing distribution-implementation design and p3-distribution workflow. Preserve existing loader source. If actual mapping reveals a necessary code/shared contract change, return the exact discrepancy before changing that boundary. No package source, adapter, root runtime, install/core/custom, tests, CI or coordinator index edits.

The same task first verifies clean F:/framework-next/337 at its returned loader checkpoint, then fast-forwards its assigned branch to the supplied integration commit. No rebase/reset or second task/worktree. Complete exact static member/profile/reference comparison and coherent local commit, then return before first push. The Issue/workflow may complete its bounded source scope after this mapping delivery; coordinator owns provider closure and P7 owns verification.

No product tool invocation, even help/select/build, and no schema validator, fixtures, tests, package/install/migration trial, audit or CI. All remain deferred-by-owner under U001 to program #322/P7. Do not fabricate package digests, runtime projections, installed locks or a generated candidate. Readable YAML and exact source inventory are the allowed evidence.
