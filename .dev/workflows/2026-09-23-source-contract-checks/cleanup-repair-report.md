# Issue 368 bounded readonly fixture cleanup repair

The helper now removes a verified readonly Git loose object from its own unique
fixture run. Cleanup failures preserve the pre-cleanup observation and remain
nonzero in both contracts and public reports. This is a helper handoff; no PR
family or whole-suite acceptance is claimed.

## Authority and fixed failure

The original #368 Astra/ultra task resumed under program #322 U001 on clean
`bd40c83060d55435df5d7bc015d8f5ab12085aea`, worktree `F:/framework-next/368`, branch
`codex/2026-09-23-source-contract-checks`. Coordinator:
`01a0ce78-db26-74e1-a615-2bd0599f7d0c`. Shared Git objects remain in the existing
persistent C: repository database; no C: checkout edits, agents or new tasks.

Read the #373 report and cleanup evidence at immutable commit
`8b151f0aa31ec91277c5399251171ebc12902f35` under
`.dev/workflows/2026-09-23-public-skill-checks/`. On source
`c1fb1c1fb07a6d246e3bcedd3cd851918f66b306`, PR assertions passed but `shutil.rmtree`
failed with PermissionError / WinError 5 on a regular 134-byte loose object,
attributes 33 (readonly + archive), without reparse. The helper had already
measured accounting but the exception prevented reporting it. The old 21-file /
117172-byte remainder is historical residue, not original high-water accounting.

## Changes and protections

- `support.py` snapshots known file/directory identities during the existing
  bounded no-link walk. Only Windows access-denied unlink/remove of a registered
  regular, single-link, readonly file can clear readonly and retry once.
- Before chmod and again before unlink, recheck lexical containment, all direct
  ancestors, original run identity, registered descendant-directory identities,
  regular/non-reparse type, single-link status, and file device/inode/size/mtime.
  Original attributes must match before mutation; only readonly is cleared
  (normal-attribute normalization is checked). Unknown operation/error/file,
  links, drift and failed retry propagate. No outside or historical file changes.
- A cleanup error carries the already measured observation, labelled
  `measurement_phase: before-cleanup`, plus residue and next action. Both existing
  runner catches emit it while retaining cleanup-failed / exit 2. `run.py` changes
  only four lines in those two catches; dispatch and reserved native arm are intact.
- New tests are wholly inside `FixtureSupportTests`. AST comparison confirms all
  other test classes, profile tables and original FixtureSupportTests methods
  unchanged. #373 workflow fixtures and #381/#382 ownership are untouched.

## Focused execution and evidence

[cleanup-repair-checks.json](cleanup-repair-checks.json) retains exact argv,
base commit, tested SHA-256 values, raw stdout/stderr and their hashes, both runs,
original failure fingerprint, and before/after historical-residue bindings.
Tests ran in place, as allowed for this helper repair; the supplied file hashes
bind the tested bytes to the subsequent local commit. No test is represented as
running on an as-yet nonexistent commit.

All commands used `python -I -B tests/framework_next/run.py --layer contracts`
and explicit `--output-root F:/framework-next/p7-runs/368-contracts`:

| Execution | Exact selected method suffixes on FixtureSupportTests | Result |
| --- | --- | --- |
| First | `test_readonly_git_object_cleanup`, `test_readonly_cleanup_refusals_preserve_accounting`, `test_cleanup_failure_accounting_in_contracts_and_public_reports` | 3 passed; 0 errors/failures/skips; exit 0; unittest 0.248 s; capture 0.599 s |
| After two test-only refinements | `test_readonly_cleanup_refusals_preserve_accounting`, `test_cleanup_failure_accounting_in_contracts_and_public_reports` | 2 passed; 0 errors/failures/skips; exit 0; unittest 0.176 s; capture 0.540 s |

The first run created a tiny real bare Git fixture (init and hash-object: two
actual Git subprocesses), confirmed a regular single-link readonly loose object,
and successfully removed the owned run while preserving its parent. That child
measured 3 files / 167 logical bytes. Its helper/runner bytes and positive test
were unchanged for the second run, which repeated only the two changed tests.
There were two Python runner launches; capture/preflight processes are outside
fixture accounting. Child accounting is retained separately rather than adding
overlapping parent/child file observations as a fabricated global total.

The final synthetic checks cover 17 refusal/retry scenarios: outside path,
traversal, unregistered file, file/ancestor/root identity drift, symlink, file
reparse, ancestor reparse, nonregular file, hardlink, writable file, attribute
drift, unknown error, unknown operation, post-chmod drift and failed single
retry. They assert no attribute/unlink mutation for refused inputs and no second
unlink on retry failure. Synthetic Windows stat attributes keep those guards
portable; this execution was Windows/Python 3.13.14, not a cross-platform trial.

Both report branches use labelled synthetic passing results followed by a
partial deletion and cleanup error. Reported accounting remains 2 files / 45
bytes, although only one file remains; exit stays 2 and outcome cleanup-failed.
No actual public entry or PR family runs in this plumbing check.

Both successful outer run directories were read back absent:
`fn-1ae6b69601f749979c5f95a54dabc2f4` and
`fn-ad34536555b5460a862f9b2008db0457` under the explicit 368 root. The old PR run
`F:/framework-next/p7-runs/373-public/fn-c21e6bb478f64c759aed8dfdbba5ea6d` remains
unchanged across both executions: device/inode, type, link count, attributes,
size, mtime and SHA-256 of every retained file match. No old cleanup retry occurred.

## Handoff and remaining scope

Syntax/readability, own-record JSON/YAML parsing, changed links, diff/scope and
complete planned commit-message checks are local checks. There are no new
unresolved observed failures in this bounded repair. Historical C1-C3/C5 and PR
failures remain retained beside their later scoped results.

Coordinator owns integration with #373/#381/#382 and separately selecting the
PR family or broader checks. No C5/full contracts/public suite, native/root,
install/apply, independent audit, provider mutation, CI restoration, push/PR or
Issue/Project mutation occurred. Unselected gates remain **deferred-by-owner**,
U001, owner program #322 coordinator / P7, next action separately assign them.
