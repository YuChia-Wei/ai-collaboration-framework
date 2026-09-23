# P7 PR worktree repair

Workflow 2026-09-23-work-management; task CR335-002; owner ai-context-governance. This bounded continuation follows the [live Issue 335 P7 authorization](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/335), read OPEN with updatedAt 2026-09-23T16:05:50Z. It preserves the earlier source delivery and CR335-001 rather than converting their static checks into behavioral acceptance.

## Actual failure and source correction

The target pilot's existing pr-prepare.execution.json records a real installed CLI execution at 2026-09-23T16:01:33.553140+00:00, exit 1; pr-prepare.stdout.json records blocked/git-read, mutation_state=none. Its pr-git-diagnostic.json isolates the exact sanitized --worktree config read, exit 128, in a normal linked worktree with the extension disabled. These three artifacts and the request were read only from C:/Github/YuChia/dotnet-mq-arch-lab-rc1-pilot/.dev/ai-context/local/rc1-record-pilot/. No target settings or bytes were changed.

The correction uses git config --no-includes --null --list with no forced scope. Git reads the repository and enabled worktree scopes plus the fixed command settings; existing process-local environment controls still suppress system/global inputs. Every returned diff/include/includeIf/promisor key retains the same rejection rule; every nonzero Git result remains blocked. Optional missing worktree config follows the same effective read path. No extension is enabled in real repositories. The exact diff flags, bounded helper, environment, path and byte controls are unchanged. [Git configuration files/scopes](https://git-scm.com/docs/git-config) document effective reads; the earlier generic --worktree fallback claim did not cover this observed multi-worktree restriction.

A fresh non-persisted graph excluded src/skills/pr/scripts; the known tracked function was read directly. Initial sandbox Issue read failed through the blocked proxy, then the scoped read-only network retry succeeded. Initial abbreviated stdout.json/execution.json paths were absent; the actual pr-prepare.stdout.json/pr-prepare.execution.json files were found in the named evidence directory and read successfully. These preparation failures are retained, distinct from the actual product failure.

## Selected execution, initially not executed

Commit source and the single test file before running:

```text
python -I -B tests/framework_next/test_pr_git_worktree.py --output-root F:/framework-next/p7-runs/335-pr-worktree
```

The test creates one unique contained child, one small repository, two commits touching one UTF-8 tracked file, and one linked worktree. It reproduces the old explicit-scope exit 128, exercises successful disabled-extension prepare/render, optional missing enabled config and safe enabled config, rejects worktree diff/include/includeIf/promisor plus local diff/include, and keeps invalid worktree/extension config blocked. All changed Git settings are fixture-only. The actual CLI runs in isolated Python subprocesses through runpy with an observational Popen audit; no Git or product transport is mocked.

Limits: 32 public launches, 96 total directly observed Git launches (including source identity and setup), 256 created-file budget and 1 MiB authored fixture bytes. Existing fixture support measures observed/retained paths and bytes. Because post-step inventories do not enumerate short-lived Git internal files, a separate conservative creation budget reserves 24 files for each of the six finite one-file Git setup mutations, four for each public call and six authored/evidence paths. Templates, hooks and automatic maintenance are disabled for fixture setup. Counts and measurement limits remain explicit; the unique fixture and raw outputs are retained on success or failure. No fixture cleanup touches any other run.

This is a selected P7 behavioral run only. Provider/network operations, full/history matrices, installation, candidate rebuild, target mutation, CI and legacy audit machinery remain deferred-by-owner under U001, owner program 322 coordinator / P7. Coordinator owns review, first push, PR/online merge, immutable candidate rebuild and the separately selected installed target update/retry.

## Results

Source/test prepared; selected behavioral execution is not-executed until the clean immutable checkpoint exists. No new pass is claimed here. Declared runtime is gpt-6-astra / ultra; no independent runtime attestation, sub-agent or new task/worktree creation is claimed.

Direct pre-commit checks completed: 9 UTF-8 files, 2 Python ASTs without imports, 1 JSON document, 2 YAML documents, 10 local links and git diff --check (exit 0). The selected behavioral run remains not-executed before this checkpoint.

## Actual selected result

The source/test checkpoint ad5d93eb71bd8b9cd5aacf74917245f72188f3cd was clean before execution. The exact selected command exited 0 from 2026-09-23T16:15:34.101727+00:00 through 2026-09-23T16:15:45.489352+00:00 (11.388 seconds). This was one run, with actual Git 2.55.0.windows.3. Four successful public outcomes cover disabled prepare/render, enabled missing config and enabled safe config; six expected unsupported/git-config outcomes cover both consumed scopes; two expected blocked/git-read outcomes preserve invalid-config failures. The old explicit-scope command separately reproduced exit 128.

[Execution summary](../evidence/CR335-002/execution-summary.json) links the exact source, command, limits and byte-preserved evidence hashes. [Raw report](../evidence/CR335-002/report.json), [Git launch events](../evidence/CR335-002/git-launches.jsonl), [direct Git results](../evidence/CR335-002/process-results.jsonl) and [public requests/results](../evidence/CR335-002/public-results.jsonl) are retained. The actual run remains at F:/framework-next/p7-runs/335-pr-worktree/fn-cdc972971aca4aaca2ed382dfe3b1fc7. No cleanup was attempted.

Actual counts: 12 public launches; 95 Git launches comprising 86 product, seven fixture (including old-command rejection) and two source-identity reads. The fixture has two commits, one authored tracked file and one linked worktree. Measured post-step inventory has 29 observed/retained files and 7,455 authored fixture/input bytes. The conservative created-file bound is 198, below 256; this is not an exact census of transient Git file creation. Raw report support.accounting process fields contain unused default zeros because that legacy helper's process observer was not activated; they are not measurements. The explicit audited launch counts and event log are authoritative for this selected run.

The first sandbox read-back of the exclusive fixture directory failed with PermissionError. A scoped read-only retry using the execution permission succeeded; this did not rerun the product or consume another fixture attempt. All expected failures remain in the raw evidence.

The closing commit updates workflow/evidence only. Source, operations reference, test and test-support bytes are unchanged from the tested commit; exact Git diff/hash read-back binds that preserved subject. Local CR335-002 repair/selected-fixture scope is completed. No installed target rerun, candidate rebuild, provider acceptance or CI pass is claimed. Those next actions remain coordinator-owned.

Closing record checks: 10 UTF-8 files, 3 JSON documents, 2 YAML documents, 116 JSONL records and 15 local links read/parsed successfully; raw evidence SHA-256 values matched their byte-preserved copies, git diff --check exited 0, and the tested package/test/support diff from ad5d93eb was empty. These closing checks do not rerun or expand the selected behavioral test.
