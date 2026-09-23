# Issue #370 current-engine source review

Source review complete: **one SHOULD FIX / P2 source finding (CR-002)** and
**one conditional, unverified casing concern (C-001)**. They have different
evidence strength; C-001 is not counted as a substantiated defect.
Historical CR-001 remains resolved in source: the verified-byte finder and main
are AST-identical to the previously reviewed repair. This is no blanket engine,
native, target or publication acceptance.

- Fixed reviewed/start commit: `ae40e6cb0d49cdfb8e2174c732d74e1d918d0c2f`.
- Prior reviewed source: `0d29b9abf36804cb2587732232d807a1b754c3a0`.
- Installed-engine comparison: `3afb4ff4207acb3e12e3953018736305a439ed21`.
- Assigned root/branch: `F:/framework-next/370`, `codex/2026-09-24-current-engine-review`.
- Authority: the live [current-engine continuation](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/370#issuecomment-5799832277), read back on 2026-09-24; U001 and the current temporary source override apply. Prospective policy/CI remains dormant.
- Same independent OpenAI Codex / gpt-6-astra / ultra conversation; selection is declared provenance, not external runtime attestation. No agents, nested tasks or callbacks.
- Common `code-reviewer` route, with proportionate `ai-context-governance` records. No .NET specialist route applies. This is not an exhaustive security audit.

## Fixed identity and coverage

[Source inventory](current-engine-source-hashes.json) contains every exact Git
blob and raw SHA-256, prior raw hashes, and preserved-report hashes. Direct
`git cat-file blob` comparisons prove all ten current files equal the fixed
subject, checkout and specified installed-engine commit. Full EnginePin commit
identities are distinct despite that file equality. Six changed; four unchanged:

| Changed since prior review | Unchanged since prior review |
| --- | --- |
| `src/tools/maintain_framework.py` | `src/distribution/__init__.py` |
| `src/distribution/data.py` | `src/distribution/package.py` |
| `src/distribution/git_source.py` | `src/distribution/installation.py` |
| `src/distribution/installation_io.py` | `src/distribution/maintenance_coordination.py` |
| `src/distribution/installation_plan.py` | |
| `src/distribution/installation_state.py` | |

Read the affected definitions, their direct installation/locking/recovery callers,
and `assembly.py` producer context, bound separately in the inventory. Criteria
come from the [installation contract](../../design/framework-next/installation-update/contract.md),
[implementation handoff](../../design/framework-next/managed-installation/handoff.md)
and [versioned-candidate contract](../../design/framework-next/versioned-candidate/contract.md).
No whole-framework, package-private helper-copy or test-suite review is claimed.

Fresh nonpersisted fast graphs covered 13 distribution files (230 nodes / 1556
edges) and the one tool entry (33 / 71), zero skipped. File-node coverage,
search/snippets and the `direct_directory` inbound trace guided review. The graph
has no commit attestation; stable HEAD and raw Git comparisons bind its source.
Graph results and absence are not proof by themselves.

## CR-002 — SHOULD FIX / P2: a directory-drive alias can evade source-output isolation

**Location:** [git_source.py:58-66](../../../src/distribution/git_source.py#L58),
`direct_directory` error-1 fallback; direct consumer
[assembly.py:60-72](../../../src/distribution/assembly.py#L60).

**Trigger:** on the Windows final-path error-1 branch, an existing DOS drive
alias points into a proper descendant of the selected repository. For example,
repository `F:/source`, alias `X:` targets `F:/source/subdir`, and an explicit
output/scratch parent is `X:/out`. This is a reasoned example, not a mapping
created or observed by this reviewer.

`lstat` sees ordinary stable directories through that drive spelling; rejecting
filesystem links/reparse points does not inspect the DOS-device mapping. The
fallback returns `abspath(value)` without the mapping guard already present in
the maintenance root/bootstrap helpers. `output_parent` then sees an unrelated
lexical drive. Its ancestor identity check visits `X:/out` and `X:/`, whose
identities are the output and `subdir`; neither is the repository root. Therefore
both containment checks admit this input, and `OwnedDirectory` creates candidate/scratch
files inside the source tree despite the explicit outside-source rule. An alias
to the repository root itself is caught; an alias to its descendant is the gap.

[Microsoft's SUBST contract](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/subst)
permits a directory to become a drive root. Its
[DOS-device API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-querydosdevicew)
describes that namespace mapping separately from filesystem ancestry. The
[source repair report](../2026-09-23-source-contract-checks/repair-report.md)
claims output containment including alternate drive spellings; current source
only proves the ancestor identities visible beneath the alias root.

**Correction:** reject non-direct DOS-drive mappings in this fallback, or obtain
and verify the complete underlying ancestry before output admission. Retain
explicit roots, no settings changes, stable identity and fail-closed behavior.
A later owner-selected regression should cover an alias to a repository
*descendant*, not just to its root, with refusal before allocation.

Confidence: high in the conditional source path; no native reproduction. This
concerns the direct candidate producer. Maintenance imports `Blob` and does not
call `GitSource`/assembly, so it is not evidence of an apply/recover write escape.
Existing files are not overwritten by the exclusive builder allocation.

The source-admitted witness is concrete: the error-1 arm preserves `X:/out`;
lexical containment against `F:/source` is false; the only visible ancestor
identities are those of `F:/source/subdir/out` and `F:/source/subdir`, neither
matching `F:/source`. No later builder check recovers that omitted ancestor.
This demonstrates the predicate gap by inspection, not by executing a mapping.
[CPython abspath](https://github.com/python/cpython/blob/v3.13.0/Lib/ntpath.py#L515-L543)
uses full-path normalization; [GetFullPathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfullpathnamew)
does not establish the actual underlying filesystem location.

## C-001 — conditional concern: protected-path stored-case proof

**Not a confirmed defect or executed reproduction.** Location:
[installation_plan.py:92-101](../../../src/distribution/installation_plan.py#L92),
using [installation_state.py:248-253](../../../src/distribution/installation_state.py#L248).
The live [#383 accepted scope](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/383)
explicitly requires preservation of exact spelling. The code states that it
rejects alternate-case protected paths and compares relative components with
case-sensitive tuple equality.

**Established source fact:** after Windows error 1, the name compared is solely
the result of `GetLongPathNameW`. If that API returns a supplied mis-cased long
component unchanged, the tuple comparison accepts it. Device/inode/mode and byte
hashes would not detect a case alias to the same file. There is no independent
stored-case observation in this branch.

**Documented semantics:** [GetLongPathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getlongpathnamew)
converts short names to long form. Microsoft documents successful input copying
when a long path is not found and possible skipping of parent-name queries for
already-long directory components. Those statements justify checking this
assumption, but do not by themselves demonstrate that the precise mis-cased
input above is echoed on a supported NTFS/ReFS host. No missing API guarantee
is presented here as a measured failure.

**Unexecuted hypothesis:** a mis-cased already-long protected component on a
case-insensitive volume follows that echo path when strict resolution fails.
Whether the real API does so in this selected environment remains unresolved.
The attributed #383 nine simulations and positive public plan establish their
selected cases, not this native casing premise; their test doubles were not
independently audited or rerun in this continuation.

Coordinator may select a bounded verification of that exact premise before
assigning a repair. If it is established, use an identity-bound exact-name
observation or refuse unavailable proof, preserving the ban on sibling/recursive
data scans. No such execution or source repair was authorized or performed here.
Content/hash and managed/protected overlap checks remain active; no content
corruption or write escape is alleged for this concern.

## Other affected source conclusions

- Bootstrap changes are confined to `_direct`, two private stdlib-only helpers
  and `os` import. The exact closure, byte budgets, `main` and retained-byte
  `_VerifiedSourceFinder` are unchanged by AST. No ordinary bytecode-loader
  regression of CR-001 was found.
- Maintenance root/bootstrap error-1 arms use direct DOS mapping, bounded native
  long-name results and stable direct ancestry. The writer's error-144 arm opens
  the selected directory and compares handle identity/volume serial/ancestry;
  it does not substitute a drive root. Other error paths still refuse. These
  observations do not settle C-001's unresolved stored-case premise.
- Selection 1/development/null and selection 2/versioned/canonical distribution
  label are closed combinations with exact integer typing and corresponding
  generator IDs. Component version semantics remain unchanged. The producer,
  candidate reader, lock reader and retained recovery documents share complete
  metadata identity; a label change changes identity even with equal members.
- Reader caches only completed alias-free directory-name listings, reobserving
  direct directory identity/type/attributes/size/timestamps before reuse and
  after enumeration. It does not cache file contents or reset entry/byte
  counters. All five namespace mutation sites invalidate their parent first:
  parent mkdir, operation mkdir, exclusive create, same-parent move and unlink.
  Mode-only changes do not alter the namespace; exact reads/mode checks remain.
- IO still rechecks roots, volume containment and child metadata; O_EXCL,
  hardlink refusal, raw before/after expectations and original limits remain.
  Unchanged apply/capture/recovery and native lock code retain locked
  recomputation, complete durable capture before marker/member mutation,
  matching operation ownership, final read-back and marker-last removal.
  No further substantiated source defect was found in these affected paths.

Directory signatures are observations under the existing stopped-external-writer
contract, not a concurrency lease. Unknown filesystems, power loss, broader
reconstruction and documented ownership conflicts remain unsupported; they are
not newly relabeled as defects or supported cases.

## Attributed execution evidence and limits

The following committed records were read, not imported, executed, independently
reproduced or promoted to a whole-engine pass:

| Owner/source | Selected observation and boundary |
| --- | --- |
| #368, `c1fb1c1fb07a6d246e3bcedd3cd851918f66b306` | [C5 receipt](../2026-09-23-source-contract-checks/repair-checks.json), `post_378_c5`: one method passed; two actual Lesson builds/readers and five synthetic corruptions. No native/apply execution. |
| #378, `aa2bffb52c0acf521302cf9f08c649ad54246c98` | [Bootstrap observations](../2026-09-23-windows-path-compatibility/reports/bootstrap-observations.json): seven simulated path regressions and one complete public plan; no apply/recover. Earlier failure history remains in its reports. |
| #381, `3755b217421a4f1238f740a09de7e034ccf56038` | [Handoff](../2026-09-23-versioned-candidate/handoff.md) and [complete result](../2026-09-23-versioned-candidate/evidence/complete-result.json): 18-component rc candidate, 113 payload + 18 runtime files, real reader. Future stable/manual lock plan is a fixture, not a real upgrade. |
| #383, `3c0832b89d73cfedfc625462d167a3811fdf7931` | [Result](../2026-09-23-protected-path-repair/evidence/result.json): actual protected-input plan, four present files and one absent binding; no writer execution. Reported nine path regressions are simulations, not native case-alias proof. |
| #382, `cb41982dde3af9d746624b6939f26fd2883623af` / `ef4ffd9f286f49b6055d9a321abbd134b263ced8` | [Reconciliation](../2026-09-23-native-maintenance-checks/evidence/native-completion-summary.json): first four cases plus two-case tail, not one passing six-case run; genuine marker interruption/same-pin finish. Current IO/state hashes differ from that native pin. |
| #386, `64bf9f6e800799976e46caa13d873f9fef898431` | [Public result](../2026-09-23-installation-scan-budget/public-result.json): one tiny complete-candidate plan/apply, 131 members, exact lock/markers/sentinels. Independently compared all ten recorded raw pin hashes: equal to this subject. This is still the worker's selected run, with a different full EnginePin, and no current independent native extension. |

Prior failures, actual/synthetic distinctions and `project_readiness=not-assessed`
remain. The selected positive observations do not establish either alias scenario.
CR-002 is source-predicate reasoning; C-001 retains an unresolved API premise.
No product/test import, test, native probe, fixture, public CLI, install or recover
was performed by this reviewer.

## Delivery and remaining ownership

Direct UTF-8/AST parsing of all ten engine files and selected producer, unchanged
loader/constants/read helpers comparisons, raw Git bindings and affected call
reasoning completed. Record checks and exact planned-message validation are
recorded in [task.json](task.json). The source stayed fixed throughout review.

Only this report, [source inventory](current-engine-source-hashes.json), existing
task and workflow are deliverables. Original [report](report.md) and
[affected review](affected-review.md) retain their exact raw bytes, including
historical limitations; later evidence is recorded here rather than rewriting
them. Artifact commit is the containing commit of this report, resolvable with
`git log -1 --format=%H -- .dev/workflows/2026-09-23-installation-source-review/current-engine-review.md`.

Coordinator task `01a0ce78-db26-74e1-a615-2bd0599f7d0c` owns first transport,
repair assignment and Issue disposition. Recommended next route:
`local-change-implementer` for CR-002, then affected `code-reviewer` review;
coordinator separately decides whether to verify C-001 before any casing repair. This task makes no source repair or provider write.
Pending native/target authority stays with its existing owners; this review does
not adopt policy/CI, activate target capabilities or close #368/#369/#370.
Unselected legacy/full/formal/hosted gates remain **deferred-by-owner**, U001,
program #322 coordinator / P7. No push, PR, merge, release or credential change.
