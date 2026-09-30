# RC3 worker branch closeout

Owner authority: the 2026-09-30 conversation requested that necessary remaining
work be made usable and integrated, rather than left on unfinished branches.
The prior instruction authorized consolidation into `0.19.0-rc3`.

## Completed work and original history

The four selected implementation/packaging/reinstall tasks are complete.
Coordinator checkpoint `1391e0346886752237e9b051d099d7adad6b57ed` entered
`0.19.0-rc3` at `1a4f3153c9e0d885d99d6a299c2850190d34eff1`.
The remaining worker results had already been cherry-picked, which preserved
content while leaving their original branch tips outside that ancestry.

| Worker branch | Original tip | Disposition |
| --- | --- | --- |
| `codex/rc3-knowledge` | `8940ae9eae1fcb1464f82c7ad4564380af59a5ae` | All knowledge bytes are identical in the integrated tree; ADR resources retain the accepted author rename and manifest routing. |
| `codex/rc3-skill-packages` | `ac3109e785c3c4e709ce0bdda3b155c7e8577ac1` | Changes are already carried by coordinator commits; the final worker patch matches the integrated patch. |
| `codex/rc3-source-trial` | `df0f557487403ba0d48563f36fc6ae291bf20876` | Verified installation tree was carried by `7f81146f9418bb663b245f51e9083d436cb20f06`; installed core, adapters, lock and selections remain identical. |

This closeout joins those original histories with the `ours` merge strategy
because their content is already present or deliberately superseded. The merge
retains the current product tree and adds only this source workflow record.
Original worker commits therefore remain reachable after branch-name removal.
The coordinator branch and the temporary closeout branch have no remaining
implementation work.

## Corrected filesystem observation

The earlier report of 34 unstaged author-file deletions was incorrect.
The restricted sandbox could not read some F: directories; Git reported those
paths as deleted. Unrestricted read-only Git status confirms all four worktrees
are clean, and the required `adr-author`, `lesson-author` and `pr-author` files
exist. No restore, source repair or deletion adoption is needed.

Unrestricted inventory found no genuine untracked files or personal settings.
Nine ignored files comprise eight commit-message files and an empty installation
guard. Their exact bytes and hashes are archived in the persistent local evidence
root before worktree retirement. A final receipt records actual removal results;
this source record does not treat a planned cleanup as executed.

## Evidence and remaining release scope

Local evidence root: `.dev/ai-context/local/rc3-final-evaluation-20260930/`.
`rc3-closeout/worktree-pre-cleanup-inventory.json` records exact preimages,
status, ignored paths and archive hashes. The closeout receipt records final
commit, ancestry, byte reuse, branch/worktree removal and the corrected observation.
The earlier failed observation is retained as historical evidence and explicitly
superseded by that read-back.

Product inputs remain bound to tested commit
`bdb5bbec012e86f5d9486dadd9872ecbbb5a4e0a`. The clean primary installation
inspection at `1a4f3153` returned `managed-bytes-consistent` with no drift.
History reconciliation and this source record do not change those product or
installation bytes, so their evidence is rebound rather than rerun.

Full behavioral acceptance, hosted CI, independent release admission and P7
restoration remain `deferred-by-owner` under U001 to program #322/P7.
Those remaining gates are separate from completion of these worker branches.
No source push, tag creation, publication, Issue closure or CI restoration is
performed by this closeout.
