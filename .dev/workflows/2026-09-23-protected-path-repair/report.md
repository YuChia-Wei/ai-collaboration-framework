# Protected path repair report

**Selected result: passed.** The bounded repair, nine focused simulated tests and
one actual F: public plan are complete. This does not establish native apply,
recovery, target readiness, CI or whole-P7 acceptance.

## Fixed source and repair

- Baseline: `cc3189193788750277269f63f3753a639becc3c6`.
- Clean executed source: `3c0832b89d73cfedfc625462d167a3811fdf7931`.
- Branch/worktree: `codex/2026-09-23-protected-path-repair`, `F:/framework-next/383`.
- Final record commit: this report's containing commit; product/test content is
  unchanged from the executed checkpoint. The existing persistent Git object
  database/refs hold both checkpoints; no push has occurred.
- Declared execution: OpenAI Codex, gpt-6-astra / ultra; one independent task,
  no subagents. This is dispatch provenance, not independent runtime attestation.

`installation_plan._protected_path` now catches only Windows WinError 1 from
strict resolution. It requires direct directory ancestry, nonzero device/inode
identities and stable identity/mode across the Windows long-name query. The
existing containment and case-sensitive relative-component comparison still
reject aliases. No protected data directory or sibling entries are enumerated.
`installation_state._windows_long_path` extracts the existing root query without
changing its direct drive mapping, drive type or bounded result checks. There
is no new engine module; all ten raw pinned members remain required.

Hardlink, raw byte and expected-absence checks still run through the original
`_Reader.read` and protected-input checks. `installation.py` shares the repaired
path function; apply/recover behavior was not exercised or rewritten here.

## Actual selected execution

```text
python -I -B tests/framework_next/test_protected_paths.py --mode actual-plan
```

The driver ran once with exit 0, Python 3.13.14 on Windows. It freshly verified
clean source/branch/HEAD, copied only the four existing raw protected files from
#382's retained project after checking their original hashes, and kept the fifth
expected-absent binding. Original #382 residue was not changed or deleted.

A real `lesson-minimal` candidate was built through `tools/build-development.py`
from the clean repair commit. The public `src/tools/maintain_framework.py` plan
returned `planned`, exit 0. All five protected rows were preserved; raw file
hashes and expected absence matched afterward. No lock/guard/operation marker
or writer storage was created. Native backend and full engine-closure plan
prerequisites are satisfied. Writer guard, quiescence, fresh observation and
exclusive allocation remain pending as returned by this read-only plan.

- Candidate identity:
  `development:3c0832b89d73cfedfc625462d167a3811fdf7931:2d9f67acfbeb908f6deb34026a5208666cc9ae43c4d323824ecada4bdc1e64fb`.
- Plan SHA-256:
  `ba243ff7099f433caba2cdf9458741a9a0751f5f4ddc4dcb58e6343351c42bf7`.
- Retained run: `F:/framework-next/p7-runs/protected-path-383/ce4aed45`.
- Final observation: **37 files / 329,045 logical bytes**, below 96 / 4 MiB.
  Five directly observed child launches comprise three driver Git reads, one
  public builder and one public plan. Nested product Git launches are unavailable.
  Observed file snapshots do not measure every transient creation.

[Preflight](evidence/preflight.json) records the clean source, caps, input hashes
and real WinError 1 observations for `.ai`, `.ai/custom` and its config file.
[Engine pin](evidence/engine-pin.json) contains all ten fresh raw hashes.
[Calls](evidence/calls.jsonl) retain exact argv/cwd/request, timestamps, durations,
exit codes and lossless base64 stdout/stderr. [Public response](evidence/plan-response.json)
and [result](evidence/result.json) retain the actual plan and its prerequisites.
[Inventory](evidence/inventory.json) excludes its own later-written file;
[manifest](evidence/manifest.json) records the final counts and raw-copy digests.

## Focused validation and limitations

```text
python -I -B tests/framework_next/test_protected_paths.py --mode regressions
```

Nine tests passed in 0.099 seconds: ordinary/fallback resolution; unchanged root
query reuse; non-Windows and other-error refusal; case/short-alias/containment;
unavailable API/direct-drive mapping; symlink/reparse/parent/identity refusal;
ancestor drift; present/absent bindings; raw-byte mismatch and hardlink refusal.
These are simulations, not native alias/link or concurrent-filesystem acceptance.

Changed Python AST, UTF-8 readability, workflow JSON/YAML and JSONL parsing,
changed local links, scope inspection and `git diff --check` passed. Both local
commits use complete message files validated before committing their exact bytes.
No independent review or full suite was run. Source graph discovery was freshly
indexed on the baseline; conclusions were verified against tracked definitions
and the direct shared caller, not search absence.

The initial sandboxed Issue read failed at its configured proxy; one scoped
read-only GitHub query then observed #383 OPEN with matching scope. After the
successful actual run, a sandboxed read of its private mode-0700 output failed
with access denied. A scoped read/copy succeeded without another public trial;
the failure was not treated as missing files or a zero-file inventory.

Unselected legacy/full/history/formal/audit/lease/effective-rule-packet/hosted
gates remain **deferred-by-owner** under U001, owner program #322 coordinator /
P7. No apply, recover or native interruption was dispatched. #382 owns the later
affected native run after coordinator integration. CI restoration, full rc.1
pilot, Issue closure and publication remain separate decisions.

## Coordinator handoff

Review these local checkpoints, integrate through the authorized source PR
process and then resume the separately selected #382 run. There is no new
owner-sensitive design decision. The changed product paths are only
`src/distribution/installation_plan.py` and `src/distribution/installation_state.py`;
the single test is `tests/framework_next/test_protected_paths.py`; all remaining
tracked changes are under this issue-owned workflow. No push, PR, merge,
Issue/Project mutation, release/tag or target installation occurred here.
