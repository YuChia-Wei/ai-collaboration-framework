# RC.2 coordinator continuation

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

The assigned receiving worktree is `F:/framework-next/rc2-coordinator`, branch
`codex/2026-09-24-rc2-coordinator`. A saved-project task location is only a bootstrap;
all source commands and writes must explicitly use the assigned F: worktree.
Do not edit main or create a second unassigned worktree as a workaround.

## First concrete work

S1 fixes the selection, content-package, catalog and lock contracts and enumerates
the reusable engineering content migration. Record exact formats, old-reader
compatibility, target rule applicability, actual package ownership and examples for
source-without-knowledge and mq-lab-with-dotnet. Then hand off exact interfaces and
members to S2 content, S3 distribution and S4 runtime owners. S5 consumes installed
knowledge and performs source/target adoption; S6 verifies the actual RC.

Use the existing #322 execution pattern: bounded online Issues, independent
Astra/ultra tasks, assigned RAM worktrees, one writer, local handoff followed by
coordinator push/PR/online merge. Do not spawn source sub-agents or revive #369.
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
