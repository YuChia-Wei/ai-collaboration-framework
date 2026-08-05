# v0.9.0 Candidate Critical Gate

## Subject

- Candidate branch commit at execution start:
  `cc832b4ec0264743854e99a7d3d7f3bf03c915ac`
- Candidate branch tree at execution start:
  `fe817e8807b8bb54b796c07441c28a0646925942`
- Command: `C:\Program Files\Git\bin\bash.exe .ai/scripts/check-all.sh --critical`
- Environment: sandbox-external Git for Windows Bash; WSL was not used
- Started: `2026-08-05 23:41:38 +08:00`
- Completed: `2026-08-05 23:57:29 +08:00`

## Result

| Result | Count |
| --- | ---: |
| Required selected | 49 |
| Required executed | 49 |
| Passed | 49 |
| Failed | 0 |
| Blocked by environment | 0 |
| Skipped by mode | 0 |
| Advisory warnings | 0 |
| Deferred | 0 |
| Not applicable | 1 |

Total wall time was 951 seconds. The slowest check was the AI Context
Packaging GWT matrix at 782 seconds. The aggregate exit code was 0.

This run occurred after the filemode remediation and its direct GWT matrix.
The later message-only rewrite maps this subject to `bb16471c04ca7fa93db699112a5742dbe7020052`
with the identical tree `fe817e8807b8bb54b796c07441c28a0646925942`.
The only later audited-source change before this evidence correction was the
supplemental workflow-plan wording fix; focused workflow-artifact validation
passed for that source-only correction. The aggregate result therefore remains
the final-code critical evidence rather than the earlier pre-fix run.
