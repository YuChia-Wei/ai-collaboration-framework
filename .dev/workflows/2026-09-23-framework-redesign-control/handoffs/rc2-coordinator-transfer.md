# RC.2 coordinator continuation

## Current owner-selected checkpoint — 2026-09-29

Source PR #412 integrated at source main `31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`;
checkpoint PR #413 was read back integrated at source main
`26e18c178b74b2db5e10aa2a9443cd7aa58325b9`. Annotated tag `v0.19.0-rc.2`
remains fixed at product commit `aad927328c20b08c8445e8ad1792eadd8ecc3466`
(tag object `0f6118554f1573d835faf67aaa418dd291dd01d1`). Issue #409, source
Issue #411 and mq-lab Issue #22 are CLOSED/completed. MQ PR #24 is merged at
`179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; `main` matches that commit, and
the primary checkout is clean. Closeout comments: #411
(https://github.com/YuChia-Wei/ai-collaboration-framework/issues/411#issuecomment-5884545394),
#22 (https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/22#issuecomment-5884545150),
and #409
(https://github.com/YuChia-Wei/ai-collaboration-framework/issues/409#issuecomment-5883082732).
Future admission gate #23 remains open; program Issues #322 and #369 remain open.

Direct user approval resolved the earlier automatic-review block for the nine
authority URL corrections and forty binding rebind. Official API2 applied subset
`subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:8e0eb8909b9a110b86398ed3f1a87d262b0691ddccdf63e7d49689a864556b71`; the new
lock is `be0cba5c82425c1fc67755b65b7956c6333d8205f637f4cb3e48e6c45f907223`.
API2 reported 384 managed members unchanged, one installation-selection change,
and `managed-bytes-consistent`. Direct target raw hashes matched the lock, the
selection (`4d74012367bd1ec4a5aedb2ed7b923880c315dd7492d32559be88f101af3a5a3`),
and corrected authority (`e46c6527b6cb7bf9cd9ef5c3cb19c0f9e36c38dd8ecdeda546c5c273b87d4c08`). The selection has 18 skills, two knowledge packages, both
runtime adapters and 40 bindings. Project readiness remains `not-assessed`; no
runtime acceptance is claimed.

Provider integration and bounded Issue closeouts are complete. Remaining work is
the separate future admission gate #23 and owner-deferred S6/P7 obligations for
#322/#369. S6/P7 are deferred, not passed; the existing `v0.19.0-rc.2` tag
requires no further tag action.

## Read in this order

1. Root AGENTS.md and the source-only execution override it names (U001).
2. This file and rc2-coordinator-transfer.json.
3. The rc.2 design; its new execution-start note supersedes the earlier proposal-only
   no-dispatch wording for the approved scope.
4. Current workflow.yaml and live Issue #322. The older coordinator-transfer.json
   is a detailed rc.1 evidence index; read specific fields only when needed.

At the time of the earlier continuation, the receiving worktree was
`F:/framework-next/rc2-coordinator`, branch
`codex/2026-09-24-rc2-coordinator`. That location is superseded by the current
checkpoint above; its original acceptance observations remain historical.

## Receiving task and observed acceptance

Task `01a0d226-d1f7-7d43-ad20-8b7b9f8e0e00` was created on host `local` with explicitly requested
`gpt-6-astra` / `ultra`. Its first turn completed read-only acceptance at clean
HEAD `2a2f124450a29d5ed315608df16edee812436468`, verified the assigned branch,
parsed the JSON/YAML and read Issue #322 as OPEN. Creation settings are not
independent runtime attestation. No product edit or implementation dispatch was
performed during acceptance. Online integration and sender release are next.

## Historical initial work plan — superseded

The following dispatch instructions describe the completed initial RC2 phase and
are retained as history. They are not current next steps; use the current
checkpoint above for remaining work.

S1 fixes the selection, content-package, catalog and lock contracts and enumerates
the reusable engineering content migration. Record exact formats, old-reader
compatibility, target rule applicability, actual package ownership and examples for
source-without-knowledge and mq-lab-with-dotnet. Then hand off exact interfaces and
members to S2 content, S3 distribution and S4 runtime owners. S5 consumes installed
knowledge and performs source/target adoption; S6 verifies the actual RC.

Use bounded online Issues, assigned RAM worktrees, one writer and local handoff
followed by coordinator push/PR/online merge. The owner's 2026-09-24 U001 amendment
allows short, clearly bounded work to use coordinator-dispatched sub-agents with
a capable lower-cost profile; larger or multi-stage work retains independent
Astra/ultra tasks. Executors do not create further tasks or delegate without a
coordinator assignment. #369 expansion remains deferred.
Routine implementation choices inside the approved direction need no repeated
owner confirmation; preserve actual approval-review rejections if any occur and
report the exact blocked action instead of bypassing them.

## Historical two-phase transfer protocol

This describes the earlier receiving-task handoff and does not govern the current
checkpoint or assign a new S1 task.

The first receiving turn is read-only acceptance of the prepared checkpoint. The
sender remains the only tracked writer until the actual task ID is recorded,
the current-coordinator pointer is updated, and the handoff PR is merged. The
sender then provides the merged SHA and exclusive-writer release. That message
starts S1 in the fresh task; no scheduled automation is involved.

The owner may archive the old task after acceptance and release. Preserve the old
worktree/evidence until normal safe cleanup conditions are checked; task archival
does not imply filesystem deletion.

## Completion and remaining limits

Source RC2 adoption and immutable tag read-back are complete. MQ's approved URL
and binding rebind, PR #24 integration and provider closeouts for #22/#411 are
complete. The target's fourteen engineering rules
and forty bindings remain target-owned; API2 reported project readiness
`not-assessed`, so no runtime or behavioral acceptance is inferred.

The outstanding future work is admission gate #23
and owner-deferred S6/P7 under #322/#369. CI/legacy formal checks remain
deferred-by-owner; no GitHub Release or new tag is selected. Preserve actual
failures and deferred outcomes in the current workflow plan rather than treating
this local checkpoint as aggregate RC2 acceptance.
