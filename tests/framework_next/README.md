# Distribution and source-loader tests

Use the repository-owned [test entrypoint](../readme.md):

```powershell
python -I -B tests/run.py --suite distribution
python -I -B tests/run.py --suite loader
python -I -B tests/run.py --suite platform
```

`distribution` reads declared sources in place and checks metadata, references,
selection, adapter projection, version grammar and small maintenance records.
It does not assemble a candidate or install a target. Test names describe behavior
and apply to the current source; no suite is tied to an RC release number.

`loader` uses tiny synthetic source modules and real Python import/cache machinery.
It needs isolated Python (`-I -B`); path admission is simulated in these unit tests.
`platform` exercises Windows API return values through simulations and requires a
Windows Python host. Neither optional suite establishes native installation,
volume safety, interruption or recovery acceptance. A missing prerequisite fails
the selected run; it is not silently skipped.

The old runner, complete candidate/install/scan-budget fixtures, public-family
trial drivers and Git linked-worktree PR tests were retired under Issue #425.
The retained `support.py` creates only owned small temporary fixtures and cleans
their exact verified roots. It does not create Git repositories or repeatedly
scan fixtures for accounting. Pure data cases do not use it.

Historical [P7 results](../../.dev/workflows/2026-09-23-source-contract-checks/p7-verification-report.md)
remain evidence for their recorded source commits. Their commands, budgets and
coverage are not the current test interface. Future native/downstream tests must
be selected from actual use cases; the retired trials are not replaced by a
claim that unit tests prove installation or agent behavior.
