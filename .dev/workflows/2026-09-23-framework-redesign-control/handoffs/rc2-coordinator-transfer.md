# RC.2 coordinator continuation

## Current owner-selected checkpoint — 2026-09-29

Source PR #412 and tag `v0.19.0-rc.2` are read back complete: `origin/main` is
`31fd8a02dcb22c9f4ddc6734d5b6ccab423211c5`, and tag object
`0f6118554f1573d835faf67aaa418dd291dd01d1` peels to product commit
`aad927328c20b08c8445e8ad1792eadd8ecc3466`. Issue #409 is closed; direct
GitHub reads show #411 and mq-lab #22 open, with #23 open as the future target
admission gate. After this source checkpoint integrates, resume from source
main; continue the remaining MQ work on draft PR #24 and head branch
`codex/2026-09-29-framework-rc2-adoption`. If source changes become necessary,
create a new bounded branch from the then-current main.

Coordinator API2 evidence for MQ: the install succeeded with lock SHA-256
`c9a47c945f19fe869696c514003f7eb64ad0219b8f4a315fde4b1d7eaa7ea15f`; the lock
contains 384 managed members and the selection has 40 bindings. Read-only raw
hash checks confirmed 384/384 members equal the selected subset manifest,
staged Git blobs and working tree. Project readiness remains `not-assessed`;
this does not prove reference validity or runtime behavior.

Nine proposed authority URL changes in `.dev/ai-context/TARGET-ENGINEERING-RULES.md`
remain unapplied pending owner disposition after automatic review required direct
approval. Do not apply that diff without the owner response. Then rebuild the
final MQ subset and perform the official API2 rebind. MQ PR #24 is read back
OPEN/draft against `main`, with head branch
`codex/2026-09-29-framework-rc2-adoption` at
`aecf4b2ebc3ed1fc661138c06a93c6d2c03101ca`; it is not merged. After approved
disposition and rebind, continue with PR integration and main read-back. Keep
#411/#22 open until integration is verified. S6/P7 and runtime acceptance remain
deferred-by-owner.

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

## First concrete work

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

## Two-phase transfer

The first receiving turn is read-only acceptance of the prepared checkpoint. The
sender remains the only tracked writer until the actual task ID is recorded,
the current-coordinator pointer is updated, and the handoff PR is merged. The
sender then provides the merged SHA and exclusive-writer release. That message
starts S1 in the fresh task; no scheduled automation is involved.

The owner may archive the old task after acceptance and release. Preserve the old
worktree/evidence until normal safe cleanup conditions are checked; task archival
does not imply filesystem deletion.

## Completion and limits

Stable 0.19.0 remains not ready. `aicf-` changes runtime entry names, not public skill
IDs. Claude shares the installed core. Reusable knowledge lives in src and is
optional in installed selections; an installed file alone does not prove consumer
routing. Source self-adoption excludes engineering knowledge it does not need.
The target's 14 rules and four customizations remain target-owned.

Carry R1-R8 and exact rc.1 identities from the JSON forward. Existing target
receipts are local/path-bound; the C: analysis archive is not online. CI, dormant
source policy, #369 native work, stable publication and new tag/Release creation
are not activated by this transfer. The narrow document/JSON/YAML/Git/commit checks
are distinct from U001-deferred formal/legacy validation.
