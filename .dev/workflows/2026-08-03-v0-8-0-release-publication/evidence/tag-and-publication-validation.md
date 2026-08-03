# v0.8.0 Tag And Publication Validation

## Observation

- Observed at: `2026-08-03T13:38:00+08:00`
- Repository: `YuChia-Wei/ai-collaboration-prompts-dotnet-backend`
- Validation mode: read-only tag, workflow, Release, asset, checksum, and
  archive-parity verification

## Immutable Tag And Hosted Publication

| Fact | Observed value |
| --- | --- |
| Annotated tag | `v0.8.0` |
| Tag object | `14a763876130cb8adcf876339c573ce0dbb9f330` |
| Peeled commit | `97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25` |
| Tagger timestamp | `2026-08-03T13:12:55+08:00` |
| Release node ID | `RE_kwDOSBe2Hc4Vsi4e` |
| Release URL | `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/releases/tag/v0.8.0` |
| Release state | stable; non-draft; non-prerelease |
| Publication run | `30786537723` (`success`) |
| Run URL | `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/actions/runs/30786537723` |

The sanctioned tag phase and hosted publication phase both exited `0`. The
publication phase intentionally validated the body rendered from the immutable
tagged `validated` skeleton; terminal published-mode body equality belongs to
the later finalization phase.

## Published Assets

| Asset | Size | GitHub/downloaded SHA-256 |
| --- | ---: | --- |
| `ai-context-dotnet-backend-v0.8.0.tar.gz` | 671844 | `e47374ab997209b0860ce082ed6e645e3789350926863a6ef488bcb07c8cb515` |
| `ai-context-dotnet-backend-v0.8.0.tar.gz.sha256` | 106 | `92da471d6dc1f496d1dd25f5ecc36302444d07a92f8175afd77cbe75687f0849` |
| `ai-context-dotnet-backend-v0.8.0.zip` | 1065353 | `94fe4ff17222423f2fa521343e02b8a7e4709c566ea22e264f5b1b1ac3a4701c` |
| `ai-context-dotnet-backend-v0.8.0.zip.sha256` | 103 | `04b720f0c190760dc9c3eef76922b71db3f79aa9965c1d8928aaaf8c4083bde4` |

Both archive hashes matched their adjacent sidecars. The package validator
passed for the downloaded ZIP and tar.gz together, including payload parity.

## Source Checkpoint Validation

- local non-hosted finalization phase: passed;
- AI context version registry: passed for 11 release records;
- release-state tests: 24/24 passed;
- release-note renderer tests: 8/8 passed;
- backlog release tests: 6/6 passed;
- GitHub provider tests: 19/19 passed;
- workflow-artifact and AI-context validation: passed;
- Git for Windows Bash quick gate with .NET SDK `10.0.302`: exit `0` in
  483.4 seconds.

The first direct `bash` aggregate attempt reached the .NET checks without a
visible `dotnet` command and exited `1`; it is retained as
`blocked-by-environment` and is not counted as passed. The authoritative rerun
used the explicit Git for Windows Bash path after its SDK read-back succeeded.
Initial fixture-only test attempts against the system Temp directory also hit
Windows ACL errors; the complete affected suites passed after `TEMP` and `TMP`
were scoped to the workspace test directory.

The first continuation branch's pre-PR commit-range check found that its pushed
checkpoint subject omitted the repository-required `|scope` segment. Shared
history was preserved without rewrite. This finalization branch starts from
`origin/main` and carries the same reviewed checkpoint content as one
policy-conforming squash commit; the old remote checkpoint remains only as
handoff history.

## Body-Only Authorization And Next Gate

The owner explicitly authorized changing only the v0.8.0 GitHub Release body.
The annotated tag, peeled commit, Release identity, release state, and four
asset name/digest pairs are frozen invariants.

The source checkpoint's published-mode preview rendered without candidate-only
claims at SHA-256
`05520da4dda5ddc1d98ca55741b07f10a2a4edb5ec8d36bfe785eae00e31fd86`.
Before any hosted mutation, the sanctioned hosted finalization command exited
`1` with `hosted release body differs from governed rendered body`. This is the
expected nonterminal negative gate and is not counted as passed.

This source checkpoint records the observed published registry and final
authored notes while keeping the workflow and `REL080-001` task in progress.
After this checkpoint merges to `main`, the exact published-mode body must be
rendered from integrated source, reviewed, supplied as the only hosted change,
and immediately read back with every invariant above unchanged. Project #3
`Published in` reconciliation and terminal hosted finalization follow that
merged-source gate.
