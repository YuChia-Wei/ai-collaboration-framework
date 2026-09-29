# RC.2 coordinator continuation

## Current owner-selected checkpoint — 2026-09-29

Continue from [the active adoption workflow](../../2026-09-29-rc2-adoption/workflow.yaml)
and its plan. Source adoption is bound to Issue #411 in
`F:/framework-next/rc2-source-adoption`, branch
`codex/2026-09-29-rc2-adoption`; downstream adoption is separately bound to
Issue #22. The source and target tasks are in progress. S6 runtime discovery,
behavioral acceptance, upgrade/recovery trials and target admission are
`deferred-by-owner` for this delivery. R5, P7, CI restoration and program #322
remain open. The former `F:/framework-next/rc2-coordinator` receiving location
below is historical and must not be resumed.

The owner has directly instructed this task to start rc.2 and prepare a fresh task
when accumulated context is excessive. This is that continuation, not another
request to approve the already selected direction. Start from the compact
[JSON checkpoint](rc2-coordinator-transfer.json) and
[rc.2 design](../../../design/framework-next/rc2-installation-selection.md).

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
