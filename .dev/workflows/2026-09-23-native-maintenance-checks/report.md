# Native maintenance observation report

**Selected result: not-passed (exit 1).** Local driver delivery and its one bounded attempt are complete. Native acceptance is incomplete; product defect N382-F01 is handed to the coordinator. This is neither target readiness nor whole-P7/CI acceptance.

## Fixed subject and actual commands

- Starting source: `031233202f21e0793c9667cac872375d65e52be0`.
- Executed clean code commit: `a9af5fe793f938ac9b66f94034bda8a2cafb50ec`.
- Branch/worktree: `codex/2026-09-23-native-maintenance-checks`, `F:/framework-next/382`.
- Final record commit: resolve this report's containing commit; the later records do not relabel the executed subject. Git objects/refs are in the existing persistent C: repository.
- Declared execution: GPT-6 Astra / ultra; dispatch provenance is not independent runtime attestation. No subagent, callback or new task was created.
- Runtime: Python 3.13.14, PyYAML 6.0.3, Windows.

```text
python -I -B tests/framework_next/run.py --layer native-windows --native-root F:/framework-next/p7-runs/native-w01/382
```

The real builder command uses `tools/build-development.py --repository F:/framework-next/382 --commit a9af5fe793f938ac9b66f94034bda8a2cafb50ec --profile lesson-minimal` with the returned run's candidate/build-scratch parents. Each maintenance call uses the exact interpreter, `-I -B`, and `F:/framework-next/382/src/tools/maintain_framework.py` with a raw stdin request. [calls.jsonl](evidence/calls.jsonl) retains exact argv/cwd/PID/exit/request and lossless stdout/stderr.

Candidate identity:

```text
development:a9af5fe793f938ac9b66f94034bda8a2cafb50ec:a78a9716872dd5187a1f96af480a8c681d9e7e06f1048b399626b6e36d82a902
```

[engine-pin.json](evidence/engine-pin.json) contains all ten exact raw file hashes, source commit, ID and version. Raw pin-file SHA-256: `4446630e1c611aa82dd3d2e4ac439004b1e1dc69edf353d43a52278c43a869a6`. This is the real development candidate, not #381's evolving versioned format.

## Per-case results

| Case | Actual observation | Disposition |
| --- | --- | --- |
| entry-pin | Real builder assembled (0); public inspect inspected/uninstalled/not-assessed (0); public plan blocked/unreadable-input (1) | Failed aggregate; pin/hash refusal subcases unexecuted after stop |
| fresh-apply | No public apply dispatched | Unexecuted, dependent on plan repair |
| same-content | No no-op dispatched | Unexecuted |
| drift-collision | No negative fixture/call dispatched | Unexecuted |
| writer-exclusion | No guard helper or competing apply dispatched | Unexecuted |
| interruption-recovery | Zero public interruption attempts; no marker or operation | Unexecuted, not a missed-window observation |

No blanket passing result is returned. No synthetic/native replacement evidence is claimed for an unexecuted case. The driver has a single interruption path and would preserve `not-observed` as non-pass if that future window is missed. These later code paths have only static evidence in this delivery.

## N382-F01: protected-input strict resolution fails on assigned F: filesystem

The public plan returns `blocked` with `unreadable-input`, `changed: false`, and no details. All five finite protected rows match their actual raw hashes or expected absence. A separate read-only primitive observation shows existing direct non-reparse `.ai`, `.ai/custom`, and `.ai/custom/framework.json` each throw `OSError`, `winerror=1`, `errno=22` at `Path.resolve(strict=True)`. [Raw diagnosis](evidence/protected-path-diagnosis.json). Its original line-70 locator points within the function; the exact expression is line 77.

Current source `src/distribution/installation_plan.py:77` calls that primitive unconditionally inside `_protected_path`, before backend preparation. `src/distribution/installation.py:207` shares this function for protected-input checks during apply/recovery. This source/primitive evidence explains the public failure; no instrumented replay or fabricated product success was used.

Smallest owner repair: protected-input canonicalization in `_protected_path`, with focused direct-path and alias/reparse/link/containment refusal regressions. Reconcile with the existing Windows path handling; do not delete protected inputs or bypass safety checks to pass the native run. The coordinator must select that product repair and subsequent affected native execution. This Issue changes no product files.

## Counts, retained roots and evidence

Selected run: 3 public/helper children (builder, inspect, plan), 5 driver Git calls, peak 1 simultaneous owned child, 0 durable operations, 0 interruption attempts. Nested product Git launches are unavailable, not zero. The runner's observed close duration was 5.352 seconds; no performance claim.

Run-close snapshot recorded 33 observed file names / 304,034 logical bytes. Later durable diagnosis/inventory records bring read-back to **35 files / 317,456 logical bytes**. Counts stay below 256 files / 16 MiB. Transient creation totals are unavailable; snapshot names are a lower bound. [Summary and evidence digests](evidence/summary.json), [native result](evidence/result.json), [post-failure inventory](evidence/post-failure-readback.json). Tracked evidence copies are source records, separate from these selected output-root counts. Tracked JSON snapshots use LF; the manifest distinguishes each durable raw hash from its tracked snapshot hash. Public stdout/stderr remain lossless base64; raw originals remain on C:.

- Native residue: `F:/framework-next/p7-runs/native-w01/382/63bb8cce`.
- Durable recovery child (empty): `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n382/recovery/63bb8cce`.
- Durable observations: `C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend/.dev/ai-context/local/p7/n382/observations/63bb8cce`.

Both C: parents were and remain ignored/untracked. Direct roots and disjoint identities were checked. The project has five authored files and no lock, marker or guard. Candidate/build-scratch outputs and every observation are retained. Process termination only was selected; no power/OS/storage-loss safety is claimed.

A later sandboxed inventory could not read the private candidate directory (WinError 5); its rglob undercount was rejected. Repeating only the read-only inventory under the original scoped creation permission saw 30 native files, four durable observation files before writing the inventory, and zero recovery files. No public retry occurred.

## Validation and handoff

Changed Python AST and workflow JSON/YAML parsing, bounded invalid-argument checks, changed report link resolution, path-scope inspection and `git diff --check` passed. Each commit uses its complete validated message file. The actual native run failed as retained above. No independent review or downstream behavior claim is made.

All unselected legacy/full/history/formal/audit/lease/handoff/hosted gates remain **deferred-by-owner** under U001, owner program #322 coordinator / P7, next action separately selected repair/adoption. Complete target pilot, versioned-candidate acceptance, stable upgrade, CI enablement and publication remain separate. No push, PR, Issue/Project/provider mutation, release/tag or target activation occurred.

Coordinator next action: inspect this local checkpoint; assign N382-F01 to the managed-installation owner; preserve existing evidence; select a new affected native run after repaired-source integration. The workflow's completed state describes bounded implementation/attempt/handoff only, not six-case acceptance or Issue closure.
