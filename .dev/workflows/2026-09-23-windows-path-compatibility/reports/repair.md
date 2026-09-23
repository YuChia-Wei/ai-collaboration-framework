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
