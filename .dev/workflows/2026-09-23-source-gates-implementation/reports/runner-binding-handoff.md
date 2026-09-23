# Issue #369 runner binding follow-up

This report retains checkpoint `6c5f4a298bc3ffdbea47348ae6ef8c9f4584b41d`.
The later [public binding](public-binding-handoff.md) supersedes only the public
reserved/unimplemented state below. Product failures and policy refusal remain.

Status: **contracts CLI/result binding implemented; overall Issue remains partial**.
Worktree `F:/framework-next/369`, branch `codex/2026-09-23-source-gates`.
Prior local checkpoint: `5ee20036392b6ad217e4029c8a256e176e9d8cdf`.
Upstream runner inspected at exact commit
`070a47335ffce99d31bd83e487447942539e4a9f` using read-only `git show` of
`tests/framework_next/run.py`, `support.py`, `README.md`, and the selected retained
report/stdout/stderr. No upstream file was merged, copied into ownership, imported
or executed. This checkout still lacks the runner until coordinator integration;
a selected missing pinned runner fails before subprocess launch.

Authority: coordinator's bounded continuation of #369, program #322 / U001.
Allowed writes: `.github/scripts/check-source-change.py`,
`.github/tests/test_source_gates.py`, `.github/workflows/source-checks.yml`, and
this Issue's existing design/workflow records. Rejected policy/AGENTS/PR-template
writes remain **STOPPED**. No new policy authority, provider operation, native
implementation, sub-agent, callback, push, PR or merge was authorized/performed.

## Actual command and result contract

```text
python -I -B tests/framework_next/run.py --layer contracts
```

`command_for('contracts')` now produces that exact argv using the active Python
interpreter. No `--case`, `--family`, history/profile aggregate or invented receipt
flag is added. The runner's actual disposable output-root precedence is retained;
no implicit drive/root selection or TEMP/TMP mutation was added.

Actual upstream exit semantics: 0 only when all selected unittest cases succeed,
none are skipped and cleanup succeeds; 1 for test failure; 2 for argument,
dependency/setup or cleanup failure. Unexpected exceptions remain nonzero. Its
stderr is normal unittest output; stdout contains small JSON observations, not a
universal successful acceptance receipt.

The caller requires subprocess status/exit 0 plus one positive `Ran N tests ...`
/ bare `OK` summary, one readable runtime observation and one fixture accounting
observation with no residue/next action. It accepts unrelated intermediate
observations. It refuses missing/duplicate/malformed observations, skipped/failed
or contradictory summaries, error observations, nonzero exits and incomplete
cleanup. It never converts an invented `status: passed` JSON into a contracts
pass. The parser is deliberately tied to this inspected interface and records
its full source commit; future output/interface changes require reconciliation.
This internal source-gate summary is not an independent acceptance receipt.

`--layer public --family <ID>` is explicitly reserved by #368 and exits 2 before
allocation. The selector refuses all seven declared public families with
`reserved-layer-not-implemented:#368` until the actual V2 interface arrives;
unknown families also fail. Native remains the unchanged blocked Windows-only
entry from the prior checkpoint. No public/native selection can become a green
stub merely because its name is known.

The dormant source workflow now explicitly declares the runner's existing
`PyYAML>=6,<7`, `jsonschema>=4.18,<5`, and `referencing` dependencies. Its Python
3.12 selection satisfies upstream Python >=3.11,<4. No local dependency was
installed; this changes only the dormant workflow command. Context/events,
action revisions, credential-free checkout, permissions and CI suspension remain
unchanged.

## Focused evidence and retained upstream failures

Command executed only in this assigned worktree:

```text
python -I -B F:/framework-next/369/.github/tests/test_source_gates.py --output-root F:/framework-next/p7-runs/369-source-gates
```

Outcome: **28 tests passed**, 0 failures/errors/skips; unittest 2.440 s, harness
2.441 s. Four meaningful new result/absence tests and the updated argv/dependency
assertions use explicitly labelled **synthetic subprocess responses**. They cover
normal unittest-plus-observation output (LF/CRLF), invented success JSON, nonzero
failure/argument/cleanup exits, missing pinned runner, reserved/unknown selections,
skip/zero/duplicate summaries, missing/duplicate/malformed observations, invalid
UTF-8, contradictory error text and retained cleanup residue. The existing tiny
real Git fixture remains only source-selector evidence, not product execution.
Its created child was cleaned; the supplied parent remains.

The original first failure (24 methods, one F: strict-resolution WinError 1 error,
0.248 s) and permitted fixture-only second pass (24/24, 1.733 s) remain in the
[prior handoff](blocked-handoff.md). This follow-up does not erase either result.

**Upstream evidence, not executed by this task:** fixed #368 reports 14 test
methods, 11 successful methods, 3 affected methods with 7 error instances; exit 1.
C1 encountered rejected YAML anchors in PR/local-backlog package metadata. C3 and
C5 encountered strict Windows final-path resolution refusal on assigned F:.
**Zero candidate builds succeeded**; C5's second build/reader/corruption cases
were unexecuted. Their package/backend repair authority remains with the
coordinator and affected owners. Binding an exit/result parser does not repair,
re-run or turn those failures into a product pass.

Direct verification for this follow-up includes changed Python AST/JSON/YAML
readability, changed local links, UTF-8/newline/whitespace, exact changed-path scope,
and complete planned-message validation before committing those exact bytes.
No independent review, product import/test, native trial or hosted result is
claimed. A fresh in-memory bounded `.github/scripts` graph (181 nodes, no reported
skips, persistence false) aided navigation; exact tracked source and Git diff were
used because the tool did not attest Git SHA. No full tree/history scan.

## Next owners and stops

1. Coordinator integrates this local follow-up with fixed #368 through its own
   online process. Runner source is not owned or mutated by #369.
2. Preserve #368's failed acceptance until separately authorized owner repairs and
   actual selected execution establish new evidence. No automatic retries here.
3. V2 public families and V3 native runner/roots/results remain undelivered; keep
   their selected commands explicitly non-passing until real bindings exist.
4. Original policy/AGENTS/template refusal remains in force pending direct user
   confirmation through the coordinator. No stopped write was retried in this turn.
5. First push/PR/merge, high-risk scoped review, actual trials, root/policy adoption
   and exact user-adopted CI restoration remain coordinator-owned. Keep #369 open.

The containing commit is this follow-up's identity; final handoff provides its
exact SHA and clean worktree read-back. Unselected legacy validation/packet
machinery and CI remain `deferred-by-owner`, U001, program #322 coordinator / P7.
