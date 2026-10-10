# Local validation and acceptance evidence

Implementation baseline: `42b99e954e3d6fbf595075a079357f0ce1df057f`; the first
implementation commit containing this report binds the new source. Windows,
Python 3.13.14, PyYAML 6.0.3. No provider writes, installation or release run.

## Attempts retained

1. Focused first run: 20 tests, 1 failure, 6.968 seconds. The new assessment
   fixture used a list for `scope` and omitted `resume.last_completed_action`.
   The existing validator correctly rejected it. Corrected the fixture to its
   existing mapping contract; no product validation was weakened.
2. Focused second run: 20 tests passed, 7.559 seconds, F fixtures.
3. Fixed five-suite runner with process-local `tempfile.tempdir` on F: 199 tests,
   0 assertion failures, 14 errors, 42.528587 seconds. All errors were existing
   maintenance fixture cleanup at `tests/framework_next/support.py:50`, strict
   `Path.resolve`, `WinError 1`. This run is **failed**, not passed.
4. Minimal control: create a temporary directory and call
   `Path(value).resolve(strict=True)`. F produced WinError 1; the ordinary C
   temporary directory succeeded. The failed suite's error locations agree with
   this storage-specific limitation. No global TEMP/TMP setting was changed.
5. `python -I -B tests/run.py` with ordinary native temp: all 199 tests passed,
   no failures/errors/skips, 41.260847 seconds. This is the same small current
   suite selection, not an installation/history/durability matrix. The storage
   change is the material state change authorizing this retry.
6. Author inspection tightened malformed-operation output bounds and timestamp
   shape, with one additional regression. Focused current source: 21 tests passed,
   7.862 seconds on F. Unchanged suites retain their result; a final immutable
   default run is planned with independent review.

Focused invocation (the created contained F root is test-only):

```powershell
python -I -B -c "import sys,tempfile,unittest; tempfile.tempdir = r'F:\codex-workflow-records-aa9b936a7d8c4f85833c448b56dacd48'; sys.path.insert(0, r'C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/tests'); unittest.main(module='tools.test_workflow_records', verbosity=2)"
```

The initial fixed-suite F invocation used the same process-local temp root and
`sys.argv = ['tests/run.py']; runpy.run_path('tests/run.py', run_name='__main__')`.
This does not activate the retired `AI_CONTEXT_TEST_TMP_ROOT` route. Original
logs are retained locally under ignored
`.dev/ai-context/local/workflow-records-validation/` as `default-suites.txt`,
`default-suites-native-temp.txt`, and `focused-final.txt`.

## Actual consumer evidence

- `test_real_cli_find_read_checkpoint_receipt_and_resume_preserve_existing_bytes`:
  isolated real Git repository, actual CLI processes and current tracked workflow
  fixture; all original artifact bytes and Git tracked diff remain unchanged.
- `test_real_assessment_validator_opt_in_uses_common_store_and_legacy_default_is_preserved`:
  actual assessment CLI succeeds with old/default and opt-in paths. A malformed
  workflow stays accepted by the old existence-only check but is rejected by the
  selected common parser. A missing locator is explicitly rejected.
- `test_two_real_cli_writers_apply_at_most_one_checkpoint`: two real processes;
  one succeeds and the other returns writer_busy or revision_conflict.
- Replace failure and lost-ack tests inject the filesystem failure boundary, but
  exercise the real file replacement/journal and operation query. They are
  controlled fault evidence, not operating-system crash or power-loss trials.
- Reparse rejection test uses controlled filesystem metadata. It is not a native
  symlink/junction trial or a claim of hostile concurrent filesystem isolation.
- A read-only CLI `resume` of the actual source
  `2026-10-02-skill-routing` record returned its two completed tasks, correct
  source HEAD, document digest and explicit 256-character truncation. The original
  record was not changed. Request/result are in ignored local validation files.

## Acceptance mapping

| Issue AC | Evidence and disposition |
| --- | --- |
| 439 AC01 | `inventory.md`, tracked producer/reader/validator locations; design evidence complete for selected scope |
| 439 AC02 | Contract three-mode matrix and full-provider scenario; Git create remains with original writer, local/remote runtime not executed |
| 439 AC03 | unavailable contract and actual selected-remote/no-fallback test; remote transport itself not implemented |
| 439 AC04 | complete refs, default-change test, persisted binding mismatch and overlapping-root refusal; migration unavailable |
| 439 AC05 | bounded context/read/error tests, document revisions and explicit missing/truncated fields; no token savings claim |
| 439 AC06 | versioned contract, inventory, compatibility scenarios, follow-up decisions; Git/local not dependent on board |
| 440 AC01 | original fixture bytes and default validator behavior preserved; no historical migration or installed projection edit |
| 440 AC02 | real CLI find/context/read/checkpoint/operation/resume chain on selected format |
| 440 AC03 | missing/malformed/version/stale-source/conflict/lock/capacity cases; existing bytes preserved on rejection |
| 440 AC04 | actual assessment CLI consumer and common resume consumer; conditional orchestrator instructions separately labeled, not actual agent acceptance |
| 440 AC05 | `docs/workflow-records.md` plus contract use, recovery and unintegrated-consumer list |

This is the selected checkout slice. Package distribution, general legacy format
coverage, create/export/import, local/remote runtime, hosted Source change gate,
PR acceptance, provider closure and downstream adoption remain outside these
local pass claims. Issues remain open; later integration must choose terminal
versus deferred intent using these explicit limitations.

## Independent review

Pending an immutable implementation commit and a fresh read-only reviewer.
The reviewer must inspect binding/authority, rejection before mutation, failure
and replay behavior, original-format compatibility, consumer wiring, output
bounds and truthful source-only delivery against the contract and source policy.
