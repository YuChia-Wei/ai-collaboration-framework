# PR #78 Hosted CI Remediation

## Metadata

- `workflow_id`: `2026-08-02-python-prerequisite-diagnostics`
- `story`: `TOOL-002` / GitHub Issue #77
- `pull_request`: [#78](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/78)
- `recorded_at`: `2026-08-03T07:17:19+08:00`
- `status`: `in_progress`

## Hosted Failure

- `AI Context Governance` run `30761100104`: passed.
- `Package AI Context Candidate` run `30761100110`: passed.
- `Portable AI Context Gates` run `30761100100`: failed only in Ubuntu quick-gate job `91531622398`; the Ubuntu and Windows prerequisite-contract jobs passed.
- The sole failing test was `GWT-018`, which is intended to prove the offline uv fallback is queried exactly once after generic Python candidates fail.

## Root Cause And Authorized Fix

`SyntheticRunnerRepo.execute` prepended the fixture bin directory but retained
the inherited host `PATH`. On Ubuntu Actions, a host `python3.12` executable was
therefore discovered by the approved versioned-Python scan before the fixture's
offline uv fallback. The real interpreter then attempted the aggregate runner
against an intentionally minimal synthetic repository and reported missing
aggregate assets.

The production resolver behaved according to its approved order. On
2026-08-03 the repository owner approved the smallest test-only correction:
make the GWT-018 child `PATH` hermetic and add minimal fixture-owned `dirname`
and `date` stubs. No production resolver, discovery priority, exit mapping, or
package behavior is changed.

## Local Validation

| Check | Outcome | Evidence |
| --- | --- | --- |
| Focused GWT-018 inside the Windows sandbox | `blocked-by-environment` | Temporary-directory ACL returned `WinError 5`; this attempt is not counted as passed. |
| Focused GWT-018 outside the sandbox | `passed` | 1 test passed in 2.187 seconds. |
| Complete `test_fail_closed_validation.py -v` outside the sandbox | `passed` | 30 tests passed in 46.253 seconds. |
| `git diff --check` | `passed` | No whitespace errors. |
| Local `bash .ai/scripts/check-all.sh --quick` | `blocked-by-environment` | Exit 1 after 599 seconds because this Git Bash environment could not resolve `dotnet`; all preceding Python, workflow, package, and fail-closed checks passed. This aggregate invocation is not counted as passed. |
| Direct PowerShell .NET validation | `passed` | Analyzer 49/49, validation 2/2, and building-block 5/5 tests passed with .NET SDK 10.0.302. |

The retained downstream package integration still requires an explicitly
supplied external repository. Its conditional skip remains a skip and is not
counted as passed.

## Remaining Integration Gate

Commit and push the test-only fixture correction, then require the new PR #78
hosted runs to pass. Merge and merged-`main` read-back remain mandatory before
workflow, Story, or Project completion. No v0.8.0 release artifact, tag,
publication, or hosted release mutation is authorized by this remediation.
