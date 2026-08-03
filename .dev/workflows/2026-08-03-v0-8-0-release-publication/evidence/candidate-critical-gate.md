# v0.8.0 Candidate Critical Gate

## Subject

- Validated lifecycle commit:
  `4c4d32a48d54b060250447c7007bf2b415df51da`
- Branch: `codex/2026-08-03-v0-8-0-release-publication`
- Candidate package subject:
  `ec50df072ec59f7e59322345f005450c48be28d7`
- Tag and publication: not created

## Candidate Phase

The sanctioned candidate command ran against a clean worktree and passed:

```text
python .ai/scripts/validate-ai-context-release-state.py --phase candidate --version v0.8.0
```

It read back `REL-v0.8.0` as a validated, untagged, unpublished candidate at
`4c4d32a48d54b060250447c7007bf2b415df51da`.

## Environment-Blocked Attempt

The first aggregate invocation resolved bare `bash` to Windows' WSL launcher:

```text
bash .ai/scripts/check-all.sh --critical
```

All preceding Python, governance, release, package, source, and shell checks
completed, but WSL interoperability was disabled and the three final .NET
commands returned `dotnet: command not found`. The command exited `1` after
573.5 seconds. This result is `blocked-by-environment`; it is not counted as a
passed gate.

PowerShell then read back the installed SDK as .NET `10.0.302`. An explicit
Git Bash probe resolved both runtimes before the replacement run:

```text
/c/Program Files/dotnet/dotnet -> 10.0.302
/c/Users/h4227/AppData/Local/Programs/Python/Python313/python -> 3.13.14
```

## Authoritative Critical Gate

The complete replacement command used the verified Git Bash runtime:

```text
& 'C:\Program Files\Git\bin\bash.exe' .ai/scripts/check-all.sh --critical
```

Observed result:

| Evidence | Result |
| --- | --- |
| Exit code | `0` |
| Elapsed | 438.6 seconds |
| Assessment catalog | 27 assessments passed structural validation |
| Workflow catalog | 57 post-adoption workflows, 77 indexed directories, and 44 backlog items passed |
| Release catalog | 11 release records passed version governance |
| AI context | 24 active indexes, 16 skills, 2 runtime roots, 345 language-policy files, 13 rules, 34 manifests, and 10 mappings passed |
| .NET execution | available and completed in the authoritative shell |

`COMMIT_RANGE` was not set, so the runner classified Selected Git Commit
Messages as not applicable. That classification is not represented as a pass.
The retained downstream-repository packaging skip and Windows symlink-
capability apply skip also remain explicitly non-passing as recorded in
`candidate-package-validation.md`.

## Disposition

The authoritative candidate lifecycle and aggregate repository gates passed.
The branch may proceed to hosted pull-request integration. GitHub checks,
merge, merged-main read-back, current-main pre-tag validation, owner-created
tag, publication, and terminal finalization remain unperformed.
