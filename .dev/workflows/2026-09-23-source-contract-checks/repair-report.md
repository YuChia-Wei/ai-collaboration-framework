# Approved repair continuation

The user's direct confirmation in the original Issue #368 conversation approves
GitSource/assembly path repair and PR/local-backlog alias expansion while keeping
path/link/reparse protections and original data semantics. The prior automatic
rejection and original failures remain in [the historical report](report.md).
No bypass occurred: repair resumed only after this direct user instruction and
fresh live Issue read-back. Starting local HEAD:
`070a47335ffce99d31bd83e487447942539e4a9f`.

## Bounded implementation

- Expanded only existing aliases in two metadata files. Recursive exact type,
  value, mapping-key order and list-order equality passed against the original
  committed blobs; package version/member/operation semantics are unchanged.
  The actual owner loader accepts both repaired working files. Proof and raw
  checkout hashes are in [metadata-alias-expansion.json](evidence/metadata-alias-expansion.json).
- `git_source.direct_directory` keeps strict resolution normally. Only Windows
  error 1 permits the explicit absolute spelling after lstat of every ancestor;
  each must be a plain directory without links/reparse points, have usable
  device/inode identity, and retain that identity after resolution. Traversal,
  network/device paths and ambiguous Windows names/short aliases are rejected.
  Missing, permission and other unsupported errors are not swallowed.
- GitSource compares the actual Git root path and device/inode with its admitted
  repository. Assembly retains its no-link check and rejects source containment
  both lexically and by ancestor identity, including alternate drive spellings.
  No new module, EnginePin member, format, backend guarantee or global monkeypatch.
- Three focused path methods passed (0.005 s): actual direct F: directory and
  invalid roots; output containment; labelled synthetic link/reparse/identity
  drift/error branches. Synthetic doubles do not prove native link/process
  behavior. Observed helper allocation: one file / 15 bytes, zero subprocesses;
  successful cleanup. Actual source/candidate tests await this repair commit.

Source scope is exactly `src/distribution/git_source.py`,
`src/distribution/assembly.py`, `src/skills/pr/skill-package.yaml`, and
`src/skills/local-backlog/skill-package.yaml`; tests and issue-owned records are
updated in the original assignment. Installation state/writer/IO/coordination
remain untouched. The reader has its own strict-root check and remains a
potential independent residual; no success is forecast.

## Next execution

Create one coherent local repair checkpoint, then run the selected contracts
against that actual commit in `F:/framework-next/368`, using
`F:/framework-next/p7-runs/368-contracts`. Preserve original evidence and new
failures. The C5 case now reports real assembly byte/inventory/hash comparison
before invoking the actual reader, retaining all reader/refusal assertions.
This makes a reader block distinguishable from a build failure without changing
acceptance. No profile beyond Lesson is physically assembled.

Changed EnginePin bytes require affected independent review; original-source
#370 cannot cover this repair. Native/root/CI/all-profile/independent/provider
acceptance remains unclaimed. Other U001 obligations remain deferred-by-owner,
owner program #322 coordinator / P7, next action separately select execution.
