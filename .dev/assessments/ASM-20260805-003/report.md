# Validation Cost External Review Intake And Decision Record

## Metadata

- `assessment_id`: `ASM-20260805-003`
- `assessment_type`: `ai-context-audit`
- `owner_skill`: `ai-context-governance`
- `status`: `final`
- `created_at`: `2026-08-05T21:21:52+08:00`
- `subject`: `codex/2026-08-05-validation-cost-remediation@7f6746b34759c1633b7083175381e76a222bb142`
- `base`: `main@eaf00ae15c0dcfccb92254c192d52b005b93fb36`
- `implementation issue`: [#128](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/128)

## Purpose And Evidence Boundary

This record preserves an owner-supplied external review so another independent AI can read the unchanged source, reproduce the repository checks, and distinguish evidence from the owner's implementation authorization. The original review is retained byte-for-byte at [evidence/external/original/validation-cost-remediation-2026-08-05/VALIDATION-COST-REMEDIATION.en.md](evidence/external/original/validation-cost-remediation-2026-08-05/VALIDATION-COST-REMEDIATION.en.md); its SHA-256 and provenance are cataloged in [evidence/evidence-catalog.yaml](evidence/evidence-catalog.yaml).

The external document assessed `main@eaf00ae`. Before implementation, Git confirmed that this commit was an ancestor of the then-current HEAD and that `.ai/scripts/check-all.sh` was unchanged since that revision. The owner explicitly authorized only the bounded work recorded in Issue #128. This assessment does not authorize further implementation, mode reclassification, changed-path selection, release allocation, publication, or integration into `main`.

## Earlier Compatibility Decisions That Remain In Force

| ID | Prior decision and repository evidence | Current disposition |
| --- | --- | --- |
| COMP-001 | `e76d89ca` made `check-all.sh` portable: resolve a usable Python 3.11+ interpreter through `AI_CONTEXT_PYTHON`, an active environment, generic and versioned PATH names, and an offline `uv` fallback. Literal `python ...` declarations remain so shell-manifest parity can govern the command inventory. | **Preserved.** This delivery changes neither resolver order nor the literal command inventory. |
| COMP-002 | `da70bb5` fixed the compatibility regression where synthetic fixtures inherited a caller's `AI_CONTEXT_PYTHON`, bypassed their PATH stub, and produced false failures. | **Preserved and covered.** `CheckAllRunnerGwtTests.test_gwt_015_given_parent_python_override_when_fixture_runs_then_path_stub_remains_authoritative` remains in the full runner class. |
| COMP-003 | `3f863be` standardized portable Python prerequisite diagnostics and native POSIX/PowerShell launchers without creating a parallel `check-all.ps1`, implicit package installation, or private-runtime discovery. | **Preserved.** A missing compatible top-level Python is now reported as `BLOCKED-BY-ENVIRONMENT` with exit `3`, still non-passing. |

## External Findings And Decision Reconciliation

| Stable ID | External claim or proposal | Decision | Repository-native evidence and rationale |
| --- | --- | --- | --- |
| VCR-001 | V-05 / Patch 1: add per-check timing and a machine-readable aggregate line. | **Adopted.** | `check-all.sh` records selected-check duration with Bash `SECONDS`, prints the slowest 15 rows, total wall time, and `AI_CONTEXT_CHECK_TIMING`. The machine line also includes blocked count. Full `CheckAllRunnerGwtTests` passed. |
| VCR-002 | V-04 / Patch 2: distinguish environment blocks; blocks stay fail-closed and use exit `3` when no genuine failure exists. | **Partially adopted with a stricter classifier.** | Required and advisory blocks have independent counters and an exit `3` only when `FAILED_CHECKS` is zero. The startup Python prerequisite follows the same contract. Tests prove missing dotnet and a read-only filesystem block, while `MSB1003` remains a genuine exit-`1` failure. |
| VCR-003 | Patch 2 proposed broad output signatures including `No module named`, `MSB1003`, generic `Permission denied`, and generic `Operation not permitted`. | **Not adopted.** | These messages can identify a repository defect, invalid command, or product configuration error. The implementation recognizes only explicit Python prerequisite diagnostics, missing Python/dotnet, narrow network-unavailable text, and `Read-only file system`. This biases toward a real failure rather than masking a defect. |
| VCR-004 | V-01/V-03 / Patch 3: make quick/critical tiering effective. | **Deferred.** | This changes enforcement selection and needs the caller/profile design owned by `VAL-002` / Issue #96. The prior caller inventory found release preparation and handoff consumers of `--critical`; no flags were reclassified here. |
| VCR-005 | V-02 / Patch 4: add deterministic `--changed` selection from declared input paths. | **Deferred.** | This is explicitly design scope for `VAL-002` / Issue #96. No input-path map or changed-path skipping was introduced. |

## WSL And Sandbox Result

The initial sandbox default `bash` probe failed with WSL `CreateInstance/E_ACCESSDENIED`. The same host, outside the sandbox, completed both `wsl.exe --status` and a minimal `wsl.exe -e sh` command with exit `0`. The latter printed `WSL_EXEC_OK` and `Linux 6.18.33.2-microsoft-standard-WSL2` in 4,941 ms.

Therefore the observed unavailability was a sandbox execution boundary, not evidence that WSL itself was unavailable. This does not prove that WSL has the repository's required .NET SDK, Python prerequisites, or writable temporary-directory configuration; those checks were not run and must not be inferred.

## Execution-Time Evidence

The machine-readable record is [evidence/execution-record.json](evidence/execution-record.json). It records exact observed elapsed milliseconds where available, distinguishes sandbox blocks from passes, and marks the real `check-all.sh --full` aggregate as `not-run` rather than estimating it from fixture time.

| Record | Outcome | Elapsed | Interpretation |
| --- | --- | ---: | --- |
| ER-001 | WSL status outside sandbox | 46 ms | WSL service/status probe succeeded. |
| ER-002 | Minimal WSL command outside sandbox | 4,941 ms | WSL execution succeeded. |
| ER-003 | Complete `CheckAllRunnerGwtTests` | 68,483 ms | 23 isolated runner cases passed. |
| ER-004 | Focused remediation regression cases | 19,551 ms | Six targeted cases passed. |
| ER-005 | Shell-asset plus AI-context validators | 4,300 ms | Combined parallel wall time only. |

## Independent Re-Review Request

An external reviewer should start with the immutable source and this decision table, then verify:

1. per-check timing does not alter command selection or the individual command predicate;
2. exit `3` is non-passing in every known caller;
3. the restricted classifier does not mask repository failures;
4. the deferred `VAL-002` design remains separate from this bounded remediation; and
5. any proposed WSL run records its host boundary, prerequisites, exit code, and elapsed duration.

## Validation At This Subject

- `python .ai/scripts/tests/test_fail_closed_validation.py -v CheckAllRunnerGwtTests` — passed: 23 tests in 68.483 seconds.
- `python .ai/scripts/validate-shell-assets.py` — passed.
- `python .ai/scripts/validate-ai-context.py` — passed.
- `python .ai/scripts/validate-git-commits.py --range main..HEAD` — passed for commit `7f6746b`.
- Git for Windows Bash syntax check and `git diff --check` — passed.

## Residual Risk And Next Action

- Patch 2 necessarily changes aggregate exit semantics for environment-only blocks; callers still treat any non-zero status as non-passing, but future CI-specific handling must preserve that rule.
- Patch 3 and Patch 4 remain deferred with `VAL-002`; this record is evidence, not an exception to that ownership.
- The current branch is unpushed and unintegrated. Keep Issue #128 open until a reviewed PR is merged and `main` is read back.
