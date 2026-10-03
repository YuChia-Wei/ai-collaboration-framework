# Validation and local delivery

Source provenance: `b52c68d64373bb54688109b9174bd4a9cea2b577` on
`codex/2026-10-03-sub-agents`, plus the authorized uncommitted changes.
Issue #435 was created and fetched independently as open. No Project mutation.
Graph lookup did not cover the current source selector; the existing index also
contains retired paths. Direct Git-tracked files were the explicit discovery
fallback, not proof based on search absence.

## Observed checks

| Command/check | Actual outcome |
| --- | --- |
| `python -I -B tests/run.py --suite distribution --suite source` (sandbox attempt) | failed: 102 tests, 16 errors, 0 assertion failures, 0 skips; Windows temporary-fixture access denied, duration 7.166492s |
| Same command with host permissions after environment change | passed: 102 tests, 0 failures/errors/skips, 7.067069s |
| Same command on final source declarations and prose | passed: 102 tests, 0 failures/errors/skips, 7.307439s |
| `python -I -B tests/run.py --suite schemas` | passed: 43 tests, 0 failures/errors/skips, 0.894149s |
| `git diff --check` | passed |
| Changed/new Markdown links | passed: 26 documents at final integrity capture, no missing local links or source links outside `src`; final validation/locator records inspected separately |
| Manifest/component members, knowledge references and dependency closure | passed by actual source declaration and distribution tests; logical source evidence, not physical assembly/installation |
| Both engineering catalog canonical digests and normative-text SHA-256 fields | passed; updated .NET test owner hashes match current source bytes |
| Existing excluded/installed trees | passed canonical Git comparison; [integrity capture](integrity-check.md) |

The initial focused declaration check caught a missing manifest newline; after
repair it caught unsorted reference declarations. Both were implementation
errors, corrected before the complete source/dependency tests. These attempts
are retained rather than counted as passes. Metadata editing was replanned to
preserve deterministic resource/reference ordering.

The first raw Git-blob comparison was unsuitable for proving checkout byte
identity in historical files: 197 differ only by LF/CRLF. The bounded batch
comparison confirmed no unexpected content difference in 2,248 existing excluded
files, and Git's canonical comparison was unchanged. All 142 tracked installation
files match raw Git bytes. No pre-edit raw-byte snapshot was taken, so this report
does not claim one. The cleanup writes did not target any existing excluded file.

## Delivery and limits

10 obsolete documents removed; useful methods extracted into four declared
engineering-common source resources and product documentation maintenance guide.
48 input guide/contract/standard files have [individual dispositions](disposition.md).
Current navigation no longer advertises removed trees as available resources.
Both root language entries retain aligned ownership and fixture instructions.

At the initial local checkpoint, changes were uncommitted and unpushed. The owner
subsequently authorized review, necessary repair and commit; see `review.md`. This is author inspection and local
source/static/fixture evidence, not independent review, fixed-head hosted Source
change gate success, physical package assembly, native/downstream acceptance,
installation, release or publication. The exact two-tree source selector will run
on future immutable commits; its affected schema/distribution/source suites were
run directly here. Tools/release/loader/platform suites were not selected by these
changes. No test or validator implementation was removed or restored.

Before later integration, the owner selects a final commit and obtains independent
scoped review for the authority changes, maintainer acceptance and actual
current-head hosted admission. User deferred PR/merge and release choice; #435
stays open. Existing sub-agent work on this branch is preserved. Self-installation
and upgrade remain a separately selected final product stage. No push, PR, merge,
Issue closure, Project update, installation, tag, release or publication occurred.

## Review continuation

The 2026-10-03 owner request extends the local checkpoint to review, repair and
commit. [Review findings and current checks](review.md) supersede the initial
pre-commit state above while preserving its observed failures and limitations.
The completed-task/Issue/evidence formats now pass the actual source selector's
working-tree preflight. Commit is authorized; push, PR and integration remain
unselected.
