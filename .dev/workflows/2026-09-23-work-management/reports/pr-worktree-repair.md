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
