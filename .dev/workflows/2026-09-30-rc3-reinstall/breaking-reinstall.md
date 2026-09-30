# Git-backed breaking reinstall contract

`python -I -B ENGINE/tools/reinstall-framework.py < request.json` is an explicit
opt-in entry shipped in the pinned Engine 2 bundle. Ordinary API 2 plan/apply
keeps its existing no-destructive-cleanup contract.

The closed request contains `reinstall_version: 1`, `operation: plan|apply`,
`project_root`, `expected_head`, sorted `cleanup` and `preserved_inputs` arrays
of `{path, sha256}`, `preview_root`, `installation`, `maintenance` and the exact
boolean `all_framework_activity_stopped: true`. Apply also
requires the exact returned `expected_plan_sha256`.

`installation` is the ordinary API 2 plan request, using the selected catalog
subset, independent engine pin, scratch/staging/recovery roots, explicit project
edit objects, bindings and protected inputs. Its `expected_lock_sha256` is null
because this operation retires the old lock. `maintenance` is a fresh truthful
quiescence declaration for the selected new component union. The caller stops
all old framework activity as well as that new scope for the entire reset.

Preservation accepts exact native Unicode or interior-space names for existing
project history, with the same containment, alias, link and preimage checks.
Managed package, cleanup and API 2 edit paths retain the portable ASCII contract.
This does not rename historical files or make them writable managed members.

All roots are explicit, direct and disjoint. The caller-selected external preview
directory receives retained input fixtures, and ordinary API 2 planning must
pass there before project cleanup. Preview writes are reported separately from
the project `changed` flag. A reused preview must contain exactly matching input
bytes; unrelated files fail. Choose a new empty preview after input changes.

The operation inventories `.ai`, `.dev`, `.agents/skills` and `.claude/skills`
completely within bounded limits. Every existing scoped file must be explicitly
classified as cleanup, preservation or an API 2 project edit. Cleanup is limited
to currently Git-tracked framework resource files in a clean worktree at the
exact selected commit. Untracked/ignored data, links, hard links, aliases,
mount/volume crossings, hidden Git index flags, custom Git content filters and
workflow-record cleanup (including the v2 store) are refused. Cleanup content
must hash to its selected Git blob under Git's normal text conversion. A current
maintenance marker blocks the reset. Root wrappers can be reconciled using
explicit project edits; this grants no whole-repository cleanup authority.

The plan exposes exact cleanup preimages, complete scoped inventory, preservation
hashes, candidate/engine identities, Git baseline and the new installation
preview. Apply recomputes it, checks its hash and re-observes preimages before
the first cleanup syscall. A preexisting inert writer guard is explicitly
acknowledged, checked with native participating-writer exclusion and reset under
the caller's declared quiescence. It is coordination storage, not a user file.

**This is a destructive, non-atomic reinstall.** It does not promise lossless
legacy migration or automatic rollback. Git at `expected_head` owns recovery of
committed cleanup files. The ordinary installer journal owns recovery after new
installation begins. `cleanup-incomplete` retains the actual removed paths and
the installer result if any; it is never reported as success. A process killed
during cleanup requires comparing the exact planned path list with Git before
retry. Neither an incomplete old operation nor new operation is bypassed.

Successful `reinstalled` means selected new managed bytes/lock read back, selected
obsolete files are absent and preserved file hashes match. Project/runtime
readiness, application tests, Git integration and publication remain separate.

## Dense preservation previews

The external preview observes its existing namespace completely before writing,
then verifies a fresh bounded snapshot of the complete materialized closure and
retained bytes. This avoids repeatedly scanning growing sibling directories.
The entry and byte limits remain unchanged; cleanup starts only after preview
verification and the ordinary installer plan both pass.
