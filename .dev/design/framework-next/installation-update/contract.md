# Managed installation contract: quiescent maintenance v1

Design only for #345. Coordinator selected this bounded revision after checkpoint `51229b63565ce6e836d57a4b107cf6df5554bf7c`; that commit remains historical, not the current invocation model. [Evidence](source-evidence.md), [formats](formats.md) and [cutover](cutover-and-slices.md) complete the design. No installer, migration or root activation is executed. U001/P7 boundaries remain.

## Maintenance boundary and versions

V1 installs while the affected capabilities are explicitly disabled for maintenance. Before apply/recover/M01 mutation, caller declares affected sessions, tools and external writers stopped. The tool checks the declaration's presence/scope, but cannot prove it is true or control agent text already loaded. Caller maintains quiescence until installation/config work and separately selected project activation checks finish.

An OS-held exclusive lock coordinates ONLY participating maintenance writers for the entire apply/recover/M01 operation. File existence is never lock ownership. Instruction reading and ordinary skill/tool invocation do not join this lock, use a common launcher or acquire a shared runtime. Existing adapter does not need an installation launcher; instruction-only skills remain runtime-free.

Concurrent nonparticipating writers are unsupported. Before/after hash checks detect some observed drift; they do not eliminate TOCTOU or make concurrent modification safe. A false quiescence declaration is not converted into a supported concurrency guarantee. Markers report incomplete maintenance and prohibit owner activation; they cannot force arbitrary readers to stop.

Propose engine `framework-managed-installation@1.0.0`, API integer 1, lock integer 1, package operation integer 1. These are unreleased proposed contracts. Initial candidate input remains actual selection/files/build schema integer 1, development mode, release_version null and builder framework-development-assembly. Bool/float/string versions do not equal integers. Current base supports metadata v1/v2; consume #346's actual delivered loader/adapter for selected v3, never a second metadata parser or presumed #347/#348 package.

Supported package transitions: absent installation -> exact candidate, or valid v1 installation -> another exact candidate under the same pinned engine. Profile change replaces the complete selected inventory; no dependency solver, floating label, historical chain, stable publication or cross-engine recovery. A downgrade can make managed bytes consistent; it does not prove project config/data remain readable. That activation decision is separate.

## Fixed external development engine

Run the development engine from an explicit source checkout OUTSIDE the project being modified, pinned to a full commit and hashes of every required implementation file. No load/import from rewritten `.ai/core`, ambient module search, automatic discovery/fetch, engine substitution or self-update. Input candidate commit may differ from engine commit; each has its own identity.

`EnginePin` in [formats](formats.md) binds id/version/full source commit and the closed required-file raw SHA-256 set. Verify checkout Git identity and executing bytes before mutation/recovery. The implementation owner must close its actual local import/resource dependency set; missing/unknown closure blocks execution. Pinning bytes is not source authenticity or publication proof. Recovery requires the SAME engine pin, not merely equal version text. If that source checkout is lost, caller must explicitly restore/provide the matching checkout from durable Git before recovery; no automatic engine acquisition.

The exact entry script, complete file set, interpreter/dependency prerequisites, pin verification bootstrap and later packaging are downstream implementation choices with one owner. This design does not invent a released binary, signature or installed shared runtime.

## Candidate integrity and public operations

Read all three candidate documents and listed files; recompute raw hashes, declared Git modes, source/profile/member/adapter bindings and closure. Reject missing/extra candidate files, invalid paths, aliases/prefix collisions, links/reparse points, unsupported metadata, incomplete completion metadata or digest disagreement. `outcome=assembled` alone is insufficient. Caller selects approved candidate identity; hashes are integrity, not trust signatures. Unknown target files are preserved.

Proposed facade `src/distribution/installation.py`; a thin source entry may call it. It neither selects the #149 CLI runtime nor enables #168 preview mutation commands.

| Operation | Contract |
| --- | --- |
| inspect | Read-only explicit project and optional candidate inspection. State uninstalled, managed-bytes-consistent, drift, recovery-needed, unsupported or blocked. No skill invocation or project-readiness verdict. |
| plan | Exact candidate/root, expected lock hash/null, engine pin/root, mode policy, explicit scratch/staging/recovery roots and durability declaration; optional finite caller-selected protected inputs. Compute delta/collisions/path budget/maintenance scope and deterministic plan hash. No mkdir, config resolution, data scan or compatibility plugins. |
| apply | Same inputs, accepted plan hash and fresh explicit maintenance declaration. Hold participating-writer lock; recompute inputs. Equal state returns unchanged with no content/state writes. Otherwise durable capture, marker, exact delta, complete read-back and lock publication. Applied means managed-bytes-consistent only; project_readiness is not-assessed. |
| recover | Explicit operation directory/hash, same engine pin/root, fresh maintenance declaration, finish/restore direction and expected observed lock/marker hashes. Uses durable objects, not original scratch/candidate. Recovered means matching managed state (or uninstalled after undoing clean install), never project readiness. |

There is no ordinary invocation/read API. Plans/results are transient, not receipts. No force/adopt-existing/overwrite-drift, uninstall, generic migration, cleanup scheduler or arbitrary shell operation. Removing a package means selecting another nonempty supported profile.

No-op requires candidate content identity, inventory, declared mode policy and actual owned state equal. Another build UUID/time cannot churn lock. No marker/staging/backup/lock rewrite or chmod. Acquire the already established writer coordination resource without replacing it; if unavailable, report blocked rather than creating state under a claimed no-op.

## Ownership and delta

| Surface | Owner/boundary |
| --- | --- |
| `.ai/framework.lock` | Installer-generated, reviewed/tracked with exact outputs; never builder input or hand-edited provenance. |
| `.ai/core/skills/<id>/<member>` | Exact payload destinations in accepted old/new inventory only. |
| `.agents/skills/framework-<id>/SKILL.md` | Exact generated Codex destinations only; no directory/sibling/custom ownership. |
| `.ai/framework.operation` | Package incomplete-maintenance marker, identical to durable record. Present/unreadable/malformed means recovery-needed; owner must not activate. No arbitrary-reader enforcement. |
| `.ai/config-transition.operation` | M01 owner's corresponding marker. Package writer refuses it and cannot clear it. |
| `.ai/local/installation.guard` | Inert, explicitly reserved maintenance coordination file. Native handle lock, not existence, excludes participating writers. Never replace/unlink to break a lock. No lease schema. |
| `.ai/custom`, `.dev`, config/templates/stores, root entries and unknown files | Project-owned; no package copy/conversion/chmod/adoption/cleanup authority. |

Before mutation verify ALL old members, including unchanged ones, against raw SHA-256/length/Git mode. Unchanged means equal descriptor; add requires absent old and absent target; change requires owned matching old; remove requires old owned absent new. Identical unowned bytes still collide. Aliases, parent/child occupation and reparse points conflict. Unknown siblings are disclosed/preserved; leave empty directories, no recursive delete. Reconciliation is project-owned; engine never implements a force choice.

POSIX materializes exact 0644/0755. Windows inventory-only retains 100644/100755 but does not assert ACL/executable-bit enforcement. Windows mode-only change updates declared inventory/lock with no member byte write and explicit mode-not-materialized result. Equal bytes/mode incur no write/chmod/mtime churn. Mode-policy/platform changes require explicit plan or unsupported result. No unrelated ACL/owner/ADS preservation promise.

## Explicit roots and durable capture

Caller supplies existing direct absolute roots; reject traversal, volume-root stores, drive-relative/device/UNC paths, links/reparse ancestors and ambiguous Windows names. No discovery, fallback, global TEMP/TMP edit or whole-project copy. Candidate/engine/recovery roots stay outside modified project; durable recovery cannot overlap candidate/engine/disposable roots. Scratch/staging may share one explicitly selected parent; otherwise selected roots do not overlap. Recheck containment at use.

Allocate an exclusive 32-hex operation ID:

- `<scratch_root>/i-<id>/`: disposable calculations, RAM allowed.
- `<staging_root>/i-<id>/`: disposable changed-file preparation, RAM allowed; same run if parent shared.
- `<recovery_root>/i-<id>/operation.json`, `objects/<sha256>`: durable complete managed before/after set. Caller explicitly declares durability for selected failure domain; path/drive name cannot prove it.
- Exact destination sibling `.fi-<12hex>`: prefix of SHA256(UTF8(operation_id + NUL + destination)); preflight uniqueness and exclusive absence. Collision blocks. Recovery clears only derived leftovers with expected bytes; unknown ones remain conflicts. Cross-volume copying is not atomic; single-file replacement uses supported same-directory primitive.

Budget all selected candidate/final/disposable/durable/control/temp paths. Proposed Windows refusal budget: full path 240 UTF-16 code units, segment 255, accounting for backend terminator/extra needs. This is a conservative product choice, not universal OS support evidence. Backend may be stricter. Fail before material writes; role/relative-path/length diagnostics avoid absolute host paths. No host/Git settings changes; #305 still requires actual evidence.

Stage only changed/add files and controls. Durable capture intentionally retains ALL old/new managed file bytes, exact locks and candidate metadata, deduplicated by SHA within one operation. It is a full managed snapshot, not a repository/data backup. No global cache service or retention engine. Failed/completed durable directories remain for separately authorized retention; scratch can disappear without losing the managed recovery set.

Optional protected_inputs are a finite caller-supplied file/hash set, used only for observed preservation checks. No parsing config meaning, enumerating record stores, following arbitrary references or inferring compatibility from hashes. Package apply never writes them. Unselected project data is outside the check, not declared validated.

## Apply and observable maintenance state

Caller first disables affected capabilities/stops affected sessions, tools and external writers, then provides explicit maintenance declaration. API verifies declared scope equals old/new selected capability union; it cannot verify stopped activity. Quiescence continues after API return until owner activation. First install reserves coordination path explicitly; unknown preexisting control files require reconciliation.

Hold OS exclusive writer lock through preparation, mutation, final read-back and result. Handle release on termination does not erase marker. File existence is not lock ownership; native backend must be supported and later exercised by P7. No force unlock or guessed lease timeout.

1. Recompute candidate/engine/lock/owned drift/protected inputs/accepted plan under lock. A pre-maintenance preview is stale unless recomputation matches. Reject an unrelated active marker.
2. Prepare next lock and complete durable closure; flush/read back using selected backend/failure-domain semantics. Write operation.json last and read it back. Incomplete capture causes zero managed mutations.
3. Publish exact marker with required ordering before member mutation; retain old lock. Marker reports incomplete maintenance to caller and future maintenance operations, not an enforced reader gate.
4. Recheck each old state immediately before exact replacement/removal. Use durable bytes if staging is lost; never truncate active target in place. These checks do not solve TOCTOU; nonparticipating concurrent writers remain unsupported. No per-file progress journal.
5. Read complete new inventory and selected protected inputs. While marker remains, publish next lock via supported single-file replacement and verify bytes. No config/data compatibility evaluation occurs.
6. After complete managed consistency, remove only this operation's marker; read back absence/lock/inventory. Report applied, managed-bytes-consistent, project_readiness=not-assessed and release writer lock. Owner still keeps capabilities inactive pending its separate activation checks. Failed durability/cleanup/read-back stays recovery-needed; retain durable objects.

No cross-file/directory/volume/whole-operation atomicity. Single-file/flush ordering must be implemented and selected by P7 for the declared failure model. If marker-before-mutation/lock-before-marker-removal ordering cannot be established, block. Inspect detects corrupt/missing lock or mismatching files even if marker was lost; it does not stop arbitrary readers.

| Observation | Maintenance interpretation |
| --- | --- |
| No lock/marker, destinations unoccupied | Uninstalled; legacy project content unaffected. |
| Supported lock, matching inventory, no markers | Managed-bytes-consistent; project readiness not assessed. |
| Complete durable record, no marker, matching old state | Prepared, no mutation admitted without fresh declaration and matching inputs. |
| Marker present/invalid, mixed bytes or torn lock | Recovery-needed; owner must keep affected capabilities disabled. |
| Marker present, matching next lock/files | Managed publication incomplete; explicit finish can recheck and clear it. |
| Marker absent, matching next state | Managed operation complete; no activation, data compatibility or historical receipt inferred. |

## Recovery and full RAM-project loss

Require same EnginePin and fresh caller maintenance declaration. Refuse unrelated valid marker/lock or active M01 marker. Check explicit expected current lock/marker hashes; a torn control file is repairable only when attributable to the selected interrupted operation, never by overwriting another valid installation.

During interrupted recovery, affected files may equal before, after, or the absence defined by add/remove. Finish writes after; restore writes before and removes only recognized additions still matching after. Unknown bytes/modes stop. Preflight all, then recheck each; no protection against a nonparticipating concurrent writer is claimed. Unexpected partial loss of previously present members is drift, not implicit overwrite authority. Same record supports interrupted restore; no reverse journal.

With marker absent and complete valid managed installation present, retained operation is read-only evidence: already-matching or conflict. Later downgrade uses fresh package plan/snapshot; the project separately evaluates current data before activation. No replay of old operation over a used installation.

For full RAM-project loss, caller explicitly recreates the project root at its original binding and selects the durable operation. `reconstruct_missing_managed=true` requires absent lock/markers and wholly absent managed set; partial unexpected loss does not qualify. Recreate marker then recover the complete selected before/after core/lock/runtime from durable objects without original candidate/scratch. Clean-install before=null restores uninstalled. Root relocation/another installation ID requires separate reconciliation.

Only managed files are recoverable this way. Project source/config/data need their own durable Git/backups and owner recovery. The installer may report managed-bytes-consistent after restoring that set, even while project data remains missing, but must report project_readiness=not-assessed and disclose unresolved selected protected inputs. It cannot claim whole-project ready or recreate missing data. Normal apply requires protected inputs to match; explicit full-loss reconstruction may report their absence without writing them. Unknown present project content stays untouched. Missing managed objects/engine or conflicting managed bytes prevent completed managed recovery.

## Selected P5 M01, independent from package apply

Coordinator selection `842b73ca09d701d1561109255193d80439dc996b`: [P5 contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/p5-selected-contract.md), [M01](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/capability-consolidation/implementation-slices.md). Read without changing base; no conversion implemented/executed.

M01 applies ONLY when actual selected consumers need v2 and explicit existing closed P2 JSON project/local config uses exact integer 1. Defaults/already-v2, unselected absent files, legacy YAML/provenance and records need no conversion. Input has only accepted Lesson fields; project may contain its write_roots/locked_fields, local has no constraints. Reject unknown roots/namespaces, duplicates, invalid/null values, nonfinite numbers and bool/float versions. Selected pair versions agree.

Output integer 2 preserves every other semantic value AND absence: no namespace/default/decision-source/permission/authority addition. Raw formatting may change with preview; durable original raw bytes remain. Adding namespaces is a separate project action. Old P2 tools reject v2. Lesson record 1->2 is not selected; derive creates a new identity.

Package project_data_action remains none. Separately assigned P6 config-transition owner provides plan/convert/recover for this one edge in agreement with actual config owners. It uses the maintenance-writer lock and explicit quiescence declaration, not an invocation runtime. Its own immutable marker records incomplete pair conversion; readers are stopped by caller, not marker enforcement. Capture durable exact before/after bytes first; individual replacements are not pair-atomic. Completion verifies only selected closed conversion semantics and consistent pair, then removes its marker. Project/capability readiness remains not-assessed by this mechanical outcome.

Project sequence: stop affected activity; select exact M01 only if needed; complete/recover pair under its owner; recompute separate package plan against actual input hashes; perform package maintenance; then project uses separately selected public reader(s) for intended activation. No automatic generic compatibility registry/plugin or data scanning. Unknown compatibility is unresolved, never passed. Caller keeps affected capabilities disabled until its checks/decision permit use.

Package failure does not undo M01. Explicit M01 restore/new restore plan requires exact current files match captured after bytes, preserving later edits. Never reverse new v2 namespaces/constraints by merely replacing the integer. Missing backup or external edit blocks restoration. M01 completion/recovery makes no data compatibility guarantee.

Metadata-v3 instruction/tool and null-config semantics remain #346's shared loader/adapter responsibility. Installer consumes actually delivered candidates/metadata; it does not invent packages, require runtime/config for instruction-only packages or integrate ordinary instruction/tool invocation. This maintenance design requires no new common adapter launcher.

## Unexecuted P7 cases

Design cases only, not tests or fixtures run here.

| Case | Required result |
| --- | --- |
| Equal candidate rebuilt | No managed/control writes, snapshots or mtime churn. |
| One changed template, unchanged runtime | Replace only changed member; exact lock update; durable snapshot may still write. |
| Mode-only delta | POSIX actual mode; Windows declared inventory only, no byte rewrite. |
| Removed owned member + unknown sibling | Preserve sibling/directory. |
| Identical unowned destination, drift/alias/reparse | Conflict; no adoption/force. |
| Partial candidate/wrong hash/version | Refuse before mutation. |
| Missing/false maintenance declaration | Missing blocks; truth unverified. Concurrent external writers unsupported. |
| Two participating maintenance writers | OS lock excludes second for entire operation; no file-existence/timeout unlock inference. |
| Agent has old instructions loaded | Caller must stop/restart affected session; marker cannot control it. |
| Crash during snapshot | No managed mutation; incomplete durable set inadmissible. |
| Crash after marker/between members/after lock | Recovery-needed, caller keeps capabilities disabled, explicit hash-bound finish/restore. |
| Open Windows file/denied replacement | Retain marker/objects; recovery-needed. |
| Candidate/staging RAM loss | Durable managed set sufficient, same pinned external engine required. |
| Full RAM project lost | Managed reconstruction only; missing data disclosed; never whole-project ready. |
| External edit during interruption | Preserve conflicting bytes; no blind restore or TOCTOU claim. |
| Completed old operation replay | Refuse mutation; fresh maintenance plan needed. |
| M01 partial pair/new v2 fields | Conditional recovery; never erase later meaning. |
| Defaults/already-v2/null-config skill | No M01/config creation/runtime requirement. |
