# VAL-007 Pre-Remediation Coverage And Cost Inventory

## Measurement Boundary

- Subject: `0965a2cf288c79fe91df3e291806d1bf66e9f8c9` after the workflow bootstrap and before runner, evidence, fixture, or timeout implementation changes.
- Method: read-only static inventory plus retained assessment timing evidence. No test suite, aggregate profile, release profile, full matrix, or nightly-full command was executed.
- Purpose: satisfy Issue #204's requirement to measure duplicate coverage before removing or consolidating it. This report authorizes no removal by itself.

## Static Inventory

| Surface | Static size | Repeated setup or execution | Current unique responsibility |
| --- | ---: | ---: | --- |
| `test_fail_closed_validation.py` | 44 test methods | 33 `SyntheticRunnerRepo()` constructions, 10 `SyntheticShellAssetRepo()` constructions, 40 direct `.execute()` call sites plus looped invocations | registry selection, dependency closure, required/advisory/blocking outcomes, immutable-history routing, source-only routing, cleanup safety |
| `test_immutable_history_validation.py` | 19 test methods | 24 effective fresh Git repository initializations in the main fixture paths; at least 264 baseline Git subprocesses before case-specific work | receipt provenance, history attacks, clean refresh admission, target-local fallback |
| `test_ai_context_packaging.py` | 38 test methods | the registry selects the complete file as `package-full-matrix` | package projection, archive identity, compatibility, workflow/release package contracts |
| `test_validation_evidence.py` | 5 test methods | small isolated temp repositories | input identity, reuse, privacy, execution disposition separation |

## Retained Timing Evidence

- The baseline assessment retained an aggregate runner execution of 379.975 seconds.
- The baseline incident retained a package matrix execution of 1177.187 seconds.
- Both exceed the repository's 120-second long-running threshold and remain prohibited during focused #204 implementation.

## Coverage Disposition

| Classification | Decision | Reason |
| --- | --- | --- |
| Unique risk | retain | runner dependency/failure selection, immutable-history attack/receipt cases, evidence privacy/identity, and external-task exact-once transport cover different failure layers |
| Mechanical setup duplication | optimize only after behavior parity proof | repeated copied runners and fresh Git baselines are the primary cost source; shared immutable templates may reduce setup while each case retains isolated writable state |
| Exact expensive rerun | suppress unless an explicit rerun reason is recorded | the same package command at the same commit/input/environment adds no new coverage merely because it is invoked after an aggregate profile |
| Cheap assertion overlap | defer | generic workflow topology overlaps some package assertions, but its cost is small and it is not the first optimization target |
| Invalid removal candidate | retain | evidence disposition serialization is not a substitute for a live process-tree timeout; immutable-history preflight is not an execution-wide snapshot; ordinary cleanup is not unreadable/locked cleanup |

## New Coverage Required Before Closure

- POSIX process-group and Windows Job Object child-grandchild termination with a delayed-writer seal oracle.
- Snapshot admission and in-run HEAD/tree/status/operation drift with remaining-chain abort.
- Exact argv, duration, outcome, cleanup, log digest, result digest, and invocation artifact manifest binding.
- Nested native-validator timeout and visible cleanup-failure paths.
- Static nightly readiness admission, deterministic artifact ownership, bounded concurrency, and an explicit non-enabled state.

## Removal Decision

No existing scenario is removed in the initial #204 implementation. Any later consolidation must cite this inventory, identify the duplicated setup or exact rerun fingerprint, retain the unique-risk assertions, and pass focused parity validation before deletion.

## Post-Remediation Disposition

- Fast and PR profiles now select the semantic `ValidationEvidenceRoutineContractGwtTests` class rather than the complete evidence module. Its observed test duration was approximately 20.6 to 25.2 seconds; the registry uses a 60-second bound to avoid environment-jitter false failures while remaining below the 120-second long-running threshold.
- Exhaustive evidence coverage remains a distinct release/nightly-only registry entry with a 180-second bound and no reuse. It was not run as part of this workflow.
- The GitHub workflow contract no longer asserts an exact total workflow-file count. Governed workflows are required as a semantic subset, and the disabled nightly job is checked by responsibility and behavior.
- The runner fixture no longer relies on a fixed target-file inventory and GWT-001 no longer requires a global exact reuse count. Missing-target and malformed-preparation cases assert their own semantic record fields instead.
- GWT-032 through GWT-038 passed as a seven-method batch in 115.683 seconds. This is too close to the long-running boundary to expand safely; future execution must split that batch.
- One interim whole-file evidence command unexpectedly completed in 121.283 seconds. Once observed, it was reclassified as long-running, was not rerun, and was replaced by bounded named groups. This historical execution is retained and is not represented as compliant external-task validation.
- A fixed-head reviewer noted that exact job maps in GitHub workflow GWT-005 still require maintenance when governed workflow responsibilities change. That is a semantic topology contract rather than a raw file-count assertion, but its sensitivity remains explicit follow-up scope for Issue #215.

No scenario was removed. Consolidation was limited to selection boundaries and less-sensitive semantic assertions; complete descendant containment, immutable admission, terminal publication, and negative evidence paths retain separate coverage.
