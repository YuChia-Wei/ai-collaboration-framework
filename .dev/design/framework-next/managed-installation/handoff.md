# Managed maintenance implementation handoff

Source implementation for [Issue #359](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/359),
under [selected P6](../p6-selected-contract.md) and the
[writer assignment](../p6-writer-handoff.md). The actual #354 reader/planner
`8be2f8ab807764cdd691cf81b537811c30bc64f7` is reused, including the delivered
metadata 1/2/3 loader. This checkpoint has no executed installation or native
behavior evidence. U001 deferrals are source workflow authority only; product
code contains no U001 switch or permanent disabled writer.

## Entry, dependencies and engine closure

The fixed development entry is `src/tools/maintain_framework.py`. Future caller
invocation is `python -I -B <explicit-checkout>/src/tools/maintain_framework.py`
with exactly one UTF-8 JSON request on stdin and one JSON result on stdout. There
are no command options, help command, fetch/install actions or skill launchers.
Exit 0 means a successful operation result, 1 a reported refusal, 2 an unexpected
dispatch/interruption/output failure with no fabricated success/unchanged result.
The exit code alone is not project readiness or provider acceptance.

Host prerequisites are Python 3.10+ and already provisioned PyYAML 6.x in the
isolated interpreter's system/explicit virtual environment. Nothing installs or
changes dependencies. `-I` excludes cwd, PYTHONPATH and user-site search; `-B` and
an immediate `sys.dont_write_bytecode=True` precede product/dependency imports.
Interpreter, standard library, installed PyYAML and native OS libraries are
explicit host prerequisites, outside the local source pin. No loaded-memory,
host-software authenticity or cryptographic source attestation is claimed.

EnginePin remains exactly `{id,version,source_commit,files}`, with
`framework-managed-installation`, `1.0.0`, a full lowercase 40/64-hex checkout HEAD,
and the following sorted complete raw SHA-256 file set:

1. `src/distribution/__init__.py`
2. `src/distribution/data.py`
3. `src/distribution/git_source.py`
4. `src/distribution/installation.py`
5. `src/distribution/installation_io.py`
6. `src/distribution/installation_plan.py`
7. `src/distribution/installation_state.py`
8. `src/distribution/maintenance_coordination.py`
9. `src/distribution/package.py`
10. `src/tools/maintain_framework.py`

The entry verifies its own exact external checkout and every local file before
product import. It explicitly loads the known distribution package without adding
the checkout to sys.path; local files cannot become an ambient standard-library
or dependency search directory. The state owner rechecks raw hashes, loaded module origins, exact
local import closure and observed files-backend Git HEAD. `ENGINE_FILES` is the
executing closure; `READER_ENGINE_FILES` retains the historical six-file subset
for identification, not writer admission. There are no additional source resource
files loaded by the maintenance engine. Package schema/reference bytes come only
from the selected candidate/durable objects and use the existing package owner.
No extra installation schema was introduced without a distinct reader need.

The bootstrap marker in memory records that entry path, not a security boundary
against a caller already executing arbitrary Python. Public operation admission
requires that fixed entry. Low-level reader dataclasses/helpers remain untrusted
as mutation evidence. The package does not invoke GitSource, assembly, selection,
adapters or a provider. Checkout/raw observations do not prove loaded-memory
identity, whole-commit byte equivalence, publication or source authenticity.

## Closed API and files

`distribution.installation` exposes `execute`, `inspect`, `plan`, `apply`, and
`recover`. `execute` selects exactly those four operations; the facade checks all
request keys/types again. Inspect delegates to installation_state; plan and
locked apply share installation_plan's `_prepare`. There is one candidate
metadata semantic implementation (`_candidate_documents`), one lock reader
(`_lock_bytes`) and the actual package metadata/reference owner; recovery does
not reproduce the metadata parser.

Every request has exactly `api_version=1`, `operation`, `project_root`,
`engine_root`, `engine`, plus the following closed fields:

| Operation | Additional fields |
| --- | --- |
| inspect | Optional `candidate_root`. |
| plan | `candidate_root`, `candidate_identity`, `expected_lock_sha256` (null = absent), `mode_policy`, `scratch_root`, `staging_root`, `recovery_root`, `durability`, `protected_inputs`, `project_data_action="none"`. |
| apply | All plan fields, `expected_plan_sha256`, `maintenance`. |
| recover | `operation_root`, `operation_sha256`, `direction="finish"|"restore"`, `expected_lock_sha256`, `expected_marker_sha256`, `maintenance`; optional exact boolean `reconstruct_missing_managed` defaults false. |

Durability has exactly `declared_by`, `declaration_reference`, `failure_domain`.
Maintenance has exactly `declared_by`, `declaration_reference`, the sorted exact
`affected_capabilities`, and exact true `sessions_stopped`, `tools_stopped`,
`external_writers_stopped`. Each call requires an explicit new declaration; its
truth, real freshness and continued quiescence cannot be technically attested.
No arbitrary agent/reader is controlled by the lock or marker.

The [selected formats](../installation-update/formats.md) remain lock 1,
operation 1 and API 1. Successful plan is exactly
`{api_version,operation,outcome,plan,plan_sha256}`. Other results are exactly
`{api_version,operation,outcome,changed,details,diagnostics}`. Apply/recover details
are exactly `managed_state`, `project_readiness`, `lock_sha256`, `operation_root`,
`counts`, `protected_input_state`. Project readiness is always `not-assessed`.
Counts have `added`, `changed`, `removed`, `unchanged`; they describe successful
member syscalls/verified unchanged rows in this call, not planned counts or
historical work. Missing-target rows can count unchanged on recovery. Controls,
parents, mode and preparation writes affect `changed`; Windows declared-only
mode updates cause no member-byte rewrite and emit `mode-not-materialized`.
Bootstrap-unavailable counts are null. Failure lock identity is null when a prior
read cannot establish current state. Diagnostics use relative paths or null;
only the explicit result operation locator carries an absolute recovery path.

## Mechanical admission and native support

Preview verifies candidate/old-lock integrity, all old members (including
unchanged), unowned collisions even for identical bytes, selected protected
inputs, root/path budget, fixed engine and native filesystem/domain support.
It does not acquire a lock. Pending writer-guard, fresh-input, declaration and
exclusive-allocation prerequisites are discharged only after those actual
conditions occur. Lock-publication and mode entries describe the checked format
and selected primitive capability; their successful execution is a later
postcondition, not a preview pass. No P7 evidence flag substitutes for admission.

| Native selection | Coordination and file operations | Limits |
| --- | --- | --- |
| Windows, local fixed/RAM NTFS or ReFS | Empty reserved guard plus nonblocking LockFileEx; same-parent MoveFileExW with WRITE_THROUGH and optional REPLACE_EXISTING; exclusive creation, file fsync, exact read-back, unlink. | Inventory-only modes. No directory-fsync/power-loss, ACL, ADS, unrelated ownership or remote-filesystem guarantee. |
| 64-bit Linux, libc renameat2; ext4-family, XFS, Btrfs, tmpfs or ramfs | flock LOCK_EX/LOCK_NB; same-parent renameat2 (RENAME_NOREPLACE for absent target); exclusive creation, fchmod 0644/0755, file and directory fsync, exact read-back, unlink. | Unknown/network/overlay filesystems and unavailable primitives refuse. Native filesystem/flush behavior still requires P7 execution. |

Supported declaration strings are `process-termination` (OS and storage remain
available) and `project-volume-loss` (recovery storage survives separately).
The latter requires different observed project/recovery devices and a recovery
volume not reported as RAM. Drive/filesystem identity and caller assertions do
not prove physical durability. Power loss, OS crash/reboot loss, controller/media
failure and a missing recovery store are unsupported. Recovery of a lost external
engine requires the caller to supply the same checkout/pin; the tool never fetches
it. A RAM-disk pretending to be a fixed disk is not detected as physical RAM.

All declared roots already exist and are direct/local/disjoint; only identical
scratch/staging parents may coincide. Nested mount/volume transitions beneath
operation roots refuse. Symlink/reparse/hardlink/case/prefix collisions refuse.
No fallback root, global TEMP/TMP edit, recursive cleanup or data-store scan.
The native exclusion protects participating maintenance writers only. External
concurrent writers are unsupported; hash checks do not eliminate TOCTOU.

## Actual allocation, capture and order

Apply previews before even first-install guard/parent writes, selects one random
32-hex ID, then checks the complete actual layout and absence under each explicit
root. Under the held native handle it recomputes the accepted plan, declaration,
old bytes and candidate again. No-op creates no ID, directory, snapshot, marker,
lock rewrite or chmod and requires an existing empty direct guard. Guard creation
on first install and every parent/temporary write is reflected in partial changed
state. Guard existence is not ownership of an OS lock; no path is unlinked or
replaced to break a lock.

The actual names are `i-<32hex>` under scratch/staging/recovery,
`objects/<64hex>` plus immutable `operation.json` in recovery, scratch metadata
and `plan.json`, and staged changed/add byte files plus the next lock. Mode-only
members are not staged. When scratch/staging coincide, their next lock is created
once. Project siblings are exactly `.fi-<12hex>`, where the suffix is SHA256 of
UTF-8(operation_id + NUL + destination). Prefix/name and protected-input overlap
checks cover all real names. Every actual path is checked against 240 full-path
and 255 per-segment UTF-16 limits before allocation; no native certification is
implied. Root/containment is checked again at use.

1. Preserve raw old/new locks, all old/new managed bytes and all three candidate
   metadata documents, deduplicated by SHA within the one durable operation.
   Flush and read back every object. Create operation.json last and reread the
   complete parsed closure and shared package bindings. Partial capture cannot
   admit managed mutation.
2. Publish an identical immutable project marker through its same-directory
   sibling. Only after marker read-back may managed mutation start. No mutable
   phase counter, per-file journal, receipt or whole-project backup exists.
3. Recheck every admitted current file immediately before replacement/removal;
   never truncate an active managed destination. Mode-only POSIX work uses
   fchmod without replacing bytes. Verified durable object bytes remain usable
   if candidate, scratch or staging disappears.
4. Verify the entire desired managed union, including removed-path absence and
   selected protected inputs. Publish/read back the new lock only then. Recheck
   the entire target again, remove this exact marker last, then read back
   absence, lock, files and selected protected inputs while still coordinated.
5. Return actual counts/changed/state. Any failed preparation, mutation, flush,
   read-back or unlock remains a failure with retained evidence. At most 24
   bounded preparation-write locators are included in failure diagnostics; this
   is a transient diagnostic prefix, not a complete residue inventory or journal.

Operation directories are never removed. Empty project parents and guard are
retained. There is no cross-file/directory/volume/whole-operation atomicity.
The shared 128 MiB read budget includes bootstrap reads, repeated source/current
observations and durable read-back; repeated writer passes consume it. Other
reader limits remain as described in the [reader handoff](../installation-planning/handoff.md).
An over-limit call fails truthfully even if preparation already happened.

## Recovery refusal and reconciliation boundaries

Recovery needs the explicit immutable operation/hash, same complete engine pin,
original canonical project/operation roots, fresh exact-scope declaration and
expected observed lock/marker hashes. Both locks, all objects and three metadata
documents are revalidated before mutation and reread under coordination. Current
members may be exact before, exact after, or the absence implied by add/remove.
Unknown/newer bytes or modes, unexpected partial loss, unrelated/torn controls,
active M01 marker, incomplete objects and engine drift are preserved and block.
Atomic control publication means no torn control is expected in the selected
process-termination model; an unrecognized control is never guessed attributable.

Finish targets after; restore targets before and removes only recognized additions.
With marker absent, a complete matching target is `already-matching`; another
state requires a fresh plan. A retained completed operation cannot authorize a
post-use rollback. A prepared upgrade with no marker and the valid old installation
is likewise read-only recovery evidence; applying the upgrade needs a fresh plan.
No-op recovery also cannot create a missing guard.

Whole-loss entry requires explicit `reconstruct_missing_managed=true`, absent
lock/markers and the entire old/new managed union absent at the original recreated
root. It may recreate coordination and the same marker, then restore only the
selected managed set. Missing selected protected files are reported unresolved;
conflicting present protected files block. Source/config/data stay separately
owned and readiness remains not-assessed.

Conservative cases requiring owner reconciliation, not silent cleanup or broader
recovery authority:

- A partial/unknown sibling is preserved. Only complete exact captured sibling
  bytes/mode may be removed by recovery. First-install failure before a complete
  record can leave empty parents/guard and partial run files.
- Restoring a clean install leaves its empty coordination resource. A later
  clean-install plan cannot adopt an unowned preexisting guard; owner reconciliation
  is needed. No automatic guard unlink is introduced.
- If whole-loss reconstruction itself is interrupted with some originally
  present members still missing, the immutable original operation cannot prove
  whether those absences came from reconstruction or unrelated partial loss.
  The next call blocks that ambiguity. This implementation does not invent an
  extra state format/journal or relax the whole-absence entry condition.
- A completed marker removal followed by a failed read-back/unlock is reported
  failed; a later explicit exact observation can establish already-matching.

These limits and [P7 cases](p7-cases.md) require coordinator/P7 consideration before
any pilot, not an inferred activation approval. Any broader recovery guarantee
needs a selected contract decision. M01 remains unassigned without demonstrated
need; project adoption, #149 CLI/runtime selection and #346/#347 blocked scope
remain with their owners.
