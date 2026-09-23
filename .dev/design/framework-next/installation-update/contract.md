# Managed installation contract proposal

Design only, proposed for #345. No operation below exists by virtue of this document. [Evidence](source-evidence.md), [formats](formats.md), and [cutover decisions](cutover-and-slices.md) form this bounded design. Implementation/activation require coordinator selection; U001 defers execution to P7.

## Version and support boundary

Propose engine `framework-managed-installation@1.0.0`, API integer `1`, lock integer `1`, operation integer `1`. These are proposed contract versions, not a framework release or implemented executable. Accept development candidate selection/files/build JSON with exact integer `schema_version:1`, `mode=development`, `release_version=null`, builder `framework-development-assembly`. Manifest/profile v1 and metadata v1/v2 retain their owners. Metadata v3, stable archives, floating labels, historical chains and cross-engine recovery remain unsupported until selected. Bool/float/string versions do not equal integers.

First transitions: absent installation -> one exact development candidate, or valid v1 installation -> another explicit candidate under this exact engine. Profile change is a complete selection change, never implicit dependency solving. Removal follows exact old inventory. Downgrade additionally needs compatible config/data readers. Semver, equal paths and unchanged package bytes are not compatibility proof.

Read all three candidate documents, recompute bindings and inspect every listed file. Require raw bytes, declared Git mode, regular files, exact allowed destinations, member/adapter closure. Reject missing/extra candidate files, path/owner/source disagreement, case/prefix collisions, links/reparse points, unsupported versions, incomplete build metadata and mismatching hashes. `outcome=assembled` alone is insufficient. Canonical fields are in [formats](formats.md). Unknown candidate format fails; unknown target content is preserved.

Digests prove integrity, not signatures or trusted publication. Caller explicitly approves candidate identity. No fetch, credential discovery, runtime installation, rebuild or silent engine substitution. Running engine is pinned outside managed destinations and cannot update itself in this operation.

## Public operations

Product facade proposal: `src/distribution/installation.py`. A thin source invocation may call it; this does not select #149/#168 public CLI runtime or enable preview mutation commands.

| Function / API operation | Inputs and result |
| --- | --- |
| `inspect` | Explicit absolute project root, optional candidate root. Read-only integrity, owned/unknown/drift inventory, mode limitations and `uninstalled`, `ready`, `drift`, `recovery-needed`, `unsupported` or `blocked`. No runtime/data-compatibility claim. |
| `plan` | Exact candidate/root, expected raw lock hash or null-for-absence, mode policy, explicit scratch/staging/recovery roots, durability declaration, selected config paths and P5 compatibility selection. Read-only delta/collisions/protected inputs/path budget/prerequisites and deterministic plan hash. No mkdir. |
| `apply` | Plan inputs plus exact accepted plan hash. Recompute under exclusive coordination; fail on change. `unchanged` writes nothing. Otherwise establish durable before/after set, stage, block execution, mutate exact members, verify, publish lock, unblock. Return `applied`, `conflict`, `unsupported`, `blocked`, or `recovery-needed` with actual counts and recovery locator. |
| `recover` | Explicit root, durable operation directory/hash, `direction=finish|restore`, expected current observed lock hash/null. No candidate or scratch dependency. Return `recovered`, `conflict`, `blocked`, `unsupported` or `recovery-needed`; never choose direction or erase unknown state automatically. |
| `guarded-invoke` | Explicit installed skill/tool/operation plus project inputs. Hold coordination throughout invocation; verify marker absent, matching entire lock/core/runtime and exact installed entry. Invoke only declared interface. Package still owns config/data validation and actual operation authority. |

API 1 requests/results have operation-specific closed fields in [formats](formats.md). Plans/results are transient, not admission receipts. No force/adopt-existing/overwrite-drift, uninstall, generic migration, cleanup scheduler or arbitrary shell operation. Package removal means another nonempty supported profile; whole uninstall needs later selection.

No-op means candidate content identity, inventory, mode policy and actual owned state are equal. Rebuilding with another run UUID/time/build.json cannot change lock. No marker/staging/backup or lock rewrite. Plan still checks prerequisites; byte equality cannot bypass them.

## Ownership and delta

| Surface | Authority |
| --- | --- |
| `.ai/framework.lock` | Installer-generated; project reviews/tracks alongside outputs. Never builder input, payload or hand-edited provenance. |
| `.ai/core/skills/<id>/<member>` | Exact payload destinations from accepted candidate and old lock only. |
| `.agents/skills/framework-<id>/SKILL.md` | Exact Codex destinations only; no sibling/custom/runtime-directory ownership. |
| `.ai/framework.operation` | Package blocking marker, identical to durable operation.json. Presence/unreadability/malformed content means recovery-needed. Never committed as active installation. |
| `.ai/config-transition.operation` | Separate M01 owner marker with identical durable M01 record; also blocks managed readers. Package engine cannot delete it. |
| `.ai/local/installation.guard` | Inert coordination file reserved by explicit first adoption, never replaced/unlinked in ordinary use. Held native lock controls concurrency; contents confer no authority. No serialized lease/receipt. |
| `.ai/custom`, `.dev`, selected config/templates/stores, root entries and unknown files | Project-owned; no implicit adoption, copy, conversion, chmod or recursive cleanup. |

Check actual old bytes/mode for ALL old members, including unchanged ones. Compare raw SHA-256, length and Git mode. `unchanged`: same descriptor; `add`: absent old and absent target; `change`: owned old differs from new; `remove`: old owned absent new. Byte-identical unowned target still conflicts on add. Parent/child occupation, aliases and unknown files blocking new paths conflict. Unknown siblings are disclosed/preserved; leave empty directories. Directory membership grants no deletion authority.

POSIX means materialized 0644/0755. Windows `inventory-only` retains 100644/100755 in lock without claiming ACL/executable-bit enforcement. Windows mode-only delta changes declared inventory/lock with zero member byte writes; return `mode-not-materialized`. Equal bytes/declared mode incur no write/chmod/mtime churn. Platform/mode-policy changes need a new explicit plan or unsupported result. No ACL/owner/ADS preservation claim follows from byte/mode parity.

Drift choices belong to project owner: preserve/select different capability or destination; repair source/build explicit candidate; independently reconcile/move customization. Engine executes none of them; re-plan afterwards. Legacy `.ai/assets`/wrappers never become managed merely by similarity.

## Explicit roots and paths

Caller supplies existing absolute direct roots. No disk discovery, upward search, fallback, parent creation, global TEMP/TMP changes or volume-root stores. Reject traversal, drive-relative/device/UNC paths, links/reparse ancestors, ambiguous Windows names, overlapping project/candidate/recovery/staging/scratch roots except scratch/staging may share one selected parent. Candidate and recovery are outside project. Recovery cannot be within candidate/disposable roots. Recheck containment at use.

Allocate one random 32-hex operation ID with exclusive creation:

- `<scratch_root>/i-<id>/`: disposable calculations; RAM allowed.
- `<staging_root>/i-<id>/`: changed-file preparation; RAM allowed. When parents equal, use the same run directory.
- `<recovery_root>/i-<id>/operation.json`, `objects/<sha256>`: durable operation, managed before/after bytes and metadata. Explicit caller declaration covers selected failure domain; drive label/type/path does not prove durability.
- Destination sibling `.fi-<12hex>` for current member/lock/marker: exclusive allocation, suffix is the first 12 lowercase hex characters of SHA256(UTF8(operation_id + NUL + destination)); check uniqueness across this operation and exclusive absence on disk. A collision blocks, never overwrites. Short name rather than mirrored long filename. The complete temporary path set is derived from the immutable operation and known control destinations; recovery removes a leftover only if its bytes match an expected before/after/control object and it is not an active destination. Otherwise preserve/report conflict. Report/retain failures. Cross-volume copy is never called atomic; use verified bytes and supported same-directory single-file replacement.

Budget actual candidate/final/scratch/staging/recovery/control/sibling paths. Propose Windows full-path budget 240 UTF-16 code units and segment budget 255, counting any terminator/backend extra requirements. This is a conservative product refusal budget, not a universal OS limit. A backend may be stricter. Refuse before material writes; diagnostics show role/relative destination/length/limit without absolute host paths. No host or Git long-path settings edits; #305 still needs execution evidence.

Stage changed/add bytes and control documents only. Durable recovery is different: retain ALL old and new owned member bytes plus exact old/new lock and candidate metadata before managed mutation; deduplicate by SHA within this operation. Complete managed recovery, never whole repository copy. No global cache/retention service. Preserve completed/failed durable directories; later explicit cleanup is outside v1. Disposable scratch loss never replaces recovery proof.

## Guard and activation

All supported managed entrypoints join one guard. This is a distribution entry boundary, not a shared runtime imported into independent skills. Propose an exclusive native OS file lock on the inert guard file held throughout invocation/apply/recover; serialize v1 instead of shared-reader leases. Handle release follows process termination; file existence is not lock ownership. Native backend is a P7 prerequisite; never remove guard to break a live lock. Nonparticipating actors are outside coordination; rechecks protect accidental drift, not a malicious concurrent writer sandbox.

Current Codex template links resources but has no executable installation gate. Markdown instructions alone cannot enforce it. Before activation, coordinator supplies shared guard/launcher and exact supported route. Direct package scripts remain unsupported managed execution unless integrated with that guard. Engine/guard must run outside `.ai/core` so replacing files cannot replace recovery authority. First adoption reserves guard path explicitly; unknown existing control paths require reconciliation.

Guard requires readable supported lock, BOTH package/config markers absent, matching entire inventory and selected invocation inputs. Root policy/adapter route through it. Missing/malformed lock fails closed; in-flight invocation finishes before apply gets guard. Retained agent text gives no bypass permission. Every invocation rechecks installation then delegates config/schema/authority validation to package.

Apply sequence under guard:

1. Recompute candidate/lock/complete drift/protected-input/accepted-plan checks. P5 owns selected config/data compatibility. No conversion runs here.
2. Prepare next lock and durable complete before/after closure. Finish/flush where supported/read back hashes and modes, write operation.json last, read back. Incomplete preparation causes zero managed mutations. Durability requires selected backend/failure-domain evidence, not merely successful flush.
3. Create exact marker and read back with supported directory-durability ordering BEFORE member changes. Keep last-good lock untouched. Existing/partial/invalid marker admits only explicit recover.
4. Recheck each old path immediately before replacement/removal. Use verified durable bytes if disposable staging vanished. Never truncate active file in place. No per-file journal; old/new states determine completion.
5. Read back whole new inventory and protected inputs; marker remains. Replace next lock via same-directory primitive and verify exact bytes. New lock with marker still blocks runtime.
6. Recheck matching state/readiness; remove only this exact marker, read back absence and inventory/lock, then return applied/release guard. Failed durability/cleanup/read-back stays recovery-needed. Retain durable set.

No cross-file/directory/volume/whole-operation atomicity claim. Single-file and flush semantics are backend-specific and must be implemented/tested in P7. Backend unable to establish marker-before-mutation and lock-before-marker-removal ordering for selected failure model blocks apply. Corrupt/missing lock or mismatching members block even if marker was lost.

States are observations, not mutable phase fields:

| Observation | Interpretation |
| --- | --- |
| No lock/marker, no destination conflict | Uninstalled; may plan. Legacy files remain project-owned. |
| Supported lock, matching inventory, no marker | Managed bytes ready; config/data/capability/authority checks remain. |
| Durable complete operation, marker absent, old matching state | Prepared, not active; begin only against original accepted inputs. |
| Marker invalid/present, mixed before/after or torn lock | Recovery-needed, normal invocation blocked. |
| Marker present, matching new lock/files | Activation incomplete; explicit finish may recheck and clear marker. |
| Marker absent, matching new lock/files | Completed content state; no historical receipt inferred; old operation cannot authorize replay. |

## Recovery and RAM-disk loss

Read exact durable operation and both complete lock object sets with the same engine version. Package recover refuses an active M01 marker; its owner must finish/reconcile it first. Caller also supplies expected current marker hash/null; a valid unrelated marker always conflicts. Check project binding, caller's expected observed current lock and marker. Existing lock may equal before/after, or null only in a defined absent state. Unrelated valid lock, unknown member bytes or reparse/control-file disagreement needs reconciliation. A torn lock can be repaired only at this operation's control path with explicit selection of its current observed hash; never overwrite another valid installation.

While marker exists, affected paths may be before, after, or the absence defined for add/remove. Finish writes after; restore writes before and removes only additions still matching after. Unknown bytes/modes conflict. Preflight whole set, then recheck each path. An unexpectedly missing previously present member is drift, not blanket restore authority. Interrupted restore uses same record; no reverse journal. Matching unchanged members receive no rewrite.

Once marker is removed and a complete valid installation exists, recovery from a retained operation is read-only: already-matching or conflict. A later downgrade is a fresh package plan with current config/data checks and recovery capture. Old operation cannot authorize rollback after activation/use.

After complete RAM-worktree loss, caller restores project-owned source/config/data through normal durable Git/backups and supplies exact operation directory. `reconstruct_missing_managed=true` is allowed only for absent lock/marker and wholly absent managed set at the same explicit project root; partial unexpected absence does not qualify. Recreate blocking marker first, then full previous lock/core/runtime from durable objects without original scratch/candidate. Relocation/other installation ID needs reconciliation outside v1. Clean-install before is null: restore removes only recognized additions and leaves uninstalled.

This cannot recover project data whose only copy was RAM. Missing/changed required config/data, missing durable object, unproven durability, unavailable exact engine or unreadable previous contracts blocks activation. May retain restored bytes with marker and remaining prerequisite, never call core-only restoration matching recovery. Unknown files/new external edits remain untouched. Package engine never restores project data.

## Selected P5 M01 boundary

Coordinator follow-up supplied immutable selection `842b73ca09d701d1561109255193d80439dc996b`, read with Git show without merging it. [P5 selected contract](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/p5-selected-contract.md) and [M01](https://github.com/YuChia-Wei/ai-collaboration-framework/blob/842b73ca09d701d1561109255193d80439dc996b/.dev/design/framework-next/capability-consolidation/implementation-slices.md) supersede the previously unavailable-edge observation. Only this one edge is selected for P6 design; it is not implemented or executed.

M01 is necessary only when actual selected consumers need v2 and explicit existing P2 JSON project/local config is version 1. Defaults, already-v2, absent unselected files, legacy YAML/provenance and records are outside conversion. Input is exact integer 1 with closed Lesson namespace, valid optional store/template settings and project write_roots/locked_fields. Local permits no constraints. Reject unknown keys/namespaces, duplicates, null/invalid settings, nonfinite values and bool/float versions. Selected project/local pair must agree.

Output is exact integer 2 with all other semantic values AND absence unchanged. Preserve namespaces, write_roots, locked_fields and store/template settings. Do not add defaults, namespaces, decision_sources, permissions or authority. Raw encoding/formatting may change with explicit preview; retain exact raw before-bytes. New namespace authoring is a separate project action. Old P2 tools reject v2; changed version does not prove compatible runtime adoption.

Package API keeps `project_data_action=none`. M01 uses separate future config-transition public operations `plan`, `convert`, `recover`, owned by a coordinator-assigned P6 config-transition implementer in agreement with Lesson and v2 consumers. Its exact conditional recovery format is in [formats](formats.md); it is not a generic conversion engine or an installer side effect. The engine never imports another skill's private config resolver or rewrites package metadata parsers. Existing/new loader authority remains #346/coordinator.

M01 plan binds exact selected file paths and before hashes, proposed after bytes, actual need, consumer compatibility and explicit durable root. Convert uses the same project coordination boundary and its own blocking marker; package and config transitions cannot overlap. Capture durable before/after bytes before changing either file. Per-file replacement cannot be pair-atomic. Both markers block selected readers; hold activation until the pair agrees and selected consumers accept it. Recompute versions/digests before each write and completion. State is inferred from before/after hashes, not a mutable progress log.

Sequence for a real v1 project needing a new v2 consumer: quiesce selected readers; plan package and M01 separately against their actual inputs; complete M01 under its owner; keep incompatible old readers inactive; recompute package plan against actual v2 config; apply package; activate only matching readers/pair. A package failure does not undo M01. Restore config only by explicit M01 recovery/new restore plan that proves the complete files still match its after bytes and no later namespace/constraint/meaning would be lost. Never down-convert newly edited v2 documents by changing the integer back. Missing matching backup, partial pair, external edits or unknown shape remains recovery-needed/unsupported.

Lesson record 1.0.0 -> 2.0.0 is not a selected mutation edge: current Lesson reads both and derive creates new identity. Historical journals/records remain preserved/unsupported.

D342-01 selects metadata v3 instruction/tool union and restricted configuration:null for future source. At this base only v1/v2 loader/candidates are delivered. Future installer support must consume #346's actual delivered loader/adapter and exact candidate selection metadata, never implement a competing metadata parser or assume #347/#348 planned packages exist. V3 instruction-only/null-config packages must not trigger config discovery/conversion/Python requirements. Guarding an instruction read differs from running a tool; the external distribution entry boundary must be explicitly extended before v3 activation. No shared skill runtime or per-skill private import is proposed. The adapter/guard extension is a coordinator decision, not new source in #345.

Compatibility is a fresh check by the exact selected package/config owners and actual inputs, not a persisted pass flag or arbitrary report title. A general cross-skill compatibility scanner is not selected. Until the narrow public read/check interface is selected, return compatibility-unresolved for transitions needing it. Equal hashes alone are not reader proof. This remaining dependency is distinct from M01 edge selection, which is now resolved.

## Unexecuted P7 cases

Design cases, not tests or fixtures run here.

| Case | Required result |
| --- | --- |
| Equal candidate rebuilt at another time | No member/lock/mode/mtime writes or operation directories. |
| One template changed, entry unchanged | Only changed member replaced; entry untouched; lock changes; durable snapshot may still write. |
| Mode-only delta | POSIX actual mode enforcement; Windows inventory-only change, no byte rewrite. |
| Removed member + unknown sibling | Remove matching owned member; preserve sibling/directory. |
| Byte-identical unowned destination | Conflict, no adoption. |
| Owned drift/missing member/alias/reparse | Refuse apply; no force path. |
| Partial build, wrong digest, unsupported version | Reject before target mutation. |
| Interruption during durable preparation | No managed mutation; incomplete operation inadmissible. |
| Crash after marker/between members/after lock | Guard blocks; explicit finish/restore recognizes hashes. |
| Open Windows file/denied replacement | Recovery-needed; retained marker/objects; no unchanged retry. |
| Candidate/staging RAM lost | Complete durable set sufficient for managed recovery. |
| Whole worktree RAM lost | Reconstruct project data separately, explicit absent-managed recovery. |
| External edits during interruption | Preserve, conflict, no blind overwrite. |
| New installation used, marker absent | Fresh downgrade plan, no old-operation replay. |
| Missing object/engine mismatch/config loss | Block activation, no invented backup. |
| Path over budget/unsupported flush backend | Refuse before mutation; P7 resolves, no host setting change. |
| Concurrent managed invocation | Native coordination conflict; no lease-breaking timeout. |
| M01 first file changed, second blocked | Pair inactive; exact before/after conditional finish/restore only. |
| M01 v2 gains namespace after conversion | No integer-only reverse; preserve new values and report unsupported recovery. |
| Defaults/already v2/null-config instruction skill | No M01, no config creation. |
