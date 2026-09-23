# Coordinator handoff: repair, prerelease pilot, then verification and release

Recorded: 2026-09-23T21:30:00+08:00. Program: [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
This is the current resume entry. Earlier phase reports remain historical evidence.
The workflow is in progress; this checkpoint is not architecture, test, release or target-adoption completion.

## Owner decisions and current authority

The owner explicitly requested a fresh coordinator conversation to reduce accumulated
context, asked this coordinator to complete the handoff and confirm the successor is
working, and will archive the old coordinator personally afterward. Create a new
conversation, not a fork of the long history. Select GPT-6 Astra with ultra reasoning.

The latest owner-selected sequence supersedes the earlier order where they conflict:

1. Repair the known installation/reader/writer problems. Use only affected focused
   checks and necessary small real observations to establish the repair.
2. Prepare a versioned prerelease and perform the actual dotnet-mq-arch-lab pilot.
3. After that pilot, revisit overall validators, test design, release delivery and
   pipelines; use actual pilot findings to shape that work.
4. Finish reconstruction and later publish stable 0.19.0 through its actual release
   process. A version intention is not a release or passing acceptance.

The owner proposed 0.19.0-rc.1 or 0.19.0-prerelease.1. The coordinator selects
**0.19.0-rc.1** as the trial target, with **0.19.0** the subsequent stable target.
This selection names no existing artifact/tag and does not make development bytes
a stable release. Before installing, establish a coherent version identity,
immutable candidate identity, installation provenance, selection/config semantics
and a concrete rc.1-to-stable upgrade route. Do not simply relabel v0.18 or a
development output. Keep per-skill versions separate from the distribution version.
Do not promise future upgrade success based only on version ordering.

The selected downstream pilot is now authorized by the owner's direct request,
after the known problems are repaired. It is limited to framework adoption in that
project. Preserve product source, databases, local configuration and target-owned
rules. U001 is source-only and must not be copied into downstream authority.
Prepare the concrete prerelease packaging/tag/publication actions under the
repository's applicable release rules; do not silently enable CI, publish stable,
alter credentials or change unrelated protections. The owner has selected a trial
version, not already approved unspecified release assets/settings.

Standing source authority remains: online Issues; coherent local commits before
push; remote branch -> online PR -> online merge; exact remote read-back; cleanup
only after completed/merged/clean evidence. No direct main push. No sub-agents,
nested agents or executor-created conversations. One independent Astra/Ultra task
per implementation Issue; the coordinator manages assignment, disjoint ownership
and integration. Reuse original Issue tasks for their continuing scope and archive
idle completed tasks to limit sidebar noise. Do not create tasks merely to poll.

## Repository pins and receiving workspace

- Source: C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend.
- GitHub: YuChia-Wei/ai-collaboration-framework.
- Saved project: local-5f8746e4b211ab4ea00c47947882f304.
- Source main/origin observed before this handoff: 90051b7008e1de2fc87ef91e08f3fb7f54fa9555,
  merged PR #376; root tracked/untracked status was empty.
- Old coordinator: 01a0c9d9-3b00-7b70-ad85-daff590e7ecd.
- Assigned successor worktree: F:/framework-next/coordinator-next.
- Handoff branch: codex/2026-09-23-coordinator-handoff.
- After online handoff integration, the predecessor prepares
  codex/2026-09-23-redesign-continuation at the merged commit in that same F: worktree.
  The startup prompt supplies the actual merged commit and receiving branch.
- Git objects remain in the persistent C: source repository. RAM files are volatile.
- Resolve this transport checkpoint from its containing Git commit, not a
  self-referential future SHA. See [machine-readable resume facts](coordinator-transfer.json).

Use the registered C: project only as task bootstrap/navigation context. All
successor repository execution and writes use the assigned F: worktree explicitly;
do not edit the main checkout or let an app create an unassigned C: worktree.
Only one coordinator writes shared records at a time. The old coordinator stops
repository writes before dispatch. The successor records its actual task ID in
workflow.yaml and updates the execution override's current-coordinator pointer
while retaining this predecessor handoff. Those administrative pointer updates
do not activate dormant policies or retire U001.

## Current implementation and evidence

18 components / 113 payload members / seven complete profile mappings are on main.
Portable skill packages, source-under-src, project data ownership and core/custom
boundaries are implemented/designed. Root and downstream adoption are not complete.
Counts describe source selections, not installation of every profile.

| Issue | Original task and retained worktree | Current result and remaining work |
| --- | --- | --- |
| #368 | 01a0cd11-1dc9-7842-abba-65b8fac0edb8; F:/framework-next/368 | Returned e71ccc989c3ae213a8e04cbe51abb80183022024; repair subject 379213a1f575aff143fb29b665c42fe5f24b219c. 16/17 methods successful, 1 error, 0 skips, exit 1. Two real Lesson assemblies have equal selected bytes/inventory/identity. The real installation_state._root still refuses F: strict resolution. Reader/refusal cases and affected source review remain. |
| #369 | 01a0cd11-7b98-7090-ae53-1bf7bf46a651; F:/framework-next/369 | Returned 0725c3dd68e6d1cb4aca5d03343cd239b8c447a1. Dormant policy/root/template pointers are integrated, not effective. Earlier 37/37 caller tests used synthetic complete runner outcomes; no real Windows native binding/acceptance. Broader policy/gate review belongs after the pilot, unless narrowly needed for a repair. |
| #373 | 01a0cd49-7805-7202-9176-e8f7b4cf4285; F:/framework-next/373 | Returned 7996b32d3d4f70553b203299e25dc69d9413ff9d. Seven family test bodies; selected read-only cases completed, no full public-family round-trip pass. Metadata aliases were subsequently repaired in #368 but not freshly exercised. Writer-volume refusal is separate from the reader failure. |

These returned commits are merged into current main. Original turns are completed;
their Issues and #322 remain OPEN. No current user approval is pending for the
previous #368 four-file repair or #369 dormant policy scope. Their earlier automatic
approval rejections remain historical. New repair paths need an explicit bounded
coordinator assignment, not a false extension of those old four files.

The #368 repaired files were src/distribution/git_source.py, assembly.py and
src/skills/pr/skill-package.yaml plus src/skills/local-backlog/skill-package.yaml.
The path fallback retained strict normal resolution, ancestor link/reparse refusal,
path identity and source/output containment; preserve those safeguards.
The newer repair changed engine bytes: the earlier #370 review cannot validate them.

#370/#371 source-pin repair and its affected review are complete through PR #374.
Ten focused loader tests passed. The one unmodified public-entry attempt refused
before dispatch; this is not native installation acceptance.

F: observations: Path.resolve(strict=True) can fail with WinError 1.
GetVolumePathNameW for F:/framework-next yielded the nested directory as the volume
root; GetVolumeInformationW on that result failed 144, while an explicit F:/ root
reported NTFS. These are observations, not a proven driver cause or permission to
skip backend/path protection. C: target behavior has not been established by these
F: observations. Do not silently change drives, relax guards or repeat an unchanged
failed run. The existing native-windows runner/binding remains unfinished; choose
the smallest actual path needed for the repair and pilot, not a full old matrix.

## Exact next work

1. Read this entry and the machine facts; verify assigned branch/root/HEAD and
   current provider state. Announce receipt with the actual observed identity so
   the predecessor can confirm startup. Continue working after acknowledgement.
2. Read the current [approved-return report](../reports/p7-approved-returns-and-cleanup.md)
   and, only as needed, the #368 repair report and #373 public report.
3. Define and open a narrowly scoped reader/Windows writer compatibility repair
   Issue (or reconcile explicit ownership with existing Issues). Inventory the
   actual shared/distributed write implementations before choosing the write set.
   Preserve symlink/reparse, containment, filesystem support, writer locking and
   recovery semantics. Supply an explicit small acceptance set and assigned F:
   worktree to its one independent Astra/Ultra task. No sub-agents.
4. Integrate the repair through online PR; perform affected review and the minimal
   relevant public/native observations needed to trust the pilot. Keep larger
   verification/gate redesign deferred to the owner's third stage.
5. Prepare rc.1 with real version/provenance and upgrade/recovery support; inventory
   target customizations and select the complete intended pilot profile and exact
   old-route retirements. A Lesson-only pilot must be described as Lesson-only,
   never as a full framework upgrade.
6. Install/activate in the actual target on an isolated branch under its own
   governance; show the user the resulting directory layout, project settings and
   usable skill/workflow entry points. Preserve a reviewable diff and recovery.
7. Use pilot outcomes to close remaining verification and release/pipeline design.
   Keep source Actions disabled until the separately adopted concrete subset.
   Stable 0.19.0 and rc.1-to-stable adoption remain observable separate outcomes.

## Target project read-back

- Path: C:/Github/YuChia/dotnet-mq-arch-lab.
- Saved project: local-64b2bfa4a5965c4f01a944f9a8021114.
- Remote: YuChia-Wei/dotnet-distributed-architecture-lab.
- Branch/main: cb122285af09e46b24102f22a0ad9d713219c1f2.
- Tracked status was empty. A full status attempt warned about two old ignored
  .python-prerequisite-fixtures/shadow directories; do not treat that as a whole
  filesystem inventory or delete them.
- .dev/ai-context/provenance.yaml records v0.18.0 from
  0e5fbfc4a4a69ecd9da543751d53edfd311f93fb and a completed v0.17 -> v0.18 migration.
- .dev/ai-context/customizations.yaml and effective-rules.yaml are target-owned
  inputs. No new .ai/core/custom/framework config was observed as tracked content.
- Target AGENTS has its own workflow, routing and commit overlay. Re-read before
  writing; do not export source U001 or overwrite project truth.
- This coordinator only inspected the target. No target file, branch or runtime
  was changed for this trial.

## Preservation and cleanup

25 completed numbered F: worktrees were removed after exact merged ancestry,
clean state and CLOSED/COMPLETED Issue proof. 41 ignored files / 45,470 bytes were
copied with SHA-256 checks to the persistent ignored archive:
C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/framework-next-control/completed-worktree-archive/.
See [cleanup evidence](../evidence/completed-worktree-cleanup.json).

Preserve F:/framework-next/368, /369, /373 and all p7-runs evidence:
- #368 actual run: F:/framework-next/p7-runs/368-contracts/fn-612302fba311482d98c4d8be0ad3a1a3.
- #373 failed/partial runs: F:/framework-next/p7-runs/373-public.
- F:/ai-context-tests and any owner-preserved ai-contex-test spelling if present.
- Unrelated older C:/ worktrees and F:/codex-v018-evaluation remain outside cleanup.
- codex/2026-08-31-subject-digest-evidence-reuse-design and
  codex/luna-requirements-trial-20260908 have unmatched patches; no associated PR
  was found. Do not delete them as merged.

25 task IDs from retained dispatch records were individually read: all latest
turns completed, no running derived turn. Archiving was assessed as possible,
not performed by this coordinator. Task archival does not close Issues, remove
worktrees or validate their contents. The owner will archive the old root after
successor startup. Keep conversation status, implementation and provider state separate.

## Provider and verification limits

At the pre-handoff read-back, main matched 90051b7, no PR was open, #322/#368/#369/#373
were OPEN, and the latest published release listing was v0.18.0.
Actions enabled=false. All nine workflows were disabled_manually, including
Source checks 364914272 and Source native checks 364914274.
Do not infer hosted success or enable any workflow to transport this handoff.

Only document/JSON/YAML/link/Git inspection and the exact commit-message checker
are selected for this transport under U001. Legacy critical/full/history,
handoff-validator/audit/lease packets and high-I/O matrices remain
deferred-by-owner (owner: #322 coordinator; next: post-pilot review).
The small JSON sibling is a resume record, not a fabricated passing formal receipt.
No product tests, target install, release or performance claim is made.

Minimum progressive references, loaded only when their phase requires them:
- [Current P7 contract and owner-order override](../../../design/framework-next/p7-execution-selection.md)
- [Original request coverage](../reports/request-coverage-at-p7-entry.md)
- [P6 selected installer contract](../../../design/framework-next/p6-selected-contract.md)
- [Adoption/recovery boundary](../../../design/framework-next/source-adoption/adoption-and-recovery.md)
