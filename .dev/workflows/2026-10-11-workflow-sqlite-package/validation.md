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
