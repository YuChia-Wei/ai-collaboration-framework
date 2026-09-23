# Proposed tiny Windows Lesson pilot

**Unexecuted; deferred-by-owner**, U001, program #322 coordinator / P7.
These are concrete paths for later selection, not created directories, approved
native bindings or durability evidence. First selection is exactly
`lesson-minimal` / `lesson@0.2.0` / `codex`; no root adoption or profile union.

## Exact proposed bindings

| Binding | Absolute proposal |
| --- | --- |
| Fixed external engine/source checkout | `F:/framework-next/p7-engine` |
| Isolated pilot project | `F:/framework-next/p7-runs/lesson-w01/project` |
| Builder candidate parent | `F:/framework-next/p7-runs/lesson-w01/candidates` |
| Builder scratch parent | `F:/framework-next/p7-runs/lesson-w01/build-scratch` |
| Maintenance scratch parent | `F:/framework-next/p7-runs/lesson-w01/scratch` |
| Maintenance staging parent | `F:/framework-next/p7-runs/lesson-w01/staging` |
| Requests/results | `F:/framework-next/p7-runs/lesson-w01/observations` |
| Disposable test opt-in | `F:/framework-next/p7-runs/fixtures` |
| Separate native Windows test root | `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/lesson-w01/native` |
| Persistent managed recovery parent | `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/lesson-w01/recovery` |
| Persistent project backup parent | `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/lesson-w01/project-backup` |
| Persistent selected observations | `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/lesson-w01/observations` |

C: parents use an existing repository ignore rule, checked again at execution.
They are outside engine/project and separate from each other. Recovery never
belongs to disposable output. Source persistence is the existing C: Git object
database plus an explicitly retained ref to the selected commit; this excludes
uncommitted files, host dependencies and project data. Coordinator may later
create a minimal tracked-source checkout, without copying whole repository
history/working tree. Do not reuse the design worktree as an active engine.

Candidate root is the builder's **returned** child
`.../candidates/candidate-<commit-prefix>-<uuid>`; builder scratch similarly uses
returned `scratch-<uuid>`. No predicted UUID/identity. Maintenance allocates
`i-<32hex>` below its three roots, durable `objects/<64hex>` and `operation.json`;
recovery uses the returned exact operation root/hash.

Starting design source: `171f33474f88888fbe853600de04bfe9c5716b25`. After selected
implementation/fixes, coordinator freezes full commit `S` and matching engine.
EnginePin is exactly `{id,version,source_commit,files}`, ID
`framework-managed-installation`, version `1.0.0`, commit `S`, sorted raw hashes
of [#359's ten files](../managed-installation/handoff.md). Compute from actual
checkout bytes; no normalization, sample hashes, six-file reader pin or branch
name. Persist `S`, raw pin and interpreter prerequisites so source owner can
recreate the same engine after F: loss; managed recovery never fetches it.

Later preflight checks existing direct/local roots, disjointness, ownership,
no reparse/hardlink/nested-volume/case/prefix collision, writable scope, complete
240/255 UTF-16 path budgets including allocated names, observed device/filesystem
and actual ignore/untracked state. All parents must exist. Owner identifies F:
as RAM; limited prior DriveInfo observed NTFS/Fixed and Get-Volume was denied.
Those observations do not prove physical durability. Do not bypass the denied
inspection with another tool/API. #364 performs no native probe.

Select `mode_policy=windows-inventory-only` and
`failure_domain=process-termination`: OS/storage remain available. C: copies
reduce sole dependence on RAM but do not prove controller/media/power-loss
survival. `project-volume-loss` is unselected: distinct device identity and a
surviving non-RAM store require fresh evidence and separate scope. Power loss,
OS crash/reboot, missing recovery storage, hostile writers, Linux/macOS/network/
overlay filesystems and ReFS are not accepted by this pilot. Installer supports
additional backends in source; Lesson's Windows tool requires local fixed/RAM
NTFS, so installer ReFS support alone does not qualify this combined pilot.

## Preparation and protected project state

Later project owner provisions only pilot `AGENTS.md`, `.gitattributes`,
`.gitignore`, `.ai/custom/framework.json` and `.dev/lessons/records` with ancestors.
Config body is exactly [#361's proposal](../source-adoption/pilot-framework.proposal.json):
config 2, Lesson namespace, tracked store, package template, locked root/tracking/
template and narrowed write root. No local config/decision adapter/accept; M01
stays unassigned. No legacy data/history copy.

Use #361's pilot route and exact byte-preserving attributes for Lesson core,
lock and generated entry. Ignore selected transient/local locations only; do not
hide `.ai/framework.operation` as readiness. Guard is
`.ai/local/installation.guard`; config transition marker is
`.ai/config-transition.operation`. Neither can be deleted to bypass admission.

Before mutation, persist a small project backup: exact route/config/attributes/
ignore bytes with digest/original path, expected-absent selected record inventory,
and the later tiny Lesson JSON immediately after write. Save observations separately.
Managed capture covers core/runtime/lock and candidate metadata, not project files/
data. Unknown/newer bytes require reconciliation, never old-backup overwrite.

`protected_inputs` selects the four project files above and exact known record
files after creation as sorted `{path,sha256}` rows (project-relative path; raw
SHA-256 or null for observed absence). No
directory/glob/store discovery. Empty collection is separately project-owned.
Missing protected inputs remain unresolved even if managed recovery matches.

## Installer cases selected before pilot

Consume #359's case inventory proportionally:

| ID | Observation / evidence class |
| --- | --- |
| N1 entry | Real isolated public inspect/plan with full pin; wrong raw hash and wrong pin membership refuse before dispatch. Check no pycache/ambient source fallback. Module-origin/missing-dependency seams remain synthetic. |
| N2 admission | Actual emitted Lesson candidate; same-byte unowned collision and unchanged old-member drift refuse without overwrite. Stale expected plan/lock/candidate/protected-input binding refuses; unknown sentinel subtree survives. |
| N3 coordination | Two real Windows processes on a tiny installed fixture: helper holds empty guard range through native LockFileEx; public maintenance refuses nonblockingly. Terminate only owned helper; fresh request proceeds after native release. Never unlink/replace guard. This proves native exclusion, not a killed installer. |
| N4 publication/no-op | Real apply verifies complete durable closure before marker/mutation, target/lock exact, marker absent, truthful counts. Same-content rebuilt candidate no-op preserves bytes/modes/mtimes and allocates no i-root/objects/marker/lock rewrite. One real denied/open-file replacement failure retains residue. |
| N5 recovery | Deterministic test-only faults before capture completion, after marker and around lock/marker completion check refusal/finish/restore on tiny synthetic subjects. Separately attempt ONE unmodified public apply termination after an observed marker event; capture exact lock/marker/member/object state and perform admissible same-engine finish or explicit restore. Bounded native directory-notification helper, no source hook/delay injection or fabricated state labelled public. |

Changed-member native fault cases may use a small deliberately authored candidate
fixture emitted by the real builder from its own exact tiny Git subject. Label
that data synthetic while retaining actual public/native operation evidence; do
not edit emitted metadata to impersonate the real pilot candidate. N4 tests the
replacement primitive only when a genuine before/after candidate exists.

N5 may miss the brief mutation window. Without attributable interrupted state,
report **not-observed**, retain actual result and stop that attempt. N3/synthetic
N5 cannot fill the gap. Coordinator selects a materially changed targeted attempt
or retains the explicit acceptance gap before root adoption; no silent fixture/
history expansion or retry-until-green. A complete marker-free target allows only
read-only already-matching; completed-operation replay cannot authorize rollback.

Residual #359 rows: exhaustive per-member interruption, Linux flush/modes, all
supported filesystems, whole-volume loss/interrupted reconstruction, complete
native budget/path sweep and broader recovery remain deferred-by-owner to
coordinator / P7 selection. First-install residue, unknown `.fi-*` siblings,
empty guard after clean-install restore and ambiguous partial whole-loss recovery
retain conservative refusal/owner reconciliation. Cheap synthetic refusal checks
do not grant native acceptance. No new journal/phase/receipt platform.

## Pilot sequence and exit evidence

1. Confirm accepted V1/Lesson V2/N1-N4 and explicit N5 disposition; select runtime,
   `S`, roots, permissions and backup scope. Record quiescence owner/window; stop
   affected sessions/tools/external writers. Declaration cannot technically control
   arbitrary readers. Keep pilot use inactive until ready.
2. Build twice using [selected commands](selected-checks.md). Compare nine exact
   payload members, one Codex entry, three metadata files and candidate identity.
   Use returned candidate root/identity in actual inspect and plan.
3. API 1 inspect then plan: exact roots/pin/candidate, observed absent lock
   (`expected_lock_sha256=null`), Windows mode, supported durability declaration,
   protected inputs, `project_data_action=none`. Consume real `plan_sha256`.
   Preview's pending exclusion/allocation gates are not execution passes.
4. Apply with unchanged inputs/hash and fresh maintenance declaration:
   `affected_capabilities=["lesson"]`, real responsible source, sessions/tools/
   external writers stopped. Check managed ten-file set, lock, durable operation,
   marker removal and protected preservation. Readiness stays `not-assessed`.
   Plan/apply second same-content candidate as no-op.
5. Invoke installed `.../project/.ai/core/skills/lesson/scripts/lesson.py` with
   actual project/installed package roots and config path: explain/query/create/
   inspect/validate/render. Create one tentative candidate from real query digest,
   never accept; persist its backup. Reads/render preserve bytes and agree on digest.
6. Observe candidate bytes -> staged blobs -> fresh tiny checkout bytes under
   effective attributes, using only a new local pilot repository and selected files.
   No history copy, push or publication. Fresh checkout binding:
   `F:/framework-next/p7-runs/lesson-w01/git-readback`, outside active project.
   Compare Windows mode inventory only; retain selected tiny bundle/files in project
   backup. Git refs alone do not cover ignored/uncommitted data.
7. Coordinator opens a fresh Codex task only under later runtime authority to
   observe installed route/config/store/read-back without src/legacy fallback.
   Executor does not spawn it. Retain actual task/model/input/output identity;
   entry text alone is not invocation evidence.
8. Persist observations and residues; report actual counts/caps and passed, failed,
   unavailable, not-observed and deferred cases, without global pass/performance
   claim. Coordinator then selects separate root adoption, broader skills,
   independent review and #365 restoration proposal. Later contained F: cleanup
   never deletes recovery storage.

Failed installation keeps use inactive. Recover exact active operation, then
reconcile project backup separately. After use, rollback needs a fresh plan and
data compatibility decision; Lesson 0.1 cannot be assumed to read v2/config 2.
Missing engine/recovery/config/data is a named blocker, not permission to choose
another root, engine or evidence source.
