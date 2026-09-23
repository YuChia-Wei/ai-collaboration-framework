# Issue 368 local checkpoint

Implementation is ready for coordinator inspection; selected acceptance is
**not complete**. Final contracts command returned **1**: 14 test methods,
11 successful methods, three affected methods producing seven error instances.
No skips, expected-failure annotations or green placeholders conceal blockers.
No distribution/package source was changed.

Authority: program #322 / U001, live
[Issue #368](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/368)
(read OPEN through gh), and
[P7 selection](../../design/framework-next/p7-execution-selection.md).
Source baseline: `38e6458f8d3e81dc2568daf1fa467571fb529fee`.
Worktree `F:/framework-next/368`; branch
`codex/2026-09-23-source-contract-checks`; common Git database is the persistent
C: project `.git`. The containing local checkpoint carries implementation and
observations; the executor's final handoff supplies its full SHA. Coordinator
owns shared indexes, first push, PR, online merge and Issue/Project reconciliation.

One declared `gpt-6-astra` / `ultra` conversation, no agents or callbacks.
Declaration is not independent runtime attestation. No provider writes, CI
changes, native maintenance or root activation occurred.

## Implemented scope and results

| Case | Actual outcome and limits |
| --- | --- |
| C1 | Read 18 declared owners / 113 exact Git payload blobs / seven profile documents. Owner closure/projection checks succeed for Lesson, knowledge, engineering and context-maintenance. PR and local-backlog metadata refuse YAML anchors, blocking their owner checks and work-management/collaboration/source-repository selection. Five error instances in this method; C1 aggregate failed. |
| C2 | Actual Lesson v2 read/write schema split; mixed CBF v3; all 11 null-config metadata/projections; minimal synthetic v1; exact-type/duplicate/owner/reference/union negatives; restricted-YAML anchor and duplicate-key refusals passed. Authorized target editors on the two implementation packages are preserved. Structural checks do not prove instruction quality. |
| C3 | Synthetic required dependency, optional absence, version mismatch, cycle and manifest case/prefix/escape collisions passed. One real tiny Git fixture was created with one commit/two entries (regular executable blob and Git symlink mode). GitSource strict root resolution failed before regular/missing/nonregular member assertions. No native OS link probe. |
| C5 | First actual `assembly.assemble` invocation failed in GitSource root resolution. Zero candidate builds completed; no candidate/scratch payload emitted; second build, actual candidate reader and five synthetic corruptions remain unexecuted. Tests are implemented and fail visibly until backend access is reconciled. |
| Helper/runner | Root precedence, tiny actual OS-temp default, invalid roots, synthetic failed-residue/identity mismatch and reserved argument refusals passed. No public/native implementation is advertised. |

### Actual commands

All repository commands used `F:/framework-next/368` as explicit workdir.

```text
python -I -B tests/framework_next/run.py --layer contracts --output-root F:/framework-next/p7-runs/368-contracts
python -I -B tests/framework_next/run.py --layer contracts --case SourceClosureTests.test_c2_actual_v2_v3_union_and_null_config_projection --output-root F:/framework-next/p7-runs/368-contracts
```

The first command is the final selection and earlier initial-layer invocation;
the second is the one repaired-C2 rerun. Full final
[stdout](evidence/contracts-final.stdout.txt) and
[stderr](evidence/contracts-final.stderr.txt) are retained as text with only line endings and trailing whitespace normalized.
Original captured-byte hashes and the initial trailing-whitespace failure are
retained in `checks.json`.
Runner/helper argv and reserved behavior are in the
[interface](../../../tests/framework_next/README.md).

Runtime: Python 3.13.14, PyYAML 6.0.3, jsonschema 4.26.0, referencing 0.37.0;
`C:/Users/h4227/AppData/Local/Programs/Python/Python313/python.exe`.
Dependencies were inspected, not installed.
Final unittest wall time: 3.483 s; helper lifetime: 3.529 s.
Final root: 7 observed/retained files, 434 observed/retained logical bytes,
15 helper-authored bytes. Two separately printed helper probes each created one
file (26 bytes synthetic cleanup / 5 bytes OS temp), then cleaned successfully.
Combined observations: 9 distinct files / 465 logical bytes, 46 helper-authored
bytes; final residue remains 7 files / 434 bytes. Git internal transient files
that disappear between checkpoints are not measured; cumulative physical I/O
is unavailable. The selected interpreter launched 10 Git processes; the runner
itself is one Python process, giving 11 known processes for final execution.
No public skill/maintenance launches or opaque nested helpers occurred.
No speed, wear, token or native durability inference.

Failed residue (preserved, not recursively deleted):

- Initial selected run: `F:/framework-next/p7-runs/368-contracts/fn-a9713554a15d4ca68b38842026f3a8a8`.
- Final selected run: `F:/framework-next/p7-runs/368-contracts/fn-7ce6045a9eae47e68aa3ecb5597100cc`.

Coordinator should inspect these bounded runs before explicitly selecting their
cleanup; they are volatile RAM fixtures, not sole durable evidence. This report
and raw final outputs are committed into the persistent Git database. Other
worktrees and `F:/ai-context-tests` were preserved.

## Retained failures and changes

1. Initial live gh read failed because the sandbox proxy at 127.0.0.1:9 refused
   connection. One scoped escalated read succeeded; no credential/settings change.
2. Initial output-parent preparation failed on `Path.resolve(strict=True)` with
   `OSError: [WinError 1]` at `F:/framework-next`. The runner then failed because
   the output parent was absent; zero tests ran. Direct lstat proved existing
   directories without symlink/reparse attributes. New helper preflight uses
   those checks plus absolute lexical paths; only the exact authorized binding
   was then created. No drive was substituted. This is a helper fix, not a
   product canonicalization bypass.
3. First selected execution: 13 methods, two assertion failures and seven error
   instances (3.442 s). Test incorrectly assumed every null-config skill needs
   only an instruction reader. Actual metadata explicitly gives
   `authorized-target-editor` to local-change-implementer and slice-implementer;
   the exact expected list was corrected, preserving source authority. Focused
   rerun passed one method (1.861 s, five Git processes). The other errors were
   preserved unchanged. Initial audit categorized ten Git launches as `other`
   because Windows supplies a null executable in the audit event; corrected
   command-line attribution yields ten Git launches in final output.
4. Added a tiny explicit no-anchor/duplicate-key parser regression; corrected
   declaration-only C1 stdout labeling and candidate file counting before the
   single final selected layer. Final 14 methods, seven errors, no assertion
   failures. No retry of unchanged failures after this final selection.

## Concrete residuals for coordinator

**Package defect, outside Issue 368 write scope:**
`src/skills/pr/skill-package.yaml` line 12 introduces `&id001`; line 54 introduces
`&id002`; multiple aliases follow. `src/skills/local-backlog/skill-package.yaml`
line 12 introduces `&id001`. `distribution.data.yaml_object` rejects anchors at
line 104. Required next action: assign package-owner normalization to explicit
sequences without changing declared operations, then rerun affected C1/public
family tests. Do not broaden the loader's closed YAML contract.

**Backend block:** `src/distribution/git_source.py:30` calls
`repository.resolve(strict=True)`, which fails with WinError 1 on the assigned
F: source and fixture roots. Direct read-only observation also reproduced this
for F: root, framework-next and this worktree; non-strict resolution and lstat
succeeded. `installation_state._root` has the same strict-resolution requirement
by source inspection; no reader success or native trial is inferred from that
inspection. Fixing only the first call would leave cross-owner canonical-root
semantics unresolved. Required next action: coordinator assigns the selected
Windows backend/canonical-root contract across distribution and installation
reader, or records its unsupported disposition; preserve explicit F: routing.
No caller monkeypatch, loader weakening or unauthorized reader repair was made.

**Implemented but not reached:** two Lesson assemblies, candidate byte/mode/hash
comparison, missing completion/payload/hash/closure refusals and real GitSource
member checks. These remain blocked-by-environment, never passed.

## Later reconciliation and automatic approval rejection

After these observations, coordinator task `01a0c9d9-3b00-7b70-ad85-daff590e7ecd`
requested a bounded extension. Live Issue #368 was re-read at its
`2026-09-23T07:13:14Z` update: expand aliases only in PR/local-backlog metadata
while preserving exact parsed values/types/order, and repair GitSource's observed
F: path admission with existing identity/traversal/link protections. Installation
state/writer/IO/coordination stayed out of scope. Source tests would need a real
committed repair; changed EnginePin bytes need affected independent review.

The attempted scoped write was **rejected by automatic approval review before
execution**. It covered `src/distribution/git_source.py`,
`src/distribution/assembly.py`, `src/skills/pr/skill-package.yaml`, and
`src/skills/local-backlog/skill-package.yaml`. Review reason: the Issue addendum
was treated as untrusted authorization for expanded source changes, and the
proposed strict-resolution fallback changes canonical-path security behavior.
The exact response said not to bypass the rejection through a workaround or
indirect execution. No product/metadata mutation or checkpoint occurred; a fresh
Git diff of all four paths is empty. No alternate tool/writer/path retry occurred.

Next action: obtain the user's explicit approval for the bounded four-file
repair before resuming it. The concrete intended change is alias expansion with
recursive exact-type/order equality proof, plus an existing-file path-admission
helper that rejects traversal, ambiguous Windows aliases and link/reparse
ancestors, permits only Windows error 1 as the observed strict-resolution
fallback, binds directory identity before/after and compares actual Git root
identity. Assembly would additionally reject source-root aliases by directory
identity. This is a pending repair proposal, not tested or applied production
behavior; the installer reader remains a separate residual owner boundary.

Only unaffected original-scope handoff/checkpoint work continued. The earlier
source findings remain valid and tests were not rerun without material changes.

## Scope, verification and deferrals

Changed scope: four `tests/framework_next` files; this workflow's locator, plan,
task, report and two raw logs; one issue-owned design README. No package,
manifest/profile, production distribution, root, policy or `.github` edits.

A bounded nonpersistent graph index covered `src/distribution` (221 nodes,
1,486 edges, zero reported skipped files). The service supplied no Git-SHA
attestation, so no completeness claim relies on it. Graph navigation was bound
to the clean starting SHA and exact tracked paths; material source defects were
confirmed with current tracked file/Git-blob reads. No full tree/test-history scan.

Direct Python AST parsing, changed JSON/YAML readability, changed-link checks,
Git scope/diff inspection and full planned-message validation are recorded in
`checks.json`. Those are limited checks, not independent review or acceptance.
The complete planned message is validated before its exact bytes are committed.

**deferred-by-owner**, U001, owner **program #322 coordinator / P7**:
C4/package-specific C6 and seven public families (next: V2 assignment); native
Windows (next: V3/backend disposition); Lesson pilot/root adoption (next: V4 after
residual disposition); unselected legacy validators/check-all/full/history/
upgrade matrices and audit/lease/effective-rule/acceptance packet machinery
(next: P7 selects effective replacement); independent review and all-profile
build acceptance (next: selected immutable review/trials); CI/provider admission,
release/tag/publication and downstream adoption (next: separately authorized
owner decision). No hosted success or CI restoration was claimed.
