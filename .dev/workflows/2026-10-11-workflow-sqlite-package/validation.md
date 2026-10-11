# Validation evidence and retained attempts

Scope: #441 AC01–AC06 and #448 AC01–AC08. Owner selected Git files plus SQLite,
Python/PyYAML prerequisites, an optional package, isolated synthetic consumer
installation and validation on 2026-10-11. Dolt is deferred as a future candidate.
Product inputs must originate in `src`; root `tools` only orchestrates source work.
Source base: `6a615e8ac19df9343835ab74a0e2436cdc974976`.

## Focused implementation checks

The following are local Windows evidence on the uncommitted implementation before
the first immutable subject. They are not hosted, published or installed evidence.

| Command / scope | Latest observed result |
| --- | --- |
| `python -I -B -c "import sys,unittest;sys.path.insert(0,'tests');s=unittest.TestLoader().loadTestsFromName('tools.test_workflow_sqlite');r=unittest.TextTestRunner(verbosity=1).run(s);sys.exit(not r.wasSuccessful())"` | 19 tests passed in 15.588 s; native C-drive fixtures, real CLI clients, competing writes/export and killed uncommitted child process |
| `python -I -B tests/run.py --suite distribution --suite release` | 111 tests passed, 0 failures/errors/skips; runner 7.473703 s |
| `python -I -B tests/run.py --suite source --suite schemas` | 51 tests passed, 0 failures/errors/skips; runner 1.202032 s |
| `git diff --check` and staged equivalent | passed before the first commit |

SQLite size-limit tests lower constants to reach the same transactional boundary
with small fixtures. They are not a maximum-capacity performance benchmark.
Activation phase-two recovery uses explicit fault injection; the killed process
test covers a real uncommitted workflow transaction, not OS power loss. The export
test holds a real read snapshot while another process reaches an uncommitted write,
then checks that the archive contains the complete old state and the active store
contains the committed new operation.

## Failures and repairs retained

- Initial sandbox Git fixture creation failed on Windows TemporaryDirectory
  permissions before executing tests. Host-permission execution was then selected;
  the environment failure is not classified as a product regression.
- Initial host Git-only run: 23 tests, one error in malformed list-valued operation
  handling. The error response now checks operation type before set membership.
- First combined Git/SQLite run: 36 tests, two failures and four errors. New test
  fixtures compared CRLF barrier output without normalization and left SQLite
  connections open on Windows. Explicit connection closing and line normalization
  repaired these fixture failures. Subsequent SQLite runs passed.
- Package worker first test attempt had six fixture errors (wrong byte helper and
  missing mock import); corrected before its 69-test focused pass.
- Release-template worker first run had one diagnostic-order failure; the new
  README proof check was moved after the established catalog-identity diagnostic.
  Its next release run passed all 38 tests.
- Parent tools/distribution run: 149 tests in 57.405 s, 12 errors. Parent had updated
  the Codex/Claude text templates without rebinding their exact-template hashes.
  Renderers now recognize the exact prior and new templates; arbitrary templates
  remain rejected. The later distribution/release 111-test run passed.
- Next packaging run: 111 tests, one error for unsorted workflow package references
  after adding the Git-format contract. Manifest member ordering was corrected.
- Source/schema run: 51 tests, five errors from synthetic engine paths outside
  `src`; after correcting that fixture, one boundary test still treated `x` as a
  valid source path. The fixture plan was expanded to check minimum/maximum
  `src/` paths and reject `tools/`; the next 51-test run passed.

## Pre-commit read-only findings

Reviewer `workflow_review` inspected the dirty source; this is advisory, not the
required immutable independent review. Parent implemented all repairs:

1. Global receipt capacity could block activation after the original was retired.
   Workflow and administrative pools are separate (4096 and 128); restore and
   retirement reserve two admin slots, activation checks one before successor
   claim. At the next-generation limit retirement fails while the original stays
   active. The finite history is retained rather than compacted.
2. Legal large revisions could exceed complete backup size. Each normal write now
   checks the actual JSON/base64 portable-data budget (60 MiB) before commit;
   admin rows have independent bounded capacity and 2 KiB size. Failed writes roll
   back without losing the previously exportable state.
3. A recomputed archive could insert a checkpoint without its retained operation.
   Preflight now checks create/parent/checkpoint/write-document state transitions,
   receipt/event relationships and timestamps. A corruption test reproduces and
   rejects the previously accepted shape.

## Outstanding at first implementation commit

The fixed default source suite, actual catalog/subset assembly and installed
Git/SQLite operation chains, repeat installation, selected real recovery/refusal,
immutable independent review, and per-Issue final acceptance remain pending.
No current #441/#448 hosted CI, PR/merge, Issue closure, production data adoption,
release publication, macOS/Linux installed execution or power-loss result is
claimed. The source project's existing managed installation remains unchanged.

## Fixed source checks and first actual installation attempt

- `ac2412a064d071d403f0d4442041b228964032ae`: fixed default suite passed
  242 tests, zero failures/errors/skips; runner 66.414335 s. Raw output SHA-256:
  `248c3294a4de0ed122de0f0eaf513d8f87d0b6bec962337e4c5118ca3e384f4a`.
- `5e9d83af70198f598be743acea6a410645b67418`: the reviewed installation runner
  was integrated; the fixed default suite passed 242 tests, zero
  failures/errors/skips; runner 67.960538 s. Raw output SHA-256:
  `841fc318ccc5e194357942b10bc8dbdc88e1a974733fc218c8a5ddc3e72f5f2e`.
- Independent reviewer `workflow_review` reviewed the complete base
  `6a615e8ac19df9343835ab74a0e2436cdc974976` to `ac2412a0` implementation and
  the runner blob `62b7faf6711d7bd4ac5985dd6ed70972a4faa37e` separately. No
  actionable finding was reported. The integrated runner has that exact blob;
  every other tracked path equals `ac2412a0`. This review was read-only, not an
  installed-execution result; the later failure below invalidates any broad
  inference that source review proves installation acceptance.
- External validator `contract_advice` executed the actual installation runner
  once at `5e9d83af` on 2026-10-11, 10:33:03–10:34:34 UTC. The attempt failed
  after 91.7 s at `013-plan-first`, before apply. Catalog assembly took 73.35 s;
  workflow subset, nonselected optional subset and initial inspect passed.
  Thirteen checks passed before the plan returned `blocked`, `changed: false`,
  `invalid-shape`. Installed CLI, repeat apply and recovery were not run.
- The product regression was a shared schema definition: source-only `Pin.path`
  also constrained `Lock.project_inputs`, rejecting all six legitimate non-src
  caller inputs (configuration, locator, plan, task and sentinels). `declared_by`
  was investigated and ruled out; it is a nonempty string, not a target-owner
  enum. `ProjectInput` now keeps caller-relative paths, while `Pin` keeps the
  strict `src/` engine source rule. The regression checks both boundaries.
- Focused schemas on an F-drive source copy with the three repaired files:
  44 tests passed, zero failures/errors/skips, runner 1.237839 s. The actual
  installation attempt must be repeated against a new immutable repaired head.

## Owner-selected test storage and cleanup

The owner explicitly selected F RAM disk for **all subsequent test paths**:
source copies, working directories, temporary files, package outputs, installation
targets, SQLite, backups and evidence. TEMP/TMP/TMPDIR are process-scoped; system
defaults are unchanged. RAM-disk results do not prove persistent-media or
power-loss durability. The retired historical acceleration workflow is not used.

The owner also explicitly rejected retaining the C-drive trial artifacts.
After checking the exact root and its two generated children for unexpected
contents and reparse paths, `C:/fw441-448` was removed and absence was read back.
The retained experience is this root-cause record and the concise summary at
`F:/workflow-validation-441-448/archive/attempt-1-5e9d83af.json` (SHA-256
`df1e1e9444ff9f6c575f59d4f8f2a50c3ba5f6ad99e50f209d0a974da976fec6`).
Original terminal SHA-256:
`038d3bb12bb1988d9c36913657f72a240e561946227fdf624a82785bff5c2ec9`.
Raw first-attempt fixtures and call files are no longer available; the summary
is retained experience, not a substitute for the next actual execution.

The two previous C-drive source-suite logs were also removed after their exact
result JSON summaries were copied and hash-checked in the same F archive.
Their raw output hashes and results remain recorded above; the raw C logs are
no longer retained. No new test data was written to C after the owner's direction.

## Repaired fixed source and actual F installation

Source subject `4ec4114dbcdffaacfada5b05a4e8d750f5304deb`, tree
`a76a26c62924f0e43dc8e5de0a42a86477386601`, was clean before and after execution.

- Full fixed suite from a separate F checkout: **243 tests passed**, zero
  failures/errors/skips, 68.19431 s. Cwd
  `F:/fw441-448/source-4ec4114d-0d8c0eab`; TEMP/TMP/TMPDIR
  `F:/fw441-448/suite-temp-23104c5c`. Report:
  `F:/fw441-448/source-test-4ec4114d.json`; raw log:
  `F:/fw441-448/full-source-4ec4114d.log`.
- Actual installation attempt 2 ran exactly once after the schema repair and
  F-only runner change. External executor `contract_advice` returned **passed**:
  69 checks, 51 calls, 114.539 s, 10:43:03–10:44:57 UTC on 2026-10-11.
  Catalog assembly used 68.625 s; no controlled benchmark or acceleration claim
  is made. Report: `F:/fw441-448/e-af7291441785/terminal.json`.
- Parent read back all 51 command records: every cwd and TEMP/TMP/TMPDIR is F.
  Preservation files before/after are byte-identical; 23 installed/caller file
  hashes and SQLite bytes are unchanged by the maintenance replay scenarios.
- Fresh final `inspect-after` reports `managed-bytes-consistent`. The preceding
  selected `recover-restore-refused` reports conflict and details `drift`; that
  is the refused operation's result, not a successful restore or the final
  independent installation observation.
- Source suite, installed runtime and final evidence reconciliation are separate
  evidence classes. See [acceptance.md](acceptance.md) for identities, hashes,
  exact commands, #441/#448 AC mapping and the v0.20.0 handoff.

## Independent review subjects and disposition

Reviewer `workflow_review` remained read-only throughout. It did not perform the
source suite or installation and did not count author repairs as its own work.

| Fixed scope | Result |
| --- | --- |
| `6a615e8a` → `ac2412a0`, all 48 changed files, plus original runner blob `62b7faf6711d7bd4ac5985dd6ed70972a4faa37e` | No actionable finding in the initial immutable review; later actual installation exposed the recorded shared-Pin regression |
| `5e9d83af` → `cd205e98f2910994a3ca77287260f70e4fb9779f`, four-file schema repair and failure record | No actionable finding; `Pin` remains src-only, caller `ProjectInput` is separate, regression tests cover both validators |
| `cd205e98` → `4ec4114dbcdffaacfada5b05a4e8d750f5304deb`, two test-tool files | No actionable finding; F-only roots and narrow Windows error-1 fallback retain no-reparse, stable identity, native device and cleanup root checks |
| Fixed F terminal/raw outputs/audit/preservation bound to `4ec4114d` | No contradiction or missing evidence in the selected installed scenarios; verified 36 audited consumer calls, 2 expected source denials each, 0 unexpected denials and only installed workflow module origins |

The final evidence-record commit changes documentation and workflow records only.
It must retain exact equality of the tested `src`, `tools`, `tests`, `.github`
and governing source-policy paths to `4ec4114d`. This is a scoped content reuse
statement, not whole-tree equivalence or hosted current-head acceptance.
