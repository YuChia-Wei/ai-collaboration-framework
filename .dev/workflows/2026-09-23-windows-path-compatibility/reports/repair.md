# Issue 378 repair observations

Initial source: 70cff755bad2c2bc55bb10f7259af3871009bb03; assigned worktree clean.
Live Issue 378 was OPEN with no comments when read. First restricted GitHub read
failed at sandbox proxy 127.0.0.1:9; approved read-only retry succeeded.
Graph index framework-next-378 was refreshed at that source, excluded all selected
skill-script directories, and returned zero selected symbols. Bounded tracked-file
inspection supplies source evidence; graph absence is not absence proof.

## Actual read-only diagnosis (before repair)

Python 3.13.14 / Windows. Both Path.cwd().resolve(strict=True) and
installation_state._root(str(Path.cwd())) raised OSError winerror=1.
For F:/framework-next/378, lstat returned st_dev=12003918052740279813,
st_ino=562949953444060, attributes=16. GetVolumePathNameW returned success and
F:/framework-next/; GetDriveTypeW returned 3. GetVolumeInformationW on that
returned string failed with error=144. A last-error value after a successful
API is not a failure diagnosis.

A second distinct read-only probe opened the same directory using metadata-only
OPEN_EXISTING and BACKUP_SEMANTICS | OPEN_REPARSE_POINT. Handle fstat and path
lstat had equal device/inode. GetVolumeInformationByHandleW succeeded: NTFS,
serial=2524687877 (the low 32 bits of st_dev). GetLongPathNameW returned the same
long directory. The explicit F:/ volume query also returned NTFS, but is not used
as substitution proof. These are observed API differences, not a proven driver
cause. No fixture, drive, credential, global environment or prior residue changed.

## Selected repair

Reader error 1 alone uses a native long-name check after plain-directory ancestry
and nonzero identity checks, then rechecks every ancestor. Other errors propagate.
Writer error 144 alone uses a directory handle bound to that verified direct path;
the returned mount path must be an ancestor, ancestry must share the device, the
handle identity and native volume serial must agree, and ancestry is rechecked.
No drive anchor replacement, filesystem guess, new package dependency, lock or
recovery-policy change. Eight private helper copies keep standalone packages
independent; AST parity is tested, as are the six identical writer backends.

## Retained failed check

`python -I -B tests/framework_next/test_windows_paths.py --mode regressions`
first attempt: 10 tests, 9 methods passed, one method had 15 subcase errors in
0.206s. Fingerprint: AttributeError at line 211: module wpc_lesson has no attribute
Failure. This was a test-harness exception-name mistake; those 15 production
negative branches did not run. Corrected both package exception names to Fault
before the second run. No actual fixture was allocated by this simulation run.

## Remaining work

Focused regression rerun, actual F: assembly/reader and Lesson write/read, then
CBF and the distribution public plan. The existing unmodified source bootstrap
src/tools/maintain_framework.py::_direct also uses strict resolve. If its one
actual attempt refuses before distribution dispatch, retain it and hand off the
additional source-owner scope; do not patch or bypass bootstrap here.

U001 legacy validators, formal packets, matrices and CI: deferred-by-owner,
program #322 coordinator/P7; next post-pilot review. No #368/#369/#373 closure,
installation, pilot, release, independent-review or CI acceptance is implied.

## API references

- [Volume path semantics](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumepathnamew)
- [Filesystem query by handle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationbyhandlew)
- [Metadata-only directory handle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)
- [Long-name query](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getlongpathnamew)

Second focused simulation run: 10 tests passed, 0 skips, 0.188s. The first
failed attempt above is retained. Actual checks have not yet run at this source
checkpoint. Both public families use their supported file request protocol.

## First actual F: run

Source checkpoint 34e18e63142549b109d23222aeb5a4798ace95d0, clean at dispatch.
Command: `python -I -B tests/framework_next/test_windows_paths.py --mode actual
--output-root F:/framework-next/p7-runs/378-compatibility`.
Run: F:/framework-next/p7-runs/378-compatibility/fn-c84e49b8d71b4f5db1bc38b9aec00793.
Runtime: Python 3.13.14, PyYAML 6.0.3, jsonschema 4.26.0, referencing 0.37.0.

- Actual Lesson-minimal assembly and installation_state.read_candidate: passed,
  10 managed members, candidate identity
  development:34e18e63142549b109d23222aeb5a4798ace95d0:7a38a78dc3ca0d355a0a3da32f767b67cbf14b7fc480eb39b5336ad20b20f83c.
- Actual Lesson public explain/query/create/inspect: all exit 0, succeeded.
  670-byte synthetic record retained, SHA-256 readback equal, no writer residue.
  Fixture uses the direct source package, not an installed package.
- CBF explain: exit 0, ok. First create: exit 2, invalid-input, mutation_state=none.
  Exact fingerprint: shape / record.statements / Actor, command and controlled-domain
  statements are required. This is an authored test-input defect before backend
  writes, not a shared setup/backend failure. Add the two required fixture
  statements, then rerun only CBF plus previously unexecuted distribution cases.
- Distribution backend/public plan not executed in this stopped run.

Overall exit 1, 10.791s; 33 files, 298299 observed/retained logical bytes,
2817 helper-authored bytes, 43 Git and 6 Python driver launches. Physical I/O and
opaque child subprocesses are not measured. The entire run and public transcript
remain retained; prior runs and F:/ai-context-tests are untouched.

## Final guard review and selected additional checks

Read-only source inspection found that long-name conversion alone does not prove
absence of a DOS drive alias. Before handoff, both fallback paths now require a
successful QueryDosDeviceW mapping to a direct device, rejecting SUBST-style
namespace aliases and device subpaths. Reader fallback also rejects remote or
unknown drive type. This does not replace the selected path/volume or broaden
filesystem support. Actual selected F: mapping query succeeded; no device or
mapping was created or changed. The device label is not a causal attribution.

The workflow selects an affected-check refresh because this adds a guard to the
fallback code: focused simulation tests including mapping/alias failures, one
actual reader/backend check and only affected public Lesson/CBF write/read.
Do not repeat the already blocked public distribution bootstrap. Earlier pass
observations remain historical against 34e18e63142549b109d23222aeb5a4798ace95d0.

## Affected CBF retry and first distribution observation

After correcting only the CBF test input, a bounded Python stdin command loaded
`test_windows_paths`, allocated one FixtureRun, called `actual_cbf`, reread the
retained candidate and called `actual_plan`. It did not repeat Lesson or assembly.
Run: F:/framework-next/p7-runs/378-compatibility/fn-09dccb468a544476811fa3ce1a3c9fc8.

CBF explain/create/inspect all returned exit 0 / ok. Direct distribution Backend
construction and _volume succeeded: device=12003918052740279813, is_ram=false.
The existing GetDriveTypeW observation is 3 (fixed); this does not prove physical
persistence or change the caller's failure-domain declaration.

The first complete public plan request failed: exit 1, outcome unsupported,
changed=false, diagnostic source-bootstrap. Exact request, response and stderr
are retained as plan-request.json, plan-response.json and plan-stderr.txt.
No public plan pass, installation or writer recovery acceptance is established.
Run exit 1; 1.717s, 8 files / 14799 logical bytes, 5306 helper-authored bytes,
1 Git and 4 Python driver processes. All residue is retained.

A separate read-only isolation called the unmodified bootstrap `_direct` on
its actual script path and its checkout root: both raised OSError winerror=1.
The public response is deliberately generic; this direct observation localizes
an unresolved bootstrap admission path. No equivalent public retry was run.
A sandbox read-back of the retained plan-response file was denied; later read-back
uses normal scoped access. The earlier CLI transcript already returned the exact
response. No evidence was overwritten to conceal either access failure.

Final focused simulation refresh after the added mapping guard: 11 tests passed,
0 skips, 0.237s. A temporary edit-command string emitted a Python invalid-escape
SyntaxWarning; production/test source loaded successfully without that warning.
