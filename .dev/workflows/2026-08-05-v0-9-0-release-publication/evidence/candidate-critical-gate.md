# v0.9.0 Candidate Critical Gate

## Subject

- Candidate branch commit at execution start:
  `bdb81e3d97e7e4afe7fc2007126a21b033c54bcd`
- Command: `C:\Program Files\Git\bin\bash.exe .ai/scripts/check-all.sh --critical`
- Environment: sandbox-external Git for Windows Bash; WSL was not used
- Started: `2026-08-05 22:49:34 +08:00`
- Completed: `2026-08-05 23:05:29 +08:00`

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

Total wall time was 955 seconds. The slowest check was the AI Context
Packaging GWT matrix at 787 seconds. The aggregate exit code was 0.

The later local filemode remediation at commit `25ae566` changed only the
package-apply planner and its direct GWT matrix. That focused matrix passed
outside the sandbox with 29 passes and one Windows symlink-privilege skip. A
fresh aggregate critical gate is still required on the final candidate commit
before integration.
